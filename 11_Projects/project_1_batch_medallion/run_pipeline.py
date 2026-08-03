"""Run the full medallion pipeline end to end.

Usage:
    python run_pipeline.py                 # process both sample batches in order
    python run_pipeline.py 2026-08-02      # process a single batch
    python run_pipeline.py --show          # process both, then print the Gold tables

Processing the two batches in order demonstrates the interesting behaviour:
Alice (C001) moves Seattle -> Denver on day 2, so dim_customer gains a second row
(SCD2), while her day-1 orders still point at the Seattle version.
"""
import sys

from src import bronze, silver, gold
from src.common import get_spark
import config

BATCHES = ["2026-08-02", "2026-08-03"]


def process_batch(spark, batch_date: str) -> None:
    print(f"\n=== processing batch {batch_date} ===")
    bronze.run(spark, batch_date)
    silver.run(spark, batch_date)
    gold.run(spark, batch_date)


def show_gold(spark) -> None:
    print("\n=== dim_customer (SCD2 — note C001 has two rows) ===")
    (
        spark.read.format("delta").load(config.as_uri(config.GOLD / "dim_customer"))
        .orderBy("customer_id", "valid_from").show(truncate=False)
    )
    print("=== fact_sales ===")
    (
        spark.read.format("delta").load(config.as_uri(config.GOLD / "fact_sales"))
        .orderBy("date_key", "order_id", "order_line_id").show(truncate=False)
    )
    print("=== quarantined orders (bad rows kept for inspection) ===")
    try:
        spark.read.format("delta").load(
            config.as_uri(config.SILVER / "_quarantine" / "orders")
        ).show(truncate=False)
    except Exception:
        print("(none)")


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--show"]
    show = "--show" in sys.argv
    batches = args if args else BATCHES

    spark = get_spark()
    for batch_date in batches:
        process_batch(spark, batch_date)
    if show or not args:
        show_gold(spark)
    spark.stop()
    print("\nDone. Delta tables are under ./lake/{bronze,silver,gold}.")


if __name__ == "__main__":
    main()
