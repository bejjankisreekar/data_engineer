# Lakehouse Architecture

## What is it?

A **lakehouse** is a data architecture that combines the **cheap, flexible storage of a [data lake](../Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)** with the **transactions, governance, and BI performance of a [data warehouse](../../02_Databases/SQL/13_SQL_Warehouse.md)** — in *one* system, on *one* copy of the data.

It's made possible by an open **table format** like [Delta Lake](01_Delta_Lake.md): once your lake files behave like transactional tables (ACID, updates, time travel), you no longer need a separate warehouse to get warehouse behavior. Store once in the lake; serve engineering, BI, streaming, and ML from the same tables.

In one line: **lakehouse = data lake storage + [Delta](01_Delta_Lake.md) table format + a SQL engine & catalog on top = warehouse behavior at lake economics.**

---

## Analogy: the warehouse *and* the loading dock, merged

In the older world (recap from [Data Lake vs Warehouse](../Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)):

- The **data lake** is the loading dock — everything dumped in raw, cheap, unsorted.
- The **data warehouse** is the tidy store shelves — cleaned, organized, ready for shoppers (analysts).

The problem: you kept **two buildings** and paid a crew to constantly copy goods from the dock to the shelves — two copies of everything, always slightly out of sync.

The **lakehouse** is a single building where the shelving system was installed *directly onto the loading dock*. Raw deliveries still arrive as-is, but you organize them **in place** — no second building, no copying crew, **one copy of the truth** that's both the raw store and the analyst-ready shelf.

---

## Why it exists: killing the two-copy problem

| Old two-system world | Lakehouse |
|---|---|
| Lake for raw + ML, warehouse for BI | One store serves both |
| **Two copies** of data, always syncing | **One copy**, many engines |
| A pipeline forever moving lake → warehouse | No copy pipeline to maintain |
| "Which number is right?" reconciliation meetings | Single source of truth |
| Warehouse-native, often proprietary storage | Open format (Delta/Parquet) in your storage |

---

## The Medallion Architecture (Bronze → Silver → Gold)

The standard way to organize a lakehouse is **three layers of Delta tables**, each one cleaner than the last:

| Layer | Contains | Consumers |
|---|---|---|
| 🥉 **Bronze** | Raw ingested data, untouched, with source + load timestamp | Data engineers, reprocessing |
| 🥈 **Silver** | Cleaned, typed, deduplicated, business-key-joined | Engineers, data scientists |
| 🥇 **Gold** | [Dimensional models](../../02_Databases/Data_Modeling/03_Dimensional_Modeling.md), KPIs, aggregates | BI analysts, dashboards, ML features |

Each layer is a set of **Delta tables**; each hop is a transformation (often incremental via [Change Data Feed](02_Delta_Table.md)). This is [ELT](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) done inside the lake.

> **Deep-dive:** the medallion pattern has its own dedicated note — **[Medallion Architecture (Bronze → Silver → Gold)](04_Medallion_Architecture.md)** — with per-layer rules, transformation code, batch-vs-streaming, anti-patterns, and interview Q&A. The rest of *this* note covers the lakehouse it lives in.

---

## Advantages

- **One copy of data** — no lake↔warehouse duplication or sync pipelines.
- **All workloads on one platform** — BI, SQL, streaming, data science, and ML read the same tables.
- **Open format** — Delta/Parquet in *your* object storage; low lock-in, many engines.
- **Lake economics** — cheap object storage, not premium warehouse storage.
- **Transactions & governance on the lake** — ACID, schema enforcement, lineage, fine-grained access (Unity Catalog).

## Disadvantages

- **Newer discipline** — teams used to pure SQL warehouses face a learning curve (Spark, files, maintenance).
- **You own the maintenance** — `OPTIMIZE`/`VACUUM`, small-file management, clustering are your job.
- **BI concurrency** — a mature warehouse can still beat a lakehouse on very high-concurrency small-query BI (narrowing fast with Photon/serverless SQL & caching).
- **Governance doesn't come free** — without a catalog and layer contracts, a lakehouse degrades into a [data swamp](../Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md).

