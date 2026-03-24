from fastapi import FastAPI
from app.database import Base, engine
from app.routes import incidents

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident Service")

app.include_router(incidents.router)