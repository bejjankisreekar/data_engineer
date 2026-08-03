# Glossary

Plain-language definitions for words that show up again and again in these notes. If a topic file uses a term without re-explaining it, it's probably here.

Terms are grouped by theme, not alphabetically, so related ideas sit together.

---

## Data basics

**Data** — any recorded fact: a name, a price, a date, a click on a website.

**Table** — data arranged in rows and columns, like a spreadsheet tab.

**Row (record)** — one entry in a table. One employee, one order, one transaction.

**Column (field/attribute)** — one piece of information collected for every row (e.g. "Salary" is a column, every employee has one).

**Schema** — the "shape" of the data: which columns exist and what type of value each one holds (text, number, date). Think of it as the labeled columns on a printed form — the schema says the form *has* a "Name" box and a "Date" box, before anyone fills them in.

**Structured / Semi-structured / Unstructured data**
- Structured: fits neatly into rows and columns (a SQL table, a CSV file).
- Semi-structured: has some organization but not a fixed grid (JSON, XML — think of a form with optional sections).
- Unstructured: no fixed organization at all (an email, a photo, a PDF).

---

## Databases and transactions

**Database** — a system for storing and retrieving data reliably. See [SQL Database](02_Databases/SQL/02_SQL_Database.md).

**Primary key** — the column that uniquely identifies each row, like an employee ID or a passport number. No two rows can share one. See [SQL Keys and Joins](02_Databases/SQL/07_SQL_Keys_and_Joins.md).

**Foreign key** — a column in one table that points to the primary key in another table, the way an invoice references a customer number instead of repeating the customer's full details.

**Join** — combining rows from two tables using a shared key, similar to matching a claim form to a customer record using their account number.

