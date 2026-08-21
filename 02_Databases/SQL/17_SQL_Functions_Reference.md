# SQL Functions Reference — every method, and why you use it

## How to read this file

A **function** (or "method") takes input and returns a value. SQL ships hundreds; you need about sixty. This file lists them by family, and for every one:

| Column | Meaning |
|---|---|
| **Function** | The call, with its arguments |
| **Example → Result** | A concrete input and exactly what comes back |
| **Why you use it** | The real job it does in a pipeline or report |

Examples use **T-SQL** (Azure SQL, Synapse, Fabric) as the default, because that's what this repo targets. A [dialect translation table](#dialect-translation--the-same-job-in-three-engines) at the end maps everything to PostgreSQL and Spark/Databricks.

Where a table is needed, examples use the same **Customers / Orders** data as [SQL by Example](16_SQL_Input_Output_Examples.md).

> **The one idea that connects all of them:** functions on a *column* run **once per row**. That's fine in a `SELECT` list and dangerous in a `WHERE` clause — see [Sargability](#sargability--the-functions-that-secretly-disable-your-indexes) before you write your first `WHERE YEAR(...) = 2026`.

---

## 1. String functions

Data arrives dirty: padded with spaces, in mixed case, with names glued into one column. String functions are the cleaning kit — most of a silver-layer transformation is these.

| Function | Example → Result | Why you use it |
|---|---|---|
| `LEN(s)` | `LEN('Meera  ')` → **5** | Length of a string. **T-SQL ignores trailing spaces** — use `DATALENGTH` for the true byte count |
| `LEFT(s, n)` / `RIGHT(s, n)` | `LEFT('Hyderabad', 3)` → **'Hyd'** | Fixed-width extraction: country codes, prefixes, year from `'2026-01'` |
| `SUBSTRING(s, start, len)` | `SUBSTRING('Hyderabad', 4, 3)` → **'era'** | Pull a slice from the middle. **1-indexed**, not 0 |
| `CHARINDEX(find, s)` | `CHARINDEX('@', 'a@b.com')` → **2** | Locate a delimiter so `SUBSTRING` knows where to cut. Returns **0** if not found |
| `CONCAT(a, b, …)` | `CONCAT('Meera', NULL, ' K')` → **'Meera K'** | Join values. **Treats NULL as empty** — unlike `+`, which returns NULL if any part is NULL |
| `CONCAT_WS(sep, a, b, …)` | `CONCAT_WS('-', 'IN', NULL, 'HYD')` → **'IN-HYD'** | Join with a separator, skipping NULLs. Building keys and file paths |
| `UPPER(s)` / `LOWER(s)` | `UPPER('meera')` → **'MEERA'** | Normalize case before comparing or joining — `'Meera'` and `'meera'` are different keys |
| `TRIM(s)` | `TRIM('  Meera  ')` → **'Meera'** | Strip whitespace. **The #1 cause of joins that silently match nothing** — `'Meera '` ≠ `'Meera'` |
| `LTRIM(s)` / `RTRIM(s)` | `RTRIM('Meera  ')` → **'Meera'** | One-sided trim (and the only option before SQL Server 2017) |
| `REPLACE(s, find, sub)` | `REPLACE('a-b-c', '-', '')` → **'abc'** | Strip or swap characters: removing thousands separators, currency symbols, hyphens from IDs |
| `REVERSE(s)` | `REVERSE('abc')` → **'cba'** | Mostly for extracting *after the last* delimiter (reverse, find first, reverse back) |
| `REPLICATE(s, n)` | `REPLICATE('0', 3)` → **'000'** | Zero-padding codes to a fixed width |
| `STUFF(s, start, len, sub)` | `STUFF('abcdef', 2, 3, 'XY')` → **'aXYef'** | Delete-and-insert in one call. Masking, and the classic comma-trim idiom |
| `STRING_AGG(col, sep)` | `STRING_AGG(Name, ', ')` → **'Meera, Raj'** | **Collapse many rows into one string** — "list every product in this order" in a single cell |
| `STRING_SPLIT(s, sep)` | `STRING_SPLIT('a,b', ',')` → 2 rows: `a`, `b` | The inverse — explode a delimited field into rows. Cleaning CSV-in-a-column |
| `FORMAT(v, fmt)` | `FORMAT(1234.5, 'N2')` → **'1,234.50'** | Culture-aware display formatting. **Slow — avoid on large result sets**; format in the BI tool instead |
| `PATINDEX('%pat%', s)` | `PATINDEX('%[0-9]%', 'ab3')` → **3** | Pattern search with wildcards, where `CHARINDEX` only does literals |

