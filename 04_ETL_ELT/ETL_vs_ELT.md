# ETL vs ELT

## What problem are we solving?

Data rarely starts out where it needs to end up, or in the shape it needs to be in. A sales system might record amounts in cents, in five different regional formats, across three different databases — but a business report needs one clean, consistent "Total Sales" number. Getting from messy source data to a clean, usable result requires three steps, always in this order of *concept*, if not always execution:

1. **Extract** — pull the data out of its source (a database, an API, a file)
2. **Transform** — clean it, reshape it, calculate new values, fix errors
3. **Load** — write the result into its final destination (usually a [data warehouse](../01_SQL/SQL_Warehouse.md))

The only real difference between ETL and ELT is **where** step 2 happens — before loading, or after.

---

## ETL: Extract, Transform, Load

```
Source  →  Extract  →  Transform (on a separate processing server)  →  Load  →  Warehouse
```

Data is cleaned and reshaped *before* it ever reaches the warehouse. The warehouse only ever receives finished, ready-to-use data.

Analogy: a caterer prepping ingredients (washing, chopping, cooking) in their own kitchen *before* driving the finished dishes to the event venue. The venue only ever sees the finished meal.

**Why choose ETL:**
- The destination warehouse has limited processing power
- You need to filter out sensitive data (e.g. remove personal information) before it's ever stored in the destination
- The transformation logic is well-established and doesn't change often

---

## ELT: Extract, Load, Transform

```
Source  →  Extract  →  Load (raw)  →  Warehouse  →  Transform (using the warehouse's own power)
```

Raw data is loaded into the destination *first*, and transformed there afterward, using the destination's own processing power.

Analogy: the caterer drives raw, unprepped ingredients straight to the event venue, which has its own large, powerful kitchen — chopping and cooking happen on-site, right before serving.

**Why choose ELT:**
- Modern cloud warehouses (Synapse, Snowflake, BigQuery) have enormous processing power to spare
- You want to keep a copy of the raw, untransformed data available for later (in case the cleaning logic needs to change)
- Faster to get data "in" and iterate on the transformation logic afterward

---

## Side-by-Side

| | ETL | ELT |
|---|---|---|
| Transform happens | Before loading | After loading |
| Needs separate processing step | Yes | No — uses destination's own power |
| Raw data kept? | Often discarded | Usually kept alongside transformed data |
| Common era | Traditional on-premises warehouses | Modern cloud warehouses and data lakes |

---

## Azure Usage

[Azure Data Factory](Azure_Data_Factory.md) can build either pattern:
- **ETL**: use Data Factory's Mapping Data Flows (or Azure Databricks) to transform data mid-pipeline, before writing to Synapse.
- **ELT**: use Data Factory purely to copy raw data into a [Data Lake](../03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md) or Synapse, then run transformation queries inside Synapse itself.

Most new Azure projects lean toward ELT, because cloud warehouses like Synapse are built to handle heavy transformation workloads efficiently.

---

## Real World Example

A retail chain collects sales data from 500 stores nightly.

- Under **ETL**, a separate server cleans and standardizes every store's data (fixing currency formats, removing test transactions) before any of it touches the warehouse.
- Under **ELT**, all 500 stores' raw data is loaded into the warehouse first, and a set of scheduled queries inside the warehouse itself does the cleaning — keeping the original raw records around in case a mistake in the cleaning logic needs to be corrected later.

---
---

# Part 2 — Advanced

## The medallion architecture — ELT with named quality gates

Modern ELT on the lakehouse formalizes "load raw, refine in place" into layers with contracts ([ADLS zone layout](../03_Data_Storage/Azure_Data_Lake_Storage.md)):

```
BRONZE  as-arrived, immutable, source-native formats + ingest metadata
   │    (contract: nothing is ever lost; re-processing is always possible)
SILVER  typed Delta, deduped, conformed keys, quality-tested
   │    (contract: one clean row per business fact; safe to build on)
GOLD    aggregated, dimensionally modeled, business definitions applied
        (contract: numbers match the business's definitions — BI-ready)
```

Each arrow is an idempotent, tested transformation ([star schema loading](../01_SQL/SQL_Warehouse.md) happens bronze→gold). The point of naming layers: **every dataset has exactly one quality promise**, so consumers know what they're standing on.

## Incremental loading — the part that separates toys from production

Full reloads stop scaling fast. The incremental toolbox:

| Technique | How | Catches deletes? |
|---|---|---|
| **Watermark** | `WHERE modified_at > last_run_max` (store the watermark transactionally!) | ❌ |
| **CDC (log-based)** | Read the DB transaction log (Debezium, native CDC) → stream of I/U/D events | ✅ |
| **File-based** | Process only new files (Auto Loader/event triggers) | n/a |
| **Snapshot diff** | Full extract, EXCEPT vs previous ([EXCEPT](../01_SQL/SQL_DQL.md)) | ✅ (expensive) |

