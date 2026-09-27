"""Order totals: subtotal, tax and shipping, in cents."""
from shoplite import config
from shoplite.utils.money import percent_of


def subtotal_cents(lines):
    """lines: (unit_price_cents, quantity) pairs."""
    return sum(price * qty for price, qty in lines)


def tax_cents(subtotal):
    return percent_of(subtotal, config.TAX_RATE)


def shipping_cents(subtotal):
    if subtotal > config.FREE_SHIPPING_THRESHOLD * 1000:
        return 0
    return config.SHIPPING_FEE_CENTS


def order_totals(lines):
    subtotal = subtotal_cents(lines)
    tax = tax_cents(subtotal)
    shipping = shipping_cents(subtotal)
    return {"subtotal": subtotal, "tax": tax, "shipping": shipping, "total": subtotal + tax + shipping}
