import sqlite3
from pathlib import Path
from typing import List, Optional

from ..db import get_db_path


def init_table(db_path: Optional[Path] = None):
    dbf = db_path or get_db_path()
    dbf.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_restaurants(db_path: Optional[Path] = None) -> List[str]:
    dbf = db_path or get_db_path()
    if not dbf.exists():
        return []
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM restaurants ORDER BY id")
        rows = cur.fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def add_restaurant(name: str, db_path: Optional[Path] = None) -> bool:
    dbf = db_path or get_db_path()
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO restaurants (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    finally:
        conn.close()


def remove_restaurant(name: str, db_path: Optional[Path] = None) -> bool:
    dbf = db_path or get_db_path()
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM restaurants WHERE name = ?", (name,))
        changed = cur.rowcount
        conn.commit()
        return changed > 0
    finally:
        conn.close()
