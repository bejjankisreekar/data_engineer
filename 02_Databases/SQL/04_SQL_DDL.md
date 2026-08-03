# SQL DDL (Data Definition Language)

## What is DDL?

DDL commands define or change the **structure** of a database — creating tables, adding or removing columns, or deleting a table entirely. DDL never touches the data sitting inside a table; it only shapes the container the data lives in.

Analogy: DDL is carpentry, not filing. It's building the filing cabinet, adding a drawer, relabeling a drawer, or removing a drawer — never touching the papers inside.

---

## CREATE

Builds a new table (or database, or other object).

```sql
CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Department VARCHAR(30),
    Salary DECIMAL(10,2)
);
```

This defines an empty table with four columns and their [data types](03_SQL_Data_Types.md) — no rows exist yet.

---

## Constraints — rules attached to columns

Constraints are rules enforced automatically every time data is added or changed:

| Constraint | Rule it enforces |
|---|---|
| `PRIMARY KEY` | Uniquely identifies each row; can't be empty or duplicated (see [07_SQL_Keys_and_Joins.md](07_SQL_Keys_and_Joins.md)) |
| `NOT NULL` | This column can never be left blank |
| `UNIQUE` | No two rows may share the same value in this column |
| `DEFAULT` | If no value is given, use this value automatically |
| `CHECK` | The value must satisfy a condition (e.g. `Salary > 0`) |

```sql
CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Status VARCHAR(20) DEFAULT 'Active',
    Salary DECIMAL(10,2) CHECK (Salary > 0)
);
```

Constraints are what stop bad data from ever being entered in the first place, rather than relying on someone to notice and fix it afterward.

---

## ALTER

Changes the structure of a table that already exists — without deleting any of its data.

```sql
-- Add a new column
ALTER TABLE Employee
ADD PhoneNumber VARCHAR(15);

-- Remove a column
ALTER TABLE Employee
DROP COLUMN PhoneNumber;

-- Change a column's data type
ALTER TABLE Employee
ALTER COLUMN Salary DECIMAL(12,2);
```

Analogy: adding a new labeled section to an existing form, without reprinting or losing any forms already filled out.

---

## DROP

Permanently deletes an entire table — structure and all data inside it.

```sql
DROP TABLE Employee;
```

This is irreversible unless you have a backup. It removes the drawer entirely, papers and all.

---

## TRUNCATE

Empties all rows out of a table instantly, but keeps the table's structure intact for future use.

```sql
TRUNCATE TABLE Employee;
```

Analogy: emptying every paper out of a drawer, but keeping the (now-empty) drawer and its label in place, ready to be refilled.

**TRUNCATE vs DELETE vs DROP**

| Command | Removes rows? | Removes table structure? | Category |
|---|---|---|---|
| `DELETE` (with no `WHERE`) | Yes, one row at a time (slower, can be undone before commit) | No | DML |
| `TRUNCATE` | Yes, all at once (faster) | No | DDL |
| `DROP` | Yes | Yes, the table itself is gone | DDL |

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both run standard T-SQL DDL. In a data warehouse specifically, DDL is used less often day-to-day than DML/DQL — tables are usually designed once (following a schema like the star schema mentioned in [13_SQL_Warehouse.md](13_SQL_Warehouse.md)) and then loaded repeatedly via pipelines like [Azure Data Factory](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md).

---

## Real World Example

When a company first sets up its HR system, a database administrator runs `CREATE TABLE` statements to build the Employee, Department, and Payroll tables, with constraints ensuring every employee has a name and a valid, non-negative salary. Years later, when the company starts tracking emergency contacts, an `ALTER TABLE` adds a new column — without disturbing a single existing employee record.

---
---

# Part 2 — Advanced

## ALTER is not free — what happens under the hood

Not all ALTERs are equal; the difference decides whether production notices:

| Change | Cost |
|---|---|
| `ADD` nullable column (no default) | **Metadata-only** — instant, any table size |
| `ADD` column with default | Modern engines: metadata-only; older ones rewrite every row |
| `ALTER COLUMN` type widening (INT→BIGINT, VARCHAR(50)→(100)) | Usually metadata-only |
| Type *narrowing* or incompatible change | **Full table rewrite + validation** — locks, log growth, hours on big tables |
| `ADD CONSTRAINT ... CHECK/FOREIGN KEY` | Scans the whole table to validate (unless `WITH NOCHECK` — see gotchas) |

Pro reflex before any ALTER on a large table: *is this metadata-only or a rewrite?* — the answer decides whether it ships at noon or 2am.

## More DDL vocabulary you'll meet

