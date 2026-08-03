# Performance Optimization

## Why this note exists (and how it links to cost)

[PySpark Performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md) covers the coding details; this note frames the **big performance levers** as an engineer's diagnostic toolkit — the things you check when a job is slow — and connects each to **cost**, because a faster job is a cheaper job ([Databricks cost](02_Databricks_Cost_Optimization.md)).

Analogy: optimizing a Spark job is like **unclogging a highway**. The cars (data) are fine; the jams come from a few specific bottlenecks — everyone merging at one exit (skew), cars reshuffling lanes constantly (shuffle), toll booths reading every car (full scans). Fix the bottleneck, not the cars.

---

## The #1 concept: the shuffle

A **shuffle** is when Spark **redistributes data across the network** so related rows land on the same executor — required by wide operations: `groupBy`, `join`, `distinct`, `orderBy`, window functions. Shuffles are the **most expensive** thing Spark does (network + disk + serialization).

You can't eliminate shuffles, but you **minimize** them:
- Filter and aggregate **early** so less data shuffles.
- Avoid unnecessary wide operations and repeated re-shuffles.
- Use **broadcast joins** (below) to skip shuffling a small table.

Understanding shuffle is the single biggest Spark-performance interview topic.

---

## Data skew — the silent killer

**Skew** = data unevenly distributed across partitions, so one task does most of the work while the rest finish and idle. Symptom in the Spark UI: one task takes 10× longer than its peers. Cause: a **skewed join/group key** (e.g., 40% of rows have `country = 'US'`, or a `null` key).

Fixes:
- **AQE (Adaptive Query Execution)** — on by default in modern Spark; auto-splits skewed partitions.
- **Salting** — add a random suffix to the hot key to spread it, then aggregate back.
- **Broadcast** the smaller side if applicable.
- **Filter out** junk keys (nulls) before the join.

Skew is *the* reason "a job that used to be fine suddenly drags" — often data grew lopsided.

---

## Broadcast joins

When joining a **big** table to a **small** one, broadcasting the small table to every executor avoids shuffling the big one entirely:

```python
from pyspark.sql.functions import broadcast
result = big_fact.join(broadcast(small_dim), "dim_id")
```

Spark auto-broadcasts tables under a threshold, but hinting `broadcast()` on a known-small dimension is a classic, high-impact win — exactly the customer/product dim joins from [Project 1](../11_Projects/02_Project_1_Batch_Medallion_Pipeline.md).

---

## Caching / persistence

If you reuse a DataFrame multiple times (multiple actions or downstream models), **cache** it so Spark doesn't recompute the whole lineage each time:

```python
df.cache()      # or .persist(StorageLevel...)
df.count()      # materialize it once
# subsequent uses read from cache
```

But cache **deliberately** — caching everything wastes memory and can *hurt*. Cache when a DataFrame is **expensive to compute and reused**; don't cache a once-used or trivially-cheap one.

---

## Reading less: pruning & pushdown

The cheapest work is work you skip ([storage cost](03_Storage_and_Query_Cost.md)):
- **Partition pruning** — filter on the partition column so whole folders are skipped.
- **Predicate pushdown** — filters pushed into the file read (Parquet/Delta), so non-matching data is never loaded.
- **Column pruning** — select only needed columns from columnar formats.

Together these can cut the data a job touches by orders of magnitude — the biggest lever of all.

---

## Diagnosing with the Spark UI

You optimize what you measure. The **Spark UI** shows where time goes:

| Symptom in UI | Likely cause | Fix |
|---|---|---|
| One task ≫ others | **Skew** | AQE / salting / filter junk keys |
| Huge "Shuffle Read/Write" | Excess shuffling | Filter early, broadcast, fewer wide ops |
| Lots of **spill** to disk | Under-provisioned memory / partitions too big | More memory or repartition |
| Many tiny tasks | Too many small files | `OPTIMIZE`/compaction |
| Executors idle | Over-provisioned cluster / low parallelism | Right-size ([cost](02_Databricks_Cost_Optimization.md)) |

"How would you debug a slow Spark job?" → *"Open the Spark UI, find the slow stage, and look for skew, shuffle, or spill."* is the answer interviewers want.

---

## Interview-grade Q&A

- *What is a shuffle and why is it expensive?* Redistributing data across the network so related rows co-locate (for join/groupBy/distinct/orderBy). It's costly (network+disk+serialization); minimize by filtering early and broadcasting.
- *What is data skew and how do you fix it?* Uneven data across partitions so one task dominates; fix with AQE, salting the hot key, broadcasting, or filtering junk keys.
- *When and how do you use a broadcast join?* Joining a big table to a small one — broadcast the small side to avoid shuffling the big one (`broadcast(df)`); Spark also auto-broadcasts under a threshold.
- *When should you cache?* When a DataFrame is expensive to compute and reused multiple times — not indiscriminately.
- *How do you make a job scan less data?* Partition pruning, predicate pushdown, and column pruning with columnar formats.
- *How do you debug a slow Spark job?* Use the Spark UI to find the slow stage and diagnose skew/shuffle/spill/small-files.
- *How does performance relate to cost?* A faster job uses less compute-time, so optimizing speed directly lowers cost.

---

## Further Learning — Docs & Videos
- Spark performance tuning: https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Adaptive Query Execution: https://learn.microsoft.com/azure/databricks/optimizations/aqe
- Handling data skew: https://learn.microsoft.com/azure/databricks/optimizations/
- Video — Spark performance tuning: https://www.youtube.com/results?search_query=spark+performance+tuning+shuffle+skew
