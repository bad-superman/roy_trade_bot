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
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Oanda Configuration
    OANDA_TOKEN: str = os.getenv("OANDA_TOKEN", "")
    OANDA_ACCOUNT_ID: str = os.getenv("OANDA_ACCOUNT_ID", "")
    OANDA_PRACTICE: bool = os.getenv("OANDA_PRACTICE", "True").lower() == "true"

    # IB Configuration
    IB_HOST: str = os.getenv("IB_HOST", "127.0.0.1")
    IB_PORT: int = int(os.getenv("IB_PORT", 7497))
    IB_CLIENT_ID: int = int(os.getenv("IB_CLIENT_ID", 1))

    # OKX Configuration
    OKX_API_KEY: str = os.getenv("OKX_API_KEY", "038979d0-c84c-45dc-b4ce-d9241143b8c3")
    OKX_SECRET: str = os.getenv("OKX_SECRET", "3C635A86E24E70CA4122F91B09881BAF")
    OKX_PASSPHRASE: str = os.getenv("OKX_PASSPHRASE", "Nihao@147852")
    OKX_DEMO: bool = os.getenv("OKX_DEMO", "True").lower() == "true" # Use demo trading

    class Config:
        env_file = ".env"

settings = Settings()
