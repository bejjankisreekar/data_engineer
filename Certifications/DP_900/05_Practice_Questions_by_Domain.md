# 05 — Practice Questions by Domain

Answer before revealing. Each answer names the domain and the reasoning.

---

## Domain 1 — Core Data Concepts

**1.** A JSON file from a web API is which type of data?
<details><summary>Answer</summary>**Semi-structured** — it has keys/tags but a flexible schema (not a fixed relational schema, not unstructured media).</details>

**2.** Placing an online order and immediately confirming it is which workload type?
<details><summary>Answer</summary>**Transactional (OLTP)** — small, fast write, current data, high concurrency.</details>

**3.** Who is responsible for designing and building data ingestion pipelines?
<details><summary>Answer</summary>The **Data Engineer** (DBA manages databases; Data Analyst builds reports).</details>

**4.** Which file format is columnar and optimized for analytics?
<details><summary>Answer</summary>**Parquet** (CSV is row-based text; JSON/Avro are semi-structured/row-based).</details>

**5.** Processing a nightly file of the day's transactions is batch or streaming?
<details><summary>Answer</summary>**Batch** — a bounded chunk on a schedule.</details>

---

## Domain 2 — Relational Data

**6.** You're migrating an on-prem SQL Server that uses SQL Agent and cross-database queries with minimal changes. Which service?
<details><summary>Answer</summary>**Azure SQL Managed Instance** — near-full SQL Server compatibility, PaaS, ideal for lift-and-shift migrations needing instance-level features.</details>

**7.** Which service gives the *least* management overhead for a new cloud app's relational database?
<details><summary>Answer</summary>**Azure SQL Database** — fully managed PaaS, cloud-native.</details>

**8.** `GRANT SELECT ON …` belongs to which SQL category?
<details><summary>Answer</summary>**DCL** (Data Control Language — permissions).</details>

**9.** An app has unpredictable, intermittent database usage and wants to avoid paying when idle. What do you recommend?
<details><summary>Answer</summary>**Serverless** compute tier of Azure SQL Database (auto-scales, auto-pauses).</details>

**10.** You need OS-level access and full control over the SQL Server installation. Which option?
<details><summary>Answer</summary>**SQL Server on an Azure VM** (IaaS).</details>

---

## Domain 3 — Non-Relational Data

**11.** Which Azure Storage service stores unstructured objects like images and video?
<details><summary>Answer</summary>**Blob Storage**.</details>

**12.** What distinguishes ADLS Gen2 from ordinary Blob Storage?
<details><summary>Answer</summary>A **hierarchical namespace** (true folders), optimized for big-data analytics.</details>

**13.** You need a globally distributed NoSQL database with single-digit-millisecond latency. Which service?
<details><summary>Answer</summary>**Azure Cosmos DB**.</details>

**14.** Your data is a social graph of people and their connections. Which Cosmos DB API?
<details><summary>Answer</summary>**Gremlin** (graph API).</details>

**15.** For data accessed only once or twice a year at the lowest storage cost, which blob tier?
<details><summary>Answer</summary>**Archive** tier.</details>

---

## Domain 4 — Analytics Workloads

**16.** Which service orchestrates and moves data between sources in a low-code pipeline?
<details><summary>Answer</summary>**Azure Data Factory**.</details>

**17.** Which pattern loads raw data first and transforms it inside the destination?
<details><summary>Answer</summary>**ELT** (Extract, Load, Transform).</details>

**18.** In Power BI, what's the difference between a report and a dashboard?
<details><summary>Answer</summary>A **report** is multi-page, built in Desktop over one dataset; a **dashboard** is a single-page canvas in the Service pinning visuals possibly from many reports.</details>

**19.** "Why did sales drop last month?" is which type of analytics?
<details><summary>Answer</summary>**Diagnostic** (why something happened).</details>

**20.** Which platform is Microsoft's unified SaaS analytics product built on OneLake?
<details><summary>Answer</summary>**Microsoft Fabric**.</details>

**21.** Which service provides Apache Spark for large-scale data processing and ML?
<details><summary>Answer</summary>**Azure Databricks** (Synapse Spark pools also, but Databricks is the Spark-first answer).</details>

**22.** Real-time IoT telemetry needs to feed a live dashboard. Which two Azure services fit ingest + process?
<details><summary>Answer</summary>**Event Hubs / IoT Hub** (ingest) + **Azure Stream Analytics** (process).</details>

---

Next: **[06 — Most Asked & Tricky Questions](06_Most_Asked_and_Tricky_Questions.md)**.
