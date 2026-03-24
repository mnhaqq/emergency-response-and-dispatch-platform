from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str):
    return pwd_context.hash(password[:72])

# Verify password
def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)

# Create token
def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Create access + refresh tokens
def create_tokens(user_id: int, role: str):
    access = create_token(
        {"sub": str(user_id), "role": role},
        timedelta(minutes=30)
    )
    refresh = create_token(
        {"sub": str(user_id)},
        timedelta(days=7)
    )
    return access, refresh