**Normalization** — organizing data so each fact is stored only once (e.g. a customer's address lives in one "Customers" table, not copied into every order). Reduces duplication and inconsistency.

**Transaction** — a single unit of work, such as "transfer money from Account A to Account B." Either the whole thing happens, or none of it does.

**ACID** — four guarantees a database makes about transactions, so they're trustworthy:
- **A**tomicity — a transaction fully happens or fully doesn't (no half-finished transfers).
- **C**onsistency — data always follows the rules (an account balance can't go negative if that's against policy).
- **I**solation — transactions happening at the same time don't interfere with each other.
- **D**urability — once saved, data survives even a power cut.

**OLTP (Online Transaction Processing)** — systems built for many small, fast read/write operations, like a bank teller processing a deposit. This is what a [SQL Database](02_Databases/SQL/02_SQL_Database.md) is optimized for.

**OLAP (Online Analytical Processing)** — systems built for large, complex questions across huge amounts of historical data, like "what were total sales by region last year?" This is what a [SQL Warehouse](02_Databases/SQL/13_SQL_Warehouse.md) is optimized for.

---

## SQL command categories

Every SQL statement belongs to one of five categories. Full explanations live in [What is SQL](02_Databases/SQL/01_What_is_SQL.md); short definitions here:

**DDL (Data Definition Language)** — commands that define or change a table's *structure*: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`. See [04_SQL_DDL.md](02_Databases/SQL/04_SQL_DDL.md).

**DML (Data Manipulation Language)** — commands that change the *data* inside a table: `INSERT`, `UPDATE`, `DELETE`. See [05_SQL_DML.md](02_Databases/SQL/05_SQL_DML.md).

**DQL (Data Query Language)** — commands that *read* data without changing it: `SELECT`. See [06_SQL_DQL.md](02_Databases/SQL/06_SQL_DQL.md).

**DCL (Data Control Language)** — commands that manage *permissions*: `GRANT`, `REVOKE`. See [12_SQL_DCL_TCL.md](02_Databases/SQL/12_SQL_DCL_TCL.md).

**TCL (Transaction Control Language)** — commands that manage how a group of changes is saved or undone: `COMMIT`, `ROLLBACK`, `SAVEPOINT`. See [12_SQL_DCL_TCL.md](02_Databases/SQL/12_SQL_DCL_TCL.md).

**View** — a saved query that behaves like a table, recalculated fresh every time it's used. See [10_SQL_Views.md](02_Databases/SQL/10_SQL_Views.md).

**Index** — a behind-the-scenes lookup structure that speeds up finding rows, like a textbook's index. See [11_SQL_Indexes.md](02_Databases/SQL/11_SQL_Indexes.md).

**Subquery** — a query nested inside another query, used when the outer query depends on a value the inner query calculates first. See [09_SQL_Subqueries.md](02_Databases/SQL/09_SQL_Subqueries.md).

---

## Storage and files

**File format** — the way data is physically written to a file (CSV, JSON, Parquet, Avro, ORC are all file formats).

**Row-based storage** — data is stored one full row at a time, like reading a filing cabinet folder by folder, one employee's entire file at once.

**Columnar storage** — data is stored one column at a time, like flipping through a single index card that only lists everyone's salary. Faster when you only need a few columns out of many.

**Compression** — shrinking file size by removing repetition, similar to summarizing a long report so it takes up less space, without losing the information.

**Data Lake** — a large storage area that holds raw data of any kind (structured, semi-structured, unstructured), before it's been cleaned or organized. Think of it as a big warehouse room where boxes arrive as-is, unsorted. See [Data Lake vs Warehouse vs Database](04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md).

**Blob** — Azure's term for "a file stored in the cloud" (Binary Large OBject). See [Azure Blob Storage](04_Storage_and_Formats/Data_Storage/02_Azure_Blob_Storage.md).

---

## Moving and processing data

**Pipeline** — an automated sequence of steps that moves data from one place to another, similar to an assembly line: extract from the source, transform it, load it into the destination.

**ETL (Extract, Transform, Load)** — extract data from a source, clean/reshape it *before* loading it into its destination. See [ETL vs ELT](05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md).

**ELT (Extract, Load, Transform)** — extract data, load it into the destination first, and transform it there afterward. Common with modern cloud warehouses that have plenty of processing power.

**Batch processing** — processing data in scheduled chunks (e.g. once every night), like a bank running end-of-day settlement.

**Streaming (real-time) processing** — processing data the instant it arrives, like a fraud-detection system checking a card swipe as it happens.

**Ingestion** — the act of bringing data into a system from an external source (a database, an API, a file drop).

---

## Azure-specific terms

**Azure Data Factory (ADF)** — Azure's tool for building and scheduling data pipelines, largely through a drag-and-drop interface. See [Azure Data Factory](05_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md).

**Azure Data Lake Storage (ADLS)** — Azure Blob Storage with extra features (folder structure, fine-grained permissions) tuned for big-data analytics. See [Azure Data Lake Storage](04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md).

**Azure Synapse Analytics** — Microsoft's cloud data warehouse and analytics service (successor to Azure SQL Data Warehouse).

**Azure Databricks** — a managed Apache Spark environment on Azure, used for large-scale data processing and machine learning.

**Delta Lake** — a storage layer (used heavily in Databricks) that adds database-like reliability (ACID transactions) on top of a data lake.

---

## Distributed systems and Spark

**Cluster / Node** — a group of machines working together as one system; each machine is a node. See [Distributed Computing](01_Foundations/Fundamentals/03_Distributed_Computing.md).

**Scale up vs scale out** — buying a bigger machine vs adding more machines. Big data tooling is built around scaling out.

**Partition** — one chunk of a dataset, small enough for one worker/core to process; the unit of parallelism in Spark and the unit of pruning in storage.

**Shuffle** — redistributing data across the cluster by key (for GROUP BY, JOIN) — the most expensive operation in distributed processing. See [Spark Processing](06_Programming/PySpark/Spark_Processing.md).

**Data skew** — when one key/partition holds far more data than the rest, so one worker becomes the bottleneck ("the job is 99% done for an hour").

**Driver / Executor** — Spark's master and workers: the driver plans and schedules; executors run tasks and hold cached data. See [Spark Architecture](06_Programming/PySpark/Spark_Architecture.md).

**Lazy evaluation** — Spark records transformations without running them, then optimizes and executes the whole plan when an action (count, write) triggers it.

**DAG (Directed Acyclic Graph)** — the dependency graph of operations an engine builds from your code before executing it.

**Broadcast join** — shipping a small table to every worker so a join needs no shuffle of the big table.

**Idempotent** — safe to run twice: re-running produces the same result instead of duplicating data. The core property of production pipelines.

**Exactly-once / at-least-once** — delivery guarantees: whether a record can be processed twice on retry. "At-least-once + idempotent writes" is how pipelines fake exactly-once.

**CDC (Change Data Capture)** — streaming inserts/updates/deletes out of a database by reading its transaction log, instead of repeatedly querying tables.

**Watermark** — the saved "high-water mark" (e.g. max `modified_at`) an incremental load uses to fetch only new/changed rows next run.

**Medallion (bronze/silver/gold)** — lakehouse layering: raw as-arrived → cleaned/typed → business-ready aggregates, with each boundary a quality contract. See [Medallion Architecture](04_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md).

**Lakehouse** — data-lake storage + a table format (Delta/Iceberg) giving warehouse behavior (ACID, schema, time travel) on one copy of data.

**Star schema / Fact / Dimension** — warehouse modeling: a central numeric fact table joined to descriptive dimension tables. See [SQL Warehouse](02_Databases/SQL/13_SQL_Warehouse.md).

**SCD (Slowly Changing Dimension)** — how to store history when a dimension attribute changes; Type 2 (new row with validity dates) is the default.

**Surrogate key** — a meaningless generated ID used to join facts to dimensions, insulating the model from source-system key changes.

---

## Cloud terms

**Region / Availability Zone** — a metro-area group of datacenters / one independent facility within it. See [Public, Private & Hybrid Cloud](03_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md).

**IaaS / PaaS / SaaS** — how much of the stack you rent: raw VMs / a managed platform for your code and data / finished software. See [SaaS, PaaS, IaaS](03_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md).

**Serverless** — compute that scales to zero and bills per use; you never size or manage instances.

**Managed identity** — an Azure service's own Entra ID identity, letting it access storage/databases with no stored password.

**RBAC (Role-Based Access Control)** — granting permissions via roles scoped to resources ("this factory may read this container").

**Private endpoint / Private Link** — projecting an Azure PaaS service (Storage, Key Vault, SQL…) as a private IP inside your VNet so traffic never touches the public internet; with public access disabled, the service is reachable only from the network. See [Network Security & Private Connectivity](05_Data_Engineering/Data_Governance/02_Network_Security_and_Private_Connectivity.md).

**Egress** — data leaving a cloud region/provider — the direction that costs money and shapes architectures.

**DBU (Databricks Unit)** — Databricks' normalized billing unit for compute consumption, charged on top of VM cost.

**RPO / RTO** — how much data you may lose / how long recovery takes, in a failover. The two numbers behind every disaster-recovery design.

---

## NoSQL and consistency

**NoSQL** — databases that don't use the relational table model, built for scale and flexible/changing data. Four families: key-value, document, wide-column, graph. See [What is NoSQL](02_Databases/NoSQL/01_What_is_NoSQL.md).

**Denormalization** — deliberately duplicating data (the opposite of normalization) so a read needs fewer joins. Standard practice in NoSQL and analytics, where read speed beats storage savings.

**CAP theorem** — in a distributed store, when the network splits you can keep only two of Consistency, Availability, Partition-tolerance — in practice a choice between CP and AP. See [CAP Theorem & Consistency](02_Databases/NoSQL/06_CAP_Theorem_and_Consistency.md).

**BASE** — the NoSQL counterpart to ACID: **B**asically **A**vailable, **S**oft state, **E**ventual consistency — trades strict guarantees for availability and scale.

**Eventual consistency** — after a write, replicas converge to the same value *given enough time*; a read right after a write may briefly return the old value.

**Partition key** — the field a NoSQL store hashes to decide which physical partition a row lives on; choosing it well is what keeps load even and queries fast (Cosmos DB, Cassandra, Event Hubs).

**RU (Request Unit)** — Azure Cosmos DB's normalized currency for throughput; every read/write/query costs some RUs and you provision (or autoscale) RUs per second. See [Azure Cosmos DB](02_Databases/NoSQL/08_Azure_Cosmos_DB.md).

---

## Delta Lake and lakehouse operations

**Transaction log (`_delta_log`)** — the ordered record of every change to a Delta table; it's what gives a pile of Parquet files ACID guarantees, time travel, and concurrent-write safety. See [Delta Lake](04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md).

**Time travel** — querying a Delta table *as of* an earlier version or timestamp, using the transaction log — for audits, debugging, and reproducible reports.

**MERGE (upsert)** — a single statement that inserts new rows and updates matching existing ones ("update if present, else insert") — the backbone of incremental loads and SCD2. See [Delta Table](04_Storage_and_Formats/Lakehouse/02_Delta_Table.md).

**OPTIMIZE** — compacts many small Delta files into fewer large ones to speed up reads (the "small-file problem" fix).

**Z-ordering** — co-locating related values in the same files during OPTIMIZE so queries can skip more data when filtering on those columns.

**VACUUM** — permanently deletes data files no longer referenced by the transaction log, past a retention window — reclaims storage but removes older time-travel versions.

**Schema evolution** — letting a table's schema change over time (e.g. a new column) without rewriting existing data or breaking the pipeline.

**Change Data Feed (CDF)** — a Delta feature that exposes the row-level inserts/updates/deletes between versions, so downstream tables can consume just what changed.

---

## Databricks platform

**Control plane vs data plane** — Databricks' split: the control plane (Databricks' account — UI, job scheduling, metadata) manages things; the data plane (your cloud subscription — clusters, storage) is where your data and compute actually live. See [What is Databricks](08_Databricks/01_What_is_Databricks.md).

