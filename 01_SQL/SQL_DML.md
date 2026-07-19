# SQL DML (Data Manipulation Language)

## What is DML?

DML commands change the **data** stored inside a table's existing structure. Where [DDL](SQL_DDL.md) is carpentry (building the drawer), DML is filing — adding, editing, or removing the papers inside a drawer that already exists.

The three DML commands are `INSERT`, `UPDATE`, and `DELETE`.

---

## INSERT — adding new rows

```sql
INSERT INTO Employee (EmployeeID, Name, Department, Salary)
VALUES (104, 'Priya', 'Finance', 58000);
```

Naming the columns explicitly (as above) is safer than relying on column order, and keeps working correctly even if the table's structure changes later.

Multiple rows can be added in a single statement:

```sql
INSERT INTO Employee (EmployeeID, Name, Department, Salary)
VALUES
    (105, 'Arjun', 'IT', 62000),
    (106, 'Sana', 'HR', 51000);
```

---

## UPDATE — changing existing rows

```sql
UPDATE Employee
SET Salary = 70000
WHERE EmployeeID = 101;
```

**The `WHERE` clause is what makes this safe.** It tells the database exactly which row(s) to change.

```sql
-- Danger: no WHERE clause
UPDATE Employee
SET Salary = 70000;
```

Without a `WHERE` clause, this updates *every single row in the table* — every employee's salary becomes 70000. This is one of the most common, most damaging mistakes in SQL. Always double-check the `WHERE` clause before running an `UPDATE`.

---

## DELETE — removing rows

```sql
DELETE FROM Employee
WHERE EmployeeID = 102;
```

Just like `UPDATE`, a `DELETE` without a `WHERE` clause removes every row in the table (though, unlike [`TRUNCATE`](SQL_DDL.md), it does so one row at a time and can typically still be undone if caught before the transaction is saved — see [SQL_DCL_TCL.md](SQL_DCL_TCL.md)).

```sql
-- Danger: no WHERE clause, deletes every row
DELETE FROM Employee;
```

---

## A Safety Habit Worth Building

Before running `UPDATE` or `DELETE`, run the equivalent `SELECT` first with the same `WHERE` clause, to see exactly which rows will be affected:

```sql
-- Step 1: check first
SELECT * FROM Employee WHERE Department = 'HR';

-- Step 2: only then, run the real change
DELETE FROM Employee WHERE Department = 'HR';
```

This costs a few extra seconds and prevents most accidental data loss.

---

## Azure Usage

Azure SQL Database, Synapse Analytics, and Databricks (via Spark SQL) all support standard `INSERT`/`UPDATE`/`DELETE`. In [ETL/ELT pipelines](../04_ETL_ELT/ETL_vs_ELT.md), DML is frequently generated automatically by tools like [Azure Data Factory](../04_ETL_ELT/Azure_Data_Factory.md) rather than typed by hand — a pipeline might insert thousands of new rows nightly as part of a scheduled load.

---

## Real World Example

An e-commerce site runs an `INSERT` every time a customer places an order, an `UPDATE` every time an order's status changes from "Processing" to "Shipped," and a `DELETE` when a customer cancels an order before it ships — three DML commands covering the entire lifecycle of a single order.

---
---

# Part 2 — Advanced

## MERGE — the upsert, the data engineer's daily verb

Loading a day's changes means "update rows that exist, insert those that don't." One statement does both:

```sql
MERGE INTO Employee AS target
USING Staging_Employee AS source
  ON target.EmployeeID = source.EmployeeID
WHEN MATCHED AND source.is_deleted = 1 THEN DELETE
WHEN MATCHED THEN
  UPDATE SET Salary = source.Salary, Department = source.Department
WHEN NOT MATCHED THEN
  INSERT (EmployeeID, Name, Department, Salary)
  VALUES (source.EmployeeID, source.Name, source.Department, source.Salary);
```

This exact shape — `MERGE INTO delta_table USING updates ON keys` — is also how Delta Lake upserts work in Databricks, making it arguably the most-typed statement in modern pipelines. Two cautions: the source must have **unique keys** (duplicate source keys = "attempt to update the same row twice" errors), and MERGE is a join under the hood — all join performance rules apply.

## Writing changes based on other tables

