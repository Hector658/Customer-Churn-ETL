\# Customer Churn ETL Pipeline



An end-to-end ETL pipeline for a synthetic sports betting platform, built to analyze customer activity, segmentation, and retention. Raw data flows through a layered transformation process (raw → staging → marts) using Python, PostgreSQL, and dbt.



This project is a companion to a churn analysis EDA originally done in R — see \[customer-churn-dataset](https://github.com/Hector658/customer-churn-dataset) for the dataset generation and exploratory analysis this pipeline is built on.



\## Architecture



```mermaid

flowchart LR

&#x20;   A\[Parquet files<br/>customers, bets, events, participants] -->|Python loader| B\[(Postgres: raw)]

&#x20;   B -->|dbt staging models| C\[(Postgres: staging)]

&#x20;   C -->|dbt marts models| D\[(Postgres: marts)]

&#x20;   D --> E\[customer\_features]

&#x20;   D --> F\[monthly\_activity]

&#x20;   D --> G\[cohort\_retention]

```



\- \*\*Extract\*\*: a Python script reads synthetic parquet files and loads them into a `raw` schema in Postgres.

\- \*\*Transform (staging)\*\*: dbt models clean and standardize each raw table into a `staging` schema, with automated data quality tests (uniqueness, non-null keys, referential integrity).

\- \*\*Transform (marts)\*\*: dbt models build business-ready tables in a `marts` schema — per-customer features, monthly activity trends, and cohort retention — ready for analysis, dashboards, or downstream ML.



\## Tech stack



\- \*\*PostgreSQL 16\*\* (via Docker) — the data warehouse

\- \*\*Python\*\* (pandas, SQLAlchemy, psycopg2) — the extract/load step

\- \*\*dbt-postgres\*\* — transformations, testing, and documentation

\- \*\*Docker Compose\*\* — reproducible local environment



\## Project structure


## Setup

### 1. Prerequisites
- Docker Desktop
- Python 3.12+

### 2. Clone and set up the environment
```bash
git clone https://github.com/Hector658/Customer-Churn-ETL.git
cd customer-churn-etl
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
```

### 3. Generate the source data
The parquet files are not committed to this repo. Run the dataset generation notebook from [customer-churn-dataset](https://github.com/Hector658/customer-churn-dataset) and place the resulting files in `data/raw/`:
- `customers.parquet`
- `bets.parquet`
- `events.parquet`
- `participants.parquet`

### 4. Configure environment variables
Create a `.env` file in the project root:



### 5. Start Postgres
```bash
docker compose up -d
```

### 6. Load raw data
```bash
python raw_loader/load_raw.py
```

### 7. Run the dbt pipeline
```bash
cd dbt_project
dbt run
dbt test
```

### 8. (Optional) Browse the documentation
```bash
dbt docs generate
dbt docs serve
```

## Data quality

The staging layer includes automated dbt tests covering:
- Primary key uniqueness and non-null constraints (`customers`, `events`, `participants`)
- Referential integrity between `bets` and `customers`/`events`

During development, these checks (and manual inspection) caught a real data bug: a staging model was initially pointed at the wrong source table, silently loading customer data into what should have been a participants table. This is documented as a reminder of why automated schema/data tests matter in a pipeline, beyond just "the query ran."

## Roadmap

- [ ] Orchestrate the pipeline with Dagster (currently run manually via CLI)
- [ ] Add an entity-relationship diagram and indexing notes
- [ ] Expose marts through SQL views for direct BI/reporting access





