"""Customers — silver layer.

Exists mainly to prove the blast-radius point: it reuses the SAME common
functions as orders. If a shared function is changed to fix orders and the
change is wrong, this pipeline's tests are what go red.
"""
from __future__ import annotations

from pyspark.sql import DataFrame

from src.common.casting import enforce_types
from src.common.cleansing import strip_control_chars, trim_strings
from src.common.schema import CONTRACTS, align_to_contract

_CONTRACT = CONTRACTS["customers"]


def build_silver(bronze: DataFrame) -> DataFrame:
    df = align_to_contract(bronze, _CONTRACT)
    df = strip_control_chars(df)
    df = trim_strings(df)
    df = enforce_types(df, _CONTRACT)
    return df.dropDuplicates(["customer_id"])
