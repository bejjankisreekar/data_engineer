# 14 — Exam Dump: Practice Set

> **What this is:** 30 extra **exam-style** practice questions with answers and one-line explanations — a rapid drill on top of [11 — Practice Questions](11_Practice_Questions_by_Domain.md), [12 — Most Asked & Tricky](12_Most_Asked_and_Tricky_Exam_Questions.md), and the [13 — Final Mock Exam](13_Final_Mock_Exam.md).
>
> **These are original questions written to the exam's style and objectives — not real/leaked exam items.** The Databricks Data Engineer Associate exam is code-heavy; make sure you can *write* the snippet, not just recognize it. Answer each before revealing.

---

## Domain 1 — Databricks Lakehouse Platform

**1.** In Databricks architecture, the web UI, job scheduling, and metadata live in the:
<details><summary>Answer</summary>**Control plane** (managed by Databricks). Your clusters and data live in the **data plane** (your cloud account).</details>

**2.** Which cluster type spins up for a scheduled job and terminates when it finishes (cheapest for automation)?
<details><summary>Answer</summary>A **job cluster**. All-purpose clusters are for interactive notebook work.</details>

**3.** Which magic command runs a shell command in a notebook cell?
<details><summary>Answer</summary>**`%sh`**. (`%sql`, `%python`, `%md`, `%run` are the other common magics.)</details>

**4.** To include another notebook's functions in the current notebook, use:
<details><summary>Answer</summary>**`%run ./other_notebook`**.</details>

**5.** Which utility lists files in a storage path from a notebook?
<details><summary>Answer</summary>**`dbutils.fs.ls(path)`**.</details>

**6.** Databricks Repos integrates notebooks with:
<details><summary>Answer</summary>**Git** (version control) — for CI/CD and collaboration.</details>

---

## Domain 2 — ELT with Spark SQL & Python

**7.** Which keyword creates a table from a query result in one statement?
<details><summary>Answer</summary>**`CREATE TABLE ... AS SELECT`** (CTAS).</details>

**8.** What's the difference between a **managed** and an **external** table when you `DROP` it?
<details><summary>Answer</summary>Dropping a **managed** table deletes both metadata **and** the underlying data files; dropping an **external** table deletes only the metadata (files remain).</details>

**9.** Which SQL operation applies inserts, updates, and deletes to a Delta table in one atomic statement?
<details><summary>Answer</summary>**`MERGE INTO`** (upsert).</details>

**10.** To read a JSON file's raw contents ad-hoc in Spark SQL, you can query:
<details><summary>Answer</summary>**`SELECT * FROM json.\`/path/file.json\``** (file-format query syntax).</details>

**11.** Which function parses a JSON string column into a struct given a schema?
<details><summary>Answer</summary>**`from_json()`**.</details>

**12.** Which explodes an array column into one row per element?
<details><summary>Answer</summary>**`explode()`**.</details>

**13.** A **temporary view** created with `CREATE TEMP VIEW`:
<details><summary>Answer</summary>Exists only for the **current SparkSession**; it's not persisted in the metastore.</details>

**14.** In PySpark, which is a **transformation** (lazy), not an action?
<details><summary>Answer</summary>**`filter()`** / `select()` / `withColumn()` — lazy. `count()`, `collect()`, `show()`, `write` are actions that trigger execution.</details>

**15.** Which counts non-null vs total for a column to check completeness?
<details><summary>Answer</summary>`count(col)` counts non-nulls; `count(*)` counts all rows — the difference reveals nulls.</details>

---

## Domain 3 — Incremental Data Processing (Delta & Streaming)

**16.** What gives a Delta table its ACID guarantees and time travel?
<details><summary>Answer</summary>The **transaction log** (`_delta_log`) — the ordered record of every commit.</details>

**17.** Which command compacts many small files into fewer large ones?
<details><summary>Answer</summary>**`OPTIMIZE`** (optionally with `ZORDER BY` to co-locate values).</details>

**18.** Which permanently removes data files no longer referenced, past the retention window?
<details><summary>Answer</summary>**`VACUUM`** — note it can remove older time-travel versions.</details>

**19.** How do you query a Delta table as it was 5 versions ago?
<details><summary>Answer</summary>**Time travel**: `SELECT * FROM t VERSION AS OF 5` (or `TIMESTAMP AS OF '...'`).</details>

**20.** Which Databricks feature incrementally ingests new files as they land in cloud storage, with schema inference?
<details><summary>Answer</summary>**Auto Loader** (`cloudFiles`).</details>

**21.** In a streaming read, what stores progress so a query can resume exactly where it stopped?
<details><summary>Answer</summary>The **checkpoint** (via `checkpointLocation`).</details>

**22.** Which output mode writes only new aggregate results each trigger for a streaming aggregation?
<details><summary>Answer</summary>**`update`** mode. (`complete` rewrites the whole result table; `append` is for non-aggregated/late-safe rows.)</details>

**23.** `COPY INTO` is used to:
<details><summary>Answer</summary>Idempotently and **incrementally load** files into a Delta table (skips already-loaded files).</details>

---

## Domain 4 — Production Pipelines (DLT & Jobs)

**24.** Which declarative framework lets you define tables + quality **expectations** and manages the pipeline for you?
<details><summary>Answer</summary>**Delta Live Tables (DLT)**.</details>

**25.** In DLT, `@dlt.expect_or_drop("valid", "amount > 0")` will:
<details><summary>Answer</summary>**Drop** rows failing the expectation (and track them in metrics). `expect` warns; `expect_or_fail` fails the pipeline.</details>

**26.** In the medallion architecture, which layer holds raw, as-ingested data?
<details><summary>Answer</summary>**Bronze**. (Silver = cleaned/conformed; Gold = business-ready aggregates.)</details>

**27.** A DLT **streaming table** vs a **materialized view** — which processes each input record once, incrementally?
<details><summary>Answer</summary>A **streaming table** (append/incremental). A materialized view recomputes results from the full source.</details>

**28.** In a multi-task Databricks Job, how do you make task B run only after task A succeeds?
<details><summary>Answer</summary>Set a **task dependency** (B "depends on" A) in the Job/Workflow.</details>

---

## Domain 5 — Data Governance (Unity Catalog)

**29.** Unity Catalog's object namespace has how many levels, and what are they?
<details><summary>Answer</summary>**Three**: `catalog.schema.table` (and volume/view). This "three-level namespace" is heavily tested.</details>

**30.** Which Unity Catalog feature restricts which **rows** a user can see in a table?
<details><summary>Answer</summary>A **row filter** (row-level security). A **column mask** hides/obscures column values.</details>

---

## Score guide

| Score | Readiness |
|---|---|
| 27–30 | Exam-ready |
| 22–26 | Close — drill the code you missed (write it by hand) |
| < 22 | Re-study the [study guide](00_Study_Guide_Overview.md) |

Next: the timed [Final Mock Exam](13_Final_Mock_Exam.md).
