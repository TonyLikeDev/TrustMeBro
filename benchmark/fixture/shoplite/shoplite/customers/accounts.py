"""Customer accounts."""
from shoplite.utils.validation import validate_email


def create_customer(conn, name, email):
    email = validate_email(email)
    if conn.execute("SELECT 1 FROM customers WHERE email = ?", (email,)).fetchone():
        raise ValueError(f"email already registered: {email}")
    cur = conn.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    return cur.lastrowid


def get_customer(conn, customer_id):
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if row is None:
        raise KeyError(f"no customer {customer_id}")
    return dict(row)
