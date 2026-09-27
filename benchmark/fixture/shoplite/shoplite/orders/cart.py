"""Shopping cart, kept in memory until checkout."""


class Cart:
    def __init__(self):
        self.items = {}  # product_id -> quantity

    def add(self, product_id, quantity=1):
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.items[product_id] = self.items.get(product_id, 0) + quantity

    def remove(self, product_id):
        self.items.pop(product_id, None)

    def is_empty(self):
        return not self.items
