# Learning Azure Data Engineering

This repository is a personal learning log for Azure Data Engineering, written as plain Markdown notes.

**No coding background required.** Every note is written so that someone from a non-technical background (commerce, law, operations, etc.) can follow along. Technical words are explained the first time they appear, and most topics include a real-world analogy before the technical explanation.

**New here? Start with the [ROADMAP](ROADMAP.md)** — a zero-to-job-ready path (9 phases, with milestones) that tells you *what to learn, in what order, and why*, linking every note in this repo. Then use the [Glossary](GLOSSARY.md) — it explains recurring jargon (schema, ACID, ETL, OLTP/OLAP, and so on) in one place so the topic notes don't have to repeat themselves.

---

## How to read these notes

Each `.md` file is **one continuous read** that takes a topic from first principles all the way to what an experienced engineer knows about it. There are no separate beginner/advanced/pro tracks to come back for later — the note simply keeps going, and every file covers its topic completely:

1. **What is it?** — a plain-language definition, usually with a real-world comparison.
2. **Example** — a small, concrete example (a table, a file, a query).
3. **Advantages / Disadvantages** — when it's a good fit and when it isn't.
4. **Azure Usage** — where this concept shows up in Azure specifically.
5. **Real World Example** — a short story tying it back to a business scenario.
6. **Under the hood** — internals, the patterns used in real projects, and worked examples (execution plans, join strategies, schema evolution rules, and so on).
7. **Design trade-offs and production reality** — the decisions experienced engineers weigh, war stories, and field-tested gotchas.
8. **Interview-grade Q&A** — at the end of every file.

Stop wherever you need to and pick the file back up later — nothing is held back for a later tier.

---

## Learning Path

Topics are grouped into **category folders** so related material lives together:

| Category folder | Contains |
|---|---|
| **01_Foundations** | Fundamentals (OLTP/OLAP, distributed computing, Hadoop) |
| **02_Databases** | SQL · NoSQL · Data Modeling · Data Warehousing |
| **03_Programming** | Python · PySpark |
| **04_Cloud** | Cloud Concepts (deployment & service models) |
| **05_Storage_and_Formats** | Storage Paradigms Map · File Formats · Data Lakes & Storage · Lakehouse (Delta Lake, Delta Table, Lakehouse, Medallion) |
| **06_Data_Engineering** | ETL / ELT · Data Integration · Data Governance & Security · Data Quality |
| **07_DevOps** | Git & GitHub (version control, branching, remotes, CI/CD, troubleshooting) — Docker · Kubernetes · Terraform · ARM covered in Job Interviews |
| **08_Databricks** | Platform · Why Spark · Clusters · Notebooks/Jobs · Workflows · Unity Catalog · ABFSS/Volumes · DLT · Auto Loader · Cost |
| **09_Streaming** | Streaming fundamentals · Event Hubs · Kafka · Stream Analytics |
| **10_Synapse_and_Fabric** | Synapse Analytics · Dedicated/Serverless SQL pools (MPP) · Microsoft Fabric · platform decision guide |
| **11_Orchestration** | DAGs · ADF triggers · Databricks Workflows · Apache Airflow |
| **12_Monitoring_and_Observability** | Monitoring · Azure Monitor/KQL · pipeline reliability · data observability |
| **13_dbt** | data build tool — models, tests, docs, snapshots (SCD2), dbt in Azure |
| **14_Testing_and_DataOps** | Testing pipelines · data quality tests · data contracts · CI/CD for data |
| **15_Cost_and_Performance** | FinOps · Databricks/Spark cost · storage & query cost · performance tuning |
| **16_Power_BI_for_Engineers** | Semantic models · star schema · DAX basics · serving from the lakehouse |
| **17_System_Design** | Design framework · batch · streaming/real-time · case studies |
| **18_Projects** | Hands-on end-to-end projects (batch medallion · streaming · ADF-orchestrated) + portfolio — the capstone |
| **Certifications** | AZ-900 · DP-900 · Databricks Data Engineer Associate · DP-700 (Fabric) |
| **Job Interviews** | 31 interview-prep topic folders |

---

### 01_Foundations › Fundamentals — the big ideas behind everything else
- [OLTP Storage](01_Foundations/Fundamentals/01_OLTP_Storage.md) — the row-based, transaction-first storage pattern behind everyday applications
- [OLAP Storage](01_Foundations/Fundamentals/02_OLAP_Storage.md) — the column-based, analysis-first storage pattern behind warehouses
- [Distributed Computing](01_Foundations/Fundamentals/03_Distributed_Computing.md) — scale out vs scale up, and how clusters of machines act as one computer
- [Master–Slave Architecture](01_Foundations/Fundamentals/04_Master_Slave_Architecture.md) — the coordinator/worker pattern used by HDFS, Spark, Kafka, and more
- [Hadoop Architecture](01_Foundations/Fundamentals/05_Hadoop_Architecture.md) — HDFS, YARN, and MapReduce: the framework that started the big data era
- [Big Data Evolution Timeline](01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md) — from databases to warehouses to Hadoop to Spark to the lakehouse
- **[Interview Questions & Answers](01_Foundations/Fundamentals/Interview_Questions_and_Answers.md)** — 39 Q&A covering this folder, theory + scenario-based, tagged by frequency

