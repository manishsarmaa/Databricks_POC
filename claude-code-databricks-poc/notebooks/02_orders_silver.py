# Databricks notebook source
# MAGIC %md
# MAGIC # Orders — Silver

# COMMAND ----------
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "poc")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------
from src.pipelines.orders.silver import build_silver

bronze = spark.read.table(f"{catalog}.{schema}.orders_bronze")
silver = build_silver(bronze)
silver.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.orders_silver")
display(silver)
