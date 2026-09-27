import unittest

from shoplite.customers.accounts import create_customer, get_customer
from shoplite.customers.addresses import add_address, addresses_for
from tests.support import fresh_db


class AccountsTest(unittest.TestCase):
    def setUp(self):
        self.conn = fresh_db()

    def test_create_and_get(self):
        cid = create_customer(self.conn, "Ann", " Ann@Example.com ")
        self.assertEqual(get_customer(self.conn, cid)["email"], "ann@example.com")

    def test_duplicate_email(self):
        create_customer(self.conn, "Ann", "ann@example.com")
        with self.assertRaises(ValueError):
            create_customer(self.conn, "Ann B", "ann@example.com")

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            create_customer(self.conn, "Bob", "not-an-email")

    def test_addresses(self):
        cid = create_customer(self.conn, "Ann", "ann@example.com")
        add_address(self.conn, cid, "1 Main St", "Springfield", "12345")
        self.assertEqual(len(addresses_for(self.conn, cid)), 1)


if __name__ == "__main__":
    unittest.main()
