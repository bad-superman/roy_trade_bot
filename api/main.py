from fastapi import FastAPI
from config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
def root():
    return {"message": "Welcome to Roy Trade Bot API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from api.routers import backtest
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["backtest"])


