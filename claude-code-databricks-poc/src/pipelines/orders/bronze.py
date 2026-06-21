"""Orders — bronze layer.

Schema-on-read as *strings*, keep every column the source sent (schema
evolution), and only normalise the headers. Reading as strings on purpose:
it stops the source's type drift (1 vs 1.0) from ever reaching us as a typing
surprise — silver casts deliberately against the contract instead.
"""
from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession

from src.common.cleansing import clean_column_names


def build_bronze(spark: SparkSession, path: str) -> DataFrame:
    df = (
        spark.read.option("header", True)
        .option("inferSchema", False)  # read everything as string; cast later
        .csv(path)
    )
    return clean_column_names(df)
