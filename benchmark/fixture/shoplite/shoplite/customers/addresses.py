"""Shipping addresses."""


def add_address(conn, customer_id, line1, city, postcode):
    cur = conn.execute(
        "INSERT INTO addresses (customer_id, line1, city, postcode) VALUES (?, ?, ?, ?)",
        (customer_id, line1, city, postcode),
    )
    conn.commit()
    return cur.lastrowid


def addresses_for(conn, customer_id):
    rows = conn.execute("SELECT * FROM addresses WHERE customer_id = ?", (customer_id,))
    return [dict(r) for r in rows]
