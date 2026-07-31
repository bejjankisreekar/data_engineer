# Microsoft Fabric

## What is it?

**Microsoft Fabric** is an **all-in-one SaaS analytics platform** that unifies everything a data team needs — data integration, data engineering (Spark), data warehousing, real-time analytics, data science, and **Power BI** — into a single product, built on top of one shared, Delta-native data lake called **OneLake**.

It's Microsoft's **next-generation, unified successor** to the separate-services world of [Synapse](01_Azure_Synapse_Analytics.md) + [ADF](../05_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) + Power BI. Where Synapse bundled engines into a workspace, Fabric goes further: it's fully **SaaS** (no infrastructure at all), everything writes to **one lake in [Delta](../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) format**, and it's billed as **one capacity**.

In one line: **Fabric = a single SaaS platform for all analytics workloads, on one Delta lake (OneLake), with Power BI built in.**

---

## Analogy: from a toolbox to an all-in-one appliance

[Synapse](01_Azure_Synapse_Analytics.md) was a **workshop with separate benches** you still had to set up and wire together. **Fabric is an all-in-one appliance** — think a single machine that ingests, transforms, warehouses, analyzes in real time, and visualizes, where every part automatically shares **one storage drawer** (OneLake). You don't assemble anything or manage the wiring; you switch between tasks and the data is simply *there*, in one place, in one format, for every tool. It's the "SaaS-ification" of the whole analytics stack.

---

## OneLake — the heart of Fabric

**OneLake** is the single, unified, organization-wide data lake — often described as **"OneDrive for data."** It's the feature everything else hangs off:

- **One lake for the whole tenant** — automatically provisioned, no storage accounts to create.
- **Delta/Parquet-native** — every Fabric engine reads and writes **open Delta** format, so there's genuinely **one copy** of data for all workloads ([lakehouse promise](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)).
- **Shortcuts** — reference data that lives elsewhere (ADLS, S3, another workspace) **without copying it** — it appears in OneLake as if local.
- **One security & governance layer** across all of it.

The payoff: the warehouse, the Spark lakehouse, and Power BI all point at the *same* Delta tables — no copies, no sync pipelines between engines.

---

## The Fabric workloads (experiences)

Fabric packages capabilities as **workloads**, all sharing OneLake:

| Workload | What it does | Cousin of |
|---|---|---|
| **Data Factory** | Ingestion & pipelines (+ Dataflows Gen2) | [Azure Data Factory](../05_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) |
| **Data Engineering** | Spark notebooks + **Lakehouse** items | [Databricks](../08_Databricks/01_What_is_Databricks.md) / Synapse Spark |
| **Data Warehouse** | Full T-SQL warehouse (Delta-backed) | Synapse dedicated pool |
| **Real-Time Intelligence** | Eventstream + Eventhouse/KQL | [Stream Analytics](../09_Streaming/04_Azure_Stream_Analytics.md) |
| **Data Science** | ML with notebooks + MLflow | Databricks ML |
| **Power BI** | Reports & dashboards, natively integrated | Power BI |
| **Databases** | Operational (SQL) databases in Fabric | Azure SQL |

---

## Lakehouse vs Warehouse items

Fabric offers two ways to hold tabular data, and choosing between them is a common question:

| | **Lakehouse** (item) | **Warehouse** (item) |
|---|---|---|
| Primary interface | Spark + SQL (read) | Full T-SQL (read **and** write) |
| Best for | Data engineering, Spark, files + tables | SQL-first teams, T-SQL DML, BI serving |
| Write with | Spark / notebooks | T-SQL (`INSERT`/`UPDATE`/`DELETE`) |
| Storage | Delta in OneLake | Delta in OneLake |

Both store **Delta in OneLake** — the difference is the *experience* and who writes to it (Spark engineers → Lakehouse; SQL developers → Warehouse). Because both are Delta, a Warehouse can query a Lakehouse's tables and vice versa.

---

## Direct Lake — the Power BI game-changer

Historically Power BI either **imported** data (fast but a copy that goes stale) or used **DirectQuery** (live but slower). **Direct Lake** is a third mode unique to Fabric: Power BI reads the **Delta files in OneLake directly** — giving import-like speed **with** live freshness and **no data copy or refresh**. This is one of Fabric's headline advantages and a frequent talking point.

---