**Worked example — splitting a full name:**

```sql
SELECT FullName,
       LEFT(FullName, CHARINDEX(' ', FullName) - 1)  AS first_name,
       SUBSTRING(FullName, CHARINDEX(' ', FullName) + 1, LEN(FullName)) AS last_name
FROM (VALUES ('Meera Kumar'), ('Raj Patel')) AS t(FullName);
```

| FullName | first_name | last_name |
|---|---|---|
| Meera Kumar | Meera | Kumar |
| Raj Patel | Raj | Patel |

> **This breaks on a name with no space** — `CHARINDEX` returns 0, so `LEFT(s, -1)` errors. Real ingestion code guards it: `CASE WHEN CHARINDEX(' ', FullName) > 0 THEN … ELSE FullName END`. Assuming every string has your delimiter is the most common cause of a failed nightly load.

---

## 2. Date and time functions

Dates are where pipelines break: time zones, month boundaries, and "elapsed time" that isn't. Nearly every fact table is partitioned or filtered by a date, so these run constantly.

| Function | Example → Result | Why you use it |
|---|---|---|
| `GETDATE()` | → **2026-08-21 14:30:00** | Current **server local** time. Avoid in pipelines — server time zone is an environment dependency |
| `SYSUTCDATETIME()` | → **2026-08-21 09:00:00.1234567** | Current **UTC**, high precision. **Use this** for audit columns and watermarks |
| `CURRENT_TIMESTAMP` | → **2026-08-21 14:30:00** | ANSI-standard alias for `GETDATE()` — portable across engines |
| `DATEADD(part, n, d)` | `DATEADD(day, -7, '2026-08-21')` → **2026-08-14** | Shift a date. Rolling windows, retention cutoffs, SCD2 expiry dates |
| `DATEDIFF(part, a, b)` | `DATEDIFF(day, '2026-01-01', '2026-01-10')` → **9** | Elapsed intervals: order-to-ship time, customer age, SLA breach checks |
| `DATEPART(part, d)` | `DATEPART(quarter, '2026-08-21')` → **3** | Extract any component — quarter, week, day-of-year — for grouping |
| `YEAR(d)` / `MONTH(d)` / `DAY(d)` | `MONTH('2026-08-21')` → **8** | Shorthand for the three most common `DATEPART` calls |
| `EOMONTH(d)` | `EOMONTH('2026-02-10')` → **2026-02-28** | Last day of the month — **handles leap years for you**. Month-end reporting boundaries |
| `DATETRUNC(part, d)` | `DATETRUNC(month, '2026-08-21')` → **2026-08-01** | Snap to period start. The clean way to bucket by month (2022+; `DATE_TRUNC` elsewhere) |
| `CAST(d AS DATE)` | `CAST('2026-08-21 14:30' AS DATE)` → **2026-08-21** | Strip the time component so day-level grouping actually groups |
| `AT TIME ZONE` | `… AT TIME ZONE 'India Standard Time'` | Convert between zones with DST handled correctly |
| `ISDATE(s)` | `ISDATE('2026-13-01')` → **0** | Validate before converting — pair with `TRY_CAST` for dirty ingestion |

### The `DATEDIFF` trap — it counts boundaries, not elapsed time

```sql
SELECT DATEDIFF(year, '2025-12-31', '2026-01-01');   -- returns 1
```

Those dates are **one day apart**, but `DATEDIFF(year, …)` returns **1**, because it counts how many year boundaries were crossed — not how many years elapsed.

