# SQL by Example — Input Table → Output Table

## How to use this file

Every other note in this folder explains a concept. **This one shows it.** One fixed set of input tables, then every SQL operation applied to them — and for each one:

- **IN** — the exact rows going in
- **QUERY** — the statement
- **OUT** — the exact rows coming out
- **What happened / Why / How** — what changed, the rule that caused it, and the mechanism underneath

Nothing is abbreviated with "…" and no output is hand-waved. If a row disappears, this file says which row and why.

---

## The input tables — used by every example below

**Customers** (4 rows)

| CustomerID | Name | City | SignupDate |
|---|---|---|---|
| 1 | Meera | Hyderabad | 2025-11-02 |
| 2 | Raj | Pune | 2026-01-15 |
| 3 | Anita | Chennai | 2026-02-20 |
| 4 | Vikram | Hyderabad | 2026-03-05 |

**Orders** (6 rows)

| OrderID | CustomerID | OrderDate | Amount | Status |
|---|---|---|---|---|
| 501 | 1 | 2026-01-10 | 2000 | Shipped |
| 502 | 1 | 2026-02-14 | 1500 | Shipped |
| 503 | 2 | 2026-02-20 | 3000 | Pending |
| 504 | 3 | 2026-03-01 | 900 | Cancelled |
| 505 | 2 | 2026-03-15 | *NULL* | Pending |
| 506 | *NULL* | 2026-03-20 | 700 | Shipped |

**Three deliberate imperfections** — each one exists to make a rule visible:

| # | The imperfection | What it exposes |
|---|---|---|
| 1 | **Vikram has no orders** | How each join treats an unmatched left row |
| 2 | **Order 505 has a NULL Amount** | How `WHERE`, `CASE`, `AVG`, and `SUM` each treat NULL differently |
| 3 | **Order 506 has a NULL CustomerID** | How an orphan row behaves in joins and `NOT IN` |

---

# Part A — Reading data

## 1. `SELECT` — choose columns

**IN:** Customers (4 rows)

```sql
SELECT Name, City FROM Customers;
```

**OUT** (4 rows)

| Name | City |
|---|---|
| Meera | Hyderabad |
| Raj | Pune |
| Anita | Chennai |
| Vikram | Hyderabad |

**What happened:** Same 4 rows, fewer columns.
**Why:** `SELECT` is a *projection* — it picks columns. It never removes rows.
**How:** The engine reads each row and emits only the requested columns. Row count in always equals row count out.

---

## 2. `WHERE` — filter rows

**IN:** Customers (4 rows)

```sql
SELECT Name, City FROM Customers WHERE City = 'Hyderabad';
```

**OUT** (2 rows)

| Name | City |
|---|---|
| Meera | Hyderabad |
| Vikram | Hyderabad |

```text
   Meera   Hyderabad   ->  'Hyderabad' = 'Hyderabad'   TRUE     kept
   Raj     Pune        ->  'Pune'      = 'Hyderabad'   FALSE    dropped
   Anita   Chennai     ->  'Chennai'   = 'Hyderabad'   FALSE    dropped
   Vikram  Hyderabad   ->  'Hyderabad' = 'Hyderabad'   TRUE     kept
```

**What happened:** 4 rows in, 2 out. Raj (Pune) and Anita (Chennai) were removed.
**Why:** `WHERE` keeps a row only when the condition evaluates to **true**.
**How:** The engine tests each row against the predicate. Without an index it scans all 4; with an index on `City` it seeks straight to the matching rows ([Indexes](11_SQL_Indexes.md)).

---

## 3. `WHERE` meets NULL — the row that fails *both* tests

**IN:** Orders (6 rows)

```sql
SELECT OrderID, Amount FROM Orders WHERE Amount > 1000;
```

**OUT** (3 rows)

| OrderID | Amount |
|---|---|
| 501 | 2000 |
| 502 | 1500 |
| 503 | 3000 |

Now the opposite test:

```sql
SELECT OrderID, Amount FROM Orders WHERE Amount <= 1000;
```

**OUT** (2 rows)

| OrderID | Amount |
|---|---|
| 504 | 900 |
| 506 | 700 |

**What happened:** 3 rows + 2 rows = **5**, but the table has **6**. Order 505 appears in neither.
**Why:** `505.Amount` is NULL. `NULL > 1000` is not false — it's **unknown**, and `WHERE` keeps only rows where the condition is **true**. Unknown is discarded, both times.
**How:** SQL uses three-valued logic: true / false / unknown. Any comparison involving NULL yields unknown.

