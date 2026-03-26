from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.db.session import Base, engine

app = FastAPI(
    title="Identity & Authentication Service",
    description="Manages users, authentication, and role-based authorization.",
    version="1.0.0",
)

# Create tables (Alembic handles this in prod; fallback for dev)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}