```text
   DATEDIFF(part, a, b) = number of PART boundaries crossed between a and b

   '2025-12-31' -> '2026-01-01'
        one year boundary crossed  ->  DATEDIFF(year, ...) = 1
        one month boundary crossed ->  DATEDIFF(month, ...) = 1
        one day boundary crossed   ->  DATEDIFF(day, ...) = 1

   ... all from a 24-hour gap.
```

**Why it matters:** computing someone's age as `DATEDIFF(year, DOB, GETDATE())` makes them a year older on 1 January instead of on their birthday. For true elapsed periods, difference in the smallest unit and divide, or compare the dates directly.

### The time zone rule

```text
   BAD:   store local time, no offset
          -> "was that 9am in Mumbai or 9am in London?"
          -> DST shifts make one hour a year ambiguous and another nonexistent

   GOOD:  store UTC (DATETIME2 / TIMESTAMP), convert only for display
          -> one unambiguous timeline; every join and comparison is correct
```

Use `SYSUTCDATETIME()` for audit columns, keep every timestamp in UTC through bronze and silver, and convert to local only in the presentation layer.

---

## 3. Numeric and math functions

| Function | Example → Result | Why you use it |
|---|---|---|
| `ROUND(n, d)` | `ROUND(1234.567, 2)` → **1234.570** | Round to d decimals. Financial presentation, tolerance comparisons |
| `ROUND(n, d, 1)` | `ROUND(1234.567, 2, 1)` → **1234.560** | Non-zero third argument **truncates** instead of rounding |
| `CEILING(n)` / `FLOOR(n)` | `CEILING(4.1)` → **5** | Round up/down always. Batch counts: "how many pages of 100 rows?" |
| `ABS(n)` | `ABS(-42)` → **42** | Magnitude regardless of sign — reconciliation tolerances, drift checks |
| `SIGN(n)` | `SIGN(-42)` → **-1** | Direction only: -1, 0, or 1. Bucketing gains vs losses |
| `POWER(n, p)` / `SQRT(n)` | `POWER(2, 10)` → **1024** | Growth calculations, distance and statistical formulas |
| `%` (modulo) | `10 % 3` → **1** | Remainder. Bucketing by hash, alternating rows, "every Nth record" sampling |
| `RAND()` | → **0.4207…** | Random float. **Non-deterministic** — never in a computed column or indexed view |
| `NEWID()` | → a GUID | Unique identifiers; `ORDER BY NEWID()` shuffles rows for sampling |

### The integer division trap

```sql
SELECT 5 / 2;                      -- 2      <- NOT 2.5
SELECT 5.0 / 2;                    -- 2.5
SELECT CAST(5 AS DECIMAL(10,2)) / 2;  -- 2.500000
```

**Why:** when both operands are integers, SQL performs **integer division** and discards the remainder. It doesn't warn.

**Where it bites:** percentage calculations. `SELECT shipped_count / total_count * 100` returns **0** for any ratio below 1 — a completion-rate dashboard permanently reading 0%. Fix by making one side decimal:

```sql
SELECT shipped_count * 100.0 / total_count AS pct;   -- 100.0 forces decimal maths
```

---

## 4. NULL-handling functions

NULL is not a value — it's the *absence* of one, and it propagates through everything it touches ([worked examples](16_SQL_Input_Output_Examples.md#3-where-meets-null--the-row-that-fails-both-tests)). These four functions are how you take control of it.

| Function | Example → Result | Why you use it |
|---|---|---|
| `ISNULL(a, b)` | `ISNULL(NULL, 0)` → **0** | Substitute a default. T-SQL only, exactly **2 arguments** |
| `COALESCE(a, b, c, …)` | `COALESCE(NULL, NULL, 'X')` → **'X'** | First non-NULL from **any number** of arguments. ANSI standard — **prefer this** |
| `NULLIF(a, b)` | `NULLIF(0, 0)` → **NULL** | Turn a specific value *into* NULL. The divide-by-zero guard |
| `IS NULL` / `IS NOT NULL` | `WHERE Amount IS NULL` | The **only** way to test for NULL. `= NULL` is always unknown |

