# SQL Database

## What is a SQL Database?

A SQL Database is a structured database used to store and manage relational data.

Analogy: think of it as a set of well-organized spreadsheets that are strictly rule-enforced — every "sheet" (table) has fixed column headings, and the system won't let anyone type a letter into a column that's supposed to hold a salary number, or leave a required box blank.

It stores data in:

- Tables
- Rows
- Columns

New to SQL entirely? Start with [What is SQL](What_is_SQL.md) first — it introduces the language itself before this file goes deeper into what a relational database is used for. See the [Glossary](../GLOSSARY.md) for quick definitions of any of these words, and [SQL Keys and Joins](SQL_Keys_and_Joins.md) for how multiple tables connect to each other.

Example:

Employee Table

| EmployeeID | Name | Department | Salary |
|------------|------|------------|--------|
|101|John|IT|60000|
|102|Alice|HR|50000|

Each row represents one record.

---

## Why use SQL Database?

SQL databases are designed for:

- Fast inserts
- Fast updates
- Fast deletes
- Transaction processing

Examples:

- Banking systems
- Hospital Management
- Ecommerce
- HRMS
- CRM

---

## SQL Operations

### Create

```sql
INSERT INTO Employee
VALUES (103,'David','Finance',55000);
```

### Read

```sql
SELECT *
FROM Employee;
```

### Update

```sql
UPDATE Employee
SET Salary = 70000
WHERE EmployeeID = 101;
```

### Delete

```sql
DELETE
FROM Employee
WHERE EmployeeID = 102;
```

These are called CRUD operations.

---

## Common SQL Databases

- SQL Server
- PostgreSQL
- MySQL
- Oracle
- Azure SQL Database

---

## Advantages

