# SQL Keys and Joins

## Why this file exists

[02_SQL_Database.md](02_SQL_Database.md) showed one table (Employee). In real systems, data is split across *many* tables, and you need a way to connect them back together. That connection relies on **keys** and **joins**.

Analogy: imagine a filing cabinet with one drawer for Customers and a separate drawer for Orders. Instead of re-writing a customer's full name and address on every single order form, each order form just references a Customer ID. To see a customer's full order history, you match the ID on the order form to the ID in the customer drawer. That matching is exactly what a join does.

---

## Primary Key

A **primary key** is the column that uniquely identifies each row in a table. No two rows can have the same value, and it can never be empty.

Customer Table

| CustomerID (primary key) | Name | City |
|---|---|---|
| 1 | Meera | Hyderabad |
| 2 | Raj | Pune |

`CustomerID` is the primary key — it's how every other table will refer to "this exact customer."

---

## Foreign Key

A **foreign key** is a column in one table that points to the primary key of another table.

Orders Table

| OrderID | CustomerID (foreign key) | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 503 | 2 | 3000 |

`CustomerID` in the Orders table isn't the order's own identity — it's a pointer back to the Customer table. This is how the database knows order 501 belongs to Meera without repeating her name and city on every row.

---

## Why not just repeat the data everywhere?

Without keys, every order row would need to repeat the customer's name, city, and every other detail. That causes two problems:

- **Wasted space** — the same customer details copied hundreds of times.
- **Inconsistency** — if Meera moves to a new city, you'd have to find and update every single order row. Miss one, and now your data disagrees with itself.

Splitting data into separate tables connected by keys, and storing each fact only once, is called **normalization**.

---

## Joins

A **join** combines rows from two tables using a shared key — usually the primary key of one table matched against the foreign key of another.

```sql
SELECT
    Orders.OrderID,
    Customer.Name,
    Orders.Amount
FROM Orders
JOIN Customer
    ON Orders.CustomerID = Customer.CustomerID;
```

Result

| OrderID | Name | Amount |
|---|---|---|
| 501 | Meera | 2000 |
| 502 | Meera | 1500 |
| 503 | Raj | 3000 |

The query reunites data that normalization intentionally kept apart.

---

## Every join type — one example, every result

To show what each join actually does, the sample data below is deliberately *imperfect*, the way real data is. Two rows have no partner on the other side:

**Customer**

| CustomerID | Name | City |
|---|---|---|
| 1 | Meera | Hyderabad |
| 2 | Raj | Pune |
| 3 | **Anita** | Chennai |

→ *Anita has never placed an order.*

**Orders**

| OrderID | CustomerID | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 503 | 2 | 3000 |
| **504** | *NULL* | 900 |

→ *Order 504 is a guest checkout — it belongs to no customer.*

Every query below joins these two tables `ON o.CustomerID = c.CustomerID`. The only thing that changes is the join type — and each one gives a different answer, which is exactly the point.

---

### First: how a join actually matches rows

Before the join types diverge, they all do the same thing — compare rows and test a condition.

Conceptually, the engine lines up **every** left row against **every** right row and evaluates the `ON` condition. 3 customers × 4 orders = **12 candidate pairs**:

| # | Customer row | Order row | `o.CustomerID = c.CustomerID` | Match? |
|---|---|---|---|---|
| 1 | 1 Meera | 501 (cust 1) | `1 = 1` → true | ✅ |
| 2 | 1 Meera | 502 (cust 1) | `1 = 1` → true | ✅ |
| 3 | 1 Meera | 503 (cust 2) | `2 = 1` → false | ❌ |
| 4 | 1 Meera | 504 (cust NULL) | `NULL = 1` → **unknown** | ❌ |
| 5 | 2 Raj | 501 (cust 1) | `1 = 2` → false | ❌ |
| 6 | 2 Raj | 502 (cust 1) | `1 = 2` → false | ❌ |
| 7 | 2 Raj | 503 (cust 2) | `2 = 2` → true | ✅ |
| 8 | 2 Raj | 504 (cust NULL) | `NULL = 2` → **unknown** | ❌ |
| 9 | 3 Anita | 501 (cust 1) | `1 = 3` → false | ❌ |
| 10 | 3 Anita | 502 (cust 1) | `1 = 3` → false | ❌ |
| 11 | 3 Anita | 503 (cust 2) | `2 = 3` → false | ❌ |
| 12 | 3 Anita | 504 (cust NULL) | `NULL = 3` → **unknown** | ❌ |

Three pairs matched. Two rows matched **nothing at all**: *Anita* (pairs 9–12 all failed) and *order 504* (pairs 4, 8, 12 all failed).

That is the entire mechanism. Every join type is just a different answer to one question:

> **What should happen to the rows that matched nothing?**

