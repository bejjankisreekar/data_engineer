# 01_SQL — Interview Questions & Answers

## How to use this file

SQL is the single most heavily interview-tested topic in data engineering — expect more questions from this file's territory than any other in this course. Questions mix two flavors, often within the same section:

- **THEORY** — concepts, trade-offs, "compare X vs Y" questions.
- **PRACTICAL / CODING** — "write this query," "find the bug," "predict the output" questions. These are the bulk of real SQL interviews, and every practical answer here includes real, correct SQL.

Every question explains *what it's testing*, and every answer explains *why it's correct* — the reasoning is what a live interview is actually probing for, not just the final SQL.

Two difficulty tags are used:

- **[Frequently Asked]** — the true SQL interview classics, asked at nearly every level: WHERE vs HAVING, types of joins, Nth highest salary, DELETE vs TRUNCATE vs DROP, primary vs foreign key, window functions, ACID.
- **[Senior/Experienced]** — deeper Pro-level material: execution plans, isolation levels/MVCC, index internals, sargability, star vs snowflake, SCD Type 2, deadlocks.

Untagged questions are solid mid-level material.

---

## Table of Contents

1. [SQL Basics — What is SQL, SQL Database, Data Types](#1-sql-basics)
2. [Modifying Data — DDL & DML](#2-modifying-data)
3. [Querying Data — DQL, Joins, Aggregates](#3-querying-data)
4. [Advanced Querying — Subqueries, Views, Indexes](#4-advanced-querying)
5. [Control — DCL & TCL](#5-control)
6. [Warehousing](#6-warehousing)
7. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. SQL Basics

*(full notes: [01_What_is_SQL.md](01_What_is_SQL.md), [02_SQL_Database.md](02_SQL_Database.md), [03_SQL_Data_Types.md](03_SQL_Data_Types.md))*

#### Q1. What is SQL, and why is it called a "declarative" language? **[Frequently Asked]**
*Why interviewers ask this:* A universal opener that also checks whether the candidate understands *how* SQL actually runs, not just that it's a query language.
**Answer:** SQL (Structured Query Language) is the language used to define, read, change, and control access to relational data. It's declarative because you state *what* result you want ("sum of sales by region") rather than *how* to compute it — the engine's query optimizer decides the actual algorithm (which index to use, which join strategy, what order to filter). This is correct because it explains the practical consequence too: the same logical query can run in milliseconds or minutes depending on indexes and statistics, and tuning SQL means shaping the optimizer's plan, not rewriting loops the way you would in an imperative language.

#### Q2. What is the logical order in which a SQL query is actually evaluated, and why does it matter? **[Frequently Asked]**
*Why interviewers ask this:* One of the highest-value "aha" facts in SQL — explains a whole category of beginner confusion in one answer.
**Answer:** SQL is *written* as `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY` but *evaluated* as `FROM → JOINs → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`. This explains why a `WHERE` clause can't reference a column alias defined in `SELECT` (WHERE runs before SELECT), why `WHERE` filters rows before grouping while `HAVING` filters groups after, and why `ORDER BY` — which runs last — *can* use SELECT aliases. This is correct because it's the mechanical explanation behind several "gotchas" candidates hit constantly, and citing it demonstrates real understanding rather than memorized syntax rules.

#### Q3. What's the difference between a SQL Database and a SQL Data Warehouse? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common comparison questions in all of data engineering — tests OLTP/OLAP understanding applied to concrete products.
**Answer:** A SQL Database (e.g. Azure SQL Database) is built for OLTP — many small, fast transactional reads/writes, current live data, normalized schema. A SQL Warehouse (e.g. Synapse, Snowflake) is built for OLAP — large historical datasets, read-heavy analytical queries, denormalized star-schema design, loaded via ETL/ELT pipelines rather than updated transaction-by-transaction. This is correct because it names both the workload and the design consequence (normalized vs. denormalized) rather than only "one is for apps, one is for reports."

#### Q4. Why should money never be stored in a `FLOAT` column? **[Frequently Asked]**
*Why interviewers ask this:* A very commonly asked data-types question, because it has a concrete, demonstrable failure and a definite right answer.
**Answer:** `FLOAT` is binary floating point, which cannot represent many base-10 decimal fractions exactly — `CAST(0.1 AS FLOAT) + CAST(0.2 AS FLOAT)` returns `0.30000000000000004`, not `0.3`. Summing millions of transactions in FLOAT accumulates visible rounding error that auditors will catch. `DECIMAL(p,s)` stores an exact base-10 value instead and is the correct type for currency; `FLOAT`'s legitimate home is scientific/sensor data where tiny relative error is acceptable and range matters more than exactness. This is correct because it demonstrates the failure concretely (with the actual wrong output) rather than asserting "FLOAT is imprecise" as an unexplained rule.

#### Q5. What happens when you compare a `VARCHAR` column to a numeric literal, and why can it silently slow down a query? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real production-debugging experience — implicit conversion is one of the most common causes of a "query that used to be fast."
**Answer:** If `OrderNumber` is `VARCHAR(20)` and the query says `WHERE OrderNumber = 12345` (an unquoted number), the engine performs an **implicit conversion**, casting every row's `OrderNumber` to a number to compare — this defeats any index on that column, turning a seek into a full scan. The fix is matching the literal's type to the column's type (`= '12345'`). This shows up in execution plans as `CONVERT_IMPLICIT` and is frequently caused by ORMs sending the wrong parameter type. This is correct because it names the exact mechanism (conversion applied to the *column* side of the predicate) that breaks index usage, not just "types should match."

#### Q6. Design the table schema for an Employee table storing ID, name, department, salary, and hire date, with the correct data types.
*Why interviewers ask this:* A basic hands-on DDL/data-types check that also reveals whether a candidate defaults to sane, sized types.
**Answer:**
```sql
CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    Name       VARCHAR(50) NOT NULL,
    Department VARCHAR(30),
    Salary     DECIMAL(10,2) CHECK (Salary > 0),
    HireDate   DATE
);
```
`INT` for a surrogate ID (fine unless the table will exceed ~2.1 billion rows, in which case `BIGINT`), `VARCHAR` sized to the realistic domain rather than an oversized default, `DECIMAL(10,2)` — never `FLOAT` — for money, and `DATE` (not a string) for the hire date so date arithmetic and correct sorting work natively. This is correct because every type choice is justified by how the column will actually be used, which is what separates a working schema from a technically-valid-but-sloppy one.

---

## 2. Modifying Data

*(full notes: [04_SQL_DDL.md](04_SQL_DDL.md), [05_SQL_DML.md](05_SQL_DML.md))*

#### Q7. What is the difference between `DELETE`, `TRUNCATE`, and `DROP`? **[Frequently Asked]**
*Why interviewers ask this:* One of the single most common SQL interview questions at every level — near-guaranteed to appear.
**Answer:** `DELETE` (DML) removes rows one at a time, can use a `WHERE` clause, is fully logged, and can be rolled back before commit. `TRUNCATE` (DDL) removes *all* rows at once, cannot have a `WHERE`, resets identity counters, and is minimally logged — much faster, but an all-or-nothing operation. `DROP` (DDL) removes the entire table object — structure and data both — and is irreversible without a backup. This is correct because it distinguishes both the *scope* (rows only vs. the whole table) and the *category* (DML vs. DDL, which affects transactional behavior) rather than just listing three verbs that "delete stuff."

#### Q8. Why is `UPDATE Employee SET Salary = 70000;` (with no `WHERE`) one of the most dangerous mistakes in SQL? **[Frequently Asked]**
*Why interviewers ask this:* Tests basic safety discipline, often as a lead-in to asking about a candidate's actual production habits.
**Answer:** Without a `WHERE` clause, the statement applies to *every row in the table* — every employee's salary becomes 70000, silently and instantly. The professional safety habit is to first run the equivalent `SELECT` with the same `WHERE` clause to confirm exactly which rows will be affected, then convert it to the `UPDATE`/`DELETE` only after reviewing that result. This is correct because it identifies the actual mechanism of the danger (unscoped mutation) and gives the concrete preventive habit interviewers want to hear, not just "be careful."

#### Q9. Write a single SQL statement that inserts a new employee row if the ID doesn't exist, or updates their salary and department if it does.
*Why interviewers ask this:* A very common practical question — tests whether the candidate knows `MERGE`/upsert syntax, one of the most-used statements in real data pipelines.
**Answer:**
```sql
MERGE INTO Employee AS target
USING (SELECT 107 AS EmployeeID, 'Kabir' AS Name, 'IT' AS Department, 64000 AS Salary) AS source
  ON target.EmployeeID = source.EmployeeID
WHEN MATCHED THEN
  UPDATE SET Salary = source.Salary, Department = source.Department
WHEN NOT MATCHED THEN
  INSERT (EmployeeID, Name, Department, Salary)
  VALUES (source.EmployeeID, source.Name, source.Department, source.Salary);
```
This is correct because `MERGE` does insert-or-update by key in a single atomic statement — the standard "upsert" pattern (Postgres equivalently uses `INSERT ... ON CONFLICT DO UPDATE`) — rather than requiring two separate statements with a race condition between them.

#### Q10. How would you safely add a `NOT NULL` column with no default to a table that already has a billion rows, without causing an outage? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic, high-stakes scenario that filters for candidates who've actually operated large production tables.
**Answer:** Adding a `NOT NULL` column with no default directly forces a full table rewrite to validate every existing row — hours of locking on a billion-row table. Instead: add the column as **nullable** first (a metadata-only operation on modern engines, instant regardless of table size), backfill the existing rows in small batches, then enforce `NOT NULL` only once every row has a value. This is correct because it sequences the change into steps that are each individually cheap, rather than one operation that forces an expensive, blocking rewrite.

#### Q11. Your nightly load job failed 60% of the way through and was automatically retried by the orchestrator. What must be true about the load for the table to end up correct? **[Senior/Experienced]**
*Why interviewers ask this:* Tests idempotency — arguably the single most important production-pipeline concept, and a very common scenario question.
**Answer:** The load must be **idempotent** — safe to run more than once without duplicating or corrupting data. The standard patterns, in order of preference: `MERGE` on a business key (re-running converges to the same end state); a scoped delete-then-insert inside one transaction (`DELETE WHERE load_date = 'X'` then insert that day's rows); or staging-plus-atomic-swap (load to staging, validate, then swap into place). A blind `INSERT ... VALUES` append is *not* idempotent and will duplicate rows on retry. This is correct because it directly answers what the table looks like after a retry — which is the exact thing the scenario is testing — rather than describing retries in the abstract.

#### Q12. What's the fastest way to load 10 million rows into a table, and why is row-by-row `INSERT` the wrong approach?
*Why interviewers ask this:* Tests whether the candidate understands the cost of per-statement overhead at pipeline scale.
**Answer:** A million individual `INSERT` statements means a million network round-trips and a million individually-logged operations — each one paying connection, parsing, and transaction-log overhead. The correct approach is a **bulk load path**: `BULK INSERT`/`bcp` in SQL Server, `COPY` in PostgreSQL, `COPY INTO` in Synapse/Databricks — these batch rows, minimize logging, and bypass per-row overhead, typically 100× faster than row-by-row inserts. This is correct because it names the actual bottleneck (per-statement overhead multiplied by row count) and the standard engine-specific fix, rather than a generic "batch it" answer.

---

## 3. Querying Data

*(full notes: [06_SQL_DQL.md](06_SQL_DQL.md), [07_SQL_Keys_and_Joins.md](07_SQL_Keys_and_Joins.md), [08_SQL_Aggregate_Functions.md](08_SQL_Aggregate_Functions.md))*

#### Q13. What is the difference between `WHERE` and `HAVING`? **[Frequently Asked]**
*Why interviewers ask this:* The single most common point of confusion for SQL learners, and therefore one of the most reliably asked questions of all.
**Answer:** `WHERE` filters individual *rows*, before any grouping happens. `HAVING` filters *groups*, after `GROUP BY` has aggregated the rows. You cannot write `WHERE AVG(Salary) > 55000` because no averaging has happened yet at the point `WHERE` runs — that condition must go in `HAVING`. This is correct because it ties the distinction to the actual [logical evaluation order](#q2-what-is-the-logical-order-in-which-a-sql-query-is-actually-evaluated-and-why-does-it-matter) rather than presenting it as an arbitrary rule to memorize.

#### Q14. Explain the four common join types with an example each. **[Frequently Asked]**
*Why interviewers ask this:* Guaranteed to come up in some form — joins are the most fundamental multi-table SQL skill.
**Answer:** **INNER JOIN** returns only rows that match in both tables. **LEFT JOIN** returns all rows from the left table plus matches from the right (unmatched right-side columns come back NULL) — e.g. every customer, even those with zero orders. **RIGHT JOIN** is the mirror of LEFT. **FULL JOIN** returns all rows from both tables, matched where possible, NULL where not. This is correct because it states which side is guaranteed to be complete for each join type, which is the detail that actually matters when choosing between them in a real query.

#### Q15. Write a query to find the second-highest salary in the Employee table. **[Frequently Asked]**
*Why interviewers ask this:* One of the most classic SQL interview questions of all time — nearly guaranteed at some point in a candidate's career.
**Answer:**
```sql
-- Method 1: OFFSET/FETCH
SELECT DISTINCT Salary
FROM Employee
ORDER BY Salary DESC
OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY;

-- Method 2: window function (extends cleanly to "Nth highest")
SELECT Salary FROM (
  SELECT Salary, DENSE_RANK() OVER (ORDER BY Salary DESC) AS rnk
  FROM Employee
) t
WHERE rnk = 2;
```
`DISTINCT` in method 1 avoids returning a tied duplicate salary as both 1st and 2nd. `DENSE_RANK` in method 2 is the more robust general form since changing `rnk = 2` to any N answers "Nth highest" without rewriting the query, and it correctly handles ties (two employees tied for 1st both get rank 1, and the next distinct salary is rank 2). This is correct because it gives both the quick answer and the pattern that generalizes to the follow-up question interviewers almost always ask next ("now the Nth highest").

#### Q16. A `LEFT JOIN` with a `WHERE` condition on the right table's column is returning fewer rows than expected — why, and how do you fix it? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common real SQL bugs, and a favorite "find the mistake" interview prompt.
**Answer:**
```sql
-- BUG: turns the LEFT JOIN back into an INNER JOIN
SELECT c.Name, o.Amount
FROM Customer c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID
WHERE o.Status = 'Shipped';   -- customers with no orders have o.Status = NULL, which fails this filter

-- FIX: move the right-table condition into the ON clause
SELECT c.Name, o.Amount
FROM Customer c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID AND o.Status = 'Shipped';
```
The `WHERE` clause runs *after* the join and filters out any row where `o.Status` is NULL — which includes every unmatched customer the LEFT JOIN was supposed to preserve. Moving the condition into `ON` filters the right side *before* the join happens, keeping every left-side row. This is correct because it identifies exactly why the row count drops (WHERE silently eliminates the NULL rows the join intentionally produced) rather than just stating the fix as a rule.

#### Q17. A report's totals doubled after a colleague added a join to enrich the data with product names. What went wrong? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of join "grain" — one of the most valuable, under-taught SQL concepts, and a very realistic production bug.
**Answer:** This is a **fan-out**: the join was one-to-many rather than one-to-one, so each fact row was duplicated once per matching row on the other side (e.g. joining Orders to a Products table that has multiple price-history rows per product), and any subsequent `SUM` counted each order multiple times. The fix is to check each table's **grain** before joining (what does one row represent?), verify row counts before vs. after the join, and pre-aggregate or deduplicate the many-side down to one row per key before joining if you need one-to-one behavior. This is correct because it names the actual mechanism (grain mismatch causing row multiplication) rather than "there's a bug in the join," which is what a senior-level answer needs to demonstrate.

#### Q18. Write a query to find departments where the average salary exceeds 55000, but only counting employees earning more than 40000. **[Frequently Asked]**
*Why interviewers ask this:* A compact test of WHERE, GROUP BY, and HAVING working together — extremely common in practical interview rounds.
**Answer:**
```sql
SELECT Department, AVG(Salary) AS AvgSalary
FROM Employee
WHERE Salary > 40000
GROUP BY Department
HAVING AVG(Salary) > 55000;
```
Reading the execution order: `WHERE` first discards any individual employee earning 40000 or less; the remaining rows are then grouped by department and averaged; `HAVING` then keeps only the departments whose *group average* exceeds 55000. This is correct because each clause is applied at the correct stage — a common wrong answer puts the salary threshold in `HAVING` instead of `WHERE`, which would compute the average over rows that should have been excluded first.

#### Q19. Write a query to return the top 3 highest-paid employees in each department. **[Frequently Asked]**
*Why interviewers ask this:* The canonical "top-N per group" problem — one of the most common practical SQL questions across all interview levels.
**Answer:**
```sql
SELECT Name, Department, Salary FROM (
  SELECT Name, Department, Salary,
         ROW_NUMBER() OVER (PARTITION BY Department ORDER BY Salary DESC) AS rn
  FROM Employee
) ranked
WHERE rn <= 3;
```
This is correct because `ROW_NUMBER()` with `PARTITION BY Department` restarts the ranking for every department independently, and filtering `rn <= 3` in an outer query (required, since `WHERE` can't see window function results directly) keeps exactly the top 3 salaries per group — the standard window-function solution to "top-N per group," which replaced older, slower correlated-subquery approaches.

#### Q20. `COUNT(*)`, `COUNT(column)`, and `COUNT(DISTINCT column)` — what's the difference? **[Frequently Asked]**
*Why interviewers ask this:* A quick, high-frequency question that tests understanding of NULL handling in aggregates.
**Answer:** `COUNT(*)` counts every row regardless of NULLs. `COUNT(column)` counts only rows where that specific column is non-NULL — aggregates ignore NULLs. `COUNT(DISTINCT column)` counts unique non-NULL values. This is correct because it explicitly ties the difference to NULL-handling, which is also why `COUNT(*)` and `COUNT(some_column)` can legitimately return different numbers on the same table — a fact often used as a quick data-quality check (row count vs. non-null count reveals how many NULLs exist).

#### Q21. Why is `COUNT(DISTINCT user_id)` expensive on a billion-row table, and what would you use instead for a dashboard? **[Senior/Experienced]**
*Why interviewers ask this:* Tests awareness of approximate algorithms, a genuinely senior-level performance concept.
**Answer:** Exact `COUNT(DISTINCT)` requires tracking every unique value seen, which is memory-hungry and, in distributed engines, forces a full shuffle to deduplicate globally across nodes. At billions of rows, the standard mitigation for dashboards is an **approximate** count using HyperLogLog (`APPROX_COUNT_DISTINCT`), which returns a result within roughly 2% error at a fraction of the cost — exact counts are reserved for reconciliation/audit queries where precision actually matters. This is correct because it names the underlying cost (global uniqueness tracking) and the specific mitigation technique (HLL-based approximation), rather than a vague "it's slow at scale."

#### Q22. Write a query that pivots sales data to show revenue for Electronics and Grocery categories as separate columns, per store.
*Why interviewers ask this:* Tests conditional aggregation ("pivoting by hand"), a workhorse pattern in real reporting SQL.
**Answer:**
```sql
SELECT StoreID,
  SUM(CASE WHEN Category = 'Electronics' THEN Amount ELSE 0 END) AS electronics_rev,
  SUM(CASE WHEN Category = 'Grocery'     THEN Amount ELSE 0 END) AS grocery_rev
FROM Sales
GROUP BY StoreID;
```
This is correct because wrapping the aggregate in a `CASE` expression computes several filtered measures in a *single pass* over the table, which is far cheaper than running one separate query per category and joining the results together — the standard "pivot by hand" pattern used constantly in reporting layers (modern engines like Postgres/BigQuery/Databricks offer `FILTER (WHERE ...)` as cleaner syntax for the same idea).

---

## 4. Advanced Querying

*(full notes: [09_SQL_Subqueries.md](09_SQL_Subqueries.md), [10_SQL_Views.md](10_SQL_Views.md), [11_SQL_Indexes.md](11_SQL_Indexes.md))*

#### Q23. What is a correlated subquery, and how is it different from a regular subquery? **[Frequently Asked]**
*Why interviewers ask this:* Tests understanding of execution semantics, not just subquery syntax.
**Answer:** A regular (uncorrelated) subquery runs once, independently, and produces a fixed value or list the outer query uses. A **correlated** subquery references a column from the outer query, so conceptually it re-evaluates once per outer row. Example: finding employees who earn more than their *own department's* average requires a correlated subquery, because "average" means something different for every employee's row. This is correct because it distinguishes them by *what they can reference* (nothing outside vs. the current outer row), which is also exactly why one runs once and the other conceptually runs per-row.

#### Q24. Why does `WHERE CustomerID NOT IN (SELECT CustomerID FROM Orders)` sometimes return zero rows, even when it obviously shouldn't? **[Frequently Asked]**
*Why interviewers ask this:* One of the most famous SQL "gotchas" — a very commonly asked trick question that separates surface-level SQL knowledge from real understanding of NULL logic.
**Answer:** If the `Orders.CustomerID` subquery result contains even a single `NULL`, the entire `NOT IN` predicate evaluates to unknown for every row and returns zero results. This is because `NOT IN (1, 2, NULL)` unfolds to `id<>1 AND id<>2 AND id<>NULL` — and `id<>NULL` is neither true nor false, it's unknown, which poisons the whole `AND` chain. The safe, NULL-proof alternative is `WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID)`. This is correct because it explains the exact mechanism (three-valued logic poisoning the NOT IN list) rather than just warning "avoid NOT IN," and gives the correct, idiomatic fix.

#### Q25. Rewrite this correlated subquery as a window function, and explain why you might prefer the rewrite: `SELECT Name, Salary FROM Employee E1 WHERE Salary > (SELECT AVG(Salary) FROM Employee E2 WHERE E2.Department = E1.Department)`. **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether the candidate can translate between two equivalent SQL idioms and reason about when it matters for performance.
**Answer:**
```sql
SELECT Name, Department, Salary
FROM (
  SELECT *, AVG(Salary) OVER (PARTITION BY Department) AS dept_avg
  FROM Employee
) t
WHERE Salary > dept_avg;
```
Both return the same result, and on some modern optimizers the correlated version is automatically **decorrelated** into an equivalent plan — but decorrelation isn't guaranteed on every engine or in every case, and when it fails, the correlated version can execute once per outer row, fine for 100 rows and catastrophic for 100 million. The window-function version computes the department average in a single pass, deterministically. This is correct because it shows both forms and states precisely *when* the rewrite matters (large tables, engines that don't reliably decorrelate) instead of claiming one form is universally faster.

#### Q26. Does querying a view run slower than querying the underlying table directly? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether the candidate understands what a view actually is internally, a very common point of confusion.
**Answer:** No — a plain view isn't pre-computed or cached; the optimizer **inlines** its definition into your query and optimizes the combined query as one unit. `SELECT * FROM ITEmployees WHERE Salary > 60000` (where the view filters `Department = 'IT'`) plans exactly as if you'd written `WHERE Department = 'IT' AND Salary > 60000` directly — your filter can still use the base table's indexes. A **materialized view**, by contrast, does store a physical result and trades freshness for speed. This is correct because it corrects the common misconception (views = cached data) and names the actual mechanism (query inlining) that explains why plain views add zero overhead by themselves.

#### Q27. Write a view that exposes employee names and departments to a reporting team, without exposing salary. **[Frequently Asked]**
*Why interviewers ask this:* Tests the very common "expose limited data without granting table access" security pattern.
**Answer:**
```sql
CREATE VIEW hr.EmployeeDirectory AS
SELECT EmployeeID, Name, Department
FROM dbo.Employee
WHERE is_deleted = 0;

GRANT SELECT ON hr.EmployeeDirectory TO reporting_role;
```
This is correct because access control happens by **revoking direct table access and granting only on the view** — the view's column list simply omits Salary, so the reporting role can never select it, and the `is_deleted` filter is baked in once so every consumer automatically sees only active employees without remembering to add that condition themselves.

#### Q28. How does an index make a lookup on a 100-million-row table fast? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether "indexes make things faster" is backed by an actual mechanical understanding.
**Answer:** Without an index, the engine performs a full table scan — checking all 100 million rows one at a time. An index builds a sorted structure (typically a B-tree) over the indexed column; the engine walks from the root of the tree to the matching leaf, usually in just 3–4 page reads regardless of table size, landing directly on the matching row(s) instead of scanning everything. This is correct because it names the actual data structure and states the complexity difference concretely (a handful of page reads vs. millions of row checks), rather than the analogy alone.

#### Q29. What's the difference between a clustered and a nonclustered index? **[Senior/Experienced]**
*Why interviewers ask this:* A step beyond "what is an index" that tests real database-internals knowledge, common in senior-level rounds.
**Answer:** A **clustered index** physically orders the table's data by the indexed key — it *is* the table storage, and there can only be one per table (data can only be sorted one physical way). A **nonclustered index** is a separate structure of `(key columns) → pointer to the row`, and a table can have many. Looking up via a nonclustered index means finding the pointer in the index, then a **key lookup** back to the actual row for any column not in the index — cheap for a handful of rows, worse than a full scan for a large fraction of the table, which is exactly why the optimizer sometimes correctly ignores a nonclustered index for a low-selectivity predicate. This is correct because it explains the key-lookup cost, which is the detail that explains *why* nonclustered indexes aren't a universal win.

#### Q30. You add an index on `WHERE YEAR(OrderDate) = 2026`, but the query still does a full scan. Why? **[Senior/Experienced]**
*Why interviewers ask this:* Tests sargability — a genuinely high-value, often-missed performance concept.
**Answer:** `YEAR(OrderDate)` wraps the indexed column in a function, forcing the engine to compute `YEAR()` on *every row* before it can compare — this makes the predicate **non-sargable**, so the index can't be used for a seek no matter how well it's built. The fix is to rewrite the condition to leave the column bare: `WHERE OrderDate >= '2026-01-01' AND OrderDate < '2027-01-01'`. This is correct because it identifies the actual rule (functions wrapped around the *column* defeat index seeks, regardless of whether an index exists) rather than "the index is wrong," and gives the standard sargable rewrite pattern.

#### Q31. Design an index to best support this query: `SELECT * FROM Orders WHERE CustomerID = ? AND OrderDate > ? ORDER BY OrderDate`. **[Senior/Experienced]**
*Why interviewers ask this:* A hands-on index-design question, testing the equality-before-range and covering-index concepts together.
**Answer:**
```sql
CREATE INDEX idx_cust_date ON Orders (CustomerID, OrderDate) INCLUDE (Amount, Status);
```
Composite index column order matters: equality predicates go first (`CustomerID`), range predicates go last (`OrderDate`) — this follows the leftmost-prefix rule, since an index sorted `(CustomerID, OrderDate)` can seek to a specific customer and then scan their orders in date order directly, which also satisfies the `ORDER BY` for free. Adding frequently-selected non-key columns via `INCLUDE` makes it a **covering index**, so the query never has to visit the base table at all. This is correct because it applies both index-design rules together (equality-then-range ordering, and covering columns) to the exact query shape given, rather than a generic "index the WHERE columns" answer.

---

## 5. Control

*(full notes: [12_SQL_DCL_TCL.md](12_SQL_DCL_TCL.md))*

#### Q32. What is the difference between DCL and TCL? **[Frequently Asked]**
*Why interviewers ask this:* Checks that the candidate knows all five SQL command categories, not just DDL/DML/DQL.
**Answer:** DCL (Data Control Language — `GRANT`, `REVOKE`) controls *who is allowed* to do what to the data. TCL (Transaction Control Language — `COMMIT`, `ROLLBACK`, `SAVEPOINT`) controls *how a group of changes* becomes permanent or gets undone. This is correct because it separates permissions (a security concern) from transaction boundaries (a correctness/atomicity concern) — two categories that are easy to conflate since both are about "controlling" SQL rather than directly reading or writing data.

#### Q33. Explain ACID's "Atomic" guarantee using a bank transfer example, and show the SQL that enforces it. **[Frequently Asked]**
*Why interviewers ask this:* A guaranteed classic — tests both conceptual understanding and the ability to write the actual enforcing SQL.
**Answer:**
```sql
BEGIN TRANSACTION;
UPDATE Account SET Balance = Balance - 500 WHERE AccountID = 1;
UPDATE Account SET Balance = Balance + 500 WHERE AccountID = 2;
COMMIT;
```
Both `UPDATE` statements together represent "transfer 500." `COMMIT` makes both permanent together — if the system crashed between the two statements and before `COMMIT`, **neither** change would be saved, because a transaction is all-or-nothing. This is correct because it grounds "Atomic" in the exact SQL construct that provides the guarantee, not just the definition — money can never leave one account without either fully arriving in the other or the whole transfer being undone.

#### Q34. What is a deadlock, and how would you design a system to avoid one? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real concurrency-control experience, common in senior backend/data-engineering interviews.
**Answer:** A deadlock happens when Transaction A locks row 1 and then wants row 2, while Transaction B has already locked row 2 and wants row 1 — neither can proceed, so the engine kills one as the "deadlock victim." Defenses, in order: touch tables/rows in a **consistent order** across every code path (e.g. always by ascending key); keep transactions **short and indexed** so fewer rows are locked for less time; use **snapshot isolation (RCSI)**, which removes reader-writer deadlocks entirely; and add automatic **retry logic with backoff** for the survivors, since deadlocks are transient by definition. This is correct because it gives a layered, ordered set of real defenses rather than a single trick, matching how this is actually handled in production systems.

#### Q35. Do Delta Lake tables in a lakehouse support transactions the same way a traditional database does? **[Senior/Experienced]**
*Why interviewers ask this:* Bridges classic OLTP transaction knowledge to the modern lakehouse world — increasingly common as interviews shift toward Spark/Databricks content.
**Answer:** Delta gives ACID guarantees, but through **optimistic concurrency** on a transaction log rather than locking: writers prepare files and then attempt to commit a new log version; a conflicting concurrent commit fails one writer, which must retry. Key differences from a database: there are **no multi-table transactions** — you cannot atomically commit across two Delta tables, so each table's write must be independently idempotent; and there are no locks, so long-running writes never block readers — conflicts only surface at commit time. This is correct because it states both what's preserved (single-table ACID) and what's genuinely different (no cross-table atomicity, no locking), which is exactly the nuance a senior answer needs to avoid over- or under-claiming Delta's guarantees.

---

## 6. Warehousing

*(full notes: [13_SQL_Warehouse.md](13_SQL_Warehouse.md))*

#### Q36. Design a star schema for a retail sales warehouse. Walk through your reasoning. **[Frequently Asked]**
*Why interviewers ask this:* One of the most common warehouse-design interview questions — tests the full dimensional modeling thought process, not just the final diagram.
**Answer:** Following the standard four-step design process: (1) **business process** — a completed sale; (2) **grain** — one row per product per order line, the single most important design decision, since every fact must be true at that exact grain; (3) **dimensions** — Date, Product, Store, Customer, Promotion (the "by" words in business questions — sales *by* store *by* month); (4) **facts** — quantity, unit price, line amount, all numeric and additive at the chosen grain. The fact table holds only keys and numbers; text descriptions live in dimensions; every fact-to-dimension relationship goes through a surrogate key; and any late-arriving or unknown dimension member resolves to a `-1 / 'Unknown'` row so facts never orphan. This is correct because it follows Kimball's standard methodology in the right order — grain before dimensions, dimensions before facts — which is exactly the sequence a real design conversation follows.

#### Q37. A customer moves from Pune to Hyderabad. How would you preserve historically accurate reporting (sales made while they lived in Pune should still show Pune)? **[Frequently Asked]**
*Why interviewers ask this:* The canonical Slowly Changing Dimension question — extremely common in warehouse/BI interviews.
**Answer:** This is solved with a **Slowly Changing Dimension Type 2**: instead of overwriting the customer's city, insert a *new row* for the same customer with updated `city`, a `valid_from`/`valid_to` date range, and an `is_current` flag marking the new row active. Sales made before the move still join to the old (now-expired) dimension row via the fact table's stored surrogate key, so historical reports remain accurate; only new sales join to the new row. This is correct because it explains *why* SCD Type 2 works — the fact table's surrogate key is fixed at load time, so it permanently points to the dimension version that was current when the sale happened, regardless of later changes.

#### Q38. Why does a warehouse typically NOT enforce foreign key constraints the way an OLTP database does? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of the practical trade-offs in warehouse design versus OLTP, a genuinely senior-level distinction.
**Answer:** Enforcing FK constraints on every bulk load of a billion-row fact table would be prohibitively expensive to validate. Warehouses (Synapse, Delta) typically **declare but don't enforce** foreign keys — integrity instead moves into the pipeline: dimensions are always loaded before facts, unresolved/unknown keys are pointed at a default `-1 'Unknown'` dimension row instead of being rejected, and orphan counts are checked with automated tests (dbt tests, Delta constraints) rather than blocking every insert. This is correct because it explains the actual cost trade-off (per-row constraint validation at bulk-load scale) and names the specific pipeline-level techniques that replace database-level enforcement.

#### Q39. Star schema vs. snowflake schema — what's the difference, and which would you default to? **[Frequently Asked]**
*Why interviewers ask this:* A very standard warehouse-modeling comparison question.
**Answer:** A **star schema** keeps dimension tables denormalized — e.g. a Product dimension has Category as a plain text column, not a separate linked table — so a fact table needs only one join per dimension. A **snowflake schema** normalizes dimensions further into sub-dimensions (Product → Category → Department), saving some storage at the cost of extra joins. Star is the default choice for BI because query simplicity and performance usually matter more than the modest storage savings snowflaking provides. This is correct because it identifies the actual trade-off (join count vs. storage) rather than just naming the shapes, and gives the practical default with its justification.

---

## Rapid-Fire Round

- Q: What does SQL stand for? — A: Structured Query Language.
- Q: What are the five SQL command categories? — A: DDL, DML, DQL, DCL, TCL.
- Q: What's the actual first clause evaluated in a SELECT query? — A: FROM (not SELECT).
- Q: WHERE or HAVING — which filters before grouping? — A: WHERE.
- Q: DELETE vs TRUNCATE — which can use a WHERE clause? — A: DELETE.
- Q: Which join returns all rows from the left table regardless of a match? — A: LEFT JOIN.
- Q: What does a correlated subquery reference that an uncorrelated one cannot? — A: A column from the outer query.
- Q: `NOT IN` with a NULL in the subquery result returns how many rows? — A: Zero.
- Q: What's the NULL-safe replacement for `NOT IN (subquery)`? — A: `NOT EXISTS`.
- Q: UNION or UNION ALL — which is cheaper? — A: UNION ALL (no dedup sort/hash).
- Q: What SQL feature lets you rank rows without collapsing them, unlike GROUP BY? — A: Window functions.
- Q: ROW_NUMBER vs RANK on a tie — which gives unique numbers? — A: ROW_NUMBER.
- Q: What does a view store physically? — A: Nothing — it's a saved query, re-run each time (unless materialized).
- Q: Clustered or nonclustered — which physically orders the table? — A: Clustered.
- Q: What makes a predicate "non-sargable"? — A: Wrapping the column in a function or expression, preventing an index seek.
- Q: What are the four ACID properties? — A: Atomicity, Consistency, Isolation, Durability.
- Q: COMMIT vs ROLLBACK — which undoes a transaction? — A: ROLLBACK.
- Q: What does a SAVEPOINT allow? — A: Undoing part of a transaction without rolling back the whole thing.
- Q: Star or snowflake — which is more denormalized? — A: Star.
- Q: What kind of key should a fact table use to join to dimensions? — A: A surrogate key.
- Q: SCD Type 1 vs Type 2 — which preserves history? — A: Type 2 (via new rows with validity ranges).
- Q: What single statement does an "upsert" in modern SQL? — A: MERGE (or INSERT ... ON CONFLICT in Postgres).
- Q: Why avoid `SELECT *` in production pipeline code? — A: Breaks contracts on schema change, defeats column pruning, wastes network/memory.
- Q: What's the safe habit before running a bulk UPDATE/DELETE? — A: Run the equivalent SELECT with the same WHERE first.

Back to the folder: [01_SQL notes](.) · Related: [00_Fundamentals Interview Q&A](../../01_Foundations/Fundamentals/Interview_Questions_and_Answers.md)

---

## Further Learning — Docs & Videos

**Documentation**
- SQL practice (LeetCode Database): https://leetcode.com/studyplan/top-sql-50/
- SQL interview questions (DataCamp): https://www.datacamp.com/blog/sql-interview-questions

**Videos**
- SQL interview questions & answers: https://www.youtube.com/results?search_query=sql+interview+questions+and+answers+data+engineer
- SQL query interview problems: https://www.youtube.com/results?search_query=sql+query+interview+questions+solved
