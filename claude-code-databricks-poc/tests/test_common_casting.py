"""The float/int drift the client called out: source sends 1, contract wants 1.0."""
from src.common.casting import enforce_types


def test_int_is_normalised_to_double(spark):
    df = spark.createDataFrame([(1,)], ["unit_price"])  # source sent an int
    out = enforce_types(df, {"unit_price": "double"})
    row = out.collect()[0]
    assert row["unit_price"] == 1.0
    assert out.schema["unit_price"].dataType.simpleString() == "double"


def test_string_date_becomes_date(spark):
    df = spark.createDataFrame([("2024-01-01",)], ["order_date"])
    out = enforce_types(df, {"order_date": "date"})
    assert out.schema["order_date"].dataType.simpleString() == "date"
