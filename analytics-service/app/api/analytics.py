from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.analytics import IncidentEvent, IncidentEventType, ResponseRecord
from app.schemas.analytics import (
    EventPayload, ResponseTimeStats,
    IncidentsByRegion, ResourceUtilization,
)
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ─── Internal event ingestion (called by incident-service) ───────────────────

@router.post("/events", status_code=status.HTTP_202_ACCEPTED, include_in_schema=False)
def ingest_event(payload: EventPayload, db: Session = Depends(get_db)):
    """
    Internal endpoint — receives lifecycle events from the Incident Service.
    No auth required (internal network only).
    """
    try:
        event_type = IncidentEventType(payload.event)
    except ValueError:
        return {"detail": "unknown event, ignored"}

    event = IncidentEvent(
        incident_id=payload.incident_id,
        event=event_type,
        recorded_at=datetime.utcnow(),
    )
    db.add(event)

    # When an incident is resolved, compute and store response record
    if event_type == IncidentEventType.INCIDENT_RESOLVED:
        created_event = (
            db.query(IncidentEvent)
            .filter(
                IncidentEvent.incident_id == payload.incident_id,
                IncidentEvent.event == IncidentEventType.INCIDENT_CREATED,
            )
            .first()
        )

        response_time = None
        resolved_at = datetime.utcnow()
        if created_event:
            response_time = int((resolved_at - created_event.recorded_at).total_seconds())

        # Upsert response record
        record = db.query(ResponseRecord).filter(ResponseRecord.incident_id == payload.incident_id).first()
        if not record:
            record = ResponseRecord(incident_id=payload.incident_id)
            db.add(record)

        record.incident_type = payload.incident_type
        record.region = payload.region
        record.assigned_unit_type = payload.assigned_unit_type
        record.assigned_unit_id = payload.assigned_unit_id
        record.created_at = created_event.recorded_at if created_event else None
        record.resolved_at = resolved_at
        record.response_time_seconds = response_time

    db.commit()
    return {"status": "accepted"}


# ─── Analytics query endpoints ────────────────────────────────────────────────

@router.get("/response-times", response_model=ResponseTimeStats)
def get_response_times(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Average, min, and max response times across all resolved incidents."""
    result = db.query(
        func.avg(ResponseRecord.response_time_seconds).label("avg"),
        func.min(ResponseRecord.response_time_seconds).label("min"),
        func.max(ResponseRecord.response_time_seconds).label("max"),
        func.count(ResponseRecord.id).label("total"),
    ).filter(ResponseRecord.response_time_seconds.isnot(None)).one()

    return ResponseTimeStats(
        average_seconds=float(result.avg) if result.avg else None,
        min_seconds=float(result.min) if result.min else None,
        max_seconds=float(result.max) if result.max else None,
        total_resolved=result.total or 0,
    )


@router.get("/incidents-by-region", response_model=List[IncidentsByRegion])
def get_incidents_by_region(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Incident counts grouped by region and incident type."""
    rows = (
        db.query(
            ResponseRecord.region,
            ResponseRecord.incident_type,
            func.count(ResponseRecord.id).label("count"),
        )
        .filter(ResponseRecord.region.isnot(None), ResponseRecord.incident_type.isnot(None))
        .group_by(ResponseRecord.region, ResponseRecord.incident_type)
        .order_by(ResponseRecord.region, ResponseRecord.incident_type)
        .all()
    )
    return [
        IncidentsByRegion(region=r.region, incident_type=r.incident_type, count=r.count)
        for r in rows
    ]


@router.get("/resource-utilization", response_model=List[ResourceUtilization])
def get_resource_utilization(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Total dispatches per unit, sorted by most deployed."""
    rows = (
        db.query(
            ResponseRecord.assigned_unit_type,
            ResponseRecord.assigned_unit_id,
            func.count(ResponseRecord.id).label("total"),
        )
        .filter(
            ResponseRecord.assigned_unit_type.isnot(None),
            ResponseRecord.assigned_unit_id.isnot(None),
        )
        .group_by(ResponseRecord.assigned_unit_type, ResponseRecord.assigned_unit_id)
        .order_by(func.count(ResponseRecord.id).desc())
        .all()
    )
    return [
        ResourceUtilization(
            unit_type=r.assigned_unit_type,
            unit_id=r.assigned_unit_id,
            total_dispatches=r.total,
        )
        for r in rows
    ]


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """High-level dashboard summary stats."""
    total_incidents = db.query(func.count(IncidentEvent.id)).filter(
        IncidentEvent.event == IncidentEventType.INCIDENT_CREATED
    ).scalar()

    total_resolved = db.query(func.count(ResponseRecord.id)).filter(
        ResponseRecord.response_time_seconds.isnot(None)
    ).scalar()

    avg_response = db.query(func.avg(ResponseRecord.response_time_seconds)).scalar()

    return {
        "total_incidents": total_incidents or 0,
        "total_resolved": total_resolved or 0,
        "average_response_time_seconds": round(float(avg_response), 1) if avg_response else None,
    }
