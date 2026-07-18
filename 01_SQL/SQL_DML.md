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
