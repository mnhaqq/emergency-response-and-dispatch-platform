from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.dependencies import get_current_user, require_role
from app.services.nearest_responder import find_nearest_responder

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE INCIDENT
@router.post("/", response_model=schemas.IncidentResponse)
def create_incident(data: schemas.IncidentCreate,
                    user=Depends(get_current_user),
                    db: Session = Depends(get_db)):

    incident = models.Incident(
        citizen_name=data.citizen_name,
        incident_type=data.incident_type,
        latitude=data.latitude,
        longitude=data.longitude,
        notes=data.notes,
        created_by=int(user["sub"])
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    responder = find_nearest_responder(
        data.latitude,
        data.longitude,
        data.incident_type
    )

    if responder:
        incident.assigned_unit = responder["id"]
        incident.status = "DISPATCHED"
        db.commit()
        db.refresh(incident)


    return incident

# GET OPEN INCIDENTS
@router.get("/open", response_model=list[schemas.IncidentResponse])
def get_open_incidents(db: Session = Depends(get_db),
                       user=Depends(get_current_user)):

    return db.query(models.Incident).filter(
        models.Incident.status != "RESOLVED"
    ).all()

# GET INCIDENT BY ID
@router.get("/{id}", response_model=schemas.IncidentResponse)
def get_incident(id: int, db: Session = Depends(get_db),
                 user=Depends(get_current_user)):

    incident = db.query(models.Incident).get(id)
    if not incident:
        raise HTTPException(404, "Incident not found")

    return incident



# UPDATE STATUS
@router.put("/{id}/status")
def update_status(id: int,
                  data: schemas.UpdateStatus,
                  db: Session = Depends(get_db),
                  user=Depends(get_current_user)):

    incident = db.query(models.Incident).get(id)
    if not incident:
        raise HTTPException(404, "Incident not found")

    incident.status = data.status
    db.commit()

    return {"message": "Status updated"}


# ASSIGN UNIT
@router.put("/{id}/assign")
def assign_unit(id: int,
                data: schemas.AssignUnit,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):

    incident = db.query(models.Incident).get(id)
    if not incident:
        raise HTTPException(404, "Incident not found")

    incident.assigned_unit = data.unit
    incident.status = "DISPATCHED"
    db.commit()

    return {"message": "Unit assigned"}