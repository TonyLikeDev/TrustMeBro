"""Money helpers. All amounts are integer cents."""


def format_money(cents):
    return f"${cents / 100:,.2f}"


def percent_of(cents, rate):
    return int(round(cents * rate))