```text
   Amount = NULL

   NULL > 1000   ->  UNKNOWN  ->  row dropped
   NULL <= 1000  ->  UNKNOWN  ->  row dropped
   NULL = NULL   ->  UNKNOWN  ->  row dropped

   the ONLY test that works:
   Amount IS NULL ->  TRUE     ->  row kept
```

```sql
SELECT OrderID, Amount FROM Orders WHERE Amount IS NULL;
```

**OUT** (1 row)

| OrderID | Amount |
|---|---|
| 505 | *NULL* |

> **The practical lesson:** two filters that look like they cover everything can silently lose rows. To genuinely cover all cases, write `WHERE Amount <= 1000 OR Amount IS NULL`.

---

## 4. `DISTINCT` — remove duplicate rows

**IN:** Customers (4 rows)

```sql
SELECT City FROM Customers;          -- without DISTINCT
```

| City |
|---|
| Hyderabad |
| Pune |
| Chennai |
| Hyderabad |

```sql
SELECT DISTINCT City FROM Customers;
```

**OUT** (3 rows)

| City |
|---|
| Hyderabad |
| Pune |
| Chennai |

**What happened:** 4 rows became 3 — the second Hyderabad was removed.
**Why:** `DISTINCT` deduplicates on **every column in the SELECT list**, not just the first.
**How:** The engine sorts or hashes the rows to find duplicates. That's real work — on a large table, `DISTINCT` is not free.

> `SELECT DISTINCT City, Name` would return all **4** rows, because Meera and Vikram have different names. Adding a column to a `DISTINCT` query can *increase* the row count.

---

## 5. `ORDER BY` — sort the output

**IN:** Orders (6 rows)

```sql
SELECT OrderID, Amount FROM Orders ORDER BY Amount DESC;
```

**OUT** (6 rows — SQL Server)

| OrderID | Amount |
|---|---|
| 503 | 3000 |
| 501 | 2000 |
| 502 | 1500 |
| 504 | 900 |
| 506 | 700 |
| 505 | *NULL* |

**What happened:** Same 6 rows, reordered. Nothing was added or removed.
**Why:** `ORDER BY` only arranges — it's the last thing to run before the rows are returned.
**How:** The engine sorts. If the sort doesn't fit in memory it **spills to disk**, which is a common cause of a slow query.

> **NULL placement is dialect-specific.** SQL Server treats NULL as the *lowest* value → last in `DESC`. PostgreSQL treats it as the *highest* → **first** in `DESC`. Never rely on the default: write `ORDER BY Amount DESC NULLS LAST` where supported.

---

## 6. `TOP` / `LIMIT` — take the first N

**IN:** Orders (6 rows)

```sql
SELECT TOP 2 OrderID, Amount FROM Orders ORDER BY Amount DESC;   -- SQL Server
SELECT OrderID, Amount FROM Orders ORDER BY Amount DESC LIMIT 2; -- PostgreSQL/MySQL
```

**OUT** (2 rows)

| OrderID | Amount |
|---|---|
| 503 | 3000 |
| 501 | 2000 |

**What happened:** Only the first 2 rows of the sorted result survived.
**Why:** `LIMIT`/`TOP` runs **after** `ORDER BY`. Without `ORDER BY` it returns 2 *arbitrary* rows that can differ between runs.
**How:** The engine can often stop early — a "Top N Sort" keeps only the best 2 in memory instead of sorting all 6.

---

## 7. `CASE` — conditional logic per row

**IN:** Orders (6 rows)

```sql
SELECT OrderID, Amount,
       CASE WHEN Amount >= 2000 THEN 'Large'
            WHEN Amount >= 1000 THEN 'Medium'
            ELSE 'Small'
       END AS size_band
FROM Orders;
```

**OUT** (6 rows)

| OrderID | Amount | size_band |
|---|---|---|
| 501 | 2000 | Large |
| 502 | 1500 | Medium |
| 503 | 3000 | Large |
| 504 | 900 | Small |
| 505 | *NULL* | **Small** ← wrong! |
| 506 | 700 | Small |

**What happened:** Order 505 was labelled `Small` despite having no amount at all.
**Why:** Every `WHEN` evaluated to unknown (NULL comparisons), so none matched, so `CASE` fell through to `ELSE`.
**How:** `CASE` tests each `WHEN` top to bottom and takes the first that is **true**. Unknown is not true, so all were skipped.

```text
   Amount = NULL

   WHEN NULL >= 2000  -> UNKNOWN, not matched
   WHEN NULL >= 1000  -> UNKNOWN, not matched
   ELSE               -> taken by default  ->  'Small'
                                                ^ a data-quality problem
                                                  silently became a category
```

**The fix — handle NULL explicitly, first:**