```sql
-- UPDATE from a join (T-SQL flavor)
UPDATE e
SET e.Salary = e.Salary * 1.10
FROM Employee e
JOIN Promotions p ON p.EmployeeID = e.EmployeeID
WHERE p.Year = 2026;

-- INSERT from a query (how warehouses are actually loaded)
INSERT INTO Sales_Fact (order_id, region_key, amount)
SELECT o.order_id, r.region_key, o.amount
FROM Staging_Orders o
JOIN Dim_Region r ON r.region_code = o.region_code;

-- Capture what changed (T-SQL OUTPUT / Postgres RETURNING)
DELETE FROM Employee
OUTPUT DELETED.EmployeeID, DELETED.Name INTO Employee_Archive
WHERE TerminationDate < '2020-01-01';
```

## Bulk loading — why pipelines don't INSERT row by row

A million single INSERTs = a million round-trips + a million log records. Bulk paths batch, minimally log, and bypass per-row overhead:

| Engine | Bulk path |
|---|---|
| SQL Server / Azure SQL | `BULK INSERT`, `bcp`, ADF Copy with bulk options |
| PostgreSQL | `COPY` |
| Synapse | `COPY INTO`, PolyBase |
| Databricks/Delta | `COPY INTO`, Auto Loader, `df.write` |

Rule of thumb: row-by-row is for applications; **set-based and bulk** is for pipelines — a 100× speed difference is normal.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Idempotent DML — the property that saves your weekend

Orchestrators retry failed jobs. If the job half-ran before failing, a blind re-run must not double the data. Idempotent patterns, in order of preference:

1. **MERGE on business keys** — re-running converges to the same state.
2. **Delete-then-insert scoped to the batch** — `DELETE WHERE load_date = '2026-07-19'` then insert that day (atomic inside a [transaction](SQL_DCL_TCL.md)).
3. **Staging + atomic swap** — load into a staging table, validate, then swap/rename.
4. Blind `INSERT ... VALUES` append — **not idempotent**; acceptable only with dedup downstream.

Interviewers phrase this as: *"your nightly job failed at 60% and re-ran — what does the table look like?"* The right answer describes one of the patterns above.

## Big DML on big tables — batching

A single `DELETE` of 50 million rows = one giant transaction: log file explosion, lock escalation to a full table lock, replication lag. Pros chunk it:

```sql
WHILE 1 = 1
BEGIN
    DELETE TOP (100000) FROM Events WHERE event_date < '2024-01-01';
    IF @@ROWCOUNT = 0 BREAK;
END
```

(Plus a pause between batches on busy systems.) Better still: design so mass deletes become **partition drops/switches** ([DDL](SQL_DDL.md)) or Delta `replaceWhere` — metadata operations instead of row carnage.

## Soft deletes and the audit trail

Many systems never physically DELETE: an `is_deleted BIT + deleted_at` flag preserves history, keeps foreign keys intact, and — critically for data engineering — makes deletes **visible to incremental extracts** (a hard-deleted row simply vanishes from a watermark query; see [OLTP extraction](../00_Fundamentals/OLTP_Storage.md)). Costs: every query needs `WHERE is_deleted = 0` (hide it in a [view](SQL_Views.md)), unique constraints need filtering, and GDPR "right to erasure" still requires a real purge path.

## Field-tested gotchas

- `UPDATE` with a join that matches multiple source rows picks one **nondeterministically** (T-SQL) or errors (Postgres) — dedupe the source first.
- Triggers fire on your DML — an innocent bulk UPDATE can cascade into row-by-row trigger logic 100× slower than the statement itself.
- `@@ROWCOUNT`/`ROW_COUNT()` is the cheapest data-quality check there is: log "rows affected" on every pipeline DML and alert when today ≠ yesterday's order of magnitude.
- On Delta, many small MERGEs = many small files + version bloat: batch micro-changes, then `OPTIMIZE` ([Spark_Processing.md](../06_PySpark/Spark_Processing.md)).

## Interview-grade Q&A

- *What is an upsert and how do you write one?* Insert-or-update by key: `MERGE` (or `INSERT ... ON CONFLICT` in Postgres).
- *How do you delete 100M old rows from a live table?* Batched deletes with log/lock breathing room — or partition-based removal if the design allows.
- *How do you make a load safe to re-run?* Idempotency: MERGE by key or scoped delete-and-reload inside a transaction.
- *Why is row-by-row slow?* Per-statement round-trip, logging, and lock overhead; set-based DML amortizes all three.
