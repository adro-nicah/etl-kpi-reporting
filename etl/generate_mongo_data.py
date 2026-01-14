import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config.db_config import MONGO_CONFIG

business_units = [
    "Sales", "Finance", "Operations", "Supply Chain", "IT Services"
]

event_types = [
    "Incident", "Maintenance", "Audit", "Outage"
]

def generate_logs():
    client = MongoClient(
        host=MONGO_CONFIG["host"],
        port=MONGO_CONFIG["port"]
    )

    collection = client[MONGO_CONFIG["database"]][MONGO_CONFIG["collection"]]

    start_date = datetime(2024, 1, 1)

    logs = []
    for _ in range(1000):
        logs.append({
            "business_unit": random.choice(business_units),
            "event_type": random.choice(event_types),
            "duration_hours": round(random.uniform(0.5, 12), 2),
            "event_date": start_date + timedelta(days=random.randint(0, 365))
        })

    collection.insert_many(logs)
    print("Large MongoDB log dataset generated successfully.")

if __name__ == "__main__":
    generate_logs()
