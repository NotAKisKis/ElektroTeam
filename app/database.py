import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "elektromanager.sqlite3"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection



def init_db():
    schema_path = DB_PATH.parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    connection = get_connection()
    try:
        connection.executescript(sql)
    finally:
        connection.close()
