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
        [(1, 5, date(2024, 1, 1), "Widget", 2, 1.0, None, None)],
        "order_id int, customer_id int, order_date date, product string, "
        "quantity int, unit_price double, status string, currency string",
    )

    assert_df_equality(actual, expected, ignore_nullable=True, ignore_row_order=True)


# Scenario 1 — control characters inside the `product` value must be stripped by
# silver (via the shared `strip_control_chars`), not crash downstream.
def test_control_chars_in_product_are_stripped(spark):
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Wid\x00get\x1f", "2", "1", "PAID")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "status"],
    )
    row = build_silver(bronze).collect()[0]
    assert row["product"] == "Widget"


# Scenario 3 — source now sends `unit_price` as an int string ("1") instead of
# "1.00"; silver must still produce a double 1.0.
def test_unit_price_int_normalised_to_double_in_silver(spark):
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Widget", "2", "1", "PAID")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "status"],
    )
    out = build_silver(bronze)
    assert out.schema["unit_price"].dataType.simpleString() == "double"
    assert out.collect()[0]["unit_price"] == 1.0


# Scenario 4 — source added an extra `notes` column the contract never asked for;
# it must NOT flow into silver.
def test_extra_notes_column_excluded_from_silver(spark):
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Widget", "2", "1", "PAID", "free-text note")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "status", "notes"],
    )
    out = build_silver(bronze)
    assert "notes" not in out.columns


# Scenario 5 (drop) — source dropped `status`; silver must still emit the column
# as NULL rather than fail.
def test_dropped_status_column_becomes_null(spark):
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Widget", "2", "1")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price"],
    )
    out = build_silver(bronze)
    assert "status" in out.columns
    assert out.collect()[0]["status"] is None


# Scenario 5 (add) — we now ingest a new `currency` column. Once it's in the
# contract, silver threads it through automatically and casts it to string.
def test_currency_column_is_ingested(spark):
    bronze = spark.createDataFrame(
        [("1", "5", "2024-01-01", "Widget", "2", "1", "PAID", "USD")],
        ["order_id", "customer_id", "order_date", "product",
         "quantity", "unit_price", "status", "currency"],
    )
    out = build_silver(bronze)
    assert "currency" in out.columns
    assert out.schema["currency"].dataType.simpleString() == "string"
    assert out.collect()[0]["currency"] == "USD"
