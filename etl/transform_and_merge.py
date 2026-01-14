import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from extract_postgres import extract_postgres
from etl.extract_mongodb import extract_mongodb

def transform_and_merge():
    kpi_df = extract_postgres()
    log_df = extract_mongodb()

    # Standardize column names
    kpi_df.columns = kpi_df.columns.str.lower()
    log_df.columns = log_df.columns.str.lower()

    # Convert dates
    kpi_df["transaction_date"] = pd.to_datetime(kpi_df["transaction_date"])
    log_df["event_date"] = pd.to_datetime(log_df["event_date"])

    # Weekly aggregation
    kpi_df["week"] = kpi_df["transaction_date"].dt.to_period("W").apply(lambda r: r.start_time)
    log_df["week"] = log_df["event_date"].dt.to_period("W").apply(lambda r: r.start_time)

    # Aggregate KPIs
    kpi_weekly = (
        kpi_df
        .groupby(["business_unit", "kpi_name", "week"], as_index=False)
        .agg({"kpi_value": "sum"})
    )

    # Aggregate logs
    log_weekly = (
        log_df
        .groupby(["business_unit", "event_type", "week"], as_index=False)
        .size()
        .rename(columns={"size": "event_count"})
    )

    # Merge datasets
    merged_df = pd.merge(
        kpi_weekly,
        log_weekly,
        on=["business_unit", "week"],
        how="left"
    )

    return merged_df

if __name__ == "__main__":
    df = transform_and_merge()
    print(df.head())
