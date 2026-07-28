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
- [OLTP Storage](00_Fundamentals/01_OLTP_Storage.md) — the row-based, transaction-first storage pattern behind everyday applications
- [OLAP Storage](00_Fundamentals/02_OLAP_Storage.md) — the column-based, analysis-first storage pattern behind warehouses
- [Distributed Computing](00_Fundamentals/03_Distributed_Computing.md) — scale out vs scale up, and how clusters of machines act as one computer
- [Master–Slave Architecture](00_Fundamentals/04_Master_Slave_Architecture.md) — the coordinator/worker pattern used by HDFS, Spark, Kafka, and more
- [Hadoop Architecture](00_Fundamentals/05_Hadoop_Architecture.md) — HDFS, YARN, and MapReduce: the framework that started the big data era
- [Big Data Evolution Timeline](00_Fundamentals/06_Big_Data_Evolution_Timeline.md) — from databases to warehouses to Hadoop to Spark to the lakehouse
- **[Interview Questions & Answers](00_Fundamentals/Interview_Questions_and_Answers.md)** — 39 Q&A covering this folder, theory + scenario-based, tagged by frequency

### 01. SQL — storing and querying data
- [What is SQL](01_SQL/01_What_is_SQL.md) — the SQL language itself, and the five command categories (DDL/DML/DQL/DCL/TCL) every other file in this folder belongs to
- [SQL Database](01_SQL/02_SQL_Database.md) — what a relational database is and why applications use one
- [SQL Data Types](01_SQL/03_SQL_Data_Types.md) — the rules that decide what a column is allowed to hold
- [SQL DDL](01_SQL/04_SQL_DDL.md) — defining structure: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, and constraints
- [SQL DML](01_SQL/05_SQL_DML.md) — changing data: `INSERT`, `UPDATE`, `DELETE`
- [SQL DQL](01_SQL/06_SQL_DQL.md) — reading data: `SELECT`, `WHERE`, `ORDER BY`, `LIKE`, `IN`, `BETWEEN`, `NULL`
- [SQL Keys and Joins](01_SQL/07_SQL_Keys_and_Joins.md) — how tables relate to each other (primary/foreign keys, joins, normalization)
- [SQL Aggregate Functions](01_SQL/08_SQL_Aggregate_Functions.md) — `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`
- [SQL Subqueries](01_SQL/09_SQL_Subqueries.md) — nesting one query inside another
- [SQL Views](01_SQL/10_SQL_Views.md) — saving a query as a reusable, table-like name
- [SQL Indexes](01_SQL/11_SQL_Indexes.md) — speeding up lookups without changing a query
- [SQL DCL and TCL](01_SQL/12_SQL_DCL_TCL.md) — controlling permissions (`GRANT`/`REVOKE`) and transactions (`COMMIT`/`ROLLBACK`/`SAVEPOINT`)
- [SQL Warehouse](01_SQL/13_SQL_Warehouse.md) — what a data warehouse is and how it differs from a database
- **[Interview Questions & Answers](01_SQL/Interview_Questions_and_Answers.md)** — 39 Q&A, heavy on practical "write this query" questions with real SQL

### 02. File Formats — how data is stored on disk
- [CSV](02_File_formats/01_CSV.md) — the simplest, most universal text format
- [JSON](02_File_formats/02_JSON.md) — flexible, nested key-value data
- [Avro](02_File_formats/03_Avro.md) — row-based format built for fast writes and schema evolution
- [ORC](02_File_formats/04_ORC.md) — columnar format from the Hadoop world
- [Parquet](02_File_formats/05_Parquet.md) — the columnar format most used in modern analytics
- [File Format Comparison](02_File_formats/06_File_Format_Comparison.md) — a side-by-side cheat sheet for choosing between them
- **[Interview Questions & Answers](02_File_formats/Interview_Questions_and_Answers.md)** — 22 Q&A covering all five formats plus the comparison framework

### 03. Cloud — where all of this runs
- [Public, Private & Hybrid Cloud](03_Cloud/01_Public_Private_Hybrid_Cloud.md) — the three deployment models: whose computers are they?
- [IaaS vs PaaS vs SaaS](03_Cloud/02_SaaS_PaaS_IaaS.md) — the three service models: how much of the stack do you manage?
- **[Interview Questions & Answers](03_Cloud/Interview_Questions_and_Answers.md)** — 18 Q&A going deep on both notes

