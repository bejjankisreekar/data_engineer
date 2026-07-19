# Spark Processing — How Spark Executes Your Code

> Prerequisite: [Spark_Architecture.md](Spark_Architecture.md) (driver, executors, tasks).
> This note covers *how* Spark turns DataFrame code into fast parallel execution.

---

## 1. Partitions — the unit of parallelism

A DataFrame isn't one table in one place; it's **many partitions spread across executors**:

```
df (10 GB, 80 partitions)
├─ partition 1  →  executor 1, core 1
├─ partition 2  →  executor 1, core 2
├─ partition 3  →  executor 2, core 1
└─ ...             (each processed independently, in parallel)
```

- More partitions than cores → tasks run in waves (fine).
- Too few partitions → idle cores; too many tiny ones → scheduling overhead.
- You control them with `repartition(n)` (full shuffle) and `coalesce(n)` (merge down, no shuffle).

---

## 2. Transformations vs Actions

| | Transformations | Actions |
|---|---|---|
| What | *Describe* a change | *Trigger* execution |
| Examples | `select`, `filter`, `withColumn`, `groupBy`, `join` | `count()`, `show()`, `collect()`, `write` |
| Runs immediately? | ❌ No — just recorded | ✅ Yes — runs the whole recorded plan |

```python
df2 = df.filter(df.amount > 0)        # nothing happens
df3 = df2.groupBy("region").count()   # still nothing
df3.show()                            # NOW the whole pipeline runs
```

---

## 3. Lazy evaluation — why "nothing happens" is a feature

Spark waits until an action so it can see the **entire plan** and optimize it before running:

- **Predicate pushdown** — if you filter after reading a [Parquet](../02_File_formats/Parquet.md) file, Spark pushes the filter *into the read* and skips whole files/row-groups.
- **Column pruning** — reads only the columns you actually use.
- **Plan rewriting** — the **Catalyst optimizer** reorders/merges operations; the **Tungsten** engine generates efficient bytecode.

Analogy: give a shopper the *whole* grocery list up front and they plan one efficient route; hand them items one at a time and they crisscross the store.

---

## 4. Narrow vs wide transformations (the performance divide)

**Narrow** — each output partition needs only *one* input partition. No data moves between executors. Fast.
`filter`, `select`, `withColumn`, `union`

**Wide** — output partitions need data from *many* input partitions → a **shuffle**: data is written, sent over the network, and regrouped by key. Expensive.
`groupBy`, `join`, `orderBy`, `distinct`, `repartition`

```
NARROW (no movement)            WIDE (shuffle!)
P1 ──▶ P1'                      P1 ─┬─▶ P1' (all "east" rows)
P2 ──▶ P2'                      P2 ─┼─▶ P2' (all "west" rows)
P3 ──▶ P3'                      P3 ─┘   ...regrouped by key
```

Every shuffle ends a **stage** ([Spark_Architecture.md](Spark_Architecture.md)). Minimizing shuffles is 80% of Spark performance tuning.

---

## 5. The DAG

Spark records your transformations as a **DAG (Directed Acyclic Graph)** — a dependency flowchart from source to result. On an action, the DAG is split into stages at shuffle boundaries and executed. Two bonuses:

- **Optimization** — the optimizer rearranges the DAG before running it.
- **Fault tolerance** — if a partition is lost, Spark replays just that branch of the DAG instead of restarting the job.

---

## 6. Caching

If you reuse a DataFrame several times, stop Spark recomputing it from scratch each action:

```python
df_clean = raw.filter(...).join(dims, "id")
df_clean.cache()          # keep in executor memory after first computation
df_clean.count()          # materializes the cache
# ...many later queries on df_clean are now served from RAM
```

Use for iterative work (ML, exploratory analysis); don't cache everything — RAM is shared with processing.

---

## 7. Putting it together

```python
df  = spark.read.parquet(".../sales/")          # transformation (read plan)
big = df.filter(df.amount > 1000)               # narrow
agg = big.groupBy("region").sum("amount")       # wide → shuffle → new stage
agg.write.parquet(".../sales_by_region/")       # ACTION → job starts
```

