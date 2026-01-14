import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pymongo import MongoClient
from config.db_config import MONGO_CONFIG

def extract_mongodb():
    client = MongoClient(
        host=MONGO_CONFIG["host"],
        port=MONGO_CONFIG["port"]
    )

    db = client[MONGO_CONFIG["database"]]
    collection = db[MONGO_CONFIG["collection"]]

    data = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(data)

    return df

if __name__ == "__main__":
    df = extract_mongodb()
    print(df.columns)
    print(df.head())
