# 08 — Delta Live Tables (DLT)

*Domain: Incremental Data Processing (22%)*

> Note: Delta Live Tables has been rebranded **Lakeflow Declarative Pipelines** in newer Databricks releases. The current Associate exam still uses the **DLT** name and syntax (`@dlt.table`, `LIVE.`, `STREAMING`), which is what this file teaches.

---

## What it is

**Delta Live Tables (DLT)** is a **declarative framework for building reliable ETL pipelines**. Instead of writing and orchestrating individual streaming/batch jobs by hand, you **declare the tables you want and the queries that define them**, and DLT automatically manages the execution: dependency ordering, cluster provisioning, incremental processing, error handling, retries, and data-quality enforcement.

**Analogy:** Hand-writing streaming jobs is like manually driving each delivery truck and remembering the route order. DLT is telling a dispatcher "here are the deliveries and what depends on what" — it figures out the order, the trucks, and handles breakdowns.

> **Exam Tip:** DLT is **declarative** — you define *what* each table should contain (a query), not *how* to run it. DLT builds the **dependency graph (DAG)** automatically from your table definitions, manages the infrastructure, and handles incremental updates and recovery. If a scenario asks for the **least-effort, managed way** to build a multi-hop pipeline with data-quality checks, the answer is **DLT**.

---

## Defining DLT tables

### In SQL

```sql
CREATE OR REFRESH STREAMING LIVE TABLE bronze
AS SELECT * FROM cloud_files('/data', 'json');

CREATE OR REFRESH LIVE TABLE silver
AS SELECT * FROM LIVE.bronze WHERE id IS NOT NULL;
```

### In Python

```python
import dlt

@dlt.table
def bronze():
    return spark.readStream.format("cloudFiles").option("cloudFiles.format","json").load("/data")

@dlt.table
def silver():
    return dlt.read_stream("bronze").where("id IS NOT NULL")
```

- **`LIVE.`** (SQL) / **`dlt.read()` / `dlt.read_stream()`** (Python) — reference **another table in the same DLT pipeline**. This is how DLT learns the dependencies and orders execution.
- **`STREAMING`** (SQL) / `spark.readStream` (Python) — makes the table incremental (processes only new data). Without `STREAMING`, the table is a **materialized view** recomputed from scratch each run.

> **Exam Tip:** Inside a DLT pipeline, always reference other pipeline tables with **`LIVE.table_name`** (SQL) or **`dlt.read()`/`dlt.read_stream()`** (Python) — this is what builds the dependency graph. Use **`STREAMING`** for incremental (append) sources; omit it for full-recompute materialized views.

---

## Streaming tables vs Materialized views

| | Streaming (live) table | Materialized view (live table) |
|---|---|---|
| Processing | **Incremental** — only new data | **Recomputed** from all source data each update |
| Source must be | Append-only (streaming source) | Any |
| Best for | Ingestion (Bronze), append pipelines | Aggregations/transforms that can change historical rows |

---

## Data quality: Expectations

DLT's signature feature is **expectations** — declarative data-quality constraints applied as data flows through:

```sql
CONSTRAINT valid_id EXPECT (id IS NOT NULL)                    -- keep, but track violations
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW    -- drop bad rows
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE -- fail the pipeline
```

```python
@dlt.expect("valid_id", "id IS NOT NULL")                 # warn/track
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")         # drop bad rows
@dlt.expect_or_fail("valid_id", "id IS NOT NULL")         # fail the update
```

| Action | Behavior on violating rows |
|---|---|
| **`EXPECT`** (no `ON VIOLATION`) / `expect` | **Keep** the rows, but **record** the violation in metrics |
| **`ON VIOLATION DROP ROW`** / `expect_or_drop` | **Drop** the offending rows; pipeline continues |
| **`ON VIOLATION FAIL UPDATE`** / `expect_or_fail` | **Fail** the pipeline update immediately |

> **Exam Tip:** Know the three expectation behaviors:
> - **default (warn/track)** — invalid rows are **retained** and counted in the data-quality metrics.
> - **DROP ROW** — invalid rows are **removed** from the target but the pipeline keeps running.
> - **FAIL UPDATE** — invalid rows **halt** the pipeline.
> This is one of the most-asked DLT topics.

---

## Pipeline execution modes

- **Triggered mode** — the pipeline runs once, processes all available data, and **stops**. Good for scheduled batch/incremental refreshes (cost-efficient).
- **Continuous mode** — the pipeline runs **continuously**, processing data as it arrives (low latency, always-on cost).

- **Development vs Production mode** — *Development* reuses the cluster and doesn't retry (faster iteration); *Production* uses a fresh cluster and retries on failure (robust).

> **Exam Tip:** **Triggered** = run-to-completion then stop (scheduled). **Continuous** = always running (real-time). **Development** mode keeps the cluster up and skips retries for fast debugging; **Production** mode provisions fresh clusters and retries on error.

---

## What DLT manages for you

- **Automatic dependency resolution & orchestration** (the DAG).
- **Cluster provisioning** and scaling.
- **Incremental processing & checkpoints** (you don't manage checkpoint locations manually).
- **Data-quality metrics** and an **event log** (auditable pipeline history).
- **Error handling and retries**.
- **Automatic table creation and schema management.**

> **Exam Tip:** With DLT you **do not manually manage checkpoints, cluster orchestration, or table dependencies** — the framework handles them. The DLT **event log** records data-quality results, lineage, and run history.

---

## Quick Review

- **DLT** = **declarative** ETL framework: define target tables + their queries; DLT builds the **DAG**, manages clusters, checkpoints, retries, and quality.
- Reference other pipeline tables with **`LIVE.`** (SQL) / **`dlt.read()`/`dlt.read_stream()`** (Python) — this creates dependencies.
- **`STREAMING`/`readStream`** = incremental table; without it = materialized view (full recompute).
- **Expectations** (`EXPECT`): default = **keep + track**, **DROP ROW** = drop bad rows, **FAIL UPDATE** = stop pipeline.
- **Triggered** (run-then-stop) vs **Continuous** (always-on); **Development** (reuse cluster, no retry) vs **Production** (fresh cluster, retries).
- DLT handles checkpoints/orchestration/retries for you; the **event log** captures quality & lineage.

---

## Further Learning — Docs & Videos

**Official documentation**
- Delta Live Tables / Lakeflow Declarative Pipelines: https://docs.databricks.com/en/delta-live-tables/index.html
- DLT SQL reference: https://docs.databricks.com/en/delta-live-tables/sql-ref.html
- DLT Python reference: https://docs.databricks.com/en/delta-live-tables/python-ref.html
- Expectations (data quality): https://docs.databricks.com/en/delta-live-tables/expectations.html
- Triggered vs continuous: https://docs.databricks.com/en/delta-live-tables/updates.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Delta Live Tables tutorial: https://www.youtube.com/results?search_query=databricks+delta+live+tables+tutorial
- DLT expectations / data quality: https://www.youtube.com/results?search_query=databricks+dlt+expectations+data+quality
- DLT pipeline end-to-end: https://www.youtube.com/results?search_query=databricks+delta+live+tables+medallion+pipeline

---

Next: **[09 — Production Pipelines: Jobs & Orchestration](09_Production_Pipelines_Jobs.md)**.
