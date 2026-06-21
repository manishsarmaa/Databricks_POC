"""Generate the sample source files. Pure stdlib, no Spark needed.

Run:  python scripts/generate_data.py
Creates data/orders.csv (100 rows), data/customers.csv, data/payments.csv.
"""
from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

PRODUCTS = ["Widget", "Gadget", "Sprocket", "Cog", "Bolt", "Washer"]
COUNTRIES = ["IN", "US", "UK", "DE", "AU"]
METHODS = ["card", "upi", "netbanking", "wallet"]
STATUSES = ["PAID", "PENDING", "CANCELLED", "REFUNDED"]


def _d(start: date, n: int) -> str:
    return (start + timedelta(days=random.randint(0, n))).isoformat()


def main() -> None:
    # customers
    n_customers = 25
    with open(os.path.join(DATA, "customers.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "name", "email", "country", "signup_date"])
        for cid in range(1, n_customers + 1):
            w.writerow([
                cid,
                f"Customer {cid}",
                f"customer{cid}@example.com",
                random.choice(COUNTRIES),
                _d(date(2023, 1, 1), 365),
            ])

    # orders (100 rows). unit_price written WITH decimals (e.g. 12.50)
    with open(os.path.join(DATA, "orders.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "customer_id", "order_date", "product",
                    "quantity", "unit_price", "status"])
        for oid in range(1, 101):
            w.writerow([
                oid,
                random.randint(1, n_customers),
                _d(date(2024, 1, 1), 300),
                random.choice(PRODUCTS),
                random.randint(1, 5),
                f"{random.uniform(5, 200):.2f}",
                random.choice(STATUSES),
            ])

    # payments (one per ~80% of orders)
    with open(os.path.join(DATA, "payments.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["payment_id", "order_id", "amount", "method", "paid_at"])
        pid = 1
        for oid in range(1, 101):
            if random.random() < 0.8:
                w.writerow([
                    pid,
                    oid,
                    f"{random.uniform(5, 500):.2f}",
                    random.choice(METHODS),
                    f"{_d(date(2024, 1, 1), 300)} 10:00:00",
                ])
                pid += 1

    print("Wrote orders.csv, customers.csv, payments.csv to", DATA)


if __name__ == "__main__":
    main()
