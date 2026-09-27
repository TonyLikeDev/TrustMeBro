import unittest

from shoplite.catalog.products import add_product
from shoplite.customers.accounts import create_customer
from shoplite.orders.cart import Cart
from shoplite.orders.checkout import place_order
from shoplite.reports.sales import best_sellers, sales_by_day
from tests.support import fresh_db


class ReportsTest(unittest.TestCase):
    def test_best_sellers_and_daily_sales(self):
        conn = fresh_db()
        cid = create_customer(conn, "Ann", "ann@example.com")
        mug = add_product(conn, "Mug", 1000, stock=20)
        cart = Cart()
        cart.add(mug, 3)
        place_order(conn, cid, cart)
        self.assertEqual(best_sellers(conn)[0], {"name": "Mug", "sold": 3})
        self.assertEqual(sales_by_day(conn)[0]["orders"], 1)


if __name__ == "__main__":
    unittest.main()
