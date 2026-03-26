from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.incident import IncidentType, IncidentStatus, ResponderType


class IncidentCreate(BaseModel):
    citizen_name: str
    incident_type: IncidentType
    latitude: float
    longitude: float
    notes: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentAssign(BaseModel):
    assigned_unit_id: str
    assigned_unit_type: ResponderType


class IncidentResponse(BaseModel):
    id: UUID
    citizen_name: str
    incident_type: IncidentType
    latitude: float
    longitude: float
    notes: Optional[str]
    created_by: str
    assigned_unit_id: Optional[str]
    assigned_unit_type: Optional[ResponderType]
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
