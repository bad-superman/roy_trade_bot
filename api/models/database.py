from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

# MySQL (Async)
# Ensure the URL starts with mysql+aiomysql for async, but pymysql is sync. 
# For this example we might stick to sync if using standard Celery, 
# but for FastAPI async is better. Let's use sync for simplicity in Celery workers
# and async for FastAPI if needed. For now, let's stick to standard SQLAlchemy sync for simplicity 
# unless high concurrency is strictly required, as Backtrader is sync.
# Wait, standard requirement is python, let's use standard SQLAlchemy (Sync) for now 
# to avoid complexity with Backtrader which is a blocking CPU bound task.
# Actually, for API we want async.

from sqlalchemy import create_engine

# Sync Engine for Celery & Backtrader compatibility
MYSQL_ENGINE = create_engine(
    settings.MYSQL_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=MYSQL_ENGINE)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB (Async for API, Sync for Workers if needed)
# We will use pymongo for sync operations in backtrader
import pymongo

def get_mongo_client():
    return pymongo.MongoClient(settings.MONGO_URL)

def get_mongo_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]

