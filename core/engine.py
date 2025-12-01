import backtrader as bt
import datetime
import numpy as np
import pandas as pd
import json
from core.strategy.base import SmaCross  # 暂时硬编码，后续做动态加载

class BacktestEngine:
    def __init__(self, start_date, end_date, initial_cash=10000.0):
        self.cerebro = bt.Cerebro()
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        self.cerebro.broker.setcash(initial_cash)
        
    def load_data(self, symbol="EURUSD", timeframe=bt.TimeFrame.Minutes):
        # TODO: Replace with MongoDB fetch
        # Mocking data for now using simple generated data or file
        # For demonstration, let's create a dummy dataframe
        
        # 模拟生成一些数据
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='1H')
        data = pd.DataFrame({
            'open': 1.1000 + (np.random.randn(len(dates)) / 100),
            'high': 1.1050 + (np.random.randn(len(dates)) / 100),
            'low': 1.0950 + (np.random.randn(len(dates)) / 100),
            'close': 1.1020 + (np.random.randn(len(dates)) / 100),
            'volume': 1000
        }, index=dates)
        
        feed = bt.feeds.PandasData(dataname=data)
        self.cerebro.adddata(feed)

    def add_strategy(self, strategy_class, **kwargs):
        self.cerebro.addstrategy(strategy_class, **kwargs)

    def add_analyzers(self):
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    def run(self):
        self.add_analyzers()
        results = self.cerebro.run()
        strat = results[0]
        
        return self._parse_results(strat)

    def _parse_results(self, strat):
        # Extract analyzer results
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        
        return {
            "final_value": self.cerebro.broker.getvalue(),
            "pnl": self.cerebro.broker.getvalue() - self.initial_cash,
            "sharpe_ratio": sharpe.get('sharperatio', 0.0),
            "max_drawdown": drawdown.get('max', {}).get('drawdown', 0.0),
            "total_trades": trades.get('total', {}).get('total', 0),
            "win_rate": trades.get('won', {}).get('total', 0) / max(1, trades.get('total', {}).get('total', 1))
        }

def run_backtest_task(strategy_name: str, params: dict, start_date: str, end_date: str):
    # 解析日期
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    engine = BacktestEngine(start, end)
    engine.load_data() # Mock data
    
    # 这里应该根据 strategy_name 动态加载
    # 暂时只支持 SmaCross
    if strategy_name == "SmaCross":
        engine.add_strategy(SmaCross, **params)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")
        
    result = engine.run()
    return result

