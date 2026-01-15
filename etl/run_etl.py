import subprocess
import sys
from datetime import datetime

def run_script(script_path):
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    return result

log_file = "etl_run.log"

with open(log_file, "a") as log:
    log.write(f"\nETL Run started at {datetime.now()}\n")

    scripts = [
        "etl/extract_postgres.py",
        "etl/extract_mongodb.py",
        "etl/transform_and_merge.py"
    ]

    for script in scripts:
        log.write(f"Running {script}\n")
        result = run_script(script)

        if result.returncode == 0:
            log.write(f"{script} completed successfully\n")
        else:
            log.write(f"ERROR in {script}\n")
            log.write(result.stderr + "\n")
            break

    log.write("ETL Run completed\n")
