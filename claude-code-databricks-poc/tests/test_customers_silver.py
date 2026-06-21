"""Regression net #1. customers reuses the shared common functions, so if a
'fix' to a common function changes its behaviour, this test catches it.
"""
from datetime import date

from chispa import assert_df_equality

from src.pipelines.customers.silver import build_silver


def test_customers_silver_basic(spark):
    bronze = spark.createDataFrame(
        [("7", "  Asha  ", "asha@example.com", "IN", "2023-02-01")],
        ["customer_id", "name", "email", "country", "signup_date"],
    )
    actual = build_silver(bronze)
    expected = spark.createDataFrame(
        [(7, "Asha", "asha@example.com", "IN", date(2023, 2, 1))],
        "customer_id int, name string, email string, country string, signup_date date",
    )
    assert_df_equality(actual, expected, ignore_nullable=True, ignore_row_order=True)