### 02_Databases › SQL — storing and querying data
- [What is SQL](02_Databases/SQL/01_What_is_SQL.md) — the SQL language itself, and the five command categories (DDL/DML/DQL/DCL/TCL) every other file in this folder belongs to
- [SQL Database](02_Databases/SQL/02_SQL_Database.md) — what a relational database is and why applications use one
- [SQL Data Types](02_Databases/SQL/03_SQL_Data_Types.md) — the rules that decide what a column is allowed to hold
- [SQL DDL](02_Databases/SQL/04_SQL_DDL.md) — defining structure: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, and constraints
- [SQL DML](02_Databases/SQL/05_SQL_DML.md) — changing data: `INSERT`, `UPDATE`, `DELETE`
- [SQL DQL](02_Databases/SQL/06_SQL_DQL.md) — reading data: `SELECT`, `WHERE`, `ORDER BY`, `LIKE`, `IN`, `BETWEEN`, `NULL`
- [SQL Keys and Joins](02_Databases/SQL/07_SQL_Keys_and_Joins.md) — how tables relate to each other (primary/foreign keys, joins, normalization)
- [SQL Aggregate Functions](02_Databases/SQL/08_SQL_Aggregate_Functions.md) — `COUNT`, `SUM`, `AVG`, `GROUP BY`, `HAVING`
- [SQL Window Functions](02_Databases/SQL/14_SQL_Window_Functions.md) — ranking, running totals, `LAG`/`LEAD`, frames, and deduplication (reads best right after aggregates)
- [SQL Subqueries](02_Databases/SQL/09_SQL_Subqueries.md) — nesting one query inside another
- [SQL Views](02_Databases/SQL/10_SQL_Views.md) — saving a query as a reusable, table-like name
- [SQL Stored Procedures and Programmability](02_Databases/SQL/15_SQL_Stored_Procedures_and_Programmability.md) — procedures, functions, triggers, temp tables, cursors, dynamic SQL
- [SQL Indexes](02_Databases/SQL/11_SQL_Indexes.md) — speeding up lookups without changing a query
- [SQL DCL and TCL](02_Databases/SQL/12_SQL_DCL_TCL.md) — controlling permissions (`GRANT`/`REVOKE`) and transactions (`COMMIT`/`ROLLBACK`/`SAVEPOINT`)
- [SQL Warehouse](02_Databases/SQL/13_SQL_Warehouse.md) — what a data warehouse is and how it differs from a database
- **[Interview Questions & Answers](02_Databases/SQL/Interview_Questions_and_Answers.md)** — 39 Q&A, heavy on practical "write this query" questions with real SQL
- **[Practical SQL Query Interview Questions](02_Databases/SQL/Practical_SQL_Query_Interview_Questions.md)** — hands-on "write the query" problems (joins, aggregates, subqueries, window functions) with worked solutions

### 02_Databases › NoSQL — non-relational databases for scale & flexible data
- [00 — Learning Path](02_Databases/NoSQL/00_NoSQL_Learning_Path.md) — the map of the module (level 0 to job-ready)
- [01 — What is NoSQL](02_Databases/NoSQL/01_What_is_NoSQL.md) — why it exists, SQL vs NoSQL, the four families, when (not) to use it
- [02 — Key-Value Stores](02_Databases/NoSQL/02_Key_Value_Stores.md) — Redis/DynamoDB, caching, sessions, cache-aside
- [03 — Document Databases](02_Databases/NoSQL/03_Document_Databases.md) — MongoDB/Cosmos DB, JSON docs, embedding vs referencing
- [04 — Wide-Column Stores](02_Databases/NoSQL/04_Wide_Column_Stores.md) — Cassandra/HBase, partition & clustering keys, LSM writes
- [05 — Graph Databases](02_Databases/NoSQL/05_Graph_Databases.md) — Neo4j, nodes/edges, index-free adjacency, traversals
- [06 — CAP Theorem & Consistency](02_Databases/NoSQL/06_CAP_Theorem_and_Consistency.md) — CP vs AP, ACID vs BASE, quorums, PACELC
- [07 — NoSQL Data Modeling](02_Databases/NoSQL/07_NoSQL_Data_Modeling.md) — model by access pattern, denormalize, schema patterns
- [08 — Azure Cosmos DB](02_Databases/NoSQL/08_Azure_Cosmos_DB.md) — partition keys, RUs, APIs, 5 consistency levels, Synapse Link
- [09 — NoSQL in Data Engineering](02_Databases/NoSQL/09_NoSQL_in_Data_Engineering.md) — change feed ingestion, flattening JSON, reverse ETL, practical scenarios
- **[Interview Questions & Answers](02_Databases/NoSQL/Interview_Questions_and_Answers.md)** — 45 Q&A across the module, tagged by frequency

### 02_Databases › Data Modeling — designing how data is structured
- [00 — Learning Path](02_Databases/Data_Modeling/00_Data_Modeling_Learning_Path.md) — the map of the module
- [01 — Data Modeling Fundamentals](02_Databases/Data_Modeling/01_Data_Modeling_Fundamentals.md) — conceptual/logical/physical, ER, keys, cardinality
- [02 — Normalization & Denormalization](02_Databases/Data_Modeling/02_Normalization_and_Denormalization.md) — 1NF–BCNF, when to denormalize
- [03 — Dimensional Modeling](02_Databases/Data_Modeling/03_Dimensional_Modeling.md) — star vs snowflake, facts, dimensions, grain, additivity
- [04 — Slowly Changing Dimensions](02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) — SCD Types 0–6 and SCD2 in Delta
- [05 — Data Vault & Modern Modeling](02_Databases/Data_Modeling/05_Data_Vault_and_Modern_Modeling.md) — Data Vault 2.0, OBT, modeling for the lakehouse
- **[Interview Questions & Answers](02_Databases/Data_Modeling/Interview_Questions_and_Answers.md)** — 26 Q&A across the module

### 05_Storage_and_Formats › 🗺️ Start here — the big picture
- **[Storage Paradigms Map](05_Storage_and_Formats/00_Storage_Paradigms_Map.md)** — Database → Warehouse → Data Lake → Lakehouse in one place: how they relate, and where each topic lives across the repo. Read this if the terms blur together.

### 05_Storage_and_Formats › File Formats — how data is stored on disk
- [CSV](05_Storage_and_Formats/File_Formats/01_CSV.md) — the simplest, most universal text format
- [JSON](05_Storage_and_Formats/File_Formats/02_JSON.md) — flexible, nested key-value data
- [Avro](05_Storage_and_Formats/File_Formats/03_Avro.md) — row-based format built for fast writes and schema evolution
- [ORC](05_Storage_and_Formats/File_Formats/04_ORC.md) — columnar format from the Hadoop world
- [Parquet](05_Storage_and_Formats/File_Formats/05_Parquet.md) — the columnar format most used in modern analytics
- [File Format Comparison](05_Storage_and_Formats/File_Formats/06_File_Format_Comparison.md) — a side-by-side cheat sheet for choosing between them
- **[Interview Questions & Answers](05_Storage_and_Formats/File_Formats/Interview_Questions_and_Answers.md)** — 22 Q&A covering all five formats plus the comparison framework

