"""Central config: paths and explicit schemas.

Everything is relative to this project folder, so the pipeline runs from a clean
checkout with no edits. In Databricks you would swap LAKE_ROOT / RAW_ROOT for
`abfss://...@storage.dfs.core.windows.net/...` paths and keep the rest identical.
"""
from pathlib import Path

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DecimalType, DateType,
)

PROJECT_ROOT = Path(__file__).resolve().parent

# Source files land here (one folder per daily batch): data/raw/<YYYY-MM-DD>/<entity>.csv
RAW_ROOT = PROJECT_ROOT / "data" / "raw"

# The medallion lake (generated output — gitignored).
LAKE_ROOT = PROJECT_ROOT / "lake"
BRONZE = LAKE_ROOT / "bronze"
SILVER = LAKE_ROOT / "silver"
GOLD = LAKE_ROOT / "gold"


def as_uri(path: Path) -> str:
    """Spark wants a string path; use the OS path (works on Windows and POSIX)."""
    return str(path)


# --- Explicit source schemas (never inferSchema in production; see PySpark note 03) ---

ORDERS_SCHEMA = StructType([
    StructField("order_id", StringType(), False),
    StructField("order_line_id", IntegerType(), False),
    StructField("order_date", DateType(), False),
    StructField("customer_id", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("quantity", IntegerType(), True),
    StructField("amount", DecimalType(12, 2), True),
    StructField("region", StringType(), True),
])

CUSTOMERS_SCHEMA = StructType([
    StructField("customer_id", StringType(), False),
    StructField("name", StringType(), True),
    StructField("city", StringType(), True),
    StructField("region", StringType(), True),
    StructField("email", StringType(), True),
])

PRODUCTS_SCHEMA = StructType([
    StructField("product_id", StringType(), False),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("unit_price", DecimalType(12, 2), True),
])

SCHEMAS = {
    "orders": ORDERS_SCHEMA,
    "customers": CUSTOMERS_SCHEMA,
    "products": PRODUCTS_SCHEMA,
}