- Structured
- Reliable
- ACID compliant — a set of guarantees (explained in the [Glossary](../GLOSSARY.md#databases-and-transactions)) that a transaction either fully completes or doesn't happen at all, so half-finished updates (like money leaving one account but never arriving in another) can't occur
- Supports relationships (see [Keys and Joins](SQL_Keys_and_Joins.md))
- Supports joins
- Fast querying

---

## Limitations

A SQL Database is built for OLTP — Online Transaction Processing, meaning many small, fast reads and writes (see [Glossary](../GLOSSARY.md#databases-and-transactions)). It is not ideal for:

- Huge analytical datasets
- Big Data
- Petabytes of data
- Data Lake storage

For those cases, see [SQL Warehouse](SQL_Warehouse.md) and [Data Lake vs Warehouse vs Database](../03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md).

---

## Azure Equivalent

Azure SQL Database

Managed cloud SQL database provided by Microsoft.

Used for applications requiring transactional processing.

---

## Example

A shopping website stores:

Customers

Orders

Products

Payments

Each purchase immediately updates inventory.

This is a perfect use case for SQL Database.

---
---

# Part 2 — Advanced

## What actually happens when you run a query

```
Your SQL → Parser → Optimizer (builds an execution plan using
           statistics + indexes) → Execution engine → Storage engine
           (reads 8KB pages via the buffer pool cache) → Results
```

Two internals worth knowing by name:

- **Buffer pool** — the database caches data pages in RAM; a "fast" query is usually one whose pages were already cached. This is why the first run is slow and the second instant — and why analytics scans are so harmful: they evict the app's hot pages (**cache pollution**).
- **Transaction log (WAL)** — every change is written to a sequential log before data files, giving crash recovery and feeding **CDC** tools that stream changes into the lake ([OLTP_Storage.md](../00_Fundamentals/OLTP_Storage.md) covers this in depth).

## Concurrency: how 1,000 users don't corrupt one table

- **Locks** — writers lock rows; conflicting writers wait. Two transactions locking in opposite order → **deadlock**, and the engine kills one.
- **MVCC / snapshot isolation** — readers see a consistent snapshot instead of blocking on writers (PostgreSQL default; SQL Server via RCSI). This is why your long `SELECT` doesn't freeze the checkout flow — and why *very* long transactions bloat the version store.
- **Isolation levels** (Read Committed → Serializable) trade correctness anomalies against throughput — detailed table in [OLTP_Storage.md](../00_Fundamentals/OLTP_Storage.md), commands in [SQL_DCL_TCL.md](SQL_DCL_TCL.md).

## Azure SQL Database — the parts that matter in practice

| Feature | Why you care |
|---|---|
| **DTU vs vCore purchase models** | vCore = transparent CPU/RAM sizing + reserved pricing; DTU = blended bundle for small apps |
| **Serverless tier** | Auto-pauses when idle — ideal for dev/test databases |
| **Read replicas / Hyperscale** | Offload reporting and ETL extracts off the primary — *always* point pipelines here |
| **Automatic backups + PITR** | Point-in-time restore to any second in retention — your real "undo" for bad deploys |
| **Elastic pools** | Many small databases sharing one resource pool (SaaS multi-tenant pattern) |

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The data engineer's contract with OLTP databases

You will mostly *extract from* these systems, and the pro rules are:

1. **Never query the primary for bulk extracts** — use a replica, and schedule off-peak.
2. **Incremental over full**: watermark on `modified_at`, or log-based CDC. Full `SELECT *` extracts stop scaling long before the database does.
3. **Watch for hard deletes and schema drift** — watermarks miss deletes ([soft-delete/CDC discussion](../00_Fundamentals/OLTP_Storage.md)); a dropped column breaks tomorrow's load. Schema-drift alerts belong in the pipeline.
4. **Respect connection limits** — a Spark job opening 200 JDBC partitions can exhaust the app's connection pool. Bound `numPartitions`, use predicate-based partitioned reads on an indexed column.

## NoSQL — where the relational model isn't the answer

| Model | Example | Sweet spot |
|---|---|---|
| Document | Cosmos DB, MongoDB | Flexible/nested app objects, global low-latency |
| Key-value | Redis | Caching, sessions |
| Wide-column | Cassandra | Massive write throughput, [masterless](../00_Fundamentals/Master_Slave_Architecture.md) |
| Graph | Neo4j | Relationship-heavy traversals |

The honest summary a senior gives: NoSQL trades ACID/joins for horizontal scale and schema flexibility (**BASE**/eventual consistency). Most business systems still fit relational; NoSQL earns its complexity at genuine scale or genuinely non-tabular shapes. And note the irony — most NoSQL stores eventually grew SQL-ish query layers, because the interface won even where the engine changed.

## Field-tested gotchas

- **ORMs hide N+1 queries** — one page load silently firing 300 SELECTs is the classic app-slowness root cause; it also hammers the DB your pipeline shares.
- **Index sprawl**: every extra index taxes every INSERT/UPDATE. OLTP tables want *few, surgical* indexes ([SQL_Indexes.md](SQL_Indexes.md)).
- **Auto-growth events** on data/log files cause mysterious latency spikes — pre-size files in on-prem SQL Server; managed services handle this for you (part of what you pay for — [SaaS_PaaS_IaaS.md](../05_cloud/SaaS_PaaS_IaaS.md)).
- A database that fits in RAM behaves like a different product than one that doesn't; capacity-plan around the *working set*, not disk size.

## Interview-grade Q&A

- *Why is the second run of a query faster?* Buffer pool cache hit — pages already in RAM.
- *How would you extract a 500 GB table nightly without hurting the app?* Read replica + incremental watermark/CDC + partitioned parallel reads + off-peak window.
- *SQL vs NoSQL in one line?* ACID + joins + fixed schema vs horizontal scale + flexible schema + eventual consistency — pick per workload, not per fashion.
- *What is PITR and why does it matter?* Point-in-time restore from continuous backups — the recovery story for "we corrupted the table at 14:32."