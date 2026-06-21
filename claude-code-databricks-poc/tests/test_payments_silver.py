"""Regression net #2. Third consumer of the shared common functions."""
from datetime import datetime

from chispa import assert_df_equality

from src.pipelines.payments.silver import build_silver


def test_payments_silver_basic(spark):
    bronze = spark.createDataFrame(
        [("100", "1", "12", "card", "2024-01-01 10:00:00")],
        ["payment_id", "order_id", "amount", "method", "paid_at"],
    )
    actual = build_silver(bronze)
    expected = spark.createDataFrame(
        [(100, 1, 12.0, "card", datetime(2024, 1, 1, 10, 0, 0))],
        "payment_id int, order_id int, amount double, method string, paid_at timestamp",
    )
    assert_df_equality(actual, expected, ignore_nullable=True, ignore_row_order=True)
