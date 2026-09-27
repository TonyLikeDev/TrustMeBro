import unittest

from shoplite.orders.pricing import order_totals


class PricingTest(unittest.TestCase):
    def test_small_order_pays_shipping(self):
        totals = order_totals([(1000, 2)])
        self.assertEqual(totals["subtotal"], 2000)
        self.assertEqual(totals["tax"], 160)
        self.assertEqual(totals["shipping"], 599)
        self.assertEqual(totals["total"], 2000 + 160 + 599)


if __name__ == "__main__":
    unittest.main()
