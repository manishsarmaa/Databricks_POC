"""Produce data/orders_broken.csv by injecting the FIVE failure modes the
client sees every day. Pure stdlib.

Run:  python scripts/break_input.py

Injected breakages:
  1. Funny characters in the data           (control char inside `product`)
  2. Renamed / weird header                 ("Unit Price!!" instead of unit_price)
  3. Data-type drift                        (unit_price sends 1 instead of 1.00)
  4. Extra column the contract never asked  ("notes")
  5. Dropped column the contract expects    ("status" removed)
"""
from __future__ import annotations

import csv
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
SRC = os.path.join(DATA, "orders.csv")
DST = os.path.join(DATA, "orders_broken.csv")


def main() -> None:
    with open(SRC, newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]

    idx = {name: i for i, name in enumerate(header)}

    # 2. rename header  unit_price -> "Unit Price!!"
    header[idx["unit_price"]] = "Unit Price!!"
    # 5. drop the status column entirely
    status_i = idx["status"]
    new_header = [h for i, h in enumerate(header) if i != status_i]
    # 4. add an unexpected extra column
    new_header.append("notes")

    out_rows = [new_header]
    for r in data:
        row = [v for i, v in enumerate(r) if i != status_i]
        row.append("free-text note")            # extra column value
        out_rows.append(row)

    # 3. type drift: first row sends an integer price (1) not (1.00)
    out_rows[1][idx["unit_price"]] = "1"
    # 1. funny character inside product on the first row
    out_rows[1][idx["product"]] = out_rows[1][idx["product"]] + "\x00\x1f"

    with open(DST, "w", newline="") as f:
        csv.writer(f).writerows(out_rows)

    print("Wrote", DST)


if __name__ == "__main__":
    main()
