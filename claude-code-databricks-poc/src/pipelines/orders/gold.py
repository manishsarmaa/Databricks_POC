"""Orders — gold layer: revenue per customer."""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_gold(silver: DataFrame) -> DataFrame:
    return (
        silver.withColumn("line_total", F.col("quantity") * F.col("unit_price"))
        .groupBy("customer_id")
        .agg(
            F.round(F.sum("line_total"), 2).alias("total_revenue"),
            F.countDistinct("order_id").alias("order_count"),
        )
        .orderBy("customer_id")
    )
