"""Payments — silver layer. Third consumer of the shared common functions."""
from __future__ import annotations

from pyspark.sql import DataFrame

from src.common.casting import enforce_types
from src.common.cleansing import strip_control_chars, trim_strings
from src.common.schema import CONTRACTS, align_to_contract

_CONTRACT = CONTRACTS["payments"]


def build_silver(bronze: DataFrame) -> DataFrame:
    df = align_to_contract(bronze, _CONTRACT)
    df = strip_control_chars(df)
    df = trim_strings(df)
    df = enforce_types(df, _CONTRACT)
    return df.dropDuplicates(["payment_id"])