### 04_Cloud › Cloud Concepts — where all of this runs
- [Public, Private & Hybrid Cloud](04_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md) — the three deployment models: whose computers are they?
- [IaaS vs PaaS vs SaaS](04_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md) — the three service models: how much of the stack do you manage?
- **[Interview Questions & Answers](04_Cloud/Cloud_Concepts/Interview_Questions_and_Answers.md)** — 18 Q&A going deep on both notes

### 05_Storage_and_Formats › Data Lakes & Storage — where data lives in Azure
- [Data Lake vs Warehouse vs Database](05_Storage_and_Formats/Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) — the three storage patterns and when each is used
- [Azure Blob Storage](05_Storage_and_Formats/Data_Lakes_and_Storage/02_Azure_Blob_Storage.md) — general-purpose cloud file storage
- [Azure Data Lake Storage](05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) — Blob Storage built for large-scale analytics
- **[Interview Questions & Answers](05_Storage_and_Formats/Data_Lakes_and_Storage/Interview_Questions_and_Answers.md)** — 26 Q&A covering all three notes

### 05_Storage_and_Formats › Lakehouse — the modern table format and architecture
- [00 — Delta Lake vs Delta Table vs Lakehouse](05_Storage_and_Formats/Lakehouse/00_Delta_Lake_vs_Delta_Table_vs_Lakehouse.md) — **start here:** the beginner-friendly clarifier of the three easily-confused terms, with diagrams
- [01 — Delta Lake](05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) — the open storage layer that adds ACID, updates/deletes, and time travel to Parquet via a transaction log
- [02 — Delta Table](05_Storage_and_Formats/Lakehouse/02_Delta_Table.md) — the table itself: managed vs external, MERGE/upsert, OPTIMIZE, VACUUM, Change Data Feed
- [03 — Lakehouse Architecture](05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) — one copy of data for BI + ML, the two-copy problem it kills, and the three pillars
- [04 — Medallion Architecture](05_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md) — the **Bronze → Silver → Gold** layering in depth: per-layer rules, transformation code, batch/streaming, anti-patterns
- **[Interview Questions & Answers](05_Storage_and_Formats/Lakehouse/Interview_Questions_and_Answers.md)** — 25 Q&A across Delta Lake, Delta tables, and the lakehouse

### 06_Data_Engineering › ETL / ELT — moving and transforming data
- [ETL vs ELT](06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) — the two common patterns for getting data from source to destination
- [Azure Data Factory](06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) — Azure's drag-and-drop data pipeline tool
- [Data Pipelines](06_Data_Engineering/ETL_ELT/03_Data_Pipelines.md) — the tool-agnostic architecture: components, batch vs streaming, DAGs, idempotency, orchestration tools, failure handling
- **[Interview Questions & Answers](06_Data_Engineering/ETL_ELT/Interview_Questions_and_Answers.md)** — 16 Q&A going deep on both notes

### 06_Data_Engineering › Data Integration — combining data from many sources
- [01 — Data Integration Fundamentals](06_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md) — ETL/ELT/replication/CDC/virtualization/streaming/API, batch vs stream
- [02 — Integration Patterns](06_Data_Engineering/Data_Integration/02_Integration_Patterns.md) — full/incremental/CDC, metadata-driven, reliability & delivery semantics
- [03 — Change Data Capture (CDC)](06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) — log-based CDC, MERGE, Delta Change Data Feed
- [04 — Azure Integration Services](06_Data_Engineering/Data_Integration/04_Azure_Integration_Services.md) — ADF, Databricks, Event Hub, Logic Apps, Event Grid, Service Bus
- **[Interview Questions & Answers](06_Data_Engineering/Data_Integration/Interview_Questions_and_Answers.md)** — 20 Q&A across the module

### 06_Data_Engineering › Data Governance & Security — trust, access, lineage, compliance
- [01 — Data Governance & Security](06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) — governance pillars, RBAC/ACL, MSI/Key Vault, Purview, Unity Catalog, lineage, GDPR
- [02 — Network Security & Private Connectivity](06_Data_Engineering/Data_Governance/02_Network_Security_and_Private_Connectivity.md) — private endpoints/Private Link, ADF Managed VNet, Databricks VNet injection & Secure Cluster Connectivity, Private DNS
- **[Interview Questions & Answers](06_Data_Engineering/Data_Governance/Interview_Questions_and_Answers.md)** — 15 Q&A on governance & security

### 06_Data_Engineering › Data Quality — delivering data people can trust
- [01 — Data Quality & Validation](06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) — quality dimensions, shift-left, quarantine, DLT expectations, Great Expectations, observability
- **[Interview Questions & Answers](06_Data_Engineering/Data_Quality/Interview_Questions_and_Answers.md)** — 14 Q&A on data quality

