"""Past orders."""


def orders_for_customer(conn, customer_id):
    rows = conn.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY id", (customer_id,))
    return [dict(r) for r in rows]


def order_items(conn, order_id):
    return [dict(r) for r in conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))]
