import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transform_and_merge import transform_and_merge

def export_to_csv():
    df = transform_and_merge()

    output_path = os.path.join("output", "weekly_kpi_report.csv")
    df.to_csv(output_path, index=False)

    print(f"Weekly KPI report exported to {output_path}")

if __name__ == "__main__":
    export_to_csv()
