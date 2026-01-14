import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine
from config.db_config import POSTGRES_CONFIG

def extract_postgres():
    engine = create_engine(
        f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
        f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )

    query = """
    SELECT business_unit,
           kpi_name,
           kpi_value,
           transaction_date
    FROM kpi_transactions;
    """

    df = pd.read_sql(query, engine)
    return df

if __name__ == "__main__":
    df = extract_postgres()
    print(df.head())