| Join type | The 3 matched pairs | Unmatched **left** (Anita) | Unmatched **right** (504) | Rows out |
|---|---|---|---|---|
| `INNER JOIN` | kept | dropped | dropped | 3 |
| `LEFT JOIN` | kept | **kept**, NULL-padded | dropped | 4 |
| `RIGHT JOIN` | kept | dropped | **kept**, NULL-padded | 4 |
| `FULL OUTER JOIN` | kept | **kept**, NULL-padded | **kept**, NULL-padded | 5 |
| `CROSS JOIN` | — the `ON` test never runs; all 12 pairs are returned | | | 12 |

Two things to notice right now, because they cause most join bugs:

- **Meera appears twice** in the matched pairs. A left row is repeated once per matching right row — that's **fan-out**, and it's why totals double after someone "just adds a join."
- **`NULL = 1` is not false, it's *unknown*** — and a join keeps a pair only when the condition is *true*. So order 504 matches nothing, not even other NULL rows: `NULL = NULL` is unknown too.

> Real engines don't literally build all 12 pairs — they use hash tables or index seeks ([see the algorithms below](#join-algorithms--what-the-engine-actually-runs)). But the *result* is identical to this model, which is why it's the right one to reason with.

### The quick map

| Join | Plain meaning | Rows from our example |
|---|---|---|
| `INNER JOIN` | Only rows that match on **both** sides | 3 |
| `LEFT [OUTER] JOIN` | **All** left rows + matches from the right | 4 |
| `RIGHT [OUTER] JOIN` | **All** right rows + matches from the left | 4 |
| `FULL [OUTER] JOIN` | **All** rows from both sides | 5 |
| `CROSS JOIN` | Every left row paired with every right row | 12 |
| **SEMI** join (`EXISTS`) | Left rows that **have** a match — no duplication, no right columns | 2 |
| **ANTI** join (`NOT EXISTS`) | Left rows that have **no** match | 1 |
| **SELF** join | A table joined to itself | varies |
| **Non-equi / theta** join | Match on `<`, `>`, `BETWEEN` — not `=` | varies |
| `LATERAL` / `APPLY` | Right side is a subquery that runs **per left row** | varies |

---

### 1. INNER JOIN — "only the rows that match"

**How it matches**

```text
  CUSTOMER (left)                     ORDERS (right)
  ---------------------               ------------------------------
  1  Meera   Hyderabad  ---------->   501   CustomerID=1      2000     kept
                        ---------->   502   CustomerID=1      1500     kept
  2  Raj     Pune       ---------->   503   CustomerID=2      3000     kept

  3  Anita   Chennai         (x)      nothing points back to 3         DROPPED
                             (x)      504   CustomerID=NULL    900     DROPPED
```

**The query**

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customer c
INNER JOIN Orders o ON o.CustomerID = c.CustomerID;   -- INNER is the default; "JOIN" alone means this
```

**What comes out**

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |

Notice **Meera is listed twice** — once per matching order. And both orphans are gone: an inner join is *simultaneously a join and a filter*, and that second job is what surprises people.

**Use it when:** you only care about complete pairs — "revenue per customer, for customers who actually bought something." It's the right default for fact-to-dimension joins in a well-loaded warehouse, where every key is guaranteed to resolve.

---

### 2. LEFT OUTER JOIN — "keep everything on the left, matched or not"

**How it matches**

```text
  CUSTOMER (left)                     ORDERS (right)
  ---------------------               ------------------------------
  1  Meera   Hyderabad  ---------->   501   CustomerID=1      2000     kept
                        ---------->   502   CustomerID=1      1500     kept
  2  Raj     Pune       ---------->   503   CustomerID=2      3000     kept
  3  Anita   Chennai    ---------->   (NULL, NULL)   <-- invented      kept
                                       by the join, not stored

                             (x)      504   CustomerID=NULL    900     DROPPED
```

**The query**

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customer c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID;    -- LEFT JOIN == LEFT OUTER JOIN
```

**What comes out**

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Anita | *NULL* | *NULL* |

Anita survives, padded with NULLs. Those NULLs aren't stored anywhere — the join *manufactures* them to mean "nothing matched."

**Use it when:** the left table is the population you must report on completely. "All customers, with their spend (zero if none)", "all products, with stock levels", "all dates in the calendar, with sales." This is the most common join in analytics, because a report that silently drops the customers with no activity answers a different question than the one that was asked.

> Pair it with `COALESCE(o.Amount, 0)` — otherwise Anita's total shows as blank rather than 0, and `AVG` skips her entirely instead of counting her as a zero.

---

### 3. RIGHT OUTER JOIN — the mirror image

**How it matches**

```text
  CUSTOMER (left)                     ORDERS (right)
  ---------------------               ------------------------------
  1  Meera   Hyderabad  ---------->   501   CustomerID=1      2000     kept
                        ---------->   502   CustomerID=1      1500     kept
  2  Raj     Pune       ---------->   503   CustomerID=2      3000     kept
  (NULL, NULL)          <----------   504   CustomerID=NULL    900     kept
   ^-- invented by the join

  3  Anita   Chennai         (x)      nothing points back to 3         DROPPED
```

