# 06_PySpark — Interview Questions & Answers

## How to use this file

PySpark/Spark is the single most heavily interview-tested topic for Data Engineer roles after SQL — expect deep, code-heavy questions here. This file mixes THEORY (concepts, internals, trade-offs) with heavy PRACTICAL/CODING questions (write this transformation, find the bug, predict the output, optimize this join, read this plan) — every practical answer includes real PySpark code. Every question states what it's testing; every answer explains why it's correct.

- **[Frequently Asked]** — the true PySpark interview classics: what is Spark, lazy evaluation, transformation vs action, RDD vs DataFrame, shuffles, broadcast joins, window functions, Delta MERGE, checkpointing, UDF costs.
- **[Senior/Experienced]** — Pro-level material: Catalyst/Tungsten internals, AQE, executor memory model, skew/salting, the Delta transaction log, exactly-once semantics, RDD lineage, custom partitioners.

---

## Table of Contents

- **Group A: Spark Fundamentals & Architecture** — [What is Spark](#a1-what-is-apache-spark) · [Architecture](#a2-spark-architecture) · [Processing](#a3-spark-processing) · [Why Spark/Databricks](#a4-why-spark-why-databricks) · [Getting Started](#a5-getting-started--sparksession)
- **Group B: DataFrames, Schemas & I/O** — [DataFrame Basics](#b1-dataframe-basics) · [Schemas & Types](#b2-schemas--data-types) · [Reading & Writing](#b3-reading--writing-data) · [Column Functions](#b4-column-operations--functions)
- **Group C: Aggregations, Joins & Windows** — [Aggregations](#c1-aggregations--grouping) · [Joins](#c2-joins) · [Window Functions](#c3-window-functions)
- **Group D: Complex Types, UDFs & Spark SQL** — [Complex Types & JSON](#d1-complex-types--json) · [UDFs & Pandas](#d2-udfs--pandas-integration) · [Spark SQL & Views](#d3-spark-sql--views)
- **Group E: Delta Lake** — [Delta Lake with PySpark](#e1-delta-lake-with-pyspark)
- **Group F: Structured Streaming** — [Structured Streaming](#f1-structured-streaming)
- **Group G: Performance Tuning & Production** — [Performance & Best Practices](#g1-performance--best-practices)
- **Group H: RDDs** — [RDDs: The Foundation](#h1-rdds-the-foundation)
- [Rapid-Fire Round](#rapid-fire-round)

---

# Group A: Spark Fundamentals & Architecture

## A1. What is Apache Spark?

*(full notes: [What_Is_Apache_Spark.md](What_Is_Apache_Spark.md))*

#### Q1. What is Apache Spark, and why is it faster than Hadoop MapReduce? **[Frequently Asked]**
*Why interviewers ask this:* The single most common opening Spark question — checks baseline understanding before anything deeper.
**Answer:** Spark is an open-source, distributed, **in-memory** data processing engine — it computes but doesn't store data itself, reading from and writing to external storage (a data lake, a database, Kafka). It's faster than MapReduce because MapReduce writes intermediate results to disk after every map/reduce stage, while Spark keeps intermediate data **in RAM** between operations, avoiding repeated disk round-trips — typically 10–100× faster, with the largest gains on multi-stage and iterative (e.g. ML) workloads. This is correct because it names the actual mechanical difference (disk round-trips vs. in-memory) rather than a vague "Spark is more modern," which is the level of precision this question expects.

#### Q2. What is lazy evaluation, and why does Spark use it? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental Spark concepts — almost guaranteed in some form.
**Answer:** Spark records every transformation (`filter`, `select`, `groupBy`) as a plan without executing it, and only runs the whole plan when an **action** (`show`, `count`, `collect`, `write`) is called. This lets Spark's Catalyst optimizer see the *entire* pipeline before running anything — enabling predicate pushdown (pushing filters into the file read), column pruning, and operator reordering, all of which would be impossible if each line executed immediately in isolation. This is correct because it explains *why* laziness exists (whole-plan optimization), not just that it happens — the "why" is what interviewers are actually probing for.

#### Q3. What's the difference between a transformation and an action? Give two examples of each. **[Frequently Asked]**
*Why interviewers ask this:* Directly tests understanding of lazy evaluation in practice.
**Answer:** A **transformation** describes a change and returns a new DataFrame without running anything (`filter`, `withColumn`, `groupBy`, `join`). An **action** triggers the actual execution of the recorded plan and returns a result to the driver or writes output (`count()`, `show()`, `collect()`, `.write`). This is correct because `df.filter(...)` alone does nothing observable — only when `.show()` or `.write` is called does Spark plan and run the whole chain, which is the concrete, demonstrable proof of the transformation/action split.

#### Q4. What is Catalyst, and what does it actually do to your code? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real internals knowledge, common in senior rounds.
**Answer:** Catalyst is Spark's query optimizer. Your DataFrame/SQL code passes through: an unresolved logical plan (parsed) → analyzed plan (columns/types resolved against the catalog) → optimized logical plan (Catalyst applies predicate pushdown, column pruning, constant folding, join reordering) → physical plan (cost-based choice, e.g. which join strategy) → whole-stage code generation via Tungsten, which fuses operators into efficient JVM bytecode. This is correct because it names the actual pipeline stages your code travels through, which is also why `df.explain()` is useful — it shows you exactly where in this pipeline the final plan landed.

#### Q5. Is PySpark slower than Scala Spark? **[Frequently Asked]**
*Why interviewers ask this:* A very commonly asked comparison, and a common source of misconceptions.
**Answer:** Not for DataFrame/SQL API work — Python only builds the query plan; the actual execution runs inside the JVM via the identical Catalyst-optimized, Tungsten-generated bytecode regardless of which language wrote the query. The one place a real "Python tax" appears is **row-by-row Python UDFs**, where data must round-trip out of the JVM to a separate Python worker process for every row — that's the only scenario where PySpark genuinely underperforms Scala. This is correct because it distinguishes the DataFrame API (equally fast) from UDFs (genuinely slower), a nuance that shows real understanding rather than a blanket true/false answer.

#### Q6. How does Spark recover a lost partition without replicating data, unlike HDFS? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of Spark's fault tolerance mechanism, a genuinely deep concept.
**Answer:** Every DataFrame/RDD remembers its **lineage** — the exact sequence of transformations that produced it. If an executor holding a partition dies, Spark doesn't need a backup copy; it simply **recomputes just that lost partition** by replaying its slice of the lineage graph from the original source. This is correct because it identifies the actual mechanism (recomputation from a recorded recipe, not data duplication) — which is also why very long transformation chains eventually need `checkpoint()` to truncate the lineage, since recomputation cost grows with chain length.

#### Q7. What does Adaptive Query Execution (AQE) do, and why was it added? **[Senior/Experienced]**
*Why interviewers ask this:* A modern, frequently asked question testing currency with Spark 3.x+ features.
**Answer:** AQE re-optimizes a query plan **mid-execution** using real runtime statistics gathered between stages, fixing three classic pain points automatically: it **coalesces shuffle partitions** (merging many tiny post-shuffle partitions instead of leaving hundreds of near-empty ones from the old fixed `spark.sql.shuffle.partitions=200` default), it **converts a join to broadcast** when a side turns out small after filtering (even if the optimizer's static estimate missed it), and it **splits skewed partitions** automatically. This is correct because it names all three concrete fixes AQE provides, not just "it makes queries faster" — each fix solves a specific, previously-manual tuning problem.

---

## A2. Spark Architecture

*(full notes: [Spark_Architecture.md](Spark_Architecture.md))*

#### Q8. Explain the Spark architecture: driver, executors, and cluster manager. **[Frequently Asked]**
*Why interviewers ask this:* Near-guaranteed — the foundational architecture question for any Spark role.
**Answer:** The **driver** runs your code, creates the SparkSession, converts your DataFrame operations into a logical plan and then a DAG of stages and tasks, and schedules those tasks onto executors — but does *no heavy data processing itself*. **Executors** are JVM processes on worker nodes that actually run the tasks (one task = one partition on one core) and hold cached data. The **cluster manager** (YARN, Kubernetes, Standalone, or Databricks) decides which physical machines provide the executors — it's resource arbitration only, not task scheduling, which stays with the driver. This is correct because it correctly separates the three roles by responsibility (plan/coordinate, execute, provide machines), which is exactly the distinction interviewers check for — candidates commonly conflate the cluster manager's role with the driver's.

#### Q9. What is a job, a stage, and a task in Spark? **[Frequently Asked]**
*Why interviewers ask this:* Core vocabulary tested constantly, especially before diagnosing performance issues.
**Answer:** A **job** is created by one action. A **stage** is a group of tasks that can run without moving data between nodes — a **shuffle** (required by `groupBy`, `join`, `orderBy`) ends one stage and starts a new one. A **task** is the smallest unit of work: processing one partition on one core. So `df.filter(...).groupBy("region").sum("amount").write...` produces one job with two stages (split at the `groupBy` shuffle), with as many tasks per stage as there are partitions. This is correct because it gives the exact worked breakdown of a concrete pipeline, which demonstrates the concept rather than just defining the three terms in isolation.

#### Q10. An executor keeps running out of memory (OOM). What are your first three suspects? **[Senior/Experienced]**
*Why interviewers ask this:* A very realistic production-debugging scenario, testing real operational experience.
**Answer:** In order: (1) a **skewed partition** — one task processing far more data than the rest because a key is heavily concentrated; (2) an **under-partitioned shuffle** — too few output partitions means each task's slice is oversized; (3) an **oversized broadcast join** — force-broadcasting a "small" table that turns out large enough to OOM every executor simultaneously (the failure pattern looks like a cluster-wide crash, not one bad task). Increasing executor RAM is only the *fourth* resort, after ruling these out. This is correct because it gives a diagnostic order rather than jumping straight to "add more memory," which is exactly the judgment a real production incident requires.

#### Q11. Client mode vs. cluster mode — what's the difference, and why does it matter for production jobs? **[Senior/Experienced]**
*Why interviewers ask this:* Tests operational deployment knowledge beyond the DataFrame API itself.
**Answer:** In **client mode**, the driver runs in *your* own process (a notebook, laptop, or edge node) — this is how interactive Databricks notebooks attach. In **cluster mode**, the driver runs *inside* the cluster, managed by the cluster manager, which can restart it if it fails. For production jobs, cluster mode is preferred because the job survives your laptop closing or a flaky VPN connection, and logs live centrally on the cluster rather than on a machine that might disappear. This is correct because it identifies the operational consequence (fragility of client mode for unattended jobs) rather than just the definitional difference.

#### Q12. Why are Databricks "job clusters" preferred over "all-purpose clusters" for production pipelines? **[Senior/Experienced]**
*Why interviewers ask this:* A practical Databricks-operations question testing cost and reliability awareness.
**Answer:** A job cluster is spun up fresh for one run and terminates immediately after, giving each run a clean, known state, right-sized resources for that specific workload, and automatic termination — no idle burn. All-purpose clusters are shared, long-lived, and meant for interactive human use; running production jobs on them risks shared-state bugs from other users' notebooks and, if left running, becomes the classic idle-cluster cost surprise. This is correct because it identifies both the reliability argument (clean state per run) and the cost argument (auto-terminate vs. idle burn) that together justify the standard practice.

---

## A3. Spark Processing

*(full notes: [Spark_Processing.md](Spark_Processing.md))*

#### Q13. What is a shuffle, and why is it the most expensive operation in Spark? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental performance concepts — a near-guaranteed question.
**Answer:** A shuffle is the redistribution of data across the cluster by key, required whenever an operation needs data from *many* input partitions to produce one output partition — `groupBy`, `join`, `orderBy`, `distinct`, `repartition`. It's expensive because it means writing data to disk, transferring it over the network, and regrouping it by key, unlike a **narrow** transformation (`filter`, `select`, `withColumn`) where each output partition depends on only one input partition and no data ever moves between executors. This is correct because it distinguishes narrow from wide transformations by their actual data-movement behavior, which is the mechanism that makes shuffles costly — "minimizing shuffles" is genuinely the majority of real Spark performance tuning.

#### Q14. What's the difference between `repartition()` and `coalesce()`? **[Frequently Asked]**
*Why interviewers ask this:* A very common practical PySpark question with a definite, testable right answer.
**Answer:** `repartition(n)` performs a **full shuffle** to redistribute data evenly into exactly `n` partitions — can increase or decrease the count. `coalesce(n)` only **merges existing partitions down**, without a shuffle, which makes it cheap but only works to *reduce* partition count, and can leave data unevenly distributed since it just combines adjacent partitions rather than truly rebalancing. This is correct because it identifies both the mechanical difference (shuffle vs. no shuffle) and the practical constraint (coalesce can only go down), which is what determines which one to reach for in a given situation.

#### Q15. Write PySpark code demonstrating that a chain of transformations doesn't execute until an action, and explain what's actually happening.
*Why interviewers ask this:* A hands-on demonstration of lazy evaluation — tests whether the concept is truly internalized, not just recited.
**Answer:**
```python
df2 = df.filter(df.amount > 0)        # nothing runs — just recorded
df3 = df2.groupBy("region").count()   # still nothing runs
df3.show()                            # NOW the entire plan executes: 1 job, 2 stages
```
Nothing physically happens at the first two lines — Spark is only building an internal logical plan. When `.show()` (an action) is finally called, Catalyst optimizes the *whole* recorded chain at once (potentially pushing the filter into the source read, pruning unused columns) and only then submits a job with stages split at the shuffle boundary caused by `groupBy`. This is correct because it demonstrates, with actual code and an execution trace, exactly *when* and *why* nothing happens versus when everything happens — proof of understanding rather than a repeated definition.

#### Q16. Write PySpark code to broadcast a small dimension table in a join, and explain when Spark does this automatically. **[Frequently Asked]**
*Why interviewers ask this:* One of the most common practical PySpark performance questions.
**Answer:**
```python
from pyspark.sql.functions import broadcast
result = big_fact.join(broadcast(small_dim), "dept_code")
```
This forces a **broadcast hash join**: the small table is copied in full to every executor, so the large table never needs to be shuffled at all — only the small side moves, and cheaply. Spark does this automatically when a table's estimated size is under `spark.sql.autoBroadcastJoinThreshold` (10 MB by default), or when AQE detects mid-query that a filtered side has become small enough, even if the static estimate missed it. This is correct because it gives both the manual code and the automatic threshold-based trigger — a fact-to-dimension join that unexpectedly shuffles a 2 TB table because a 50 MB dimension wasn't detected as broadcastable is one of the most common avoidable Spark performance disasters, and this is the fix.

#### Q17. Your job is running slowly. Walk me through your diagnosis process, in order. **[Senior/Experienced]**
*Why interviewers ask this:* One of the highest-value senior Spark questions — tests real, structured troubleshooting, not guessing.
**Answer:** (1) **Spark UI** — find the dominant stage, check for skew (max task time far greater than median), spill, and shuffle read/write sizes; (2) `df.explain()` — look for unexpected shuffles (`Exchange` nodes), the wrong join strategy (`SortMergeJoin` where `BroadcastHashJoin` was expected), and filters that aren't being pushed down (`PushedFilters: []`); (3) **fix the plan** — broadcast hints, pre-aggregation before joins, salting for skew, earlier filtering; (4) only *then* touch resources — more partitions, more memory, a bigger cluster. This is correct because it states the actual professional order (measure → diagnose the plan → fix the plan → fix resources last), explicitly rejecting the common junior instinct of reaching for a bigger cluster before any diagnosis — "config changes without a plan diagnosis are astrology."

---

## A4. Why Spark? Why Databricks?

*(full notes: [Why_Spark_Why_Databricks.md](Why_Spark_Why_Databricks.md))*

#### Q18. Spark is free and open-source — what exactly are you paying for with Databricks? **[Frequently Asked]**
*Why interviewers ask this:* A very common question testing whether the candidate understands the platform vs. engine distinction.
**Answer:** Four things raw open-source Spark doesn't provide: **operations** (managed clusters — provisioning, patching, autoscaling, auto-terminate, all handled for you instead of requiring a platform team); **performance** (Photon, Databricks' optimized execution engine, plus a tuned Spark runtime); **collaboration** (notebooks, built-in scheduling, Workflows); and **governance** (Unity Catalog — central permissions, lineage, data discovery). This is correct because it names the four concrete value categories rather than a vague "convenience" — the interview one-liner is "we pay to delete an infrastructure team's worth of undifferentiated work."

#### Q19. What does Delta Lake add on top of plain Parquet files that makes it "the load-bearing feature" of the lakehouse? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common lakehouse questions, testing the Parquet-vs-Delta distinction clearly.
**Answer:** Plain Parquet-on-a-lake fails in specific ways: a job dying mid-write leaves readers seeing a half-written folder; two concurrent writers can corrupt data; there's no schema enforcement or evolution tracking; a bad deploy corrupts data with no way back; upserts require rewriting everything. Delta's `_delta_log` transaction log fixes each: **atomic commits** (a write either fully appears in the log or never happened), **optimistic concurrency** (a conflicting concurrent commit fails cleanly and retries), **schema enforcement/evolution**, **time travel** (`VERSION AS OF` / `RESTORE`), and **MERGE INTO** for real upserts. This is correct because it maps each specific lake pain to the specific Delta feature that solves it, rather than a generic "Delta adds ACID" — which is exactly the level of detail a senior interviewer wants.

#### Q20. When is Databricks the wrong choice for a workload? **[Senior/Experienced]**
*Why interviewers ask this:* A judgment question testing whether the candidate defaults reflexively to Spark/Databricks or actually matches tools to problems.
**Answer:** Data under roughly 100 GB and batch-shaped — DuckDB, Polars, or even plain Azure SQL will beat a Spark cluster on both speed and cost, since cluster startup time alone can exceed the total runtime of a single-node solution; a pure extract-and-load copy with no real transformation, where a simple copy tool (like ADF's Copy Activity) suffices; a single daily dashboard refresh, where a serverless SQL query beats spinning up a cluster; and teams with no Python/Spark skills and no runway to build them, since an unoperated tool is a liability. This is correct because it names concrete, checkable disqualifying conditions rather than treating Databricks as universally correct — this is precisely the kind of "know when NOT to use the big tool" reasoning senior interviews are designed to surface.

---

## A5. Getting Started & SparkSession

*(full notes: [01_Getting_Started_SparkSession.md](01_Getting_Started_SparkSession.md))*

#### Q21. What is a SparkSession, and what does it provide? **[Frequently Asked]**
*Why interviewers ask this:* A basic but essential entry-point question.
**Answer:** The `SparkSession` is your single handle to the entire Spark engine — it holds the cluster connection, configuration, and the catalog of tables/views. Every operation starts from it: `spark.read`, `spark.sql`, `spark.createDataFrame`. There is one session per application; calling `SparkSession.builder.getOrCreate()` a second time returns the existing session rather than creating a new cluster connection. This is correct because it identifies the session as the *single unifying entry point* (replacing the older separate SparkContext/SQLContext split), which is the practical fact that matters day to day.

#### Q22. Why should every production PySpark job explicitly set the session timezone? **[Senior/Experienced]**
*Why interviewers ask this:* A specific, high-value gotcha testing real production experience with timestamp bugs.
**Answer:**
```python
spark.conf.set("spark.sql.session.timeZone", "UTC")
```
Timestamp values are stored as UTC instants internally but *rendered* in the session's configured timezone — if two jobs (say, an extract job and a load job) run with different inherited cluster timezones, the same underlying data displays shifted by hours, and "daily" aggregations can split a single business day across two partitions. Pinning the timezone explicitly, and standardizing on UTC storage everywhere, removes this entire class of subtle, hard-to-notice bugs. This is correct because it names the exact mechanism (storage vs. rendering timezone mismatch) rather than "timezones are tricky," and gives the concrete one-line fix.

---

# Group B: DataFrames, Schemas & I/O

## B1. DataFrame Basics

*(full notes: [02_DataFrame_Basics.md](02_DataFrame_Basics.md))*

#### Q23. What is a DataFrame in Spark, and how is it different from a pandas DataFrame? **[Frequently Asked]**
*Why interviewers ask this:* Very common for candidates coming from a pandas/data-science background — tests whether the distributed nature is understood.
**Answer:** A Spark DataFrame is a **distributed** table — named, typed columns split into partitions spread across many machines in a cluster, with **lazy** execution (a DataFrame is really a *plan*, not materialized data, until an action runs it). A pandas DataFrame lives entirely in one machine's RAM and executes every operation immediately. Both are immutable-looking in normal use, but Spark DataFrames are genuinely immutable at the API level — every transformation returns a new DataFrame, which is what allows Spark's optimizer to reason about and rewrite an entire chain. This is correct because it contrasts the two on the dimensions that actually matter for how you write code differently against each — distribution, laziness, and scale ceiling.

#### Q24. Why does calling `.collect()` on a large DataFrame crash the driver? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common practical PySpark mistakes, and a favorite "explain the bug" question.
**Answer:** `.collect()` pulls **every row** of the DataFrame — regardless of size — from all the executors back into the driver's memory as Python objects. The driver is a single JVM process and does no heavy data processing itself; forcing gigabytes or terabytes of distributed data into it exhausts its memory and crashes the application. The safe alternatives are `.take(n)` or `.limit(n).collect()` for a bounded preview, or aggregating/filtering down to something small before ever calling `.collect()`. This is correct because it identifies the exact mechanism (all-rows to a single-process driver) that causes the crash, and gives the concrete safe alternatives that avoid it.

#### Q25. Write a single PySpark chain that filters employees earning over 50000, adds a `monthly` salary column, and sorts by department then salary descending.
*Why interviewers ask this:* A basic hands-on chaining exercise testing fluency with the core DataFrame verbs.
**Answer:**
```python
result = (emp
    .filter(F.col("salary") > 50000)
    .withColumn("monthly", F.col("salary") / 12)
    .orderBy("dept", F.desc("salary")))
```
This is correct because each step is a transformation returning a new DataFrame (nothing executes until an action like `.show()` is eventually called), and Catalyst typically compiles this entire chain into a much smaller number of physical stages than the number of lines written — chaining doesn't mean multiple passes over the data.

#### Q26. Why is `count()` "just to check the row count" considered bad practice inside a production pipeline? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding that actions aren't free, a genuinely valuable production habit.
**Answer:** `count()` is an action — it triggers a full job over the entire DataFrame, not a metadata lookup (except specifically for Delta tables, where row counts can sometimes be served from committed metadata). Sprinkling `count()` calls through pipeline code as progress checks silently doubles or triples the actual work done, since each one re-triggers the upstream plan. The better pattern is computing a count once into a variable if genuinely needed, or relying on the write operation's own output metrics (e.g. Delta's `operationMetrics` from `DESCRIBE HISTORY`) instead. This is correct because it identifies that an action's cost is real and repeated, not just "counting is slow" — the fix (rely on write metrics, or count once) is what a reviewer actually wants to see in code.

---

## B2. Schemas & Data Types

*(full notes: [03_Schemas_and_Data_Types.md](03_Schemas_and_Data_Types.md))*

#### Q27. Why should production PySpark code always declare an explicit schema instead of using `inferSchema=True`? **[Frequently Asked]**
*Why interviewers ask this:* A very common practical question, testing production discipline over convenience.
**Answer:** Schema inference reads the file an extra time and *guesses* the type per file — a column that's numeric today can silently become a string tomorrow the moment one row contains something like `"N/A"`, and different files in the same folder can infer different schemas. Declaring the schema explicitly (via `StructType` or a DDL string) makes the shape of the data a contract you enforce, not a guess the engine makes fresh on every run. This is correct because it names the concrete failure mode (silent type drift across runs/files) rather than a vague "inference is slow," which is the level of specificity this question expects.

#### Q28. What does a failed `.cast()` produce in PySpark, and how do you catch it in production? **[Senior/Experienced]**
*Why interviewers ask this:* A specific, high-value gotcha — tests whether the candidate knows casts fail silently.
**Answer:** A failed cast produces **`null`**, not an error — `F.col("amount").cast("decimal(18,4)")` on a genuinely non-numeric string silently becomes `null` rather than raising an exception. To catch this in production:
```python
typed = df.withColumn("amount_d", F.col("amount").cast("decimal(18,4)"))
bad = typed.filter(F.col("amount").isNotNull() & F.col("amount_d").isNull())
# 'bad' rows had values that LOOKED numeric but weren't
```
This is correct because it identifies the silent-failure behavior (the actual gotcha) and gives the concrete instrumentation pattern (comparing pre/post-cast nullness) that surfaces the casualties instead of letting them vanish unnoticed — `try_cast` (Spark 3.4+) makes the same intent explicit, and under ANSI mode (Spark 4 default) a bad cast raises an error instead, so the right answer also depends on knowing which runtime behavior applies.

#### Q29. Does setting `nullable=False` on a `StructField` prevent nulls from being written to that column? **[Senior/Experienced]**
*Why interviewers ask this:* A commonly misunderstood detail, testing precise knowledge of schema enforcement layers.
**Answer:** No — `nullable=False` in a Spark schema is **metadata the optimizer may use**, not an enforced constraint; Spark will not reject a null value on read or write based on it alone. Real enforcement happens at the table layer — Delta Lake's `NOT NULL`/`CHECK` constraints, or explicit validation filters in the pipeline itself. This is correct because it corrects a common false assumption directly — a candidate designing a pipeline "protected" only by schema nullability has a gap that a null value will eventually expose in production.

---

## B3. Reading & Writing Data

*(full notes: [04_Reading_and_Writing_Data.md](04_Reading_and_Writing_Data.md))*

#### Q30. Write PySpark code to read a database table over JDBC in parallel, and explain why the naive version is slow. **[Frequently Asked]**
*Why interviewers ask this:* A very common practical question about a genuinely frequent real-world bottleneck.
**Answer:**
```python
jdbc_df = (spark.read.format("jdbc")
    .option("url", "jdbc:sqlserver://server.database.windows.net;database=sales")
    .option("dbtable", "orders")
    .option("user", user).option("password", pwd)
    .option("partitionColumn", "order_id")
    .option("lowerBound", 1).option("upperBound", 10_000_000)
    .option("numPartitions", 8)
    .load())
```
Without `partitionColumn`/`numPartitions`, a JDBC read is **single-threaded** — one task issues one query and pulls all the data through one connection, regardless of how many executors the cluster has. Setting a partition column and bounds lets Spark split the read into `numPartitions` parallel range-based queries. This is correct because it names the actual default behavior (single connection, single task) that makes naive JDBC reads slow, and shows the specific options that fix it — while also flagging that `numPartitions` should be bounded respectfully so as not to overwhelm the source database's connection pool.

#### Q31. Why is a plain `overwrite` to a Parquet folder path (not a Delta table) dangerous for concurrent readers? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of atomicity at the storage layer, and why table formats exist.
**Answer:** A plain `overwrite` to a raw Parquet path is **not atomic** — it deletes old files and writes new ones as separate operations, so a reader that queries mid-write can see a half-deleted, half-written folder: some old files gone, some new files not yet arrived. Delta Lake solves this by making writes transactional via its log — a write either fully appears as a new committed version or never happened at all, so readers never see an inconsistent intermediate state. This is correct because it identifies the exact failure window (concurrent read during a non-atomic multi-file operation) that a table format is specifically designed to close.

#### Q32. Write PySpark code to write a DataFrame as Delta, partitioned by year and month, with a controlled number of output files per partition.
*Why interviewers ask this:* A very common practical write-path question testing partitioning and file-count control together.
**Answer:**
```python
(df.repartition(8, "year", "month")   # 8 files per partition value, evenly shuffled
   .write.format("delta")
   .partitionBy("year", "month")
   .mode("append")
   .save("abfss://silver@lake.dfs.core.windows.net/sales/"))
```
This is correct because `partitionBy` creates the folder-per-value layout (`year=2026/month=07/...`) that lets readers filtering on those columns skip entire folders, while `repartition` before the write controls how many files land in each partition — targeting roughly 100 MB–1 GB per file avoids both the small-files problem (too many tiny files) and the single-task bottleneck of `coalesce(1)`.

---

## B4. Column Operations & Functions

*(full notes: [05_Column_Operations_and_Functions.md](05_Column_Operations_and_Functions.md))*

#### Q33. Why does `df.filter(F.col("dept") != "IT")` silently drop rows where `dept` is null, and how do you fix it? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common PySpark null-handling gotchas, directly analogous to the SQL `NULL` trap.
**Answer:** Comparisons with null in PySpark follow the same three-valued logic as SQL — `null != "IT"` evaluates to *unknown*, not true, so rows with a null department are excluded from both `= "IT"` and `!= "IT"` filters. The fix is to explicitly include the null case if it should be kept: `df.filter((F.col("dept") != "IT") | F.col("dept").isNull())`. This is correct because it names the underlying logic (three-valued, not two-valued) rather than treating it as an arbitrary quirk, and gives the precise fix for "not X, including unknown."

#### Q34. Write PySpark code to bucket employees into Senior/Mid/Entry salary bands using conditional logic.
*Why interviewers ask this:* Tests fluency with `when`/`otherwise`, PySpark's equivalent of SQL's `CASE`.
**Answer:**
```python
df.withColumn("band",
    F.when(F.col("salary") >= 65000, "Senior")
     .when(F.col("salary") >= 55000, "Mid")
     .otherwise("Entry"))
```
This is correct because `when`/`otherwise` conditions evaluate top-down and the first match wins, exactly mirroring SQL's `CASE WHEN` — and it's worth noting that a missing `.otherwise()` produces `null` for any row that matches none of the conditions, which is sometimes intentional and sometimes a forgotten edge case.

#### Q35. Why should a candidate almost never write a custom Python function to clean a string column, and what should they use instead? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether the candidate reaches for the built-in function library before jumping to custom code — a genuinely important habit.
**Answer:** `pyspark.sql.functions` (as `F`) is a large standard library of functions that run at JVM speed inside the engine's optimized execution — string cleanup like trimming, case normalization, regex extraction, and padding are all covered (`F.trim`, `F.lower`, `F.regexp_replace`, `F.regexp_extract`, `F.lpad`). A chained `F.when(...)`/built-in expression pipeline is typically 10–100× faster than an equivalent row-by-row Python UDF, because built-ins participate in Catalyst's optimization and whole-stage code generation while a UDF is an opaque black box the optimizer can't see into. This is correct because it names the actual performance gap and the mechanism behind it (optimizer visibility), which is the deeper reasoning behind the blanket advice "check `F.*` before writing a UDF."

---

# Group C: Aggregations, Joins & Window Functions

## C1. Aggregations & Grouping

*(full notes: [06_Aggregations_and_Grouping.md](06_Aggregations_and_Grouping.md))*

#### Q36. Write PySpark code to compute headcount, average salary, and total payroll per department. **[Frequently Asked]**
*Why interviewers ask this:* A baseline aggregation question testing `groupBy`/`agg` fluency.
**Answer:**
```python
(emp.groupBy("dept")
    .agg(F.count("*").alias("headcount"),
         F.avg("salary").alias("avg_salary"),
         F.sum("salary").alias("payroll"))
    .show())
```
This is correct because `.agg()` with explicit aliases is the professional form — it computes multiple aggregates in a single pass with clear output column names, versus chaining several separate shortcut calls (`.count()`, `.avg(...)`) which is less flexible and less readable for more than one metric.

#### Q37. Why does aggregating 1 TB of data down to 50 groups ship only a small amount of data over the network? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real understanding of the shuffle mechanics behind `groupBy`, not just the API surface.
**Answer:** `groupBy().agg()` runs in two phases: each partition first **pre-aggregates locally** (map-side combining) before anything is shuffled, and only the compact partial results move across the network to be combined into the final answer per key. This is why `collect_list` behaves completely differently from `sum` on the same grouping — it *can't* pre-shrink, since it must retain every individual value, so it ships everything and is a much heavier operation on large groups. This is correct because it identifies the two-phase partial-aggregation mechanism as the actual reason for the low network cost, and correctly flags the one aggregate function (`collect_list`) where that optimization doesn't apply.

#### Q38. Why is `groupBy("customer_id")` over 500 million distinct customers potentially a much bigger problem than `groupBy("region")` over 12 regions, even on the same table? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of cardinality as the real cost driver in aggregation, not table size.
**Answer:** Hash aggregation builds an in-memory hash table of the distinct groups seen so far — the cost driver is the **number of distinct groups**, not the total row count. `groupBy("region")` with 12 groups fits trivially in memory at any table size; `groupBy("customer_id")` with 500 million groups can force the aggregation to **spill to disk**, dramatically slowing the job. This is correct because it isolates the actual scaling variable (group cardinality) rather than "big data is slow," which is the distinction that should drive how metrics tables and dashboards are designed.

---

## C2. Joins

*(full notes: [07_Joins.md](07_Joins.md))*

#### Q39. What join types does PySpark support, and what does `left_semi` return that `inner` doesn't? **[Frequently Asked]**
*Why interviewers ask this:* Tests knowledge of the less commonly known but genuinely useful semi/anti join types.
**Answer:** `inner`, `left`/`right`, `full` (outer), `left_semi`, `left_anti`, and `cross`. `left_semi` returns only left-table rows that **have** a match — like SQL's `EXISTS` — but carries *no columns from the right table* and, crucially, can never duplicate a left row even if multiple right rows match (no fan-out risk). `left_anti` is the mirror — left rows with **no** match, like `NOT EXISTS`. This is correct because it identifies semi/anti joins as structurally safer than `inner`-then-`distinct()` for existence checks (no possibility of row duplication), which is why they're described as "underused workhorses" over the more error-prone alternatives.

#### Q40. Write PySpark code to join employees to their department names, and explain the "ambiguous column" error that occurs with a naive expression-form join.
*Why interviewers ask this:* One of the most common practical PySpark bugs — a guaranteed question in a hands-on round.
**Answer:**
```python
# BUG: expression-form join keeps BOTH id columns and both name columns if both tables have 'name'
j = orders.join(cust, orders["cust_id"] == cust["id"], "inner")
j.select("name")   # AnalysisException: Reference 'name' is ambiguous

# FIX 1 — same-key syntax coalesces automatically:
orders.join(cust.withColumnRenamed("id", "cust_id"), "cust_id")

# FIX 2 — rename before joining:
cust2 = cust.select(F.col("id").alias("cust_id"), F.col("name").alias("cust_name"))
orders.join(cust2, "cust_id")
```
This is correct because it identifies that expression-form joins (`df1["a"] == df2["b"]`) keep both sides' columns unresolved by name, causing ambiguity whenever the same column name exists on both sides — while the same-key string/list syntax (`on="cust_id"`) automatically coalesces the key into one column. Renaming columns *before* joining is the cleanest habit that prevents the problem entirely.

#### Q41. Write the two-line "insurance" check that catches a join fan-out bug during development. **[Senior/Experienced]**
*Why interviewers ask this:* Tests a genuinely valuable, easy-to-apply production habit around join grain.
**Answer:**
```python
before = orders.count()
after  = orders.join(dim, "key", "left").count()
assert before == after, "join fanned out — dim has duplicate keys!"
```
A left join should never grow the left side's row count — if it does, the right-side (`dim`) table wasn't unique on the join key, and every matching left row got duplicated once per extra match (fan-out). This is correct because it's a concrete, cheap, automatable check that catches the single most common class of join bugs (grain mismatch) before it silently inflates downstream sums — exactly the kind of habit interviewers want to hear a candidate already has.

#### Q42. Your fact-to-dimension join takes 40 minutes; the dimension is 200 MB after filtering to current rows. What's your first fix, and how do you verify it worked? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic scenario testing the broadcast-join diagnosis and verification loop.
**Answer:** Force a broadcast of the dimension side, since 200 MB is well within reasonable broadcast range even though it exceeds the 10 MB default threshold:
```python
result = big_fact.join(F.broadcast(small_dim), "dept_code")
```
Verify with `result.explain()` — the plan should show `BroadcastHashJoin` instead of `SortMergeJoin`. If it still shows `SortMergeJoin` against a small table, the query is likely mis-estimating the dimension's size (e.g. filtering happens *after* the join in the plan) — check `explain()`'s size estimates and consider filtering the dimension into its own DataFrame explicitly before joining. This is correct because it gives the concrete fix, the concrete verification step (reading `explain()` for the specific operator name), and the fallback diagnosis if the fix doesn't take effect — a complete troubleshooting loop, not just a guess.

---

## C3. Window Functions

*(full notes: [08_Window_Functions.md](08_Window_Functions.md))*

#### Q43. Write PySpark code to find the top 3 highest-paid employees in each department. **[Frequently Asked]**
*Why interviewers ask this:* The canonical top-N-per-group question — extremely common in practical PySpark interviews.
**Answer:**
```python
from pyspark.sql.window import Window

w = Window.partitionBy("dept").orderBy(F.desc("salary"))
top3 = (emp.withColumn("rn", F.row_number().over(w))
           .filter(F.col("rn") <= 3)
           .drop("rn"))
```
This is correct because `row_number()` with `partitionBy("dept")` restarts the ranking independently for every department, and filtering `rn <= 3` in a subsequent step (required, since `WHERE`/`filter` can't see window results in the same expression) keeps exactly the top 3 per group — the standard window-function replacement for older, slower correlated-subquery approaches.

#### Q44. Write PySpark code to deduplicate a CDC feed to the latest version of each record, deterministically. **[Frequently Asked]**
*Why interviewers ask this:* One of the most common real production patterns — nearly guaranteed in a practical round.
**Answer:**
```python
w = Window.partitionBy("business_key").orderBy(F.desc("updated_at"), F.desc("_ingest_file"))
latest = (raw.withColumn("rn", F.row_number().over(w))
             .filter("rn = 1").drop("rn"))
```
This is correct because it includes a **tiebreaker column** (`_ingest_file`) after the primary ordering column — without one, two records with the exact same `updated_at` timestamp would be picked arbitrarily and non-reproducibly between runs, which is exactly the kind of subtle nondeterminism that breaks trust in a "latest per key" pipeline.

#### Q45. Why is `Window.orderBy("ts")` without a `partitionBy` dangerous on a billion-row table? **[Senior/Experienced]**
*Why interviewers ask this:* A high-value gotcha testing understanding of how window functions actually execute.
**Answer:** A window with no `partitionBy` pulls the **entire dataset into a single partition** to compute a truly global ordering — every row's window computation depends on a global position, so Spark can't split the work across executors. This silently becomes a single-task bottleneck on a job that looked parallel everywhere else. If a genuinely global order is required, `monotonically_increasing_id()` gives unique-but-not-strictly-sequential IDs without forcing this collapse — otherwise, the requirement itself should be questioned. This is correct because it names the exact mechanism (forced single-partition computation) rather than "it's slow," and the fact that it's *silent* — no error, just one enormous straggler task — is what makes it a genuinely dangerous gotcha in practice.

#### Q46. Explain and implement sessionization: grouping a user's events into sessions where a gap of more than 30 minutes starts a new session. **[Senior/Experienced]**
*Why interviewers ask this:* A classic advanced window-function interview question (the "gaps and islands" problem), used to test genuine mastery.
**Answer:**
```python
w = Window.partitionBy("user").orderBy("ts")
sessions = (events
    .withColumn("prev_ts", F.lag("ts").over(w))
    .withColumn("new_sess",
        (F.col("ts").cast("long") - F.col("prev_ts").cast("long") > 1800).cast("int"))
    .fillna({"new_sess": 1})
    .withColumn("session_id", F.sum("new_sess").over(w)))
```
`lag` looks back one row within each user's event stream to compute the time gap to the previous event; a gap over 1800 seconds (30 minutes) flags a session boundary; and a **running sum of those boundary flags** (another window function, over the same ordering) produces a monotonically increasing session number per user. This is correct because it combines two distinct window-function patterns (offset lookback via `lag`, and a running-total aggregate) to solve a problem that plain `groupBy` cannot express at all — the boundary condition itself depends on row order, which `groupBy` has no concept of.

---

# Group D: Complex Types, UDFs & Spark SQL

## D1. Complex Types & JSON

*(full notes: [09_Complex_Types_and_JSON.md](09_Complex_Types_and_JSON.md))*

#### Q47. Write PySpark code to flatten a nested order document (with a `customer.city` struct field and an `items` array) into one row per line item. **[Frequently Asked]**
*Why interviewers ask this:* A very common practical question testing struct navigation and `explode` together.
**Answer:**
```python
lines = (order
    .select("order_id", F.col("customer.city").alias("city"),
            F.explode("items").alias("item"))
    .select("order_id", "city", "item.sku", "item.qty", "item.price"))
```
This is correct because struct fields are navigated with dot-notation directly inside `select` (no special function needed), while `explode` is the operation that turns an array column into multiple rows — one per element — which is why row counts multiply after an explode, exactly the same "grain change" math as a one-to-many SQL join.

#### Q48. Compute each order's total value *without* using `explode`. **[Senior/Experienced]**
*Why interviewers ask this:* Tests knowledge of higher-order functions as a lighter-weight alternative to explode-transform-collect.
**Answer:**
```python
order.withColumn("total",
    F.aggregate("items", F.lit(0.0), lambda acc, x: acc + x.qty * x.price))
```
`F.aggregate` is a higher-order function that runs a reducer *inside* the array for each row, without ever multiplying the row count the way `explode` → aggregate → re-collect would. This is correct because it avoids the unnecessary grain change entirely — exploding a 1-million-order table with 50-item arrays into 50 million rows just to sum them back down per order is wasted work that higher-order functions skip completely.

#### Q49. Write PySpark code to parse a Kafka `value` column (raw JSON bytes) into typed columns, and explain how you'd count unparseable messages. **[Frequently Asked]**
*Why interviewers ask this:* A very common streaming-adjacent practical question.
**Answer:**
```python
from pyspark.sql.types import StructType, StructField, StringType, LongType

payload_schema = StructType([
    StructField("event", StringType()),
    StructField("user_id", LongType()),
])

parsed = (raw
    .withColumn("data", F.from_json(F.col("value").cast("string"), payload_schema))
    .select("data.*"))

unparseable_count = parsed.filter(F.col("event").isNull() & F.col("user_id").isNull()).count()
```
This is correct because `from_json` with an explicit schema is the production path (typed and fast, unlike untyped exploration tools like `get_json_object`), and rows that fail to match the schema become an **all-null struct** rather than raising an error — so counting rows where every extracted field is null is the standard way to surface the parse-failure rate as a monitored metric instead of letting bad messages silently vanish.

---

## D2. UDFs & Pandas Integration

*(full notes: [10_UDFs_and_Pandas_Integration.md](10_UDFs_and_Pandas_Integration.md))*

#### Q50. Why is a row-by-row Python UDF 10–100× slower than a built-in Spark function? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental and frequently asked PySpark performance questions.
**Answer:** For every row, a UDF requires Spark to **serialize the value, ship it out of the JVM to a separate Python worker process, run the Python function, and ship the result back** — a round-trip that happens per row. A UDF is also an opaque black box to Catalyst: no pushdown or optimization can happen through it, and it breaks whole-stage code generation (Tungsten's fused JVM bytecode pipeline). Built-in `F.*` functions, by contrast, run entirely inside the JVM as part of the optimized, codegen'd execution. This is correct because it names both costs (the per-row serialization round-trip *and* the loss of optimizer visibility), which together explain the full magnitude of the slowdown, not just one factor.

#### Q51. Write a pandas UDF, and explain why a naive z-score implementation has a subtle bug. **[Senior/Experienced]**
*Why interviewers ask this:* Tests real pandas UDF mechanics, including a genuinely common mistake.
**Answer:**
```python
@F.pandas_udf("double")
def zscore(v: pd.Series) -> pd.Series:
    return (v - v.mean()) / v.std()   # BUG: computes mean/std per BATCH, not per whole column
```
A pandas UDF receives data in **Arrow batches**, not the whole column at once — this function computes `mean()`/`std()` separately for each batch, so the "z-score" is relative to whatever rows happened to land in that particular batch, not the true global (or group-wise) statistics. For genuine group-wise or global aggregation-dependent logic, the correct tool is a window function or `applyInPandas` on a properly defined group, not a plain `pandas_udf`. This is correct because it identifies exactly where the batch boundary breaks the intended semantics — a bug that would pass casual testing on small data but silently produce wrong numbers at scale, when batch boundaries actually matter.

#### Q52. What is `applyInPandas`, and how is it different from a regular `pandas_udf`? **[Senior/Experienced]**
*Why interviewers ask this:* Tests knowledge of the full pandas-integration toolkit beyond the basic scalar UDF.
**Answer:**
```python
def detrend(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf["sales_detrended"] = pdf["sales"] - pdf["sales"].rolling(7, min_periods=1).mean()
    return pdf

result = daily_sales.groupBy("store").applyInPandas(
    detrend, schema="store string, date date, sales double, sales_detrended double")
```
`applyInPandas` runs a "split-apply-combine" pattern: it hands a **complete pandas DataFrame for one entire group** to your function, letting you use genuinely pandas-native logic (rolling windows, per-group models, forecasting) — a `pandas_udf` operates on Series in arbitrary batches with no group guarantee. The contract is that each *group* must fit in one executor's memory. This is correct because it identifies the specific capability `applyInPandas` unlocks (whole-group pandas logic) that a plain `pandas_udf` cannot provide, and states the memory constraint that governs when it's safe to use.

#### Q53. Give the full decision ladder for choosing between built-ins, higher-order functions, pandas UDFs, and row UDFs. **[Frequently Asked]**
*Why interviewers ask this:* A synthesis question that tests whether the candidate has internalized the whole UDF-avoidance discipline, not just one fact.
**Answer:** In order of preference: (1) **built-in `F.*` functions / SQL expressions** — always check first, the function library covers far more than most people expect; (2) **higher-order functions** for array/struct logic (`F.transform`, `F.aggregate`, `F.filter`); (3) **pandas UDFs / `applyInPandas`** — vectorized, for genuinely custom math or pandas/scipy/sklearn-ecosystem logic; (4) **row-by-row UDF** — last resort, and worth a comment justifying why nothing above could express the logic. This is correct because each step down the ladder costs performance and optimizer visibility while gaining expressiveness — reciting this ladder in order is exactly what interviewers want, since most "we need a UDF" moments actually dissolve at step 1 or 2.

---

## D3. Spark SQL & Views

*(full notes: [11_Spark_SQL_and_Views.md](11_Spark_SQL_and_Views.md))*

#### Q54. Does `spark.sql("...")` run slower than the equivalent DataFrame API code? **[Frequently Asked]**
*Why interviewers ask this:* A very common question testing whether the SQL-vs-DataFrame choice is understood as stylistic, not performance-based.
**Answer:** No — both compile through the **same Catalyst optimizer to identical physical plans**. The choice between SQL and the DataFrame API is purely about readability, team skills, and dynamic/parameterized logic needs (the DataFrame API handles loops and config-driven logic far better than string-templated SQL), never about performance. This is correct because it states the actual architectural fact (shared optimizer, identical plans) rather than a guess, which is exactly what distinguishes a confident correct answer from a plausible-sounding wrong one.

#### Q55. Does registering a DataFrame as a temp view and querying it five times make anything faster? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether views are correctly understood as unmaterialized, a common misconception carried over from database views.
**Answer:** No — a temp view is a **named plan**, not materialized data; referencing it five times re-runs the underlying plan five times, exactly like a SQL CTE that isn't explicitly materialized. If an expensive intermediate result is genuinely reused, the fix is to `.cache()` the DataFrame or write it to a physical staging table — the view registration alone saves nothing computationally. This is correct because it corrects the natural but wrong assumption (that naming something makes it faster) and gives the actual mechanism that would provide the reuse benefit the candidate is probably imagining.

#### Q56. When would you deliberately choose NOT to put transformation logic in SQL? **[Senior/Experienced]**
*Why interviewers ask this:* Tests judgment about the practical SQL-vs-DataFrame-API split real teams use.
**Answer:** Two concrete cases: dynamic or parameterized logic that needs loops or conditionals over a *config* (e.g. applying a different cleaning rule per table from a metadata table) — the DataFrame API's Python control flow handles this cleanly, while SQL forces either building fragile query strings or duplicating near-identical statements; and reusable, independently unit-tested functions, where a pure Python function (`DataFrame in, DataFrame out`) can be tested with tiny inline DataFrames outside of any SQL context. The anti-pattern to avoid either way is building SQL via f-string templating with embedded `if`/loop logic — that's the exact signal to switch to the DataFrame API instead. This is correct because it names concrete, checkable scenarios (parameterized/config-driven logic, testable reusable functions) rather than a vague preference, and flags the specific anti-pattern (f-string SQL) that signals the wrong tool is being used.

---

# Group E: Delta Lake

## E1. Delta Lake with PySpark

*(full notes: [12_Delta_Lake_with_PySpark.md](12_Delta_Lake_with_PySpark.md))*

#### Q57. What is Delta Lake, and why use it instead of plain Parquet? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental and frequently asked modern lakehouse questions.
**Answer:** Delta Lake is Parquet files plus a **transaction log** (`_delta_log/`), which gives lake storage database-like behavior: ACID transactions, schema enforcement, time travel, and `MERGE` support — none of which raw Parquet files provide alone. Interview one-liner: "Parquet is a file format; Delta is Parquet plus a transaction log that makes a set of those files behave like a database table." This is correct because it states the precise relationship (Delta *contains* Parquet, plus a metadata layer) rather than treating them as two competing, unrelated formats.

#### Q58. Write a Delta `MERGE` statement that updates matching employees, deletes those flagged as deleted, and inserts new ones. **[Frequently Asked]**
*Why interviewers ask this:* The upsert pattern is arguably the single most-run statement in real lakehouse pipelines — a near-guaranteed practical question.
**Answer:**
```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "silver.employees")

(target.alias("t")
 .merge(updates.alias("s"), "t.id = s.id")
 .whenMatchedUpdate(set={"salary": "s.salary", "dept": "s.dept"})
 .whenMatchedDelete(condition="s.is_deleted = true")
 .whenNotMatchedInsertAll()
 .execute())
```
This is correct because it covers all three MERGE clauses (matched-update, matched-delete, not-matched-insert) that together implement a full upsert-with-deletes in one atomic statement — and the source `updates` DataFrame must be **deduplicated on the key first**, since duplicate source keys cause a "multiple source rows matched" error at runtime, a very common practical pitfall.

#### Q59. How does the Delta transaction log actually work, and why does it prevent readers from ever seeing a half-written table? **[Senior/Experienced]**
*Why interviewers ask this:* A frequently asked "explain the internals" question that separates surface-level Delta knowledge from real understanding.
**Answer:** `_delta_log/` holds numbered JSON commit files (plus periodic Parquet checkpoints for efficiency) — each commit lists exactly which data files were **added** and **removed** in that version. A reader determines the current state of the table by combining the latest checkpoint with subsequent commits, which together give the *exact* file set for a given version. Because uncommitted files simply never appear in the log, a reader can never see a partially-written table — the write either fully lands as a new committed log entry, or it never happened at all from the reader's perspective. Concurrent writers use **optimistic concurrency**: if two commits conflict, one succeeds and the other fails with `ConcurrentAppendException` and must retry. This is correct because it explains the actual mechanism (the log as the single source of truth for "what files currently exist") rather than "Delta uses ACID transactions" as an unexplained label — and it directly explains *why* time travel is simply "replay to an older commit."

#### Q60. What is the relationship between `VACUUM` and time travel, and what's the risk of running `VACUUM` too aggressively? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of a genuine, common production trade-off in Delta table maintenance.
**Answer:** Time travel works by reading *older* files still referenced by past log entries; `VACUUM` physically **deletes** files no longer referenced by any commit within the retention window (default 7 days via `delta.deletedFileRetentionDuration`). Running `VACUUM` past that retention permanently breaks time travel and `RESTORE` for versions older than the cutoff, and — more dangerously — can break any *currently running* reader still holding an older snapshot if retention is disabled or set too aggressively. This is correct because it identifies the direct tension (VACUUM deletes exactly what time travel depends on) and the specific operational risk (breaking a concurrent reader), which is why retention policy should be decided per table class rather than universally minimized for storage savings.

#### Q61. A streaming job doing frequent small MERGEs into a Delta table has caused storage to triple in a month. What are the two likeliest causes, and how do you fix each? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic operational scenario testing Delta maintenance knowledge under real production conditions.
**Answer:** First, **streaming plus frequent MERGE is a classic small-file factory** — each micro-batch MERGE can produce new small files, and without regular compaction, file count (and associated overhead) balloons; the fix is scheduling `OPTIMIZE` regularly (or enabling `delta.autoOptimize.*` table properties for automatic compaction). Second, **VACUUM not being run** (or retention set too long) on a high-churn table means old file versions from every MERGE commit pile up indefinitely, since MERGE rewrites files rather than editing them in place; the fix is a deliberate, table-appropriate `VACUUM` schedule. This is correct because it names two independent, both-plausible causes (file proliferation from MERGE + missing compaction, and unvacuumed old versions) with a distinct fix for each, matching how a real incident investigation would actually branch.

---

# Group F: Structured Streaming

## F1. Structured Streaming

*(full notes: [13_Structured_Streaming.md](13_Structured_Streaming.md))*

#### Q62. What is the core mental model behind Spark Structured Streaming? **[Frequently Asked]**
*Why interviewers ask this:* The foundational concept for the entire streaming API — a near-guaranteed question if streaming comes up.
**Answer:** A stream is treated as an **unbounded table**, and the exact same DataFrame API used for batch processing runs incrementally against it — `spark.read` becomes `spark.readStream`, `df.write` becomes `df.writeStream`, and the same transformations (filters, joins, aggregations) apply unchanged. This is correct because it identifies the actual unifying idea (one API, two execution modes) rather than treating streaming as a separate system — it's also *why* Lambda architecture (maintaining two separate pipelines for batch and real-time) became largely unnecessary once this unification existed.

#### Q63. What is a checkpoint in Structured Streaming, and why is it non-negotiable? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental streaming concepts, testing understanding of failure recovery.
**Answer:** A checkpoint is the stream's memory — which input has already been processed, plus any accumulated state (for aggregations) — stored in a dedicated location, one folder **per query**. Without a checkpoint, a restarted stream has no way to know what it already processed, either reprocessing everything from scratch (duplicates) or silently starting from an arbitrary point (data loss). Deleting a checkpoint folder is destructive — the stream effectively starts over. This is correct because it names exactly what state the checkpoint holds and precisely what breaks without it, rather than a vague "checkpoints are for recovery."

#### Q64. What is `trigger(availableNow=True)`, and why is it described as "most production streaming pipelines"? **[Senior/Experienced]**
*Why interviewers ask this:* Tests knowledge of a practical, frequently used pattern that many candidates miss in favor of assuming streaming always means 24/7 clusters.
**Answer:** `availableNow=True` processes **all currently pending data, then stops** — giving you streaming's bookkeeping benefits (exactly-once semantics via checkpointing, no reprocessing of already-handled data) while running like a scheduled batch job: the cluster only runs while there's actual work, then terminates. Scheduled hourly or nightly, this is genuinely how most "streaming" pipelines run in production — continuous, always-on clusters are reserved for workloads where minutes-level latency is a real business requirement, which is a smaller set of cases than the word "streaming" suggests. This is correct because it corrects a common assumption (streaming = always-on) and identifies the specific trigger option and its cost/latency trade-off.

#### Q65. Why are watermarks required for streaming aggregations, and what happens to data that arrives later than the watermark allows? **[Frequently Asked]**
*Why interviewers ask this:* A core streaming concept, essential for any windowed aggregation question.
**Answer:**
```python
counts = (events
    .withWatermark("ts", "30 minutes")
    .groupBy(F.window("ts", "5 minutes"), "region")
    .agg(F.count("*").alias("events")))
```
Aggregating a stream requires keeping running state per key/window indefinitely unless bounded — a watermark declares how late data is allowed to arrive (here, 30 minutes), letting Spark finalize and drop state for windows older than that bound. Data arriving **later than the watermark allows is dropped**, not merged into a reopened window — which is why the real lateness of the actual data source should be measured before choosing a watermark duration, and why `append` output mode only emits a window's result once the watermark has passed it (an inherent latency cost equal to window size plus lateness). This is correct because it names both the mechanism (bounding otherwise-infinite state) and the concrete consequence (dropped late data, delayed emission) that a candidate must account for when designing a streaming aggregation.

#### Q66. Write PySpark code implementing a streaming MERGE (CDC-to-silver pattern) using `foreachBatch`. **[Senior/Experienced]**
*Why interviewers ask this:* One of the most common real production streaming patterns, and a strong practical test of combining Structured Streaming with Delta.
**Answer:**
```python
def upsert(batch_df, batch_id):
    (DeltaTable.forName(spark, "silver.orders").alias("t")
     .merge(batch_df.dropDuplicates(["order_id"]).alias("s"), "t.order_id = s.order_id")
     .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())

(orders.writeStream.foreachBatch(upsert)
    .option("checkpointLocation", chk)
    .trigger(availableNow=True)
    .start())
```
`foreachBatch` is the escape hatch that hands you a normal, static DataFrame for each micro-batch, inside which any batch-style logic (including MERGE) is available. This is correct because it deduplicates the batch on the key *before* merging (required, since a batch can contain multiple changes to the same key within the window), and because it flags the real caveat: writing to two sinks inside one `foreachBatch` call is not atomic across those sinks, so idempotency for multi-sink writes must be designed explicitly using the provided `batch_id`.

#### Q67. What does "exactly-once" actually mean in Structured Streaming, and what breaks that guarantee? **[Senior/Experienced]**
*Why interviewers ask this:* Tests precise understanding rather than treating "exactly-once" as an unconditional magic property.
**Answer:** End-to-end exactly-once holds for the **default single-sink path**: a replayable source (Kafka offsets or a trackable file list) plus a checkpoint (recording exactly what's been read) plus a transactional sink (Delta) together guarantee no duplicates and no loss. Any deviation from that path — a `foreachBatch` writing to two separate sinks, or a non-transactional sink — drops the guarantee back to at-least-once, meaning the pipeline logic must be designed to be idempotent anyway regardless of what the framework promises. This is correct because it states the exact conditions under which the guarantee genuinely holds, rather than treating "exactly-once" as an unconditional feature — a senior-level nuance that matters the moment a design deviates even slightly from the default path.

---

# Group G: Performance Tuning & Production

## G1. Performance & Best Practices

*(full notes: [14_Performance_and_Best_Practices.md](14_Performance_and_Best_Practices.md))*

#### Q68. Give the correct order of steps for diagnosing and fixing a slow Spark job. **[Frequently Asked]**
*Why interviewers ask this:* A synthesis question testing the full tuning workflow, not just isolated facts.
**Answer:** (1) **Measure** — Spark UI: which stage dominates, is there skew, spill, or unexpectedly large shuffle sizes? (2) **Plan** — `df.explain()`: unexpected shuffles, wrong join strategy, filters not being pushed down? (3) **Fix the plan** — broadcast hints, pre-aggregation, earlier filtering/selecting, salting for skew; (4) **fix the data** — file sizes via `OPTIMIZE`, partitioning/clustering, stale statistics; (5) **fix resources** — partitions, memory, cluster size, *last, not first*. This is correct because it states the actual professional priority order — jumping straight to "add a bigger cluster" without steps 1–4 is explicitly called out as the defining junior mistake, since it sometimes works by accident but skips the diagnosis that would find the real, cheaper fix.

#### Q69. How should a PySpark transformation pipeline be structured to be unit-testable? **[Senior/Experienced]**
*Why interviewers ask this:* Tests software-engineering maturity applied to Spark code, increasingly common in senior interviews.
**Answer:**
```python
# transformations.py — pure function: DataFrame in, DataFrame out, no I/O
def clean_orders(df: DataFrame) -> DataFrame:
    return (df.filter(F.col("order_id").isNotNull())
              .withColumn("amount", F.col("amount").cast("decimal(18,4)")))

# test_transformations.py — runs on local[*] Spark, no cluster needed
def test_clean_orders_drops_null_ids(spark):
    src = spark.createDataFrame([(1, "10.5"), (None, "9.0")], "order_id long, amount string")
    out = clean_orders(src)
    assert out.count() == 1
```
The structural rule is **I/O at the edges, logic in pure functions**: transformation logic takes a DataFrame and returns a DataFrame with no reads/writes inside it, which lets it be tested with tiny inline DataFrames on a local Spark session — no cluster, no real data, in CI. This is correct because it identifies the specific architectural discipline (separating I/O from logic) that makes testing possible at all — a job that mixes reads/writes throughout its transformation code cannot be unit-tested this way.

#### Q70. What does it mean for a PySpark job to be "idempotent," and give three concrete write patterns that achieve it. **[Frequently Asked]**
*Why interviewers ask this:* Arguably the single most important production-pipeline property, and a near-guaranteed question in some form.
**Answer:** Idempotent means running the same job twice produces the same correct end state — no duplicated or corrupted data — which matters because orchestrators retry failed jobs, and a half-completed run followed by a blind retry must not double-count anything. Three patterns: `MERGE` on business keys (re-running converges to the same state); a `replaceWhere`-scoped Delta overwrite on a deterministic partition (`replaceWhere="date='2026-07-19'"`, rewriting exactly that slice atomically); and staging-plus-atomic-swap (load to staging, validate, then swap into place). The one non-idempotent pattern to flag is a blind `append` — the most common production data bug in existence when combined with retries. This is correct because it names the actual test ("what happens if this runs twice?") and gives three real patterns plus the specific anti-pattern that fails it.

#### Q71. A `FetchFailedException` appears in the driver logs. What does it mean, and what's the likely root cause? **[Senior/Experienced]**
*Why interviewers ask this:* A specific, realistic log-reading question testing whether the candidate can translate an error message into an actual diagnosis.
**Answer:** `FetchFailedException` means a task tried to fetch shuffle data from a peer executor that no longer exists or no longer has it — the visible symptom of **executor churn**: a spot VM eviction, an OOM kill, or dynamic deallocation removing an executor that was still holding shuffle output another stage needed. This forces a partial stage re-execution to regenerate the lost shuffle data. This is correct because it translates a raw exception name into its actual root cause category (executor loss, specifically around shuffle data) rather than treating it as a generic error — the fix direction (investigate why executors are disappearing: spot eviction policy, memory pressure, dynamic allocation aggressiveness) follows directly from correctly identifying this.

#### Q72. Your team wants to fix a slow nightly job by "adding a bigger cluster." What do you check first, and what evidence would actually justify that? **[Senior/Experienced]**
*Why interviewers ask this:* A judgment scenario testing resistance to the reflexive "throw resources at it" instinct.
**Answer:** Check the Spark UI for the dominant stage first — if the job is bottlenecked on a single **skewed task** (max task time far exceeding the median), or on excessive **shuffle/spill**, or on a **missed broadcast join**, a bigger cluster adds more idle capacity around the same bottleneck without fixing it; those problems are fixed in the plan (salting, broadcasting, pre-aggregation), not by adding nodes. A bigger cluster is genuinely justified when the UI shows evenly distributed work across *all* tasks with no single stage dominating disproportionately, and the workload is simply larger than the current cluster's total core/memory capacity can process in the required time. This is correct because it gives the specific UI evidence that distinguishes "this needs more resources" from "this needs a better plan" — the exact judgment call the scenario is testing.

---

# Group H: RDDs

## H1. RDDs: The Foundation

*(full notes: [15_RDDs_The_Foundation.md](15_RDDs_The_Foundation.md))*

#### Q73. What is an RDD, and how is it different from a DataFrame? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental and frequently asked PySpark questions — nearly guaranteed at some point.
**Answer:** An RDD (Resilient Distributed Dataset) is Spark's most basic data structure — an immutable, distributed collection of *any* Python/Java/Scala objects, split into partitions, with no column names or types Spark understands, and **no optimizer** looking inside it. A DataFrame is a distributed *table* — named, typed columns — that Catalyst can see into and optimize (reorder operations, push down filters, generate efficient bytecode). An RDD `.map(lambda x: ...)` is an opaque function Spark must run exactly as written; a DataFrame expression like `F.col("amount") > 0` is data the optimizer can reason about and rewrite. This is correct because it identifies the actual differentiator (optimizer visibility, not just "DataFrames have columns") — which is also the direct explanation for why DataFrames are strictly faster for structured data work.

#### Q74. Write word count from scratch using RDDs, and explain what `flatMap` does that `map` cannot. **[Frequently Asked]**
*Why interviewers ask this:* The classic "hello world" of big data — still asked to test whether the candidate understands RDD mechanics at a basic level.
**Answer:**
```python
text = spark.sparkContext.parallelize(["spark is fast", "spark is fun"])
word_counts = (text
    .flatMap(lambda line: line.split(" "))     # one element per WORD, not per line
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b))
word_counts.collect()
# [('spark', 2), ('is', 2), ('fast', 1), ('fun', 1)]
```
`map` gives exactly one output per input — mapping a line to a list of words with `map` would produce an RDD of *lists*, not words. `flatMap` gives zero-or-more outputs per input and flattens the results into a single-level RDD, which is exactly what turning "lines" into "words" requires — it's the RDD-level ancestor of DataFrame's `explode`. This is correct because it demonstrates the exact difference with a concrete failure case (map would leave nested lists) rather than an abstract description.

#### Q75. Why is `reduceByKey` almost always preferred over `groupByKey`? Trace exactly what each ships across the network. **[Frequently Asked]**
*Why interviewers ask this:* The single most important RDD performance lesson, and a very common interview question in its own right.
**Answer:**
```python
pairs = sc.parallelize([("IT", 60000), ("IT", 65000), ("HR", 50000)])

# groupByKey: ships EVERY value across the network, THEN combines
pairs.groupByKey().mapValues(sum)     # all of IT's 60000 and 65000 travel to one node, summed there

# reduceByKey: combines LOCALLY on each partition first, THEN ships only the partial sums
pairs.reduceByKey(lambda a, b: a + b) # each node pre-sums its own IT values; only the small partial travels
```
`reduceByKey` performs **map-side pre-aggregation** — combining values locally within each partition before any shuffle — so only the small combined results move across the network. `groupByKey` ships every individual value across the network first and only combines afterward, which is dramatically more network-heavy for large groups. This is exactly the same partial-aggregation optimization that makes DataFrame `groupBy().sum()` cheap, except at the RDD level *you* must choose the efficient operation — the DataFrame API's optimizer makes this choice automatically, which is a large part of why the DataFrame API replaced hand-written RDD code for everyday work. This is correct because it traces the actual data movement for both operations side by side, which is what the question explicitly asks for.

#### Q76. An executor dies mid-job while processing an RDD. Walk through exactly how Spark recovers the lost partition. **[Senior/Experienced]**
*Why interviewers ask this:* Tests the mechanical understanding of RDD fault tolerance — a common deep-dive question.
**Answer:** Every RDD remembers its **lineage** — the exact chain of transformations that produced it (e.g. `textFile → map → filter → reduceByKey`). Spark never keeps a backup replica of the data itself for safety; instead, when an executor holding a partition dies, Spark identifies which partition was lost and **recomputes just that partition** by replaying its specific slice of the lineage graph from the original source — not the whole dataset, and not from any stored backup copy. This is correct because it names the exact concept (lineage-based recomputation, not replication) that makes RDD/DataFrame fault tolerance work, and explicitly distinguishes it from HDFS's very different approach (multiple stored physical copies).

#### Q77. You're maintaining an old RDD pipeline with a 200-step transformation chain that keeps failing slowly on executor loss. What single technique would you reach for, and why? **[Senior/Experienced]**
*Why interviewers ask this:* Tests knowledge of `checkpoint()` as distinct from `cache()`, a commonly confused pair.
**Answer:**
```python
spark.sparkContext.setCheckpointDir("path/checkpoints/")
long_chain_rdd.checkpoint()
```
`checkpoint()` writes the RDD to reliable storage and **truncates its lineage** — after checkpointing, recovery from a future failure only needs to replay from the checkpoint forward, not from the original source through all 200 prior steps. Without it, recomputation cost grows with the length of the lineage chain — a 200-step chain makes even a single lost partition expensive to rebuild, and repeated failures compound that cost every time. This is correct because it identifies the specific problem (recomputation cost scaling with lineage length) and the specific tool that solves exactly that problem — `cache()` alone wouldn't help here, since a cached-but-evicted partition still falls back to full lineage replay.

#### Q78. When would an experienced engineer still reach for the RDD API today instead of the DataFrame API? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether the candidate understands RDDs as a deliberate occasional tool rather than either "always use DataFrames" or "RDDs are equally valid day to day" — both wrong extremes.
**Answer:** Four legitimate cases: genuinely unstructured data requiring per-record custom logic with no column shape at all (parsing exotic binary formats); needing fine-grained control over physical partitioning that the DataFrame API doesn't expose, such as a **custom partitioner** to keep specific keys co-located across repeated joins/`reduceByKey` calls; maintaining or migrating legacy pre-2015 Spark codebases; and occasionally `df.rdd.mapPartitions(...)` as a genuine escape hatch when even `pandas_udf`/`mapInPandas` can't express something. For everything else — which is nearly all day-to-day data engineering work — the DataFrame API is strictly better: faster by default, more readable, and automatically optimized. This is correct because it lists specific, checkable conditions rather than a blanket rule, which is what distinguishes real engineering judgment from a memorized "RDDs are legacy" talking point.

---

## Rapid-Fire Round

- Q: What makes Spark faster than MapReduce? — A: In-memory processing between stages instead of writing to disk every step.
- Q: Transformation or action — which triggers execution? — A: Action.
- Q: What does the driver do that it should NEVER do at scale? — A: `.collect()` a huge DataFrame — it forces all data into one process.
- Q: Narrow or wide transformation — which requires a shuffle? — A: Wide (e.g. groupBy, join, orderBy).
- Q: repartition() or coalesce() — which avoids a shuffle? — A: coalesce() (only reduces partition count).
- Q: What threshold decides automatic broadcast joins by default? — A: 10 MB (`spark.sql.autoBroadcastJoinThreshold`).
- Q: What does AQE do that the old static optimizer couldn't? — A: Re-optimize mid-query using real runtime statistics (coalesce shuffle partitions, switch to broadcast, split skew).
- Q: RDD or DataFrame — which has an optimizer? — A: DataFrame (Catalyst); RDDs have none.
- Q: What does a failed `.cast()` produce in PySpark? — A: null, not an error (unless ANSI mode is enabled).
- Q: Window function without partitionBy — what's the danger? — A: Pulls the entire dataset into one partition/task.
- Q: What's the standard "top-N per group" pattern? — A: `row_number()` over a partitioned+ordered window, filtered `<= N`.
- Q: Why is a row-by-row Python UDF slow? — A: Per-row serialization round-trip to a separate Python worker process, and it's opaque to the optimizer.
- Q: What's the decision ladder before writing a UDF? — A: Built-ins → higher-order functions → pandas UDF → row UDF (last resort).
- Q: What does Delta add on top of plain Parquet? — A: A transaction log giving ACID commits, schema enforcement, time travel, and MERGE.
- Q: What must you do to the MERGE source before merging? — A: Deduplicate it on the key.
- Q: What does VACUUM do, and what's the risk of running it too aggressively? — A: Deletes old unreferenced files; can break time travel and concurrent readers on older snapshots.
- Q: What is a checkpoint in Structured Streaming? — A: The stream's record of what's been processed plus accumulated state, for failure recovery.
- Q: What happens to streaming data that arrives later than the watermark? — A: It's dropped.
- Q: `trigger(availableNow=True)` behaves like what? — A: A scheduled batch job — process everything pending, then stop.
- Q: What makes a pipeline "idempotent"? — A: Running it twice produces the same correct result, no duplicates.
- Q: RDD fault tolerance — recomputation or replication? — A: Recomputation from lineage.
- Q: reduceByKey or groupByKey — which pre-aggregates locally before shuffling? — A: reduceByKey.
- Q: What does checkpoint() do to an RDD's lineage that cache() does not? — A: Truncates it, so recovery doesn't replay the whole chain.
- Q: In the performance tuning workflow, what should you fix last, not first? — A: Resources (partitions/memory/cluster size).

Back to the folder: [06_PySpark notes](.) · Related: [01_SQL Interview Q&A](../01_SQL/Interview_Questions_and_Answers.md)