---

## Azure Usage

| Concept | Azure implementation |
|---|---|
| Lakehouse platform | **Azure Databricks** (Delta + Unity Catalog + Databricks SQL) |
| Storage layer | **ADLS Gen2** — where Bronze/Silver/Gold Delta files live |
| Unified SaaS lakehouse | **Microsoft Fabric** — OneLake stores everything as Delta; Lakehouse & Warehouse items share it |
| Governance / catalog | **Unity Catalog** (Databricks), **Microsoft Purview** ([governance](../../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)) |
| BI on top | **Power BI** via SQL endpoint / Direct Lake |

---

## Real World Example

A logistics company used to run a data lake (for GPS pings, scanned documents, and ML training data) *and* a separate Synapse warehouse (for finance and ops dashboards), with a nightly pipeline copying curated data from the lake into the warehouse. Reports were always a day behind, and the two systems disagreed often enough that a standing weekly meeting existed just to reconcile numbers.

They moved to a Databricks lakehouse: raw pings and documents land in **Bronze**, a streaming job cleans and joins them into **Silver**, and **Gold** holds the star-schema tables Power BI reads directly via the SQL endpoint. Data scientists train delivery-time models on the *same* Silver tables the dashboards trust. One copy, no copy-pipeline, no reconciliation meeting — and dashboards update within minutes instead of a day.

---
---

# Part 2 — Advanced

## Where the lakehouse sits in the big-data timeline

The lakehouse is the **fourth era** ([full timeline](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)): databases → warehouses → Hadoop/data lakes → lakehouse. Each fixed the prior era's pain: warehouses gave lakes analytics but were rigid and proprietary; lakes gave scale and openness but lost transactions and governance; the lakehouse keeps the lake's openness and *adds back* the warehouse's guarantees via open table formats.

## The three pillars that make it work

1. **Open table format** ([Delta Lake](01_Delta_Lake.md)) — ACID, time travel, schema enforcement on plain files.
2. **A performant query engine** — Spark for engineering; a vectorized SQL engine (Databricks Photon, Fabric) for interactive BI speed on those files.
3. **A governance catalog** — Unity Catalog / Purview for one permission model, lineage, and discovery across all engines ([governance](../../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)).

Miss any pillar and you don't have a lakehouse — you have a lake with extra steps.

## Medallion as contracts, not just folders

The power of Bronze/Silver/Gold is that each boundary is a **contract**:

- **Bronze** promises "everything we received, unchanged" — the replay source when logic changes downstream.
- **Silver** promises "clean, deduplicated, conformed" — the enterprise view engineers and scientists share.
- **Gold** promises "business-defined, report-ready" — the numbers finance signs off on.

Pointing BI at Silver "just for now" quietly breaks the Gold contract and puts dashboard load on engineering tables. Layers are boundaries to *enforce*, not just a naming convention.

## Streaming and batch on the same tables

Because a Delta table is both a stream sink and a stream source, the *same* medallion pipeline runs in batch or streaming with little change — Bronze can be a streaming ingest, Silver a streaming transform, Gold a micro-batch aggregate ([Structured Streaming](../../03_Programming/PySpark/13_Structured_Streaming.md)). This "one pipeline, two speeds" is a defining lakehouse advantage over the old batch-only warehouse.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Lakehouse doesn't delete warehouse discipline

The seductive misread is "lakehouse means we skip modeling and governance." The storage engines merged; the *disciplines did not*. [Dimensional modeling](../../02_Databases/Data_Modeling/03_Dimensional_Modeling.md), quality gates, a semantic layer, and access governance still decide whether the project succeeds. A lakehouse without Gold-layer modeling and a catalog is just a faster way to build a swamp.

## Open format is the real strategic bet

