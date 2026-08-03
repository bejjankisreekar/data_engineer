# 09 — Exam Dump: Practice Set

> **What this is:** 30 extra **exam-style** practice questions with answers and one-line explanations — a rapid drill on top of [06 — Practice Questions](06_Practice_Questions_by_Domain.md), [07 — Most Asked & Tricky](07_Most_Asked_and_Tricky_Questions.md), and the [08 — Final Mock Exam](08_Final_Mock_Exam.md).
>
> **These are original questions written to the exam's style and objectives — not real/leaked exam items.** DP-700 replaced the retired DP-203; expect Fabric-first scenarios. Answer each before revealing.

---

## Domain 1 — Implement & Manage an Analytics Solution

**1.** Which Fabric item supports full T-SQL `INSERT`/`UPDATE`/`DELETE`?
<details><summary>Answer</summary>The **Warehouse**. (A Lakehouse SQL analytics endpoint is **read-only** T-SQL.)</details>

**2.** You must reference data in an Amazon S3 bucket inside OneLake **without copying** it. Use a:
<details><summary>Answer</summary>**Shortcut** — references external data in place, always current.</details>

**3.** Which feature gives a near-real-time analytical replica of an Azure SQL Database in OneLake with **no ETL**?
<details><summary>Answer</summary>**Mirroring** — continuous replication into OneLake as Delta.</details>

**4.** A user should create notebooks and pipelines but **not** manage access. Which workspace role?
<details><summary>Answer</summary>**Contributor**. (Member/Admin can manage access; Viewer is read-only.)</details>

**5.** How do you promote content across Dev → Test → Prod in Fabric?
<details><summary>Answer</summary>**Deployment pipelines** (with deployment rules). Git integration handles version control separately.</details>

**6.** Restrict each sales rep to only their region's rows in a Warehouse table. Which feature?
<details><summary>Answer</summary>**Row-Level Security (RLS)**.</details>

**7.** Hide a credit-card column's real value from unauthorized users while keeping it stored. Use:
<details><summary>Answer</summary>**Dynamic Data Masking (DDM)**. (CLS removes column access entirely; OLS hides objects.)</details>

**8.** OneLake stores all Fabric data primarily in which open format?
<details><summary>Answer</summary>**Delta / Parquet**.</details>

**9.** Which classifies and protects data with an org-wide label (e.g. "Confidential") that follows the data?
<details><summary>Answer</summary>A **sensitivity label** (Microsoft Purview Information Protection).</details>

**10.** What is the unit of compute you purchase and scale for Fabric?
<details><summary>Answer</summary>A **capacity** (measured in Capacity Units / SKUs like F2, F64).</details>

---

## Domain 2 — Ingest & Transform Data

**11.** Move very large volumes efficiently with **minimal** transformation. Which item?
<details><summary>Answer</summary>A **Data pipeline with a Copy activity**.</details>

**12.** You need heavy **low-code** (Power Query) transformation during ingest. Use:
<details><summary>Answer</summary>**Dataflow Gen2**.</details>

**13.** No-code ingestion and routing of a real-time event stream is done with:
<details><summary>Answer</summary>An **Eventstream**.</details>

**14.** Where do you store and query high-volume real-time telemetry with **KQL**?
<details><summary>Answer</summary>An **Eventhouse / KQL Database**.</details>

**15.** Apply new and changed rows to a Delta dimension table in one atomic step. Which operation?
<details><summary>Answer</summary>**`MERGE`** (upsert) — not a full overwrite.</details>

**16.** The business needs full history of dimension changes (old + new values). Which SCD type?
<details><summary>Answer</summary>**SCD Type 2** (new row per change, with validity dates), implemented via `MERGE`.</details>

**17.** Load only rows changed since the last run. Which pattern?
<details><summary>Answer</summary>**Incremental load** using a watermark (e.g. `LastModified > @lastRun`) or CDC.</details>

**18.** Which engine handles complex, large-scale **programmatic** transforms in a Lakehouse?
<details><summary>Answer</summary>**Spark** (PySpark / Spark SQL) in a **Notebook**.</details>

**19.** You must run a T-SQL transformation across Warehouse tables on a schedule. Which combination?
<details><summary>Answer</summary>A stored procedure / T-SQL script invoked from a **Data pipeline** (scheduled).</details>

**20.** Which reads a Lakehouse table with T-SQL for BI **without** being able to modify it?
<details><summary>Answer</summary>The **SQL analytics endpoint** of the Lakehouse (read-only).</details>

**21.** Which optimization physically reorders Delta data to improve Power BI/Direct Lake read performance in Fabric?
<details><summary>Answer</summary>**V-Order** (write-time optimization), plus `OPTIMIZE` for file compaction.</details>

**22.** In a pipeline, how do you run an activity **only if** the previous one failed?
<details><summary>Answer</summary>Use the activity dependency condition **"On failure"** (also: On success, On completion, On skip).</details>

---

## Domain 3 — Monitor & Manage an Analytics Solution

**23.** Where do you see the run history and status of pipelines, notebooks, and dataflows in Fabric?
<details><summary>Answer</summary>The **Monitoring hub**.</details>

**24.** Which app shows whether a capacity is overloaded (throttling) and what's consuming it?
<details><summary>Answer</summary>The **Microsoft Fabric Capacity Metrics** app.</details>

**25.** A pipeline fails intermittently on a flaky source. Which setting makes it re-attempt automatically?
<details><summary>Answer</summary>Configure **retries** (retry count + interval) on the activity.</details>

**26.** Which Fabric item triggers actions (email, Teams, run a pipeline) when a data condition is met?
<details><summary>Answer</summary>**Data Activator** (Reflex / Activator).</details>

**27.** A Spark notebook job is slow. Where do you inspect stages, tasks, and shuffle?
<details><summary>Answer</summary>The **Spark UI** (via the Monitoring hub / notebook run details).</details>

**28.** Capacity is throttling during nightly loads. Two valid fixes:
<details><summary>Answer</summary>**Scale up the capacity SKU** or **spread/stagger the workload** (smoothing) so demand fits the capacity.</details>

**29.** You need to know which report broke when an upstream table's schema changed. Which capability helps?
<details><summary>Answer</summary>**Lineage view** in Fabric (impact analysis across items).</details>

**30.** Which language queries real-time data in an Eventhouse?
<details><summary>Answer</summary>**KQL (Kusto Query Language)**.</details>

---

## Score guide

| Score | Readiness |
|---|---|
| 27–30 | Exam-ready — book DP-700 |
| 22–26 | Close — review the Fabric-item decisions you missed |
| < 22 | Re-study the [study guide](00_DP700_Study_Guide_Overview.md) |

Next: the timed [Final Mock Exam](08_Final_Mock_Exam.md).
