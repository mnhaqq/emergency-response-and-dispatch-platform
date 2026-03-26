import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class IncidentEventType(str, enum.Enum):
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"


class IncidentEvent(Base):
    """
    Lightweight event log pushed by the Incident Service.
    Used to compute response times and incident counts.
    """
    __tablename__ = "incident_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String, nullable=False, index=True)
    event = Column(SAEnum(IncidentEventType), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ResponseRecord(Base):
    """
    Computed once an incident is resolved — stores final metrics.
    """
    __tablename__ = "response_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String, unique=True, nullable=False, index=True)
    incident_type = Column(String, nullable=True)
    region = Column(String, nullable=True)        # derived from lat/lon or stored manually
    assigned_unit_type = Column(String, nullable=True)
    assigned_unit_id = Column(String, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)   # created_at -> resolved_at
    created_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