**The query**

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customer c
RIGHT JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**What comes out**

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| *NULL* | 504 | 900 |

Now every **order** survives, including orphaned guest order 504, and the *customer* side is NULL-padded instead.

**Use it when:** honestly — rarely. `A RIGHT JOIN B` is identical to `B LEFT JOIN A`, and most teams standardize on LEFT so that reading a long query means tracking one direction only. RIGHT JOIN earns its place mainly when you're appending a table to the end of an existing chain and don't want to rewrite the whole FROM clause.

---

### 4. FULL OUTER JOIN — "keep everything from both sides"

**How it matches**

```text
  CUSTOMER (left)                     ORDERS (right)
  ---------------------               ------------------------------
  1  Meera   Hyderabad  ---------->   501   CustomerID=1      2000     kept
                        ---------->   502   CustomerID=1      1500     kept
  2  Raj     Pune       ---------->   503   CustomerID=2      3000     kept
  3  Anita   Chennai    ---------->   (NULL, NULL)   <-- invented      kept
  (NULL, NULL)          <----------   504   CustomerID=NULL    900     kept
   ^-- invented

  nothing is dropped
```

**The query**

```sql
SELECT c.Name, o.OrderID, o.Amount
FROM Customer c
FULL OUTER JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**What comes out**

| Name | OrderID | Amount |
|---|---|---|
| Meera | 501 | 2000 |
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Anita | *NULL* | *NULL* |
| *NULL* | 504 | 900 |

Both orphans survive — the unmatched customer *and* the unmatched order. This is the only join where every input row is guaranteed to appear somewhere in the output.

**Use it when:** reconciling two sources that are each supposed to be complete. "Which records are in the source system but not the warehouse, and vice versa?" is a FULL OUTER JOIN, and it's the backbone of data-quality and migration-validation queries. Also handy for merging two partially-overlapping metric sets into one report.

> **Dialect note:** MySQL has no `FULL OUTER JOIN` — emulate it with `LEFT JOIN ... UNION ... RIGHT JOIN`. SQL Server, PostgreSQL, Oracle, Snowflake, Databricks, and Synapse all support it natively.

---

### 5. CROSS JOIN — every combination (Cartesian product)

**How it matches** — it doesn't. There is no `ON` clause, so nothing is tested; every left row is paired with every right row.

```text
  Meera   x   501, 502, 503, 504   ->   4 rows
  Raj     x   501, 502, 503, 504   ->   4 rows
  Anita   x   501, 502, 503, 504   ->   4 rows
                                      ----------
                                        12 rows      (3 customers x 4 orders)
```

**The query**

```sql
SELECT c.Name, o.OrderID
FROM Customer c
CROSS JOIN Orders o;          -- no ON clause at all
```

**What comes out** (first 6 of 12 rows)

| Name | OrderID |
|---|---|
| Meera | 501 |
| Meera | 502 |
| Meera | 503 |
| Meera | 504 |
| Raj | 501 |
| … | … |

Most of these pairings are meaningless here — Meera has nothing to do with order 503. That's the point: a cross join asserts no relationship at all.

**Use it when:** you genuinely want all combinations —

- **Generating a dense grid** — every store × every date, so a report shows zero-sales days instead of skipping them (then LEFT JOIN the actuals onto that grid).
- **Applying one scalar to every row** — `CROSS JOIN (SELECT MAX(load_date) AS latest FROM Runs) r`, a clean single-row broadcast.
- **Building test data**, or expanding a range of numbers/dates.

**The danger:** the *accidental* cross join. Forget the `ON` condition (or write `ON 1=1`) and 100k rows × 100k rows is 10 billion rows — a query that runs until the cluster dies. This is precisely why explicit `JOIN ... ON` syntax replaced old comma joins: the syntax makes a forgotten condition obvious.

---

### 6. SEMI JOIN — "does a match exist?" (filter, don't join)

A semi join answers *"which left rows have at least one match?"* and returns **only left columns, with no row multiplication**.

**How it matches** — the moment a left row finds *one* match, it's kept and the search stops. Extra matches change nothing.

```text
  1  Meera  ---> 501   found a match  --+
            ---> 502   (also matches)   |--> Meera is output ONCE, not twice
  2  Raj    ---> 503   found a match  ----> Raj is output once
  3  Anita       (x)   zero matches   ----> excluded

  the right-side columns are never returned -- only used to answer yes/no
