# 01 — Fabric & Workspace Fundamentals

*Domain: Implement and manage an analytics solution (30–35%)*

---

## What it is

Before ingesting or transforming anything, you must know **what the Fabric building blocks are** and **how a workspace is configured**. This note covers the platform pieces, the item types a data engineer uses, and workspace/capacity settings. The conceptual "what is Fabric" background is in the learning note: [Microsoft Fabric](../../10_Synapse_and_Fabric/03_Microsoft_Fabric.md).

---

## Fabric core concepts

- **OneLake** — the single, tenant-wide, **Delta/Parquet-native** lake every item shares ("OneDrive for data"). One copy of data for all engines.
- **Capacity (F SKU)** — the compute the tenant buys (e.g. F64); all workloads draw from it. Sizing/pausing the capacity is the main cost lever.
- **Workspace** — a collaboration container for items, bound to a capacity, with roles and (optionally) Git and deployment pipelines.
- **Domain** — a tenant-level grouping of workspaces by business area (governance/data-mesh style).
- **Item** — any Fabric artifact (Lakehouse, Warehouse, Notebook, Pipeline, etc.).

> **Exam Tip:** **OneLake stores everything as open Delta**, so a table written by Spark in a Lakehouse is instantly queryable by a Warehouse and readable by Power BI Direct Lake — no copies. This "one copy, many engines" fact underlies many answers.

---

## The Fabric items a data engineer uses

| Item | What it is | Primary use |
|---|---|---|
| **Lakehouse** | Delta tables **+ files**, Spark + SQL | Data engineering, medallion, notebooks |
| **Warehouse** | Full read/write **T-SQL** warehouse (Delta-backed) | SQL-first modeling & serving |
| **SQL analytics endpoint** | Read-only T-SQL over a Lakehouse's tables | Query lakehouse tables with SQL |
| **Eventhouse / KQL Database** | Real-time analytics store (KQL) | Streaming/telemetry analytics |
| **Data pipeline** | Orchestration + Copy activity (ADF-style) | Ingest & orchestrate |
| **Dataflow Gen2** | Power Query low-code transform | Low-code ingest/transform |
| **Notebook** | Spark (PySpark/Spark SQL) | Complex transforms, ML |
| **Eventstream** | No-code streaming ingest/routing | Real-time pipelines |
| **Semantic model** | Power BI data model | BI serving |

> **Exam Tip:** **Lakehouse vs Warehouse** — Lakehouse is Spark+SQL for engineers (write with Spark/notebooks); Warehouse is full read/write T-SQL for SQL developers. Both store Delta in OneLake; a Lakehouse's **SQL analytics endpoint** is *read-only* T-SQL, while a Warehouse supports T-SQL `INSERT/UPDATE/DELETE`.

---

## Workspace settings a data engineer configures

- **License/Capacity** — assign the workspace to a Fabric capacity.
- **Roles** — Admin, Member, Contributor, Viewer (see [02](02_Security_Governance_and_Lifecycle.md)).
- **Spark settings** — default pool, environment (libraries), runtime version, node sizing, autoscale.
- **Data workflow / OneLake settings** — default storage behavior.
- **Git integration & deployment pipelines** — lifecycle (see [02](02_Security_Governance_and_Lifecycle.md)).
- **Domains** — assign the workspace to a business domain.

> **Exam Tip:** **Spark environments** package the runtime version + libraries + Spark configs for reproducible notebook execution. If a scenario needs a specific library available to all notebooks in a workspace, attach it to a **custom environment**, not a per-notebook `%pip` (though `%pip` works notebook-scoped).

---

## Shortcuts & Mirroring (data without copying)

Two ways to bring external data into OneLake **without a copy pipeline** — heavily tested:

- **Shortcut** — a *reference* that makes data in ADLS Gen2, Amazon S3, GCS, or another Fabric workspace appear in OneLake as if local. No duplication, always current.
- **Mirroring** — a near-real-time, continuously-synced **replica** of an operational database (Azure SQL DB, Cosmos DB, Snowflake, etc.) into OneLake as Delta, with no ETL to build.

> **Exam Tip:** Need to *reference* existing lake/cloud files in place → **Shortcut**. Need a *live replica* of an operational database for analytics with zero ETL → **Mirroring**. Neither requires a traditional copy job.

---

## Capacity model basics

- Everything consumes **Capacity Units (CUs)** from the shared capacity.
- Fabric applies **smoothing** (spreading bursts over time) and **bursting** (temporarily exceeding to finish faster), then **throttling** if sustained demand exceeds the capacity.
- The **Fabric Capacity Metrics app** is where you monitor consumption (see [05](05_Monitor_and_Optimize.md)).

> **Exam Tip:** A "workloads are slowing down / getting throttled" scenario points to **capacity** being overloaded — scale up the F SKU, pause noisy workloads, or use the Capacity Metrics app to find the culprit.

---

## Quick Review

- **OneLake** = one tenant-wide Delta lake; **capacity (F SKU)** = shared compute; **workspace** = collaboration container bound to a capacity; **domain** = business grouping.
- Key items: **Lakehouse** (Spark+SQL, files+tables), **Warehouse** (full T-SQL), **SQL analytics endpoint** (read-only T-SQL over a lakehouse), **Eventhouse/KQL** (real-time), **Pipeline**, **Dataflow Gen2**, **Notebook**, **Eventstream**.
- **Lakehouse write = Spark; Warehouse write = T-SQL.** Both are Delta in OneLake.
- **Shortcut** = reference external data in place; **Mirroring** = live replica of an operational DB — both avoid copy pipelines.
- **Spark environments** package runtime + libraries for reproducible notebooks.
- Throttling → the **capacity** is the bottleneck; check the **Capacity Metrics app**.

---

## Further Learning — Docs & Videos

- What is Microsoft Fabric: https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview
- OneLake shortcuts: https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts
- Fabric database mirroring: https://learn.microsoft.com/en-us/fabric/database/mirrored-database/overview
- Video search: https://www.youtube.com/results?search_query=dp-700+fabric+workspace+lakehouse+warehouse

---

Next: **[02 — Security, Governance & Lifecycle](02_Security_Governance_and_Lifecycle.md)**.
