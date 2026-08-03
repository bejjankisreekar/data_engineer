# Databricks — Learning Path

**Azure Databricks** is the platform where most modern Azure data engineering actually happens: it's a managed Apache Spark environment with the [lakehouse](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) built in. If [PySpark](../03_Programming/PySpark/00_PySpark_Learning_Path.md) is the *language* and [Delta Lake](../05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) is the *storage format*, **Databricks is the house they both live in.**

This module teaches the **platform** — clusters, notebooks, jobs, governance, and the managed features (Unity Catalog, DLT, Auto Loader) that turn raw Spark into a production data platform.

> **Note on the two Databricks tracks in this repo:** this `08_Databricks/` folder is the **learning path** — concepts first, in the house 3-part style. The separate [Databricks Data Engineer Associate](../Certifications/Databricks_Data_Engineer_Associate/00_Study_Guide_Overview.md) folder is **exam prep** for the certification. Read this to *understand*; read that to *pass the test*.

---

## Prerequisites

Before this module, you should have done:
- [PySpark](../03_Programming/PySpark/00_PySpark_Learning_Path.md) — Databricks runs Spark; you need to speak it
- [Delta Lake](../05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) & [Lakehouse Architecture](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) — the storage foundation
- [Azure Data Lake Storage](../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md) — where the data physically lives

---

## The map

| # | Note | What it covers |
|---|---|---|
| 01 | [What is Databricks?](01_What_is_Databricks.md) | The platform, control plane vs data plane, workspace, why it exists |
| 02 | [Clusters & Compute](02_Clusters_and_Compute.md) | All-purpose vs job clusters, pools, autoscaling, Photon, SQL warehouses, cost |
| 03 | [Notebooks, Repos & Jobs](03_Notebooks_Repos_and_Jobs.md) | Notebooks, Git Repos, Workflows/Jobs orchestration, widgets, `dbutils` |
| 04 | [Unity Catalog](04_Unity_Catalog.md) | Governance: metastore, three-level namespace, access control, lineage |
| 05 | [Delta Live Tables (DLT)](05_Delta_Live_Tables.md) | Declarative pipelines, expectations, streaming tables, the medallion made easy |
| 06 | [Auto Loader & Ingestion](06_Auto_Loader_and_Ingestion.md) | Incremental file ingestion, schema inference/evolution, `COPY INTO` |
| — | [Interview Q&A](Interview_Questions_and_Answers.md) | Q&A across the whole module |

---

## Suggested route

- **Just want the concepts:** 01 → 02 → 04. That's the platform in three notes.
- **Building pipelines:** all of 01–06 in order.
- **Interview tomorrow:** the [Q&A](Interview_Questions_and_Answers.md) + the [Databricks interview folder](../Job%20Interviews/Azure%20Databricks/Databricks%20Interview%20Questions.md) + [Performance Optimization](../Job%20Interviews/Azure%20Databricks/Performance%20Optimization.md).

**Milestone for the module:** explain the control-plane/data-plane split, pick the right cluster type for a job, describe Unity Catalog's three-level namespace, and sketch a medallion pipeline built with DLT + Auto Loader.
