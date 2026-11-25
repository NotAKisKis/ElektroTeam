from app.database import init_db, get_connection


def seed_categories():
    init_db()

    categories = [
        ("TV",),
        ("Phones",),
        ("Drones",),
        ("Headphones",),
    ]

    con = get_connection()

    try:
        con.executemany(
            "INSERT OR IGNORE INTO categories(name) VALUES (?)",
            categories
        )
        con.commit()

    finally:
        con.close()


if __name__ == "__main__":
    seed_categories()
    print("Categories initialized")