### 04. Data Storage — where data lives in Azure
- [Data Lake vs Warehouse vs Database](04_Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) — the three storage patterns and when each is used
- [Azure Blob Storage](04_Data_Storage/02_Azure_Blob_Storage.md) — general-purpose cloud file storage
- [Azure Data Lake Storage](04_Data_Storage/03_Azure_Data_Lake_Storage.md) — Blob Storage built for large-scale analytics
- **[Interview Questions & Answers](04_Data_Storage/Interview_Questions_and_Answers.md)** — 26 Q&A covering all three notes

### 05. ETL / ELT — moving and transforming data
- [ETL vs ELT](05_ETL_ELT/01_ETL_vs_ELT.md) — the two common patterns for getting data from source to destination
- [Azure Data Factory](05_ETL_ELT/02_Azure_Data_Factory.md) — Azure's drag-and-drop data pipeline tool
- [Data Pipelines](05_ETL_ELT/03_Data_Pipelines.md) — the tool-agnostic architecture: components, batch vs streaming, DAGs, idempotency, orchestration tools, failure handling
- **[Interview Questions & Answers](05_ETL_ELT/Interview_Questions_and_Answers.md)** — 16 Q&A going deep on both notes

### 06. Python — the language of data engineering
- [00 — Python Learning Path](06_Python/00_Python_Learning_Path.md) — the map of the series and the suggested route
- [01 — Getting Started](06_Python/01_Getting_Started.md) — what Python is, installing it, running code, the REPL
- [02 — Variables & Data Types](06_Python/02_Variables_and_Data_Types.md) — int/float/str/bool/None and dynamic typing
- [03 — Strings](06_Python/03_Strings.md) — slicing, methods, f-strings, formatting
- [04 — Lists, Tuples & Sets](06_Python/04_Lists_Tuples_Sets.md) — the ordered and unordered collections
- [05 — Dictionaries](06_Python/05_Dictionaries.md) — key-value data, the workhorse of Python
- [06 — Conditionals & Loops](06_Python/06_Conditionals_and_Loops.md) — if/elif/else, for, while, range, break/continue
- [07 — Functions](06_Python/07_Functions.md) — def, arguments, return, *args/**kwargs, lambda, scope
- [08 — Comprehensions](06_Python/08_Comprehensions.md) — list/dict/set comprehensions
- [09 — Files & Exceptions](06_Python/09_Files_and_Exceptions.md) — reading/writing files, try/except error handling
- [10 — Modules & Virtual Environments](06_Python/10_Modules_and_Virtual_Environments.md) — import, pip, venv, project structure
- [11 — Python for Data Engineering](06_Python/11_Python_for_Data_Engineering.md) — pandas intro and the bridge to PySpark
- **[Interview Questions & Answers](06_Python/Interview_Questions_and_Answers.md)** — Q&A covering the whole module

### 07. PySpark — big data processing

**Concept track** (how Spark works inside):
- [What is Apache Spark?](07_PySpark/What_Is_Apache_Spark.md) — the distributed, in-memory processing engine, explained from scratch
- [Spark Architecture](07_PySpark/Spark_Architecture.md) — driver, executors, cluster manager, jobs, stages, and tasks
- [Spark Processing](07_PySpark/Spark_Processing.md) — partitions, lazy evaluation, transformations vs actions, shuffles, caching
- [Why Spark? Why Databricks?](07_PySpark/Why_Spark_Why_Databricks.md) — why Spark replaced MapReduce, and what Databricks adds on top

**Coding track** (zero-to-pro series — start at 00 and read in order):
- [00 — PySpark Learning Path](07_PySpark/00_PySpark_Learning_Path.md) — the map of the whole series and suggested routes
- [01 — Getting Started & SparkSession](07_PySpark/01_Getting_Started_SparkSession.md) — install, run, and your entry point
- [02 — DataFrame Basics](07_PySpark/02_DataFrame_Basics.md) — select, filter, withColumn, sort — the daily verbs
- [03 — Schemas & Data Types](07_PySpark/03_Schemas_and_Data_Types.md) — declaring structure, casting, timezone discipline
- [04 — Reading & Writing Data](07_PySpark/04_Reading_and_Writing_Data.md) — CSV/JSON/Parquet/Delta/JDBC in and out
- [05 — Column Operations & Functions](07_PySpark/05_Column_Operations_and_Functions.md) — strings, dates, conditionals, null handling
- [06 — Aggregations & Grouping](07_PySpark/06_Aggregations_and_Grouping.md) — groupBy, agg, pivot, rollup
- [07 — Joins](07_PySpark/07_Joins.md) — every join type, broadcast, semi/anti, fan-out defense
- [08 — Window Functions](07_PySpark/08_Window_Functions.md) — ranking, lag/lead, running totals, dedupe
- [09 — Complex Types & JSON](07_PySpark/09_Complex_Types_and_JSON.md) — structs, arrays, explode, from_json
- [10 — UDFs & Pandas Integration](07_PySpark/10_UDFs_and_Pandas_Integration.md) — custom functions and when not to write them
- [11 — Spark SQL & Views](07_PySpark/11_Spark_SQL_and_Views.md) — mixing SQL and DataFrames, catalogs
- [12 — Delta Lake with PySpark](07_PySpark/12_Delta_Lake_with_PySpark.md) — MERGE, time travel, OPTIMIZE, the transaction log
- [13 — Structured Streaming](07_PySpark/13_Structured_Streaming.md) — checkpoints, triggers, watermarks, foreachBatch
- [14 — Performance & Best Practices](07_PySpark/14_Performance_and_Best_Practices.md) — the tuning workflow, testing, production habits
- [15 — RDDs: The Foundation](07_PySpark/15_RDDs_The_Foundation.md) — map/reduce, lineage, shuffles, and why the DataFrame API replaced hand-written RDD code

**[Interview Questions & Answers](07_PySpark/Interview_Questions_and_Answers.md)** — 78 Q&A, the largest in the series, covering all 19 files above with real PySpark code in every practical answer

### 08. Data Warehousing — architectures beyond a single central warehouse
- [Data Warehouse Fundamentals](08_Data_Warehousing/01_Data_Warehouse_Fundamentals.md) — Inmon's four properties, warehouse layers (staging/ODS/marts), single/two/three-tier architecture, Inmon vs Kimball
- [Data Mart](08_Data_Warehousing/02_Data_Mart.md) — dependent vs independent vs hybrid marts, star schema per mart, the "spreadmart" failure mode
- [Data Mesh](08_Data_Warehousing/03_Data_Mesh.md) — the four principles (domain ownership, data as a product, self-serve platform, federated governance), when it's the right call vs overkill
- [Data Fabric & Architecture Comparison](08_Data_Warehousing/04_Data_Fabric_and_Architecture_Comparison.md) — data fabric vs data mesh, the Microsoft Fabric naming collision, a five-pattern decision framework

### 09. Git & GitHub — version control from zero to production-ready
- [00 — Learning Path](09_Git_GitHub/00_Git_GitHub_Learning_Path.md) — the map of the series, Git vs GitHub in one sentence
- [01 — Introduction to Version Control](09_Git_GitHub/01_Introduction_to_Version_Control.md) — why Git exists, installation, config, `git init`, core terminology
- [02 — Core Workflow: Add, Commit, Status, Log](09_Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md) — the daily loop, `.gitignore`, commit message conventions
- [03 — Branching & Merging](09_Git_GitHub/03_Branching_and_Merging.md) — branches, fast-forward vs three-way merges, a full hands-on merge conflict walkthrough
- [04 — Remotes: Push, Pull, Fetch, Clone](09_Git_GitHub/04_Remotes_Push_Pull_Fetch_Clone.md) — tracking branches, SSH vs HTTPS auth, `origin`/`upstream`, force push dangers
- [05 — GitHub Essentials](09_Git_GitHub/05_GitHub_Essentials.md) — Issues, Pull Requests end to end, forking, merge strategies
- [06 — Rebase, Cherry-Pick, Reset & Revert](09_Git_GitHub/06_Rebase_Cherry_Pick_Reset_Revert.md) — rewriting history safely, interactive rebase, reflog recovery
- [07 — Stash, Tags & Other Commands](09_Git_GitHub/07_Stash_Tags_and_Other_Commands.md) — `stash`, `tag`, `blame`, `bisect`, worktrees
- [08 — Branching Strategies & Collaboration](09_Git_GitHub/08_Branching_Strategies_and_Collaboration.md) — Git Flow vs GitHub Flow vs trunk-based, branch protection, CODEOWNERS
- [09 — Production Best Practices & CI/CD](09_Git_GitHub/09_Production_Best_Practices_and_CICD.md) — Conventional Commits, hooks, GitHub Actions, secrets, Git LFS, signed commits
- [10 — Troubleshooting & Real-World Scenarios](09_Git_GitHub/10_Troubleshooting_and_Real_World_Scenarios.md) — symptom-indexed fixes for every common Git disaster

---

## Certificates & Exams

A separate self-contained track outside the main learning path, for certification prep specifically.

### AZ-900 — Microsoft Azure Fundamentals
- [00 — Study Guide Overview](9999_certificates_exams/AZ_900/00_AZ900_Study_Guide_Overview.md) — exam format, domain weights, and the study plan — start here
- [01 — Cloud Concepts](9999_certificates_exams/AZ_900/01_Cloud_Concepts.md) — benefits, CapEx/OpEx, IaaS/PaaS/SaaS, deployment models
- [02 — Azure Architecture Fundamentals](9999_certificates_exams/AZ_900/02_Azure_Architecture_Fundamentals.md) — regions, zones, resource groups, subscriptions, ARM
- [03 — Azure Compute Services](9999_certificates_exams/AZ_900/03_Azure_Compute_Services.md) — VMs, App Service, containers, AKS, Functions
- [04 — Azure Networking Services](9999_certificates_exams/AZ_900/04_Azure_Networking_Services.md) — VNets, VPN Gateway, ExpressRoute, load balancing options
- [05 — Azure Storage Services](9999_certificates_exams/AZ_900/05_Azure_Storage_Services.md) — Blob/Files/Table/Queue, tiers, redundancy (LRS–RA-GZRS)
- [06 — Identity, Access & Security](9999_certificates_exams/AZ_900/06_Identity_Access_Security.md) — Entra ID, RBAC, Zero Trust, Defender, Sentinel
- [07 — Cost Management](9999_certificates_exams/AZ_900/07_Cost_Management.md) — pricing tools, Reserved/Spot instances, budgets
- [08 — Governance & Compliance](9999_certificates_exams/AZ_900/08_Governance_and_Compliance.md) — Azure Policy, resource locks, Blueprints, Purview
- [09 — Monitoring & Management Tools](9999_certificates_exams/AZ_900/09_Monitoring_and_Management_Tools.md) — Portal/CLI/Cloud Shell, ARM vs Bicep, Advisor vs Service Health
- [10 — Practice Questions by Domain](9999_certificates_exams/AZ_900/10_Practice_Questions_by_Domain.md) — 40 questions with explanations
- [11 — Most Asked & Tricky Questions](9999_certificates_exams/AZ_900/11_Most_Asked_and_Tricky_Exam_Questions.md) — the 15 comparison pairs that decide most wrong answers
- [12 — Final Mock Exam](9999_certificates_exams/AZ_900/12_Final_Mock_Exam.md) — a timed 50-question simulation with a scoring guide

---

## Roadmap (coming later)

These modules are planned next (numbered to follow `09_Git_GitHub`), following the typical Azure Data Engineer learning path (roughly aligned with the Microsoft DP-203 certification):

- 10. Databricks & Delta Lake — hands-on lakehouse, Unity Catalog, DLT (see also the [Databricks certification track](9999_certificates_exams/Databricks_Data_Engineer_Associate/00_Study_Guide_Overview.md))
- 11. Streaming Data — Event Hubs, Kafka, Stream Analytics, batch vs. real-time
- 12. Security & Governance — access control, Microsoft Purview, data classification
- 13. Monitoring & Orchestration — Airflow, pipeline monitoring, alerting, cost management
- 14. Reporting — Power BI basics for data engineers

Folders are numbered in the order they're meant to be read, since later topics build on earlier ones. The `9999_certificates_exams/` folder sits deliberately last as a separate certification-prep track.
