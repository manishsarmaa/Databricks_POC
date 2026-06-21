"""Shared cleansing functions.

IMPORTANT: every pipeline (orders, customers, payments, ...) imports from this
module. A change here can break ANY pipeline, so the regression net for these
functions is the *full* test suite, not just one pipeline's tests.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

# Control / non-printable characters (the "funny characters" that break silver/gold).
_CONTROL_CHARS = r"[\x00-\x1f\x7f]"


def clean_column_names(df: DataFrame) -> DataFrame:
    """Normalise headers to lower snake_case and strip funny characters.

    Handles the "renamed column / weird header" failure mode, e.g.
    "  Order ID!! " -> "order_id".
    """
    new_names = []
    for c in df.columns:
        n = c.strip().lower()
        n = re.sub(r"[^0-9a-z]+", "_", n)   # any run of non-alphanumerics -> _
        n = re.sub(r"_+", "_", n).strip("_")
        new_names.append(n or "col")
    return df.toDF(*new_names)


def _string_columns(df: DataFrame) -> list[str]:
    return [f.name for f in df.schema.fields if isinstance(f.dataType, StringType)]


def strip_control_chars(df: DataFrame, columns: Optional[Iterable[str]] = None) -> DataFrame:
    """Remove non-printable/control characters from string columns.

    Handles the "funny characters inside the data" failure mode.
    """
    targets = list(columns) if columns is not None else _string_columns(df)
    for c in targets:
        df = df.withColumn(c, F.regexp_replace(F.col(c), _CONTROL_CHARS, ""))
    return df


def trim_strings(df: DataFrame, columns: Optional[Iterable[str]] = None) -> DataFrame:
    """Trim leading/trailing whitespace from string columns."""
    targets = list(columns) if columns is not None else _string_columns(df)
    for c in targets:
        df = df.withColumn(c, F.trim(F.col(c)))
    return df
