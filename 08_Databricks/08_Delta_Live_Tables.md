# Delta Live Tables (DLT)

> **Naming note:** Databricks has rebranded DLT as **Lakeflow Declarative Pipelines**. The concept, syntax, and interview terminology are still overwhelmingly "DLT" / "Delta Live Tables" — both names refer to the same thing.

## What is it?

**Delta Live Tables (DLT)** is a framework for building data pipelines **declaratively**: instead of writing *how* to run and orchestrate each step, you declare *what* each table should contain, and DLT figures out the execution order, runs it incrementally, manages the infrastructure, enforces data quality, and handles errors and recovery for you.

It's the managed, opinionated way to build a [medallion](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) (Bronze→Silver→Gold) pipeline on Databricks.

In one line: **DLT = declarative pipelines — you define the tables and quality rules; DLT builds, orchestrates, and maintains the pipeline.**

---

## Analogy: GPS vs turn-by-turn memorization

Building a pipeline the manual way ([Jobs](04_Notebooks_Repos_and_Jobs.md)) is like **memorizing every turn** of a route — you specify each step, its order, its retries, its dependencies. If a road changes, you re-memorize.

DLT is a **GPS**: you say "get me to the Gold table," declare the waypoints (Bronze, Silver), and the system computes the route (dependency graph), reroutes around problems (retries/recovery), and tells you if you're going the wrong way (data-quality expectations). You describe the destination; it drives.

---

## Declarative vs imperative — the core shift

**Imperative (normal notebook/job):**
```python
bronze = spark.read.json("/landing")
bronze.write.saveAsTable("bronze")
silver = spark.table("bronze").dropDuplicates().where("amount > 0")
silver.write.saveAsTable("silver")
# ...you also wire up order, retries, incremental logic, schedule
```

**Declarative (DLT):**
```python
import dlt

@dlt.table
def bronze():
    return spark.readStream.format("cloudFiles").option("cloudFiles.format","json").load("/landing")

@dlt.table
@dlt.expect_or_drop("valid_amount", "amount > 0")   # data-quality rule
def silver():
    return dlt.read_stream("bronze").dropDuplicates()
```

You declare each table as a function returning a DataFrame. DLT reads the dependencies (`silver` reads `bronze`), builds the **DAG**, runs it in order, incrementally, on managed compute — and enforces the quality expectation.

---

## Data-quality expectations (the standout feature)

Expectations are quality rules attached to a table, with three behaviours:

| Decorator | On violation |
|---|---|
| `@dlt.expect("rule", "amount > 0")` | **Warn** — keep the row, record the metric |
| `@dlt.expect_or_drop(...)` | **Drop** the bad row, keep the pipeline running |
| `@dlt.expect_or_fail(...)` | **Fail** the pipeline update |

Violations are tracked as metrics you can monitor over time — turning [data quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) from a hope into an enforced, observable part of the pipeline.

---

## Advantages

- **Less code, fewer bugs** — no hand-written orchestration, incremental logic, or dependency wiring.
- **Built-in data quality** — expectations enforce and measure quality inline.
- **Automatic DAG & incremental processing** — DLT computes order and processes only new data.
- **Auto-recovery & retries** — managed error handling and restart from checkpoints.
- **Batch + streaming unified** — streaming tables and materialized views in one framework.
- **Lineage & observability** — the pipeline graph, metrics, and data quality visible in one UI.
- **Auto-managed infrastructure** — DLT provisions and scales compute for you.

## Disadvantages

- **Databricks-only** — a proprietary framework; logic isn't portable to plain Spark elsewhere.
- **Less low-level control** — the abstraction can fight you on unusual patterns.
- **Cost model** — managed convenience has its own DBU pricing; understand it before scaling.
- **Learning curve** — decorators, streaming tables vs materialized views, and pipeline settings are new concepts.

---

## Azure Usage

- Runs as a **pipeline** in the Databricks workspace, often triggered as a task inside a [Job](04_Notebooks_Repos_and_Jobs.md) or by **Auto Loader** file arrival ([next note](09_Auto_Loader_and_Ingestion.md)).
- Writes governed Delta tables under **Unity Catalog** ([04](06_Unity_Catalog.md)).
- Common shape: ADF or Auto Loader lands files → DLT builds Bronze/Silver/Gold with expectations → Power BI reads Gold.

---

## Real World Example

An IoT team ingests sensor files that occasionally arrive corrupt (missing readings, negative temperatures). Their old hand-built pipeline silently loaded the bad rows, and dashboards showed impossible values until someone noticed days later. Rebuilt in DLT: the Bronze streaming table ingests raw files via Auto Loader; the Silver table carries `@dlt.expect_or_drop("sane_temp", "temp_c BETWEEN -50 AND 80")`, so corrupt readings are dropped and *counted*; Gold aggregates the clean data. Now bad data is quarantined automatically, the drop rate is a monitored metric that alerts when a sensor misbehaves, and the whole Bronze→Silver→Gold graph — with row counts and quality stats — is visible in one pipeline UI.

---
---

# Part 2 — Advanced

## Streaming tables vs materialized views

