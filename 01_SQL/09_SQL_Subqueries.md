# SQL Subqueries

## What is a subquery?

A subquery is a `SELECT` query written inside another query, used to answer a question that depends on the result of a smaller question first.

Analogy: "Find every employee who earns more than the *average* salary" can't be answered in a single, direct comparison, because you don't know the average salary until you've calculated it. A subquery calculates that average first, then feeds it into the main query — like a clerk who first tallies up a company-wide average on a scratchpad, then walks through employee records comparing each one against that scratchpad number.

---

## A Subquery in WHERE

```sql
SELECT Name, Salary
FROM Employee
WHERE Salary > (
    SELECT AVG(Salary) FROM Employee
);
```

The inner query (`SELECT AVG(Salary) FROM Employee`) runs first and produces a single number. The outer query then uses that number as if it had been typed in directly.

---

## Subqueries with IN

Return rows where a column matches *any* value from a list produced by another query:

```sql
SELECT Name
FROM Employee
WHERE Department IN (
    SELECT Department FROM Department WHERE Region = 'South'
);
```

"Show me employees whose department is one of the departments located in the South region" — without needing to know or type those department names directly.

---

## Correlated Subqueries

A regular subquery runs once, independently. A **correlated** subquery references the outer query and re-runs once *for every row* the outer query considers.

```sql
SELECT Name, Salary, Department
FROM Employee E1
WHERE Salary > (
    SELECT AVG(Salary)
    FROM Employee E2
    WHERE E2.Department = E1.Department
);
```

This finds employees earning more than the average *for their own department* (not the company-wide average) — the inner query recalculates a fresh average for each employee's specific department as it goes.

---

## Subqueries vs Joins

Many subqueries can be rewritten as a [join](07_SQL_Keys_and_Joins.md), and vice versa. As a rough guide:

| Use a subquery when | Use a join when |
|---|---|
| You need a single calculated value to compare against (e.g. an average, a max) | You need to combine columns from both tables in the final result |
| The logic reads more clearly as "first find X, then find Y using X" | You need matching rows from two tables side by side |

Neither is universally "faster" — it depends on the specific database engine and the size of the tables involved. Readability is often the better tiebreaker for a beginner.

---

## EXISTS — checking for existence rather than a value

```sql
SELECT Name
FROM Customer C
WHERE EXISTS (
    SELECT 1 FROM Orders O WHERE O.CustomerID = C.CustomerID
);
```

"Show me every customer who has placed at least one order." `EXISTS` only cares *whether* the inner query returns any rows at all, not what those rows contain — often faster than an equivalent `IN` subquery on large tables.

---

## Azure Usage

Subqueries run the same way in Azure SQL Database, Synapse Analytics, and Databricks' Spark SQL as in standard SQL. In large-scale analytics on Synapse, correlated subqueries should be used carefully — because they can re-run once per outer row, they can become slow on very large tables, and a join or a window function is sometimes a faster alternative.

---

## Real World Example

A university wants a list of students who scored above the *average* score in their *own* course — not the average across the entire university. A correlated subquery recalculates the relevant average freshly for each student's specific course before comparing.

---
---

# Part 2 — Advanced

## CTEs — subqueries you can read

A **Common Table Expression** (`WITH`) names a subquery up front, turning nested logic into a readable pipeline:

```sql
WITH dept_avg AS (
    SELECT Department, AVG(Salary) AS avg_salary
    FROM Employee
    GROUP BY Department
),
above_avg AS (
    SELECT e.Name, e.Department, e.Salary, d.avg_salary
    FROM Employee e
    JOIN dept_avg d ON d.Department = e.Department
    WHERE e.Salary > d.avg_salary
)
SELECT * FROM above_avg ORDER BY Salary DESC;
```

