# 01 — Databricks Lakehouse Platform Fundamentals

*Domain: Databricks Lakehouse Platform (24%)*

---

## What it is

The **Lakehouse** is an architecture that combines the low-cost, open storage of a **data lake** with the reliability, performance, and management features of a **data warehouse** — in a single system. Instead of copying data between a lake (for data science/ML) and a warehouse (for BI/SQL), you keep one copy in cheap cloud object storage and run *all* workloads on it.

**Analogy:** A data lake is a huge, cheap warehouse where you dump everything in boxes — flexible but messy, no guarantees. A data warehouse is a tidy, expensive retail store with a strict catalog — reliable but rigid and costly. The lakehouse is the cheap warehouse *with* the retail store's catalog, checkout, and inventory system bolted on: cheap storage, warehouse-grade management.

The technology that makes this possible on Databricks is **Delta Lake** — an open-source storage layer that adds ACID transactions, schema enforcement, and time travel on top of Parquet files in object storage.

---

## The problem the Lakehouse solves

The old world had two separate systems:

| | Data Lake | Data Warehouse |
|---|---|---|
| Storage cost | Low (object storage) | High |
| Data types | All (structured, semi, unstructured) | Structured only |
| Reliability | No ACID, no schema enforcement | ACID, schema enforced |
| Best for | Data science, ML, raw data | BI, SQL analytics, reporting |
| Openness | Open formats | Often proprietary |

Keeping both meant **two copies of data, two governance models, and constant ETL between them** — expensive and error-prone. The Lakehouse gives you **one copy** that serves BI, SQL, data science, ML, and streaming.

> **Exam Tip:** If asked "what does the Lakehouse combine?" the answer is *the flexibility and low cost of data lakes* with *the reliability, ACID transactions, and performance of data warehouses*. The enabling technology is **Delta Lake**.

---

## Key characteristics of the Lakehouse

- **ACID transactions** — reliable concurrent reads/writes (via Delta Lake).
- **Schema enforcement and governance** — bad data is rejected; schema is tracked.
- **Open storage format** — data stored as Parquet + a transaction log; not locked to one vendor.
- **Decoupled storage and compute** — you pay for cheap object storage separately from compute clusters, and can scale each independently.
- **Support for diverse workloads** — SQL analytics, BI, data science, machine learning, and streaming on the same data.
- **Support for all data types** — structured, semi-structured, unstructured.
- **End-to-end streaming** — real-time data supported natively (Structured Streaming + Delta).

---

## Databricks platform architecture: Control Plane vs Data Plane

Databricks separates responsibilities into two planes. **This is a commonly tested concept.**

- **Control Plane** — managed by Databricks in Databricks' own cloud account. Holds the **backend services**: the web UI, notebooks, job scheduler, cluster manager, and query history. Your notebook *code* and results (in encrypted form) live here.
- **Data Plane (Compute Plane)** — where your data is processed. In the **classic** deployment this runs **in your own cloud account** (your VPC/VNet), so the clusters and the data they touch stay in your environment. In **serverless** deployment the compute runs in Databricks' account instead.

> **Exam Tip:** The **customer's data lives in the customer's cloud storage account** (S3 / ADLS / GCS) — it does **not** move into Databricks. Databricks compute reads it in place. The Control Plane never stores your source data; it stores metadata, notebooks, and configs.

---

## Databricks personas / workspace surfaces

The Databricks workspace offers different experiences ("personas") for different roles:

- **Data Engineering** — notebooks, Jobs/Workflows, Delta Live Tables, clusters.
- **Machine Learning** — MLflow, model registry, feature store, AutoML.
- **SQL (Databricks SQL / DBSQL)** — a warehouse-style experience for analysts: SQL editor, dashboards, alerts, and **SQL Warehouses** (SQL-optimized compute).

> **Exam Tip:** **Databricks SQL** is the BI/analyst experience; its compute is called a **SQL Warehouse** (formerly "SQL Endpoint"). A **cluster** is the general-purpose compute for notebooks/jobs. Don't confuse the two.

---

## Core platform components (what runs where)

| Component | What it is |
|---|---|
| **Workspace** | The environment/UI where you organize notebooks, dashboards, libraries, experiments. |
| **Cluster** | Managed Spark compute (driver + workers) for notebooks and jobs. |
| **SQL Warehouse** | SQL-optimized compute for Databricks SQL / BI queries. |
| **Notebook** | Interactive, multi-language document (Python, SQL, Scala, R) attached to a cluster. |
| **Job / Workflow** | Scheduled, automated execution of notebooks/scripts/pipelines. |
| **Delta Lake** | The default storage layer providing ACID + time travel. |
| **Unity Catalog** | Centralized governance: catalogs, schemas, tables, permissions, lineage. |
| **DBFS** | Databricks File System — an abstraction over cloud object storage (being de-emphasized in favor of Unity Catalog volumes). |

---

## Apache Spark's role

Databricks was founded by the creators of **Apache Spark**. Spark is the distributed processing engine underneath everything: it splits work across a cluster of machines and processes data in parallel and (mostly) in memory. Databricks adds a managed, optimized runtime on top of open-source Spark — the **Databricks Runtime (DBR)** — with performance improvements (e.g., the **Photon** vectorized engine) and pre-installed libraries.

- **Photon** — a native, vectorized C++ execution engine that speeds up SQL and DataFrame workloads. Enabled per-cluster; transparent to your code.
- **Databricks Runtime (DBR)** — the versioned bundle of Spark + optimizations + libraries you pick when creating a cluster. Variants include DBR **ML** (adds ML libraries) and DBR **Photon**.

> **Exam Tip:** **Photon** improves query performance and lowers cost — but does not change your code or results. If a scenario asks how to speed up SQL/BI workloads with no code change, Photon is the answer.

---

## Quick Review

- The **Lakehouse** = low-cost open storage of a data lake + reliability/ACID/performance of a warehouse, in one system. Enabled by **Delta Lake**.
- One copy of data serves BI, SQL, data science, ML, and streaming — no lake↔warehouse copying.
- **Control Plane** (Databricks-managed: UI, jobs, notebooks metadata) vs **Data/Compute Plane** (where data is processed; classic = your cloud account, serverless = Databricks' account).
- **Your source data stays in your own cloud object storage** — Databricks reads it in place.
- **Cluster** = general compute (notebooks/jobs); **SQL Warehouse** = SQL/BI compute for Databricks SQL.
- **Databricks Runtime (DBR)** = the Spark bundle; **Photon** = vectorized engine that speeds up SQL with no code change.
- Delta Lake is the **default** table format — assume it unless told otherwise.

---

## Further Learning — Docs & Videos

**Official documentation**
- What is the Databricks Lakehouse Platform: https://docs.databricks.com/en/introduction/index.html
- Databricks architecture (control plane / compute plane): https://docs.databricks.com/en/getting-started/overview.html
- Photon engine: https://docs.databricks.com/en/compute/photon.html
- Databricks SQL overview: https://docs.databricks.com/en/sql/index.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- "What is a Lakehouse?" search: https://www.youtube.com/results?search_query=databricks+lakehouse+architecture+explained
- Databricks Data Engineer Associate exam prep: https://www.youtube.com/results?search_query=databricks+certified+data+engineer+associate+lakehouse+platform

---

Next: **[02 — Workspace, Clusters, Notebooks & Repos](02_Workspace_Clusters_Notebooks_Repos.md)**.
