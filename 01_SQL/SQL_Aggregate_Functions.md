# SQL Aggregate Functions and Grouping

## What is an aggregate function?

An aggregate function takes many rows and reduces them down to a single summary value — a total, an average, a count. This is how SQL answers "big picture" questions instead of just listing individual rows.

Analogy: [SQL_DQL.md](SQL_DQL.md) is like asking a clerk to hand you a stack of individual invoices matching some criteria. An aggregate function is asking that clerk instead to just tell you the *total* of that stack, without handing you every invoice.

---

## The Five Common Aggregate Functions

| Function | Returns |
|---|---|
| `COUNT()` | How many rows |
| `SUM()` | Total of a numeric column |
| `AVG()` | Average of a numeric column |
| `MIN()` | Smallest value |
| `MAX()` | Largest value |

```sql
SELECT COUNT(*) FROM Employee;
-- e.g. 250 — total number of employees

SELECT SUM(Salary) FROM Employee;
-- e.g. 15,000,000 — total payroll

SELECT AVG(Salary) FROM Employee;
-- e.g. 60,000 — average salary

SELECT MAX(Salary), MIN(Salary) FROM Employee;
-- highest and lowest paid employee's salary
```

Without any grouping, an aggregate function collapses the *entire table* down to one row of output.

---

## GROUP BY — aggregating per category

Usually you don't want one number for the whole table — you want one number *per department*, *per month*, *per region*. `GROUP BY` splits the table into buckets first, then applies the aggregate function separately to each bucket.

```sql
SELECT Department, AVG(Salary) AS AvgSalary
FROM Employee
GROUP BY Department;
```

Result

| Department | AvgSalary |
|---|---|
| IT | 63000 |
| HR | 51000 |
| Finance | 58000 |

Analogy: instead of one grand total for the whole company, this is like sorting invoices into labeled piles by department first, then totaling each pile separately.

**Rule to remember**: every column in the `SELECT` list must either be inside an aggregate function, or listed in `GROUP BY`. SQL doesn't know what single value to show for a non-grouped, non-aggregated column when multiple rows are being collapsed into one.

---

## HAVING — filtering on aggregated results

`WHERE` filters individual rows *before* grouping happens. `HAVING` filters groups *after* they've been aggregated. This is the single most common point of confusion for SQL beginners.

```sql
SELECT Department, AVG(Salary) AS AvgSalary
FROM Employee
WHERE Salary > 40000
GROUP BY Department
HAVING AVG(Salary) > 55000;
```

Reading it in order of execution: first throw out any individual employee earning 40000 or less (`WHERE`), then group the rest by department and average their salaries, then keep only the departments whose *average* comes out above 55000 (`HAVING`).

You cannot write `WHERE AVG(Salary) > 55000` — at the point `WHERE` runs, no averaging has happened yet.

---

## Azure Usage

Aggregate functions and `GROUP BY` are the backbone of nearly every report built on Azure SQL Database or Azure Synapse Analytics — "total sales by region," "average handling time by call center," "monthly active users by product" are all one `GROUP BY` query each. Power BI visuals are frequently just a friendly front-end over a query shaped exactly like this.

---

## Real World Example

A retail chain's monthly report — "total revenue and number of transactions per store" — is a single query: `SUM(Amount)` and `COUNT(*)`, grouped by `StoreID`, with a `HAVING COUNT(*) > 100` added to exclude any newly opened store that hasn't yet processed enough transactions to be meaningfully compared to the rest.
