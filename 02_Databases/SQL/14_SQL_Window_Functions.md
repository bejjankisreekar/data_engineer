# SQL Window Functions

> Looking for the full catalogue of non-window functions (string, date, numeric, NULL, conversion)? See [SQL Functions Reference](17_SQL_Functions_Reference.md).

## Why this file exists

[Aggregate functions](08_SQL_Aggregate_Functions.md) answer "what's the total per region?" — but they **destroy the detail rows** to do it. [Joins](07_SQL_Keys_and_Joins.md) connect tables sideways. Neither can answer the questions data engineers get asked every day:

- "Show each sale **and** what percentage of its region's total it represents."
- "Keep only the **latest** row per customer from this staging load."
- "What was each rep's **previous** sale, and how much did they grow?"
- "Give me the **top 3** performers in every region — not overall."

All four need the same thing: a calculation over a *group* of rows, reported **on every row**, without collapsing anything. That's a **window function**.

Analogy: a `GROUP BY` report is a summary sheet — the 500 individual rows go in, one row per region comes out, and the detail is gone. A window function is a spreadsheet where you add a column: every original row stays exactly where it is, and each one gets a new cell computed by looking at its neighbours.

---

## The sample data

Every example below uses this one table.

**Sales**

| SaleID | Region | SalesRep | SaleDate | Amount |
|---|---|---|---|---|
| 1 | East | Meera | 2026-01-05 | 500 |
| 2 | East | Raj | 2026-01-12 | 700 |
| 3 | East | Anita | 2026-02-03 | 700 |
| 4 | West | Vikram | 2026-01-08 | 300 |
| 5 | West | Priya | 2026-02-11 | 900 |
| 6 | West | Sam | 2026-03-02 | 400 |

Two things were made deliberately awkward, because they're what break real queries:

- **East has a tie** — Raj and Anita both sold 700. Ties are where `RANK`, `DENSE_RANK`, and frame defaults quietly disagree with each other.
- **Region totals differ** — East 1900, West 1600. Grand total 3500.

---

## GROUP BY vs window function — collapse or annotate?

This is the whole idea, in one comparison.

**GROUP BY collapses:**

```sql
SELECT Region, SUM(Amount) AS region_total
FROM Sales
GROUP BY Region;
```

| Region | region_total |
|---|---|
| East | 1900 |
| West | 1600 |

Six rows went in. **Two came out.** `SalesRep`, `SaleDate`, and every individual `Amount` are gone — you cannot ask for them, because they no longer exist in the result.

**A window function annotates:**

```sql
SELECT Region, SalesRep, Amount,
       SUM(Amount) OVER (PARTITION BY Region) AS region_total
FROM Sales;
```

| Region | SalesRep | Amount | region_total |
|---|---|---|---|
| East | Meera | 500 | 1900 |
| East | Raj | 700 | 1900 |
| East | Anita | 700 | 1900 |
| West | Vikram | 300 | 1600 |
| West | Priya | 900 | 1600 |
| West | Sam | 400 | 1600 |

Six rows went in. **Six came out.** Every row kept its identity *and* gained its region's total. Now `Amount * 100.0 / region_total` is one more column away — a calculation that needs a self-join or a subquery without window functions.

> **The rule of thumb:** if the answer needs both the detail *and* a summary of that detail in the same row, you need a window function. `GROUP BY` can never do it, because it has already thrown the detail away.

---

## Anatomy of the `OVER` clause

Every window function is `function() OVER (...)`. The `OVER` clause has exactly three optional parts, and they always mean the same thing:

```text
   SUM(Amount)  OVER ( PARTITION BY Region  ORDER BY SaleDate  ROWS BETWEEN ... )
   -----------         ------------------   -----------------  ----------------
        |                      |                    |                  |
        |                      |                    |                  +-- 3. FRAME:
        |                      |                    |                      which rows inside the
        |                      |                    |                      partition count RIGHT NOW
        |                      |                    |
        |                      |                    +-- 2. ORDER BY:
        |                      |                        the order within each partition
        |                      |                        (required for ranking + running totals)
        |                      |
        |                      +-- 1. PARTITION BY:
        |                          split rows into independent groups
        |                          (leave it out = one window over the whole result)
        |
        +-- the function itself: SUM, ROW_NUMBER, LAG, ...
```

