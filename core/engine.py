import matplotlib
matplotlib.use('Agg')  # Prevent GUI backend issues
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
        self.data = None # Store dataframe for plotting later
        
    def load_data(self, symbol="EURUSD", timeframe=bt.TimeFrame.Minutes):
        # TODO: Replace with MongoDB fetch
        # Mocking data for now using simple generated data or file
        # For demonstration, let's create a dummy dataframe
        
        # 模拟生成一些数据
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='1H')
        self.data = pd.DataFrame({
            'open': 1.1000 + (np.random.randn(len(dates)) / 100),
            'high': 1.1050 + (np.random.randn(len(dates)) / 100),
            'low': 1.0950 + (np.random.randn(len(dates)) / 100),
            'close': 1.1020 + (np.random.randn(len(dates)) / 100),
            'volume': 1000
        }, index=dates)
        
        feed = bt.feeds.PandasData(dataname=self.data)
        self.cerebro.adddata(feed)

    def add_strategy(self, strategy_class, **kwargs):
        self.cerebro.addstrategy(strategy_class, **kwargs)

    def add_analyzers(self):
        # 夏普率需要足够的样本数和正确的 timeframe 参数
        # timeframe=bt.TimeFrame.Minutes, compression=60 (如果是小时线)
        # riskfreerate 默认是 0.01 (1%)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, compression=1, riskfreerate=0.0)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        # Add transactions analyzer to get trade details
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name='transactions')

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
        
        # Extract chart data (OHLC)
        chart_data = []
        if self.data is not None:
            chart_data = []
            # Resample if too many points to avoid browser lag
            df_chart = self.data.copy()
            if len(df_chart) > 2000:
               df_chart = df_chart.iloc[::max(1, len(df_chart)//1000)] # Simple thinning
            
            for index, row in df_chart.iterrows():
                chart_data.append([
                    index.strftime("%Y-%m-%d %H:%M"),
                    row['open'],
                    row['close'],
                    row['low'],
                    row['high']
                ])
        
        # Extract Trade Signals (Buy/Sell points) from observers or analyze trades
        # Using transactions analyzer
        transactions = strat.analyzers.transactions.get_analysis()
        trade_markers = []
        for dt, txn_info in transactions.items():
            # txn_info is a list of [amount, price, sid, symbol, value]
            # We only care about the first one for simplicity or iterate
            # amount > 0 is buy, < 0 is sell
            amount = txn_info[0][0]
            price = txn_info[0][1]
            trade_markers.append({
                "date": dt.strftime("%Y-%m-%d %H:%M"),
                "type": "buy" if amount > 0 else "sell",
                "price": price,
                "amount": abs(amount)
            })

        return {
            "final_value": self.cerebro.broker.getvalue(),
            "pnl": self.cerebro.broker.getvalue() - self.initial_cash,
            # SharpeRatio may return None if insufficient data or no trades
            "sharpe_ratio": sharpe.get('sharperatio', 0.0) if sharpe.get('sharperatio') is not None else 0.0,
            "max_drawdown": drawdown.get('max', {}).get('drawdown', 0.0),
            "total_trades": trades.get('total', {}).get('total', 0),
            "win_rate": trades.get('won', {}).get('total', 0) / max(1, trades.get('total', {}).get('total', 1)),
            "chart_data": chart_data, # OHLC data for charts
            "trade_markers": trade_markers # Buy/Sell points
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
