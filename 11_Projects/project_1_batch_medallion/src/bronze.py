"""Bronze layer — land raw data faithfully, add ingestion metadata, never transform.

Bronze is append-only and reprocessable: because we keep every raw row plus where it
came from, Silver/Gold can always be rebuilt without re-reading the source.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit

import config


def load_entity(spark: SparkSession, entity: str, batch_date: str) -> int:
    src = config.RAW_ROOT / batch_date / f"{entity}.csv"
    raw = (
        spark.read.option("header", True)
        .schema(config.SCHEMAS[entity])       # explicit schema — never inferSchema in prod
        .csv(config.as_uri(src))
    )

    bronze = (
        raw.withColumn("_ingest_ts", current_timestamp())
        .withColumn("_source_file", input_file_name())
        .withColumn("_batch_date", lit(batch_date))
    )

    dest = config.BRONZE / entity
    (
        bronze.write.format("delta")
        .mode("append")
        .partitionBy("_batch_date")
        .option("mergeSchema", "true")        # tolerate a new column arriving on a later day
        .save(config.as_uri(dest))
    )
    return bronze.count()


def run(spark: SparkSession, batch_date: str) -> None:
    print(f"[bronze] batch {batch_date}")
    for entity in ("orders", "customers", "products"):
        n = load_entity(spark, entity, batch_date)
        print(f"[bronze]   {entity}: appended {n} rows")
