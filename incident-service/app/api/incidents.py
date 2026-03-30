import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.incident import Incident, IncidentStatus, IncidentType
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentStatusUpdate, IncidentAssign
from app.services.dependencies import get_current_user, require_system_admin
from app.services.dispatcher import (
    incident_type_to_responder,
    find_nearest_responder,
    notify_analytics,
    INTERNAL_HEADERS,
)
from app.config import settings
from app.services.utils import _region_from_coords
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_system_admin),
):
    try:
        incident_type_enum = IncidentType(payload.incident_type) 
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid incident type: {payload.incident_type}")
    incident = Incident(
        citizen_name=payload.citizen_name,
        incident_type=incident_type_enum,
        latitude=payload.latitude,
        longitude=payload.longitude,
        notes=payload.notes,
        created_by=current_user["sub"],
        status=IncidentStatus.CREATED,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Auto-dispatch: find nearest available responder
    responder_type = incident_type_to_responder(payload.incident_type)
    nearest = find_nearest_responder(payload.latitude, payload.longitude, responder_type)

    if nearest:
        incident.assigned_unit_id = nearest["id"]
        incident.assigned_unit_type = responder_type
        incident.status = IncidentStatus.DISPATCHED

        # Tell dispatch service to mark the vehicle as on-duty
        try:
            with httpx.Client(timeout=10.0) as client:
                client.put(
                    f"{settings.DISPATCH_SERVICE_URL}/vehicles/{nearest['id']}/status",
                    json={"status": "ON_DUTY", "incident_id": str(incident.id)},
                    headers=INTERNAL_HEADERS,
                )
                logger.info("Dispatch request success")
        except Exception:
            logger.exception("Dispatch request failed")
            pass

        db.commit()
        db.refresh(incident)

    notify_analytics(
        incident_id=str(incident.id),
        event="INCIDENT_CREATED",
        incident_type=incident.incident_type.value,
        region=_region_from_coords(incident.latitude, incident.longitude),
        assigned_unit_type=incident.assigned_unit_type.value if incident.assigned_unit_type else None,
        assigned_unit_id=incident.assigned_unit_id,
    )
    return incident


@router.get("/open", response_model=List[IncidentResponse])
def get_open_incidents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return (
        db.query(Incident)
        .filter(Incident.status.in_([IncidentStatus.CREATED, IncidentStatus.DISPATCHED, IncidentStatus.IN_PROGRESS]))
        .order_by(Incident.created_at.desc())
        .all()
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}/status", response_model=IncidentResponse)
def update_status(
    incident_id: UUID,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status

    # Free up vehicle when incident is resolved
    if payload.status == IncidentStatus.RESOLVED and incident.assigned_unit_id:
        try:
            with httpx.Client(timeout=10.0) as client:
                client.put(
                    f"{settings.DISPATCH_SERVICE_URL}/vehicles/{incident.assigned_unit_id}/status",
                    json={"status": "AVAILABLE", "incident_id": None},
                    headers=INTERNAL_HEADERS,
                )
                logger.info("Dispatch request success")
        except Exception:
            logger.error("Dispatch request failed")
            pass
        notify_analytics(
            incident_id=str(incident.id),
            event="INCIDENT_RESOLVED",
            incident_type=incident.incident_type.value,
            region=_region_from_coords(incident.latitude, incident.longitude),
            assigned_unit_type=incident.assigned_unit_type.value if incident.assigned_unit_type else None,
            assigned_unit_id=incident.assigned_unit_id,
        )

    db.commit()
    db.refresh(incident)
    return incident


@router.put("/{incident_id}/assign", response_model=IncidentResponse)
def manually_assign(
    incident_id: UUID,
    payload: IncidentAssign,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_system_admin),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.assigned_unit_id = payload.assigned_unit_id
    incident.assigned_unit_type = payload.assigned_unit_type
    incident.status = IncidentStatus.DISPATCHED
    db.commit()
    db.refresh(incident)
    return incident
