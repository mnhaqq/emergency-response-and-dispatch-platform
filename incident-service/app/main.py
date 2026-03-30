from fastapi import FastAPI
from app.api.incidents import router as incident_router
from app.db.session import Base, engine
import logging

app = FastAPI(
    title="Emergency Incident Service",
    description="Records and manages emergency incidents with auto-dispatch.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)
app.include_router(incident_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "incident-service"}
