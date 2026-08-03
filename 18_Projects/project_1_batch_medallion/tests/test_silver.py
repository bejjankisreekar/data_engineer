"""Unit tests for the Silver transforms — the kind of tests a data CI pipeline runs.

Run:  pytest -q     (from the project folder)

These use a local Spark session and small in-memory DataFrames — no lake, no Azure.
They demonstrate the two Silver guarantees: dedupe and quarantine.
"""
import datetime as dt
from decimal import Decimal

import pytest

from src.common import get_spark
from src.silver import _dedupe_latest


@pytest.fixture(scope="session")
def spark():
    s = get_spark("silver-tests")
    yield s
    s.stop()


def test_dedupe_keeps_latest_ingest(spark):
    rows = [
        # same business key, two ingests — the later _ingest_ts must win
        ("O1", 1, "OLD", dt.datetime(2026, 8, 2, 1, 0, 0)),
        ("O1", 1, "NEW", dt.datetime(2026, 8, 3, 1, 0, 0)),
        ("O2", 1, "ONLY", dt.datetime(2026, 8, 2, 1, 0, 0)),
    ]
    df = spark.createDataFrame(rows, ["order_id", "order_line_id", "payload", "_ingest_ts"])

    out = {
        (r["order_id"], r["order_line_id"]): r["payload"]
        for r in _dedupe_latest(df, ["order_id", "order_line_id"]).collect()
    }

    assert out[("O1", 1)] == "NEW"        # newest ingest kept
    assert out[("O2", 1)] == "ONLY"
    assert len(out) == 2                    # duplicate collapsed


def test_bad_rows_are_split_from_good(spark):
    from pyspark.sql.functions import col

    rows = [
        ("O1", 1, Decimal("9.99"), 1),      # good
        ("O2", 1, Decimal("-9.99"), 1),     # bad: negative amount
        ("O3", 1, None, 2),                 # bad: null amount
        ("O4", 1, Decimal("5.00"), -1),     # bad: negative quantity
    ]
    df = spark.createDataFrame(rows, ["order_id", "order_line_id", "amount", "quantity"])

    bad_cond = (
        col("amount").isNull() | (col("amount") < 0)
        | col("quantity").isNull() | (col("quantity") < 0)
    )
    good = df.filter(~bad_cond)
    bad = df.filter(bad_cond)

    assert good.count() == 1
    assert bad.count() == 3
