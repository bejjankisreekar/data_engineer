# Synapse & Fabric — Interview Questions & Answers

Covers the whole module: [Synapse Analytics](01_Azure_Synapse_Analytics.md), [SQL Pools](02_Dedicated_vs_Serverless_SQL_Pools.md), [Microsoft Fabric](03_Microsoft_Fabric.md), [Synapse vs Fabric vs Databricks](04_Synapse_vs_Fabric_vs_Databricks.md). Tagged **[Theory]** / **[Scenario]**, ⭐ = very frequently asked. See also the [Synapse interview folder](../Job%20Interviews/Azure%20Synapse/Synapse%20Interview%20Questions.md).

---

## Azure Synapse Analytics

**1. ⭐ [Theory] What is Azure Synapse Analytics?**
A unified analytics platform combining four engines in one workspace over ADLS: a dedicated MPP SQL warehouse, a serverless SQL engine that queries lake files in place, Apache Spark pools, and ADF-style pipelines — all sharing one data lake and security model.

**2. ⭐ [Theory] Dedicated vs serverless SQL pool?**
Dedicated is a provisioned MPP warehouse that loads and stores data in distributed tables for fast, high-concurrency BI (billed per DWU while online). Serverless has no provisioning or storage — it runs T-SQL over lake files in place, billed per TB scanned — ideal for ad-hoc exploration and a logical warehouse.

**3. [Theory] How do Synapse Pipelines relate to ADF?**
They're the same engine embedded in Synapse — identical activities, linked services, integration runtimes, and mapping data flows. Skills and patterns transfer directly between standalone ADF and Synapse Pipelines.

**4. [Theory] What is Synapse Link?**
HTAP (Hybrid Transactional/Analytical Processing) — it maintains an auto-synced analytical copy of operational data (Cosmos DB, Azure SQL, Dataverse) so you can run analytics on near-real-time data without building CDC/ETL or hitting the transactional store.

**5. [Scenario] Would you start a new project on Synapse today?**
Generally no for green-field — Synapse is mature but Microsoft's investment has shifted to Fabric, its successor. Keep and optimize existing Synapse estates, but weigh Fabric or Databricks for new builds.

---

## MPP & distribution (dedicated pool)

**6. ⭐ [Theory] Explain the MPP architecture of a dedicated SQL pool.**
A control node receives and plans the query; multiple compute nodes execute in parallel over 60 data distributions; adding DWUs adds compute. Performance depends on minimizing cross-distribution data movement (shuffle).

