import unittest

from shoplite.catalog.products import add_product, get_product, list_products, update_stock
from shoplite.catalog.search import search_products
from tests.support import fresh_db


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.conn = fresh_db()

    def test_add_and_get(self):
        pid = add_product(self.conn, "Mug", 1200, stock=3, category="kitchen")
        self.assertEqual(get_product(self.conn, pid)["name"], "Mug")

    def test_update_stock(self):
        pid = add_product(self.conn, "Mug", 1200, stock=3)
        self.assertEqual(update_stock(self.conn, pid, -2), 1)
        with self.assertRaises(ValueError):
            update_stock(self.conn, pid, -5)

    def test_search_by_category(self):
        add_product(self.conn, "Blue mug", 1200, category="kitchen")
        add_product(self.conn, "Blue shirt", 2500, category="clothing")
        names = [p["name"] for p in search_products(self.conn, "Blue", category="kitchen")]
        self.assertEqual(names, ["Blue mug"])

    def test_in_stock_only(self):
        add_product(self.conn, "A", 100, stock=0)
        add_product(self.conn, "B", 100, stock=1)
        self.assertEqual([p["name"] for p in list_products(self.conn, in_stock_only=True)], ["B"])


if __name__ == "__main__":
    unittest.main()
