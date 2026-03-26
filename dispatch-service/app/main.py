from fastapi import FastAPI
from app.api.vehicles import router as vehicle_router
from app.db.session import Base, engine

app = FastAPI(
    title="Dispatch Tracking Service",
    description="Manages vehicle registration, GPS tracking, and real-time location via WebSockets.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)
app.include_router(vehicle_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "dispatch-service"}
