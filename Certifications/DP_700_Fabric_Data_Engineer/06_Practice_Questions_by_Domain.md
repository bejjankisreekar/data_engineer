# 06 — Practice Questions by Domain

Answer before revealing. Each answer names the reasoning.

---

## Domain 1 — Implement & Manage

**1.** You need a user to build notebooks and pipelines in a workspace but not manage who else has access. Which role?
<details><summary>Answer</summary>**Contributor** — creates/edits items but cannot manage access (Member/Admin can).</details>

**2.** You want to reference data sitting in an ADLS Gen2 account inside your Lakehouse without copying it. What do you use?
<details><summary>Answer</summary>A **OneLake shortcut** — references external data in place, always current, no copy.</details>

**3.** You need a continuously-synced analytical replica of an Azure SQL Database with no ETL. What feature?
<details><summary>Answer</summary>**Mirroring** — near-real-time replica into OneLake as Delta.</details>

**4.** How do you promote content from Dev to Test to Prod in Fabric?
<details><summary>Answer</summary>**Deployment pipelines** (with deployment rules for stage-specific settings). Git handles version control separately.</details>

**5.** Sales reps must see only their own region's rows in a Warehouse table. Which security feature?
<details><summary>Answer</summary>**Row-Level Security (RLS)**.</details>

**6.** You want to hide the real values of an SSN column from analysts without removing the column. What do you use?
<details><summary>Answer</summary>**Dynamic Data Masking (DDM)** (or CLS to remove access entirely).</details>

**7.** Which stores data as open Delta so Spark, T-SQL, and Power BI all read one copy?
<details><summary>Answer</summary>**OneLake** — the Delta-native lake underpinning all Fabric items.</details>

---

## Domain 2 — Ingest & Transform

**8.** You must move very large volumes from many sources into OneLake with low code. Which item?
<details><summary>Answer</summary>A **Data pipeline with a Copy activity** (Dataflow Gen2 if heavy transform is needed during ingest).</details>

**9.** Copy activity vs Dataflow Gen2 — which for heavy low-code transformation during ingest?
<details><summary>Answer</summary>**Dataflow Gen2** (Power Query). Copy is for efficient movement with minimal transform.</details>

**10.** You need no-code ingestion and routing of a real-time event stream. Which item?
<details><summary>Answer</summary>**Eventstream**.</details>

**11.** Where do you store and query real-time telemetry with KQL?
<details><summary>Answer</summary>An **Eventhouse / KQL Database**.</details>

**12.** You need to apply new and changed rows to a Delta dimension table in one atomic step. Which operation?
<details><summary>Answer</summary>**`MERGE`** (upsert) — not a full overwrite.</details>

**13.** The business wants full history of dimension changes. Which SCD type?
<details><summary>Answer</summary>**SCD Type 2** (new row per change), implemented with `MERGE`.</details>

**14.** You must load only rows changed since the last run. What pattern?
<details><summary>Answer</summary>**Incremental load** using a watermark (e.g. `LastModified > @lastRun`) or CDC.</details>

**15.** Which engine for complex, large-scale programmatic transforms in a Lakehouse?
<details><summary>Answer</summary>**Spark** (PySpark/Spark SQL) in a Notebook.</details>

---

## Domain 3 — Monitor & Optimize

**16.** Where do you see the run history/status of all pipelines and notebooks in one place?
<details><summary>Answer</summary>The **Monitoring hub**.</details>

**17.** Queries on a streaming-written table are slow due to millions of tiny files. Fix?
<details><summary>Answer</summary>Run **`OPTIMIZE`** to compact small files (and ensure V-Order for read speed).</details>

**18.** Warehouse queries slowed sharply after a large data load. First thing to check?
<details><summary>Answer</summary>**Update statistics** — stale stats cause bad query plans.</details>

**19.** Workloads across the tenant are being throttled. What's happening and where do you look?
<details><summary>Answer</summary>The **capacity (F SKU) is overloaded** — use the **Capacity Metrics app** to find top consumers; scale up, stagger jobs, or pause noisy workloads.</details>

**20.** Which Fabric write-time optimization speeds up Direct Lake / Power BI reads?
<details><summary>Answer</summary>**V-Order**.</details>

**21.** How do you make a pipeline resilient to a transient source error?
<details><summary>Answer</summary>Configure **retries, timeouts, and on-failure paths**, and keep steps idempotent.</details>

**22.** You want to trigger an alert/action when an eventstream metric crosses a threshold. Which tool?
<details><summary>Answer</summary>**Data Activator (Activator)**.</details>

---

Next: **[07 — Most Asked & Tricky Questions](07_Most_Asked_and_Tricky_Questions.md)**.
