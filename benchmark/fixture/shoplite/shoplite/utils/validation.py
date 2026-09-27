"""Input validation helpers."""
import re

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email):
    email = email.strip().lower()
    if not EMAIL.match(email):
        raise ValueError(f"invalid email: {email}")
    return email


def require_positive(value, name, allow_zero=False):
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{name} must be positive")
    return value
