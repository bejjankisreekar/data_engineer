# 08 — Exam Dump: Practice Set

> **What this is:** 30 extra **exam-style** practice questions with answers and one-line explanations — a rapid drill on top of [05 — Practice Questions](05_Practice_Questions_by_Domain.md), [06 — Most Asked & Tricky](06_Most_Asked_and_Tricky_Questions.md), and the [07 — Final Mock Exam](07_Final_Mock_Exam.md).
>
> **These are original questions written to the exam's style and objectives — not real/leaked exam items.** Answer each before revealing.

---

## Domain 1 — Core Data Concepts (~25–30%)

**1.** A CSV file with a fixed set of columns and rows is best described as:
<details><summary>Answer</summary>**Structured data** — fits a rigid rows-and-columns schema.</details>

**2.** JSON and XML documents are examples of:
<details><summary>Answer</summary>**Semi-structured data** — organized with tags/keys but no fixed table grid.</details>

**3.** A system optimized for many small, fast inserts/updates (e.g. an e-commerce checkout) is:
<details><summary>Answer</summary>**OLTP** (Online Transaction Processing) — row-based, transaction-first.</details>

**4.** A system optimized for large analytical queries over historical data is:
<details><summary>Answer</summary>**OLAP** (Online Analytical Processing) — column-based, read-heavy.</details>

**5.** Processing a nightly batch of yesterday's sales files is an example of:
<details><summary>Answer</summary>**Batch processing** — bounded data on a schedule. (Streaming processes events as they arrive.)</details>

**6.** Which role is primarily responsible for building and maintaining data pipelines?
<details><summary>Answer</summary>The **Data Engineer**. (Data Analyst builds reports; DBA manages the database.)</details>

**7.** The four guarantees a transactional database makes — atomicity, consistency, isolation, durability — are:
<details><summary>Answer</summary>**ACID**.</details>

**8.** An image, a video, and a PDF are examples of:
<details><summary>Answer</summary>**Unstructured data**.</details>

---

## Domain 2 — Relational Data on Azure (~20–25%)

**9.** A **fully managed PaaS** relational database with automatic patching and high availability, ideal for new cloud apps, is:
<details><summary>Answer</summary>**Azure SQL Database**.</details>

**10.** You need near-100% SQL Server compatibility to lift-and-shift an on-prem app with minimal changes. Choose:
<details><summary>Answer</summary>**Azure SQL Managed Instance**.</details>

**11.** Which SQL command category includes `SELECT`?
<details><summary>Answer</summary>**DQL** (Data Query Language). `INSERT/UPDATE/DELETE` = DML; `CREATE/ALTER/DROP` = DDL.</details>

**12.** Which Azure services offer managed **open-source** relational databases? (best answer)
<details><summary>Answer</summary>**Azure Database for PostgreSQL / MySQL / MariaDB**.</details>

**13.** A column that uniquely identifies each row in a table is a:
<details><summary>Answer</summary>**Primary key**.</details>

**14.** Running SQL Server on an Azure **VM** (you manage the OS and SQL) is which service model?
<details><summary>Answer</summary>**IaaS** — maximum control, maximum management responsibility.</details>

**15.** Which command **structurally** removes all rows from a table quickly, without logging each row?
<details><summary>Answer</summary>**`TRUNCATE`** (DDL) — faster than `DELETE`, but can't use a `WHERE` clause.</details>

---

## Domain 3 — Non-Relational Data on Azure (~15–20%)

**16.** The Azure service for storing large amounts of unstructured objects (images, backups, logs) is:
<details><summary>Answer</summary>**Azure Blob Storage**.</details>

**17.** Which Blob tier suits data accessed frequently with lowest access cost?
<details><summary>Answer</summary>**Hot** tier.</details>

**18.** Azure's globally distributed, multi-model **NoSQL** database with single-digit-millisecond latency is:
<details><summary>Answer</summary>**Azure Cosmos DB**.</details>

**19.** Which Cosmos DB API is the default and works with document/JSON data?
<details><summary>Answer</summary>The **NoSQL (Core / SQL) API**.</details>

**20.** Which Azure Storage service provides fully managed **SMB/NFS file shares** in the cloud?
<details><summary>Answer</summary>**Azure Files**.</details>

**21.** ADLS Gen2 differs from plain Blob Storage mainly by adding:
<details><summary>Answer</summary>A **hierarchical namespace** (true folders) + fine-grained ACLs — tuned for big-data analytics.</details>

**22.** Which Cosmos DB API would you choose to migrate an existing **MongoDB** application?
<details><summary>Answer</summary>The **API for MongoDB**.</details>

---

## Domain 4 — Analytics Workloads on Azure (~25–30%)

**23.** The primarily **low-code, drag-and-drop** service for orchestrating data movement and ETL/ELT is:
<details><summary>Answer</summary>**Azure Data Factory (ADF)**.</details>

**24.** Microsoft's unified analytics platform combining SQL pools, Spark pools, and pipelines is:
<details><summary>Answer</summary>**Azure Synapse Analytics**.</details>

**25.** The managed **Apache Spark** platform for large-scale processing and ML on Azure is:
<details><summary>Answer</summary>**Azure Databricks**.</details>

**26.** The primary tool for building interactive **reports and dashboards** in the Microsoft stack is:
<details><summary>Answer</summary>**Power BI**.</details>

**27.** Loading raw data first and transforming it inside the destination is the ______ pattern:
<details><summary>Answer</summary>**ELT** (Extract, Load, Transform) — common with powerful cloud warehouses. ETL transforms before loading.</details>

**28.** The three-layer lakehouse pattern raw → cleaned → business-ready is called:
<details><summary>Answer</summary>The **medallion architecture** (Bronze → Silver → Gold).</details>

**29.** Microsoft's SaaS analytics platform storing everything as Delta in **OneLake** is:
<details><summary>Answer</summary>**Microsoft Fabric**.</details>

**30.** In a data warehouse, the central table of numeric measurements surrounded by descriptive tables is the ______, and the descriptive tables are ______:
<details><summary>Answer</summary>The **fact table** and **dimension tables** (a **star schema**).</details>

---

## Score guide

| Score | Readiness |
|---|---|
| 27–30 | Exam-ready |
| 22–26 | Close — review weak domains |
| < 22 | Re-study the [study guide](00_DP900_Study_Guide_Overview.md) |

Next: the timed [Final Mock Exam](07_Final_Mock_Exam.md).
