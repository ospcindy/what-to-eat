from pathlib import Path
import sys


# ensure project root is importable when running pytest from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import db
from lib.models import restaurants


def test_restaurant_crud(tmp_path):
    db_path = tmp_path / "what_to_eat_test.db"

    # initialize DB (creates table)
    db.init_db(db_path=db_path)
    assert db_path.exists()

    # initially empty
    assert restaurants.get_restaurants(db_path=db_path) == []

    # add new restaurant
    assert restaurants.add_restaurant("單品A", db_path=db_path) is True

    # duplicate add returns False
    assert restaurants.add_restaurant("單品A", db_path=db_path) is False

    # read back
    assert restaurants.get_restaurants(db_path=db_path) == ["單品A"]

    # remove
    assert restaurants.remove_restaurant("單品A", db_path=db_path) is True
    assert restaurants.get_restaurants(db_path=db_path) == []
