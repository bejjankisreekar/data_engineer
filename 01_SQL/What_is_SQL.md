# What is SQL?

## What is SQL?

SQL stands for **S**tructured **Q**uery **L**anguage. It's the language you use to talk to a relational database — to create its structure, put data in, take data out, change it, and control who's allowed to touch it.

Analogy: if a [SQL Database](SQL_Database.md) is a filing cabinet, SQL is the set of instructions you'd hand to a clerk to work with it — "create a new drawer," "file this form," "find every form from March," "shred this folder." The clerk (the database engine) does the physical work; SQL is just the precise language you use to give the instructions.

SQL is not tied to one company or product. Microsoft SQL Server, Azure SQL Database, PostgreSQL, MySQL, and Oracle all understand SQL, with only small differences in syntax between them (Microsoft's dialect is called **T-SQL**, or Transact-SQL).

---

## Why "Structured"?

SQL only works on data that follows a defined **schema** — a fixed set of columns and types, agreed upon before any data is stored (see the [Glossary](../GLOSSARY.md#data-basics)). That's the "structured" in Structured Query Language: you can't ask SQL a question about data whose shape you haven't first defined.

---

## The Five Categories of SQL Commands

Every SQL statement falls into one of five categories, based on *what kind of thing it does*. This repo has one file per category — this page is just the map.

| Category | Stands for | What it does | Example commands | Learn more |
|---|---|---|---|---|
| DDL | Data Definition Language | Defines or changes the *structure* of the database (tables, columns) | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | [SQL_DDL.md](SQL_DDL.md) |
| DML | Data Manipulation Language | Changes the *data* inside existing tables | `INSERT`, `UPDATE`, `DELETE` | [SQL_DML.md](SQL_DML.md) |
| DQL | Data Query Language | Retrieves (reads) data without changing it | `SELECT` | [SQL_DQL.md](SQL_DQL.md) |
| DCL | Data Control Language | Controls *who is allowed* to do what | `GRANT`, `REVOKE` | [SQL_DCL_TCL.md](SQL_DCL_TCL.md) |
| TCL | Transaction Control Language | Controls how a group of changes is saved or undone | `COMMIT`, `ROLLBACK`, `SAVEPOINT` | [SQL_DCL_TCL.md](SQL_DCL_TCL.md) |

Analogy for all five together, using the filing cabinet: DDL is buying and labeling a new drawer. DML is adding, editing, or removing individual forms in that drawer. DQL is asking "show me all forms from March." DCL is deciding who's allowed to open which drawer. TCL is the rule that either an entire stack of forms gets filed together, or none of them do — no half-finished filing.

---

## A Very First Query

```sql
SELECT Name, Department
FROM Employee
WHERE Department = 'IT';
```

Read this the way you'd read a sentence, left to right: "Show me the Name and Department, from the Employee table, but only where the Department is IT." SQL reads close enough to plain English on purpose — it was designed in the 1970s specifically so that non-programmers (business analysts, in particular) could ask questions of a database without needing to learn a full programming language.

---

## Basic Syntax Rules

- Statements typically end with a semicolon `;`
- SQL keywords (`SELECT`, `FROM`, `WHERE`) are traditionally written in UPPERCASE by convention, though SQL itself doesn't require this — it's purely to make queries easier for humans to read
- Text values are wrapped in single quotes: `'IT'`
- Number values are not quoted: `60000`

---

## Azure Usage

Azure SQL Database, Azure Synapse Analytics, and Azure Databricks (via Spark SQL) all accept SQL as their query language. Learning standard SQL transfers almost directly across all of them, and across most non-Azure database products too — this is one of the most portable, long-lasting skills in data engineering.

---

## Real World Example

A bank's customer service system runs entirely on SQL behind the scenes: DDL created the Customer and Account tables when the system was built years ago. DML runs every time a customer's balance changes. DQL runs every time a teller looks up an account. DCL ensures a teller can view balances but not, say, delete audit logs. TCL ensures that a transfer between two accounts either fully completes or doesn't happen at all — never leaving money "in transit" and lost.
