# SQL Indexes

## What is an index?

An index is an extra, behind-the-scenes structure that helps the database find rows faster, without having to check every single row in a table one by one.

Analogy: it's exactly like the index at the back of a textbook. Without it, finding every mention of "photosynthesis" means flipping through the entire book page by page. With the index, you look up "photosynthesis," see it's on pages 45, 112, and 201, and jump straight there. The index doesn't contain the actual chapter content — it's a shortcut pointing to where that content lives.

---

## Without an Index

```sql
SELECT * FROM Employee
WHERE EmployeeID = 4500;
```

Without an index on `EmployeeID`, the database performs a **full table scan** — checking every single row, one at a time, to see if it matches. On a table with 10 million rows, that's 10 million checks for a single lookup.

---

## With an Index

```sql
CREATE INDEX idx_EmployeeID
ON Employee (EmployeeID);
```

Now the database maintains a sorted lookup structure for `EmployeeID` (commonly a structure called a B-tree, though the exact internals don't matter for using it). Finding `EmployeeID = 4500` becomes closer to flipping straight to the right page in a phone book sorted by name, instead of reading every entry from the start.

---

## Indexes Aren't Free

An index speeds up *reading*, but it comes at a cost:

- **Extra storage** — the index itself takes up disk space, separate from the table's own data
- **Slower writes** — every `INSERT`, `UPDATE`, or `DELETE` must also update every index on that table, since the shortcut structure has to stay accurate

Analogy: keeping a textbook's index up to date takes extra work every time a new chapter is added — but it's worth it if the book gets looked up in far more often than it gets edited.

This is why indexes are added deliberately, on columns that are:

- Frequently searched or filtered on (`WHERE`, `JOIN` conditions)
- Not being constantly rewritten

The [`PRIMARY KEY`](07_SQL_Keys_and_Joins.md) of a table is automatically indexed by most databases, precisely because it's so frequently used to look up and join rows.

---

## When Not to Index

- Small tables (a full scan of a few hundred rows is already instant — an index adds overhead for no benefit)
- Columns rarely used in `WHERE` or `JOIN` conditions
- Tables that are written to far more often than they're read from (e.g. a raw logging table that's rarely queried directly)

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both support indexes, and Synapse specifically offers **columnstore indexes** — an index type designed around [columnar storage](../02_File_formats/05_Parquet.md) principles, built for the large-scale analytical queries a data warehouse typically runs. Choosing the right indexing strategy is one of the most common ways a database administrator improves report performance without changing a single query.

---

## Real World Example

An airline's booking system runs thousands of lookups per second for `WHERE FlightNumber = ...`. An index on `FlightNumber` turns each of those lookups from "scan every booking ever made" into "jump almost directly to the matching rows" — the difference between a booking confirmation appearing instantly versus taking several seconds under heavy load.

---
---

# Part 2 — Advanced

## Clustered vs nonclustered — the fundamental split

- **Clustered index** = the table itself, physically ordered by the key. One per table (the data can only be sorted one way). In SQL Server, the primary key is clustered by default; a heap (no clustered index) is the alternative.
- **Nonclustered index** = a separate sorted structure of `(key columns) → pointer to the row`. Many per table.