Execution: **1 job → 2 stages** (split at the groupBy shuffle) **→ one task per partition per stage**, spread across every executor core — with the filter pushed down into the Parquet read and only `region`/`amount` columns ever loaded.

---

## Quick answers for interviews

- *Why is Spark fast?* In-memory processing + lazy evaluation with whole-plan optimization + massive parallelism. (vs [MapReduce](../00_Fundamentals/Hadoop_Architecture.md) writing to disk every stage.)
- *What triggers execution?* Only actions.
- *What's a shuffle and why care?* Network redistribution of data by key; the most expensive operation — it creates stage boundaries.
- *Difference between `repartition` and `coalesce`?* repartition shuffles to any number of partitions; coalesce only merges down, avoiding a shuffle.

---
---

# Part 2 — Advanced

## Join strategies — the biggest performance decision Spark makes

| Strategy | How | When chosen |
|---|---|---|
| **Broadcast hash join** | Ship the small table to *every* executor; no shuffle of the big side | One side under `spark.sql.autoBroadcastJoinThreshold` (default 10 MB) — or you force it |
| **Sort-merge join** | Shuffle *both* sides by key, sort, merge | The default for two large tables |
| **Shuffle hash join** | Shuffle both, build hash map on smaller side | Niche; AQE may pick it |

```python
from pyspark.sql.functions import broadcast
big.join(broadcast(dim_region), "region_id")   # explicit hint — dim tables almost always
```

A fact-to-dimension join that shuffles 2 TB because the optimizer mis-estimated a 50 MB dimension is *the* classic avoidable disaster; `explain()` showing `SortMergeJoin` where you expected `BroadcastHashJoin` is your cue.

## Skew — diagnosing and fixing the straggler

**Symptom:** stage 99% done for an hour; Spark UI shows max task time/shuffle size ≫ median (one `customer_id` owns 40% of rows).

Fixes, in order of preference:

1. **AQE skew handling** (Spark 3+, on by default in Databricks) — automatically splits oversized shuffle partitions. Often just works.
2. **Broadcast the other side** — no shuffle, no skew.
3. **Salting** — manually split the hot key:

```python
# Explode the hot key into 10 sub-keys, join, then the salt disappears in aggregation
from pyspark.sql import functions as F
big  = big.withColumn("salt", (F.rand()*10).cast("int"))
small = small.join(spark.range(10).withColumnRenamed("id","salt"), how="cross")
joined = big.join(small, ["key","salt"])
```

4. Filter/handle the hot key separately (nulls are a common "hot key" — join non-null, union nulls back).

## AQE — what adaptive execution actually changes

Between stages, Spark now looks at *real* sizes and rewrites the rest of the plan:

- **Coalesces shuffle partitions** — the old "tune `spark.sql.shuffle.partitions` (default 200)" ritual mostly dies; 200 partitions of 3 KB become 4 sensible ones.
- **Converts to broadcast join** when a side turns out small post-filter.
- **Splits skewed partitions** (see above).

You still set an upper bound (`spark.sql.shuffle.partitions`) — AQE only merges down. Rule of thumb when tuning manually: **~128 MB per shuffle partition**.

## Caching, persistence levels, and checkpointing

- `cache()` = `persist(MEMORY_AND_DISK)`: evicted partitions recompute from lineage. Other levels (`MEMORY_ONLY`, `DISK_ONLY`, `_SER`) trade CPU vs RAM.
- **Cache is lazy and LRU-evicted** — check the Storage tab to see if it actually fit; a "cached" DataFrame that's 30% in memory silently recomputes the rest.
- **checkpoint()** *truncates lineage* by writing to reliable storage — for iterative algorithms or very long plans where recomputation/planning itself becomes the cost.
- **Uncache when done** (`unpersist()`) — cached data squeezes execution memory and causes spills elsewhere.

## Writing well — the output side of processing

