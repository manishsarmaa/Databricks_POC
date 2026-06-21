# Databricks notebook source
# MAGIC %md
# MAGIC # Orders — Gold (revenue per customer)

# COMMAND ----------
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "poc")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------
from src.pipelines.orders.gold import build_gold

silver = spark.read.table(f"{catalog}.{schema}.orders_silver")
gold = build_gold(silver)
gold.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.orders_gold")
display(gold)
