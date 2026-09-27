"""Product categories."""


def get_or_create_category(conn, name):
    row = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def list_categories(conn):
    return [r["name"] for r in conn.execute("SELECT name FROM categories ORDER BY name")]
