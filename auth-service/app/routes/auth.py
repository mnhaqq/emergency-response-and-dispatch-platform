from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import SessionLocal
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# REGISTER
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=auth.hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# LOGIN
@router.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    access, refresh = auth.create_tokens(user.id, user.role)

    return {
        "access_token": access,
        "refresh_token": refresh
    }

# REFRESH TOKEN
@router.post("/refresh-token")
def refresh_token(refresh_token: str):
    from jose import jwt

    try:
        payload = jwt.decode(refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("sub")

        access, refresh = auth.create_tokens(user_id, payload.get("role", ""))
        return {
            "access_token": access,
            "refresh_token": refresh
        }
    except:
        raise HTTPException(401, "Invalid refresh token")

# PROFILE
@router.get("/profile", response_model=schemas.UserResponse)
def profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(models.User).get(int(user["sub"]))
    return db_user