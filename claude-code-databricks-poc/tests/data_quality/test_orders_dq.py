"""Data-quality gates on the orders silver output. These assert *properties*
of the data (not exact rows), which is what you run against real volumes.
"""
from datetime import date

from src.pipelines.orders.silver import build_silver


def _silver(spark):
    bronze = spark.createDataFrame(
        [
            ("1", "5", "2024-01-01", "Widget", "2", "10.00", "PAID"),
            ("2", "6", "2024-01-02", "Gadget", "1", "5.50", "PENDING"),
            ("1", "5", "2024-01-01", "Widget", "2", "10.00", "PAID"),  # dup
        ],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "status"],
    )
    return build_silver(bronze)


def test_primary_key_not_null(spark):
    s = _silver(spark)
    assert s.filter(s.order_id.isNull()).count() == 0


def test_primary_key_unique(spark):
    s = _silver(spark)
    assert s.count() == s.dropDuplicates(["order_id"]).count()


def test_no_negative_prices(spark):
    s = _silver(spark)
    assert s.filter(s.unit_price < 0).count() == 0
