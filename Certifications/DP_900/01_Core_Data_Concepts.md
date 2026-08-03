# 01 — Core Data Concepts

*Domain: Core data concepts (25–30%)*

---

## What it is

This domain is the **vocabulary** of data — the ideas every later domain builds on: the *kinds* of data, the two big *workload types* (transactional vs analytical), the *roles* who work with data, and *how* data is stored and processed. It's the highest-weighted domain and the easiest to score if you learn the definitions cleanly.

Much of it is covered in depth in this repo's [Foundations](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md) and [Storage & Formats](../../05_Storage_and_Formats/File_Formats/06_File_Format_Comparison.md) notes.

---

## Types of data

| Type | Definition | Examples |
|---|---|---|
| **Structured** | Fits a fixed schema of rows & columns | Relational tables, CSV with a schema |
| **Semi-structured** | Has tags/keys but a flexible schema | [JSON](../../05_Storage_and_Formats/File_Formats/02_JSON.md), XML, [Avro](../../05_Storage_and_Formats/File_Formats/03_Avro.md) |
| **Unstructured** | No predefined data model | Images, video, audio, PDFs, free text |

> **Exam Tip:** Structured = relational/tabular with a fixed schema. Semi-structured = JSON/XML (self-describing, flexible). Unstructured = media/files with no schema. A key-value or document store holds **semi-structured** data.

---

## Transactional (OLTP) vs Analytical (OLAP)

The most important distinction in the whole exam:

| | **Transactional (OLTP)** | **Analytical (OLAP)** |
|---|---|---|
| Purpose | Run the business (day-to-day operations) | Analyze the business (insights, reporting) |
| Operations | Many small reads/writes (insert/update) | Few large reads, aggregations |
| Design | Normalized, row-based | Denormalized, often column-based |
| Latency | Milliseconds, high concurrency | Seconds–minutes, complex queries |
| Example | "Place this order" | "Total sales by region last year" |

Deep dives: [OLTP](../../01_Foundations/Fundamentals/01_OLTP_Storage.md) · [OLAP](../../01_Foundations/Fundamentals/02_OLAP_Storage.md).

> **Exam Tip:** OLTP = **transactions**, current data, normalized, ACID. OLAP = **analytics**, historical data, aggregations. A data warehouse is an **OLAP** system; an app's operational database is **OLTP**.

---

## Batch vs Streaming

| | **Batch** | **Streaming** |
|---|---|---|
| Data | Collected, processed in chunks on a schedule | Processed continuously as it arrives |
| Latency | High (minutes–hours) | Low (seconds) |
| Example | Nightly sales load | Live IoT / fraud alerts |

Full treatment: [Streaming Fundamentals](../../09_Streaming/01_Streaming_Fundamentals.md).

> **Exam Tip:** Batch = bounded data on a schedule; streaming = unbounded data in real time. Azure streaming services: **Event Hubs / IoT Hub** (ingest), **Stream Analytics** (process).

---

## Data roles

| Role | Responsibility |
|---|---|
| **Database Administrator (DBA)** | Manages databases: availability, security, backups, performance, users/permissions |
| **Data Engineer** | Builds/manages data pipelines and storage; ingests, cleans, transforms, integrates data |
| **Data Analyst** | Explores and visualizes data to produce insights (e.g., Power BI reports) |

> **Exam Tip:** DBA = keeps databases healthy & secure. Data Engineer = builds the *pipelines/storage*. Data Analyst = builds the *reports/visuals*. Match the task to the role — "designs and builds ETL" → data engineer; "creates dashboards" → data analyst; "configures backups and security" → DBA.

---

## Data storage: files vs databases

- **File storage** — data in files ([CSV](../../05_Storage_and_Formats/File_Formats/01_CSV.md), [JSON](../../05_Storage_and_Formats/File_Formats/02_JSON.md), [Parquet](../../05_Storage_and_Formats/File_Formats/05_Parquet.md), Avro, ORC) in a file system or object store. Cheap, flexible, schema-on-read.
- **Databases** — data managed by a database engine with querying, indexing, and integrity — **relational** (tables/SQL) or **non-relational/NoSQL** (documents, key-value, graph, column-family).

File format quick facts (commonly tested):
- **CSV** — simple, text, row-based, human-readable.
- **JSON** — semi-structured, nested, self-describing.
- **Parquet** — columnar, compressed, great for analytics.
- **Avro** — row-based, good for streaming/schema evolution.
- **ORC** — columnar, from the Hadoop world.

Full comparison: [File Format Comparison](../../05_Storage_and_Formats/File_Formats/06_File_Format_Comparison.md).

---

## Relational database concepts (preview of Domain 2)

- **Table** — rows (records) and columns (fields).
- **Primary key** — uniquely identifies each row; **foreign key** — links to another table's primary key.
- **Index** — speeds up lookups.
- **View** — a saved query that acts like a virtual table.
- **Normalization** — organizing data to reduce redundancy.

See [SQL Keys & Joins](../../02_Databases/SQL/07_SQL_Keys_and_Joins.md) and [Normalization](../../02_Databases/Data_Modeling/02_Normalization_and_Denormalization.md).

---

## Quick Review

- **Structured** (tabular/fixed schema), **semi-structured** (JSON/XML, flexible), **unstructured** (media/files).
- **OLTP** = transactions, current, normalized, ACID; **OLAP** = analytics, historical, aggregations, columnar.
- **Batch** = scheduled chunks; **streaming** = continuous real-time (Event Hubs → Stream Analytics).
- Roles: **DBA** (manage DBs), **Data Engineer** (pipelines/storage), **Data Analyst** (visualize/report).
- Storage: **files** (CSV/JSON/Parquet/Avro/ORC) vs **databases** (relational vs NoSQL).
- **Parquet** = columnar/analytics; **CSV** = simple text; **JSON/Avro** = semi-structured.

---

## Further Learning — Docs & Videos

- Explore core data concepts (Microsoft Learn): https://learn.microsoft.com/en-us/training/paths/azure-data-fundamentals-explore-core-data-concepts/
- DP-900 exam page: https://learn.microsoft.com/en-us/credentials/certifications/azure-data-fundamentals/
- Video search: https://www.youtube.com/results?search_query=dp-900+core+data+concepts

---

Next: **[02 — Relational Data on Azure](02_Relational_Data_on_Azure.md)**.
