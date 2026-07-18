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

The [`PRIMARY KEY`](SQL_Keys_and_Joins.md) of a table is automatically indexed by most databases, precisely because it's so frequently used to look up and join rows.

---

## When Not to Index

- Small tables (a full scan of a few hundred rows is already instant — an index adds overhead for no benefit)
- Columns rarely used in `WHERE` or `JOIN` conditions
- Tables that are written to far more often than they're read from (e.g. a raw logging table that's rarely queried directly)

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both support indexes, and Synapse specifically offers **columnstore indexes** — an index type designed around [columnar storage](../02_File_formats/Parquet.md) principles, built for the large-scale analytical queries a data warehouse typically runs. Choosing the right indexing strategy is one of the most common ways a database administrator improves report performance without changing a single query.

---

## Real World Example

An airline's booking system runs thousands of lookups per second for `WHERE FlightNumber = ...`. An index on `FlightNumber` turns each of those lookups from "scan every booking ever made" into "jump almost directly to the matching rows" — the difference between a booking confirmation appearing instantly versus taking several seconds under heavy load.
