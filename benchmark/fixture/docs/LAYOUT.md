<!-- trustmebro -->
# Project layout

Map of the code: where things are, what they do, how they connect. **Rule: when a change adds, moves or removes a folder, component, table or piece of logic, update this file in the same commit.** One line per entry; point to files, don't paste code.

Last updated: 2026-09-21.

## Overview

A small shop backend in Python (standard library, sqlite3). A checkout goes: `Cart` → `place_order` → `order_totals` (pricing) → rows in `orders` / `order_items` → stock decremented → confirmation email. All amounts are integer cents.

## Folder tree

```
shoplite/
├── config.py              shop settings: admin/shop email, tax rate, shipping fee, free-shipping threshold
├── cli.py                 command line: init, add-product, products
├── db/                    schema.sql (tables), connection.py (connect, init_db)
├── catalog/               products.py (CRUD, update_stock), categories.py, search.py
├── customers/             accounts.py (create/get, email validation), addresses.py
├── orders/                cart.py (Cart), pricing.py (subtotal, tax, shipping), checkout.py (place_order), history.py
├── notifications/         email.py (send_email, OUTBOX, order confirmation), templates.py (email texts)
├── reports/               sales.py (sales_by_day, best_sellers)
└── utils/                 money.py (format_money, percent_of), validation.py (validate_email, require_positive)
tests/                     unittest suites per module; support.py gives an in-memory database
```

## Components

| Component | Path | Does | Depends on |
| :--- | :--- | :--- | :--- |
| Database | `shoplite/db/` | schema and connections | |
| Catalog | `shoplite/catalog/` | products, categories, stock, search | db, utils |
| Customers | `shoplite/customers/` | accounts, addresses | db, utils |
| Orders | `shoplite/orders/` | cart, pricing, checkout, history | catalog, customers, notifications |
| Notifications | `shoplite/notifications/` | outgoing email (collected in `OUTBOX`) | config, utils |
| Reports | `shoplite/reports/` | sales per day, best sellers | db |

**Flows**
- checkout: `orders/cart.py:Cart` → `orders/checkout.py:place_order` → `orders/pricing.py:order_totals` → `catalog/products.py:update_stock` → `notifications/email.py:send_order_confirmation`

## Database

Defined in: `shoplite/db/schema.sql`

| Table | Key fields | Relations |
| :--- | :--- | :--- |
| categories | name | |
| products | name, price_cents, stock | category_id → categories |
| customers | name, email (unique) | |
| addresses | line1, city, postcode | customer_id → customers |
| orders | subtotal/tax/shipping/total_cents | customer_id → customers |
| order_items | quantity, unit_price_cents | order_id → orders, product_id → products |

## Logic

- **place order**: checks stock, prices the cart, writes the order, decrements stock, emails a confirmation → `shoplite/orders/checkout.py:place_order`
- **totals**: subtotal, 8% tax, shipping (free above `FREE_SHIPPING_THRESHOLD`) → `shoplite/orders/pricing.py:order_totals`, `shipping_cents`
- **stock**: change stock, refuse to go negative → `shoplite/catalog/products.py:update_stock`
- **email**: queue a message in `OUTBOX` → `shoplite/notifications/email.py:send_email`
- **email validation**: normalise and check addresses → `shoplite/utils/validation.py:validate_email`
