"""Schema contracts + alignment.

The contract is the single source of truth for what silver/gold expect. The
source can add, drop, reorder or rename columns all it likes; `align_to_contract`
makes the DataFrame conform before any downstream logic runs. This is the
"enforce in silver" half of the pattern (schema-evolution-in-bronze is the
other half: bronze keeps everything, silver conforms to the contract).
"""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# column -> Spark SQL type string, per dataset.
CONTRACTS: dict[str, dict[str, str]] = {
    "orders": {
        "order_id": "int",
        "customer_id": "int",
        "order_date": "date",
        "product": "string",
        "quantity": "int",
        "unit_price": "double",
        "status": "string",
        "currency": "string",
    },
    "customers": {
        "customer_id": "int",
        "name": "string",
        "email": "string",
        "country": "string",
        "signup_date": "date",
    },
    "payments": {
        "payment_id": "int",
        "order_id": "int",
        "amount": "double",
        "method": "string",
        "paid_at": "timestamp",
    },
}


def align_to_contract(df: DataFrame, contract: dict[str, str]) -> DataFrame:
    """Make `df` conform to `contract` regardless of what the source sent.

    - expected column missing  -> added as NULL  (handles a *dropped* source column)
    - unexpected extra column  -> dropped        (handles an *added* source column)
    - column order             -> normalised to contract order

    Types are NOT cast here; call `enforce_types` afterwards.
    """
    for column in contract:
        if column not in df.columns:
            df = df.withColumn(column, F.lit(None))
    return df.select(*contract.keys())
