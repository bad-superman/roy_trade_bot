import backtrader as bt
from config.settings import settings

class IBBroker:
    """
    Interactive Brokers Wrapper for Backtrader using IBStore
    """
    def __init__(self, host=None, port=None, client_id=None):
        self.host = host or settings.IB_HOST
        self.port = port or settings.IB_PORT
        self.client_id = client_id or settings.IB_CLIENT_ID

    def get_store(self):
        store_kwargs = dict(
            host=self.host,
            port=self.port,
            clientId=self.client_id,
            notifyall=False,  # Optional: tune based on needs
            _debug=False
        )
        return bt.stores.IBStore(**store_kwargs)

    def get_broker(self):
        store = self.get_store()
        return store.getbroker()
    
    def get_data(self, symbol, timeframe=bt.TimeFrame.Minutes, compression=1, **kwargs):
        """
        Returns a Data Feed from IB Store
        Symbol format for IB in backtrader usually requires specific formatting or contract objects.
        For simple Forex, e.g. 'EUR.USD' (Cash)
        """
        store = self.get_store()
        
        # IB specific symbol handling could be complex.
        # Assuming user passes standard pair like "EURUSD"
        # We might need to convert to IB format depending on asset class.
        # For Forex (CASH), IB often expects 'EUR' as symbol and 'USD' as currency.
        # But backtrader IB store often takes a string that it tries to parse or explicit contract.
        # Let's assume standard Backtrader IB format: 'EUR.USD-CASH-IDEALPRO'
        
        dataname = symbol
        if "XAU" in symbol:
             # Gold handling (Commodity) - Simplistic assumption
             dataname = f"{symbol}-CMDTY-SMART"
        elif len(symbol) == 6 and "USD" in symbol:
             # Simple Forex assumption
             base = symbol[:3]
             quote = symbol[3:]
             dataname = f"{base}.{quote}-CASH-IDEALPRO"

        return store.getdata(
            dataname=dataname,
            timeframe=timeframe,
            compression=compression,
            **kwargs
        )

