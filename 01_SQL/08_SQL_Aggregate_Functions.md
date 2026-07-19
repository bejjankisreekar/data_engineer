# SQL Aggregate Functions and Grouping

## What is an aggregate function?

An aggregate function takes many rows and reduces them down to a single summary value — a total, an average, a count. This is how SQL answers "big picture" questions instead of just listing individual rows.

Analogy: [06_SQL_DQL.md](06_SQL_DQL.md) is like asking a clerk to hand you a stack of individual invoices matching some criteria. An aggregate function is asking that clerk instead to just tell you the *total* of that stack, without handing you every invoice.

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

---
---

# Part 2 — Advanced

## NULLs change aggregate answers

Aggregates **ignore NULLs** — which is sometimes what you want, and sometimes a silent lie:

```sql
-- 10 employees, 2 have NULL salary
SELECT COUNT(*)        -- 10  (all rows)
     , COUNT(Salary)   -- 8   (non-NULL only)
     , AVG(Salary)     -- sum of 8 ÷ 8  — NOT ÷ 10!
FROM Employee;
```

If missing should mean zero: `AVG(COALESCE(Salary, 0))`. If not, report the NULL count alongside. `SUM` of zero rows is `NULL`, not 0 — wrap in `COALESCE(SUM(x), 0)` when feeding dashboards.

## Conditional aggregation — pivoting by hand

One pass over the table, many filtered measures — a workhorse pattern in every reporting layer:

```sql
SELECT StoreID,
  SUM(CASE WHEN Category = 'Electronics' THEN Amount ELSE 0 END) AS electronics_rev,
  SUM(CASE WHEN Category = 'Grocery'     THEN Amount ELSE 0 END) AS grocery_rev,
  COUNT(CASE WHEN Amount > 1000 THEN 1 END)                      AS big_ticket_orders,
  AVG(CASE WHEN is_member = 1 THEN Amount END)                   AS avg_member_basket
FROM Sales
GROUP BY StoreID;
```

(Postgres/BigQuery/Databricks spell it more cleanly: `SUM(Amount) FILTER (WHERE Category='Grocery')` / `COUNT_IF(...)`.) One scan beats five separate queries — remember [the cost hierarchy](../00_Fundamentals/03_Distributed_Computing.md).

## Multi-level totals: ROLLUP, CUBE, GROUPING SETS

```sql
SELECT Region, StoreID, SUM(Amount) AS revenue
FROM Sales
GROUP BY ROLLUP (Region, StoreID);
-- rows: each (region, store) + subtotal per region (StoreID NULL) + grand total (both NULL)
```

- `ROLLUP(a,b)` — hierarchy subtotals: (a,b), (a), ().
- `CUBE(a,b)` — *every* combination: adds (b) alone.
- `GROUPING SETS ((a,b),(a),())` — pick exactly which levels.
- Use `GROUPING(col)` to distinguish "subtotal NULL" from a real NULL value.

## DISTINCT aggregates and their cost

`COUNT(DISTINCT user_id)` must track every unique value — memory-hungry and shuffle-heavy at scale, and most engines allow only limited mixing of different DISTINCT columns in one query. At billions of rows, pros switch to **`APPROX_COUNT_DISTINCT`** (HyperLogLog, ~2% error) for dashboards, keeping exact counts for reconciliation ([OLAP approximation](../00_Fundamentals/02_OLAP_Storage.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## GROUP BY vs window functions — collapse or annotate?

The decision every analyst makes daily: `GROUP BY` **collapses** rows into one per group; a window function **annotates** each row with its group's value ([full window coverage](06_SQL_DQL.md)):

```sql
-- "each employee's salary AND their department average, side by side"
SELECT Name, Salary,
       AVG(Salary) OVER (PARTITION BY Department) AS dept_avg,
       Salary - AVG(Salary) OVER (PARTITION BY Department) AS vs_dept
FROM Employee;   -- impossible with plain GROUP BY without a self-join
```

## How engines execute GROUP BY (why some are slow)

- **Hash aggregation** — build a hash table of groups in memory (the analytics default). Too many distinct groups → **spill to disk** → slow. `GROUP BY customer_id` over 500M customers is a monster; `GROUP BY region` (12 groups) is trivial — *cardinality of the grouping key is the cost driver*.
- **Distributed engines add partial aggregation**: each node pre-aggregates locally, then shuffles only the compact partials — why `groupBy().sum()` in Spark ships tiny data but `groupByKey()`/collect-style patterns ship everything ([shuffle mechanics](../06_PySpark/Spark_Processing.md)).
- Pre-aggregated **summary tables / materialized views** exist precisely to pay a big GROUP BY once instead of per dashboard refresh.

## Aggregates as data-quality instrumentation

Seniors use aggregation reflexively to *test* data, not just report it:

```sql
SELECT load_date,
       COUNT(*)                                    AS row_count,
       COUNT(DISTINCT order_id)                    AS distinct_orders,   -- ≠ row_count → dupes!
       SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) AS negative_amounts,
       MIN(order_ts), MAX(order_ts)                                        -- timezone/late-data smell test
FROM staging.orders
GROUP BY load_date ORDER BY load_date DESC;
```

Trend these per load and alert on deviations — this five-line query catches more pipeline bugs than most test suites.

## Field-tested gotchas

- `AVG` of averages ≠ average: averaging per-store averages weights a 10-sale store equal to a 10,000-sale store — carry `SUM` and `COUNT` separately, divide at the end (this also makes aggregates **re-aggregatable** across levels).
- Integer division: `SUM(a)/SUM(b)` on INT columns truncates in some engines — multiply by `1.0` first.
- `SUM` on FLOAT is order-dependent at scale (parallel plans give slightly different cents per run) — money is DECIMAL, always ([data types](03_SQL_Data_Types.md)).
- `HAVING` without `GROUP BY` is legal (treats the whole table as one group) — occasionally useful, mostly a review flag.
- `GROUP BY 1, 2` (ordinal) breaks silently when someone reorders the SELECT list — name the columns in production code.

## Interview-grade Q&A

- *`COUNT(*)` vs `COUNT(col)`?* All rows vs non-NULL values — the difference *is* the NULL count, itself a useful metric.
- *WHERE vs HAVING?* Row filter before grouping vs group filter after aggregation ([processing order](01_What_is_SQL.md)).
- *Average salary next to each employee — GROUP BY or window?* Window: you need annotation, not collapse.
- *Why is `COUNT(DISTINCT)` expensive and what's the mitigation at scale?* Global uniqueness tracking across nodes; approximate (HLL) counts or pre-deduplicated summary tables.
