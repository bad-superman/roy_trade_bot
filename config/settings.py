import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Roy Trade Bot"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MYSQL_URL: str = os.getenv("MYSQL_URL", "mysql+pymysql://trade_user:trade_password@localhost/roy_trade_db")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://root:rootpassword@localhost:27017/")
    MONGO_DB_NAME: str = "roy_trade_data"
    
    # Redis
    # Use 'redis' as hostname when running inside docker network trade_net
    # But fallback to 'localhost' for local development
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

settings = Settings()