### The three jobs they do

**1. Supply a default so arithmetic works:**

```sql
SELECT AVG(COALESCE(Amount, 0)) FROM Orders;   -- 1350, counting missing as zero
SELECT AVG(Amount) FROM Orders;                -- 1620, ignoring missing entirely
```

Both are correct — for different questions. Choosing is a business decision, not a technical one.

**2. Prevent divide-by-zero without a `CASE`:**

```sql
SELECT Amount / NULLIF(OrderCount, 0) AS avg_per_order FROM …;
```

If `OrderCount` is 0, `NULLIF` makes it NULL, and dividing by NULL yields NULL instead of crashing. A NULL in a report is honest; a failed query at 3am is not.

**3. Fall back through a priority chain:**

```sql
SELECT COALESCE(preferred_name, legal_name, email, 'Unknown') AS display_name FROM …;
```

Reads top to bottom and stops at the first non-NULL — a whole `CASE` block in one call.

### `ISNULL` vs `COALESCE`

| | `ISNULL` | `COALESCE` |
|---|---|---|
| Standard | T-SQL only | **ANSI** — works everywhere |
| Arguments | Exactly 2 | Any number |
| Result data type | Takes the **first** argument's type | Takes the **highest-precedence** type |
| Evaluation | Once | The expression may be **evaluated twice** |

That data type row causes real bugs:

```sql
SELECT ISNULL(CAST(NULL AS VARCHAR(3)), 'Hyderabad');   -- 'Hyd'  <- silently TRUNCATED
SELECT COALESCE(CAST(NULL AS VARCHAR(3)), 'Hyderabad'); -- 'Hyderabad'
```

`ISNULL` forced the result into `VARCHAR(3)` from the first argument. **Default to `COALESCE`.**

---

## 5. Conversion functions

Every ingestion pipeline converts types — text files have no types, so everything arrives as a string.

| Function | Example → Result | Why you use it |
|---|---|---|
| `CAST(v AS type)` | `CAST('123' AS INT)` → **123** | ANSI standard conversion. **Portable — prefer it** |
| `CONVERT(type, v, style)` | `CONVERT(VARCHAR, d, 23)` → **'2026-08-21'** | T-SQL only, but has **style codes** for date formatting |
| `TRY_CAST(v AS type)` | `TRY_CAST('abc' AS INT)` → **NULL** | Returns NULL instead of **erroring** on bad input |
| `TRY_CONVERT(type, v)` | `TRY_CONVERT(DATE, '2026-13-01')` → **NULL** | Same safety, with style codes |
| `PARSE` / `TRY_PARSE` | `TRY_PARSE('21/08/2026' AS DATE USING 'en-GB')` | Culture-aware parsing. Slow (CLR) — only for genuinely locale-specific input |

### Why `TRY_CAST` is the ingestion workhorse

```sql
-- CAST: one bad row kills the entire batch
SELECT CAST(Amount_Text AS DECIMAL(10,2)) FROM staging.RawOrders;
-- Msg 8114: Error converting data type varchar to numeric.
-- ...which row? It doesn't say. 2 million rows, one is bad.

-- TRY_CAST: bad rows become NULL, and you can find them
SELECT OrderID, Amount_Text,
       TRY_CAST(Amount_Text AS DECIMAL(10,2)) AS Amount_Clean
FROM staging.RawOrders
WHERE TRY_CAST(Amount_Text AS DECIMAL(10,2)) IS NULL   -- quarantine the failures
  AND Amount_Text IS NOT NULL;
```

| OrderID | Amount_Text | Amount_Clean |
|---|---|---|
| 5011 | `'1,200.00'` | *NULL* ← comma isn't valid in a decimal |
| 5012 | `'N/A'` | *NULL* ← placeholder text |
| 5013 | `'  900 '` | 900.00 ← whitespace is tolerated |