The hidden cost of nonclustered lookups: finding rows in the index, then fetching the rest of each row from the table = a **key lookup** per row. Cheap for 10 rows, worse than a scan for 100,000 — which is why the optimizer sometimes *ignores* your index for low-selectivity predicates (and it's right).

## Composite indexes and the leftmost-prefix rule

```sql
CREATE INDEX idx_dept_hire ON Employee (Department, HireDate);
```

This index serves: `WHERE Department = 'IT'` ✅, `WHERE Department = 'IT' AND HireDate > '2025-01-01'` ✅ — but **not** `WHERE HireDate > '2025-01-01'` alone ❌ (like a phone book sorted by last-then-first name: useless for finding all "Priya"s). Column order rule of thumb: **equality columns first, range columns last**; the most selective equality first among equals.

## Covering indexes — the report-query trick

If the index contains *every* column a query touches, the table is never visited at all:

```sql
CREATE INDEX idx_cover
ON Orders (CustomerID) INCLUDE (OrderDate, Amount);   -- T-SQL INCLUDE = in leaf, not in sort key
SELECT OrderDate, Amount FROM Orders WHERE CustomerID = 42;  -- index-only: no key lookups
```

The single most effective targeted fix for a hot query — at the cost of a wider index to maintain on every write.

## Columnstore — indexes for analytics

Rowstore B-trees answer "find these few rows fast"; **columnstore indexes** (Synapse default, SQL Server option) store data [column-wise, compressed, batch-processed](../00_Fundamentals/02_OLAP_Storage.md) — built for "scan a billion rows, aggregate three columns." The two coexist: clustered columnstore for the big fact table + a few B-tree indexes for point lookups on it. In the lakehouse the same role is played by [Parquet](../02_File_formats/05_Parquet.md) + statistics + Z-ordering — "indexing" became file layout ([Spark_Processing.md](../06_PySpark/Spark_Processing.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Selectivity & statistics — why the optimizer ignores your index

The optimizer estimates, from **statistics** (histograms of column values), how many rows a predicate returns:

- `WHERE status = 'CANCELLED'` (0.1% of rows) → index seek, brilliant.
- `WHERE status = 'COMPLETED'` (95% of rows) → seek + 95M key lookups would be madness → full scan, *correctly*.

When statistics go stale (bulk loads without updating them), estimates go wrong, and plans flip from seeks to scans "randomly overnight" — the most common enterprise performance mystery. Pro toolkit: auto-update stats on, manual `UPDATE STATISTICS` after big loads, and reading estimated-vs-actual rows in [plans](06_SQL_DQL.md).

## The write-side ledger

Every index is a standing tax: extra pages per INSERT, potential **page splits** (a full index page splits in two — fragmentation + log churn) on out-of-order inserts, extra locks/latches, longer maintenance windows. Real-world numbers: an OLTP table with 12 indexes can spend more time maintaining indexes than inserting data. Discipline pros apply:

- Review `sys.dm_db_index_usage_stats` (or equivalents) quarterly: **drop indexes with zero seeks and millions of updates**.
- Consolidate near-duplicates (`(A)` is redundant if `(A,B)` exists).
- **Filtered/partial indexes** for hot subsets: `CREATE INDEX ... WHERE status = 'PENDING'` — tiny, fast, cheap to maintain.
- On staging tables: drop indexes, bulk load, rebuild — cheaper than maintaining them through the load ([bulk loading](05_SQL_DML.md)).

## Fragmentation & maintenance (the honest modern take)

Logical fragmentation mattered enormously on spinning disks; on SSDs and cloud storage it matters far less than received wisdom claims. What still matters: **page density** (half-empty pages waste buffer pool RAM) and statistics freshness. Modern guidance: rebuild/reorganize on evidence (density, not a fragmentation % ritual), and spend the saved effort on statistics and query design.

## Field-tested gotchas

- Non-sargable predicates make every index irrelevant — `WHERE YEAR(col)=2026` seeks nothing ([sargability](06_SQL_DQL.md)); fix the query before adding indexes.
- **GUID clustered keys** = random insert points = perpetual page splits ([data types](03_SQL_Data_Types.md)); cluster on sequential keys.
- An index on a column with skewed data can be great for the rare values and useless for the common one — parameter sniffing then caches the wrong plan for everyone (`OPTIMIZE FOR`/recompile hints are the escape hatches).
- Missing-index DMV suggestions are hints, not orders — they suggest overlapping monsters; a human consolidates.
- Foreign key columns are **not** auto-indexed in most engines — unindexed FKs make parent deletes and joins scan the child table ([keys](07_SQL_Keys_and_Joins.md)).

## Interview-grade Q&A

- *Clustered vs nonclustered?* Table-order-defining (one) vs separate pointer structures (many); nonclustered pay key-lookup costs unless covering.
- *Why would the optimizer skip an index?* Low selectivity, stale stats, non-sargable predicate, or lookup cost exceeding a scan.
- *Design an index for `WHERE a=? AND b>? ORDER BY b`?* Composite `(a, b)` — equality first, range second; add INCLUDE columns to cover the select list.
- *Indexing strategy for a warehouse fact table?* Clustered columnstore (or Parquet/Delta + Z-order in the lake), partition alignment, minimal B-trees for point access.
