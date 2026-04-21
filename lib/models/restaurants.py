import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

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
                name TEXT NOT NULL UNIQUE,
                distance INTEGER,
                price INTEGER
            )
            """
        )
        # 舊資料庫可能缺少 distance / price 欄位，用 ALTER TABLE 補上
        existing = {row[1] for row in cur.execute("PRAGMA table_info(restaurants)")}
        if "distance" not in existing:
            cur.execute("ALTER TABLE restaurants ADD COLUMN distance INTEGER")
        if "price" not in existing:
            cur.execute("ALTER TABLE restaurants ADD COLUMN price INTEGER")
        conn.commit()
    finally:
        conn.close()


def get_restaurants(db_path: Optional[Path] = None) -> List[Dict]:
    dbf = db_path or get_db_path()
    if not dbf.exists():
        return []
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, distance, price FROM restaurants ORDER BY id")
        rows = cur.fetchall()
        return [{"name": r[0], "distance": r[1], "price": r[2]} for r in rows]
    finally:
        conn.close()


def add_restaurant(
    name: str,
    distance: Optional[int] = None,
    price: Optional[int] = None,
    db_path: Optional[Path] = None,
) -> bool:
    dbf = db_path or get_db_path()
    conn = sqlite3.connect(dbf)
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO restaurants (name, distance, price) VALUES (?, ?, ?)",
                (name, distance, price),
            )
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