```

**The query**

```sql
SELECT c.CustomerID, c.Name
FROM Customer c
WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID);
```

**What comes out**

| CustomerID | Name |
|---|---|
| 1 | Meera |
| 2 | Raj |

Compare against the INNER JOIN in #1, which returned **Meera twice**. The semi join returns her **once**. That difference is the entire reason semi joins exist.

**Use it when:** you're filtering, not enriching — "customers who have ordered", "products appearing in any active promotion", "accounts with a failed login in the last hour". Any time you catch yourself adding `SELECT DISTINCT` to undo the fan-out an inner join just caused, what you wanted was a semi join.

**Why `EXISTS` beats `IN (subquery)`:** identical intent, but `IN` carries a nasty [NULL trap](09_SQL_Subqueries.md) — if the subquery returns even one NULL, `NOT IN` returns no rows at all. `EXISTS` is NULL-safe and usually plans at least as well.

Some engines expose the operation directly: `FROM Customer c LEFT SEMI JOIN Orders o ON o.CustomerID = c.CustomerID` (Spark/Databricks, Hive).

---

### 7. ANTI JOIN — "find what's missing"

The exact complement of the semi join: left rows with **no** match.

**How it matches**

```text
  1  Meera  ---> 501, 502   has matches  ----> excluded
  2  Raj    ---> 503        has matches  ----> excluded
  3  Anita       (x)        zero matches ----> KEPT   <-- the only survivor

  flip the two tables around and the same join finds order 504,
  the row whose foreign key points at nobody
```

**The query**

```sql
-- Preferred: says exactly what it means, and is NULL-safe
SELECT c.CustomerID, c.Name
FROM Customer c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID);

-- Equivalent classic form: LEFT JOIN, then keep only the rows that failed to match
SELECT c.CustomerID, c.Name
FROM Customer c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID
WHERE o.CustomerID IS NULL;         -- must test a NOT NULL column from the right table
```

**What comes out**

| CustomerID | Name |
|---|---|
| 3 | Anita |

The second form is worth tracing: the LEFT JOIN produces the 4 rows from #2, and `WHERE o.CustomerID IS NULL` then throws away every row that *did* match — leaving only the NULL-padded one the join invented.

**Use it when:** this is the workhorse of data engineering.

- **Data quality** — "fact rows whose foreign key resolves to no dimension row", the orphan test every pipeline should run.
- **Incremental loads** — "source rows not yet in the target", the insert half of an upsert.
- **Business questions framed as absence** — churn candidates, unconverted signups, unpaid invoices.

> The `IS NULL` form only works if you test a column that can never legitimately be NULL in the right table. Test a nullable column and you conflate "no match" with "matched, but that value was NULL" — a silent, ugly bug. `NOT EXISTS` sidesteps it entirely.

---

### 8. Symmetric difference — "in one side or the other, but not both"

**How it matches** — run a FULL OUTER JOIN, then delete the middle.

```text
  FULL OUTER JOIN produces 5 rows:

     Meera + 501    <- matched, filtered OUT
     Meera + 502    <- matched, filtered OUT
     Raj   + 503    <- matched, filtered OUT
     Anita + NULL   <- unmatched left    KEPT
     NULL  + 504    <- unmatched right   KEPT
```

**The query**

```sql
SELECT c.CustomerID, c.Name, o.OrderID
FROM Customer c
FULL OUTER JOIN Orders o ON o.CustomerID = c.CustomerID
WHERE c.CustomerID IS NULL OR o.OrderID IS NULL;
```

**What comes out**

| CustomerID | Name | OrderID |
|---|---|---|
| 3 | Anita | *NULL* |
| *NULL* | *NULL* | 504 |

Everything that failed to reconcile, from both directions, in one result set.

**Use it when:** validating a migration or a sync. "Show me every record that exists on exactly one side" is the single query that proves two systems agree — and names every row where they don't.

---

### 9. SELF JOIN — a table joined to itself

Not a separate keyword: any join type where both sides are the *same* table, told apart by aliases. It's how you walk a hierarchy stored in one table.

**Employee**

| EmpID | Name | ManagerID |
|---|---|---|
| 1 | Meera | *NULL* |
| 2 | Raj | 1 |
| 3 | Anita | 1 |

**How it matches** — the same rows appear on both sides of the arrow, under two aliases:

```text
  e  (the employee side)              m  (the manager side)
  --------------------------          --------------------------
  2  Raj     ManagerID=1  ------->    1  Meera     EmpID=1
  3  Anita   ManagerID=1  ------->    1  Meera     EmpID=1
  1  Meera   ManagerID=NULL   (x)     nobody -- she is the top of the tree

  the join condition is  m.EmpID = e.ManagerID  -- not the primary key to itself