**Unity Catalog** — Databricks' central governance layer: a three-level `catalog.schema.table` namespace with access control, lineage, and masking across workspaces. See [Unity Catalog](08_Databricks/04_Unity_Catalog.md).

**Delta Live Tables (DLT)** — a declarative framework where you define the tables you want and their quality *expectations*, and Databricks manages the pipeline, dependencies, and infrastructure. See [Delta Live Tables](08_Databricks/05_Delta_Live_Tables.md).

**Auto Loader** — Databricks' tool for incrementally and reliably ingesting new files as they land in cloud storage, with automatic schema inference and evolution. See [Auto Loader & Ingestion](08_Databricks/06_Auto_Loader_and_Ingestion.md).

**Photon** — Databricks' vectorized, C++ query engine that speeds up SQL/DataFrame workloads without code changes.

**Job cluster vs all-purpose cluster** — a job cluster spins up for one automated job and terminates after (cheaper); an all-purpose cluster is shared and interactive (for notebooks/exploration). See [Clusters & Compute](08_Databricks/02_Clusters_and_Compute.md).

**Asset Bundles (DABs)** — Databricks' way to define jobs, notebooks, DLT pipelines, and cluster config as code in a `databricks.yml`, deployed per environment via `databricks bundle deploy` — the modern basis for Databricks CI/CD. See [CI/CD for ADF & Databricks](15_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md).

