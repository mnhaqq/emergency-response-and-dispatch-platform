from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
from app.database import Base
from app.enums import IncidentType

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    citizen_name = Column(String, nullable=False)
    incident_type = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    notes = Column(String)

    created_by = Column(Integer, nullable=False)  # Admin ID
    assigned_unit = Column(String, nullable=True)

    status = Column(String, default="CREATED")

    created_at = Column(DateTime, default=datetime.utcnow)