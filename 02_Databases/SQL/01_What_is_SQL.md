# What is SQL?

## What is SQL?

SQL stands for **S**tructured **Q**uery **L**anguage. It's the language you use to talk to a relational database — to create its structure, put data in, take data out, change it, and control who's allowed to touch it.

Analogy: if a [SQL Database](02_SQL_Database.md) is a filing cabinet, SQL is the set of instructions you'd hand to a clerk to work with it — "create a new drawer," "file this form," "find every form from March," "shred this folder." The clerk (the database engine) does the physical work; SQL is just the precise language you use to give the instructions.

SQL is not tied to one company or product. Microsoft SQL Server, Azure SQL Database, PostgreSQL, MySQL, and Oracle all understand SQL, with only small differences in syntax between them (Microsoft's dialect is called **T-SQL**, or Transact-SQL).

---

## Why "Structured"?

SQL only works on data that follows a defined **schema** — a fixed set of columns and types, agreed upon before any data is stored (see the [Glossary](../../GLOSSARY.md#data-basics)). That's the "structured" in Structured Query Language: you can't ask SQL a question about data whose shape you haven't first defined.

---

## The Five Categories of SQL Commands

Every SQL statement falls into one of five categories, based on *what kind of thing it does*. This repo has one file per category — this page is just the map.

| Category | Stands for | What it does | Example commands | Learn more |
|---|---|---|---|---|
| DDL | Data Definition Language | Defines or changes the *structure* of the database (tables, columns) | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | [04_SQL_DDL.md](04_SQL_DDL.md) |
| DML | Data Manipulation Language | Changes the *data* inside existing tables | `INSERT`, `UPDATE`, `DELETE` | [05_SQL_DML.md](05_SQL_DML.md) |
| DQL | Data Query Language | Retrieves (reads) data without changing it | `SELECT` | [06_SQL_DQL.md](06_SQL_DQL.md) |
| DCL | Data Control Language | Controls *who is allowed* to do what | `GRANT`, `REVOKE` | [12_SQL_DCL_TCL.md](12_SQL_DCL_TCL.md) |
| TCL | Transaction Control Language | Controls how a group of changes is saved or undone | `COMMIT`, `ROLLBACK`, `SAVEPOINT` | [12_SQL_DCL_TCL.md](12_SQL_DCL_TCL.md) |

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

---

## SQL is declarative — and that changes everything

In Python you write *how* (loop, compare, accumulate). In SQL you declare *what* ("sum of sales by region") and the engine's **query optimizer** invents the how: which index to use, which join algorithm, what order to filter. Consequences:

- The same query can run in 2 ms or 2 hours depending on indexes/statistics — performance work means influencing the optimizer, not rewriting loops ([11_SQL_Indexes.md](11_SQL_Indexes.md)).
- Two very differently *written* queries often compile to the identical plan — readable SQL is free.

## Logical processing order (the #1 "aha" for intermediate SQL)

SQL is *written* in one order but *evaluated* in another:

```
Written:   SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY
Evaluated: FROM → [JOINs] → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

This single fact explains the classic confusions:

- You **can't use a SELECT alias in WHERE** (`WHERE total > 100` fails if `total` is defined in SELECT — WHERE runs first).
- **WHERE vs HAVING**: WHERE filters rows *before* grouping; HAVING filters groups *after* ([08_SQL_Aggregate_Functions.md](08_SQL_Aggregate_Functions.md)).
- `ORDER BY` *can* use aliases — it runs last.

## Dialects: standard core, vendor edges

| Dialect | Product | Sample differences |
|---|---|---|
| T-SQL | SQL Server / Azure SQL / Synapse | `TOP 10`, `GETDATE()`, `ISNULL()` |
| PL/pgSQL flavor | PostgreSQL | `LIMIT 10`, `NOW()`, `COALESCE()`, rich JSON ops |
| Spark SQL | Databricks | `LIMIT`, backtick identifiers, Delta extensions (`MERGE`, time travel) |
| ANSI standard | the shared core | joins, aggregates, subqueries, window functions |

Pro habit: write ANSI-standard SQL by default; isolate dialect-specific syntax so migrations (and copy-pasting between systems) stay cheap.

---

## SQL injection — the one security lesson everyone must know

Building SQL by gluing user input into strings is the oldest critical vulnerability on the web:

```python
query = f"SELECT * FROM users WHERE name = '{user_input}'"
# user_input = "x'; DROP TABLE users; --"   → executes YOUR data away
```

The fix is **parameterized queries** — the input travels as a *value*, never as SQL text:

```python
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
```

This applies to pipelines too: notebook widgets and job parameters interpolated into `spark.sql(f"...")` are injection surfaces inside your own platform.

## NULL — SQL's three-valued logic

`NULL` is not a value; it's "unknown," and comparisons with it return neither true nor false but *unknown*:

- `NULL = NULL` → unknown (use `IS NULL`)
- `WHERE col <> 'x'` silently **drops NULL rows** — the most common subtle bug in filters
- `NOT IN (subquery)` returns **zero rows** if the subquery yields a single NULL — use `NOT EXISTS` ([09_SQL_Subqueries.md](09_SQL_Subqueries.md))
- Aggregates ignore NULLs (`COUNT(col)` vs `COUNT(*)` differ)

Seniors treat every nullable column as a design decision, not a default.

## SQL's longevity — why this skill compounds

SQL (1974, standardized 1986) has outlived every "SQL killer": object databases (90s), XML (00s), NoSQL (10s — most added SQL layers back), and now sits on top of every big data engine (Spark SQL, Trino, KQL-adjacent tools). The reason: it's a *math-backed interface* (relational algebra), not an implementation — engines change underneath, the language stays. Career translation: SQL fluency transfers across every employer and platform you will ever touch; deep product-specific skills often don't.

## Interview-grade Q&A

- *Why can't WHERE see SELECT aliases?* Logical processing order — WHERE evaluates before SELECT.
- *Declarative vs imperative?* SQL declares the result; the optimizer chooses the algorithm. You tune by shaping the plan, not writing loops.
- *Difference between `COUNT(*)`, `COUNT(col)`, `COUNT(DISTINCT col)`?* All rows; non-NULL values of col; unique non-NULL values.
- *How do you prevent SQL injection?* Parameterized queries / prepared statements everywhere — including f-strings in Spark notebooks.

---

## Further Learning — Docs & Videos

**Documentation**
- What is SQL? (W3Schools): https://www.w3schools.com/sql/sql_intro.asp
- SQL overview (Mode SQL Tutorial): https://mode.com/sql-tutorial/introduction-to-sql/
- ANSI SQL standard (PostgreSQL docs): https://www.postgresql.org/docs/current/sql.html

**Videos**
- SQL explained for beginners: https://www.youtube.com/results?search_query=what+is+sql+explained+for+beginners
- SQL full course: https://www.youtube.com/results?search_query=sql+full+course+freecodecamp
