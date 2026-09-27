"""Products and stock."""
from shoplite.catalog.categories import get_or_create_category
from shoplite.utils.validation import require_positive


def add_product(conn, name, price_cents, stock=0, category=None):
    require_positive(price_cents, "price_cents", allow_zero=True)
    require_positive(stock, "stock", allow_zero=True)
    category_id = get_or_create_category(conn, category) if category else None
    cur = conn.execute(
        "INSERT INTO products (name, price_cents, stock, category_id) VALUES (?, ?, ?, ?)",
        (name, price_cents, stock, category_id),
    )
    conn.commit()
    return cur.lastrowid


def get_product(conn, product_id):
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        raise KeyError(f"no product {product_id}")
    return dict(row)


def list_products(conn, in_stock_only=False):
    sql = "SELECT * FROM products" + (" WHERE stock > 0" if in_stock_only else "") + " ORDER BY name"
    return [dict(r) for r in conn.execute(sql)]


def update_stock(conn, product_id, delta):
    """Change stock by delta (negative to remove). Returns the new stock level. Does not commit."""
    product = get_product(conn, product_id)
    new_stock = product["stock"] + delta
    if new_stock < 0:
        raise ValueError(f"not enough stock for {product['name']}")
    conn.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    return new_stock
