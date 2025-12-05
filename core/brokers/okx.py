import backtrader as bt
import ccxt
import time
from datetime import datetime, timedelta
from collections import deque
from config.settings import settings

class OKXStore(object):
    """
    Singleton Store to hold CCXT Exchange instance
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.exchange = ccxt.okx({
            'apiKey': settings.OKX_API_KEY,
            'secret': settings.OKX_SECRET,
            'password': settings.OKX_PASSPHRASE,
            'enableRateLimit': True,
        })
        
        if settings.OKX_DEMO:
            self.exchange.set_sandbox_mode(True)

    def get_broker(self):
        return OKXBroker(store=self)

    def get_data(self, symbol, timeframe=bt.TimeFrame.Minutes, compression=1, **kwargs):
        return OKXData(store=self, symbol=symbol, timeframe=timeframe, compression=compression, **kwargs)

class OKXBroker(bt.BrokerBase):
    """
    Custom Broker for OKX via CCXT
    """
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.exchange = store.exchange
        self._cash = 0
        self._value = 0

    def getcash(self):
        # Fetch balance from OKX
        try:
            balance = self.exchange.fetch_balance()
            # Assuming USDT based trading for simplicity in total value calculation
            self._cash = balance['USDT']['free'] if 'USDT' in balance else 0
            self._value = balance['total']['USDT'] if 'USDT' in balance.get('total', {}) else 0
        except Exception as e:
            print(f"Error fetching balance: {e}")
        return self._cash

    def getvalue(self):
        self.getcash() # Update value
        return self._value

    def getposition(self, data):
        # TODO: Implement position fetching
        # CCXT fetch_positions or fetch_balance depending on spot/futures
        return super().getposition(data)

    def submit(self, order):
        # Place order via CCXT
        symbol = order.data.dataname
        side = 'buy' if order.isbuy() else 'sell'
        order_type = 'market' if order.exectype == bt.Order.Market else 'limit'
        amount = order.size
        price = order.price if order_type == 'limit' else None

        try:
            print(f"Submitting OKX Order: {side} {amount} {symbol} @ {price or 'Market'}")
            # CCXT create_order(symbol, type, side, amount, price=None, params={})
            response = self.exchange.create_order(symbol, order_type, side, amount, price)
            order.submit(self)
            order.completed() # In real implementation, we should track status via fetch_order
            print(f"OKX Order Placed: {response['id']}")
            return order
        except Exception as e:
            print(f"OKX Order Failed: {e}")
            order.reject(self)
            return None

class OKXData(bt.feed.DataBase):
    """
    Polling Data Feed for OKX using CCXT
    """
    def __init__(self, store, symbol, **kwargs):
        super().__init__(**kwargs)
        self.store = store
        self.symbol = symbol
        self.exchange = store.exchange
        self.last_dt = None
        
        # Set timeframe string for CCXT
        self.tf_map = {
            bt.TimeFrame.Minutes: '1m',
            bt.TimeFrame.Days: '1d',
        }
        self.ccxt_tf = self.tf_map.get(self.p.timeframe, '1m')

    def start(self):
        super().start()
        # Initial fetch could be done here

    def _load(self):
        # Poll for new data
        # In a real live feed, we need to manage time and sleep to avoid rate limits
        # Backtrader calls _load in a loop.
        
        try:
            # Fetch last few candles
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.ccxt_tf, limit=5)
            if not ohlcv:
                return False
            
            # Get the latest completed candle (usually index -2, or -1 if just closed)
            # CCXT returns [timestamp, open, high, low, close, volume]
            # timestamp is ms
            
            last_candle = ohlcv[-1]
            dt = datetime.fromtimestamp(last_candle[0] / 1000.0)
            
            if self.last_dt and dt <= self.last_dt:
                # No new data yet
                # Return False or create a delay?
                # Backtrader expects _load to return True if data is loaded
                # For live feeds, we often need to handle 'no new data' gracefully
                # A simple trick in polling feeds is to return False but not stop the feed
                # But bt DataBase stops if False is returned. 
                # We need to wait here until new data arrives for 'Live' feel or use a Queue
                time.sleep(5) # Simple polling wait
                return False # Retry logic needed or better architecture
            
            self.last_dt = dt
            
            self.lines.datetime[0] = bt.date2num(dt)
            self.lines.open[0] = last_candle[1]
            self.lines.high[0] = last_candle[2]
            self.lines.low[0] = last_candle[3]
            self.lines.close[0] = last_candle[4]
            self.lines.volume[0] = last_candle[5]
            
            return True
            
        except Exception as e:
            print(f"Error fetching OKX data: {e}")
            return False


if __name__ == "__main__":
    import sys
    import os
    # Allow running this file directly for testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    okx_store = OKXStore.get_instance()
    okxBroker = okx_store.get_broker()
    print(okxBroker.getcash())
    
    symbol = "BTC/USDT"
    timeframe = '1m'
    limit = 5
    ohlcv = okx_store.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    for candle in ohlcv[-3:]:  # 显示最后3条
        timestamp, open_price, high, low, close, volume = candle
        dt = datetime.fromtimestamp(timestamp / 1000.0)
        print(f"{dt.strftime('%Y-%m-%d %H:%M:%S'):<20} "
              f"{open_price:<10.2f} {high:<10.2f} {low:<10.2f} "
              f"{close:<10.2f} {volume:<15.6f}")