# Azure Synapse Analytics

## What is it?

**Azure Synapse Analytics** is a **unified analytics platform** that brings together, in one workspace, the pieces a data team used to buy separately: a **data warehouse** (SQL pools), a **big-data engine** ([Spark](../03_Programming/PySpark/00_PySpark_Learning_Path.md) pools), **data integration** (pipelines — essentially [Azure Data Factory](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) built in), and a query-over-the-lake engine — all managed from a single UI called **Synapse Studio**.

It was Microsoft's flagship analytics platform (the evolution of Azure SQL Data Warehouse) and remains widely deployed — though for *new* builds Microsoft now steers customers to [Microsoft Fabric](03_Microsoft_Fabric.md).

In one line: **Synapse = data warehouse + Spark + data pipelines + lake querying, unified in one workspace.**

---

## Analogy: a single workshop with every tool

Before Synapse, doing analytics was like driving between separate specialist shops — one place to weld (warehouse), another to cut wood (Spark), another to paint (pipelines) — each with its own key, its own paperwork, its own bill. **Synapse is one big workshop with every station under one roof**: the warehouse bench, the Spark bench, the pipeline bench, all sharing the same materials store (your [data lake](../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md)) and one door key (one workspace, one security model). You walk between stations instead of driving across town.

---

## The four engines inside Synapse

```
                 ┌──────────── Synapse Studio (one UI) ────────────┐
                 │                                                  │
 Dedicated SQL Pool     Serverless SQL Pool     Spark Pool     Pipelines
 (provisioned MPP        (pay-per-TB query        (Apache        (ADF-style
  data warehouse)         over the lake)           Spark)         orchestration)
                 │                                                  │
                 └────────────► ADLS Gen2 (the shared data lake) ◄──┘
```

| Engine | What it is | Use for |
|---|---|---|
| **Dedicated SQL pool** | Provisioned **MPP** data warehouse (formerly SQL DW) | Large, predictable BI/warehouse workloads — see [02](02_Dedicated_vs_Serverless_SQL_Pools.md) |
| **Serverless SQL pool** | Pay-per-query T-SQL over files in the lake | Ad-hoc exploration, logical warehouse, no provisioning — see [02](02_Dedicated_vs_Serverless_SQL_Pools.md) |
| **Apache Spark pool** | Managed Spark clusters | Data engineering, ML, big-data transforms |
| **Pipelines** | The ADF engine embedded | Ingestion & orchestration |

The key idea: **all four read/write the same ADLS lake**, so you pick the right engine per task without copying data between silos.

---

## Advantages

- **One workspace** — warehouse, Spark, and pipelines under a single UI and security model.
- **Choice of engine per workload** — provisioned warehouse *or* serverless SQL *or* Spark, same data.
- **Serverless SQL over the lake** — query Parquet/CSV/JSON/Delta with T-SQL, no infrastructure, pay per TB scanned.
- **Powerful MPP warehouse** — dedicated pools scale to serious data-warehouse workloads.
- **Built-in integration** — ADF pipelines, Synapse Link (near-real-time HTAP from operational stores), Power BI integration.
- **Deep Azure security** — Entra ID, managed identities, VNet, Key Vault.

## Disadvantages

- **Being superseded by Fabric** — new investment is going to Fabric; a green-field build today should seriously consider Fabric or Databricks.
- **Dedicated pool cost** — a provisioned warehouse bills while it's on (pause it when idle).
- **Spark isn't as advanced as Databricks** — Synapse Spark trails Databricks on performance features, Delta tooling, and ecosystem.
- **Two SQL engines confuse newcomers** — dedicated vs serverless have very different models and limits.

---

## Azure Usage

A common Synapse-centred architecture:

```
Sources → Synapse Pipelines (ingest) → ADLS (bronze/silver, Parquet/Delta)
        → Synapse Spark (transform)   → Dedicated SQL pool (gold star schema)
        → Power BI (dashboards)
Serverless SQL pool: ad-hoc T-SQL over any lake file, any time
Synapse Link: near-real-time analytics on Cosmos DB / SQL without ETL
```

- **Synapse Link** provides **HTAP** — it replicates operational data (Cosmos DB, Azure SQL) into an analytical store automatically, so you analyze fresh data without building [CDC](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) pipelines yourself.

---

## Real World Example

A retailer runs its enterprise BI on a Synapse **dedicated SQL pool** — a star-schema warehouse feeding hundreds of Power BI reports. Raw data lands in ADLS via **Synapse Pipelines**; a **Spark pool** cleans and conforms it; the modeled gold tables load into the dedicated pool for fast, high-concurrency reporting. Meanwhile, a data analyst who just wants to peek at last week's raw log files runs **serverless SQL pool** queries directly over the Parquet in the lake — no pool to provision, billed only for the terabytes scanned. All of it lives in one Synapse workspace with one set of permissions, and the dedicated pool is **paused overnight** to save cost.

---
---

# Part 2 — Advanced

## Dedicated vs serverless — the fork that matters most

This is the defining Synapse decision, covered in depth in [02](02_Dedicated_vs_Serverless_SQL_Pools.md):
- **Dedicated SQL pool** — you *provision* compute (measured in **DWUs**), data is *loaded and stored* in the pool's MPP-distributed tables. Fast, high-concurrency, predictable — but always-on cost and a loading step.
- **Serverless SQL pool** — no provisioning, no storage; you query files *in place* in the lake and pay **per TB scanned**. Perfect for exploration and a "logical" warehouse over the lake, but not for high-concurrency, low-latency BI.

