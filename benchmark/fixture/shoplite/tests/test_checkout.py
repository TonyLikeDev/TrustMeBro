import unittest

from shoplite.catalog.products import add_product, get_product
from shoplite.customers.accounts import create_customer
from shoplite.notifications.email import OUTBOX
from shoplite.orders.cart import Cart
from shoplite.orders.checkout import place_order
from tests.support import fresh_db


class CheckoutTest(unittest.TestCase):
    def setUp(self):
        self.conn = fresh_db()
        OUTBOX.clear()
        self.customer = create_customer(self.conn, "Ann", "ann@example.com")
        self.mug = add_product(self.conn, "Mug", 1000, stock=20)

    def test_place_order(self):
        cart = Cart()
        cart.add(self.mug, 2)
        order = place_order(self.conn, self.customer, cart)
        self.assertEqual(order["subtotal"], 2000)
        self.assertEqual(get_product(self.conn, self.mug)["stock"], 18)
        self.assertEqual(len(OUTBOX), 1)

    def test_not_enough_stock(self):
        cart = Cart()
        cart.add(self.mug, 99)
        with self.assertRaises(ValueError):
            place_order(self.conn, self.customer, cart)

    def test_empty_cart(self):
        with self.assertRaises(ValueError):
            place_order(self.conn, self.customer, Cart())


if __name__ == "__main__":
    unittest.main()
