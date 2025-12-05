from celery import Celery
from config.settings import settings
from core.engine import run_backtest_task as engine_run_backtest

celery_app = Celery(
    "roy_trade_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def run_backtest_celery(self, strategy_name: str, symbol: str, params: dict, start_date: str, end_date: str):
    """
    Celery 任务包装器：调用核心回测引擎
    """
    try:
        result = engine_run_backtest(strategy_name, symbol, params, start_date, end_date)
        return {"status": "success", "result": result}
    except Exception as e:
        # Log error properly in production
        return {"status": "failed", "error": str(e)}
