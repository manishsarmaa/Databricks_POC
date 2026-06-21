"""Shared type-enforcement function.

Used by every pipeline. Directly addresses the "source changed the data type"
failure mode (e.g. a column was float, the source suddenly sends 1 instead of
1.0). We never trust the inferred type from the file; we cast to the contract.
"""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def enforce_types(df: DataFrame, type_map: dict[str, str]) -> DataFrame:
    """Cast each column to its declared contract type.

    `type_map` maps column name -> Spark SQL type string ("int", "double",
    "date", "timestamp", "string", ...). Columns absent from the DataFrame are
    skipped (they are added/aligned earlier by `align_to_contract`).
    """
    for column, dtype in type_map.items():
        if column in df.columns:
            df = df.withColumn(column, F.col(column).cast(dtype))
    return df
