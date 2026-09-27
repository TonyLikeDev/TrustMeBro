"""Outgoing email. Messages are collected in OUTBOX; a real sender would deliver them."""
from shoplite import config
from shoplite.notifications.templates import order_confirmation

OUTBOX = []


def send_email(to, subject, body):
    OUTBOX.append({"to": to, "from": config.SHOP_EMAIL, "subject": subject, "body": body})


def send_order_confirmation(customer, order):
    subject, body = order_confirmation(customer, order)
    send_email(customer["email"], subject, body)
