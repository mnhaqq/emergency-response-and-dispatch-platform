from fastapi import FastAPI
from app.api.analytics import router as analytics_router
from app.db.session import Base, engine

app = FastAPI(
    title="Analytics & Monitoring Service",
    description="Aggregates incident and dispatch data to produce operational insights.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "analytics-service"}
