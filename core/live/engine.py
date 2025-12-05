import backtrader as bt
import datetime
from core.strategy.base import SmaCross
from core.brokers.oanda import OandaBroker
from core.brokers.ib import IBBroker
from core.brokers.okx import OKXStore
from config.settings import settings

class LiveEngine:
    def __init__(self, strategy_class, params: dict, symbol: str = "EURUSD", broker_type: str = "oanda"):
        self.cerebro = bt.Cerebro()
        self.strategy_class = strategy_class
        self.params = params
        self.symbol = symbol
        self.broker_type = broker_type.lower()

    def setup(self):
        broker_instance = None
        
        if self.broker_type == "oanda":
            broker_instance = OandaBroker(practice=settings.OANDA_PRACTICE)
            print(f"Setup Oanda Live Trading for {self.symbol}")
        elif self.broker_type == "ib":
            broker_instance = IBBroker()
            print(f"Setup IB Live Trading for {self.symbol}")
        elif self.broker_type == "okx":
            # OKX implementation via CCXT wrapper
            store = OKXStore.get_instance()
            # Use custom wrapper methods
            broker = store.get_broker()
            self.cerebro.setbroker(broker)
            
            data = store.get_data(self.symbol)
            self.cerebro.adddata(data)
            print(f"Setup OKX Live Trading for {self.symbol}")
            
            # Add Strategy
            self.cerebro.addstrategy(self.strategy_class, **self.params)
            return # OKX setup done differently above, return early or refactor

        else:
            raise ValueError(f"Unsupported broker type: {self.broker_type}")

        # Set Broker & Data (For Oanda/IB)
        if self.broker_type in ["oanda", "ib"]:
            try:
                broker = broker_instance.get_broker()
                self.cerebro.setbroker(broker)
                
                data = broker_instance.get_data(self.symbol)
                self.cerebro.adddata(data)
            except Exception as e:
                print(f"Failed to setup broker {self.broker_type}: {e}")
                raise e
            
            # Add Strategy
            self.cerebro.addstrategy(self.strategy_class, **self.params)
        
        # Add Writers/Analyzers if needed for live monitoring (e.g. storing to DB)
        # self.cerebro.addwriter(...)

    def run(self):
        print("Starting Live Trading Engine...")
        try:
            results = self.cerebro.run()
            return results
        except KeyboardInterrupt:
            print("Live Trading Stopped by User")
        except Exception as e:
            print(f"Live Trading Error: {e}")
            raise e

if __name__ == "__main__":
    # Test Run (requires valid config)
    try:
        engine = LiveEngine(SmaCross, {'pfast': 10, 'pslow': 30}, symbol="EURUSD")
        engine.setup()
        engine.run()
    except Exception as e:
        print(f"Cannot run live engine test: {e}")