---

## Streaming

**Checkpoint** — the saved progress of a streaming query (which data it has already processed) that lets it restart exactly where it left off after a failure. See [Structured Streaming](06_Programming/PySpark/13_Structured_Streaming.md).

**Windowing (tumbling / sliding / session)** — grouping unbounded stream events into finite time buckets so you can aggregate them ("count per 5-minute window"). See [Streaming Fundamentals](09_Streaming/01_Streaming_Fundamentals.md).

**Consumer group** — a named set of consumers that reads a stream independently of other groups, each tracking its own position — so many apps can read the same events. See [Azure Event Hubs](09_Streaming/02_Azure_Event_Hubs.md).

**Offset** — a consumer's bookmark: the position of the last event it read in a partition, so it can resume without re-reading or skipping. See [Apache Kafka](09_Streaming/03_Apache_Kafka.md).

**Lambda vs Kappa architecture** — two designs for combining batch + streaming: Lambda runs separate batch and speed layers; Kappa uses one streaming path for both. See [Streaming Fundamentals](09_Streaming/01_Streaming_Fundamentals.md).

**KQL (Kusto Query Language)** — the pipe-based read query language of Azure Data Explorer, Log Analytics, and Fabric Eventhouse, built for fast analytics over large append-only event/log data. See [KQL & Real-Time Intelligence](09_Streaming/05_KQL_and_Real_Time_Intelligence.md).

