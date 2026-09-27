import unittest

from shoplite.orders.cart import Cart


class CartTest(unittest.TestCase):
    def test_add_merges_quantities(self):
        cart = Cart()
        cart.add(1, 2)
        cart.add(1, 3)
        self.assertEqual(cart.items, {1: 5})

    def test_remove(self):
        cart = Cart()
        cart.add(1)
        cart.remove(1)
        self.assertTrue(cart.is_empty())

    def test_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            Cart().add(1, 0)


if __name__ == "__main__":
    unittest.main()
