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