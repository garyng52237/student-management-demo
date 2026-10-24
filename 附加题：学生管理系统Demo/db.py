import sqlite3
from pathlib import Path

from flask import g


BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "student.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_FILE)
    db.execute("PRAGMA foreign_keys = ON")
    with SCHEMA_FILE.open("r", encoding="utf-8") as file:
        db.executescript(file.read())
    db.commit()
    db.close()


init_db()
