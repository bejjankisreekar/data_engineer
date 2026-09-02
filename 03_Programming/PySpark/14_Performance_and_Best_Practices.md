# 14 — Performance & Best Practices (Capstone)

> Prev: [Structured Streaming](13_Structured_Streaming.md) · Series home: [Learning Path](00_PySpark_Learning_Path.md)

This file consolidates the tuning knowledge scattered through the series into one workflow, then covers what the series hasn't yet: testing, project structure, and production habits. Deep theory lives in [Spark_Processing.md](Spark_Processing.md) and [Spark_Architecture.md](Spark_Architecture.md) — this is the practitioner's checklist.

---

## The performance workflow (in order, always)

```
1. MEASURE   Spark UI → which stage dominates? skew? spill? shuffle sizes?
2. PLAN      df.explain() → unexpected shuffles? wrong join strategy? filters not pushed?
3. FIX PLAN  broadcast hints, pre-aggregation, early filters/selects, salting
4. FIX DATA  file sizes (OPTIMIZE), partitioning/clustering, stats
5. FIX RESOURCES  partitions, memory, cluster size — LAST, not first
```

Jumping to step 5 ("just use a bigger cluster") without steps 1–2 is the defining junior mistake — and occasionally the right answer, but only *after* the diagnosis says so.

### The high-yield fixes, ranked by how often they're the answer

1. **Read less**: filter early on partition/cluster columns, select only needed columns, [sargable predicates](../../02_Databases/SQL/06_SQL_DQL.md) so [Parquet pushdown](../../05_Storage_and_Formats/File_Formats/05_Parquet.md) works.
2. **Broadcast the small side** of joins ([file 07](07_Joins.md)) — verify in the plan.
3. **Fix skew** — AQE first, then salting/hot-key handling ([file 07](07_Joins.md), [Spark_Processing](Spark_Processing.md)).
4. **Compact small files** — `OPTIMIZE`, sane writer partitioning ([files 04](04_Reading_and_Writing_Data.md), [12](12_Delta_Lake_with_PySpark.md)).
5. **Kill UDFs** that built-ins can replace ([file 10](10_UDFs_and_Pandas_Integration.md)).
6. **Cache only reused intermediates** — and `unpersist` after ([Spark_Processing](Spark_Processing.md)).
7. Shuffle partition sizing — mostly AQE's job now; target ~128 MB/partition when manual.

---

## Writing PySpark like software (because it is)

### Structure jobs as testable functions

```python
# transformations.py — pure functions: DataFrame in, DataFrame out, no I/O
def clean_orders(df: DataFrame) -> DataFrame:
    return (df.filter(F.col("order_id").isNotNull())
              .withColumn("amount", F.col("amount").cast("decimal(18,4)")))

# job.py — thin I/O shell around them
df = spark.read.table(f"{catalog}.bronze.orders")
clean_orders(df).write.mode("append").saveAsTable(f"{catalog}.silver.orders")
```

I/O at the edges, logic in pure functions — the single structural habit that makes everything below possible.

### Test them

```python
# test_transformations.py — runs on local[*] Spark (pytest fixture), no cluster needed
def test_clean_orders_drops_null_ids(spark):
    src = spark.createDataFrame([(1, "10.5"), (None, "9.0")], "order_id long, amount string")
    out = clean_orders(src)
    assert out.count() == 1
    assert dict(out.dtypes)["amount"] == "decimal(18,4)"
```

Unit-test transformations with tiny inline DataFrames; integration-test pipelines against sample files; data-quality-test *production data* with [expectations at the boundaries](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md). `pyspark` installs from pip — CI runs all of this on a plain build agent.

### Parameterize environment, never hardcode it

Catalog/schema/paths come from job parameters or config (`dev` vs `prod` — [namespace note](11_Spark_SQL_and_Views.md)); secrets from Key Vault/secret scopes ([never literals](04_Reading_and_Writing_Data.md)); code in git, deployed via CI (Databricks Asset Bundles is the current standard), not cloned notebooks ([the discipline](../../08_Databricks/02_Why_Spark_Why_Databricks.md)).

### Make every job idempotent — the checklist

- Write with MERGE-by-key or `replaceWhere`-scoped overwrite, never blind append ([files 12](12_Delta_Lake_with_PySpark.md), [04](04_Reading_and_Writing_Data.md)).
- Watermarks/state committed atomically with the data ([ETL gotchas](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md)).
- Ask of every job: *"what happens if this runs twice?"* — if the answer is "duplicates," it's not done.

