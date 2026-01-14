import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config.db_config import POSTGRES_CONFIG

business_kpis = {
    "Sales": ["Revenue", "Units Sold", "Customer Growth"],
    "Finance": ["Cost", "Profit Margin", "Budget Variance"],
    "Operations": ["Downtime Hours", "Throughput"],
    "Supply Chain": ["Lead Time", "Inventory Turnover"],
    "IT Services": ["Incident Count", "Resolution Time"]
}

def generate_data():
    conn = psycopg2.connect(
        host=POSTGRES_CONFIG["host"],
        database=POSTGRES_CONFIG["database"],
        user=POSTGRES_CONFIG["user"],
        password=POSTGRES_CONFIG["password"]
    )
    cur = conn.cursor()

    start_date = datetime(2024, 1, 1)
    weeks = 52

    for week in range(weeks):
        date = start_date + timedelta(weeks=week)

        for unit, kpis in business_kpis.items():
            for kpi in kpis:
                value = round(random.uniform(50, 500), 2)

                cur.execute("""
                    INSERT INTO kpi_transactions
                    (business_unit, kpi_name, kpi_value, transaction_date)
                    VALUES (%s, %s, %s, %s)
                """, (unit, kpi, value, date))

    conn.commit()
    cur.close()
    conn.close()

    print("Large KPI dataset generated successfully.")

if __name__ == "__main__":
    generate_data()

