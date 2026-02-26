# Minimal dbt Core Project (DuckDB)

This repository includes a minimal dbt Core project using the DuckDB adapter and a local DuckDB database file.

## Project layout

- `dbt_project.yml`: dbt project configuration.
- `seeds/companies.csv`, `seeds/leads.csv`: source seed data.
- `models/staging/stg_companies.sql`, `models/staging/stg_leads.sql`: staging models.
- `models/marts/leads_by_segment.sql`: simple aggregate mart.
- `models/staging/schema.yml`: model descriptions and tests.

## 1) Install dependencies

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install dbt-core dbt-duckdb
```

### macOS (Terminal)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install dbt-core dbt-duckdb
```

## 2) Configure profile

Create `~/.dbt/profiles.yml` with:

```yaml
brownrice_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: brownrice.duckdb
      threads: 1
```

## 3) Run dbt

From this repo root:

### Windows (PowerShell)

```powershell
dbt seed
dbt build
dbt docs generate
# optional:
# dbt docs serve
```

### macOS (Terminal)

```bash
dbt seed
dbt build
dbt docs generate
# optional:
# dbt docs serve
```

## Included tests

In `models/staging/schema.yml`:

- `stg_leads.lead_id`: `unique`, `not_null`
- `stg_leads.company_id`: `not_null`, `relationships` to `stg_companies.company_id`
