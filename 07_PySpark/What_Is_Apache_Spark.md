# What is Apache Spark?

## Definition

**Apache Spark is an open-source, distributed, in-memory data processing engine.** Unpack that word by word:

- **Open-source** — free, maintained by the Apache Software Foundation, huge community.
- **Distributed** — it splits work across a [cluster of machines](../00_Fundamentals/03_Distributed_Computing.md) so it can handle data far bigger than one machine.
- **In-memory** — it keeps intermediate data in RAM instead of writing to disk between steps (the key speed advantage over [Hadoop MapReduce](../00_Fundamentals/05_Hadoop_Architecture.md)).
- **Processing engine** — it *computes*; it does **not store** data. Spark reads from storage (Azure Data Lake, S3, databases, Kafka), transforms the data, and writes results back out.

Born at UC Berkeley's AMPLab in 2009, became a top-level Apache project in 2014, and is today the de facto standard engine for big data — the engine inside Databricks, Microsoft Fabric, AWS Glue, and more.

---

## Analogy

If your data lake is a giant warehouse of raw ingredients, Spark is a **fleet of chefs with a head chef**: the head chef (driver) reads the recipe once, splits it into steps, and hundreds of chefs (executors) cook their portion simultaneously — keeping ingredients on the counter (RAM) instead of walking to the pantry (disk) between every step.

---

## What can Spark do? (one engine, many workloads)

| Library | Workload | Example |
|---|---|---|
| **Spark SQL / DataFrames** | Batch processing & SQL | Clean 2 TB of sales data nightly |
| **Structured Streaming** | Near-real-time streams | Process Kafka events as they arrive |
| **MLlib** | Machine learning | Train a churn model on full history |
| **GraphX / GraphFrames** | Graph processing | Social-network analysis |
| **pandas API on Spark** | pandas code at scale | Reuse pandas skills on big data |

Before Spark you needed a different tool for each of these. One engine + one API = the main reason it won.

---

## Languages

Spark is written in Scala (runs on the JVM) but you can use it from:

- **Python (PySpark)** ← most common for data engineers, and the focus of this folder
- SQL
- Scala, Java, R

```python
# PySpark taste — this one snippet runs across a whole cluster
df = spark.read.parquet("abfss://raw@datalake.dfs.core.windows.net/sales/")
result = (df.filter(df.amount > 0)
            .groupBy("region")
            .sum("amount"))
result.write.parquet("abfss://curated@datalake.dfs.core.windows.net/sales_by_region/")
```

Notice: no loops, no thread management, no "which machine does what." You describe *what* you want; Spark's engine plans *how* to do it in parallel.

---

## Key ideas to know

| Concept | Meaning |
|---|---|
| **DataFrame** | Distributed table (rows/columns) — your main working object |
| **Partition** | One chunk of a DataFrame, processed by one task on one core |
| **Transformation** | An operation that *describes* a change (filter, groupBy) — not run yet |
| **Action** | An operation that *triggers* execution (count, write, show) |
| **Lazy evaluation** | Spark collects all transformations, then optimizes and runs the whole plan at once when an action is called |

These are covered in depth in [Spark_Processing.md](Spark_Processing.md), and the cluster components in [Spark_Architecture.md](Spark_Architecture.md).

---

## What Spark is NOT

- ❌ Not a database — no storage of its own
- ❌ Not a data warehouse — though it can power one (lakehouse)
- ❌ Not for small data — spinning up a cluster to process 10 MB is overkill; use pandas
- ❌ Not the same thing as Databricks — Databricks is a commercial *platform built around* Spark (see [Why_Spark_Why_Databricks.md](Why_Spark_Why_Databricks.md))

---

## Where it sits in the big picture

```
Sources (OLTP DBs, APIs, Kafka)
        ↓
Data Lake (ADLS / S3 — storage)
        ↓
★ SPARK (processing: clean, join, aggregate) ★
        ↓
Warehouse / Delta tables / ML models / Dashboards
```

For the history of how we got here, see [06_Big_Data_Evolution_Timeline.md](../00_Fundamentals/06_Big_Data_Evolution_Timeline.md).

---
---

# Part 2 — Advanced

## The three APIs: RDD → DataFrame → Dataset

| API | What it is | When you'd touch it |
|---|---|---|
| **RDD** (2011) | Resilient Distributed Dataset — a raw distributed collection of Java/Python objects with functional ops (`map`, `reduceByKey`) | Almost never directly today; it's the substrate everything compiles down to |
| **DataFrame** (2015) | Distributed table with named, typed columns + a **query optimizer** | Your default, always |
| **Dataset** (2016) | DataFrame + compile-time types | Scala/Java only; PySpark has no Dataset |

Why DataFrames beat RDDs: an RDD `lambda` is a black box Python function Spark must run as-is; a DataFrame expression (`col("amount") > 0`) is *data Spark can reason about* — reorder, push down, compile to JVM bytecode. Same logic, radically better plan. Rule: **stay inside DataFrame/SQL expressions; drop to RDDs only when the API truly can't express the operation.**

## What "resilient" means — lineage

Every DataFrame/RDD remembers the **lineage** of operations that produced it (read → filter → join…). Spark doesn't replicate intermediate data; if a partition is lost with an executor, it **recomputes just that partition** from lineage. Fault tolerance by *recomputation*, not duplication — cheap until lineage gets very long (see checkpointing in [Spark_Processing.md](Spark_Processing.md)).

