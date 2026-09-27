"""Product search."""


def search_products(conn, text, category=None):
    sql = ("SELECT p.* FROM products p LEFT JOIN categories c ON c.id = p.category_id "
           "WHERE p.name LIKE ?")
    args = [f"%{text}%"]
    if category:
        sql += " AND c.name = ?"
        args.append(category)
    return [dict(r) for r in conn.execute(sql + " ORDER BY p.name", args)]