Then apply changes with **MERGE at the target** ([upserts](../01_SQL/SQL_DML.md)), and design for **late-arriving data** — events landing days late must merge into old partitions, not vanish.

## Orchestration concepts (whatever the tool)

A production pipeline is a **DAG of dependencies** with per-node retry policy, timeout, and alerting; runs are parameterized by *logical date* (backfills = re-running old dates — only safe because steps are [idempotent](../01_SQL/SQL_DML.md)); state ("what loaded through when") lives in a control table, not in someone's memory. Tools: [ADF](Azure_Data_Factory.md), Databricks Workflows, Airflow — same concepts, different skins. The transformation layer inside the warehouse increasingly belongs to **dbt**: SQL models in git, tests, docs, lineage — ELT's "T" industrialized.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Data quality as pipeline code, not hope

Every silver/gold transition runs assertions — and *fails loudly or quarantines* on breach:

- **Schema tests**: columns/types match contract (drift alert — [JSON drift](../02_File_formats/JSON.md)).
- **Integrity tests**: keys unique, no orphan foreign keys, row counts within expected bands ([aggregate instrumentation](../01_SQL/SQL_Aggregate_Functions.md)).
- **Business tests**: no negative quantities, dates within range, totals reconcile to source within tolerance.
- Framework examples: dbt tests, Delta constraints + DLT expectations, Great Expectations. The senior stance: **an untested pipeline doesn't "work," it just hasn't been caught** — and quality failures page the *producing* team, per the data contract.

## Streaming blurs ETL/ELT — and the batch mindset must go with it

With CDC → Event Hubs → Structured Streaming → Delta, "nightly load" becomes "continuous merge," and batch is just a bounded stream ([kappa's victory](../00_Fundamentals/Big_Data_Evolution_Timeline.md)). What changes in your head: watermarks become event-time watermarks (late-data bounds), idempotency becomes exactly-once sinks ([delivery semantics](../00_Fundamentals/Distributed_Computing.md)), and "the load finished" becomes freshness SLOs ("gold lags source by < 15 min"). The same medallion layers survive intact — they just update continuously.

## Choosing ETL vs ELT in 2026 — the honest decision

ELT won as the default (cheap elastic compute at the destination, raw retention, dbt ecosystem), but ETL survives in specific niches — and pros name them rather than tribalize:

- **PII/compliance**: mask/tokenize *before* the data lands anywhere broad-access ([GDPR pressure](../05_cloud/Public_Private_Hybrid_Cloud.md)) — a T-before-L step by law, effectively "EtLT."
- **Source-side reduction**: pushing filters/projections to the extract when moving everything is prohibitively expensive (huge on-prem → cloud links).
- **Real transformation ≠ location**: a Databricks job reading bronze and writing silver is "ELT" by letter, ETL by muscle — the letters matter less than *raw retention + idempotency + tests*, which is the actual modern doctrine.

## Field-tested gotchas

- Watermark stored before the load commits = data loss on crash; stored after = duplicates. Store it **in the same transaction/atomic commit** as the load.
- `modified_at` maintained by the *application* misses bulk fixes done directly in SQL — log-based CDC or periodic reconciliation sweeps catch the drift.
- Timezones in "daily" batches: define the day in *one* timezone everywhere, or store-close data lands in tomorrow's partition ([timestamp discipline](../01_SQL/SQL_Data_Types.md)).
- Backfills that replay months through a pipeline sized for one day: throttle, partition the backfill, and warn downstream — a backfill is a production event, not a rerun button.
- Distinguish **pipeline failure** (retry fixes it) from **data failure** (retry duplicates it) in alerting — treating both as "re-run" is how duplicate-day incidents happen.

## Interview-grade Q&A

- *ETL vs ELT — which and why?* ELT by default (cloud compute at destination, raw retention, iterate transforms); ETL where compliance or transfer economics force pre-load transformation.
- *Design an incremental load for a 2 TB orders table.* Log-based CDC (or indexed watermark) → bronze append → MERGE to silver by key with dedupe-window → tested gold aggregates; transactional watermark; late-data MERGE into old partitions.
- *What makes a pipeline production-grade?* Idempotent steps, quality gates, lineage/state tracking, alerting tied to contracts, backfill story — not just "it ran."
- *Where does dbt fit?* The T of ELT: versioned, tested SQL models inside the warehouse/lakehouse, replacing hand-managed transformation scripts.