## Advantages

- **Truly unified** — every analytics workload in one SaaS product, one bill, one governance model.
- **OneLake = one copy** — all engines share open Delta; no copy pipelines between warehouse/lake/BI.
- **No infrastructure** — fully SaaS; no clusters, pools, or storage accounts to manage.
- **Direct Lake** — fast *and* fresh Power BI with no import/refresh.
- **Shortcuts** — use data in ADLS/S3/other workspaces without copying.
- **Deep Power BI integration** — the strongest BI story of any platform.

## Disadvantages

- **Newer / maturing** — younger than Synapse/Databricks; features and limits still evolving.
- **Capacity model** — one shared **capacity (F SKU)** for everything means noisy-neighbour and capacity-planning considerations.
- **Less open/portable than Databricks** — a Microsoft-tenant SaaS; OneLake is Delta (open) but the platform is Microsoft-bound.
- **Spark trails Databricks** — capable, but not yet at Databricks' performance/feature/ecosystem depth.

---

## Azure Usage

- **Capacities (F SKUs)** — Fabric is licensed as a capacity (e.g. F64) shared across all workloads in the tenant; you size and can pause/scale it. Power BI Premium capacities map into Fabric.
- **Billing model shift** — instead of per-service bills (ADF + Synapse + storage + Power BI), it's one capacity — simpler, but capacity management becomes the cost lever.
- **Governance** — integrates with **Microsoft Purview** for cataloging, lineage, and sensitivity across OneLake ([governance](../05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)).

---

## Real World Example

A mid-size insurer wants analytics without a platform team. In **Fabric**, a **Data Factory** pipeline ingests policy and claims data into a **Lakehouse** in OneLake (Delta). Data engineers transform it with **Spark notebooks** into clean silver/gold tables; a **Warehouse** item exposes those same Delta tables to SQL developers who build marts with T-SQL. Analysts build **Power BI** reports in **Direct Lake** mode — reading the gold Delta straight from OneLake, always current, no import refresh. A **Real-Time Intelligence** eventstream feeds a live claims-volume dashboard. A **shortcut** surfaces a partner's data sitting in ADLS without copying it. It's all one SaaS product, one OneLake copy of the data, and one capacity bill — with zero infrastructure to manage.

---
---

# Part 2 — Advanced

## "One copy" is the real architectural shift

Fabric's deepest idea is that **OneLake holds one Delta copy that every engine reads** — the [lakehouse "one copy, many engines"](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) principle made the *default*, not something you assemble. A table written by Spark in a Lakehouse is immediately queryable by the Warehouse's T-SQL engine and readable by Power BI Direct Lake — no ETL between them. This is what removes the copy-pipeline tax that defined the Synapse-era architecture.

## Shortcuts vs copying

Shortcuts let OneLake **reference** data in other locations (ADLS Gen2, Amazon S3, Google Cloud Storage, other Fabric workspaces) so it appears local without duplication. This is Fabric's answer to data silos: virtualize instead of copy. It's conceptually similar to [Delta Sharing / external locations](../08_Databricks/04_Unity_Catalog.md) — the principle of "govern and access in place" rather than move.

## Fabric vs Synapse — the lineage

Fabric's engines are the **evolution** of Synapse's: Fabric Warehouse ≈ a re-architected Synapse SQL warehouse (now Delta-backed on OneLake), Fabric Data Engineering ≈ Synapse Spark, Fabric Data Factory ≈ ADF/Synapse pipelines, Fabric Real-Time Intelligence ≈ Stream Analytics. The big changes: **SaaS** (no provisioning), **OneLake** (one open-Delta store), and **Power BI fused in**. If you know Synapse, you can map every Fabric workload to a Synapse ancestor.

## The capacity model

Everything in Fabric draws from a shared **capacity** measured in Capacity Units. This simplifies billing but introduces **smoothing/bursting** and noisy-neighbour dynamics — a heavy Spark job and interactive Power BI queries compete for the same capacity. Capacity sizing and monitoring (the Fabric Capacity Metrics app) become the cost/performance discipline, replacing per-service DWU/DBU/SU tuning.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Fabric's bet: SaaS simplicity for the Microsoft-centric org

