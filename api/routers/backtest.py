from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
from core.engine import run_backtest_task

router = APIRouter()

class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    start_date: str
    end_date: str
    params: Dict[str, Any] = {}
    initial_cash: float = 10000.0

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """
    同步运行回测（仅演示用，生产环境应使用Celery异步）
    """
    try:
        # 在实际生产中，这里应该发送给 Celery worker
        # task = run_backtest_celery.delay(...)
        # return {"task_id": task.id}
        
        # 为了快速演示，直接同步调用
        result = run_backtest_task(
            strategy_name=request.strategy,
            params=request.params,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
def list_strategies():
    return ["SmaCross"]

