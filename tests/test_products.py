
from app import database


def test_pt01_empty_catalog(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.json() == []


def test_pt02_catalog_with_products(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201

    response = client.get("/api/products")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == product_payload["name"]
    assert items[0]["stock"] == 15


def test_pt03_existing_product_by_id(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201
    product_id = created.json()["id"]

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["price_grosz"] == 2999


def test_pt04_unknown_product_is_404(client):
    response = client.get("/api/products/999999")
    assert response.status_code == 404
    assert isinstance(response.json()["detail"], str)


def test_pt05_valid_product_created(client, product_payload):
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 201
    result = response.json()
    assert isinstance(result["id"], int)
    assert result["name"] == product_payload["name"]
    assert result["discount_type"] == "percent"
    assert result["discount_value"] == 10
    assert result["created_at"]


def test_pt06_negative_price_is_rejected(client, product_payload):
    product_payload["price_grosz"] = -1
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422
    assert client.get("/api/products").json() == []


def test_pt07_negative_stock_is_rejected(client, product_payload):
    product_payload["stock"] = -2
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422
    assert client.get("/api/products").json() == []


def test_pt08_missing_name_is_rejected(client, product_payload):
    product_payload.pop("name")
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422
    assert client.get("/api/products").json() == []


def test_pt09_nonexistent_category_is_rejected(client, product_payload):
    product_payload["category_id"] = 999999
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422
    assert client.get("/api/products").json() == []


def test_pt10_create_then_read_same_data(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201
    product_id = created.json()["id"]
    read = client.get(f"/api/products/{product_id}")
    assert read.status_code == 200
    assert read.json() == created.json()


def test_empty_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_categories_after_inserting_one(client, category_id):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert response.json() == [
        {"id": category_id, "name": "Gniazdka", "description": None}
    ]


def test_invalid_id_type_returns_422(client):
    response = client.get("/api/products/not-an-integer")
    assert response.status_code == 422


def test_whitespace_only_name_is_rejected(client, product_payload):
    product_payload["name"] = "   "
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422


def test_discount_percent_above_100_is_rejected(client, product_payload):
    product_payload["discount_value"] = 101
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422


def test_fixed_discount_more_than_price_is_rejected(client, product_payload):
    product_payload["discount_type"] = "fixed"
    product_payload["discount_value"] = product_payload["price_grosz"] + 1
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422


def test_no_discount_requires_zero_value(client, product_payload):
    product_payload["discount_type"] = "none"
    product_payload["discount_value"] = 1
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422


def test_put_updates_product_and_preserves_id_and_created_at(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201
    old = created.json()

    new_data = {**product_payload, "stock": 25, "price_grosz": 3999,
                "discount_type": "fixed", "discount_value": 500}
    response = client.put(f"/api/products/{old['id']}", json=new_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["stock"] == 25
    assert updated["price_grosz"] == 3999
    assert updated["discount_type"] == "fixed"
    assert updated["id"] == old["id"]
    assert updated["created_at"] == old["created_at"]
    assert client.get(f"/api/products/{old['id']}").json() == updated


def test_put_unknown_product_returns_404(client, product_payload):
    response = client.put("/api/products/999999", json=product_payload)
    assert response.status_code == 404


def test_put_nonexistent_category_returns_422(client, product_payload):
    product_payload["category_id"] = 999999
    response = client.put("/api/products/999999", json=product_payload)
    assert response.status_code == 422


def test_delete_product_returns_204_and_then_404(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201
    product_id = created.json()["id"]

    deleted = client.delete(f"/api/products/{product_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/products/{product_id}").status_code == 404
    assert client.delete(f"/api/products/{product_id}").status_code == 404


def test_delete_unknown_product_returns_404(client):
    response = client.delete("/api/products/999999")
    assert response.status_code == 404


def test_data_persists_between_database_connections(client, product_payload):
    created = client.post("/api/products", json=product_payload)
    assert created.status_code == 201
    product_id = created.json()["id"]

    connection = database.get_connection()
    try:
        row = connection.execute(
            "SELECT name, stock FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        assert row is not None
        assert row["name"] == product_payload["name"]
        assert row["stock"] == product_payload["stock"]
    finally:
        connection.close()


def test_wrong_stock_type_is_rejected(client, product_payload):
    product_payload["stock"] = "not-a-number"
    response = client.post("/api/products", json=product_payload)
    assert response.status_code == 422
