# ElektroManager — backend (ElektroTeam)

University project for WSB Merito Warszawa. Backend for an electronics shop built with **FastAPI + SQLite**.

## Current milestone

This repository provides a local-development API for browsing categories/products and creating, replacing and deleting products. The catalog and admin page UI are built separately by Oleksii. Browser-side integration and end-to-end UI testing are **outside this backend milestone**.

> **Security:** This development build does not have authentication. `POST`, `PUT` and `DELETE` are unrestricted. Run it locally on `127.0.0.1` only; do **not** expose it as a public service.

## Requirements

- Python 3.10+ (3.11+ recommended).
- SQLite 3.37+ (the schema uses `STRICT` tables). Verify: `python -c "import sqlite3; print(sqlite3.sqlite_version)"`.

### Setup (Windows PowerShell, from `ElektroTeam/`)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Local links:

- API: `http://127.0.0.1:8000`
- Swagger/OpenAPI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

On startup, FastAPI's `lifespan` calls `init_db()`, which reads `schema.sql` and creates tables if they do not yet exist. The local `elektromanager.sqlite3` file is ignored by Git. `CREATE TABLE IF NOT EXISTS` does **not** perform schema migrations for existing tables.

## API contract (for Oleksii)

All prices are stored and transferred in **integer grosz** (`2999` means 29.99 PLN). `stock = 0` is allowed and means the product is currently unavailable. The API currently returns raw `price_grosz`, `discount_type` and `discount_value`; **it does not yet return a calculated final price or `is_available`**.

| HTTP method | Endpoint | Purpose | Expected status |
|---|---|---|---|
| `GET` | `/health` | Health check | `200` |
| `GET` | `/api/categories` | List categories | `200`, array (possibly `[]`) |
| `GET` | `/api/products` | List products | `200`, array (possibly `[]`) |
| `GET` | `/api/products/{id}` | Get a product | `200`, `404`; malformed `id`: `422` |
| `POST` | `/api/products` | Create a product | `201`, invalid input: `422` |
| `PUT` | `/api/products/{id}` | Replace all editable product fields | `200`, `404`, `422` |
| `DELETE` | `/api/products/{id}` | Delete product | `204` (empty body), `404` |

### Product input for POST and PUT

```json
{
  "name": "Gniazdko elektryczne",
  "description": "Podwojne gniazdko 230V",
  "price_grosz": 2999,
  "stock": 15,
  "category_id": 1,
  "discount_type": "percent",
  "discount_value": 10,
  "image_url": null
}
```

`name`, `price_grosz`, `stock`, `category_id` are required. Other fields may be omitted; `description` and `image_url` default to `null`, `discount_type` to `none`, `discount_value` to `0`.

- `name`: 1–150 characters in the request body and not whitespace-only. SQLite additionally checks the trimmed length (raw input is not automatically trimmed).
- `description`: `null` or 1–1000 characters; cannot be whitespace-only.
- `price_grosz`: integer, ≥ 0.
- `stock`: integer, ≥ 0.
- `category_id`: existing category ID, integer ≥ 1.
- `discount_type`: `none`, `percent`, or `fixed`.
- `discount_value`: integer, ≥ 0. For `none` it must be 0; for `percent` it must be ≤ 100; for `fixed` it must be ≤ `price_grosz` (fixed discounts are also in grosz).
- `image_url`: `null` or 1–2048 characters; URL format is **not** strictly validated in this milestone.

For **PUT**, submit a full product body. Omitting optional fields resets them to their defaults. `id` and `created_at` are controlled by SQLite and cannot be modified through PUT. No PATCH endpoint is implemented.

**Product response** (`GET`, successful `POST`, successful `PUT`):

```json
{
  "id": 1,
  "name": "Gniazdko elektryczne",
  "description": "Podwojne gniazdko 230V",
  "price_grosz": 2999,
  "stock": 15,
  "category_id": 1,
  "discount_type": "percent",
  "discount_value": 10,
  "image_url": null,
  "created_at": "2026-11-23 14:26:17"
}
```

`created_at` is set by SQLite as UTC (`CURRENT_TIMESTAMP`). `GET /api/categories` returns objects with fields `id`, `name`, `description`. `DELETE` succeeds with no JSON body.

**Error responses** are JSON with a `detail` field. Validation errors may contain a structured array in `detail` (Pydantic). Missing products and unknown categories yield descriptive error strings. The exact wording of product-not-found messages is not guaranteed; frontend should use the **HTTP status code**.

### Categories for a local demo

There is **no POST /api/categories** endpoint in this milestone. To add a development category from the `ElektroTeam/` directory:

```powershell
.\.venv\Scripts\python.exe -c "from app.database import get_connection; c = get_connection(); c.execute('INSERT INTO categories (name) VALUES (?)', ('Gniazdka',)); c.commit(); c.close()"
```

Run this only once per category name: `categories.name` has a `UNIQUE` constraint. Then inspect `GET /api/categories` and use the returned `id` for creating products.

### Frontend / CORS note

The backend has **no CORS middleware configured** in the current milestone. If Oleksii serves frontend from a **different browser origin** (different host or port), cross-origin `fetch()` requests may be blocked by the browser. Before integration, decide whether to serve frontend from the same origin or enable narrowly scoped `CORSMiddleware` with the actual frontend origin(s). Do not set unrestricted production CORS for an unauthenticated write API.

## Automated tests (pytest)

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The suite uses `TestClient` and the application's real `lifespan`. Each test gets a **fresh temporary SQLite file**, with the real schema copied into that temporary directory. The development database `elektromanager.sqlite3` is not modified by tests. Tests cover empty and populated catalog, reads, validation errors, categories, create/update/delete, and persistence across SQLite connections.

## Project structure

```text
ElektroTeam/
├── app/
│   ├── __init__.py
│   ├── database.py          # get_connection, init_db
│   ├── main.py              # FastAPI routes and lifespan
│   └── schemas.py           # Pydantic ProductCreate
├── tests/
│   ├── conftest.py          # test-only DB and fixtures
│   └── test_products.py     # pytest checks
├── schema.sql               # SQLite tables and constraints
├── requirements.txt
├── README.md
└── .gitignore
```

## Scope / known limitations

- Local educational/demo backend, not a production ecommerce server.
- No users, authentication, orders, cart, category editing, image upload, or payments.
- No API field for calculated discounted price; consumers receive raw discount values.
- Frontend integration and full demonstration depend on Oleksii's UI and are a later stage.
- For the complete first backend milestone: tests must pass on the actual working copy, the API contract must match that copy, and the work must be committed/pushed to the `feature/backend` branch for a pull request.