**Real-Time Intelligence / Eventhouse** — Microsoft Fabric's real-time workload: an **Eventstream** routes events into an **Eventhouse (KQL database)** for sub-second queries, feeding live dashboards and event-driven alerts. The same Kusto engine as Azure Data Explorer.

---

## Synapse and Microsoft Fabric

**MPP (Massively Parallel Processing)** — splitting a query across many compute nodes that each work on a slice of the data in parallel — how a dedicated SQL pool scales. See [Dedicated vs Serverless SQL Pools](10_Synapse_and_Fabric/02_Dedicated_vs_Serverless_SQL_Pools.md).

**Distribution (hash / round-robin / replicated)** — how a dedicated SQL pool spreads a table's rows across its nodes; a good choice minimizes data movement during joins.

**DWU (Data Warehouse Unit)** — the unit you scale a dedicated SQL pool by, bundling compute, memory, and I/O.

**OneLake** — Microsoft Fabric's single, tenant-wide data lake — "one copy" of data that every Fabric workload shares. See [Microsoft Fabric](10_Synapse_and_Fabric/03_Microsoft_Fabric.md).

**Direct Lake** — Fabric's Power BI mode that reads Delta tables straight from OneLake — import-like speed without importing, DirectQuery-like freshness without the per-query round-trip.

---

## Orchestration, testing and DataOps

**Backfill** — running a pipeline over historical dates it missed or that changed, to (re)populate past partitions. See [Orchestration Fundamentals](12_Orchestration/01_Orchestration_Fundamentals.md).

**Trigger** — what starts a pipeline run: a schedule, a tumbling window, or an event (e.g. a file landing). See [ADF Orchestration](12_Orchestration/02_ADF_Orchestration.md).

**Data contract** — an agreed, enforced schema-and-expectations promise between a data producer and its consumers, so upstream changes don't silently break downstream. See [Data Contracts](15_Testing_and_DataOps/03_Data_Contracts.md).

**DataOps** — applying DevOps discipline (version control, testing, CI/CD, monitoring) to data pipelines. See [DataOps & CI/CD for Data](15_Testing_and_DataOps/04_DataOps_and_CICD_for_Data.md).

**CI/CD (Continuous Integration / Continuous Delivery)** — automatically testing every change and shipping it through environments, so releases are frequent, small, and safe. See [Production Best Practices & CI/CD](07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md).

---

## Data quality, governance and observability

**Data quality dimensions** — the yardsticks for "good" data: completeness, accuracy, consistency, timeliness, validity, uniqueness. See [Data Quality Fundamentals](05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md).

