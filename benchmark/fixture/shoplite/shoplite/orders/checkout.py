"""Checkout: turn a cart into an order."""
from shoplite.catalog.products import get_product, update_stock
from shoplite.customers.accounts import get_customer
from shoplite.notifications.email import send_order_confirmation
from shoplite.orders.pricing import order_totals


def place_order(conn, customer_id, cart):
    if cart.is_empty():
        raise ValueError("cart is empty")
    customer = get_customer(conn, customer_id)
    products = {pid: get_product(conn, pid) for pid in cart.items}
    for pid, qty in cart.items.items():
        if products[pid]["stock"] < qty:
            raise ValueError(f"not enough stock for {products[pid]['name']}")
    # TODO: discount codes (see README, Planned)
    totals = order_totals([(products[pid]["price_cents"], qty) for pid, qty in cart.items.items()])
    with conn:
        cur = conn.execute(
            "INSERT INTO orders (customer_id, subtotal_cents, tax_cents, shipping_cents, total_cents) "
            "VALUES (?, ?, ?, ?, ?)",
            (customer_id, totals["subtotal"], totals["tax"], totals["shipping"], totals["total"]),
        )
        order_id = cur.lastrowid
        for pid, qty in cart.items.items():
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents) VALUES (?, ?, ?, ?)",
                (order_id, pid, qty, products[pid]["price_cents"]),
            )
            update_stock(conn, pid, -qty)
    order = {"id": order_id, "customer_id": customer_id, **totals}
    send_order_confirmation(customer, order)
    return order