```sql
CASE WHEN Amount IS NULL   THEN 'Unknown'
     WHEN Amount >= 2000   THEN 'Large'
     WHEN Amount >= 1000   THEN 'Medium'
     ELSE 'Small' END AS size_band
```

| OrderID | Amount | size_band |
|---|---|---|
| 505 | *NULL* | Unknown |

> This is one of the most common silent bugs in reporting: an `ELSE` branch quietly absorbing missing data into a real business category.

---

# Part B — Aggregating

## 8. Aggregate functions — five answers from one column

**IN:** Orders, the `Amount` column: `2000, 1500, 3000, 900, NULL, 700`

```sql
SELECT COUNT(*)      AS count_star,
       COUNT(Amount) AS count_amount,
       SUM(Amount)   AS total,
       AVG(Amount)   AS average,
       MIN(Amount)   AS smallest,
       MAX(Amount)   AS largest
FROM Orders;
```

**OUT** (1 row)

| count_star | count_amount | total | average | smallest | largest |
|---|---|---|---|---|---|
| 6 | **5** | 8100 | **1620** | 700 | 3000 |

**What happened:** 6 rows collapsed into 1. `COUNT(*)` says 6 but `COUNT(Amount)` says 5, and the average is 1620 rather than 1350.
**Why:** **Every aggregate except `COUNT(*)` ignores NULLs.** `COUNT(*)` counts *rows*; `COUNT(Amount)` counts *non-null values*.
**How:** `AVG` is `SUM / COUNT(Amount)`, not `SUM / COUNT(*)`:

```text
   SUM   = 2000 + 1500 + 3000 + 900 + 700  = 8100    (NULL simply skipped)
   COUNT(*)      = 6      <- rows
   COUNT(Amount) = 5      <- non-null values

   AVG = 8100 / 5 = 1620      <- what SQL returns
         8100 / 6 = 1350      <- what people expect
```

**Which is right?** It depends on what NULL *means*. If order 505's amount is genuinely unknown, 1620 is correct — you shouldn't average in a value you don't have. If a missing amount means zero, say so explicitly:

```sql
SELECT AVG(COALESCE(Amount, 0)) FROM Orders;    -- 1350
```

---

## 9. `GROUP BY` — one row out per group

**IN:** Orders (6 rows)

```sql
SELECT Status, COUNT(*) AS orders, SUM(Amount) AS revenue
FROM Orders
GROUP BY Status;
```

**OUT** (3 rows)

| Status | orders | revenue |
|---|---|---|
| Shipped | 3 | 4200 |
| Pending | 2 | 3000 |
| Cancelled | 1 | 900 |

**What happened:** 6 rows became 3 — one per distinct `Status`. `OrderID`, `OrderDate`, and individual amounts no longer exist in the result.
**Why:** `GROUP BY` *collapses*. Any column not in the `GROUP BY` and not wrapped in an aggregate is gone, and asking for it is an error.
**How:** The engine buckets rows by the grouping key, then folds each bucket down to one row:

```text
   Shipped  [501:2000, 502:1500, 506:700]  ->  count 3, sum 4200
   Pending  [503:3000, 505:NULL       ]  ->  count 2, sum 3000
                        ^ counted by COUNT(*), skipped by SUM
   Cancelled[504: 900               ]  ->  count 1, sum  900
```

Note Pending: `COUNT(*)` = 2 but only one row contributed to the 3000.

---

## 10. `HAVING` vs `WHERE` — filtering before or after grouping

**IN:** Orders (6 rows)

```sql
SELECT Status, COUNT(*) AS orders
FROM Orders
GROUP BY Status
HAVING COUNT(*) > 1;
```

**OUT** (2 rows)

| Status | orders |
|---|---|
| Shipped | 3 |
| Pending | 2 |

Cancelled (1 order) was removed **after** its group was formed.

Now the same-looking query with `WHERE`:

```sql
SELECT Status, COUNT(*) AS orders
FROM Orders
WHERE Status <> 'Cancelled'
GROUP BY Status;
```

**OUT** (2 rows)

| Status | orders |
|---|---|
| Shipped | 3 |
| Pending | 2 |

**What happened:** Same output, completely different mechanism.
**Why:** `WHERE` filters **rows before grouping**; `HAVING` filters **groups after aggregating**. `WHERE COUNT(*) > 1` is an error — the count doesn't exist yet.
**How:** The order of operations decides what's visible when:

```text
   FROM        6 rows
     |
   WHERE       filters ROWS         <- COUNT(*) does not exist yet
     |
   GROUP BY    builds groups
     |
   HAVING      filters GROUPS       <- COUNT(*) exists now
     |
   SELECT      computes output columns
     |
   ORDER BY    sorts
```

