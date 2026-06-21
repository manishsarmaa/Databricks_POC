"""End-to-end silver test for orders, exercising the failure modes together:
extra column, dropped column, funny chars, type drift.
"""
from datetime import date

from chispa import assert_df_equality

from src.pipelines.orders.silver import build_silver


def test_orders_silver_handles_all_breakages(spark):
    # bronze = all-string, headers already normalised by the bronze step.
    # Note: `status` is MISSING (dropped by source) and `notes` is EXTRA.
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Wid\x00get", "2", "1", "free-text note")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "notes"],
    )

    actual = build_silver(bronze)

    expected = spark.createDataFrame(
        [(1, 5, date(2024, 1, 1), "Widget", 2, 1.0, None)],
        "order_id int, customer_id int, order_date date, product string, "
        "quantity int, unit_price double, status string",
    )

    assert_df_equality(actual, expected, ignore_nullable=True, ignore_row_order=True)
