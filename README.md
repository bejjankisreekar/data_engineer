# Learning Azure Data Engineering

This repository is a personal learning log for Azure Data Engineering, written as plain Markdown notes.

**No coding background required.** Every note is written so that someone from a non-technical background (commerce, law, operations, etc.) can follow along. Technical words are explained the first time they appear, and most topics include a real-world analogy before the technical explanation.

If you are new here, start with the [Glossary](GLOSSARY.md) — it explains recurring jargon (schema, ACID, ETL, OLTP/OLAP, and so on) in one place so the topic notes don't have to repeat themselves.

---

## How to read these notes

Each `.md` file follows the same shape, in **three levels of depth** — read as far as your current level needs, and come back for the rest later:

**Part 1 — Basics** (top of every file)
1. **What is it?** — a plain-language definition, usually with a real-world comparison.
2. **Example** — a small, concrete example (a table, a file, a query).
3. **Advantages / Disadvantages** — when it's a good fit and when it isn't.
4. **Azure Usage** — where this concept shows up in Azure specifically.
5. **Real World Example** — a short story tying it back to a business scenario.

**Part 2 — Advanced** — how it works under the hood: internals, the patterns used in real projects, and worked examples (execution plans, join strategies, schema evolution rules, and so on).

**Part 3 — Pro Level** — what experienced engineers carry: design trade-offs, production war stories, field-tested gotchas, and **interview-grade Q&A** at the end of every file.

---

## Learning Path

### 00. Fundamentals — the big ideas behind everything else
- [OLTP Storage](00_Fundamentals/OLTP_Storage.md) — the row-based, transaction-first storage pattern behind everyday applications
- [OLAP Storage](00_Fundamentals/OLAP_Storage.md) — the column-based, analysis-first storage pattern behind warehouses
- [Distributed Computing](00_Fundamentals/Distributed_Computing.md) — scale out vs scale up, and how clusters of machines act as one computer
- [Master–Slave Architecture](00_Fundamentals/Master_Slave_Architecture.md) — the coordinator/worker pattern used by HDFS, Spark, Kafka, and more
- [Hadoop Architecture](00_Fundamentals/Hadoop_Architecture.md) — HDFS, YARN, and MapReduce: the framework that started the big data era
- [Big Data Evolution Timeline](00_Fundamentals/Big_Data_Evolution_Timeline.md) — from databases to warehouses to Hadoop to Spark to the lakehouse

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

### 05. Cloud — where all of this runs
- [Public, Private & Hybrid Cloud](05_cloud/Public_Private_Hybrid_Cloud.md) — the three deployment models: whose computers are they?
- [IaaS vs PaaS vs SaaS](05_cloud/SaaS_PaaS_IaaS.md) — the three service models: how much of the stack do you manage?

### 06. PySpark — big data processing

**Concept track** (how Spark works inside):
- [What is Apache Spark?](06_PySpark/What_Is_Apache_Spark.md) — the distributed, in-memory processing engine, explained from scratch
- [Spark Architecture](06_PySpark/Spark_Architecture.md) — driver, executors, cluster manager, jobs, stages, and tasks
- [Spark Processing](06_PySpark/Spark_Processing.md) — partitions, lazy evaluation, transformations vs actions, shuffles, caching
- [Why Spark? Why Databricks?](06_PySpark/Why_Spark_Why_Databricks.md) — why Spark replaced MapReduce, and what Databricks adds on top

**Coding track** (zero-to-pro series — start at 00 and read in order):
- [00 — PySpark Learning Path](06_PySpark/00_PySpark_Learning_Path.md) — the map of the whole series and suggested routes
- [01 — Getting Started & SparkSession](06_PySpark/01_Getting_Started_SparkSession.md) — install, run, and your entry point
- [02 — DataFrame Basics](06_PySpark/02_DataFrame_Basics.md) — select, filter, withColumn, sort — the daily verbs
- [03 — Schemas & Data Types](06_PySpark/03_Schemas_and_Data_Types.md) — declaring structure, casting, timezone discipline
- [04 — Reading & Writing Data](06_PySpark/04_Reading_and_Writing_Data.md) — CSV/JSON/Parquet/Delta/JDBC in and out
- [05 — Column Operations & Functions](06_PySpark/05_Column_Operations_and_Functions.md) — strings, dates, conditionals, null handling
- [06 — Aggregations & Grouping](06_PySpark/06_Aggregations_and_Grouping.md) — groupBy, agg, pivot, rollup
- [07 — Joins](06_PySpark/07_Joins.md) — every join type, broadcast, semi/anti, fan-out defense
- [08 — Window Functions](06_PySpark/08_Window_Functions.md) — ranking, lag/lead, running totals, dedupe
- [09 — Complex Types & JSON](06_PySpark/09_Complex_Types_and_JSON.md) — structs, arrays, explode, from_json
- [10 — UDFs & Pandas Integration](06_PySpark/10_UDFs_and_Pandas_Integration.md) — custom functions and when not to write them
- [11 — Spark SQL & Views](06_PySpark/11_Spark_SQL_and_Views.md) — mixing SQL and DataFrames, catalogs
- [12 — Delta Lake with PySpark](06_PySpark/12_Delta_Lake_with_PySpark.md) — MERGE, time travel, OPTIMIZE, the transaction log
- [13 — Structured Streaming](06_PySpark/13_Structured_Streaming.md) — checkpoints, triggers, watermarks, foreachBatch
- [14 — Performance & Best Practices](06_PySpark/14_Performance_and_Best_Practices.md) — the tuning workflow, testing, production habits
- [15 — RDDs: The Foundation](06_PySpark/15_RDDs_The_Foundation.md) — map/reduce, lineage, shuffles, and why the DataFrame API replaced hand-written RDD code

---

## Roadmap (coming later)

These modules are planned next, following the typical Azure Data Engineer learning path (roughly aligned with the Microsoft DP-203 certification):

- 06. PySpark (continued) — Databricks hands-on, Delta Lake, DataFrame API in depth
- 07. Azure — platform-wide concepts (resource groups, subscriptions, identities)
- 08. Data Factory — pipelines, triggers, integration runtimes in depth
- 09. Modern Data Warehousing — Azure Synapse Analytics, Microsoft Fabric
- 10. Streaming Data — Event Hubs, Stream Analytics, batch vs. real-time
- 11. Security & Governance — access control, Microsoft Purview, data classification
- 12. Monitoring & Orchestration — pipeline monitoring, alerting, cost management
- 13. Reporting — Power BI basics for data engineers

Folders are numbered in the order they're meant to be read, since later topics build on earlier ones.