> **Performance rule:** filter in `WHERE` whenever you can. `WHERE` shrinks the data *before* the expensive grouping work; `HAVING` throws away results you already paid to compute.

---

# Part C — Combining tables

> The complete join catalog — 13 types with matching diagrams — is in [SQL Keys and Joins](07_SQL_Keys_and_Joins.md). This section shows the four core joins on *this* dataset so the row counts are traceable.

## 11. `INNER JOIN` — only matched pairs

**IN:** Customers (4) + Orders (6)

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customers c
INNER JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**OUT** (5 rows)

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Raj | 505 | *NULL* |
| Anita | 504 | 900 |

**What happened:** 4 + 6 rows in, 5 rows out. **Vikram vanished** (no orders) and **order 506 vanished** (NULL CustomerID). Meera and Raj each appear **twice**.
**Why:** An inner join keeps only pairs where the condition is true. `NULL = 1` is unknown, so 506 matches nothing — not even other NULLs.
**How:** Each left row is emitted **once per matching right row** — that repetition is *fan-out*:

```text
   Meera  -> 501, 502     ->  2 output rows   (Meera duplicated)
   Raj    -> 503, 505     ->  2 output rows   (Raj duplicated)
   Anita  -> 504          ->  1 output row
   Vikram -> (nothing)    ->  0 output rows   DROPPED
            (nothing) 506 ->  0 output rows   DROPPED
                              ---------------
                                5 rows
```

> **Why this matters:** `SELECT SUM(c.SomeCustomerValue)` after this join would double-count Meera and Raj. That's the #1 cause of "the totals doubled after I added a join."

---

## 12. `LEFT JOIN` — keep every customer

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customers c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**OUT** (6 rows)

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Raj | 505 | *NULL* |
| Anita | 504 | 900 |
| **Vikram** | *NULL* | *NULL* |

**What happened:** Vikram is back, padded with NULLs. Order 506 is still gone.
**Why:** `LEFT JOIN` guarantees every **left** row appears at least once. It says nothing about the right table.
**How:** Those NULLs are **not stored anywhere** — the join manufactures them to mean "nothing matched."

**Two rows now have a NULL Amount, for completely different reasons:**

| Row | Amount is NULL because |
|---|---|
| Raj / 505 | A real order exists, but its amount was never recorded — **stored** NULL |
| Vikram | No order exists at all — **invented** by the join |

`COUNT(o.OrderID)` distinguishes them (Vikram counts 0, Raj counts 1); `COUNT(*)` does not.

---

## 13. `FULL OUTER JOIN` — keep everything

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customers c
FULL OUTER JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**OUT** (7 rows)

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Raj | 505 | *NULL* |
| Anita | 504 | 900 |
| **Vikram** | *NULL* | *NULL* |
| *NULL* | **506** | 700 |

**What happened:** Both orphans survive — the customer with no order *and* the order with no customer.
**Why:** `FULL OUTER` is the only join where every input row is guaranteed to appear somewhere in the output.
**How:** Matched pairs, then unmatched-left NULL-padded, then unmatched-right NULL-padded.

**Row count summary for this dataset:**

| Join | Rows out | Who's missing |
|---|---|---|
| `INNER` | 5 | Vikram, order 506 |
| `LEFT` | 6 | order 506 |
| `RIGHT` | 6 | Vikram |
| `FULL OUTER` | 7 | nobody |
| `CROSS` | **24** | nobody — 4 × 6 every combination |

---

## 14. Finding what's missing — the anti join

```sql
SELECT c.Name
FROM Customers c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID);
```

**OUT** (1 row)

| Name |
|---|
| Vikram |

**What happened:** Only the customer with zero orders came back.
**Why:** `NOT EXISTS` keeps a left row precisely when the subquery finds nothing.
**How:** The engine probes for a match and stops at the first hit — it never needs to count them.

**Now the trap.** The "obvious" version with `NOT IN`:

```sql
SELECT c.Name FROM Customers c
WHERE c.CustomerID NOT IN (SELECT CustomerID FROM Orders);
```

**OUT: 0 rows.** Not one. Vikram doesn't appear either.

**Why:** The subquery returns `1, 1, 2, 3, 2, NULL`. `NOT IN` expands to `CustomerID <> 1 AND ... AND CustomerID <> NULL`, and that last comparison is **unknown** for every row — so no row is ever true.

