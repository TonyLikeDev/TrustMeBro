"""Command line: python3 -m shoplite.cli <command>."""
import argparse

from shoplite.catalog.products import add_product, list_products
from shoplite.db.connection import connect, init_db
from shoplite.utils.money import format_money


def main(argv=None):
    parser = argparse.ArgumentParser(prog="shoplite")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    add = sub.add_parser("add-product")
    add.add_argument("name")
    add.add_argument("price_cents", type=int)
    add.add_argument("--stock", type=int, default=0)
    sub.add_parser("products")
    args = parser.parse_args(argv)
    conn = connect()
    if args.cmd == "init":
        init_db(conn)
    elif args.cmd == "add-product":
        print(add_product(conn, args.name, args.price_cents, args.stock))
    else:
        for p in list_products(conn):
            print(f"{p['id']:>4}  {p['name']:<24}{format_money(p['price_cents']):>10}  stock {p['stock']}")


if __name__ == "__main__":
    main()
