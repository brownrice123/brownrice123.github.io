# SQL Checks as Code (SQLite)

Minimal Python project for running data-quality checks against a SQLite database using SQL assertion queries generated from YAML rules.

## Project structure

- `dq/runner.py`: CLI runner for checks.
- `checks.yaml`: Example checks config.
- `sample_data/make_sample_db.py`: Creates `sample_data/sample.db` with sample data (includes intentional failures).
- `requirements.txt`: Python dependencies.

## How to run

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python sample_data/make_sample_db.py
python -m dq.runner --db sample_data/sample.db --checks checks.yaml
```

### macOS (Terminal)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python sample_data/make_sample_db.py
python -m dq.runner --db sample_data/sample.db --checks checks.yaml
```

## Expected behavior

- Each check prints one line in the format:
  - `[PASS] <check name> - offending rows: 0`
  - `[FAIL] <check name> - offending rows: <n>`
- Exit code is:
  - `0` when all checks pass
  - `1` when any check fails