```text
   Vikram (4) NOT IN (1, 1, 2, 3, 2, NULL)

     4 <> 1     TRUE
     4 <> 2     TRUE
     4 <> 3     TRUE
     4 <> NULL  UNKNOWN   <-- one unknown poisons the whole AND chain
     ----------------------
     result:    UNKNOWN   -> row dropped
```

**How to avoid it:** use `NOT EXISTS` (NULL-safe by construction), or add `WHERE CustomerID IS NOT NULL` to the subquery. This bug produces an empty report rather than an error, which is why it survives code review.

---

# Part D — Subqueries, CTEs, and windows

## 15. Subquery in `WHERE`

**IN:** Customers (4) + Orders (6)

```sql
SELECT Name FROM Customers
WHERE CustomerID IN (SELECT CustomerID FROM Orders WHERE Amount > 1500);
```

**OUT** (2 rows)

| Name |
|---|
| Meera |
| Raj |

**What happened:** Two customers returned, each exactly once.
**Why:** The inner query produced `{1, 2}` (order 501 → customer 1, order 503 → customer 2). `IN` is a membership test, so it can't duplicate the outer row.
**How:** Inner query first, then the outer filter:

```text
   step 1: SELECT CustomerID FROM Orders WHERE Amount > 1500
           501 (2000) -> 1
           503 (3000) -> 2
           result set: {1, 2}

   step 2: keep Customers whose ID is in {1, 2}
           Meera(1) YES   Raj(2) YES   Anita(3) no   Vikram(4) no
```

> Compare with the INNER JOIN in #11, which returned Meera **twice**. Same intent, different row counts — use a subquery/`EXISTS` when you're filtering, a join when you need columns from the other table.

---

## 16. CTE — naming an intermediate result

```sql
WITH customer_totals AS (
    SELECT CustomerID, SUM(Amount) AS total_spend, COUNT(*) AS order_count
    FROM Orders
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
)
SELECT c.Name, t.order_count, t.total_spend
FROM Customers c
LEFT JOIN customer_totals t ON t.CustomerID = c.CustomerID;
```

**The CTE alone produces** (3 rows):

| CustomerID | total_spend | order_count |
|---|---|---|
| 1 | 3500 | 2 |
| 2 | 3000 | 2 |
| 3 | 900 | 1 |

**OUT** (4 rows)

| Name | order_count | total_spend |
|---|---|---|
| Meera | 2 | 3500 |
| Raj | 2 | 3000 |
| Anita | 1 | 900 |
| Vikram | *NULL* | *NULL* |

**What happened:** Every customer appears exactly **once**, with their totals attached. No fan-out.
**Why:** Aggregating *before* joining reduces Orders to one row per customer, so the join is one-to-one.
**How:** This is the standard fix for the double-counting problem in #11:

```text
   WRONG:  join first (5 rows, Meera twice), then aggregate  -> customer values double-counted
   RIGHT:  aggregate first (1 row per customer), then join   -> each customer counted once
```

Raj's `total_spend` is 3000, not NULL — `SUM` skipped his NULL amount but still summed order 503. Vikram's NULL comes from the LEFT JOIN finding nothing; wrap in `COALESCE(t.total_spend, 0)` to show 0.

---

## 17. Window function — aggregate *without* collapsing

> Full treatment: [SQL Window Functions](14_SQL_Window_Functions.md).

```sql
SELECT OrderID, Status, Amount,
       SUM(Amount) OVER (PARTITION BY Status)                          AS status_total,
       ROW_NUMBER() OVER (PARTITION BY Status ORDER BY Amount DESC)    AS rn,
       LAG(Amount)  OVER (ORDER BY OrderDate)                          AS prev_amount
FROM Orders;
```

**OUT** (6 rows — every input row survives)

| OrderID | Status | Amount | status_total | rn | prev_amount |
|---|---|---|---|---|---|
| 501 | Shipped | 2000 | 4200 | 1 | *NULL* |
| 502 | Shipped | 1500 | 4200 | 2 | 2000 |
| 506 | Shipped | 700 | 4200 | 3 | *NULL* |
| 503 | Pending | 3000 | 3000 | 1 | 1500 |
| 505 | Pending | *NULL* | 3000 | 2 | 900 |
| 504 | Cancelled | 900 | 900 | 1 | 3000 |

**What happened:** 6 rows in, **6 rows out** — with the group total attached to each one. Compare `GROUP BY` in #9, which returned 3 rows and destroyed the detail.
**Why:** A window function *annotates*; `GROUP BY` *collapses*. Windows are the only way to show detail and summary on the same row.
**How:** Partition, order within each partition, then compute per row:

```text
   GROUP BY :  6 rows  ->  3 rows   (detail destroyed)
   OVER ()   :  6 rows  ->  6 rows   (detail preserved + summary added)
```

