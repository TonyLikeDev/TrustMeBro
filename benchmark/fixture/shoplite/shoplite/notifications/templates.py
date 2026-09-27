"""Email texts."""
from shoplite.utils.money import format_money


def order_confirmation(customer, order):
    subject = f"Your shoplite order #{order['id']}"
    body = (f"Hi {customer['name']},\n\nThanks for your order.\n"
            f"Subtotal: {format_money(order['subtotal'])}\nTax: {format_money(order['tax'])}\n"
            f"Shipping: {format_money(order['shipping'])}\nTotal: {format_money(order['total'])}\n")
    return subject, body