The durable reason to choose a lakehouse is **optionality**: your data sits as open Delta/Parquet in storage you control, so you can point Spark, Trino, DuckDB, Fabric, or next year's engine at it without a migration. Evaluate every platform with two questions: *does it read/write open formats in **my** storage?* and *whose catalog governs it?* Those answers predict lock-in far better than any feature checklist ([SaaS/PaaS lock-in](../../04_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md)).

## Where a classic warehouse still wins

Be honest in interviews: if the org is SQL-only, has a mature BI estate, runs high-concurrency small queries, and has no ML/streaming pressure, a traditional warehouse may still be the right call — the migration cost can exceed the duplication cost the lakehouse would remove. The lakehouse is the default for *new, mixed-workload* platforms, not a mandate to rip out everything.

## The cost model is compute + people, not storage

Object storage is cheap (~$20/TB/month); the real spend is **compute** (idle Spark clusters, an always-on oversized SQL endpoint) and **people** (the team maintaining duplicate pipelines). The lakehouse's biggest saving is deleting the lake→warehouse copy pipeline and its reconciliation overhead — price the *copies and pipelines*, not just the storage.

## Field-tested gotchas

- **"Lakehouse" with no catalog or contracts is a swamp** — table format alone isn't governance.
- **BI pointed at Silver** creates permanent load on engineering tables and breaks the Gold contract.
- **Metric drift** — the same KPI computed in Spark (Gold) and in a BI tool's own DAX will disagree (timezones, nulls, float summation); a single semantic layer beats reconciliation heroics ([metric governance](../../02_Databases/SQL/13_SQL_Warehouse.md)).
- **Skipping Bronze** ("we'll transform on ingest") removes your replay source — when logic changes, you can't reprocess history.
- **Under-maintained Delta tables** (no `OPTIMIZE`/clustering) make BI on the lakehouse feel slow and "prove" the warehouse was better — it's a maintenance gap, not an architecture flaw.

## Interview-grade Q&A

- *What is a lakehouse in one sentence?* An architecture that puts a transactional table format (Delta) and a SQL engine on top of cheap open lake storage, so one copy of data serves BI, streaming, and ML — warehouse behavior at lake economics.
- *What are the medallion layers and why?* Bronze (raw, replay source), Silver (clean, conformed enterprise view), Gold (business-modeled, report-ready) — progressive refinement with each boundary as a contract.
- *What three things make a lakehouse possible?* An open table format (ACID/time travel), a fast query engine, and a governance catalog.
- *Lakehouse vs warehouse — when do you still pick the warehouse?* SQL-only shop, mature BI, high-concurrency small queries, no ML/streaming — migration cost beats the duplication it would save.
- *Biggest risk of a lakehouse?* Skipping governance and modeling and letting it rot into a data swamp — the storage merged, but the discipline didn't.

---

## Related Notes

- **Prev:** [Delta Lake](01_Delta_Lake.md) · [Delta Table](02_Delta_Table.md) — the format and tables the lakehouse is built from.
- **Next:** [Medallion Architecture](04_Medallion_Architecture.md) — the Bronze/Silver/Gold layering, in depth.
- **Foundations:** [Data Lake vs Warehouse vs Database](../Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) · [Big Data Evolution Timeline](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)
- **Modeling the Gold layer:** [Dimensional Modeling](../../02_Databases/Data_Modeling/03_Dimensional_Modeling.md) · [Data Warehouse Fundamentals](../../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md)
- **Building it:** [ETL vs ELT](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) · [Structured Streaming](../../03_Programming/PySpark/13_Structured_Streaming.md) · [Data Governance](../../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)

---

## Further Learning — Docs & Videos

**Documentation**
- What is a data lakehouse? (Databricks): https://www.databricks.com/glossary/data-lakehouse
- Medallion architecture: https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion
- Microsoft Fabric lakehouse: https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview
- The original lakehouse paper (CIDR 2021): https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf

**Videos**
- Data lakehouse explained: https://www.youtube.com/results?search_query=data+lakehouse+explained
- Medallion architecture (bronze silver gold): https://www.youtube.com/results?search_query=medallion+architecture+bronze+silver+gold
