# Learning Azure Data Engineering

This repository is a personal learning log for Azure Data Engineering, written as plain Markdown notes.

**No coding background required.** Every note is written so that someone from a non-technical background (commerce, law, operations, etc.) can follow along. Technical words are explained the first time they appear, and most topics include a real-world analogy before the technical explanation.

If you are new here, start with the [Glossary](GLOSSARY.md) — it explains recurring jargon (schema, ACID, ETL, OLTP/OLAP, and so on) in one place so the topic notes don't have to repeat themselves.

---

## How to read these notes

Each `.md` file follows the same shape:

1. **What is it?** — a plain-language definition, usually with a real-world comparison.
2. **Example** — a small, concrete example (a table, a file, a query).
3. **Advantages / Disadvantages** — when it's a good fit and when it isn't.
4. **Azure Usage** — where this concept shows up in Azure specifically.
5. **Real World Example** — a short story tying it back to a business scenario.

---

## Learning Path

### 01. SQL — storing and querying data
- [What is SQL](01_SQL/What_is_SQL.md) — the SQL language itself, and the five command categories (DDL/DML/DQL/DCL/TCL) every other file in this folder belongs to
- [SQL Database](01_SQL/SQL_Database.md) — what a relational database is and why applications use one
- [SQL Data Types](01_SQL/SQL_Data_Types.md) — the rules that decide what a column is allowed to hold
- [SQL DDL](01_SQL/SQL_DDL.md) — defining structure: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, and constraints
- [SQL DML](01_SQL/SQL_DML.md) — changing data: `INSERT`, `UPDATE`, `DELETE`
- [SQL DQL](01_SQL/SQL_DQL.md) — reading data: `SELECT`, `WHERE`, `ORDER BY`, `LIKE`, `IN`, `BETWEEN`, `NULL`
- [SQL Keys and Joins](01_SQL/SQL_Keys_and_Joins.md) — how tables relate to each other (primary/foreign keys, joins, normalization)
- [SQL Aggregate Functions](01_SQL/SQL_Aggregate_Functions.md) — `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`
- [SQL Subqueries](01_SQL/SQL_Subqueries.md) — nesting one query inside another
- [SQL Views](01_SQL/SQL_Views.md) — saving a query as a reusable, table-like name
- [SQL Indexes](01_SQL/SQL_Indexes.md) — speeding up lookups without changing a query
- [SQL DCL and TCL](01_SQL/SQL_DCL_TCL.md) — controlling permissions (`GRANT`/`REVOKE`) and transactions (`COMMIT`/`ROLLBACK`/`SAVEPOINT`)
- [SQL Warehouse](01_SQL/SQL_Warehouse.md) — what a data warehouse is and how it differs from a database

### 02. File Formats — how data is stored on disk
- [CSV](02_File_formats/CSV.md) — the simplest, most universal text format
- [JSON](02_File_formats/JSON.md) — flexible, nested key-value data
- [Avro](02_File_formats/Avro.md) — row-based format built for fast writes and schema evolution
- [ORC](02_File_formats/ORC.md) — columnar format from the Hadoop world
- [Parquet](02_File_formats/Parquet.md) — the columnar format most used in modern analytics
- [File Format Comparison](02_File_formats/File_Format_Comparison.md) — a side-by-side cheat sheet for choosing between them

### 03. Data Storage — where data lives in Azure
- [Data Lake vs Warehouse vs Database](03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md) — the three storage patterns and when each is used
- [Azure Blob Storage](03_Data_Storage/Azure_Blob_Storage.md) — general-purpose cloud file storage
- [Azure Data Lake Storage](03_Data_Storage/Azure_Data_Lake_Storage.md) — Blob Storage built for large-scale analytics

### 04. ETL / ELT — moving and transforming data
- [ETL vs ELT](04_ETL_ELT/ETL_vs_ELT.md) — the two common patterns for getting data from source to destination
- [Azure Data Factory](04_ETL_ELT/Azure_Data_Factory.md) — Azure's drag-and-drop data pipeline tool

---

## Roadmap (coming later)

These modules are planned next, following the typical Azure Data Engineer learning path (roughly aligned with the Microsoft DP-203 certification):

- 05. Big Data Processing — Azure Databricks, Apache Spark, Delta Lake
- 06. Modern Data Warehousing — Azure Synapse Analytics, Microsoft Fabric
- 07. Streaming Data — Event Hubs, Stream Analytics, batch vs. real-time
- 08. Security & Governance — access control, Microsoft Purview, data classification
- 09. Monitoring & Orchestration — pipeline monitoring, alerting, cost management
- 10. Reporting — Power BI basics for data engineers

Folders are numbered in the order they're meant to be read, since later topics build on earlier ones.
