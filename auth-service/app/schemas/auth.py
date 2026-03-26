from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole
from typing import Optional


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    station_id: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    station_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
