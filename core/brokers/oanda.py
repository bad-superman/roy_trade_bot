import backtrader as bt
from config.settings import settings

class OandaBroker:
    """
    Oanda Broker Wrapper for Backtrader
    This class helps configuring Cerebro to use Oanda Store for live trading
    """
    def __init__(self, token=None, account_id=None, practice=True):
        self.token = token or settings.OANDA_TOKEN
        self.account_id = account_id or settings.OANDA_ACCOUNT_ID
        self.practice = practice

    def get_store(self):
        if not self.token or not self.account_id:
            raise ValueError("Oanda API Token and Account ID must be provided in settings or init.")
        
        store_kwargs = dict(
            token=self.token,
            account=self.account_id,
            practice=self.practice,
            notif_transactions=True
        )
        return bt.stores.OandaStore(**store_kwargs)

    def get_broker(self):
        store = self.get_store()
        return store.getbroker()
    
    def get_data(self, symbol, timeframe=bt.TimeFrame.TimeFrame.Minutes, compression=1, **kwargs):
        """
        Returns a Data Feed from Oanda Store
        """
        store = self.get_store()
        
        # Map common symbols if necessary, Oanda uses EUR_USD format
        oanda_symbol = symbol.replace("/", "_").replace("USD", "_USD").replace("EUR", "EUR_") if "_" not in symbol else symbol
        # Simple heuristic fix for standard pairs like EURUSD -> EUR_USD
        if len(symbol) == 6 and "_" not in symbol:
             oanda_symbol = f"{symbol[:3]}_{symbol[3:]}"
             
        return store.getdata(
            dataname=oanda_symbol,
            timeframe=timeframe,
            compression=compression,
            **kwargs
        )