**Why this pattern matters:** it turns a **hard failure** into a **data quality measurement**. The good rows load, the bad rows land in a quarantine table with their original text, and someone can fix the source. That's the difference between a pipeline that fails and a pipeline that reports.

### Implicit conversion — the silent index killer

```sql
-- CustomerID is INT, but the parameter is passed as a string
WHERE CustomerID = '123'
```

SQL converts one side automatically. When it converts the **column** rather than the literal, the index on that column becomes unusable and you get a scan instead of a seek. Match your types deliberately — see below.

---

## 6. Conditional functions

| Function | Example → Result | Why you use it |
|---|---|---|
| `CASE WHEN … THEN … ELSE … END` | see below | The universal conditional. **ANSI, works everywhere** |
| `IIF(cond, a, b)` | `IIF(1 > 2, 'Y', 'N')` → **'N'** | T-SQL shorthand for a two-branch `CASE` |
| `CHOOSE(n, a, b, c)` | `CHOOSE(2, 'Lo', 'Mid', 'Hi')` → **'Mid'** | Pick the nth item — mapping small integer codes to labels |
| `GREATEST(a,b,…)` / `LEAST(…)` | `GREATEST(3, 9, 5)` → **9** | Max/min **across columns in one row** (aggregates go down columns, these go across) |

**Two `CASE` forms:**

```sql
-- Searched CASE: any condition, including ranges and IS NULL
CASE WHEN Amount IS NULL THEN 'Unknown'
     WHEN Amount >= 2000 THEN 'Large'
     ELSE 'Small' END

-- Simple CASE: equality against one expression only
CASE Status WHEN 'Shipped'   THEN 1
            WHEN 'Pending'   THEN 2
            ELSE 99 END
```

**Why `CASE` earns its keep in data engineering:** conditional aggregation — pivoting without `PIVOT`.

```sql
SELECT
    SUM(CASE WHEN Status = 'Shipped'   THEN Amount ELSE 0 END) AS shipped_revenue,
    SUM(CASE WHEN Status = 'Pending'   THEN Amount ELSE 0 END) AS pending_revenue,
    COUNT(CASE WHEN Status = 'Cancelled' THEN 1 END)           AS cancelled_count
FROM Orders;
```

| shipped_revenue | pending_revenue | cancelled_count |
|---|---|---|
| 4200 | 3000 | 1 |

One pass over the table produces three differently-filtered measures. The alternative — three separate queries joined together — reads the table three times.

> Note `COUNT(CASE WHEN … THEN 1 END)` with **no `ELSE`**: unmatched rows become NULL, and `COUNT` skips NULLs. Adding `ELSE 0` would count every row instead — a classic off-by-everything bug.

---

## 7. Aggregate functions

Functions that collapse many rows into one value. Full treatment in [SQL Aggregate Functions](08_SQL_Aggregate_Functions.md).

| Function | Example → Result | Why you use it |
|---|---|---|
| `COUNT(*)` | → **6** | Counts **rows**, including those with NULLs |
| `COUNT(col)` | `COUNT(Amount)` → **5** | Counts **non-NULL values** — the difference reveals missing data |
| `COUNT(DISTINCT col)` | `COUNT(DISTINCT CustomerID)` → **3** | Cardinality: unique customers, distinct products |
| `SUM(col)` | `SUM(Amount)` → **8100** | Totals. Skips NULLs |
| `AVG(col)` | `AVG(Amount)` → **1620** | Mean — divides by `COUNT(col)`, **not** `COUNT(*)` |
| `MIN` / `MAX` | `MAX(Amount)` → **3000** | Extremes; also works on dates and strings (first/last alphabetically) |
| `STDEV` / `VAR` | | Spread — outlier detection and data-quality thresholds |
| `STRING_AGG(col, sep)` | → **'Meera, Raj'** | Concatenate a group into one string |

> **The instrumentation trick:** `COUNT(*) - COUNT(col)` gives the exact number of NULLs in a column. One expression, and it's the basis of most automated completeness tests.

---

## 8. Window functions

Same functions, but they **annotate rows instead of collapsing them**. Full treatment in [SQL Window Functions](14_SQL_Window_Functions.md).

