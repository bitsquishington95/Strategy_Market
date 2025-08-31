# app/db/connection.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "ceos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_conn = None

def get_db_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn

def init_db():
    conn = get_db_conn()
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as fh:
        conn.executescript(fh.read())
    conn.commit()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")