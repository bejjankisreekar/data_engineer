"""Silver layer — make data trustworthy: standardized, deduped, bad rows quarantined.

Reads the FULL Bronze history each run and overwrites Silver. That makes the stage
idempotent: re-running produces the same Silver regardless of how many times it ran.
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, row_number, trim, upper
from pyspark.sql.window import Window

import config


def _dedupe_latest(df: DataFrame, keys: list[str]) -> DataFrame:
    """Keep the most recently ingested version of each business key."""
    w = Window.partitionBy(*keys).orderBy(col("_ingest_ts").desc())
    return df.withColumn("_rn", row_number().over(w)).filter("_rn = 1").drop("_rn")


def build_orders(spark: SparkSession) -> None:
    bronze = spark.read.format("delta").load(config.as_uri(config.BRONZE / "orders"))

    clean = bronze.withColumn("region", upper(trim(col("region"))))

    # Quarantine invalid rows instead of dropping them silently.
    bad_cond = (
        col("amount").isNull() | (col("amount") < 0)
        | col("quantity").isNull() | (col("quantity") < 0)
    )
    bad = clean.filter(bad_cond)
    good = clean.filter(~bad_cond)

    if bad.count() > 0:
        (
            bad.write.format("delta").mode("append")
            .save(config.as_uri(config.SILVER / "_quarantine" / "orders"))
        )

    deduped = _dedupe_latest(good, ["order_id", "order_line_id"])
    (
        deduped.write.format("delta").mode("overwrite")
        .option("overwriteSchema", "true")
        .save(config.as_uri(config.SILVER / "orders"))
    )
    print(f"[silver]   orders: {deduped.count()} clean, {bad.count()} quarantined")


def build_dimension_source(spark: SparkSession, entity: str, key: str) -> None:
    """Silver for customers/products: standardize + keep latest version per key."""
    bronze = spark.read.format("delta").load(config.as_uri(config.BRONZE / entity))
    if entity == "customers":
        bronze = bronze.withColumn("region", upper(trim(col("region"))))
    deduped = _dedupe_latest(bronze, [key])
    (
        deduped.write.format("delta").mode("overwrite")
        .option("overwriteSchema", "true")
        .save(config.as_uri(config.SILVER / entity))
    )
    print(f"[silver]   {entity}: {deduped.count()} rows")


def run(spark: SparkSession, batch_date: str) -> None:
    print(f"[silver] batch {batch_date}")
    build_orders(spark)
    build_dimension_source(spark, "customers", "customer_id")
    build_dimension_source(spark, "products", "product_id")
