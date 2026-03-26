from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EventPayload(BaseModel):
    incident_id: str
    event: str
    incident_type: Optional[str] = None
    region: Optional[str] = None
    assigned_unit_type: Optional[str] = None
    assigned_unit_id: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class ResponseTimeStats(BaseModel):
    average_seconds: Optional[float]
    min_seconds: Optional[float]
    max_seconds: Optional[float]
    total_resolved: int


class IncidentsByRegion(BaseModel):
    region: str
    incident_type: str
    count: int


class ResourceUtilization(BaseModel):
    unit_type: str
    unit_id: str
    total_dispatches: int
