# shoplite

A small shop backend: products, customers, carts and orders. Python 3 standard library only (sqlite3). All amounts are integer cents.

## Run the tests

    python3 -m unittest discover -s tests -t .

## Command line

    python3 -m shoplite.cli init
    python3 -m shoplite.cli add-product "Mug" 1200 --stock 10
    python3 -m shoplite.cli products

## Planned

- Discount codes at checkout (code `SAVE10`: 10% off)
- Low-stock alerts for the admin
