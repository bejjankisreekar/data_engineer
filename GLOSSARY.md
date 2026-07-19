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

**Database** — a system for storing and retrieving data reliably. See [SQL Database](01_SQL/SQL_Database.md).

**Primary key** — the column that uniquely identifies each row, like an employee ID or a passport number. No two rows can share one. See [SQL Keys and Joins](01_SQL/SQL_Keys_and_Joins.md).

**Foreign key** — a column in one table that points to the primary key in another table, the way an invoice references a customer number instead of repeating the customer's full details.

**Join** — combining rows from two tables using a shared key, similar to matching a claim form to a customer record using their account number.

**Normalization** — organizing data so each fact is stored only once (e.g. a customer's address lives in one "Customers" table, not copied into every order). Reduces duplication and inconsistency.

**Transaction** — a single unit of work, such as "transfer money from Account A to Account B." Either the whole thing happens, or none of it does.

**ACID** — four guarantees a database makes about transactions, so they're trustworthy:
- **A**tomicity — a transaction fully happens or fully doesn't (no half-finished transfers).
- **C**onsistency — data always follows the rules (an account balance can't go negative if that's against policy).
- **I**solation — transactions happening at the same time don't interfere with each other.
- **D**urability — once saved, data survives even a power cut.

**OLTP (Online Transaction Processing)** — systems built for many small, fast read/write operations, like a bank teller processing a deposit. This is what a [SQL Database](01_SQL/SQL_Database.md) is optimized for.

**OLAP (Online Analytical Processing)** — systems built for large, complex questions across huge amounts of historical data, like "what were total sales by region last year?" This is what a [SQL Warehouse](01_SQL/SQL_Warehouse.md) is optimized for.

---

## SQL command categories

Every SQL statement belongs to one of five categories. Full explanations live in [What is SQL](01_SQL/What_is_SQL.md); short definitions here:

**DDL (Data Definition Language)** — commands that define or change a table's *structure*: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`. See [SQL_DDL.md](01_SQL/SQL_DDL.md).

**DML (Data Manipulation Language)** — commands that change the *data* inside a table: `INSERT`, `UPDATE`, `DELETE`. See [SQL_DML.md](01_SQL/SQL_DML.md).

**DQL (Data Query Language)** — commands that *read* data without changing it: `SELECT`. See [SQL_DQL.md](01_SQL/SQL_DQL.md).

**DCL (Data Control Language)** — commands that manage *permissions*: `GRANT`, `REVOKE`. See [SQL_DCL_TCL.md](01_SQL/SQL_DCL_TCL.md).

**TCL (Transaction Control Language)** — commands that manage how a group of changes is saved or undone: `COMMIT`, `ROLLBACK`, `SAVEPOINT`. See [SQL_DCL_TCL.md](01_SQL/SQL_DCL_TCL.md).

**View** — a saved query that behaves like a table, recalculated fresh every time it's used. See [SQL_Views.md](01_SQL/SQL_Views.md).

**Index** — a behind-the-scenes lookup structure that speeds up finding rows, like a textbook's index. See [SQL_Indexes.md](01_SQL/SQL_Indexes.md).

**Subquery** — a query nested inside another query, used when the outer query depends on a value the inner query calculates first. See [SQL_Subqueries.md](01_SQL/SQL_Subqueries.md).

---

## Storage and files

**File format** — the way data is physically written to a file (CSV, JSON, Parquet, Avro, ORC are all file formats).

**Row-based storage** — data is stored one full row at a time, like reading a filing cabinet folder by folder, one employee's entire file at once.

**Columnar storage** — data is stored one column at a time, like flipping through a single index card that only lists everyone's salary. Faster when you only need a few columns out of many.

**Compression** — shrinking file size by removing repetition, similar to summarizing a long report so it takes up less space, without losing the information.

**Data Lake** — a large storage area that holds raw data of any kind (structured, semi-structured, unstructured), before it's been cleaned or organized. Think of it as a big warehouse room where boxes arrive as-is, unsorted. See [Data Lake vs Warehouse vs Database](03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md).

**Blob** — Azure's term for "a file stored in the cloud" (Binary Large OBject). See [Azure Blob Storage](03_Data_Storage/Azure_Blob_Storage.md).

---

## Moving and processing data

**Pipeline** — an automated sequence of steps that moves data from one place to another, similar to an assembly line: extract from the source, transform it, load it into the destination.

**ETL (Extract, Transform, Load)** — extract data from a source, clean/reshape it *before* loading it into its destination. See [ETL vs ELT](04_ETL_ELT/ETL_vs_ELT.md).

**ELT (Extract, Load, Transform)** — extract data, load it into the destination first, and transform it there afterward. Common with modern cloud warehouses that have plenty of processing power.

**Batch processing** — processing data in scheduled chunks (e.g. once every night), like a bank running end-of-day settlement.

**Streaming (real-time) processing** — processing data the instant it arrives, like a fraud-detection system checking a card swipe as it happens.

**Ingestion** — the act of bringing data into a system from an external source (a database, an API, a file drop).

---

## Azure-specific terms

**Azure Data Factory (ADF)** — Azure's tool for building and scheduling data pipelines, largely through a drag-and-drop interface. See [Azure Data Factory](04_ETL_ELT/Azure_Data_Factory.md).

**Azure Data Lake Storage (ADLS)** — Azure Blob Storage with extra features (folder structure, fine-grained permissions) tuned for big-data analytics. See [Azure Data Lake Storage](03_Data_Storage/Azure_Data_Lake_Storage.md).

**Azure Synapse Analytics** — Microsoft's cloud data warehouse and analytics service (successor to Azure SQL Data Warehouse).

**Azure Databricks** — a managed Apache Spark environment on Azure, used for large-scale data processing and machine learning.

**Delta Lake** — a storage layer (used heavily in Databricks) that adds database-like reliability (ACID transactions) on top of a data lake.

---

## Distributed systems and Spark

**Cluster / Node** — a group of machines working together as one system; each machine is a node. See [Distributed Computing](00_Fundamentals/Distributed_Computing.md).

**Scale up vs scale out** — buying a bigger machine vs adding more machines. Big data tooling is built around scaling out.

**Partition** — one chunk of a dataset, small enough for one worker/core to process; the unit of parallelism in Spark and the unit of pruning in storage.

**Shuffle** — redistributing data across the cluster by key (for GROUP BY, JOIN) — the most expensive operation in distributed processing. See [Spark Processing](06_PySpark/Spark_Processing.md).

**Data skew** — when one key/partition holds far more data than the rest, so one worker becomes the bottleneck ("the job is 99% done for an hour").

**Driver / Executor** — Spark's master and workers: the driver plans and schedules; executors run tasks and hold cached data. See [Spark Architecture](06_PySpark/Spark_Architecture.md).

**Lazy evaluation** — Spark records transformations without running them, then optimizes and executes the whole plan when an action (count, write) triggers it.

**DAG (Directed Acyclic Graph)** — the dependency graph of operations an engine builds from your code before executing it.

**Broadcast join** — shipping a small table to every worker so a join needs no shuffle of the big table.

**Idempotent** — safe to run twice: re-running produces the same result instead of duplicating data. The core property of production pipelines.

**Exactly-once / at-least-once** — delivery guarantees: whether a record can be processed twice on retry. "At-least-once + idempotent writes" is how pipelines fake exactly-once.

**CDC (Change Data Capture)** — streaming inserts/updates/deletes out of a database by reading its transaction log, instead of repeatedly querying tables.

**Watermark** — the saved "high-water mark" (e.g. max `modified_at`) an incremental load uses to fetch only new/changed rows next run.

**Medallion (bronze/silver/gold)** — lakehouse layering: raw as-arrived → cleaned/typed → business-ready aggregates. See [ETL vs ELT](04_ETL_ELT/ETL_vs_ELT.md).

**Lakehouse** — data-lake storage + a table format (Delta/Iceberg) giving warehouse behavior (ACID, schema, time travel) on one copy of data.

**Star schema / Fact / Dimension** — warehouse modeling: a central numeric fact table joined to descriptive dimension tables. See [SQL Warehouse](01_SQL/SQL_Warehouse.md).

**SCD (Slowly Changing Dimension)** — how to store history when a dimension attribute changes; Type 2 (new row with validity dates) is the default.

**Surrogate key** — a meaningless generated ID used to join facts to dimensions, insulating the model from source-system key changes.

---

## Cloud terms

**Region / Availability Zone** — a metro-area group of datacenters / one independent facility within it. See [Public, Private & Hybrid Cloud](05_cloud/Public_Private_Hybrid_Cloud.md).

**IaaS / PaaS / SaaS** — how much of the stack you rent: raw VMs / a managed platform for your code and data / finished software. See [SaaS, PaaS, IaaS](05_cloud/SaaS_PaaS_IaaS.md).

**Serverless** — compute that scales to zero and bills per use; you never size or manage instances.

**Managed identity** — an Azure service's own Entra ID identity, letting it access storage/databases with no stored password.

**RBAC (Role-Based Access Control)** — granting permissions via roles scoped to resources ("this factory may read this container").

**Egress** — data leaving a cloud region/provider — the direction that costs money and shapes architectures.

**DBU (Databricks Unit)** — Databricks' normalized billing unit for compute consumption, charged on top of VM cost.

**RPO / RTO** — how much data you may lose / how long recovery takes, in a failover. The two numbers behind every disaster-recovery design.

---

*This glossary grows as new topic files are added. If you hit an unfamiliar term in a topic note that isn't listed here, that's a gap worth filling.*
