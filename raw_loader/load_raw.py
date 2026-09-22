import os
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR"))

# Table name -> parquet file name
TABLES = {
    "customers": "customers.parquet",
    "bets": "bets.parquet",
    "events": "events.parquet",
    "participants": "participants.parquet",
}


def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def drop_array_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    array_columns = [
        col for col in df.columns
        if df[col].apply(lambda x: isinstance(x, (list, np.ndarray))).any()
    ]
    if array_columns:
        print(f"  Skipping array-type column(s) in {table_name}: {array_columns}")
        df = df.drop(columns=array_columns)
    return df


def load_table(engine, table_name: str, file_name: str) -> None:
    file_path = RAW_DATA_DIR / file_name
    print(f"Reading {file_path}...")
    df = pd.read_parquet(file_path)
    df = drop_array_columns(df, table_name)

    inspector = inspect(engine)
    table_exists = inspector.has_table(table_name, schema="raw")

    if table_exists:
        print(f"Truncating raw.{table_name} and reloading {len(df)} rows...")
        with engine.begin() as conn:
            conn.execute(text(f'TRUNCATE TABLE raw."{table_name}"'))
        df.to_sql(table_name, engine, schema="raw", if_exists="append", index=False)
    else:
        print(f"Creating raw.{table_name} and loading {len(df)} rows...")
        df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False)

    print(f"Done: raw.{table_name}")


def main():
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.commit()

    for table_name, file_name in TABLES.items():
        load_table(engine, table_name, file_name)

    print("All tables loaded successfully.")


if __name__ == "__main__":
    main()