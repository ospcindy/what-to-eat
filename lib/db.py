import os
import platform
import sqlite3
from pathlib import Path
from typing import Optional, Iterator
from contextlib import contextmanager


DB_FILENAME = "what_to_eat.db"


def get_user_data_dir(app_name: str = "what-to-eat") -> Path:
    """Return a suitable per-user data directory for the current platform.

    - Windows: %LOCALAPPDATA%\<app_name>
    - macOS: ~/Library/Application Support/<app_name>
    - Linux/other: ~/.local/share/<app_name>
    """
    if os.getenv("WHAT_TO_EAT_DATA_DIR"):
        return Path(os.getenv("WHAT_TO_EAT_DATA_DIR"))

    system = platform.system()
    if system == "Windows":
        local_app = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if local_app:
            return Path(local_app) / app_name
        # fallback to home
        return Path.home() / f"AppData/Local/{app_name}"
    if system == "Darwin":
        return Path.home() / "Library/Application Support" / app_name
    # default for Linux and others
    return Path.home() / ".local/share" / app_name


def get_db_path() -> Path:
    """Return the default DB path in the user's data directory.

    Note: callers may pass an explicit `db_path` to functions to override.
    """
    data_dir = get_user_data_dir()
    return data_dir / DB_FILENAME


def ensure_db_dir(db_path: Optional[Path] = None) -> Path:
    dbf = db_path or get_db_path()
    dbf.parent.mkdir(parents=True, exist_ok=True)
    return dbf


@contextmanager
def connect(db_path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    """Context manager yielding a sqlite3.Connection. Ensures parent dir exists."""
    dbf = ensure_db_dir(db_path)
    conn = sqlite3.connect(dbf)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Optional[Path] = None):
    """Ensure DB directory exists and create default tables via models.

    This function will call the models' init routines to create their tables.
    """
    ensure_db_dir(db_path)
    # create model tables (import inside function to avoid import cycles)
    from .models import restaurants as _restaurants

    _restaurants.init_table(db_path=db_path)


# Backwards-compatible wrappers that delegate to the restaurants model.
def get_restaurants(db_path: Optional[Path] = None):
    from .models import restaurants as _restaurants

    return _restaurants.get_restaurants(db_path=db_path)


def add_restaurant(name: str, db_path: Optional[Path] = None) -> bool:
    from .models import restaurants as _restaurants

    return _restaurants.add_restaurant(name, db_path=db_path)


def remove_restaurant(name: str, db_path: Optional[Path] = None) -> bool:
    from .models import restaurants as _restaurants

    return _restaurants.remove_restaurant(name, db_path=db_path)
