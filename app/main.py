from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.database import init_db, get_connection
from app.schemas import ProductCreate

#жизнь проги от запуска до смерти
@asynccontextmanager
async def lifespan(app):
    print("Приложение запускается")
    init_db()
    yield
    print("Приложение останавливается")

#инициализация
app = FastAPI(lifespan=lifespan)


#статус
@app.get("/health")
def health():
    return {"status": "ok"}


#получение всех продуктов
@app.get("/api/products")
def products():
    con = get_connection()
    try:
        rows = con.execute(
        "SELECT * FROM products"
        ).fetchall()
        products = [dict(row) for row in rows]
    finally:
        con.close()
    return products



#получение определённого продукта
@app.get("/api/products/{id}")
def product_by_id(id: int):
    con = get_connection()

    try:
        row = con.execute(
            "SELECT * FROM products WHERE id = ?", (id,)
        ).fetchone()
    
    finally:
        con.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="There is NO such product"
        )


    return dict(row)

#список категорий
@app.get("/api/categories")
def get_categories():
    con = get_connection()
    try:
        rows = con.execute(
            "SELECT * FROM categories"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        con.close()


#добавляем продукты
@app.post("/api/products", status_code=201)
def create_product(product: ProductCreate):
    con = get_connection()

    try:
        category = con.execute(
            "SELECT id FROM categories WHERE id = ?",
            (product.category_id,)
        ).fetchone()

        if category is None:
            raise HTTPException(
                status_code=422,
                detail="Category not found"
            )

        cursor = con.execute(
            """
            INSERT INTO products (
                name, description, price_grosz, stock,
                category_id, discount_type, discount_value, image_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.name,
                product.description,
                product.price_grosz,
                product.stock,
                product.category_id,
                product.discount_type,
                product.discount_value,
                product.image_url
            )
        )

        con.commit()

        row = con.execute(
            "SELECT * FROM products WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return dict(row)

    finally:
        con.close()


#меняем продукты


@app.put("/api/products/{id}")
def update_product(id: int, product: ProductCreate):
    con = get_connection()

    try:
        category = con.execute(
            "SELECT id FROM categories WHERE id = ?",
            (product.category_id,)
        ).fetchone()

        if category is None:
            raise HTTPException(
                status_code=422,
                detail="Category not found"
            )

        cursor = con.execute(
            """
            UPDATE products
            SET name = ?,
                description = ?,
                price_grosz = ?,
                stock = ?,
                category_id = ?,
                discount_type = ?,
                discount_value = ?,
                image_url = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.description,
                product.price_grosz,
                product.stock,
                product.category_id,
                product.discount_type,
                product.discount_value,
                product.image_url,
                id
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        con.commit()

        row = con.execute(
            "SELECT * FROM products WHERE id = ?",
            (id,)
        ).fetchone()

        return dict(row)

    finally:
        con.close()



@app.delete("/api/products/{id}", status_code=204)
def delete_product(id: int):
    con = get_connection()

    try:
        cursor = con.execute(
            "DELETE FROM products WHERE id = ?",
            (id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        con.commit()

    finally:
        con.close()
