import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class VehicleType(str, enum.Enum):
    AMBULANCE = "AMBULANCE"
    FIRE_TRUCK = "FIRE_TRUCK"
    POLICE = "POLICE"


class VehicleStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ON_DUTY = "ON_DUTY"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_number = Column(String, unique=True, nullable=False)
    vehicle_type = Column(SAEnum(VehicleType), nullable=False)
    station_id = Column(String, nullable=False)        # hospital / police station / fire station ID
    driver_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)            # current GPS latitude
    longitude = Column(Float, nullable=True)           # current GPS longitude
    status = Column(SAEnum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)
    current_incident_id = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
