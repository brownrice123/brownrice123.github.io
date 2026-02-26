# Metric Anomaly Monitoring (SQL + Python)

This project detects daily metric anomalies using a SQL-defined baseline and a Python runner.

## What it does

- Reads `data/daily_metrics.csv`.
- Computes a **7-day moving average baseline** using the **previous 7 days only**.
- Computes deviation: `(metric_value - baseline) / baseline`.
- Flags anomalies where `abs(deviation) >= 0.30` and baseline is available.
- Writes:
  - `outputs/flagged_days.csv`
  - `outputs/anomaly_report.md`

## Setup

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/run_monitoring.py
```

### macOS (Terminal)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_monitoring.py
```

## Files

- `sql/anomalies.sql` - anomaly logic in SQL (DuckDB reads CSV directly).
- `src/run_monitoring.py` - executes SQL, writes flagged CSV + Markdown report.
- `data/daily_metrics.csv` - sample input with intentional spikes/drops.
