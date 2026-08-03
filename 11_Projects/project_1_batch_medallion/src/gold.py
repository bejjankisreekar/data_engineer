"""Gold layer — the business-ready star schema.

- dim_date       : conformed date dimension (rebuilt from Silver)
- dim_product    : SCD Type 1 (latest values overwrite) with a surrogate key
- dim_customer   : SCD Type 2 (history kept) via Delta MERGE — the interesting one
- fact_sales     : grain = one row per order line, joined to the dim version valid
                   at the order date (so old orders keep the old customer city)
"""
from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, concat_ws, crc32, date_format, dayofmonth, lit, month, year,
)

import config


def build_dim_date(spark: SparkSession) -> None:
    orders = spark.read.format("delta").load(config.as_uri(config.SILVER / "orders"))
    dim = (
        orders.select("order_date").distinct()
        .withColumn("date_key", date_format("order_date", "yyyyMMdd").cast("int"))
        .withColumn("year", year("order_date"))
        .withColumn("month", month("order_date"))
        .withColumn("day", dayofmonth("order_date"))
    )
    (
        dim.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
        .save(config.as_uri(config.GOLD / "dim_date"))
    )


def build_dim_product(spark: SparkSession) -> None:
    products = spark.read.format("delta").load(config.as_uri(config.SILVER / "products"))
    dim = products.select(
        crc32(col("product_id")).alias("product_key"),
        "product_id", "product_name", "category", "unit_price",
    )
    (
        dim.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
        .save(config.as_uri(config.GOLD / "dim_product"))
    )


def _new_customer_versions(df, batch_date: str):
    bd = lit(batch_date).cast("date")
    return (
        df.select("customer_id", "name", "city", "region", "email")
        .withColumn("valid_from", bd)
        .withColumn("valid_to", lit(None).cast("date"))
        .withColumn("is_current", lit(True))
        .withColumn(
            "customer_key",
            crc32(concat_ws("|", col("customer_id"), col("valid_from").cast("string"))),
        )
    )


def build_dim_customer(spark: SparkSession, batch_date: str) -> None:
    """SCD2: close changed rows, append new versions; brand-new customers inserted."""
    incoming = spark.read.format("delta").load(config.as_uri(config.SILVER / "customers"))
    path = config.as_uri(config.GOLD / "dim_customer")

    # First ever load: everyone is a fresh current row.
    if not DeltaTable.isDeltaTable(spark, path):
        _new_customer_versions(incoming, batch_date).write.format("delta") \
            .mode("overwrite").save(path)
        return

    dim = DeltaTable.forPath(spark, path)
    current_open = (
        dim.toDF().filter("is_current = true")
        .select("customer_id", col("city").alias("_cur_city"))
    )

    # Rows that are new (no open row) or changed (city differs).
    to_add = (
        incoming.join(current_open, "customer_id", "left")
        .filter(col("_cur_city").isNull() | (col("city") != col("_cur_city")))
    )

    # Step 1: close the currently-open row for customers whose city changed.
    (
        dim.alias("t")
        .merge(incoming.alias("s"), "t.customer_id = s.customer_id AND t.is_current = true")
        .whenMatchedUpdate(
            condition="t.city <> s.city",
            set={"is_current": "false", "valid_to": f"cast('{batch_date}' as date)"},
        )
        .execute()
    )

    # Step 2: append the new current version for changed + brand-new customers.
    _new_customer_versions(to_add, batch_date).write.format("delta").mode("append").save(path)


def build_fact_sales(spark: SparkSession) -> None:
    orders = spark.read.format("delta").load(config.as_uri(config.SILVER / "orders")).alias("o")
    dc = spark.read.format("delta").load(config.as_uri(config.GOLD / "dim_customer")).alias("c")
    dp = spark.read.format("delta").load(config.as_uri(config.GOLD / "dim_product")).alias("p")
    dd = spark.read.format("delta").load(config.as_uri(config.GOLD / "dim_date")).alias("d")

    # Join to the customer version that was valid on the order date (SCD2-aware).
    scd2_match = (
        (col("o.customer_id") == col("c.customer_id"))
        & (col("o.order_date") >= col("c.valid_from"))
        & (col("c.valid_to").isNull() | (col("o.order_date") < col("c.valid_to")))
    )

    fact = (
        orders
        .join(dc, scd2_match, "left")
        .join(dp, col("o.product_id") == col("p.product_id"), "left")
        .join(dd, col("o.order_date") == col("d.order_date"), "left")
        .select(
            col("d.date_key"),
            col("c.customer_key"),
            col("p.product_key"),
            col("o.order_id"),
            col("o.order_line_id"),
            col("o.quantity"),
            col("o.amount"),
            col("o.region"),
        )
    )
    (
        fact.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
        .save(config.as_uri(config.GOLD / "fact_sales"))
    )
    print(f"[gold]   fact_sales: {fact.count()} rows")


def run(spark: SparkSession, batch_date: str) -> None:
    print(f"[gold] batch {batch_date}")
    build_dim_date(spark)
    build_dim_product(spark)
    build_dim_customer(spark, batch_date)   # SCD2 — must run before the fact
    build_fact_sales(spark)
