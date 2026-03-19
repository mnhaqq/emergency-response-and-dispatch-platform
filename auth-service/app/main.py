from fastapi import FastAPI
from app.routes import auth
from app.database import engine, Base

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)