```

**The query**

```sql
SELECT e.Name AS employee, m.Name AS manager
FROM Employee e
LEFT JOIN Employee m ON m.EmpID = e.ManagerID;   -- LEFT, so the CEO isn't dropped
```

**What comes out**

| employee | manager |
|---|---|
| Meera | *NULL* |
| Raj | Meera |
| Anita | Meera |

**Use it when:** the relationship is between rows of the *same* entity — employee→manager, product→parent category, page→referring page. Also for **row-to-row comparison**: joining a table to itself on `t2.date = t1.date - 1` to compute day-over-day change (though a window function like `LAG` is usually cheaper and clearer for that).

> Use `LEFT` for hierarchies unless you deliberately want to drop the root — swap it for `INNER` above and Meera vanishes, silently losing the top of every tree.

---

### 10. Equi join vs non-equi (theta) join — what the `ON` condition looks like

Everything so far matched with `=`. That's an **equi join** — the overwhelming majority of real joins, and the only kind an engine can hash.

A **non-equi join** (also *theta join*) matches on any other predicate: `<`, `>`, `BETWEEN`, `!=`, or a range overlap.

**DiscountTier**

| Tier | MinAmount | MaxAmount |
|---|---|---|
| Bronze | 0 | 1999 |
| Silver | 2000 | 2999 |
| Gold | 3000 | 999999 |

**How it matches** — not "is equal to" but "falls inside":

```text
  ORDERS (Amount)                     DISCOUNTTIER (a range, not a key)
  ---------------                     ---------------------------------
  504     900  --- falls inside --->  Bronze     0 .. 1999
  502    1500  --- falls inside --->  Bronze     0 .. 1999
  501    2000  --- falls inside --->  Silver  2000 .. 2999
  503    3000  --- falls inside --->  Gold    3000 .. 999999

  ON o.Amount BETWEEN t.MinAmount AND t.MaxAmount
```

**The query**

```sql
SELECT o.OrderID, o.Amount, t.Tier
FROM Orders o
JOIN DiscountTier t ON o.Amount BETWEEN t.MinAmount AND t.MaxAmount;
```

**What comes out**

| OrderID | Amount | Tier |
|---|---|---|
| 501 | 2000 | Silver |
| 502 | 1500 | Bronze |
| 503 | 3000 | Gold |
| 504 | 900 | Bronze |

Note that order 504 *does* appear here — it has no customer, but it does have an amount, and this join never looks at `CustomerID`.

**Use it when:** the match is a *range*, not an identity —

- **Banding/tiering** — amount → discount tier, score → grade, age → bracket.
- **Effective-dated lookups** — the defining pattern of SCD Type 2: `ON f.CustomerKey = d.CustomerKey AND f.OrderDate BETWEEN d.ValidFrom AND d.ValidTo`, which picks the version of the dimension that was current *when the fact happened*.
- **Interval overlap** — did these two sessions overlap in time?

> **Watch the gaps and overlaps.** If the tiers were `0–2000` and `2000–2999`, order 501 (exactly 2000) would match **both** and be counted twice. If they were `0–1999` and `2001–2999`, an order of exactly 2000 would match **neither** and silently disappear. Range tables need contiguous, non-overlapping bounds — a rule no `FOREIGN KEY` can enforce for you.

**The cost:** a non-equi join can't be hashed, so engines fall back to nested loops or a sort-merge over ranges, and the intermediate row count can explode. Keep the range table small (tier tables are tiny — that's why this pattern works), and in Spark/Databricks reach for **range join optimization** hints when both sides are large.

---

### 11. `USING` and `NATURAL JOIN` — shorthands, and when to avoid them

These don't change *which* rows match — they change how you *write* the condition, and what the output columns look like.

```sql
-- ON: explicit, always correct
SELECT * FROM Orders o JOIN Customer c ON o.CustomerID = c.CustomerID;

-- USING: shorthand when both columns share a name; also collapses them to one output column
SELECT * FROM Orders JOIN Customer USING (CustomerID);

-- NATURAL JOIN: joins on EVERY identically-named column, implicitly
SELECT * FROM Orders NATURAL JOIN Customer;
```

**The output difference** — same rows, different columns:

`SELECT *` with `ON` returns `CustomerID` **twice**, once from each table:

| OrderID | CustomerID | Amount | CustomerID | Name | City |
|---|---|---|---|---|---|
| 501 | 1 | 2000 | 1 | Meera | Hyderabad |

`SELECT *` with `USING (CustomerID)` merges them into **one** column:

| CustomerID | OrderID | Amount | Name | City |
|---|---|---|---|---|
| 1 | 501 | 2000 | Meera | Hyderabad |

That's the real convenience of `USING`, and why it's popular for ad-hoc analysis. It requires the column to be named identically on both sides.

**`NATURAL JOIN` is best avoided in production code.** It infers the join keys from whichever column names happen to match *today*:

```text
  today:      shared column names = {CustomerID}
              -> joins ON CustomerID              -> 3 rows, correct

  someone adds updated_at to BOTH tables:
              shared column names = {CustomerID, updated_at}
              -> joins ON CustomerID AND updated_at   -> 0 rows, no error, no warning
