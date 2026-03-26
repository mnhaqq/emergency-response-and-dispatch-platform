from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.vehicle import VehicleType, VehicleStatus


class VehicleRegister(BaseModel):
    registration_number: str
    vehicle_type: VehicleType
    station_id: str
    driver_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


class VehicleStatusUpdate(BaseModel):
    status: VehicleStatus
    incident_id: Optional[str] = None


class VehicleResponse(BaseModel):
    id: UUID
    registration_number: str
    vehicle_type: VehicleType
    station_id: str
    driver_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: VehicleStatus
    current_incident_id: Optional[str]
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class LocationResponse(BaseModel):
    id: UUID
    registration_number: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: VehicleStatus
    last_updated: datetime

    class Config:
        from_attributes = True
