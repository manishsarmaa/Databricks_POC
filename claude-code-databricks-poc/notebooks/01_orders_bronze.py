# Databricks notebook source
# MAGIC %md
# MAGIC # Orders — Bronze
# MAGIC Thin wrapper. All logic lives in `src/` so it can be unit-tested locally
# MAGIC with no cluster. Runs on Free Edition serverless + Unity Catalog.

# COMMAND ----------
import os
import sys

# the bundle syncs the repo into the workspace; add its root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "poc")
dbutils.widgets.text("source_path", "/Volumes/workspace/poc/raw/orders.csv")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
source_path = dbutils.widgets.get("source_path")

# COMMAND ----------
from src.pipelines.orders.bronze import build_bronze

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
bronze = build_bronze(spark, source_path)
bronze.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.orders_bronze")
display(bronze)
