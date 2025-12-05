# Roy Trade Bot - 量化交易系统

## 项目简介
基于 Python Backtrader 二次开发的外汇/黄金量化交易系统，包含策略管理、回测、实盘交易、风控和行情模块。

## 技术栈
- **Backend**: Python 3.10, FastAPI, Celery
- **Quant Core**: Backtrader
- **Database**: MySQL (配置/账户), MongoDB (行情/日志), Redis (缓存/MQ)
- **Frontend**: React/Vue (待定)

## 快速启动

### 环境要求
- Docker & Docker Compose

### 启动服务
```bash
docker compose up -d
```

### 访问接口
- API文档: http://localhost:8000/docs

