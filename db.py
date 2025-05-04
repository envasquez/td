from functools import wraps
from sqlite3 import Connection, connect

import pandas as pd


def db_conn(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        c: Connection = connect(database="tournaments.db")
        try:
            return func(c, *args, **kwargs)
        finally:
            c.close()

    return wrapper


def load_query(filename: str) -> str:
    with open(filename, mode="r", encoding="utf-8") as f:
        return f.read()


def load_data(c: Connection, q_file: str) -> pd.DataFrame:
    return pd.read_sql_query(load_query(q_file), c)
