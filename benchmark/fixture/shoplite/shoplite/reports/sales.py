"""Sales reports."""


def sales_by_day(conn):
    rows = conn.execute("SELECT date(created_at) AS day, COUNT(*) AS orders, SUM(total_cents) AS revenue "
                        "FROM orders GROUP BY day ORDER BY day")
    return [dict(r) for r in rows]


def best_sellers(conn, limit=5):
    rows = conn.execute("SELECT p.name, SUM(i.quantity) AS sold FROM order_items i "
                        "JOIN products p ON p.id = i.product_id GROUP BY p.id ORDER BY sold DESC LIMIT ?", (limit,))
    return [dict(r) for r in rows]