| Function | Why you use it |
|---|---|
| `ROW_NUMBER()` | Deduplication — keep exactly one row per key |
| `RANK()` / `DENSE_RANK()` | Competition ranking, with and without gaps after ties |
| `NTILE(n)` | Quartiles, deciles, splitting work into even batches |
| `LAG()` / `LEAD()` | Previous/next row — period-over-period change, detecting status transitions |
| `FIRST_VALUE()` / `LAST_VALUE()` | First/last in a partition — opening and closing values |
| `SUM() OVER (…)` | Running totals, percent-of-total, group total on every row |

---

## 9. JSON functions

Every API extract and event stream lands as JSON. These read it without leaving SQL.

| Function | Example → Result | Why you use it |
|---|---|---|
| `JSON_VALUE(json, path)` | `JSON_VALUE('{"city":"Pune"}', '$.city')` → **'Pune'** | Extract one **scalar** value |
| `JSON_QUERY(json, path)` | Returns an object or array | Extract a nested **object/array** (`JSON_VALUE` returns NULL for these) |
| `OPENJSON(json)` | Returns a rowset | **Shred an array into rows** — the JSON equivalent of unnesting |
| `ISJSON(s)` | `ISJSON('{bad')` → **0** | Validate before parsing, so malformed payloads quarantine instead of erroring |
| `FOR JSON PATH` | Result set → JSON string | The reverse: serialize a query result for an API response |

```sql
SELECT JSON_VALUE(payload, '$.customer.city')  AS city,
       JSON_VALUE(payload, '$.order.amount')   AS amount
FROM staging.RawEvents
WHERE ISJSON(payload) = 1;                     -- skip malformed rows, don't crash
```

> **The trade-off:** parsing JSON on every read is slow and can't use ordinary indexes. Extract the fields you filter on into real typed columns during the bronze→silver step, and keep the raw JSON alongside for replay. Parse once on write, not on every read.

---

## 10. System and metadata functions

| Function | Returns | Why you use it |
|---|---|---|
| `@@ROWCOUNT` | Rows affected by the last statement | Logging load counts, detecting a no-op run |
| `SCOPE_IDENTITY()` | Last identity value **in this scope** | Retrieve a generated key. Safer than `@@IDENTITY`, which sees trigger inserts |
| `SUSER_SNAME()` | Current login | Audit columns — who changed this row |
| `DB_NAME()` / `OBJECT_NAME(id)` | Database / object name | Dynamic and metadata-driven pipelines |
| `@@VERSION` | Engine version string | Confirming which feature set is available |
| `SYSTEM_USER` | Current security context | ANSI-standard alternative to `SUSER_SNAME()` |

---

## Sargability — the functions that secretly disable your indexes

**Sargable** = "Search ARGument able" = the engine can use an index **seek** rather than scanning the whole table. Wrapping an indexed column in a function destroys that.

```sql
-- NOT sargable: the function must run on EVERY row before the comparison,
-- so the index on OrderDate cannot be seeked
WHERE YEAR(OrderDate) = 2026

-- Sargable: the column is left bare; the index seeks a contiguous range
WHERE OrderDate >= '2026-01-01' AND OrderDate < '2027-01-01'
```

```text
   NOT sargable
   ------------
   for each of 50,000,000 rows:  compute YEAR(OrderDate), compare to 2026
   -> full index/table scan, 50M function calls

   Sargable
   --------
   navigate the index to '2026-01-01', read forward until '2027-01-01'
   -> seek + range read, touches only matching rows
```

Same result. Orders of magnitude apart.

**The pattern repeats everywhere:**

| Don't | Do |
|---|---|
| `WHERE YEAR(OrderDate) = 2026` | `WHERE OrderDate >= '2026-01-01' AND OrderDate < '2027-01-01'` |
| `WHERE UPPER(Name) = 'MEERA'` | Use a case-insensitive collation, or store a normalized column |
| `WHERE LEFT(Code, 3) = 'ABC'` | `WHERE Code LIKE 'ABC%'` (a leading-wildcard `'%ABC'` is **not** sargable) |
| `WHERE Amount * 1.1 > 1000` | `WHERE Amount > 1000 / 1.1` — move the maths to the literal side |
| `WHERE CAST(CustomerID AS VARCHAR) = '123'` | `WHERE CustomerID = 123` — match the column's type |