## Catalyst & Tungsten — the engine room

Your code takes this trip on every action:

```
DataFrame/SQL
  → Unresolved logical plan     (parse)
  → Analyzed plan               (resolve columns/types via catalog)
  → Optimized logical plan      (CATALYST: pushdown, pruning, constant folding, join reordering)
  → Physical plans → cost-based choice   (which join strategy, etc.)
  → Whole-stage codegen         (TUNGSTEN: fuse operators into tight JVM bytecode, off-heap memory)
  → DAG of stages/tasks → executors
```

Practical payoffs of knowing this: `df.explain()` shows the plan; **PySpark DataFrame code runs at JVM speed** (Python only builds the plan — no row-by-row Python unless you use Python UDFs); and SQL vs DataFrame API produce **identical plans** — use whichever reads better.

## Structured Streaming in one screen

The same DataFrame API over an unbounded table:

```python
stream = (spark.readStream.format("kafka")
          .option("subscribe", "orders").load())
agg = stream.groupBy(window("timestamp", "5 minutes"), "region").count()
(agg.writeStream.format("delta")
    .option("checkpointLocation", ".../chk")   # exactly-once bookkeeping
    .outputMode("append").start())
```

Micro-batches by default (~100ms+ latency), **checkpointing** for failure recovery, **watermarks** to bound late-data state. One mental model, batch and streaming — the reason Lambda architecture died ([evolution timeline](../00_Fundamentals/06_Big_Data_Evolution_Timeline.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Version awareness (what changed and why it matters)

- **Spark 2.x** → SparkSession unified entry point; Structured Streaming GA.
- **Spark 3.0–3.2** → **Adaptive Query Execution (AQE)**: re-optimizes mid-job using real runtime statistics — auto-coalesces shuffle partitions, switches to broadcast joins, splits skewed partitions. Also dynamic partition pruning, pandas API on Spark (3.2).
- **Spark 3.4–4.x** → **Spark Connect**: thin-client protocol decoupling your Python process from the driver (the basis of Databricks serverless notebooks); ANSI SQL mode by default (4.0) — silent `null`-on-overflow becomes an error, a real migration item.
- On Databricks you pick a **runtime** (e.g. DBR 15.x = Spark 3.5 + Photon + patches) rather than raw Spark versions.

## When Spark is the wrong tool

| Situation | Better tool |
|---|---|
| Data fits on one machine (< ~100 GB) | DuckDB / Polars / pandas — faster *and* ~free |
| Sub-second query latency for apps | A database/warehouse endpoint, not a Spark job |
| Millisecond event-at-a-time streaming | Flink (true per-event processing) |
| Simple EL copy without transforms | [ADF](../05_ETL_ELT/02_Azure_Data_Factory.md) copy activity |

Cluster startup alone (minutes) can exceed the total runtime of a DuckDB solution. Senior engineers are distinguished less by Spark tricks than by **not reaching for Spark reflexively**.

## Reading `df.explain()` like a pro

The four things to scan for in a physical plan:

1. `PushedFilters: [...]` on the scan — did your predicate reach the file reader?
2. `Exchange` — each one is a shuffle; count them, question them.
3. `BroadcastHashJoin` vs `SortMergeJoin` — is the small table actually being broadcast?
4. `WholeStageCodegen` markers — Python UDFs break these fused pipelines (rows must round-trip to a Python worker — 10–100× slower). Prefer built-ins; if unavoidable, use **pandas UDFs** (Arrow-vectorized) over row UDFs.

## Field-tested gotchas

- `.collect()` on big data = driver OOM. Use `.limit()`, write to a table, or aggregate first.
- `df.count()` "just to check" triggers a full job — in production code, count once and reuse, or rely on written-output metrics.
- **Schema inference on JSON/CSV reads the data twice** and guesses badly at scale — always pass an explicit schema in production ([CSV](../02_File_formats/01_CSV.md), [JSON](../02_File_formats/02_JSON.md)).
- Notebook state lies: a re-run cell may reference a stale cached DataFrame. Restarting a cluster "fixing" the bug usually means hidden state, not magic.

## Interview-grade Q&A

- *RDD vs DataFrame?* RDD = untyped distributed objects, no optimizer; DataFrame = columnar, schema-aware, Catalyst-optimized. DataFrames win unless you need arbitrary object manipulation.
- *Is PySpark slower than Scala Spark?* Not for DataFrame/SQL work — both emit the same JVM plan. Only Python UDFs pay a Python tax.
- *How does Spark recover lost data without replication?* Lineage: recompute lost partitions from the recorded transformation graph.
- *What does AQE do?* Uses runtime stats between stages to fix the three classic pains automatically: too many shuffle partitions, missed broadcast joins, skew.

---

## Further Learning — Docs & Videos

**Documentation**
- Apache Spark official site: https://spark.apache.org/
- Spark overview: https://spark.apache.org/docs/latest/
- What is Apache Spark? (Databricks): https://www.databricks.com/glossary/what-is-apache-spark

**Videos**
- Apache Spark explained for beginners: https://www.youtube.com/results?search_query=what+is+apache+spark+explained
- Spark full course: https://www.youtube.com/results?search_query=apache+spark+full+course
