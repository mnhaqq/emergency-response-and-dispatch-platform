import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class IncidentType(str, enum.Enum):
    MEDICAL = "MEDICAL"
    FIRE = "FIRE"
    CRIME = "CRIME"
    ACCIDENT = "ACCIDENT"
    OTHER = "OTHER"


class IncidentStatus(str, enum.Enum):
    CREATED = "CREATED"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class ResponderType(str, enum.Enum):
    AMBULANCE = "AMBULANCE"
    FIRE_TRUCK = "FIRE_TRUCK"
    POLICE = "POLICE"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_name = Column(String, nullable=False)
    incident_type = Column(SAEnum(IncidentType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String, nullable=False)          # admin user ID from auth service
    assigned_unit_id = Column(String, nullable=True)     # vehicle/unit ID from dispatch service
    assigned_unit_type = Column(SAEnum(ResponderType), nullable=True)
    status = Column(SAEnum(IncidentStatus), nullable=False, default=IncidentStatus.CREATED)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