Two NULL notes: `prev_amount` for order 506 is NULL because the row before it by date (505) has a NULL amount — `LAG` faithfully returns the value it finds. And order 501 has no previous row at all.

---

## 18. `UNION` vs `UNION ALL` — stacking results

```sql
SELECT City FROM Customers
UNION
SELECT 'Mumbai';
```

**OUT** (4 rows)

| City |
|---|
| Chennai |
| Hyderabad |
| Mumbai |
| Pune |

```sql
SELECT City FROM Customers
UNION ALL
SELECT 'Mumbai';
```

**OUT** (5 rows)

| City |
|---|
| Hyderabad |
| Pune |
| Chennai |
| Hyderabad |
| Mumbai |

**What happened:** `UNION` returned 4 rows, `UNION ALL` returned 5. The duplicate Hyderabad survived only in `UNION ALL`.
**Why:** `UNION` **deduplicates**; `UNION ALL` simply concatenates.
**How:** Deduplication requires a sort or hash of the combined set — real CPU work, and it's why `UNION` output often comes back sorted (a side effect, never something to rely on).

> **Default to `UNION ALL`.** Use plain `UNION` only when you actually need duplicates removed. On large tables the difference is substantial, and stacking daily partitions — where duplicates are impossible by construction — is the classic case where `UNION` wastes an entire sort.

---

# Part E — Changing data

## 19. `INSERT` — add rows

**BEFORE:** Orders (6 rows)

```sql
INSERT INTO Orders (OrderID, CustomerID, OrderDate, Amount, Status)
VALUES (507, 4, '2026-03-25', 1200, 'Pending');
```

**AFTER** (7 rows)

| OrderID | CustomerID | OrderDate | Amount | Status |
|---|---|---|---|---|
| 501 | 1 | 2026-01-10 | 2000 | Shipped |
| 502 | 1 | 2026-02-14 | 1500 | Shipped |
| 503 | 2 | 2026-02-20 | 3000 | Pending |
| 504 | 3 | 2026-03-01 | 900 | Cancelled |
| 505 | 2 | 2026-03-15 | *NULL* | Pending |
| 506 | *NULL* | 2026-03-20 | 700 | Shipped |
| **507** | **4** | **2026-03-25** | **1200** | **Pending** |

**What happened:** One row added. Vikram now has an order — so the joins in #11–#14 would all return different results.
**Why:** `INSERT` appends; it never modifies existing rows.
**How:** The engine writes the row, updates every index on the table, and checks constraints. **`CustomerID = 4` had to exist in Customers** or a foreign key would reject the insert ([keys](07_SQL_Keys_and_Joins.md)).

> Run this statement twice and you get a primary-key violation on `OrderID = 507` — which is exactly why pipelines need [idempotent](15_SQL_Stored_Procedures_and_Programmability.md) load patterns rather than bare inserts.

---

## 20. `UPDATE` — change existing rows

**BEFORE** (the Pending rows)

| OrderID | Amount | Status |
|---|---|---|
| 503 | 3000 | Pending |
| 505 | *NULL* | Pending |

```sql
UPDATE Orders
SET Status = 'Shipped'
WHERE Status = 'Pending' AND Amount > 1000;
```

**AFTER**

| OrderID | Amount | Status |
|---|---|---|
| 503 | 3000 | **Shipped** |
| 505 | *NULL* | Pending ← unchanged |

**What happened:** 1 row updated, not 2.
**Why:** Order 505's `Amount > 1000` is unknown (NULL), so the `WHERE` didn't select it — the same three-valued logic as #3, now silently deciding which rows get written.
**How:** `UPDATE` runs `WHERE` first to select rows, then writes. Row count never changes.

> **The unforgiving version:** omit the `WHERE` and `UPDATE Orders SET Status = 'Shipped'` changes **every row in the table** with no confirmation. Always `SELECT` with your `WHERE` clause first to see what you're about to hit, and run it inside a transaction you can roll back.

---

## 21. `DELETE` vs `TRUNCATE`

```sql
DELETE FROM Orders WHERE Status = 'Cancelled';
```

**AFTER:** 5 rows — order 504 removed, everything else untouched.

```sql
TRUNCATE TABLE Orders;
```

**AFTER:** **0 rows.** The table still exists, with all its columns and indexes — but it's empty.

| | `DELETE` | `TRUNCATE` |
|---|---|---|
| Can filter with `WHERE`? | Yes | **No** — all or nothing |
| Logging | Per row | Per page — far faster |
| Fires triggers? | Yes | **No** |
| Resets `IDENTITY`? | No | **Yes** |
| Rollback-able? | Yes | Yes (in SQL Server, inside a transaction) |
| Blocked by an inbound foreign key? | Only for referenced rows | **Always**, even if no rows reference it |

