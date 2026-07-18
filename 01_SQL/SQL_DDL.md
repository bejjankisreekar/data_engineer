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

This defines an empty table with four columns and their [data types](SQL_Data_Types.md) — no rows exist yet.

---

## Constraints — rules attached to columns

Constraints are rules enforced automatically every time data is added or changed:

| Constraint | Rule it enforces |
|---|---|
| `PRIMARY KEY` | Uniquely identifies each row; can't be empty or duplicated (see [SQL_Keys_and_Joins.md](SQL_Keys_and_Joins.md)) |
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

Azure SQL Database and Azure Synapse Analytics both run standard T-SQL DDL. In a data warehouse specifically, DDL is used less often day-to-day than DML/DQL — tables are usually designed once (following a schema like the star schema mentioned in [SQL_Warehouse.md](SQL_Warehouse.md)) and then loaded repeatedly via pipelines like [Azure Data Factory](../04_ETL_ELT/Azure_Data_Factory.md).

---

## Real World Example

When a company first sets up its HR system, a database administrator runs `CREATE TABLE` statements to build the Employee, Department, and Payroll tables, with constraints ensuring every employee has a name and a valid, non-negative salary. Years later, when the company starts tracking emergency contacts, an `ALTER TABLE` adds a new column — without disturbing a single existing employee record.
