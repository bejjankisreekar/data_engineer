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

Many subqueries can be rewritten as a [join](SQL_Keys_and_Joins.md), and vice versa. As a rough guide:

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