- **Files:** aim 100 MB–1 GB each. `df.repartition(n)` before write controls the count; `coalesce(1)` to "make one CSV" also makes *one task* write it — fine for samples, terrible for TBs.
- **Partitioned writes:** `df.write.partitionBy("year","month")` = pruning for readers; never partition by high-cardinality columns ([OLAP physical design](../00_Fundamentals/OLAP_Storage.md)).
- **Save modes:** `append` / `overwrite` / `errorifexists`; with Delta, prefer `MERGE` for upserts and `replaceWhere` for partition-scoped overwrites.
- Delta maintenance: `OPTIMIZE` (compact small files) + `ZORDER BY (high_cardinality_col)` (co-locate for data skipping), `VACUUM` (purge old versions).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## A real tuning session, in order

1. **Spark UI** → dominant stage → shuffle size, spill, task-time distribution (skew?).
2. `explain()` → shuffles you didn't expect? Joins using the wrong strategy? Filters not pushed (`PushedFilters: []` — casting a column or wrapping it in a function kills pushdown)?
3. Fix *the plan* (broadcast hints, pre-aggregation, salting, partition pruning) before touching *resources*.
4. Only then: partitions → memory → cluster size. Config changes without a plan diagnosis are astrology.

**Shuffle-reduction patterns pros use constantly:** pre-aggregate before joining (`groupBy` first shrinks the shuffle), `select` only needed columns *before* wide ops, filter as early as possible, and reuse one shuffle for multiple aggregations instead of several `groupBy`s over raw data.

## UDF economics

| Kind | Mechanics | Relative speed |
|---|---|---|
| Built-in functions | JVM/whole-stage codegen | 1× (baseline) |
| **pandas UDF** (Arrow) | Vectorized batches to Python | ~2–10× slower |
| Row-by-row Python UDF | Pickle every row to a Python worker | 10–100× slower |

Order of resort: built-ins (`F.*` covers more than people think — `regexp_extract`, `transform` on arrays, `aggregate`) → SQL expressions → pandas UDF → row UDF (last, with a comment justifying it). Also: Python UDFs are a black box to Catalyst — filters can't be pushed through them.

## Exactly-once output — the pro's obsession

Tasks retry; stages replay; jobs re-run on schedule. Every write path must tolerate that:

- **Delta/Iceberg transactional commits** make each write atomic — a half-failed job leaves no partial files visible.
- **Idempotent patterns:** `MERGE` on business keys; `overwrite` a *deterministic* partition (`replaceWhere="date='2026-07-19'"`) rather than blind `append`; streaming's `checkpointLocation` + Delta gives end-to-end exactly-once.
- The blind-`append`-on-retry duplicate is the most common production data bug in existence. Design every job to be **safely re-runnable**, then let your orchestrator retry freely.

## Field-tested gotchas

- `spark.sql.shuffle.partitions` applies to *shuffles*, not reads — input parallelism comes from file splits.
- `dropDuplicates()` is a full shuffle of everything — dedupe within partitions or via window-rank on keys when possible.
- Window functions without `PARTITION BY` pull the entire dataset into **one partition** — the silent single-task killer.
- `count()` on a Delta table is metadata-fast, but `count()` mid-plan still materializes the plan — cache first if you must count *and* proceed.
- Timezones: Spark session timezone silently rewrites timestamps on read/write — pin `spark.sql.session.timeZone` and store UTC ([data type pitfalls](../01_SQL/SQL_Data_Types.md)).

## Interview-grade Q&A

- *How does Spark choose a join strategy, and how do you override it?* Size estimates vs broadcast threshold; override with `broadcast()`/join hints; verify in `explain()`.
- *Your job is slow — walk me through diagnosis.* UI → dominant stage → skew/spill/shuffle → plan via explain → targeted fix; resources last.
- *How do you get exactly-once from an at-least-once world?* Transactional sinks (Delta) + idempotent writes (MERGE / deterministic overwrite) + streaming checkpoints.
- *Why is a Python UDF slow and what's the escalation path?* Row serialization to Python workers + optimizer opacity; built-ins → pandas UDF → row UDF.
