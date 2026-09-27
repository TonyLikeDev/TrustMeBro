from shoplite.db.connection import connect, init_db


def fresh_db():
    conn = connect(":memory:")
    init_db(conn)
    return conn
