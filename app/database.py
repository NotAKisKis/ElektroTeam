import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "elektromanager.sqlite3"

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    return connection



def init_db():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    connection = get_connection()
    try:
        connection.executescript(sql)
    finally:
        connection.close()
