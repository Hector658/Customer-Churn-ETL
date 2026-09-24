import os
from pathlib import Path

import numpy as np
import pandas as pd
from dagster import asset
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR"))


def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def drop_array_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    array_columns = [
        col for col in df.columns
        if df[col].apply(lambda x: isinstance(x, (list, np.ndarray))).any()
    ]
    if array_columns:
        df = df.drop(columns=array_columns)
    return df


def load_table(table_name: str, file_name: str) -> int:
    engine = get_engine()
    file_path = RAW_DATA_DIR / file_name
    df = pd.read_parquet(file_path)
    df = drop_array_columns(df, table_name)

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.commit()

    inspector = inspect(engine)
    table_exists = inspector.has_table(table_name, schema="raw")

    if table_exists:
        with engine.begin() as conn:
            conn.execute(text(f'TRUNCATE TABLE raw."{table_name}"'))
        df.to_sql(table_name, engine, schema="raw", if_exists="append", index=False, chunksize=5000)
    else:
        df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False, chunksize=5000)

    return len(df)


@asset
def raw_customers() -> int:
    return load_table("customers", "customers.parquet")


@asset
def raw_bets() -> int:
    return load_table("bets", "bets.parquet")


@asset
def raw_events() -> int:
    return load_table("events", "events.parquet")


@asset
def raw_participants() -> int:
    return load_table("participants", "participants.parquet")