- **Streaming table** — ingests *append-only, incremental* data (each new file/record processed once). Ideal for Bronze ingestion and append flows.
- **Materialized view** — the *full result* of a query, recomputed (incrementally where possible) when inputs change. Ideal for Silver/Gold aggregates that must reflect updates/deletes.

Choosing correctly per layer is the main DLT design skill: Bronze usually streaming tables; Gold aggregates often materialized views.

## CDC with `APPLY CHANGES INTO`

DLT has first-class [Change Data Capture](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md): `APPLY CHANGES INTO` (a.k.a. `AUTO CDC`) applies inserts/updates/deletes from a change feed and handles out-of-order events and [SCD Type 1 or 2](../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) — replacing a hand-written, error-prone `MERGE` with a declarative statement.

## Pipeline modes & development

- **Triggered** — runs once to update all tables, then stops (batch-style, cheaper).
- **Continuous** — keeps running for low-latency streaming.
- **Development vs production mode** — dev reuses the cluster and doesn't retry (fast iteration); production uses fresh compute with full retries.

## DLT vs Jobs vs Auto Loader — how they fit

They're complementary, not competing: **Auto Loader** *ingests* files incrementally, often *inside* a DLT streaming table; **DLT** *builds and maintains* the medallion with quality rules; **Jobs/Workflows** can *schedule/trigger* a DLT pipeline alongside non-DLT tasks. A common stack is Job → triggers → DLT pipeline (using Auto Loader) → UC tables.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## DLT trades control for correctness — know when that's the right trade

DLT shines for **standard medallion pipelines** where you want quality enforcement, incremental processing, and recovery *without* hand-rolling them — that's most pipelines, so it's a strong default. It fights you on highly custom orchestration, exotic sinks, or logic that doesn't fit the "each table is a function of upstream tables" model. The senior call: use DLT for the 80% of conventional ELT, drop to Jobs + hand-written Spark for the genuinely bespoke 20% — and don't contort DLT to force-fit the exceptions.

## Expectations are a contract, and drop rates are an SLO

The real power isn't dropping bad rows — it's that the **drop/violation rate becomes a monitored metric**. A Silver table quietly dropping 3% then 15% of rows signals an upstream break *before* the dashboard lies. Treat expectation metrics like SLOs: alert on them, trend them, and make a rising drop rate a page, not a surprise discovered in a meeting ([data quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md)).

## Streaming-table semantics bite the unwary

A DLT streaming table processes each input **once** — reprocessing history or changing upstream logic doesn't retroactively reprocess already-ingested data without a **full refresh**. Engineers expecting a materialized-view-style recompute get confused when a Bronze fix doesn't propagate. Know which of your tables are append-only streams vs recomputed views, and reach for full refresh deliberately.

## Field-tested gotchas

- **Wrong table type** — using a streaming table where you needed a recomputing materialized view (or vice versa), causing "why didn't my update show up?".
- **`expect` when you meant `expect_or_drop`** — warn-only lets bad rows through; pick the behaviour deliberately.
- **Ignoring expectation metrics** — the feature's value is monitoring them, not just setting them.
- **Forcing bespoke orchestration into DLT** — some pipelines belong in Jobs + Spark.
- **Forgetting full refresh** — after a logic change, streaming tables may need one to reprocess history.

## Interview-grade Q&A

- *What is DLT / Delta Live Tables?* A declarative pipeline framework: you define each table and its quality rules; DLT builds the DAG, processes incrementally, manages compute, enforces expectations, and handles recovery.
- *Declarative vs imperative here?* Imperative = you write each step and its orchestration; declarative = you declare the target tables and DLT derives order, incremental logic, and error handling.
- *What are expectations?* Inline data-quality rules — `expect` (warn), `expect_or_drop` (drop bad rows), `expect_or_fail` (fail the run) — tracked as monitorable metrics.
- *Streaming table vs materialized view?* Streaming table = append-only incremental ingest, each record once; materialized view = full query result recomputed (incrementally) when inputs change.
- *How does DLT do CDC?* `APPLY CHANGES INTO` applies a change feed with out-of-order handling and SCD Type 1/2, replacing hand-written MERGE.

---

## Related Notes

- **Prev:** [Unity Catalog](06_Unity_Catalog.md) · **Next:** [Auto Loader & Ingestion](09_Auto_Loader_and_Ingestion.md)
- **Medallion:** [Lakehouse Architecture](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · **Quality:** [Data Quality Fundamentals](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) · **CDC:** [Change Data Capture](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)
- **Cert:** [Delta Live Tables](../Certifications/Databricks_Data_Engineer_Associate/08_Delta_Live_Tables.md)

---

## Further Learning — Docs & Videos

**Documentation**
- DLT / Lakeflow Declarative Pipelines: https://learn.microsoft.com/en-us/azure/databricks/dlt/
- DLT expectations: https://learn.microsoft.com/en-us/azure/databricks/dlt/expectations

**Videos**
- Delta Live Tables explained: https://www.youtube.com/results?search_query=delta+live+tables+explained
- DLT expectations data quality: https://www.youtube.com/results?search_query=delta+live+tables+expectations
