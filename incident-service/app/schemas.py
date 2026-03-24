from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enums import IncidentType

class IncidentCreate(BaseModel):
    citizen_name: str
    incident_type: IncidentType
    latitude: float
    longitude: float
    notes: Optional[str]

class IncidentResponse(BaseModel):
    id: int
    citizen_name: str
    incident_type: IncidentType
    latitude: float
    longitude: float
    notes: Optional[str]
    created_by: int
    assigned_unit: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateStatus(BaseModel):
    status: str

class AssignUnit(BaseModel):
    unit: str