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

Order Table

| OrderID | CustomerID (foreign key) | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 503 | 2 | 3000 |

`CustomerID` in the Order table isn't the order's own identity — it's a pointer back to the Customer table. This is how the database knows order 501 belongs to Meera without repeating her name and city on every row.

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
    Order.OrderID,
    Customer.Name,
    Order.Amount
FROM Order
JOIN Customer
    ON Order.CustomerID = Customer.CustomerID;
```

Result

| OrderID | Name | Amount |
|---|---|---|
| 501 | Meera | 2000 |
| 502 | Meera | 1500 |
| 503 | Raj | 3000 |

The query reunites data that normalization intentionally kept apart.

---

## Common Join Types

| Join Type | Returns |
|---|---|
| INNER JOIN | Only rows that match in both tables |
| LEFT JOIN | All rows from the left table, plus matches from the right (unmatched right side is blank) |
| RIGHT JOIN | All rows from the right table, plus matches from the left |
| FULL JOIN | All rows from both tables, matched where possible |

Example: a LEFT JOIN from Customer to Order would still show a customer who has never placed an order — with blank order details — because "all customers" is the priority, not "only customers with orders."

---

## Real World Example

An insurance company keeps:

- A **Policyholders** table (one row per person)
- A **Claims** table (one row per claim, referencing a Policyholder via a foreign key)

A claims officer never re-types a policyholder's full details onto every claim. They just reference the Policyholder ID, and a join pulls the full policyholder details back in whenever a report is generated. This is the same pattern behind almost every business system: banking, healthcare, retail, and HR.

---
---

# Part 2 — Advanced

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

Also in the family: **anti-join** ("customers with NO orders") — `LEFT JOIN ... WHERE o.CustomerID IS NULL`, or better `NOT EXISTS`; **semi-join** ("customers who have at least one order, without duplicating them") — `EXISTS`. Prefer EXISTS over `IN (subquery)`: same intent, no [NULL trap](09_SQL_Subqueries.md), often better plans.

## Join algorithms — what the engine actually runs

| Algorithm | How | Best when |
|---|---|---|
| **Nested loops** | For each outer row, seek the inner table | Small outer + indexed inner (OLTP point queries) |
| **Hash join** | Build hash table on smaller input, probe with larger | Large unsorted inputs (analytics default) |
| **Merge join** | Both inputs sorted on key, zip together | Pre-sorted/indexed inputs |

You don't pick these directly — but you *cause* them: bad statistics that underestimate rows send a million-row input into nested loops (the "query that ran fine yesterday" classic). Distributed engines add a location dimension: **broadcast vs shuffle joins** ([Spark join strategies](../../06_Programming/PySpark/Spark_Processing.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

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
