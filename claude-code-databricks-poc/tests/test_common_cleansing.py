"""Unit tests for the shared cleansing functions."""
from src.common.cleansing import clean_column_names, strip_control_chars, trim_strings


def test_clean_column_names_normalises_funny_headers(spark):
    df = spark.createDataFrame([(1,)], ["  Order ID!! "])
    assert clean_column_names(df).columns == ["order_id"]


def test_clean_column_names_multiple(spark):
    df = spark.createDataFrame([(1, 2)], ["Unit Price!!", "Created@At"])
    assert clean_column_names(df).columns == ["unit_price", "created_at"]


def test_strip_control_chars_removes_non_printable(spark):
    df = spark.createDataFrame([("ab\x00c\x1f",)], ["v"])
    assert strip_control_chars(df).collect()[0]["v"] == "abc"


def test_trim_strings(spark):
    df = spark.createDataFrame([("  hi  ",)], ["v"])
    assert trim_strings(df).collect()[0]["v"] == "hi"


# Scenario 2 — source renamed `unit_price` to a weird header. Prove the shared
# `clean_column_names` (called in bronze) normalises it back to `unit_price`.
def test_unit_price_weird_header_normalised(spark):
    df = spark.createDataFrame([(1,)], ["Unit Price!!"])
    assert clean_column_names(df).columns == ["unit_price"]