**The rule:** keep the **column bare** on one side of the comparison and put every function, cast, and calculation on the **literal** side. A function on a literal runs once; a function on a column runs once per row.

> If you genuinely need to filter on a derived value, materialize it: a **persisted computed column** (`ALTER TABLE … ADD OrderYear AS YEAR(OrderDate) PERSISTED`) can itself be indexed, giving you sargability on the expression.

---

## Deterministic vs non-deterministic

A function is **deterministic** if the same input always yields the same output.

| Deterministic | Non-deterministic |
|---|---|
| `LEN`, `SUBSTRING`, `ABS`, `ROUND`, `DATEADD`, `DATEDIFF`, `CAST` | `GETDATE()`, `SYSUTCDATETIME()`, `RAND()`, `NEWID()`, `@@ROWCOUNT` |

**Why it matters:**

- **Indexed views and persisted computed columns require deterministic functions.** `AS YEAR(OrderDate) PERSISTED` is allowed; `AS DATEDIFF(year, DOB, GETDATE()) PERSISTED` is rejected — the value would silently go stale.
- **Reproducible pipelines.** A transformation using `GETDATE()` produces different output on a rerun, so a backfill won't match the original load. Pass the logical run date **in as a parameter** instead — that's what makes a backfill reproducible.

```sql
-- Not reproducible: depends on when it runs
WHERE OrderDate >= DATEADD(day, -7, GETDATE())

-- Reproducible: same @RunDate always yields the same rows
WHERE OrderDate >= DATEADD(day, -7, @RunDate)
```

---

## Dialect translation — the same job in three engines

An Azure data engineer writes T-SQL in Synapse and Spark SQL in Databricks in the same afternoon. These are the differences that actually catch you out.

| Job | SQL Server / Synapse | PostgreSQL | Spark / Databricks |
|---|---|---|---|
| String length | `LEN(s)` | `LENGTH(s)` | `LENGTH(s)` |
| Concatenate | `CONCAT(a,b)` or `a + b` | `CONCAT(a,b)` or `a \|\| b` | `CONCAT(a,b)` |
| Substring | `SUBSTRING(s,1,3)` | `SUBSTRING(s FROM 1 FOR 3)` | `SUBSTRING(s,1,3)` |
| Find position | `CHARINDEX(find, s)` | `POSITION(find IN s)` | `INSTR(s, find)` |
| NULL default | `ISNULL(a,b)` / `COALESCE` | `COALESCE(a,b)` | `COALESCE(a,b)` / `NVL` |
| Current UTC | `SYSUTCDATETIME()` | `NOW() AT TIME ZONE 'UTC'` | `CURRENT_TIMESTAMP()` |
| Add days | `DATEADD(day, 7, d)` | `d + INTERVAL '7 days'` | `DATE_ADD(d, 7)` |
| Date difference | `DATEDIFF(day, a, b)` | `b - a` (integer days) | `DATEDIFF(b, a)` ← **args reversed!** |
| Truncate to month | `DATETRUNC(month, d)` | `DATE_TRUNC('month', d)` | `DATE_TRUNC('MONTH', d)` |
| Safe cast | `TRY_CAST(v AS INT)` | `v::INT` (throws) | `TRY_CAST(v AS INT)` |
| Aggregate strings | `STRING_AGG(c, ',')` | `STRING_AGG(c, ',')` | `CONCAT_WS(',', COLLECT_LIST(c))` |
| Filter on a window fn | subquery / CTE | subquery / CTE | **`QUALIFY`** |
| Top N | `SELECT TOP 5` | `LIMIT 5` | `LIMIT 5` |

