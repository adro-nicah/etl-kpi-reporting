import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from extract_postgres import extract_postgres
from etl.extract_mongodb import extract_mongodb

def data_quality_checks(df):
    # 1. Null checks
    if df.isnull().any().any():
        raise ValueError("Data Quality Error: Null values detected")

    # 2. Duplicate checks
    if df.duplicated().any():
        raise ValueError("Data Quality Error: Duplicate rows detected")

    # 3. Data type checks
    if not pd.api.types.is_numeric_dtype(df["kpi_value"]):
        raise TypeError("Data Quality Error: kpi_value must be numeric")

    if not pd.api.types.is_datetime64_any_dtype(df["week"]):
        raise TypeError("Data Quality Error: week must be a datetime")

    # 4. Business rule checks
    if (df["kpi_value"] < 0).any():
        raise ValueError("Data Quality Error: Negative KPI values detected")

    print("Data quality checks passed")


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

    # Fill missing event counts with 0
    merged_df["event_count"] = merged_df["event_count"].fillna(0)

    # Run data quality checks
    data_quality_checks(merged_df)

    # Save final dataset for Power BI
    merged_df.to_csv("data/weekly_kpi_report.csv", index=False)

    return merged_df



if __name__ == "__main__":
    df = transform_and_merge()
    print(df.head())
