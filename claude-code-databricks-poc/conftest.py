"""Local SparkSession for the test suite. Runs on any laptop, no cluster."""
import os
import sys
import time

# Pin the process timezone to UTC so timestamp tests are deterministic on any
# machine (Databricks itself runs UTC). Without this, a SQL string->timestamp
# cast resolves in UTC while Python's collect() renders in the local zone, so
# the payments test drifts by the local offset on non-UTC laptops.
os.environ["TZ"] = "UTC"
if hasattr(time, "tzset"):
    time.tzset()  # POSIX only; on Windows the CRT reads TZ directly

# Point Spark's Python workers at the same interpreter running pytest. Without
# this, Spark launches workers via a different (or missing) Python and they fail
# to connect back to the driver — on Windows this surfaces as Py4JJavaError /
# PythonWorkerFactory socket-accept failures and every Spark test errors out.
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

import pytest
from pyspark.sql import SparkSession

# make `src` importable regardless of where pytest is invoked from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("poc-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()
