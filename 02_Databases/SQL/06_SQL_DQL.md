# SQL DQL (Data Query Language)

## What is DQL?

DQL is the part of SQL used purely to **read** data, without changing anything. It has exactly one command: `SELECT`. Given how often it's used, `SELECT` arguably deserves its own category more than any other keyword in SQL.

---

## The Basic Shape

```sql
SELECT column1, column2
FROM TableName
WHERE condition
ORDER BY column1;
```

Read as a sentence: "get these columns, from this table, only for rows matching this condition, sorted by this column."

---

## SELECT — choosing columns

```sql
-- Every column
SELECT * FROM Employee;

-- Specific columns only
SELECT Name, Salary FROM Employee;
```

Using `*` is convenient while exploring data, but naming specific columns is better practice in real pipelines and reports — it's clearer what's being retrieved, and it keeps working correctly even if someone adds a new column to the table later.

---

## WHERE — filtering rows

```sql
SELECT * FROM Employee
WHERE Department = 'IT';
```

Common comparison operators:

| Operator | Meaning |
|---|---|
| `=` | Equal to |
| `!=` or `<>` | Not equal to |
| `>` , `<` | Greater than, less than |
| `>=` , `<=` | Greater than or equal to, less than or equal to |

Combine conditions with `AND` / `OR`:

```sql
SELECT * FROM Employee
WHERE Department = 'IT' AND Salary > 60000;
```

---

## Handy Filtering Keywords

```sql
-- Matches any of a list of values
SELECT * FROM Employee
WHERE Department IN ('IT', 'HR');

-- Matches a range (inclusive)
SELECT * FROM Employee
WHERE Salary BETWEEN 50000 AND 65000;

-- Pattern matching: % means "any characters"
SELECT * FROM Employee
WHERE Name LIKE 'J%';   -- names starting with J

-- Checking for missing values
SELECT * FROM Employee
WHERE PhoneNumber IS NULL;
```

**A note on NULL**: `NULL` means "no value recorded" — it isn't the same as zero or an empty string. You can never test for it with `= NULL`; you must use `IS NULL` or `IS NOT NULL`. This trips up almost everyone the first time they hit it.

---

## DISTINCT — removing duplicates

```sql
SELECT DISTINCT Department
FROM Employee;
```

Returns each department name once, even if hundreds of employees share it — useful for quickly seeing "what values actually exist in this column."

---

## ORDER BY — sorting results

```sql
SELECT Name, Salary
FROM Employee
ORDER BY Salary DESC;
```

`ASC` (ascending, smallest/earliest first) is the default; `DESC` reverses it (largest/latest first).

---

## Putting it together

```sql
SELECT Name, Department, Salary
FROM Employee
WHERE Department IN ('IT', 'Finance')
  AND Salary > 55000
ORDER BY Salary DESC;
```

"Show me the name, department, and salary of every IT or Finance employee earning more than 55000, sorted highest salary first."

---

## Azure Usage

`SELECT` queries are how analysts and Power BI reports actually pull data out of Azure SQL Database or Azure Synapse Analytics — DQL is the command category end users interact with the most, even if they never touch DDL or DML directly.

---

## Real World Example

A store manager wants to know: "Which products priced over 500, in the Electronics category, are we running low on?" That entire business question translates directly into one `SELECT` statement with a `WHERE` clause combining several conditions, sorted by remaining stock — no other SQL command category is needed just to answer a question.

---
---

# Part 2 — Advanced

## Sargability — writing WHERE clauses indexes can use

A predicate is **sargable** (Search ARGument-able) when the engine can seek an index instead of scanning:

```sql
-- NOT sargable: function wraps the column → every row must be computed
WHERE YEAR(OrderDate) = 2026
WHERE UPPER(Name) = 'PRIYA'
WHERE Salary * 12 > 600000

-- Sargable rewrites: keep the column naked, move math to the constant side
WHERE OrderDate >= '2026-01-01' AND OrderDate < '2027-01-01'
WHERE Name = 'Priya'            -- (or a case-insensitive collation/index)
WHERE Salary > 50000
```

Also non-sargable: leading-wildcard `LIKE '%son'` (no seek possible; `LIKE 'J%'` is fine) and [implicit type conversions](03_SQL_Data_Types.md). This single habit fixes more slow queries than any server setting.

## CASE — logic inside a query

```sql
SELECT Name, Salary,
       CASE
         WHEN Salary >= 65000 THEN 'Senior band'
         WHEN Salary >= 55000 THEN 'Mid band'
         ELSE 'Entry band'
       END AS SalaryBand
FROM Employee;
```

CASE works anywhere an expression works — including inside aggregates (`SUM(CASE WHEN region='East' THEN amount END)` = classic pivot-by-hand) and in `ORDER BY` for custom sort orders.