> **The single worst trap in that table:** `DATEDIFF` takes `(part, start, end)` in T-SQL but `(end, start)` in Spark. The same expression compiles in both and returns values of the **opposite sign**. Nothing errors — the numbers are just wrong.

---

## Field-tested gotchas

- **`LEN` ignores trailing spaces** in T-SQL — `LEN('a   ')` is 1. Use `DATALENGTH` when the padding matters.
- **`+` propagates NULL, `CONCAT` doesn't.** `'Hello ' + NULL` is NULL; `CONCAT('Hello ', NULL)` is `'Hello '`. Silent blank fields usually trace back to this.
- **Integer division truncates without warning.** `count_a / count_b * 100` returns 0 for every ratio under 1.
- **`DATEDIFF` counts boundaries, not elapsed time** — one day can be "one year."
- **`ISNULL` truncates to the first argument's type.** Use `COALESCE`.
- **`FORMAT` and `PARSE` are CLR-based and slow** — measurably so over millions of rows. Format in the presentation layer.
- **`COUNT(CASE WHEN … THEN 1 END)` needs no `ELSE`** — adding `ELSE 0` counts every row instead of the matching ones.
- **Functions on indexed columns in `WHERE` kill seeks.** The most common real-world cause of a query that "suddenly got slow" after a small edit.
- **`ORDER BY NEWID()` sorts the entire table** to shuffle it — fine for 10k rows, catastrophic for 10M. Use `TABLESAMPLE` for large-scale sampling.
- **Implicit conversion is invisible in the query text** but appears in the execution plan as `CONVERT_IMPLICIT` — worth knowing when you read a plan ([DQL](06_SQL_DQL.md)).

---

## Interview-grade Q&A

- *`ISNULL` vs `COALESCE`?* `COALESCE` is ANSI, takes any number of arguments, and resolves to the highest-precedence data type; `ISNULL` is T-SQL, takes exactly two, and adopts the **first** argument's type — which can silently truncate. Prefer `COALESCE`.
- *`CAST` vs `CONVERT` vs `TRY_CAST`?* `CAST` is ANSI-portable; `CONVERT` is T-SQL with style codes for date formatting; `TRY_CAST` returns NULL instead of erroring, which is what you want for ingestion so one bad row doesn't fail the batch.
- *Why is `WHERE YEAR(OrderDate) = 2026` slow?* It's not sargable — the function runs per row, so the index can't be seeked. Rewrite as a date range on the bare column.
- *How do you avoid divide-by-zero?* `NULLIF(denominator, 0)` — the division yields NULL instead of an error.
- *What's the difference between `COUNT(*)` and `COUNT(col)`?* `COUNT(*)` counts rows; `COUNT(col)` counts non-NULL values. Their difference is the NULL count in that column.
- *How would you pivot without `PIVOT`?* Conditional aggregation: `SUM(CASE WHEN cond THEN val ELSE 0 END)` per output column — one table pass instead of several.
- *Why avoid `GETDATE()` inside a transformation?* It's non-deterministic, so reruns and backfills produce different results. Pass the logical run date as a parameter.
- *You need the first non-null of five columns — what do you use?* `COALESCE` with all five, in priority order.
- *How do you handle a bad value in a numeric column during ingestion?* `TRY_CAST` to NULL, then quarantine rows where the cast returned NULL but the source text wasn't NULL — converting a hard failure into a measurable data-quality metric.

---

## Further Learning — Docs & Videos

**Documentation**
- Built-in functions (T-SQL): https://learn.microsoft.com/en-us/sql/t-sql/functions/functions
- String functions (PostgreSQL): https://www.postgresql.org/docs/current/functions-string.html
- Built-in functions (Spark SQL): https://spark.apache.org/docs/latest/api/sql/
- Sargability and index usage: https://learn.microsoft.com/en-us/sql/relational-databases/performance/

**Videos**
- SQL string and date functions explained: https://www.youtube.com/results?search_query=sql+string+and+date+functions+explained
- Sargable queries and index seeks vs scans: https://www.youtube.com/results?search_query=sargable+sql+index+seek+vs+scan