Same result as the correlated subquery — but each step is named, testable (`SELECT * FROM dept_avg` while developing), and reusable within the query. Modern style guides (and dbt's entire methodology) prefer chained CTEs over deep nesting. Note: a CTE is *not automatically materialized* — most engines inline it like a view; referencing one CTE five times may run it five times (Postgres offers `WITH ... AS MATERIALIZED` to pin it).

## Recursive CTEs — SQL that walks hierarchies

The one thing plain SELECT can't do — traverse arbitrary-depth trees (org charts, BOMs, folder structures):

```sql
WITH RECURSIVE org AS (
    SELECT EmployeeID, Name, ManagerID, 1 AS depth      -- anchor: the CEO
    FROM Employee WHERE ManagerID IS NULL
    UNION ALL
    SELECT e.EmployeeID, e.Name, e.ManagerID, o.depth+1 -- recursive step
    FROM Employee e JOIN org o ON e.ManagerID = o.EmployeeID
)
SELECT * FROM org;    -- every employee with their depth under the CEO
```

(T-SQL: same shape without the `RECURSIVE` keyword.) Guard against cycles (`WHERE depth < 20` / `OPTION (MAXRECURSION ...)`).

## Where else subqueries live

- **Derived tables** — a subquery in FROM: `SELECT ... FROM (SELECT ...) AS t` — the pre-CTE way; still common.
- **Scalar subqueries in SELECT** — `SELECT Name, (SELECT COUNT(*) FROM Orders o WHERE o.CustomerID = c.CustomerID) FROM Customer c` — readable but *correlated per row*; on big outer tables rewrite as a pre-aggregated join.
- **LATERAL / CROSS APPLY** — a subquery in FROM that *can* reference previous tables — "top 3 orders per customer" without window functions:

```sql
SELECT c.Name, t.OrderID, t.Amount
FROM Customer c
CROSS APPLY (SELECT TOP 3 OrderID, Amount
             FROM Orders o WHERE o.CustomerID = c.CustomerID
             ORDER BY Amount DESC) t;
```

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The NOT IN + NULL trap (worth memorizing verbatim)

```sql
SELECT Name FROM Customer
WHERE CustomerID NOT IN (SELECT CustomerID FROM Orders);
-- If Orders.CustomerID contains even ONE NULL → returns ZERO rows. Always.
```

Why: `id NOT IN (1, 2, NULL)` unfolds to `id<>1 AND id<>2 AND id<>NULL`; the last is *unknown*, poisoning the whole predicate ([three-valued logic](01_What_is_SQL.md)). The professional default for anti-joins:

```sql
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID)
```

`NOT EXISTS` is NULL-safe, states intent, and optimizes to a proper anti-join.

## Does "correlated = slow" still hold?

Nuanced answer that distinguishes seniors: modern optimizers **decorrelate** many correlated subqueries into joins/aggregations automatically — the two spellings often produce identical plans. But decorrelation has limits (complex correlations, some engines' apply operators), and when it fails you get once-per-row execution: fine for 100 outer rows, catastrophic for 100 million. The pro workflow: write for clarity, **check the plan** ([reading plans](06_SQL_DQL.md)), and rewrite to window functions or pre-aggregated CTE joins when you see per-row apply on a big input. Window functions replace the classic correlated patterns wholesale:

```sql
-- "above own department's average" — one scan, no correlation
SELECT Name, Department, Salary
FROM (SELECT *, AVG(Salary) OVER (PARTITION BY Department) AS dept_avg
      FROM Employee) t
WHERE Salary > dept_avg;
```

## Subqueries in distributed engines

In Spark SQL / Synapse, every subquery is a plan subtree — the concerns shift to data movement:

- An uncorrelated scalar subquery becomes a tiny job whose result is **broadcast** — cheap.
- `IN (subquery)` / `EXISTS` become **semi-joins**; NOT EXISTS an **anti-join** — all subject to [broadcast vs shuffle decisions](../06_PySpark/Spark_Processing.md).
- Correlated scalar subqueries must be decorrelatable or Spark rejects/struggles — another reason the window-function rewrite is the lakehouse idiom.

## Field-tested gotchas

- A scalar subquery that returns **two rows** throws a runtime error (works in dev, dies in prod when data grows) — enforce with `MAX()`/`TOP 1` + deterministic `ORDER BY` or a uniqueness guarantee.
- Subquery in a loop pattern (app code calling per-row lookups) is the N+1 problem wearing SQL clothes — set-based rewrite, always.
- Deeply nested subqueries defeat readability *and* sometimes optimizer heuristics — flatten to CTEs; the plan usually improves along with the humans.
- In `EXISTS (SELECT 1 ...)`, `SELECT *`/`1`/`42` are identical — the engine only tests row existence; don't cargo-cult a "performance" difference.

## Interview-grade Q&A

- *Why did `NOT IN` return nothing?* A NULL in the subquery's result; use NOT EXISTS.
- *Correlated vs uncorrelated?* References outer query (conceptually per-row) vs independent (runs once); optimizers often decorrelate — verify in the plan.
- *When choose a CTE over a subquery?* Multi-step logic, reuse within the query, readability/testability; recursive traversals require it.
- *Top 3 orders per customer — three ways?* Window `ROW_NUMBER` filter, `CROSS APPLY` with TOP, or a rank-filtered self-join; window is the distributed-engine default.
