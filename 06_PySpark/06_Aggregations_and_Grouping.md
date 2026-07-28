# 06 — Aggregations & Grouping

> Prev: [Column Operations](05_Column_Operations_and_Functions.md) · Next: [Joins](07_Joins.md)

Same concepts as [SQL aggregation](../01_SQL/08_SQL_Aggregate_Functions.md) — `groupBy` = GROUP BY, and every SQL rule (null behavior, WHERE-vs-HAVING) carries over. What's new is the distributed cost model underneath.

---

## Level 1 — The basics

```python
# Whole-table aggregates
emp.agg(F.count("*"), F.avg("salary"), F.max("salary")).show()

# Per-group
(emp.groupBy("dept")
    .agg(F.count("*").alias("headcount"),
         F.avg("salary").alias("avg_salary"),
         F.sum("salary").alias("payroll"),
         F.min("hire_date").alias("first_hire"))
    .show())

# Multiple grouping columns
sales.groupBy("region", "year").agg(F.sum("amount").alias("revenue"))

# HAVING = filter AFTER the agg
(emp.groupBy("dept").agg(F.avg("salary").alias("avg_sal"))
    .filter(F.col("avg_sal") > 55000))
```

Shortcuts (`.count()`, `.sum("salary")`, `.avg(...)` directly on groupBy) exist, but `.agg()` with aliases is the professional form — explicit names, many aggregates at once.

### The aggregate functions you'll reach for

```python
F.count("*")               # rows          F.countDistinct("cust_id")
F.sum(), F.avg(), F.min(), F.max()
F.first(), F.last()        # ⚠ nondeterministic without ordering!
F.collect_list("item")     # group values → array (keeps duplicates)
F.collect_set("item")      # → array of distinct values
F.sum(F.when(F.col("region")=="East", F.col("amount")).otherwise(0))   # conditional agg / manual pivot
F.approx_count_distinct("user_id")   # HyperLogLog — big-data cardinality (~2% err)
```

Nulls are ignored by aggregates exactly as in SQL — `F.count("col")` vs `F.count("*")` differ by the null count ([details](../01_SQL/08_SQL_Aggregate_Functions.md)).

---

## Level 2 — Pivot, rollup, cube

```python
# PIVOT — rows → columns
(sales.groupBy("region")
      .pivot("year", [2024, 2025, 2026])       # listing values = faster + stable schema
      .agg(F.sum("amount"))
      .show())
# region | 2024 | 2025 | 2026

# Unpivot back (Spark 3.4+)
wide.unpivot("region", ["2024", "2025", "2026"], "year", "amount")

# Subtotals
sales.rollup("region", "store").agg(F.sum("amount"))   # (r,s) + (r) + grand total
sales.cube("region", "year").agg(F.sum("amount"))      # every combination
# distinguish subtotal-null from data-null:
.withColumn("is_total", F.grouping("store"))
```

Same semantics as [SQL ROLLUP/CUBE](../01_SQL/08_SQL_Aggregate_Functions.md).

### What actually happens: partial aggregation

`groupBy().agg()` runs in two phases: each partition pre-aggregates locally (map-side), then only the compact partials **shuffle** by key for the final combine ([shuffle mechanics](Spark_Processing.md)). This is why aggregating 1 TB down to 50 groups ships kilobytes over the network — and why `collect_list` is different: it can't pre-shrink (it keeps every value), so it ships *everything*. Treat `collect_list` on big groups as a red flag.

---

## Level 3 — Pro corner

- **Cost driver = number of distinct groups**, not table size: `groupBy("region")` (12 groups) is trivial at any scale; `groupBy("customer_id")` (500M groups) is a monster that may spill ([hash agg spills](../01_SQL/08_SQL_Aggregate_Functions.md)). Design metrics tables around group cardinality.
- **countDistinct at scale**: exact distinct forces expensive shuffles and limits query shapes; `approx_count_distinct` for dashboards, exact only for reconciliation ([OLAP approximation](../00_Fundamentals/02_OLAP_Storage.md)).
- **`first()`/`last()` without ordering are nondeterministic across runs** — never build logic on them; use a [window + row_number](08_Window_Functions.md) for "latest per key."
- **Skewed groups** (one key = 40% of rows) make one task the straggler — AQE mostly handles it; for extreme cases, two-phase salt-then-aggregate ([skew fixes](Spark_Processing.md)).
- **Pre-aggregate before joins**: `orders.groupBy("cust").agg(...)` *then* join to customers ships far less than join-then-aggregate ([join grain](../01_SQL/07_SQL_Keys_and_Joins.md)) — the single most common query rewrite in tuning sessions.
- **Aggregates as data-quality checks** — the [instrumentation habit](../01_SQL/08_SQL_Aggregate_Functions.md) in PySpark form:

```python
(df.groupBy("load_date").agg(
    F.count("*").alias("rows"),
    F.countDistinct("order_id").alias("dist_orders"),        # ≠ rows → duplicates!
    F.sum(F.when(F.col("amount") < 0, 1).otherwise(0)).alias("neg_amounts"),
    F.min("order_ts"), F.max("order_ts"))
 ).show()
```

- **Re-aggregatability**: store `SUM` and `COUNT` in summary tables, never `AVG` — averages of averages lie ([why](../01_SQL/08_SQL_Aggregate_Functions.md)).

## Checkpoint

1. Revenue and order count per region per month, only months with revenue > 1M, sorted.
2. Pivot that into regions × months. Why list the pivot values explicitly?
3. Why is `collect_list` more expensive than `sum` on the same groups?

Next: combining tables → [07 — Joins](07_Joins.md).

---

## Further Learning — Docs & Videos

**Documentation**
- GroupBy and aggregation: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.groupBy.html
- Aggregate functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html

**Videos**
- PySpark groupBy and aggregations: https://www.youtube.com/results?search_query=pyspark+groupby+aggregation+tutorial
