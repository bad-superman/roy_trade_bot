import sys
import os
import datetime
import random
import pymongo
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

def generate_mock_data(symbol, start_date, days=30):
    client = pymongo.MongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB_NAME]
    collection = db[f"bars_{symbol}_1h"]
    
    # Clear existing
    collection.delete_many({})
    
    base_price = 1800.0 if "XAU" in symbol else 1.1000
    current_price = base_price
    
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    records = []
    
    print(f"Generating data for {symbol}...")
    
    for i in range(days * 24):
        dt = start + datetime.timedelta(hours=i)
        
        # Random walk
        change = (random.random() - 0.5) * (base_price * 0.005)
        open_p = current_price
        close_p = current_price + change
        high_p = max(open_p, close_p) + random.random() * (base_price * 0.001)
        low_p = min(open_p, close_p) - random.random() * (base_price * 0.001)
        
        record = {
            "datetime": dt,
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": int(random.random() * 1000)
        }
        records.append(record)
        current_price = close_p

    if records:
        collection.insert_many(records)
        print(f"Inserted {len(records)} records into {collection.name}")

if __name__ == "__main__":
    generate_mock_data("XAUUSD", "2023-01-01")
    generate_mock_data("EURUSD", "2023-01-01")

