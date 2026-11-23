
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):


    root = Path(database.__file__).resolve().parent.parent
    shutil.copyfile(root / "schema.sql", tmp_path / "schema.sql")
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.sqlite3")


    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def category_id(client: TestClient):

    connection = database.get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO categories (name) VALUES (?)", ("Gniazdka",)
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


@pytest.fixture
def product_payload(category_id: int):
    return {
        "name": "Gniazdko elektryczne",
        "description": "Podwojne gniazdko 230V",
        "price_grosz": 2999,
        "stock": 15,
        "category_id": category_id,
        "discount_type": "percent",
        "discount_value": 10,
        "image_url": None,
    }
