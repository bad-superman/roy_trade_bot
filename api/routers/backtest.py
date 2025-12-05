from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from celery.result import AsyncResult
from tasks.worker import run_backtest_celery

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
    异步提交回测任务
    """
    task = run_backtest_celery.delay(
            strategy_name=request.strategy,
            symbol=request.symbol,
            params=request.params,
            start_date=request.start_date,
            end_date=request.end_date
        )
    return {"task_id": task.id, "status": "submitted"}

@router.get("/status/{task_id}")
async def get_backtest_status(task_id: str):
    """
    查询回测任务状态
    """
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return {"state": "PENDING", "status": "Pending..."}
    elif task_result.state != 'FAILURE':
        result = task_result.result
        if result and isinstance(result, dict) and result.get("status") == "failed":
             return {
                "state": "FAILURE",
                "error": result.get("error")
            }
            
        return {
            "state": task_result.state,
            "result": result
        }
    else:
        return {
            "state": "FAILURE",
            "error": str(task_result.result)
        }

@router.get("/strategies")
def list_strategies():
    return ["SmaCross"]