### 03_Programming › Python — the language of data engineering
- [00 — Python Learning Path](03_Programming/Python/00_Python_Learning_Path.md) — the map of the series and the suggested route
- [01 — Getting Started](03_Programming/Python/01_Getting_Started.md) — what Python is, installing it, running code, the REPL
- [02 — Variables & Data Types](03_Programming/Python/02_Variables_and_Data_Types.md) — int/float/str/bool/None and dynamic typing
- [03 — Strings](03_Programming/Python/03_Strings.md) — slicing, methods, f-strings, formatting
- [04 — Lists, Tuples & Sets](03_Programming/Python/04_Lists_Tuples_Sets.md) — the ordered and unordered collections
- [05 — Dictionaries](03_Programming/Python/05_Dictionaries.md) — key-value data, the workhorse of Python
- [06 — Conditionals & Loops](03_Programming/Python/06_Conditionals_and_Loops.md) — if/elif/else, for, while, range, break/continue
- [07 — Functions](03_Programming/Python/07_Functions.md) — def, arguments, return, *args/**kwargs, lambda, scope
- [08 — Comprehensions](03_Programming/Python/08_Comprehensions.md) — list/dict/set comprehensions
- [09 — Files & Exceptions](03_Programming/Python/09_Files_and_Exceptions.md) — reading/writing files, try/except error handling
- [10 — Modules & Virtual Environments](03_Programming/Python/10_Modules_and_Virtual_Environments.md) — import, pip, venv, project structure
- [11 — Python for Data Engineering](03_Programming/Python/11_Python_for_Data_Engineering.md) — pandas intro and the bridge to PySpark
- **[Interview Questions & Answers](03_Programming/Python/Interview_Questions_and_Answers.md)** — Q&A covering the whole module

### 03_Programming › PySpark — big data processing

**Concept track** (how Spark works inside):
- [What is Apache Spark?](03_Programming/PySpark/What_Is_Apache_Spark.md) — the distributed, in-memory processing engine, explained from scratch
- [Spark Architecture](03_Programming/PySpark/Spark_Architecture.md) — driver, executors, cluster manager, jobs, stages, and tasks
- [Spark Processing](03_Programming/PySpark/Spark_Processing.md) — partitions, lazy evaluation, transformations vs actions, shuffles, caching
- *(["Why Spark? Why Databricks?"](08_Databricks/02_Why_Spark_Why_Databricks.md) now lives in the [08_Databricks](08_Databricks/00_Databricks_Learning_Path.md) module)*

**Coding track** (zero-to-pro series — start at 00 and read in order):
- [00 — PySpark Learning Path](03_Programming/PySpark/00_PySpark_Learning_Path.md) — the map of the whole series and suggested routes
- [01 — Getting Started & SparkSession](03_Programming/PySpark/01_Getting_Started_SparkSession.md) — install, run, and your entry point
- [02 — DataFrame Basics](03_Programming/PySpark/02_DataFrame_Basics.md) — select, filter, withColumn, sort — the daily verbs
- [03 — Schemas & Data Types](03_Programming/PySpark/03_Schemas_and_Data_Types.md) — declaring structure, casting, timezone discipline
- [04 — Reading & Writing Data](03_Programming/PySpark/04_Reading_and_Writing_Data.md) — CSV/JSON/Parquet/Delta/JDBC in and out
- [05 — Column Operations & Functions](03_Programming/PySpark/05_Column_Operations_and_Functions.md) — strings, dates, conditionals, null handling
- [06 — Aggregations & Grouping](03_Programming/PySpark/06_Aggregations_and_Grouping.md) — groupBy, agg, pivot, rollup
- [07 — Joins](03_Programming/PySpark/07_Joins.md) — every join type, broadcast, semi/anti, fan-out defense
- [08 — Window Functions](03_Programming/PySpark/08_Window_Functions.md) — ranking, lag/lead, running totals, dedupe
- [09 — Complex Types & JSON](03_Programming/PySpark/09_Complex_Types_and_JSON.md) — structs, arrays, explode, from_json
- [10 — UDFs & Pandas Integration](03_Programming/PySpark/10_UDFs_and_Pandas_Integration.md) — custom functions and when not to write them
- [11 — Spark SQL & Views](03_Programming/PySpark/11_Spark_SQL_and_Views.md) — mixing SQL and DataFrames, catalogs
- [12 — Delta Lake with PySpark](03_Programming/PySpark/12_Delta_Lake_with_PySpark.md) — MERGE, time travel, OPTIMIZE, the transaction log
- [13 — Structured Streaming](03_Programming/PySpark/13_Structured_Streaming.md) — checkpoints, triggers, watermarks, foreachBatch
- [14 — Performance & Best Practices](03_Programming/PySpark/14_Performance_and_Best_Practices.md) — the tuning workflow, testing, production habits
- [15 — RDDs: The Foundation](03_Programming/PySpark/15_RDDs_The_Foundation.md) — map/reduce, lineage, shuffles, and why the DataFrame API replaced hand-written RDD code

**📋 [PySpark Syntax & Methods Reference](03_Programming/PySpark/PySpark_Syntax_and_Methods_Reference.md)** — the dense one-page look-up: read every file format (CSV/JSON/Parquet/Delta/JDBC…) + every common operation (filter, select, join, groupBy, window, complex types, UDFs…) with syntax and snippets

**[Interview Questions & Answers](03_Programming/PySpark/Interview_Questions_and_Answers.md)** — 78 Q&A, the largest in the series, covering all 19 files above with real PySpark code in every practical answer

### 02_Databases › Data Warehousing — architectures beyond a single central warehouse
- [Data Warehouse Fundamentals](02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md) — Inmon's four properties, warehouse layers (staging/ODS/marts), single/two/three-tier architecture, Inmon vs Kimball
- [Data Mart](02_Databases/Data_Warehousing/02_Data_Mart.md) — dependent vs independent vs hybrid marts, star schema per mart, the "spreadmart" failure mode
- [Data Mesh](02_Databases/Data_Warehousing/03_Data_Mesh.md) — the four principles (domain ownership, data as a product, self-serve platform, federated governance), when it's the right call vs overkill
- [Data Fabric & Architecture Comparison](02_Databases/Data_Warehousing/04_Data_Fabric_and_Architecture_Comparison.md) — data fabric vs data mesh, the Microsoft Fabric naming collision, a five-pattern decision framework
- **[Interview Questions & Answers](02_Databases/Data_Warehousing/Interview_Questions_and_Answers.md)** — 30 Q&A across warehouse fundamentals, layers/ODS, Inmon vs Kimball, marts, mesh, and fabric

### 07_DevOps › Git & GitHub — version control from zero to production-ready
- [00 — Learning Path](07_DevOps/Git_GitHub/00_Git_GitHub_Learning_Path.md) — the map of the series, Git vs GitHub in one sentence
- [01 — Introduction to Version Control](07_DevOps/Git_GitHub/01_Introduction_to_Version_Control.md) — why Git exists, installation, config, `git init`, core terminology
- [02 — Core Workflow: Add, Commit, Status, Log](07_DevOps/Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md) — the daily loop, `.gitignore`, commit message conventions
- [03 — Branching & Merging](07_DevOps/Git_GitHub/03_Branching_and_Merging.md) — branches, fast-forward vs three-way merges, a full hands-on merge conflict walkthrough
- [04 — Remotes: Push, Pull, Fetch, Clone](07_DevOps/Git_GitHub/04_Remotes_Push_Pull_Fetch_Clone.md) — tracking branches, SSH vs HTTPS auth, `origin`/`upstream`, force push dangers
- [05 — GitHub Essentials](07_DevOps/Git_GitHub/05_GitHub_Essentials.md) — Issues, Pull Requests end to end, forking, merge strategies
- [06 — Rebase, Cherry-Pick, Reset & Revert](07_DevOps/Git_GitHub/06_Rebase_Cherry_Pick_Reset_Revert.md) — rewriting history safely, interactive rebase, reflog recovery
- [07 — Stash, Tags & Other Commands](07_DevOps/Git_GitHub/07_Stash_Tags_and_Other_Commands.md) — `stash`, `tag`, `blame`, `bisect`, worktrees
- [08 — Branching Strategies & Collaboration](07_DevOps/Git_GitHub/08_Branching_Strategies_and_Collaboration.md) — Git Flow vs GitHub Flow vs trunk-based, branch protection, CODEOWNERS
- [09 — Production Best Practices & CI/CD](07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md) — Conventional Commits, hooks, GitHub Actions, secrets, Git LFS, signed commits
- [10 — Troubleshooting & Real-World Scenarios](07_DevOps/Git_GitHub/10_Troubleshooting_and_Real_World_Scenarios.md) — symptom-indexed fixes for every common Git disaster
- **[Interview Questions & Answers](07_DevOps/Git_GitHub/Interview_Questions_and_Answers.md)** — 46 Q&A from the core workflow to rebase vs revert, branching strategies, CI/CD, notebooks in Git, and "you broke production" scenarios

### 08_Databricks — the managed lakehouse platform (where modern Azure DE happens)
- [00 — Learning Path](08_Databricks/00_Databricks_Learning_Path.md) — the map of the module, prerequisites, and how it differs from the cert track
- [01 — What is Databricks?](08_Databricks/01_What_is_Databricks.md) — the platform, **control plane vs data plane**, workspace, runtime, why it exists
- [02 — Why Spark? Why Databricks?](08_Databricks/02_Why_Spark_Why_Databricks.md) — why Spark replaced MapReduce, and what Databricks adds on top
- [03 — Clusters & Compute](08_Databricks/03_Clusters_and_Compute.md) — all-purpose vs job clusters, pools, autoscaling, Photon, SQL warehouses, DBUs & cost
- [04 — Notebooks, Repos & Jobs](08_Databricks/04_Notebooks_Repos_and_Jobs.md) — notebooks, `dbutils`, widgets, Git Repos, secrets
- [05 — Databricks Workflows](08_Databricks/05_Databricks_Workflows.md) — Jobs, task graphs, job clusters, scheduling, DLT pipelines
- [06 — Unity Catalog](08_Databricks/06_Unity_Catalog.md) — governance: the three-level namespace, access control, masking/row filters, lineage
- [07 — Storage Access: ABFSS & Volumes](08_Databricks/07_Storage_Access_ABFSS_and_Volumes.md) — `abfss://` paths, Unity Catalog **Volumes**, External Locations & Storage Credentials, DBFS, legacy mounts
- [08 — Delta Live Tables (DLT)](08_Databricks/08_Delta_Live_Tables.md) — declarative pipelines, quality expectations, streaming tables vs materialized views, CDC
- [09 — Auto Loader & Ingestion](08_Databricks/09_Auto_Loader_and_Ingestion.md) — incremental file ingestion, schema evolution, file notification, `COPY INTO`
- [10 — Databricks & Spark Cost Optimization](08_Databricks/10_Databricks_Cost_Optimization.md) — DBUs, cluster sizing, autoscaling, spot, Photon, job vs all-purpose
- **[Interview Questions & Answers](08_Databricks/Interview_Questions_and_Answers.md)** — 30 Q&A across the whole module

### 09_Streaming — processing data in real time (Event Hubs, Kafka, Stream Analytics)
- [00 — Learning Path](09_Streaming/00_Streaming_Learning_Path.md) — the map, prerequisites, and how the pieces (pipe vs processor) fit together
- [01 — Streaming Fundamentals](09_Streaming/01_Streaming_Fundamentals.md) — batch vs stream, the event log, windows, watermarks, delivery semantics, **Lambda vs Kappa**
- [02 — Azure Event Hubs](09_Streaming/02_Azure_Event_Hubs.md) — managed event ingestion: partitions, consumer groups, throughput, Capture, the Kafka endpoint
- [03 — Apache Kafka](09_Streaming/03_Apache_Kafka.md) — the open-source streaming platform: topics, brokers, offsets, replication, exactly-once, the ecosystem
- [04 — Azure Stream Analytics](09_Streaming/04_Azure_Stream_Analytics.md) — SQL-based stream processing: inputs/outputs, windowing functions, reference data, Streaming Units
- [05 — KQL & Real-Time Intelligence](09_Streaming/05_KQL_and_Real_Time_Intelligence.md) — where events land to be queried instantly: **KQL**, Azure Data Explorer, and Fabric **Eventhouse/Eventstream** (a DP-700 topic)
- **[Interview Questions & Answers](09_Streaming/Interview_Questions_and_Answers.md)** — 30 Q&A across the whole module

### 10_Synapse_and_Fabric — Microsoft's analytics platforms (and Fabric, its successor)
- [00 — Learning Path](10_Synapse_and_Fabric/00_Learning_Path.md) — the map, prerequisites, and one-line orientation on all three platforms
- [01 — Azure Synapse Analytics](10_Synapse_and_Fabric/01_Azure_Synapse_Analytics.md) — the unified platform: SQL pools, Spark pools, pipelines, Synapse Studio, Synapse Link
- [02 — Dedicated vs Serverless SQL Pools](10_Synapse_and_Fabric/02_Dedicated_vs_Serverless_SQL_Pools.md) — **MPP internals, distribution (hash/round-robin/replicated)**, DWUs, loading, pay-per-query
- [03 — Microsoft Fabric](10_Synapse_and_Fabric/03_Microsoft_Fabric.md) — SaaS analytics, **OneLake**, workloads, **Direct Lake**, Lakehouse vs Warehouse items, capacities
- [04 — Synapse vs Fabric vs Databricks](10_Synapse_and_Fabric/04_Synapse_vs_Fabric_vs_Databricks.md) — the **decision framework** — which platform for which job
- **[Interview Questions & Answers](10_Synapse_and_Fabric/Interview_Questions_and_Answers.md)** — 26 Q&A across the whole module

### 18_Projects — hands-on, end-to-end (the part that gets you hired)
- [00 — Learning Path](18_Projects/00_Projects_Learning_Path.md) — why projects beat tutorials, the shared reference architecture
- [01 — Setup & Prerequisites](18_Projects/01_Project_Setup_and_Prerequisites.md) — Azure/Databricks/Git setup, secure ADLS access, repo structure, cost cleanup
- [02 — Project 1: Batch Medallion Pipeline](18_Projects/02_Project_1_Batch_Medallion_Pipeline.md) — ADLS → Databricks → Delta Bronze/Silver/Gold → Power BI, with SCD2 & quarantine · 🖥️ **[runnable repo](18_Projects/project_1_batch_medallion/README.md)** (PySpark + Delta, runs locally, with sample data + tests)
- [03 — Project 2: Streaming Pipeline](18_Projects/03_Project_2_Streaming_Pipeline.md) — Event Hubs → Structured Streaming → checkpointing, watermarking, exactly-once
- [04 — Project 3: Orchestrated ELT with ADF](18_Projects/04_Project_3_ADF_Orchestrated_ELT.md) — triggers, dependencies, retries, metadata-driven, alerting
- [05 — Portfolio & GitHub Presentation](18_Projects/05_Portfolio_and_GitHub_Presentation.md) — READMEs, résumé bullets, the 2-minute project walkthrough
- **[Interview Questions & Answers](18_Projects/Interview_Questions_and_Answers.md)** — 38 Q&A for **defending your project**: the 2-minute walkthrough, per-project follow-ups (idempotency, SCD2, watermarks, metadata-driven ADF), and résumé claims that survive scrutiny

### 11_Orchestration — scheduling & coordinating pipelines
- [00 — Learning Path](11_Orchestration/00_Orchestration_Learning_Path.md) · [01 — Fundamentals (DAGs, idempotency, backfill)](11_Orchestration/01_Orchestration_Fundamentals.md)
- [02 — ADF Orchestration (triggers, metadata-driven)](11_Orchestration/02_ADF_Orchestration.md) · [03 — Apache Airflow](11_Orchestration/03_Apache_Airflow.md) · [Databricks Workflows](08_Databricks/05_Databricks_Workflows.md) *(in the Databricks module)*
- **[Interview Questions & Answers](11_Orchestration/Interview_Questions_and_Answers.md)**

### 12_Monitoring_and_Observability — knowing your pipelines (and data) are healthy
- [00 — Learning Path](12_Monitoring_and_Observability/00_Monitoring_Learning_Path.md) · [01 — Monitoring Fundamentals (SLIs/SLOs/alerting)](12_Monitoring_and_Observability/01_Monitoring_Fundamentals.md)
- [02 — Azure Monitor & Log Analytics (KQL)](12_Monitoring_and_Observability/02_Azure_Monitor_and_Log_Analytics.md) · [03 — Pipeline Reliability](12_Monitoring_and_Observability/03_Pipeline_Reliability.md) · [04 — Data Observability (5 pillars)](12_Monitoring_and_Observability/04_Data_Observability.md)
- **[Interview Questions & Answers](12_Monitoring_and_Observability/Interview_Questions_and_Answers.md)**

### 13_dbt — SQL transformations with software-engineering discipline
- [00 — Learning Path](13_dbt/00_dbt_Learning_Path.md) · [01 — What is dbt](13_dbt/01_What_is_dbt.md) · [02 — Models & refs](13_dbt/02_Models_and_Refs.md)
- [03 — Tests & Documentation](13_dbt/03_Tests_and_Documentation.md) · [04 — Snapshots, Seeds & Macros (SCD2)](13_dbt/04_Snapshots_Seeds_Macros.md) · [05 — dbt in Azure](13_dbt/05_dbt_in_Azure.md)
- **[Interview Questions & Answers](13_dbt/Interview_Questions_and_Answers.md)**

### 14_Testing_and_DataOps — proving pipelines correct and shipping them safely
- [00 — Learning Path](14_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md) · [01 — Testing Pipelines (pytest/chispa)](14_Testing_and_DataOps/01_Testing_Data_Pipelines.md)
- [02 — Data Quality Testing (Great Expectations)](14_Testing_and_DataOps/02_Data_Quality_Testing.md) · [03 — Data Contracts](14_Testing_and_DataOps/03_Data_Contracts.md) · [04 — DataOps & CI/CD for Data](14_Testing_and_DataOps/04_DataOps_and_CICD_for_Data.md)
- [05 — CI/CD for ADF & Databricks](14_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md) — the concrete how-to: ADF ARM release flow, Databricks **Asset Bundles**, GitHub Actions/Azure DevOps
- **[Interview Questions & Answers](14_Testing_and_DataOps/Interview_Questions_and_Answers.md)**

### 15_Cost_and_Performance — FinOps and making pipelines fast & cheap
- [00 — Learning Path](15_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md) · [01 — Cost Fundamentals (FinOps)](15_Cost_and_Performance/01_Cost_Fundamentals_FinOps.md)
- [02 — Storage & Query Cost](15_Cost_and_Performance/02_Storage_and_Query_Cost.md) · [03 — Performance Optimization (shuffle/skew)](15_Cost_and_Performance/03_Performance_Optimization.md) · [Databricks/Spark Cost](08_Databricks/10_Databricks_Cost_Optimization.md) *(in the Databricks module)*
- **[Interview Questions & Answers](15_Cost_and_Performance/Interview_Questions_and_Answers.md)**

### 16_Power_BI_for_Engineers — serving the Gold layer to the business
- [00 — Learning Path](16_Power_BI_for_Engineers/00_Power_BI_Learning_Path.md) · [01 — Fundamentals](16_Power_BI_for_Engineers/01_Power_BI_Fundamentals.md) · [02 — Semantic Model & Star Schema](16_Power_BI_for_Engineers/02_Semantic_Model_and_Star_Schema.md)
- [03 — DAX Basics](16_Power_BI_for_Engineers/03_DAX_Basics.md) · [04 — Serving from the Lakehouse (Direct Lake)](16_Power_BI_for_Engineers/04_Serving_from_the_Lakehouse.md)
- **[Interview Questions & Answers](16_Power_BI_for_Engineers/Interview_Questions_and_Answers.md)**

### 17_System_Design — the senior interview filter: "design a data platform for X"
- [00 — Learning Path](17_System_Design/00_System_Design_Learning_Path.md) · [01 — The Design Framework](17_System_Design/01_Design_Framework.md)
- [02 — Batch Pipeline Design](17_System_Design/02_Batch_Pipeline_Design.md) · [03 — Streaming & Real-Time Design (Lambda/Kappa)](17_System_Design/03_Streaming_and_Realtime_Design.md) · [04 — Case Studies](17_System_Design/04_Case_Studies.md)
- **[Interview Questions & Answers](17_System_Design/Interview_Questions_and_Answers.md)**

---

## Certificates & Exams

A separate self-contained track outside the main learning path, for certification prep specifically.

### AZ-900 — Microsoft Azure Fundamentals
- [00 — Study Guide Overview](Certifications/AZ_900/00_AZ900_Study_Guide_Overview.md) — exam format, domain weights, and the study plan — start here
- [01 — Cloud Concepts](Certifications/AZ_900/01_Cloud_Concepts.md) — benefits, CapEx/OpEx, IaaS/PaaS/SaaS, deployment models
- [02 — Azure Architecture Fundamentals](Certifications/AZ_900/02_Azure_Architecture_Fundamentals.md) — regions, zones, resource groups, subscriptions, ARM
- [03 — Azure Compute Services](Certifications/AZ_900/03_Azure_Compute_Services.md) — VMs, App Service, containers, AKS, Functions
- [04 — Azure Networking Services](Certifications/AZ_900/04_Azure_Networking_Services.md) — VNets, VPN Gateway, ExpressRoute, load balancing options
- [05 — Azure Storage Services](Certifications/AZ_900/05_Azure_Storage_Services.md) — Blob/Files/Table/Queue, tiers, redundancy (LRS–RA-GZRS)
- [06 — Identity, Access & Security](Certifications/AZ_900/06_Identity_Access_Security.md) — Entra ID, RBAC, Zero Trust, Defender, Sentinel
- [07 — Cost Management](Certifications/AZ_900/07_Cost_Management.md) — pricing tools, Reserved/Spot instances, budgets
- [08 — Governance & Compliance](Certifications/AZ_900/08_Governance_and_Compliance.md) — Azure Policy, resource locks, Blueprints, Purview
- [09 — Monitoring & Management Tools](Certifications/AZ_900/09_Monitoring_and_Management_Tools.md) — Portal/CLI/Cloud Shell, ARM vs Bicep, Advisor vs Service Health
- [10 — Practice Questions by Domain](Certifications/AZ_900/10_Practice_Questions_by_Domain.md) — 40 questions with explanations
- [11 — Most Asked & Tricky Questions](Certifications/AZ_900/11_Most_Asked_and_Tricky_Exam_Questions.md) — the 15 comparison pairs that decide most wrong answers
- [12 — Final Mock Exam](Certifications/AZ_900/12_Final_Mock_Exam.md) — a timed 50-question simulation with a scoring guide
- [13 — Exam Dump: Practice Set](Certifications/AZ_900/13_Exam_Dump_Practice_Set.md) — 30 extra exam-style Q&A with explanations

### DP-900 — Microsoft Azure Data Fundamentals
The data counterpart to AZ-900 — the ideal foundational entry point to the data track.
- [00 — Study Guide Overview](Certifications/DP_900/00_DP900_Study_Guide_Overview.md) — exam format, four domains, study plan — start here
- [01 — Core Data Concepts](Certifications/DP_900/01_Core_Data_Concepts.md) — structured/semi/unstructured, OLTP vs OLAP, batch vs stream, data roles
- [02 — Relational Data on Azure](Certifications/DP_900/02_Relational_Data_on_Azure.md) — SQL categories, Azure SQL Database / MI / VM, PostgreSQL/MySQL
- [03 — Non-Relational Data on Azure](Certifications/DP_900/03_Non_Relational_Data_on_Azure.md) — Storage services, blob tiers, Cosmos DB & its APIs
- [04 — Analytics Workloads on Azure](Certifications/DP_900/04_Analytics_Workloads_on_Azure.md) — ADF, Synapse, Databricks, Fabric, Power BI, ETL/ELT
- [05 — Practice Questions by Domain](Certifications/DP_900/05_Practice_Questions_by_Domain.md) · [06 — Most Asked & Tricky](Certifications/DP_900/06_Most_Asked_and_Tricky_Questions.md) · [07 — Final Mock Exam](Certifications/DP_900/07_Final_Mock_Exam.md) · [08 — Exam Dump: Practice Set](Certifications/DP_900/08_Exam_Dump_Practice_Set.md)

### Databricks Certified Data Engineer Associate
The hands-on Spark/Delta credential — the practical counterpart to the Microsoft certs, focused on the Databricks Lakehouse Platform.
- [00 — Study Guide Overview](Certifications/Databricks_Data_Engineer_Associate/00_Study_Guide_Overview.md) — exam format, domain weights, and study plan — start here
- [01 — Lakehouse Platform Fundamentals](Certifications/Databricks_Data_Engineer_Associate/01_Lakehouse_Platform_Fundamentals.md) — the platform, control plane vs data plane, workspace, Repos
- [02 — Workspace, Clusters, Notebooks & Repos](Certifications/Databricks_Data_Engineer_Associate/02_Workspace_Clusters_Notebooks_Repos.md) — compute, notebooks, Git integration
- [03 — Delta Lake Fundamentals](Certifications/Databricks_Data_Engineer_Associate/03_Delta_Lake_Fundamentals.md) — ACID, transaction log, time travel, OPTIMIZE/VACUUM
- [04 — ELT with Spark SQL](Certifications/Databricks_Data_Engineer_Associate/04_ELT_with_Spark_SQL.md) — CTAS, views, MERGE, higher-order functions
- [05 — ELT with PySpark & Python](Certifications/Databricks_Data_Engineer_Associate/05_ELT_with_PySpark_and_Python.md) — DataFrames, UDFs, control flow
- [06 — Structured Streaming](Certifications/Databricks_Data_Engineer_Associate/06_Structured_Streaming.md) — readStream/writeStream, checkpoints, triggers
- [07 — Auto Loader & Multi-Hop](Certifications/Databricks_Data_Engineer_Associate/07_Auto_Loader_and_Multi_Hop.md) — incremental ingestion + the medallion architecture
- [08 — Delta Live Tables](Certifications/Databricks_Data_Engineer_Associate/08_Delta_Live_Tables.md) — declarative pipelines, expectations, streaming tables vs materialized views
- [09 — Production Pipelines & Jobs](Certifications/Databricks_Data_Engineer_Associate/09_Production_Pipelines_Jobs.md) — Workflows, scheduling, dependencies, alerts
- [10 — Data Governance & Unity Catalog](Certifications/Databricks_Data_Engineer_Associate/10_Data_Governance_Unity_Catalog.md) — the three-level namespace, access control, lineage
- [11 — Practice Questions by Domain](Certifications/Databricks_Data_Engineer_Associate/11_Practice_Questions_by_Domain.md) · [12 — Most Asked & Tricky](Certifications/Databricks_Data_Engineer_Associate/12_Most_Asked_and_Tricky_Exam_Questions.md) · [13 — Final Mock Exam](Certifications/Databricks_Data_Engineer_Associate/13_Final_Mock_Exam.md) · [14 — Exam Dump: Practice Set](Certifications/Databricks_Data_Engineer_Associate/14_Exam_Dump_Practice_Set.md)

### DP-700 — Microsoft Fabric Data Engineer Associate
The associate-level flagship — **the cert that replaced the retired DP-203** as Microsoft's forward-looking data-engineering credential.
- [00 — Study Guide Overview](Certifications/DP_700_Fabric_Data_Engineer/00_DP700_Study_Guide_Overview.md) — exam format, three domains, prerequisites, study plan — start here
- [01 — Fabric & Workspace Fundamentals](Certifications/DP_700_Fabric_Data_Engineer/01_Fabric_and_Workspace_Fundamentals.md) — OneLake, items, workspaces, shortcuts, mirroring, capacity
- [02 — Security, Governance & Lifecycle](Certifications/DP_700_Fabric_Data_Engineer/02_Security_Governance_and_Lifecycle.md) — roles, RLS/CLS/OLS/DDM, sensitivity labels, Git, deployment pipelines
- [03 — Ingest Data](Certifications/DP_700_Fabric_Data_Engineer/03_Ingest_Data.md) — pipelines, Dataflow Gen2, notebooks, Eventstream, load patterns
- [04 — Transform Data](Certifications/DP_700_Fabric_Data_Engineer/04_Transform_Data.md) — Spark/T-SQL/KQL, MERGE/upsert, SCD, windowing
- [05 — Monitor & Optimize](Certifications/DP_700_Fabric_Data_Engineer/05_Monitor_and_Optimize.md) — Monitoring hub, Capacity Metrics, OPTIMIZE/V-Order, troubleshooting
- [06 — Practice Questions by Domain](Certifications/DP_700_Fabric_Data_Engineer/06_Practice_Questions_by_Domain.md) · [07 — Most Asked & Tricky](Certifications/DP_700_Fabric_Data_Engineer/07_Most_Asked_and_Tricky_Questions.md) · [08 — Final Mock Exam](Certifications/DP_700_Fabric_Data_Engineer/08_Final_Mock_Exam.md) · [09 — Exam Dump: Practice Set](Certifications/DP_700_Fabric_Data_Engineer/09_Exam_Dump_Practice_Set.md)

---

## Roadmap (coming later)

Following the typical Azure Data Engineer learning path (aligned with the modern **DP-700 Fabric Data Engineer** certification, which replaced the retired DP-203). See the **[ROADMAP](ROADMAP.md)** for the full zero-to-job-ready plan.

**Recently added ✅**
- **[02_Databases › NoSQL](02_Databases/NoSQL/00_NoSQL_Learning_Path.md)** — key-value, document, wide-column, graph, CAP, Cosmos DB
- **[18_Projects](18_Projects/00_Projects_Learning_Path.md)** — hands-on end-to-end pipelines + portfolio presentation
- **[11_Orchestration](11_Orchestration/00_Orchestration_Learning_Path.md)** — ADF triggers, Databricks Workflows, Apache Airflow
- **[12_Monitoring_and_Observability](12_Monitoring_and_Observability/00_Monitoring_Learning_Path.md)** — Azure Monitor/KQL, reliability, data observability
- **[13_dbt](13_dbt/00_dbt_Learning_Path.md)** — models, tests, docs, snapshots (SCD2), dbt in Azure
- **[14_Testing_and_DataOps](14_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)** — pipeline testing, data quality, data contracts, CI/CD for data
- **[15_Cost_and_Performance](15_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md)** — FinOps, Databricks/Spark cost, performance tuning
- **[16_Power_BI_for_Engineers](16_Power_BI_for_Engineers/00_Power_BI_Learning_Path.md)** — semantic models, star schema, DAX, Direct Lake serving
- **[17_System_Design](17_System_Design/00_System_Design_Learning_Path.md)** — the design framework, batch/streaming design, case studies
- **[07_DevOps › Git & GitHub](07_DevOps/Git_GitHub/00_Git_GitHub_Learning_Path.md)** — version control from zero to production-ready (branching, remotes, CI/CD, troubleshooting)

Topics are grouped into numbered **category folders** (`01_Foundations` → `18_Projects`) so related material lives together, and the category numbers still suggest a reading order. The `Certifications/` and `Job Interviews/` folders sit outside the numbered learning path as separate tracks.

---

## Interview Prep

For focused, concise interview revision (Azure Data Engineer, 5+ yrs), see the **[Job Interviews](Job%20Interviews/README.md)** handbook — 31 topic folders covering ADF, Databricks, PySpark, SQL, Delta Lake, Synapse, streaming, IaC, and more, each with Q&A, scenarios, code, and cheat sheets.
