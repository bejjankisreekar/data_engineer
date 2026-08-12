# Azure Synapse & Microsoft Fabric — Learning Path

Two of the biggest names in the Azure analytics world — and they're directly related: **Microsoft Fabric is the SaaS successor to Azure Synapse Analytics**. Together they're the "Microsoft-native" answer to the analytics platform question, sitting alongside [Databricks](../08_Databricks/00_Databricks_Learning_Path.md) as the two platforms an Azure Data Engineer is expected to know.

This module teaches **Synapse** (still widely deployed, heavily interviewed — especially its MPP SQL engine), **Fabric** (where Microsoft is investing now), and — crucially — **when to use which**, including versus Databricks.

---

## Prerequisites

- [SQL Warehouse](../02_Databases/SQL/13_SQL_Warehouse.md) & [Data Warehouse Fundamentals](../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md) — Synapse *is* a warehouse
- [Distributed Computing](../01_Foundations/Fundamentals/03_Distributed_Computing.md) & [Master–Slave Architecture](../01_Foundations/Fundamentals/04_Master_Slave_Architecture.md) — MPP is distributed SQL
- [Lakehouse Architecture](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) & [Delta Lake](../05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) — Fabric's OneLake is Delta-native
- [Data Lake vs Warehouse vs Database](../05_Storage_and_Formats/Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)

---

## The map

| # | Note | What it covers |
|---|---|---|
| 01 | [Azure Synapse Analytics](01_Azure_Synapse_Analytics.md) | The unified platform — SQL pools, Spark pools, pipelines, Synapse Studio, Synapse Link |
| 02 | [Dedicated vs Serverless SQL Pools](02_Dedicated_vs_Serverless_SQL_Pools.md) | MPP internals, **distribution (hash/round-robin/replicated)**, DWUs, loading, the pay-per-query engine |
| 03 | [Microsoft Fabric](03_Microsoft_Fabric.md) | SaaS analytics, **OneLake**, workloads, Direct Lake, Lakehouse vs Warehouse items, capacities |
| 04 | [Synapse vs Fabric vs Databricks](04_Synapse_vs_Fabric_vs_Databricks.md) | The decision framework — which platform for which job |
| — | [Interview Q&A](Interview_Questions_and_Answers.md) | Q&A across the whole module |

---

## Suggested route

- **Interview-focused:** [02](02_Dedicated_vs_Serverless_SQL_Pools.md) (distribution/MPP is the classic Synapse question) → [04](04_Synapse_vs_Fabric_vs_Databricks.md) (the "which would you pick?" question).
- **Modern-stack focused:** [03](03_Microsoft_Fabric.md) (OneLake + Direct Lake) → [04](04_Synapse_vs_Fabric_vs_Databricks.md).
- **Complete:** 01 → 02 → 03 → 04 in order.

**Milestone for the module:** explain MPP and pick a distribution strategy for a fact vs dimension table; describe what OneLake and Direct Lake change; and, given a scenario, argue Synapse vs Fabric vs Databricks with reasons.

---

## One-line orientation

- **Synapse Analytics** — a mature warehouse + Spark + pipelines platform; its **dedicated SQL pool** is a powerful MPP data warehouse. Being **superseded by Fabric** for new builds.
- **Microsoft Fabric** — an all-in-one **SaaS** analytics platform built on **OneLake** (one Delta-native lake for the org), unifying data engineering, warehousing, real-time, and Power BI under one capacity.
- **Databricks** — the best-in-class lakehouse/Spark platform; the main alternative to both.
