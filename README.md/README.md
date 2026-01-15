# ETL KPI Business Reporting Pipeline

## Overview
This project implements a fully automated ETL (Extract, Transform, Load) pipeline for KPI-based business reporting. The solution integrates structured KPI data from PostgreSQL with semi-structured operational log data from MongoDB, performs data quality checks and weekly aggregations, and produces a unified dataset suitable for business intelligence dashboards and executive reporting.

The pipeline is designed to be reliable, auditable, and schedulable, reflecting real-world data engineering practices.

---

## Architecture
**Data Sources**
- PostgreSQL: Business KPIs (e.g., KPI name, value, transaction date, business unit)
- MongoDB: Operational event logs (event type, event date, business unit)

**ETL Stages**
1. **Extract**
   - KPI data extracted from PostgreSQL
   - Event logs extracted from MongoDB
2. **Transform**
   - Column standardisation
   - Date normalization
   - Weekly aggregation
   - KPI summarisation
   - Event count aggregation
   - Data quality validation
3. **Load**
   - Merged weekly KPI and event dataset
   - Output made available for dashboards and reporting tools

---

## Project Structure

etl-kpi-reporting/
│
├── etl/
│ ├── extract_postgres.py
│ ├── extract_mongodb.py
│ ├── transform_and_merge.py
│ └── run_etl.py
│
├── logs/
│ └── etl-run.log
│
├── requirements.txt
├── README.md
└── .gitignore


---

## Technologies Used
- Python 3.x
- Pandas
- PostgreSQL
- MongoDB
- Windows Task Scheduler
- Git & GitHub

---

## Automation & Scheduling
The ETL pipeline is automated using **Windows Task Scheduler**, enabling unattended execution at defined intervals. Each run is logged to ensure traceability and auditability.

---

## Logging & Monitoring
All ETL executions are logged with timestamps, extraction counts, transformation status, and completion indicators. Logs provide operational transparency and simplify troubleshooting.

---

## How to Run Manually
```bash
python etl/run_etl.py


Author

Phalo Kobamelo
Business Intelligence & Data Analytics


