import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    POLICE_ADMIN = "POLICE_ADMIN"
    FIRE_SERVICE_ADMIN = "FIRE_SERVICE_ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(SAEnum(UserRole), nullable=False)
    password_hash = Column(String, nullable=False)
    station_id = Column(String, nullable=True)   # links user to a hospital/station
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
