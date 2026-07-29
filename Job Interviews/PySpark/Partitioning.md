# Partitioning (Spark & Delta)

## Overview
Partitioning controls parallelism and how much data is read. Interviewers test the difference between **in-memory partitions** (Spark parallelism) and **on-disk partitioning** (folder layout for pruning), plus `repartition`/`coalesce` and ZORDER.

---

## Two kinds of "partitioning" (don't confuse them)
| | In-memory partitions | On-disk (table) partitioning |
|---|---|---|
| What | Chunks of a DataFrame across executors | Physical folders by column value |
| Controls | Parallelism (1 task/partition) | Data skipping / partition pruning on read |
| Set by | `repartition`, `coalesce`, `shuffle.partitions` | `partitionBy("date")` on write |

---

## repartition vs coalesce
- `repartition(n[, col])` — **full shuffle**; increase or decrease; even distribution; can partition by column.
- `coalesce(n)` — **no shuffle**; **decrease only**; cheap; possibly uneven. Use before writing to reduce output files.

## On-disk partitioning best practices
- Partition on a **low-cardinality**, frequently-filtered column (usually **date**).
- ❌ Never partition on **high-cardinality** (user_id) → millions of tiny folders/files (small-file disaster).
- Target file sizes **~128MB–1GB**.
- For high-cardinality filter columns, use **ZORDER** (Delta) instead of partitioning.

## Partition pruning
When you filter on the partition column, Spark reads only relevant folders:
```python
spark.read.format("delta").load("/orders").filter("date = '2026-01-01'")  # reads one folder
```

---

## Code
```python
# Write partitioned by date
df.write.format("delta").partitionBy("event_date").saveAsTable("silver.events")

# Reduce output files before write (no shuffle)
df.coalesce(8).write.format("delta").mode("overwrite").save("/gold/x")

# Delta: cluster high-cardinality filter column
# OPTIMIZE silver.events ZORDER BY (customer_id)
```

---

## Scenario Questions
**S1. "Queries filtering by customer_id are slow."** Don't partition by customer_id (high-cardinality). Partition by date, `ZORDER BY (customer_id)`.
**S2. "Too many small files after partitioning by user_id."** Repartition strategy wrong — switch to date partition + ZORDER, run `OPTIMIZE`.
**S3. "Only 4 tasks on a 40-core cluster."** Too few partitions → `repartition(160)` or raise `shuffle.partitions`.

---

## Quick Revision
- ✔ In-memory partitions = parallelism; disk partitioning = pruning
- ✔ `repartition` = shuffle (up/down); `coalesce` = no shuffle (down)
- ✔ Partition on **low-cardinality** (date); ZORDER for high-cardinality
- ✔ Target ~128MB–1GB files; avoid small files
- ✔ Filter on partition column → **partition pruning**

## Common Interview Mistakes
- Partitioning on high-cardinality columns.
- Using `repartition` where `coalesce` avoids a shuffle.
- Ignoring file-size targets → small-file problem.

## Senior-Level Discussion
Seniors size partitions to cluster cores and target file size, distinguish shuffle partitions from write partitions, and combine **date partitioning + ZORDER** with `OPTIMIZE`/auto-compaction to keep both pruning and file sizes healthy.

## Related Topics
[PySpark Interview Questions](PySpark%20Interview%20Questions.md) · [Performance Optimization](../Azure%20Databricks/Performance%20Optimization.md) · [Delta Lake](../Delta%20Lake/)