```

A routine, unrelated schema change silently rewrites your join condition. Explicit `ON` is a few more characters and cannot break this way.

> Also legacy: the **comma join**, `FROM Orders o, Customer c WHERE o.CustomerID = c.CustomerID`. Functionally an inner join, but the join condition sits in `WHERE` mixed in with real filters, and forgetting it produces a silent 12-row cross join rather than a syntax error. Explicit `JOIN ... ON` won for exactly that reason.

---

### 12. `LATERAL` / `APPLY` — a join whose right side runs per left row

An ordinary join's right side is a fixed table. A **lateral join** lets the right side be a subquery that can *reference the current left row* — effectively a correlated join.

**How it matches** — the subquery is re-executed once per left row, with that row's values substituted in:

```text
  c = 1 Meera  -->  run:  SELECT ... WHERE CustomerID = 1 ORDER BY OrderID DESC LIMIT 1
                    got:  502  (1500)          <- 502 beats 501, most recent wins

  c = 2 Raj    -->  run:  SELECT ... WHERE CustomerID = 2 ORDER BY OrderID DESC LIMIT 1
                    got:  503  (3000)

  c = 3 Anita  -->  run:  SELECT ... WHERE CustomerID = 3 ORDER BY OrderID DESC LIMIT 1
                    got:  (no rows)            <- LEFT/OUTER form keeps her, NULL-padded
                                                  CROSS APPLY would drop her
```

**The query**

```sql
-- PostgreSQL / Oracle / standard SQL
SELECT c.Name, recent.OrderID, recent.Amount
FROM Customer c
LEFT JOIN LATERAL (
    SELECT o.OrderID, o.Amount
    FROM Orders o
    WHERE o.CustomerID = c.CustomerID     -- references the outer row: only legal because of LATERAL
    ORDER BY o.OrderID DESC
    LIMIT 1
) recent ON TRUE;

-- SQL Server spelling: CROSS APPLY (= inner) / OUTER APPLY (= left)
SELECT c.Name, recent.OrderID, recent.Amount
FROM Customer c
OUTER APPLY (SELECT TOP 1 o.OrderID, o.Amount
             FROM Orders o WHERE o.CustomerID = c.CustomerID
             ORDER BY o.OrderID DESC) recent;
```

**What comes out**

| Name | OrderID | Amount |
|---|---|---|
| Meera | 502 | 1500 |
| Raj | 503 | 3000 |
| Anita | *NULL* | *NULL* |

One row per customer — Meera is **not** duplicated, because the subquery returned exactly one row for her. That's the difference from a plain LEFT JOIN, which would have given her both 501 and 502.

**Use it when:**

- **Top-N per group** — the most recent order per customer, the three highest-scoring attempts per student. (A `ROW_NUMBER()` window function does the same job; LATERAL often wins when N is small and the inner side is well indexed, because it can stop early.)
- **Calling a table-valued function per row**, or expanding a JSON/array column into rows alongside its parent (`CROSS JOIN LATERAL jsonb_array_elements(...)`, `CROSS APPLY OPENJSON(...)`).

---

### 13. ASOF join — nearest match in time

Specialist, but increasingly common in time-series and streaming work (Databricks, DuckDB, pandas, kdb+): match each left row to the **most recent right row at or before its timestamp**, instead of to an exact match.

**quotes**

| quote_time | symbol | price |
|---|---|---|
| 09:00:00 | ACME | 100 |
| 09:00:05 | ACME | 101 |
| 09:00:09 | ACME | 102 |

**trades**

| trade_time | symbol | qty |
|---|---|---|
| 09:00:03 | ACME | 10 |
| 09:00:07 | ACME | 5 |

**How it matches** — no timestamp is ever equal, so an equi join would return *nothing*. ASOF walks backwards to the last known value instead:

```text
  time ------>   09:00:00    09:00:03    09:00:05    09:00:07    09:00:09
                    |           |           |           |           |
  QUOTES           100          .          101          .          102
  TRADES            .        qty 10         .        qty 5          .
                              |                       |
                              +--> walk back to       +--> walk back to
                                   the last quote          the last quote
                                   at or before            at or before
                                   09:00:03  =>  100       09:00:07  =>  101

  rule: match the latest right row where quote_time <= trade_time
        (a plain equi join on timestamps would match nothing at all)
```

**The query**

```sql
-- Databricks SQL
SELECT t.trade_time, t.qty, q.price
FROM trades t
ASOF JOIN quotes q
  ON t.symbol = q.symbol AND t.trade_time >= q.quote_time;