**7. ⭐ [Theory] What are the distribution strategies and when do you use each?**
Hash (large fact tables — distribute on a high-cardinality, frequently-joined column), round-robin (staging/load tables or when there's no good hash key), and replicated (small dimension tables copied to every node, < ~2 GB). Chosen to co-locate joined data and minimize shuffle.

**8. ⭐ [Scenario] A dedicated-pool query got slow as data grew. Diagnose it.**
Almost always a distribution problem, not a DWU problem: misaligned hash keys or non-replicated small dimensions forcing data movement (shuffle), or a skewed/low-cardinality hash key piling rows onto a few distributions (data skew), often worsened by stale statistics. Fix distribution and refresh stats before scaling DWUs.

**9. [Scenario] How would you distribute a star schema?**
Hash-distribute large fact tables on their common join key; replicate small dimension tables to every node so joins are local; round-robin only staging tables. This co-locates the join and minimizes data movement.

**10. [Theory] How do you load data into a dedicated pool?**
`COPY INTO` (modern, simplest) or PolyBase to bulk-load from the lake, and CTAS (`CREATE TABLE AS SELECT`) to transform and redistribute data within the pool.

**11. [Theory] What indexing does a dedicated pool use?**
Clustered Columnstore Index (CCI) is the default and best for large analytical tables (compression + fast scans); heap or clustered rowstore indexes suit small or lookup-heavy tables.

**12. [Scenario] How does serverless SQL control cost?**
It bills per terabyte scanned, so file layout is a cost lever: converting to Parquet, partitioning for pruning, and compacting small files can cut both runtime and cost dramatically. Avoid full scans of giant unpartitioned files.

**13. [Theory] What's the biggest dedicated-pool cost mistake?**
Leaving it online 24/7 — it bills for provisioned DWUs whenever it's running, regardless of load. Pause it on a schedule (storage persists) and use serverless for ad-hoc queries.

---

## Microsoft Fabric

**14. ⭐ [Theory] What is Microsoft Fabric?**
An all-in-one SaaS analytics platform unifying Data Factory, Data Engineering (Spark/Lakehouse), Data Warehouse, Real-Time Intelligence, Data Science, and Power BI on one Delta-native lake (OneLake), billed as a single capacity — the SaaS successor to Synapse.

**15. ⭐ [Theory] What is OneLake?**
Fabric's single, tenant-wide, Delta/Parquet-native data lake ("OneDrive for data") that every workload shares. It gives one copy of data for all engines and supports shortcuts to reference external data (ADLS/S3/other workspaces) without copying.

**16. ⭐ [Theory] What is Direct Lake?**
A Power BI storage mode unique to Fabric that reads Delta files in OneLake directly — combining import-mode speed with live freshness and no data copy or refresh. It replaces the old import-vs-DirectQuery trade-off.

**17. [Theory] Lakehouse vs Warehouse item in Fabric?**
Both store Delta in OneLake. A Lakehouse is a Spark+SQL experience for data engineers (write with Spark/notebooks); a Warehouse is a full read/write T-SQL experience for SQL teams. Because both are Delta, each can query the other's tables.

**18. [Theory] What are shortcuts?**
References that make data living elsewhere (ADLS, S3, GCS, other Fabric workspaces) appear in OneLake without copying it — Fabric's "virtualize instead of duplicate" answer to data silos.

**19. [Theory] How is Fabric billed?**
As a shared **capacity** (F SKUs, e.g. F64) covering all workloads in the tenant, replacing per-service bills (ADF + Synapse + storage + Power BI). Capacity sizing/monitoring becomes the cost lever, with smoothing/bursting and noisy-neighbour effects to manage.

**20. [Scenario] Fabric vs Synapse — how are they related?**
Fabric is the SaaS successor: its engines map to Synapse ancestors (Fabric Warehouse ≈ Synapse SQL, Data Engineering ≈ Synapse Spark, Data Factory ≈ ADF/pipelines, Real-Time Intelligence ≈ Stream Analytics), but fully managed, unified on OneLake with open Delta, and with Power BI built in.

---

## Choosing a platform

**21. ⭐ [Scenario] Synapse vs Fabric vs Databricks — one line each.**
Synapse: mature MPP SQL warehouse platform, superseded by Fabric. Fabric: SaaS, unified, Power BI-native on OneLake. Databricks: best-in-class open Spark/lakehouse/ML.

**22. ⭐ [Scenario] Power BI-heavy org, small platform team — which platform and why?**
Fabric — SaaS means no infrastructure to run, Power BI is built in with Direct Lake (fast + fresh, no refresh), and OneLake gives one Delta copy for every workload. It maximizes integration and minimizes ops for exactly that profile.

**23. [Scenario] A team needs top-tier Spark and ML across multiple clouds. Which?**
Databricks — best Spark performance (Photon), Delta features, Unity Catalog governance, MLflow, and it's open and multi-cloud, unlike the Azure/Microsoft-bound Synapse and Fabric.

**24. [Scenario] Why is "just use Databricks" a weak interview answer?**
It ignores the constraints the question embeds — team size, ops appetite, Power BI gravity, existing investment, budget. The senior signal is naming the deciding constraint and matching the platform to it; sometimes that's Fabric's simplicity or an existing Synapse estate, not Databricks' raw power.

**25. [Theory] What ties all three platforms together?**
Open Delta on object storage. Because they all read/write Delta, they interoperate (Databricks can write Delta that Fabric reads via a shortcut; Synapse serverless can query Databricks' Delta), which is why mixed architectures — e.g. Databricks for engineering + Fabric/Power BI for BI — are common and low-lock-in at the data layer.

---

## Putting it together

**26. [Scenario] Design a Microsoft-native analytics platform for a mid-size insurer with some ML needs.**
Core on **Fabric**: Data Factory ingests into a **Lakehouse** in OneLake (Delta); Spark notebooks build silver/gold; a **Warehouse** item exposes gold to SQL teams; **Direct Lake** Power BI serves fast, fresh dashboards; **Real-Time Intelligence** handles a live eventstream. Add **Databricks** for the ML workload, pointing at the *same* OneLake Delta via shortcuts. Don't stand up new Synapse — Fabric replaces it. The reasoning: ops-light + Power BI gravity → Fabric; ML depth → Databricks; open Delta lets both share one copy.

---

## Related Notes

- Module: [00 Learning Path](00_Learning_Path.md) → [01 Synapse](01_Azure_Synapse_Analytics.md) · [02 SQL Pools](02_Dedicated_vs_Serverless_SQL_Pools.md) · [03 Fabric](03_Microsoft_Fabric.md) · [04 Decision framework](04_Synapse_vs_Fabric_vs_Databricks.md)
- [Databricks](../08_Databricks/00_Databricks_Learning_Path.md) · [Lakehouse](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Data Warehouse Fundamentals](../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md)
