from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

INTERNAL_SERVICE_KEY = "internal-service-key-change-in-production"


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_internal_key: Optional[str] = Header(None),
) -> dict:
    # Allow internal service-to-service calls via a shared secret header
    if x_internal_key and x_internal_key == INTERNAL_SERVICE_KEY:
        return {"sub": "internal-service", "role": "internal"}

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