- **Computed/generated columns** — `FullName AS (FirstName + ' ' + LastName)`; `PERSISTED` stores and can index it.
- **Temporal tables** (SQL Server) — `SYSTEM_VERSIONING = ON` gives an automatic history table; query `FOR SYSTEM_TIME AS OF '2026-01-01'` — the OLTP cousin of Delta time travel.
- **Partitioned tables** — one logical table, many physical chunks by range (e.g. by month): enables instant partition `SWITCH` loads and per-partition maintenance ([warehouse partitioning](../../01_Foundations/Fundamentals/02_OLAP_Storage.md)).
- **Identity/sequences** — `IDENTITY(1,1)` / `CREATE SEQUENCE`: auto-numbering with the gaps-are-normal caveat.
- **Schemas as namespaces** — `sales.Orders` vs `hr.Employee`: permission boundaries and name organization ([DCL](12_SQL_DCL_TCL.md)).

## DDL in the lakehouse dialect

The same category exists in Spark SQL/Databricks, with new powers:

```sql
CREATE TABLE sales.orders (
  order_id BIGINT,
  amount   DECIMAL(19,4),
  order_ts TIMESTAMP
) USING DELTA
PARTITIONED BY (order_date DATE);

ALTER TABLE sales.orders ADD COLUMN channel STRING;   -- metadata-only in Delta
ALTER TABLE sales.orders SET TBLPROPERTIES ('delta.enableChangeDataFeed'='true');
```

Differences that matter: constraints are limited (Delta supports `NOT NULL` and `CHECK`; **no enforced foreign keys** — integrity is your pipeline's job), and `CREATE OR REPLACE TABLE` is the idiomatic atomic rebuild.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Schema changes as code: migrations

Nobody senior runs ad-hoc ALTERs against production. Structure changes ship as **migrations** — versioned, ordered, reviewed scripts (Flyway, Liquibase, dbt for the warehouse, alembic) applied identically to dev → test → prod:

```
V042__add_channel_to_orders.sql   ← in git, code-reviewed, CI-applied
```

Rules of the discipline: every migration is **forward-only and re-runnable** (guard with `IF NOT EXISTS`), destructive steps are split from additive ones, and the schema in git *is* the source of truth — a production table that differs from git is an incident, not a quirk.

## The expand–contract pattern (zero-downtime change)

You can't rename a column the app is reading. Pros change schemas in three deploys:

1. **Expand** — add the new column/table alongside the old; write to both (or backfill).
2. **Migrate** — move readers to the new column; verify.
3. **Contract** — drop the old column *after* nothing references it (verified by monitoring, not hope).

The same pattern governs breaking changes to lakehouse tables consumed by other teams — which is why **schema evolution policy** (what's additive vs breaking) belongs in every data contract.

## TRUNCATE vs DELETE — the fine print that bites

- `TRUNCATE` requires heavier locks, **resets IDENTITY counters**, fails if foreign keys reference the table, and can't have a `WHERE`.
- Despite folklore, in SQL Server/PostgreSQL `TRUNCATE` *is* transactional (rollback-able); in Oracle/MySQL it effectively is not (implicit commit) — know your engine before using it in a transaction.
- In pipelines, prefer *atomic replace* over truncate-then-load: `CREATE OR REPLACE TABLE` / partition `SWITCH` / Delta `overwrite` — a failed load after TRUNCATE leaves an **empty production table**, the classic 6am incident.

## Field-tested gotchas

- `WITH NOCHECK` foreign keys/checks don't validate existing rows *and* are ignored by the optimizer — untrusted constraints are documentation, not protection.
- Dropping a column doesn't always reclaim space (metadata-hidden until rebuild) — and in Delta, `DROP COLUMN` behavior depends on column-mapping mode.
- Every DDL statement takes a **schema lock**: an innocent ALTER can queue behind a long transaction and then *block every query* behind itself — always deploy DDL with a lock timeout and off-peak.
- `DROP TABLE` in the lake deletes metadata; whether *files* die depends on managed vs external tables ([ADLS](../../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)) — know which you have before "cleaning up."

## Interview-grade Q&A

- *How do you add a NOT NULL column to a billion-row table without downtime?* Add nullable + default via metadata-only path, backfill in batches, then enforce NOT NULL.
- *DELETE vs TRUNCATE vs DROP?* Row-by-row logged DML with WHERE / instant deallocation keeping structure (resets identity, FK-blocked) / removes the object itself.
- *How do schema changes reach production in your team?* Versioned migrations in git through CI, expand–contract for breaking changes — never manual ALTERs.
- *Do Delta tables have foreign keys?* Declarable-but-unenforced (informational) at best; referential integrity is enforced by pipeline tests/MERGE logic instead.

---

## Further Learning — Docs & Videos

**Documentation**
- SQL CREATE/ALTER/DROP (W3Schools): https://www.w3schools.com/sql/sql_create_table.asp
- DDL statements (PostgreSQL): https://www.postgresql.org/docs/current/ddl.html

**Videos**
- SQL DDL commands explained: https://www.youtube.com/results?search_query=sql+ddl+create+alter+drop+truncate