---

## Pro corner

### The incident playbook (what actually breaks in production)

| Symptom | First suspects | Where covered |
|---|---|---|
| Job suddenly 5× slower, no code change | Input data grew/skewed; small-file buildup; stats stale | [07](07_Joins.md), [12](12_Delta_Lake_with_PySpark.md) |
| Executor OOM | Skewed partition; oversized broadcast; UDF memory (Python side) | [Spark_Architecture](Spark_Architecture.md), [10](10_UDFs_and_Pandas_Integration.md) |
| Driver OOM | `collect`/`toPandas` on big data; huge query plan (loops adding columns); too many tasks' results | [02](02_DataFrame_Basics.md), [10](10_UDFs_and_Pandas_Integration.md) |
| `FetchFailedException` | Executor churn (spot eviction, OOM kills) → shuffle data lost; stage retries | [Spark_Architecture](Spark_Architecture.md) |
| Duplicated rows after a failure | Non-idempotent write + retry | this file, [12](12_Delta_Lake_with_PySpark.md) |
| "99% done for an hour" | Skew (one straggler task) — check max vs median task time | [07](07_Joins.md), [Spark_Processing](Spark_Processing.md) |
| Numbers differ between runs | Nondeterminism: `first()` without order, float summation order, `current_timestamp` in logic | [06](06_Aggregations_and_Grouping.md) |

### Query-plan smells (one `explain()` scan)

`CartesianProduct` (missed join condition) · `SortMergeJoin` against a tiny dim (missed broadcast) · `Exchange` repeated with the same keys (unshared window/join partitioning) · `Filter` *above* the scan with `PushedFilters: []` (non-sargable) · `BatchEvalPython` (row UDF in the hot path) · a plan hundreds of lines long from loop-generated columns (checkpoint or rewrite with `select(*exprs)`).

### Cost habits (Databricks specifics)

Job clusters + auto-terminate + spot workers as the default ([cost levers](../../08_Databricks/02_Why_Spark_Why_Databricks.md)); Photon for SQL-shaped work, not UDF-heavy work; `availableNow` triggers instead of 24/7 streams unless latency pays for itself ([13](13_Structured_Streaming.md)); tag jobs and review the cost dashboard monthly — a data platform's bill is an engineering artifact, not an act of God ([FinOps](../../04_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md)).

### The senior checklist for any new pipeline

1. Contract: schema declared, drift policy chosen, owner named ([03](03_Schemas_and_Data_Types.md), [JSON drift](../../05_Storage_and_Formats/File_Formats/02_JSON.md)).
2. Idempotent writes + retry-safe orchestration.
3. Quality gates with quarantine + alert, not silent drops ([ETL](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md)).
4. Reconciliation counts logged every run ([06](06_Aggregations_and_Grouping.md)).
5. OPTIMIZE/VACUUM/retention scheduled from day one ([12](12_Delta_Lake_with_PySpark.md)).
6. Runbook: what to do when it fails at 3am — written by the person who built it.
7. And the [pre-question](../../01_Foundations/Fundamentals/03_Distributed_Computing.md): does this workload need Spark at all?

## Checkpoint (series final)

1. A nightly join-heavy job crept from 20 to 90 minutes over six months. Walk the full diagnosis, in order.
2. Design the testing pyramid for a bronze→silver→gold pipeline: what's unit-tested, integration-tested, and data-tested?
3. Your team wants to "add a bigger cluster" as the fix for a slow job. What do you check first, and what evidence would justify the bigger cluster?

**You've reached the end of the series.** From here: practice on real datasets, read the [concept track](00_PySpark_Learning_Path.md) files if you skipped them, and revisit each file's Pro corner before interviews — they're written to be the answers.

---

## Further Learning — Docs & Videos

**Documentation**
- Spark performance tuning: https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Adaptive Query Execution (AQE): https://spark.apache.org/docs/latest/sql-performance-tuning.html#adaptive-query-execution
- Databricks optimization guide: https://docs.databricks.com/en/optimizations/index.html

**Videos**
- PySpark performance tuning (partitioning, caching, AQE, skew): https://www.youtube.com/results?search_query=pyspark+performance+tuning+partitioning+shuffle+skew