**Why the difference:** `DELETE` is DML — it processes rows individually, logging each one. `TRUNCATE` is DDL — it deallocates the table's data pages wholesale without looking at rows at all. That's why it's dramatically faster and why it can't fire row-level triggers.

---

## 22. `MERGE` — insert and update in one statement (upsert)

**TARGET — Customers** (4 rows)

| CustomerID | Name | City |
|---|---|---|
| 1 | Meera | Hyderabad |
| 2 | Raj | Pune |
| 3 | Anita | Chennai |
| 4 | Vikram | Hyderabad |

**SOURCE — Customers_Staging** (2 rows)

| CustomerID | Name | City |
|---|---|---|
| 3 | Anita | **Bengaluru** ← moved |
| 5 | **Priya** | Delhi ← brand new |

```sql
MERGE INTO Customers AS tgt
USING Customers_Staging AS src
    ON tgt.CustomerID = src.CustomerID
WHEN MATCHED AND tgt.City <> src.City THEN
    UPDATE SET tgt.City = src.City, tgt.Name = src.Name
WHEN NOT MATCHED BY TARGET THEN
    INSERT (CustomerID, Name, City) VALUES (src.CustomerID, src.Name, src.City);
```

**AFTER** (5 rows)

| CustomerID | Name | City | |
|---|---|---|---|
| 1 | Meera | Hyderabad | untouched |
| 2 | Raj | Pune | untouched |
| 3 | Anita | **Bengaluru** | **UPDATED** |
| 4 | Vikram | Hyderabad | untouched |
| **5** | **Priya** | **Delhi** | **INSERTED** |

**What happened:** One row updated, one inserted, two left alone — in a single statement and a single pass.
**Why:** `MERGE` joins source to target on the key, then routes each row by whether it matched.
**How:**

```text
   src 3  ->  matches tgt 3   ->  WHEN MATCHED         ->  UPDATE
   src 5  ->  matches nothing ->  WHEN NOT MATCHED     ->  INSERT
   tgt 1,2,4 -> not in source ->  no clause applies    ->  untouched
```

**Why data engineers care:** this is the shape of every incremental load and every SCD Type 2 dimension update. Delta Lake's `MERGE INTO` is the same statement with the same semantics on a lakehouse table.

> **Two cautions.** The source must have **one row per key** — duplicates make `MERGE` throw or write non-deterministically. And `WHEN NOT MATCHED BY SOURCE THEN DELETE` will delete target rows absent from the source, which is correct for a full snapshot and catastrophic for an incremental batch.

---

# Part F — Structure and safety

## 23. `ALTER TABLE ADD COLUMN` — what happens to existing rows

**BEFORE:** Customers (4 rows, 4 columns)

```sql
ALTER TABLE Customers ADD Country VARCHAR(50);
```

**AFTER** (4 rows, 5 columns)

| CustomerID | Name | City | SignupDate | Country |
|---|---|---|---|---|
| 1 | Meera | Hyderabad | 2025-11-02 | *NULL* |
| 2 | Raj | Pune | 2026-01-15 | *NULL* |
| 3 | Anita | Chennai | 2026-02-20 | *NULL* |
| 4 | Vikram | Hyderabad | 2026-03-05 | *NULL* |

**What happened:** Every existing row got NULL in the new column. Row count unchanged.
**Why:** Existing rows have no value for a column that didn't exist when they were written, and NULL is SQL's representation of "no value."
**How:** Adding a **nullable** column is a metadata-only change in modern engines — instant, regardless of table size. Adding a **`NOT NULL` column with a default** may have to rewrite every row, which on a billion-row table is an outage. That difference is why schema migrations are planned rather than typed ad hoc ([DDL](04_SQL_DDL.md)).

---

## 24. Views — a saved query, not a saved result

```sql
CREATE VIEW v_ShippedOrders AS
SELECT OrderID, CustomerID, Amount FROM Orders WHERE Status = 'Shipped';

SELECT * FROM v_ShippedOrders;
```

**OUT** (3 rows)

| OrderID | CustomerID | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 506 | *NULL* | 700 |

Now change the underlying table:

```sql
UPDATE Orders SET Status = 'Shipped' WHERE OrderID = 503;
SELECT * FROM v_ShippedOrders;      -- same view, no redefinition
```

**OUT** (4 rows)

| OrderID | CustomerID | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 503 | 2 | 3000 |
| 506 | *NULL* | 700 |