```

**What comes out**

| trade_time | qty | price |
|---|---|---|
| 09:00:03 | 10 | 100 |
| 09:00:07 | 5 | 101 |

The 09:00:09 quote is never used — no trade happened at or after it.

**Use it when:** joining a trade to the prevailing price quote, a sensor reading to the last known calibration, or an event to the config that was live when it fired. It's expressible as a non-equi join plus `ROW_NUMBER()`, but far slower and much harder to read.

---

### Side by side: the same join, seven ways

One condition (`o.CustomerID = c.CustomerID`), one dataset, every result at a glance:

| | Meera+501 | Meera+502 | Raj+503 | Anita (no order) | 504 (no customer) | Rows |
|---|---|---|---|---|---|---|
| `INNER JOIN` | ✅ | ✅ | ✅ | — | — | 3 |
| `LEFT JOIN` | ✅ | ✅ | ✅ | ✅ NULL-padded | — | 4 |
| `RIGHT JOIN` | ✅ | ✅ | ✅ | — | ✅ NULL-padded | 4 |
| `FULL OUTER JOIN` | ✅ | ✅ | ✅ | ✅ NULL-padded | ✅ NULL-padded | 5 |
| semi (`EXISTS`) | ✅ *(Meera once)* | *collapsed* | ✅ | — | — | 2 |
| anti (`NOT EXISTS`) | — | — | — | ✅ | — | 1 |
| `CROSS JOIN` | *all 12 pairings, condition never tested* | | | | | 12 |

### Which join do I actually want?

| The question you're answering | The join |
|---|---|
| "Customers **and** their orders" (only those with orders) | `INNER JOIN` |
| "**All** customers, with orders where they exist" | `LEFT JOIN` |
| "**Every** record from both sides, reconciled" | `FULL OUTER JOIN` |
| "Customers **who have** ordered" (no duplicates, no order columns) | semi join — `EXISTS` |
| "Customers who have **never** ordered" | anti join — `NOT EXISTS` |
| "Rows that exist on **one side only**" | `FULL OUTER JOIN` + `WHERE ... IS NULL` |
| "**Every combination** of X and Y" | `CROSS JOIN` |
| "Each employee **and their manager**" (same table) | self join |
| "Which **band / tier / date range** does this value fall into?" | non-equi join (`BETWEEN`) |
| "The **most recent** child row per parent" | `LATERAL` / `APPLY`, or `ROW_NUMBER()` |
| "The **last known value** as of this timestamp" | `ASOF JOIN` |

**The one habit that prevents most join bugs:** before writing the join, say out loud which rows must survive. "All customers" → LEFT. "Only matched" → INNER. "Just checking existence" → EXISTS. The join type is a statement about your *population*, not merely about how to glue two tables together — pick it from the question, not from habit.

---

## Real World Example

An insurance company keeps:

- A **Policyholders** table (one row per person)
- A **Claims** table (one row per claim, referencing a Policyholder via a foreign key)

A claims officer never re-types a policyholder's full details onto every claim. They just reference the Policyholder ID, and a join pulls the full policyholder details back in whenever a report is generated. This is the same pattern behind almost every business system: banking, healthcare, retail, and HR.

---

## Join grain — the concept that prevents most join bugs

Every table has a **grain**: what one row represents (one customer / one order / one order *line*). Joins multiply rows when grains mismatch:

- one-to-one → row counts unchanged
- one-to-many (Customer→Orders) → customer data *repeats* per order — `SUM(customer.credit_limit)` is now wrong (fan-out double counting!)
- many-to-many → row explosion

Pro reflexes: state each table's grain before writing the join; check `COUNT(*)` before vs after; **pre-aggregate the many side to the join grain** when you need one row per key:

```sql
SELECT c.CustomerID, c.Name, o.total_amount
FROM Customer c
LEFT JOIN (SELECT CustomerID, SUM(Amount) AS total_amount
           FROM Orders GROUP BY CustomerID) o
  ON o.CustomerID = c.CustomerID;
```

## LEFT JOIN subtleties everyone hits

```sql
-- BUG: WHERE on the right table turns LEFT JOIN back into INNER JOIN
SELECT c.Name, o.Amount
FROM Customer c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID
WHERE o.Status = 'Shipped';          -- customers with no orders vanish (o.Status IS NULL fails the filter)