## Paging and TOP-N properly

```sql
-- T-SQL / standard: skip 20, take 10 (requires ORDER BY)
SELECT Name, Salary FROM Employee
ORDER BY Salary DESC
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

Two pro caveats: **without ORDER BY, row order is undefined** — "it always came back sorted" is an accident of the current plan, not a promise; and OFFSET-based paging re-reads all skipped rows each page (page 10,000 is slow) — keyset paging (`WHERE Salary < @last_seen ...`) scales better.

## Combining result sets

```sql
SELECT Name FROM Current_Employees
UNION       -- deduplicates (sorts/hashes to do so — costs more)
SELECT Name FROM Former_Employees;

-- UNION ALL keeps duplicates — cheaper; DEFAULT choice in pipelines
-- INTERSECT = rows in both; EXCEPT = rows in first but not second
```

`EXCEPT` is an underrated data-quality tool: `SELECT key FROM source EXCEPT SELECT key FROM target` = "what didn't load?"

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Window functions — the biggest DQL power-up

Aggregates that *don't collapse rows*: every row keeps its identity and gains a computed value over a defined "window" of related rows.

```sql
SELECT Name, Department, Salary,
  ROW_NUMBER() OVER (PARTITION BY Department ORDER BY Salary DESC) AS rn,
  SUM(Salary)  OVER (PARTITION BY Department)                      AS dept_total,
  LAG(Salary)  OVER (PARTITION BY Department ORDER BY HireDate)    AS prev_hire_salary
FROM Employee;
```

The patterns you'll use weekly:

- **Top-N per group** — `ROW_NUMBER() ... WHERE rn <= 3` (via subquery/CTE, since WHERE can't see window results — [processing order](01_What_is_SQL.md)).
- **Deduplication** — `ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY updated_at DESC) = 1` keeps the latest version of each key: *the* standard CDC/staging dedupe.
- **Running totals / moving averages** — `SUM(...) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.
- **Gaps & islands, sessionization** — `LAG` + conditional flags + running sums.

`ROW_NUMBER` vs `RANK` vs `DENSE_RANK`: on ties → unique 1,2,3 / 1,1,3 / 1,1,2. Warehouse dialects add `QUALIFY` (filter on window results directly — Databricks/Snowflake) — use it where available.

## Reading an execution plan (the 20% that answers 80%)

`EXPLAIN` (Postgres/Spark) or "Include Actual Plan" (SSMS), then scan for:

1. **Scan vs Seek** on the big table — did your sargable WHERE work?
2. **Estimated vs actual rows** wildly off → stale statistics or optimizer-opaque expressions; every downstream choice (join type, memory grant) is then wrong.
3. **The fattest arrow** — most plans have one dominant data movement; optimize that, ignore the rest.
4. Warnings: implicit conversions, spills to tempdb.

In Spark, same skill: `df.explain()` + the SQL tab ([Spark UI](../../03_Programming/PySpark/Spark_Architecture.md)).

## Field-tested gotchas

- `SELECT *` in production breaks contracts silently (new columns flow downstream), defeats [columnar pruning](../../01_Foundations/Fundamentals/02_OLAP_Storage.md), and inflates network/memory. Exploration only.
- `DISTINCT` slapped on to "fix duplicates" hides a join bug and adds a full sort/hash — find the row multiplication instead ([joins](07_SQL_Keys_and_Joins.md)).
- `WHERE col <> 'x'` **drops NULL rows** (three-valued logic) — add `OR col IS NULL` when you mean "not x, including unknown."
- `ORDER BY` on a billion rows is a full sort — in distributed engines a single-node bottleneck; sort at the smallest possible result, ideally in the BI layer.
- `BETWEEN` on datetimes: `BETWEEN '07-01' AND '07-31'` silently loses July 31's daytime rows — use `>= first AND < next_month`.

## Interview-grade Q&A

- *Get the top 3 earners per department?* `ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)` filtered `<= 3`.
- *Why did the query slow down after wrapping the date in a function?* Non-sargable predicate → index seek became a scan.
- *`UNION` vs `UNION ALL`?* UNION dedupes (extra sort/hash cost); UNION ALL concatenates — default to ALL unless dedup is the intent.
- *A query returns duplicates after adding a join — instinct?* The join hit a one-to-many; fix grain (pre-aggregate or dedupe the many-side), don't mask with DISTINCT.

---

## Further Learning — Docs & Videos

**Documentation**
- SELECT statement (W3Schools): https://www.w3schools.com/sql/sql_select.asp
- Queries (PostgreSQL): https://www.postgresql.org/docs/current/queries.html

**Videos**
- SQL SELECT / WHERE / ORDER BY: https://www.youtube.com/results?search_query=sql+select+where+order+by+group+by
