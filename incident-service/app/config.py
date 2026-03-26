from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    DISPATCH_SERVICE_URL: str = "http://dispatch-service:8000"
    ANALYTICS_SERVICE_URL: str = "http://analytics-service:8000"

    class Config:
        env_file = ".env"


settings = Settings()
