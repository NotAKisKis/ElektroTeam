
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
        CHECK (length(trim(name)) BETWEEN 1 AND 100),
    description TEXT
        CHECK (length(trim(description)) BETWEEN 1 AND 400)
) STRICT;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
        CHECK (length(trim(name)) BETWEEN 1 AND 150),
    description TEXT
        CHECK (length(trim(description)) BETWEEN 1 AND 1000),
    price_grosz INTEGER NOT NULL
        CHECK (price_grosz >= 0),
    stock INTEGER NOT NULL
        CHECK (stock >= 0),
    category_id INTEGER NOT NULL,

    discount_type TEXT NOT NULL DEFAULT 'none'
        CHECK (discount_type IN ('none', 'percent', 'fixed')),
    discount_value INTEGER NOT NULL DEFAULT 0
        CHECK (discount_value >= 0),

    image_url TEXT
        CHECK (length(trim(image_url)) BETWEEN 1 AND 2048),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT,

    CHECK (
        (discount_type = 'none' AND discount_value = 0)
        OR
        (discount_type = 'percent'
            AND discount_value BETWEEN 0 AND 100)
        OR
        (discount_type = 'fixed'
            AND discount_value <= price_grosz)
    )
) STRICT;