-- FIX: put right-table conditions in the ON clause
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID AND o.Status = 'Shipped';
```

This is the same trap from the other direction as the [anti join](#7-anti-join--find-whats-missing): `WHERE o.col IS NULL` *deliberately* keeps only unmatched rows, while `WHERE o.col = 'X'` *accidentally* discards them. One clause, two opposite intents — which is why right-table filters belong in `ON` unless you mean the anti-join.

## Join algorithms — what the engine actually runs

| Algorithm | How | Best when |
|---|---|---|
| **Nested loops** | For each outer row, seek the inner table | Small outer + indexed inner (OLTP point queries) |
| **Hash join** | Build hash table on smaller input, probe with larger | Large unsorted inputs (analytics default) |
| **Merge join** | Both inputs sorted on key, zip together | Pre-sorted/indexed inputs |

You don't pick these directly — but you *cause* them: bad statistics that underestimate rows send a million-row input into nested loops (the "query that ran fine yesterday" classic). Distributed engines add a location dimension: **broadcast vs shuffle joins** ([Spark join strategies](../../03_Programming/PySpark/Spark_Processing.md)).

---

## Natural vs surrogate keys — the design decision

| | Natural key (email, national ID, order no.) | Surrogate key (IDENTITY/sequence int) |
|---|---|---|
| Meaningful? | Yes — but meanings *change* (emails change, IDs get re-issued) | No — and that's the point |
| Stability | Fragile | Permanent |
| Join cost | Often wide strings | Narrow ints |

Mature designs: **surrogate primary key + unique constraint on the natural/business key**. In [warehouses](13_SQL_Warehouse.md) surrogates are mandatory — they're what makes SCD Type 2 history possible (same customer, multiple dimension rows, distinct surrogate keys — [OLAP dimensional modeling](../../01_Foundations/Fundamentals/02_OLAP_Storage.md)).

## Referential integrity: enforce, or trust the pipeline?

- OLTP: **enforce with FK constraints** — the database is the last line of defense against orphaned rows. (Note: FKs need supporting indexes; an unindexed FK makes parent deletes table-scan the child.)
- Warehouses/lakehouse: FKs are typically **declared but unenforced** (Synapse, Delta) — checking them on billion-row bulk loads would be ruinous. Integrity moves into the pipeline: load dimensions before facts, resolve unknown keys to a `-1 / 'Unknown'` dimension row, and **test** orphan counts (dbt tests, Delta constraints) instead of constraint-enforcing them.
- `ON DELETE CASCADE` is powerful and dangerous — one parent delete silently mowing down children is a favorite root cause; most teams prefer RESTRICT + explicit deletes.

## Normalization vs denormalization — the pendulum, honestly

- **3NF** for OLTP: one fact, one place; updates stay cheap and consistent ([normal forms](../../01_Foundations/Fundamentals/01_OLTP_Storage.md)).
- **Star schema** for analytics: intentional, *controlled* denormalization — dimensions repeat text so queries need one join, not seven.
- **One Big Table (OBT)** — fully pre-joined wide tables — increasingly common as the final BI layer on columnar engines (storage is cheap, joins aren't free); fed *from* a governed star, not instead of one.

The senior answer to "should we normalize?" is always: *for which workload, at which layer?*

## Field-tested gotchas

- Joining on NULLable columns: `NULL = NULL` is never true — rows with NULL keys silently drop from INNER JOINs (and match nothing in LEFT JOINs' right side).
- Mixed collations/types on join keys force conversions that kill index seeks ([implicit conversion](03_SQL_Data_Types.md)).
- Accidental cross join via a missed ON condition in old-style comma joins — one reason explicit `JOIN ... ON` syntax won.
- Chained LEFT JOINs where a middle join is INNER quietly re-filters everything to its left — audit join types when a "complete" list comes back short.

## Interview-grade Q&A

- *Name every join type you know.* INNER, LEFT/RIGHT/FULL OUTER, CROSS — plus the ones that aren't keywords in every dialect: SEMI (`EXISTS`), ANTI (`NOT EXISTS`), SELF, non-equi/theta, and LATERAL/APPLY. Naming the last group is what separates a memorized answer from a working one.
- *INNER JOIN vs `EXISTS` — when does it matter?* When the right side has multiple matches: the inner join duplicates the left row per match, `EXISTS` returns it once. If you're filtering rather than enriching, `EXISTS` is correct and needs no `DISTINCT`.
- *What's an anti join for?* Finding absence — orphaned fact rows, source rows not yet loaded, customers who never converted. `NOT EXISTS` over `NOT IN` (NULL trap) or `LEFT JOIN ... IS NULL`.
- *When would you actually use a FULL OUTER JOIN?* Reconciliation — comparing two supposedly-identical datasets and surfacing what's on one side only. Rare in reporting, common in data quality and migration validation.
- *Why avoid `NATURAL JOIN`?* It picks join keys from whatever column names currently match, so adding an unrelated `updated_at` to both tables silently changes the result with no error.
- *A report's totals doubled after adding a join — why?* Fan-out: joined a one-to-many at the wrong grain; pre-aggregate or fix the key.
- *LEFT JOIN + WHERE right.col = X returns fewer rows than expected — why?* The WHERE filters out the NULL (unmatched) rows; move the condition into ON.
- *Natural vs surrogate keys?* Surrogates for stability/joins, natural keys as unique constraints; surrogates required for dimension history.
- *How does a warehouse guarantee integrity without enforced FKs?* Load order, default 'Unknown' members, and automated orphan tests in the pipeline.

---

## Further Learning — Docs & Videos

**Documentation**
- SQL joins (W3Schools): https://www.w3schools.com/sql/sql_join.asp
- Primary/foreign keys (PostgreSQL): https://www.postgresql.org/docs/current/ddl-constraints.html
- Visual guide to SQL joins: https://www.atlassian.com/data/sql/sql-join-types-explained-visually

**Videos**
- SQL joins explained (INNER/LEFT/RIGHT/FULL): https://www.youtube.com/results?search_query=sql+joins+explained+inner+left+right+full
- Primary key vs foreign key: https://www.youtube.com/results?search_query=primary+key+vs+foreign+key+sql
