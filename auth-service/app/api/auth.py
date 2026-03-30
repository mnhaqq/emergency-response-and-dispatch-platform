from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserProfile
from app.services.auth_utils import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        role_enum = UserRole(payload.role)  # convert string -> enum
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {payload.role}")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        role=role_enum,
        password_hash=hash_password(payload.password),
        station_id=payload.station_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = payload.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": str(user.id), "role": user.role.value, "station_id": user.station_id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest):
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    token_data = {"sub": decoded["sub"], "role": decoded["role"], "station_id": decoded.get("station_id")}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/verify", tags=["Internal"])
def verify_token(current_user: User = Depends(get_current_user)):
    """Internal endpoint used by other services to verify a JWT and get user info."""
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
        "station_id": current_user.station_id,
    }