Rule of thumb: **serverless to explore the lake, dedicated to serve governed BI at scale.**

## Synapse Spark vs Databricks

Synapse Spark pools run Apache Spark integrated into the workspace — convenient if you're already all-in on Synapse. But [Databricks](../08_Databricks/01_What_is_Databricks.md) generally leads on Spark performance (Photon), Delta features (liquid clustering, deletion vectors), governance (Unity Catalog), and ecosystem (DLT, MLflow). Teams doing serious data engineering / ML often pair **Databricks for Spark** with **Synapse for the SQL warehouse**, or move to Fabric/Databricks entirely.

## Synapse Pipelines = ADF

Synapse Pipelines are the **same engine as Azure Data Factory**, embedded in the workspace — same activities, linked services, integration runtimes, and mapping data flows ([ADF](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md)). The practical difference is packaging: standalone ADF vs pipelines living inside Synapse alongside the SQL and Spark engines. Skills transfer directly between them.

## Synapse Link — HTAP without ETL

Synapse Link creates an automatically-synced **analytical copy** of operational data (Cosmos DB, Azure SQL, Dataverse) so you can run analytics on near-real-time data without building extraction pipelines or hammering the transactional store — Microsoft's HTAP (Hybrid Transactional/Analytical Processing) play.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The honest 2025+ positioning: Synapse is legacy-forward, not future-forward

A senior engineer states this plainly in interviews: **Synapse is mature and everywhere, but Microsoft's forward investment is in [Fabric](03_Microsoft_Fabric.md).** Fabric's warehouse and Spark are the spiritual successors to Synapse's, on top of OneLake. So: keep and optimize existing Synapse estates, but for green-field, weigh **Fabric** (Microsoft-native SaaS) or **Databricks** (best lakehouse) rather than starting new on dedicated SQL pools. Knowing *where a platform is in its lifecycle* is a senior signal.

## Pause the dedicated pool — it's the biggest cost lever

A dedicated SQL pool bills for its provisioned DWUs whenever it's *online*, regardless of query load. The single biggest Synapse cost mistake is leaving it running 24/7 for a workload that's queried during business hours. Pause it on a schedule (storage persists, compute stops), scale DWUs to the workload, and use serverless for the ad-hoc queries that don't justify keeping the pool warm.

## Choose the engine per workload, not per platform loyalty

The Synapse trap is doing everything in the dedicated pool because it's there — running exploratory scans that belong in serverless (cheaper), or heavy transforms that belong in Spark (more flexible). The pro routes each workload to its best engine: serverless for explore, Spark for transform, dedicated for governed high-concurrency serving — the same "right tool per job" discipline as the [lake/warehouse/lakehouse](../05_Storage_and_Formats/Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) choice.

## Field-tested gotchas

- **Dedicated pool left online 24/7** — the classic runaway bill; pause when idle.
- **Serverless for high-concurrency BI** — wrong tool; per-query scan cost and latency don't suit dashboards.
- **Betting a green-field build on dedicated pools in 2025+** — consider Fabric/Databricks first.
- **Expecting Databricks-grade Spark** — Synapse Spark is capable but trails; don't assume feature parity.
- **Confusing the two SQL engines** — dedicated (provisioned, stored, distributed) and serverless (pay-per-scan, in-lake) have different limits, syntax quirks, and use cases.

## Interview-grade Q&A

- *What is Azure Synapse Analytics?* A unified analytics platform combining a dedicated MPP SQL warehouse, a serverless SQL engine over the lake, Apache Spark pools, and ADF-style pipelines in one workspace over ADLS.
- *Dedicated vs serverless SQL pool?* Dedicated is provisioned, stores data in MPP-distributed tables, and serves high-concurrency BI (always-on cost); serverless has no provisioning/storage and queries lake files per-TB-scanned (ideal for ad-hoc/logical warehouse).
- *How do Synapse Pipelines relate to ADF?* They're the same engine embedded in Synapse — same activities, linked services, and data flows; skills transfer directly.
- *What is Synapse Link?* HTAP — an auto-synced analytical copy of operational data (Cosmos DB/SQL) for near-real-time analytics without building ETL.
- *Synapse or Fabric for a new project?* Synapse is mature but being superseded by Fabric; for green-field, weigh Fabric (Microsoft SaaS) or Databricks — reserve Synapse for existing estates.

---

## Related Notes

- **Next:** [Dedicated vs Serverless SQL Pools](02_Dedicated_vs_Serverless_SQL_Pools.md) · [Microsoft Fabric](03_Microsoft_Fabric.md) · [Decision framework](04_Synapse_vs_Fabric_vs_Databricks.md)
- **Foundations:** [SQL Warehouse](../02_Databases/SQL/13_SQL_Warehouse.md) · [Data Warehouse Fundamentals](../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md)
- **Related engines:** [Azure Data Factory](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) · [Databricks](../08_Databricks/01_What_is_Databricks.md)
- **Interview:** [Synapse Q&A](../Job%20Interviews/Azure%20Synapse/Synapse%20Interview%20Questions.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Azure Synapse Analytics: https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is
- Synapse SQL architecture: https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/overview-architecture

**Videos**
- Azure Synapse Analytics explained: https://www.youtube.com/results?search_query=azure+synapse+analytics+explained
- Synapse dedicated vs serverless: https://www.youtube.com/results?search_query=synapse+dedicated+vs+serverless+sql+pool