**What happened:** The view's output changed without touching the view.
**Why:** A view stores **the query text**, not rows. Every `SELECT` from it re-runs that query against current data.
**How:** The engine substitutes the view definition into your query and optimizes them together, as if you'd typed the subquery yourself.

> A [materialized/indexed view](10_SQL_Views.md) is the opposite trade: it *does* store results, so reads are fast, but the data is only as fresh as the last refresh.

---

## 25. Transactions — making changes provisional

**BEFORE:** Orders (6 rows)

```sql
BEGIN TRANSACTION;

    DELETE FROM Orders WHERE Status = 'Cancelled';
    SELECT COUNT(*) FROM Orders;        -- 5  (visible to THIS session only)

ROLLBACK TRANSACTION;

SELECT COUNT(*) FROM Orders;            -- 6  (the delete never happened)
```

**What happened:** Inside the transaction the table looked like 5 rows. After the rollback it's 6 again.
**Why:** Until `COMMIT`, changes are **provisional**. `ROLLBACK` discards them entirely.
**How:** The engine writes changes to the transaction log first and holds locks; a rollback replays the log backwards to undo them. Other sessions never saw the 5-row state at all (at default isolation) — see [transactions and isolation levels](12_SQL_DCL_TCL.md).

> This is the safety net for every risky `UPDATE` or `DELETE`: wrap it, run your `SELECT` to verify the result, then decide between `COMMIT` and `ROLLBACK`. Note that some engines (PostgreSQL, and Delta/Spark) behave differently — Delta has no interactive multi-statement transaction, but each write is atomic on its own.

---

# The summary table — how each operation changes row count

The single most useful thing to internalize. When a result has the wrong number of rows, this table tells you which operation to suspect.

| Operation | Rows out, relative to rows in | Watch for |
|---|---|---|
| `SELECT` (columns) | **Identical** | Never changes row count |
| `WHERE` | Fewer or equal | NULLs fail *every* comparison and drop out |
| `DISTINCT` | Fewer or equal | Deduplicates on **all** selected columns |
| `ORDER BY` | **Identical** | Only reorders; NULL placement is dialect-specific |
| `LIMIT` / `TOP n` | At most n | Meaningless without `ORDER BY` |
| `GROUP BY` | **Collapses** to one row per group | Non-grouped columns cease to exist |
| `HAVING` | Fewer or equal **groups** | Runs after aggregation, unlike `WHERE` |
| Window function | **Identical** | Adds columns, never rows |
| `INNER JOIN` | Fewer **or more** | Both filters *and* multiplies (fan-out) |
| `LEFT JOIN` | ≥ left row count | Can still multiply if the right side matches many |
| `FULL OUTER JOIN` | ≥ both counts | The only join that loses nothing |
| `CROSS JOIN` | left × right | 4 × 6 = 24 here; catastrophic at scale |
| `UNION` | ≤ sum of both | Pays for a dedupe sort |
| `UNION ALL` | **Exactly** the sum | Almost always what you want |
| `EXISTS` / `IN` (subquery) | Fewer or equal | Filters without duplicating, unlike a join |
| `INSERT` | +n | Re-running duplicates unless made idempotent |
| `UPDATE` | **Identical** | No `WHERE` = every row in the table |
| `DELETE` | Fewer | Fires triggers, logs per row |
| `TRUNCATE` | **0** | No `WHERE`, no triggers, resets identity |
| `MERGE` | ≥ target count | Duplicate source keys are an error |

**The three rules behind almost every surprise in this file:**

1. **NULL is not a value — it's the absence of one.** It fails every comparison including `= NULL`, quietly falls through `CASE` to `ELSE`, is skipped by `SUM`/`AVG`/`COUNT(col)`, and poisons `NOT IN`.
2. **Joins both filter and multiply.** An inner join can return fewer rows than either input *and* more than both.
3. **The clause order isn't the execution order.** `WHERE` runs before `GROUP BY`, which runs before `HAVING` and `SELECT`, which run before `ORDER BY`. That's why you can't filter on an alias or a window function in `WHERE`.

---

## Further Learning — Docs & Videos

**Documentation**
- SQL tutorial with runnable examples (W3Schools): https://www.w3schools.com/sql/
- Logical query processing order (SQL Server): https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql
- NULL handling and three-valued logic (PostgreSQL): https://www.postgresql.org/docs/current/functions-comparison.html

**Videos**
- SQL joins visualized with real tables: https://www.youtube.com/results?search_query=sql+joins+visualized+examples
- NULL behaviour in SQL explained: https://www.youtube.com/results?search_query=sql+null+behaviour+explained
