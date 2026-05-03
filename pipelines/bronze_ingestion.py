# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

STORAGE_ACCOUNT = "retaillakeo743lars"

CATALOG = "retail_platform"
SCHEMA = "bronze"

EVENT_TYPES = [
    "orders",
    "payments",
    "product_events",
    "customers",
]

# COMMAND ----------

spark.sql("""
CREATE CATALOG IF NOT EXISTS retail_platform
MANAGED LOCATION 'abfss://bronze@retaillakeo743lars.dfs.core.windows.net/retail_platform'
""")

spark.sql("CREATE SCHEMA IF NOT EXISTS retail_platform.bronze")

# COMMAND ----------

def ingest_bronze_table(event_type: str) -> None:
    input_path = f"abfss://landing@{STORAGE_ACCOUNT}.dfs.core.windows.net/{event_type}/"
    checkpoint_path = f"abfss://checkpoints@{STORAGE_ACCOUNT}.dfs.core.windows.net/bronze/{event_type}/"
    schema_path = f"abfss://schemas@{STORAGE_ACCOUNT}.dfs.core.windows.net/bronze/{event_type}/"
    target_table = f"{CATALOG}.{SCHEMA}.bronze_{event_type}"

    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", schema_path)
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load(input_path)
        .withColumn("_ingestion_timestamp", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_event_type", F.lit(event_type))
    )

    query = (
        df.writeStream
        .format("delta")
        .option("checkpointLocation", checkpoint_path)
        .option("mergeSchema", "true")
        .trigger(availableNow=True)
        .toTable(target_table)
    )

    query.awaitTermination()
    print(f"Bronze ingestion completed for: {target_table}")

# COMMAND ----------

for event_type in EVENT_TYPES:
    ingest_bronze_table(event_type)

# COMMAND ----------

display(spark.sql(f"SHOW TABLES IN {CATALOG}.{SCHEMA}"))