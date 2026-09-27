from pathlib import Path
import sqlite3

from fastapi import FastAPI


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "warehouse.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


app = FastAPI(
    title="Warehouse Management API",
    description="Backend для АСУ складского учёта",
    version="0.1.0",
)


def get_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    if DB_PATH.exists():
        return

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_db() as connection:
        connection.executescript(schema)


init_db()


@app.get("/")
def root():
    return {
        "message": "Warehouse API is running"
    }


@app.get("/health")
def health():
    with get_db() as connection:
        connection.execute("SELECT 1")

    return {
        "status": "ok",
        "database": "ok"
    }