**Expectations** — declarative rules that data must satisfy (e.g. "`amount` is never null"); rows that fail can be dropped, quarantined, or fail the run. Used by DLT and Great Expectations.

**Quarantine** — routing rows that fail validation to a separate location for inspection instead of dropping them or letting them poison the clean table.

**Data lineage** — the tracked path of data from source through every transformation to its final use — for impact analysis, debugging, and compliance.

**Data observability** — continuously monitoring the *health of the data itself* (freshness, volume, schema, distribution, lineage — the "five pillars"), not just whether the job ran. See [Data Observability](13_Monitoring_and_Observability/04_Data_Observability.md).

**SLI / SLO** — a Service Level Indicator is a measured signal (e.g. pipeline freshness); a Service Level Objective is the target for it ("data is <2h old, 99% of days"). See [Monitoring Fundamentals](13_Monitoring_and_Observability/01_Monitoring_Fundamentals.md).

**Purview** — Microsoft's data-governance service: cataloging, classification, and lineage across the estate. See [Data Governance & Security](05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md).

**Key Vault** — Azure's managed store for secrets, keys, and certificates, so pipelines never hard-code passwords or connection strings.

**ACL (Access Control List)** — fine-grained, per-file/folder permissions on ADLS Gen2, layered on top of coarse-grained RBAC.

**GDPR** — EU data-protection regulation; in practice it drives requirements like the "right to be forgotten" (deleting a person's data on request), which shapes lakehouse design.

---

## dbt and analytics engineering

**dbt (data build tool)** — a tool for transforming data *in the warehouse* with version-controlled SQL `SELECT`s, plus built-in testing and documentation. See [What is dbt](14_dbt/01_What_is_dbt.md).

**Model** — in dbt, a single `SELECT` statement in a `.sql` file that dbt materializes as a view or table. See [Models & refs](14_dbt/02_Models_and_Refs.md).

**ref()** — the dbt function models use to reference each other; it builds the dependency DAG and lets dbt figure out build order automatically.

**Snapshot** — dbt's mechanism for capturing how a mutable source row changes over time — i.e. it implements SCD Type 2. See [Snapshots, Seeds & Macros](14_dbt/04_Snapshots_Seeds_Macros.md).

**Macro** — a reusable, parameterized SQL snippet (Jinja) in dbt — the DRY building block for repeated logic.

---

## Power BI and serving

**Semantic model (dataset)** — the modeled layer Power BI queries: tables, relationships, and measures that turn raw Gold tables into business-friendly metrics. See [Semantic Model & Star Schema](17_Power_BI_for_Engineers/02_Semantic_Model_and_Star_Schema.md).

**DAX (Data Analysis Expressions)** — Power BI's formula language for calculated measures and columns (e.g. year-over-year growth). See [DAX Basics](17_Power_BI_for_Engineers/03_DAX_Basics.md).

**Import vs DirectQuery vs Direct Lake** — three ways Power BI gets data: copy it in (fast, stale), query the source live each time (fresh, slower), or read Delta straight from OneLake (fast *and* fresh). See [Serving from the Lakehouse](17_Power_BI_for_Engineers/04_Serving_from_the_Lakehouse.md).

---

## Cost and performance

**FinOps** — the practice of managing cloud cost as an engineering concern: visibility, accountability, and optimization of spend. See [Cost Fundamentals (FinOps)](16_Cost_and_Performance/01_Cost_Fundamentals_FinOps.md).

**Small-file problem** — thousands of tiny files that cripple read performance (huge listing/opening overhead); fixed by compaction (`OPTIMIZE`) and sensible partitioning.

**Predicate pushdown / partition pruning** — skipping data that a query's filters can't possibly match — pushing the filter down to the file/partition level so less data is read. See [Performance Optimization](16_Cost_and_Performance/04_Performance_Optimization.md).

---

*This glossary grows as new topic files are added. If you hit an unfamiliar term in a topic note that isn't listed here, that's a gap worth filling.*