| Part | If you include it | If you leave it out |
|---|---|---|
| `PARTITION BY` | Calculation restarts for each group | The whole result set is one single window |
| `ORDER BY` | Rows are ranked/accumulated in that order | No order — the function sees the entire partition at once |
| frame (`ROWS`/`RANGE`) | You control exactly which neighbouring rows count | A **default frame** is applied — and the default changes depending on whether `ORDER BY` is present (see [Frames](#frames-the-part-everyone-skips-and-then-debugs)) |

---

## How a window function actually computes

Same approach as the [join matching grid](07_SQL_Keys_and_Joins.md#first-how-a-join-actually-matches-rows) — here's the mechanism, step by step, for `SUM(Amount) OVER (PARTITION BY Region ORDER BY SaleDate)`.

**Step 1 — partition.** Split the rows into independent groups. Nothing crosses a partition boundary, ever:

```text
   ALL 6 ROWS
        |
        +---- PARTITION "East" ----+       +---- PARTITION "West" ----+
        |  Meera   01-05    500    |       |  Vikram  01-08    300    |
        |  Raj     01-12    700    |       |  Priya   02-11    900    |
        |  Anita   02-03    700    |       |  Sam     03-02    400    |
        +--------------------------+       +--------------------------+
```

**Step 2 — order within each partition.** East is already in date order; West likewise.

**Step 3 — for each row, build its frame and compute.** The default frame here is "everything from the start of the partition through the current row":

```text
   PARTITION "East"                     frame for this row          SUM
   ---------------------------------------------------------------------
   Meera   01-05   500     [ Meera ]                                 500
   Raj     01-12   700     [ Meera, Raj ]                           1200
   Anita   02-03   700     [ Meera, Raj, Anita ]                    1900
                             ^ the frame grows one row at a time
                               -- that is what makes it a "running" total

   PARTITION "West"
   ---------------------------------------------------------------------
   Vikram  01-08   300     [ Vikram ]                                300
   Priya   02-11   900     [ Vikram, Priya ]                        1200
   Sam     03-02   400     [ Vikram, Priya, Sam ]                   1600
```

**The result**

| Region | SalesRep | SaleDate | Amount | running_total |
|---|---|---|---|---|
| East | Meera | 2026-01-05 | 500 | 500 |
| East | Raj | 2026-01-12 | 700 | 1200 |
| East | Anita | 2026-02-03 | 700 | 1900 |
| West | Vikram | 2026-01-08 | 300 | 300 |
| West | Priya | 2026-02-11 | 900 | 1200 |
| West | Sam | 2026-03-02 | 400 | 1600 |

Notice West restarts at 300 rather than continuing from 1900. **That's `PARTITION BY` doing its job** — and forgetting it is the single most common window-function bug, because the query still runs and still returns the right number of rows. It just accumulates across groups that should have been independent.

---

## The three families of window function

Every window function belongs to one of three groups. Learn the families, not the list.

| Family | What it does | Members |
|---|---|---|
| **1. Ranking** | Assigns a position within the partition | `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `CUME_DIST` |
| **2. Aggregate** | Any normal aggregate, used with `OVER` | `SUM`, `AVG`, `COUNT`, `MIN`, `MAX`, `STDDEV`, … |
| **3. Offset / value** | Reaches out to another row in the partition | `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE` |

---

## Family 1 — Ranking functions

All six are computed the same way: order the partition, then number the rows. They differ **only in how they treat ties** — which is exactly what interviewers ask about, and exactly what silently corrupts a "top N" report.

### `ROW_NUMBER`, `RANK`, `DENSE_RANK` — the tie question

Order East by `Amount DESC`. Raj and Anita are tied at 700.

```text
   PARTITION "East", ORDER BY Amount DESC

   SalesRep   Amount    ROW_NUMBER   RANK   DENSE_RANK
   ------------------------------------------------------
   Raj          700         1          1         1
   Anita        700         2          1         1     <-- tied with Raj
   Meera        500         3          3         2
                            ^          ^         ^
                            |          |         +-- no gap: next distinct value is 2
                            |          +-- gap: skips 2 because two rows took position 1
                            +-- always unique, ties broken arbitrarily
```

```sql
SELECT Region, SalesRep, Amount,
       ROW_NUMBER() OVER (PARTITION BY Region ORDER BY Amount DESC) AS rn,
       RANK()       OVER (PARTITION BY Region ORDER BY Amount DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY Region ORDER BY Amount DESC) AS dense_rnk
FROM Sales;
```

| Region | SalesRep | Amount | rn | rnk | dense_rnk |
|---|---|---|---|---|---|
| East | Raj | 700 | 1 | 1 | 1 |
| East | Anita | 700 | 2 | 1 | 1 |
| East | Meera | 500 | 3 | 3 | 2 |
| West | Priya | 900 | 1 | 1 | 1 |
| West | Sam | 400 | 2 | 2 | 2 |
| West | Vikram | 300 | 3 | 3 | 3 |

**Which one do you want?**

| Use | Function | Why |
|---|---|---|
| **Deduplication** — keep exactly one row per key | `ROW_NUMBER` | You need precisely one winner. `RANK` would keep *both* tied rows and re-introduce the duplicate you were removing. |
| **"Top 3 performers"** — a genuine competition | `RANK` | Two people tied for 1st means there is no 2nd place. Olympic medals work this way. |
| **"Top 3 price points"** — distinct levels | `DENSE_RANK` | You're ranking the *values*, not the rows, so no gaps. |
| **Pagination / stable row IDs** | `ROW_NUMBER` | The only one guaranteed to be unique and gapless. |

> **The dedupe trap:** `ROW_NUMBER() ... = 1` gives one row per key *even when tied* — but if the `ORDER BY` can't break the tie deterministically, **which** row survives is arbitrary and may change between runs. Always order by something unique as a final tiebreaker: `ORDER BY updated_at DESC, source_file, row_id`.

### `NTILE(n)` — split into n buckets

```sql
SELECT Region, SalesRep, Amount,
       NTILE(2) OVER (PARTITION BY Region ORDER BY Amount DESC) AS half
FROM Sales;
```

```text
   PARTITION "East": 3 rows into 2 buckets -> 3/2 is not whole,
                     so the EARLIER buckets get the extra row (2 then 1)

   Raj      700   -> bucket 1
   Anita    700   -> bucket 1
   Meera    500   -> bucket 2
```

| Region | SalesRep | Amount | half |
|---|---|---|---|
| East | Raj | 700 | 1 |
| East | Anita | 700 | 1 |
| East | Meera | 500 | 2 |
| West | Priya | 900 | 1 |
| West | Sam | 400 | 1 |
| West | Vikram | 300 | 2 |

**Use it when:** quartiles, deciles, percentile bands — "which spending quartile is this customer in?", "split the workload into 8 even batches for parallel processing."

> **`NTILE` splits by *row count*, not by *value*.** Two customers with identical spend can land in different buckets purely because of where they sit in the sort. If you need value-based bands, use a [non-equi join to a range table](07_SQL_Keys_and_Joins.md#10-equi-join-vs-non-equi-theta-join--what-the-on-condition-looks-like) or `CASE`, not `NTILE`.

### `PERCENT_RANK` and `CUME_DIST` — relative position

| Function | Formula | Range |
|---|---|---|
| `PERCENT_RANK()` | `(RANK - 1) / (total_rows - 1)` | 0 to 1, always starts at 0 |
| `CUME_DIST()` | `rows_at_or_before_this_value / total_rows` | >0 to 1, always ends at 1 |

```text
   PARTITION "East", ORDER BY Amount DESC   (3 rows)

   Raj      700   RANK=1   PERCENT_RANK = (1-1)/2 = 0.0    CUME_DIST = 2/3 = 0.667
   Anita    700   RANK=1   PERCENT_RANK = (1-1)/2 = 0.0    CUME_DIST = 2/3 = 0.667
   Meera    500   RANK=3   PERCENT_RANK = (3-1)/2 = 1.0    CUME_DIST = 3/3 = 1.000
                                                            ^ both 700s count as
                                                              "at or before", so both
                                                              tied rows share 2/3
```

**Use them when:** "is this transaction in the top 1% by value?" (`PERCENT_RANK`), or building a cumulative distribution for outlier detection. In practice `NTILE` and explicit percentile functions (`PERCENTILE_CONT`) cover most needs — these two are worth *recognizing* more than reaching for.

---

## Family 2 — Aggregate functions with `OVER`

Any aggregate you already know becomes a window function by adding `OVER`. Nothing else changes — `SUM` still sums, it just doesn't collapse rows.

### Partition total and percent of total

```sql
SELECT Region, SalesRep, Amount,
       SUM(Amount) OVER (PARTITION BY Region)                       AS region_total,
       SUM(Amount) OVER ()                                          AS grand_total,
       ROUND(Amount * 100.0 / SUM(Amount) OVER (PARTITION BY Region), 1) AS pct_of_region
FROM Sales;
```

Note `OVER ()` — completely empty. That's a valid window meaning **"every row in the result"**, which is how you get a grand total onto every row.

| Region | SalesRep | Amount | region_total | grand_total | pct_of_region |
|---|---|---|---|---|---|
| East | Meera | 500 | 1900 | 3500 | 26.3 |
| East | Raj | 700 | 1900 | 3500 | 36.8 |
| East | Anita | 700 | 1900 | 3500 | 36.8 |
| West | Vikram | 300 | 1600 | 3500 | 18.8 |
| West | Priya | 900 | 1600 | 3500 | 56.3 |
| West | Sam | 400 | 1600 | 3500 | 25.0 |

**Use it when:** percent-of-total, contribution analysis, "this rep vs their region average" — any comparison of a row against its own group. Without windows this needs a subquery or self-join per comparison; with windows it's one extra column each.

> **Add `ORDER BY` and the meaning changes completely.** `SUM(Amount) OVER (PARTITION BY Region)` is the region **total** on every row. `SUM(Amount) OVER (PARTITION BY Region ORDER BY SaleDate)` is a **running** total. Same function, same partition — the presence of `ORDER BY` silently switches on a default frame. This catches people constantly, and is covered next.

### Running totals and moving averages

```sql
SELECT Region, SaleDate, Amount,
       SUM(Amount) OVER (PARTITION BY Region ORDER BY SaleDate)                 AS running_total,
       AVG(Amount) OVER (PARTITION BY Region ORDER BY SaleDate
                         ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)              AS avg_2row,
       COUNT(*)    OVER (PARTITION BY Region ORDER BY SaleDate)                 AS sale_no
FROM Sales;
```

```text
   PARTITION "East"        running frame              2-row moving frame
   ------------------------------------------------------------------------
   01-05   500      [500]                 = 500      [500]           = 500.0
   01-12   700      [500,700]             = 1200     [500,700]       = 600.0
   02-03   700      [500,700,700]         = 1900     [700,700]       = 700.0
                     ^ grows forever                  ^ slides, always 2 wide
```

| Region | SaleDate | Amount | running_total | avg_2row | sale_no |
|---|---|---|---|---|---|
| East | 2026-01-05 | 500 | 500 | 500.0 | 1 |
| East | 2026-01-12 | 700 | 1200 | 600.0 | 2 |
| East | 2026-02-03 | 700 | 1900 | 700.0 | 3 |
| West | 2026-01-08 | 300 | 300 | 300.0 | 1 |
| West | 2026-02-11 | 900 | 1200 | 600.0 | 2 |
| West | 2026-03-02 | 400 | 1600 | 650.0 | 3 |

**Use it when:** cumulative revenue, running balances, 7-day moving averages, "how many orders had this customer placed before this one?" (`COUNT(*) OVER (... ORDER BY ...)` minus 1).

---

## Family 3 — Offset and value functions

These reach out and grab a value from *another row* in the same partition. They're what makes period-over-period comparison a one-liner.

### `LAG` and `LEAD` — the previous and next row

```sql
SELECT Region, SaleDate, Amount,
       LAG(Amount)      OVER (PARTITION BY Region ORDER BY SaleDate) AS prev_amount,
       LEAD(Amount)     OVER (PARTITION BY Region ORDER BY SaleDate) AS next_amount,
       Amount - LAG(Amount, 1, 0) OVER (PARTITION BY Region ORDER BY SaleDate) AS change_vs_prev
FROM Sales;
```

```text
   PARTITION "East"
   ---------------------------------------------------------------
                       LAG (look back)      LEAD (look forward)
   01-05   500    <--- NULL (nothing before)  ---> 700
   01-12   700    <--- 500                    ---> 700
   02-03   700    <--- 700                    ---> NULL (nothing after)

   LAG/LEAD never cross a partition boundary -- West starts fresh at NULL
```

| Region | SaleDate | Amount | prev_amount | next_amount | change_vs_prev |
|---|---|---|---|---|---|
| East | 2026-01-05 | 500 | *NULL* | 700 | 500 |
| East | 2026-01-12 | 700 | 500 | 700 | 200 |
| East | 2026-02-03 | 700 | 700 | *NULL* | 0 |
| West | 2026-01-08 | 300 | *NULL* | 900 | 300 |
| West | 2026-02-11 | 900 | 300 | 400 | 600 |
| West | 2026-03-02 | 400 | 900 | *NULL* | -500 |

Both take three arguments: `LAG(column, offset, default)`. `LAG(Amount, 1, 0)` means "the value 1 row back, or **0** if there isn't one" — which is why `change_vs_prev` shows 500 instead of NULL on the first row. Without that default, every arithmetic expression touching the first row of each partition silently becomes NULL.

**Use it when:** month-over-month growth, detecting status changes (`WHERE status <> LAG(status) OVER (...)`), calculating gaps between events, building SCD Type 2 `ValidTo` dates from the next row's `ValidFrom`.

### `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`

```sql
SELECT Region, SaleDate, Amount,
       FIRST_VALUE(Amount) OVER (PARTITION BY Region ORDER BY SaleDate) AS first_sale,
       LAST_VALUE(Amount)  OVER (PARTITION BY Region ORDER BY SaleDate) AS last_sale_WRONG,
       LAST_VALUE(Amount)  OVER (PARTITION BY Region ORDER BY SaleDate
                                 ROWS BETWEEN UNBOUNDED PRECEDING
                                          AND UNBOUNDED FOLLOWING)      AS last_sale_RIGHT
FROM Sales;
```

| Region | SaleDate | Amount | first_sale | last_sale_WRONG | last_sale_RIGHT |
|---|---|---|---|---|---|
| East | 2026-01-05 | 500 | 500 | **500** | 700 |
| East | 2026-01-12 | 700 | 500 | **700** | 700 |
| East | 2026-02-03 | 700 | 500 | **700** | 700 |

**`last_sale_WRONG` just returns the current row's own value** — it isn't a bug in the engine, it's the default frame doing exactly what it's documented to do. See the next section, because this trap is the single best argument for understanding frames.

---

## Frames — the part everyone skips, and then debugs

A **frame** is the slice of the partition visible to the function *for the row being computed*. It only applies when `ORDER BY` is present.

### The two defaults you must know

| Your `OVER` clause | Frame you actually get | Meaning |
|---|---|---|
| `OVER (PARTITION BY x)` — **no** ORDER BY | the entire partition | every row sees every row → a **total** |
| `OVER (PARTITION BY x ORDER BY y)` | `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | start of partition → here → a **running** value |

That second default explains `LAST_VALUE`: the frame *ends at the current row*, so "the last value in the frame" is the current row itself. Widening the frame to `UNBOUNDED FOLLOWING` fixes it.

```text
   Default frame, computing row 2 of East:

      [ row1  row2 ] row3          FIRST_VALUE -> row1   (correct by luck)
        ^^^^^^^^^^                 LAST_VALUE  -> row2   (the current row!)
        the visible frame

   Explicit  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING:

      [ row1  row2  row3 ]         LAST_VALUE  -> row3   (what you meant)
        ^^^^^^^^^^^^^^^^^
```

### Frame syntax

```sql
ROWS  BETWEEN <start> AND <end>     -- counts physical rows
RANGE BETWEEN <start> AND <end>     -- counts by ORDER BY *value*, ties included
GROUPS BETWEEN <start> AND <end>    -- counts groups of tied rows (SQL:2011, PostgreSQL 11+)
```

Where `<start>` / `<end>` are: `UNBOUNDED PRECEDING`, `n PRECEDING`, `CURRENT ROW`, `n FOLLOWING`, `UNBOUNDED FOLLOWING`.

| Frame | Gives you |
|---|---|
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | running total |
| `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` | 7-row moving window |
| `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` | centred 3-row smoothing |
| `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING` | "how much is still to come" |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | whole partition (what `LAST_VALUE` needs) |

### `ROWS` vs `RANGE` — the tie trap

They're identical **until the `ORDER BY` column has duplicate values**. Order East by `Amount DESC` (Raj and Anita both 700):

```text
   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
   -- strictly positional: each row sees only the rows physically before it
   Raj     700   [700]              =  700
   Anita   700   [700, 700]         = 1400
   Meera   500   [700, 700, 500]    = 1900

   RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW   (the DEFAULT)
   -- value-based: all rows with the SAME ORDER BY value are peers and
   --              are included together, so tied rows get identical answers
   Raj     700   [700, 700]         = 1400   <-- jumped ahead: includes Anita
   Anita   700   [700, 700]         = 1400
   Meera   500   [700, 700, 500]    = 1900
```

A "running total" that's supposed to climb 700 → 1400 → 1900 instead reads 1400 → 1400 → 1900. **`RANGE` is the default**, so this is what you get unless you ask for `ROWS`.

> **Practical rule:** write `ROWS` explicitly for running totals and moving averages. Use `RANGE` deliberately when tied rows *should* share a value — for example a daily running total where multiple transactions share a date and you want the whole day counted at once.

---

## Where you can (and can't) use a window function

Window functions are evaluated **after** `FROM`, `WHERE`, `GROUP BY`, and `HAVING`, but **before** `ORDER BY` and `LIMIT`. That single fact explains every "why won't this work" error.

```text
   FROM / JOIN
        |
   WHERE            <-- window functions DO NOT EXIST YET  (cannot filter on them)
        |
   GROUP BY / HAVING  <-- still don't exist
        |
   SELECT           <-- window functions are computed HERE
        |
   ORDER BY         <-- can use them (they exist now)
        |
   LIMIT
```

```sql
-- ERROR: rn does not exist yet when WHERE runs
SELECT SalesRep, ROW_NUMBER() OVER (PARTITION BY Region ORDER BY Amount DESC) AS rn
FROM Sales
WHERE rn <= 2;
```

**Three ways to fix it:**

```sql
-- 1. CTE (clearest, and the one to use by default)
WITH ranked AS (
    SELECT Region, SalesRep, Amount,
           ROW_NUMBER() OVER (PARTITION BY Region ORDER BY Amount DESC) AS rn
    FROM Sales
)
SELECT Region, SalesRep, Amount FROM ranked WHERE rn <= 2;

-- 2. Subquery (identical logic, denser)
SELECT * FROM (
    SELECT Region, SalesRep, Amount,
           ROW_NUMBER() OVER (PARTITION BY Region ORDER BY Amount DESC) AS rn
    FROM Sales
) t WHERE t.rn <= 2;

-- 3. QUALIFY -- filters window results directly, no wrapper needed
--    (Databricks, Snowflake, BigQuery, Teradata -- NOT SQL Server or PostgreSQL)
SELECT Region, SalesRep, Amount
FROM Sales
QUALIFY ROW_NUMBER() OVER (PARTITION BY Region ORDER BY Amount DESC) <= 2;
```

**Top 2 per region:**

| Region | SalesRep | Amount |
|---|---|---|
| East | Raj | 700 |
| East | Anita | 700 |
| West | Priya | 900 |
| West | Sam | 400 |

> You **can** put a window function in `ORDER BY` directly (`ORDER BY SUM(Amount) OVER (PARTITION BY Region) DESC`) — it runs after `SELECT`, so the value exists by then.
>
> You **cannot** nest window functions (`SUM(ROW_NUMBER() OVER (...)) OVER (...)`) — wrap the inner one in a CTE and window over that.

---

## The patterns you'll actually use weekly

### 1. Deduplication — keep the latest row per key

The most-used window pattern in data engineering, full stop. Every CDC feed, every re-delivered event, every staging table with overlapping loads needs it.

**Staging_Customers** (the same customer arrived three times)

| CustomerID | Name | City | updated_at |
|---|---|---|---|
| 1 | Meera | Hyderabad | 2026-01-05 |
| 1 | Meera | Bengaluru | 2026-03-11 |
| 2 | Raj | Pune | 2026-02-02 |

```sql
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY CustomerID
                              ORDER BY updated_at DESC) AS rn
    FROM Staging_Customers
)
SELECT CustomerID, Name, City, updated_at
FROM ranked
WHERE rn = 1;
```

| CustomerID | Name | City | updated_at |
|---|---|---|---|
| 1 | Meera | Bengaluru | 2026-03-11 |
| 2 | Raj | Pune | 2026-02-02 |

**Why `ROW_NUMBER` and not `RANK`:** if two rows share the same `updated_at`, `RANK` gives both rank 1 and the duplicate survives — defeating the entire purpose. `ROW_NUMBER` always picks exactly one.

### 2. Top-N per group

Covered above — `ROW_NUMBER` (or `RANK`, if ties should all qualify) in a CTE, filtered to `<= N`. This is the SQL equivalent of the [`LATERAL`/`APPLY` join](07_SQL_Keys_and_Joins.md#12-lateral--apply--a-join-whose-right-side-runs-per-left-row); window functions usually win when N is large or the table is columnar, `LATERAL` when N is 1 and the inner side is indexed.

### 3. Period-over-period change

```sql
SELECT Region, SaleDate, Amount,
       LAG(Amount) OVER (PARTITION BY Region ORDER BY SaleDate) AS prev,
       ROUND( (Amount - LAG(Amount) OVER (PARTITION BY Region ORDER BY SaleDate))
              * 100.0 / NULLIF(LAG(Amount) OVER (PARTITION BY Region ORDER BY SaleDate), 0)
            , 1) AS pct_change
FROM Sales;
```

`NULLIF(..., 0)` guards against divide-by-zero when the previous period was 0 — a NULL result is honest; a crashed report is not.

### 4. Gaps and islands / sessionization

"Group consecutive events into sessions when the gap exceeds 30 minutes." The three-step trick:

```sql
WITH flagged AS (      -- step 1: mark where a NEW session starts
    SELECT UserID, EventTime,
           CASE WHEN EventTime - LAG(EventTime) OVER (PARTITION BY UserID ORDER BY EventTime)
                     > INTERVAL '30 minutes'
                THEN 1 ELSE 0 END AS is_new_session
    FROM Events
),
sessions AS (          -- step 2: running sum of the flags = a session ID
    SELECT *,
           SUM(is_new_session) OVER (PARTITION BY UserID ORDER BY EventTime) AS session_id
    FROM flagged
)
SELECT UserID, session_id,       -- step 3: aggregate per session
       MIN(EventTime) AS started, MAX(EventTime) AS ended, COUNT(*) AS events
FROM sessions
GROUP BY UserID, session_id;
```

```text
   EventTime   gap     is_new_session   running SUM = session_id
   ------------------------------------------------------------
   09:00        -            1                  1
   09:10      10 min         0                  1     same session
   09:15       5 min         0                  1     same session
   10:30      75 min         1                  2     NEW session
   10:35       5 min         0                  2     same session
```

The running sum over a 0/1 flag turns "where does a group start" into "which group am I in" — a technique worth memorizing, because it solves every consecutive-run problem: streaks, downtime windows, contiguous date ranges.

### 5. Building SCD Type 2 validity ranges

```sql
SELECT CustomerID, City,
       updated_at AS ValidFrom,
       LEAD(updated_at) OVER (PARTITION BY CustomerID ORDER BY updated_at) AS ValidTo,
       CASE WHEN LEAD(updated_at) OVER (PARTITION BY CustomerID ORDER BY updated_at) IS NULL
            THEN 'Y' ELSE 'N' END AS IsCurrent
FROM Customer_History;
```

`LEAD` supplies each row's expiry from the *next* version's start date, and the row where `LEAD` returns NULL is by definition the current one. See [Slowly Changing Dimensions](../Data_Modeling/04_Slowly_Changing_Dimensions.md).

---

## Performance — what a window function costs

A window function's cost is dominated by **one thing: sorting**.

- `PARTITION BY x ORDER BY y` requires the rows sorted by `(x, y)`. If no index provides that order, the engine sorts — and a sort that doesn't fit in memory **spills to disk**, which is where "the query got slow" comes from.
- **Identical `OVER` clauses share one sort.** Three functions all using `OVER (PARTITION BY Region ORDER BY SaleDate)` cost roughly one sort, not three. Three *different* `OVER` clauses cost three sorts.
- **So: standardize your `OVER` clauses.** Use a named window to make the reuse explicit and impossible to get subtly wrong:

```sql
SELECT Region, SaleDate, Amount,
       SUM(Amount) OVER w AS running_total,
       LAG(Amount) OVER w AS prev,
       ROW_NUMBER() OVER w AS seq
FROM Sales
WINDOW w AS (PARTITION BY Region ORDER BY SaleDate);   -- PostgreSQL, MySQL 8+, Oracle, Databricks
```

- **`PARTITION BY` helps** — it lets the engine process each partition independently, and in Spark it maps directly onto a shuffle by that key. A window with **no** `PARTITION BY` on a large table is a red flag: it forces all data through a *single* partition/task, and no amount of cluster is going to help.
- **Filter before you window.** `WHERE` runs first, so narrowing rows early shrinks what has to be sorted. Filtering *after* (in the CTE wrapper) means you sorted rows you then threw away.
- **A covering index on `(partition_col, order_col)`** can let an OLTP engine skip the sort entirely.

---

## Dialect differences worth knowing

| Feature | Support |
|---|---|
| Core windows (`OVER`, `PARTITION BY`, frames) | Everywhere: SQL Server 2012+, PostgreSQL, Oracle, MySQL 8+, Spark, Snowflake, BigQuery |
| `QUALIFY` | Databricks, Snowflake, BigQuery, Teradata — **not** SQL Server or PostgreSQL |
| `WINDOW w AS (...)` named windows | PostgreSQL, MySQL 8+, Oracle, Spark — **not** SQL Server |
| `GROUPS` frame mode | PostgreSQL 11+, Oracle — patchy elsewhere |
| `IGNORE NULLS` on `LAG`/`LEAD`/`FIRST_VALUE` | Oracle, Snowflake, BigQuery, Databricks, SQL Server 2022+ — not older SQL Server, not PostgreSQL (emulate with a conditional running `MAX`) |
| `RANGE` with `INTERVAL` (e.g. `RANGE BETWEEN INTERVAL '7' DAY PRECEDING ...`) | PostgreSQL, Oracle, Snowflake — genuinely useful for calendar-based windows with missing days |

> `IGNORE NULLS` deserves a mention: `LAST_VALUE(price) IGNORE NULLS OVER (...)` is the idiomatic "last known non-null value" / forward-fill, which otherwise takes an awkward `MAX(CASE ...)` running window.

---

## Field-tested gotchas

- **Forgetting `PARTITION BY`.** The query succeeds and returns the right row count — it just accumulates across groups that should be independent. Nothing errors; the numbers are simply wrong. Always ask "restart per what?"
- **`ORDER BY` changed a total into a running total.** Adding `ORDER BY` to an aggregate window silently switches on the default frame. If you want the partition total, leave `ORDER BY` out — or write the frame explicitly.
- **`RANGE` vs `ROWS` on tied values.** The default is `RANGE`; ties share a value. Write `ROWS` for genuine running totals.
- **`LAST_VALUE` returns the current row.** Default frame ends at `CURRENT ROW`. Needs `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
- **Non-deterministic dedupe.** `ROW_NUMBER` with a non-unique `ORDER BY` picks an arbitrary winner that can change between runs — reruns produce different data, and the diff is nearly impossible to explain later. Always add a unique tiebreaker.
- **`COUNT(*) OVER (ORDER BY ...)` is a running count, not a total.** Same `ORDER BY` trap, different function.
- **Windows over the whole table with no partition** serialize in distributed engines — one task, one core, however big the cluster.
- **NULLs sort somewhere.** `ORDER BY updated_at DESC` puts NULLs first in PostgreSQL and last in SQL Server by default. If NULL timestamps exist in your dedupe key, the "latest" row may be the one that has no timestamp at all. Be explicit: `NULLS LAST`.

---

## Interview-grade Q&A

- *`ROW_NUMBER` vs `RANK` vs `DENSE_RANK`?* On ties: 1,2,3 / 1,1,3 / 1,1,2. `ROW_NUMBER` is always unique, `RANK` leaves gaps after ties, `DENSE_RANK` doesn't. Use `ROW_NUMBER` for deduplication because it guarantees exactly one winner.
- *How do you keep only the latest record per key?* `ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC)` in a CTE, filtered to `= 1` — with a unique tiebreaker in the `ORDER BY` so it's deterministic.
- *Why can't I filter on a window function in `WHERE`?* Windows are computed after `WHERE` in the logical processing order. Wrap in a CTE/subquery, or use `QUALIFY` where the dialect supports it.
- *What's the difference between `GROUP BY` and a window function?* `GROUP BY` collapses rows into one per group; a window function annotates every row with its group's value, keeping the detail. Use a window whenever you need detail and summary side by side.
- *What does `SUM(x) OVER (PARTITION BY r)` give you versus `SUM(x) OVER (PARTITION BY r ORDER BY d)`?* The first is the partition total on every row; the second is a running total, because `ORDER BY` activates a default frame ending at the current row.
- *Explain `ROWS` vs `RANGE`.* `ROWS` counts physical rows; `RANGE` counts by `ORDER BY` value, so tied rows are treated as peers and receive identical results. `RANGE` is the default — a common source of wrong running totals.
- *Why does `LAST_VALUE` return the current row?* The default frame is `UNBOUNDED PRECEDING TO CURRENT ROW`, so the last row *in the frame* is the current row. Widen the frame to `UNBOUNDED FOLLOWING`.
- *How do you group consecutive events into sessions?* `LAG` to detect gaps, a `CASE` to flag session starts, then a running `SUM` over that flag to produce a session ID — the gaps-and-islands pattern.
- *What's the performance cost of a window function?* A sort per distinct `OVER` clause. Reuse identical `OVER` clauses (or a named `WINDOW`), filter before windowing, and never run an unpartitioned window over a huge table in a distributed engine.

---

## Further Learning — Docs & Videos

**Documentation**
- Window functions tutorial (PostgreSQL): https://www.postgresql.org/docs/current/tutorial-window.html
- OVER clause reference (SQL Server): https://learn.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql
- Window functions (Databricks SQL): https://docs.databricks.com/en/sql/language-manual/sql-ref-window-functions.html

**Videos**
- SQL window functions explained: https://www.youtube.com/results?search_query=sql+window+functions+explained
- ROW_NUMBER vs RANK vs DENSE_RANK: https://www.youtube.com/results?search_query=row_number+vs+rank+vs+dense_rank
