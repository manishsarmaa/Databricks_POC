"""Orders — silver layer.

Conform to the contract, clean the data, enforce types. Every step here is a
shared `src.common` function, so the same fix applied to a common function is
exercised by orders *and* customers *and* payments tests.
"""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.common.casting import enforce_types
from src.common.cleansing import strip_control_chars, trim_strings
from src.common.schema import CONTRACTS, align_to_contract

_CONTRACT = CONTRACTS["orders"]


def build_silver(bronze: DataFrame) -> DataFrame:
    df = align_to_contract(bronze, _CONTRACT)   # add missing / drop extra cols
    df = strip_control_chars(df)                # remove funny chars in the data
    df = trim_strings(df)
    df = enforce_types(df, _CONTRACT)           # 1 -> 1.0, "2024-01-01" -> date
    df = df.filter(F.col("order_id").isNotNull())
    df = df.dropDuplicates(["order_id"])
    return df