Fabric's strategic pitch is **radical simplification** for organizations already living in Microsoft/Power BI — one product, one lake, one bill, no infrastructure. The senior read: Fabric is compelling when the org is **Power BI-heavy, wants minimal platform ops, and values integration over best-of-breed control**. It's a weaker fit when you need Databricks-grade Spark/ML, multi-cloud portability, or fine-grained infrastructure control. "Is this org optimizing for *simplicity/integration* or for *power/openness*?" is the question that predicts Fabric vs Databricks.

## OneLake is open even though Fabric is SaaS

A subtle but important point for lock-in discussions: because OneLake stores **open Delta/Parquet**, your data isn't trapped in a proprietary format even though the platform is Microsoft SaaS — other engines (including Databricks, via shortcuts/Delta) can read it. The lock-in is in the *platform and tooling*, not the *data format*. This is a genuinely better position than closed warehouses, and worth stating precisely rather than dismissing Fabric as "locked in."

## Direct Lake has boundaries — know them

Direct Lake is powerful but "falls back" to DirectQuery under certain conditions (unsupported features, some data types, model size vs capacity limits), which quietly changes performance. A pro validates that a model actually *stays* in Direct Lake mode rather than assuming it, and lays out the OneLake Delta tables (well-sized files, proper types) so Direct Lake performs — the same file-hygiene discipline that matters everywhere in the lakehouse.

## Field-tested gotchas

- **Assuming Fabric is production-mature for every edge case** — it's newer; validate limits before betting a critical migration on it.
- **Capacity noisy-neighbour** — one heavy Spark/warehouse job throttling Power BI on the shared capacity; size and monitor capacity deliberately.
- **Expecting Databricks-grade Spark/ML** — Fabric Spark is capable but not at parity.
- **Direct Lake silently falling back to DirectQuery** — validate the mode; don't assume the fast path.
- **Lakehouse vs Warehouse confusion** — pick by who writes (Spark engineers → Lakehouse; T-SQL developers → Warehouse); both are Delta in OneLake.

## Interview-grade Q&A

- *What is Microsoft Fabric?* An all-in-one SaaS analytics platform unifying Data Factory, Data Engineering, Data Warehouse, Real-Time Intelligence, Data Science, and Power BI on one Delta-native lake (OneLake), billed as a single capacity.
- *What is OneLake?* Fabric's single, tenant-wide, Delta/Parquet-native data lake ("OneDrive for data") that every workload shares — enabling one copy of data for all engines, plus shortcuts to reference external data without copying.
- *Fabric vs Synapse?* Fabric is the SaaS successor: same lineage of engines (warehouse, Spark, pipelines, real-time) but fully managed, unified on OneLake with open Delta, and with Power BI built in — no provisioning of pools/clusters.
- *What is Direct Lake?* A Power BI mode unique to Fabric that reads Delta files in OneLake directly — import-like speed with live freshness and no data copy or refresh.
- *Lakehouse vs Warehouse item?* Both store Delta in OneLake; Lakehouse is Spark+SQL for data engineers, Warehouse is full read/write T-SQL for SQL teams.
- *When Fabric vs Databricks?* Fabric for Power BI-heavy, ops-light, integration-first Microsoft shops; Databricks for best-in-class Spark/ML, openness, and multi-cloud control.

---

## Related Notes

- **Prev:** [Dedicated vs Serverless SQL Pools](02_Dedicated_vs_Serverless_SQL_Pools.md) · **Next:** [Synapse vs Fabric vs Databricks](04_Synapse_vs_Fabric_vs_Databricks.md)
- **Foundations:** [Lakehouse Architecture](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Delta Lake](../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) · [Data Fabric & Architecture Comparison](../02_Databases/Data_Warehousing/04_Data_Fabric_and_Architecture_Comparison.md)
- **Related workloads:** [Real-Time Intelligence ≈ Stream Analytics](../09_Streaming/04_Azure_Stream_Analytics.md) · [Data Factory](../05_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md)

---

## Further Learning — Docs & Videos

**Documentation**
- What is Microsoft Fabric: https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview
- OneLake: https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview
- Direct Lake: https://learn.microsoft.com/en-us/power-bi/enterprise/directlake-overview

**Videos**
- What is Microsoft Fabric: https://www.youtube.com/results?search_query=what+is+microsoft+fabric
- OneLake and Direct Lake explained: https://www.youtube.com/results?search_query=microsoft+fabric+onelake+direct+lake
