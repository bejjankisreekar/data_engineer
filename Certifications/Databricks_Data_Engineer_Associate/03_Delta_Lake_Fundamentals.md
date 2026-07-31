# 03 — Delta Lake Fundamentals

*Domain: Databricks Lakehouse Platform (24%)* — **the single most tested topic on the exam.**

---

## What it is

**Delta Lake** is an open-source storage layer that brings **ACID transactions**, **schema enforcement**, **time travel**, and performance optimizations to data stored in cloud object storage. It is the **default table format** on Databricks.

Physically, a Delta table is a directory containing:
- **Parquet data files** — the actual rows, columnar and compressed.
- **A transaction log** — a `_delta_log/` subdirectory of JSON (and periodic Parquet checkpoint) files that record **every change** as an ordered series of commits.

**Analogy:** Parquet files are the pages of a ledger. The `_delta_log` is the ledger's index and audit trail — it records, in order, exactly what was added or removed in each transaction. Reading a Delta table means reading the log to know *which* Parquet files currently make up the table.

> **Exam Tip:** A Delta table = **Parquet data files + a `_delta_log` transaction log**. The transaction log is the source of truth for what the table contains and is what enables ACID, time travel, and schema enforcement.

---

## ACID transactions

Delta gives you the four ACID guarantees on a data lake:

- **Atomicity** — a write either fully commits or not at all (no half-written tables).
- **Consistency** — the table moves from one valid state to another.
- **Isolation** — concurrent readers/writers don't see each other's partial work; readers get a consistent snapshot.
- **Durability** — committed changes persist.

This means multiple jobs can read and write the same table safely, and a failed job won't corrupt the table.

---

## The transaction log (`_delta_log`)

- Each successful write creates a new **JSON commit file** (e.g., `000000.json`, `000001.json`) describing which files were **added** and **removed**.
- Reads determine the current table state by replaying the log.
- Every ~10 commits, Delta writes a **Parquet checkpoint** to speed up log replay.
- The log is what enables **time travel**, **ACID**, and **optimistic concurrency**.

---

## Managed vs External (Unmanaged) tables

**This distinction is heavily tested.**

| | Managed table | External (unmanaged) table |
|---|---|---|
| Who controls storage location | Databricks (default managed location) | You specify `LOCATION '...'` |
| `DROP TABLE` behavior | Deletes **both metadata and underlying data files** | Deletes **only the metadata**; data files remain |
| Created by | `CREATE TABLE name ...` (no LOCATION) | `CREATE TABLE name ... LOCATION '/path'` |

> **Exam Tip:** The defining difference: **dropping a *managed* table deletes the data; dropping an *external* table leaves the data in place** (only metadata is removed). If a question asks "you dropped the table but the files are still there — what kind was it?" → external. Specifying a `LOCATION` makes a table external.

---

## Creating Delta tables

```sql
-- Managed Delta table (Delta is the default; USING DELTA is optional)
CREATE TABLE students (id INT, name STRING, value DOUBLE);

-- External Delta table at a specific location
CREATE TABLE students
USING DELTA
LOCATION '/mnt/delta/students';

-- Create from a query (CTAS)
CREATE TABLE new_table AS SELECT * FROM existing_table;

-- Replace/create atomically (overwrites if exists, keeps history)
CREATE OR REPLACE TABLE students AS SELECT * FROM source;
```

> **Exam Tip:** `CREATE OR REPLACE TABLE` (CRAS) fully replaces the table's data **atomically** while **retaining the table's history** (it's a new version, not a drop) — old versions remain available via time travel. `CREATE TABLE IF NOT EXISTS` creates only when absent. `INSERT OVERWRITE` replaces data but requires the table to already exist and enforces the existing schema.

---

## Writing data: append, overwrite, MERGE

```sql
INSERT INTO students VALUES (1, 'Ada', 3.5);          -- append rows
INSERT OVERWRITE students SELECT * FROM staging;       -- replace all rows, keep schema
```

### MERGE (upsert) — very commonly tested

`MERGE` performs insert/update/delete in a single atomic transaction — the standard way to do **upserts** and **change data capture**:

```sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED AND s.deleted = true THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

> **Exam Tip:** `MERGE INTO` deduplicates and upserts in one atomic operation — use it to update existing rows and insert new ones without scanning/rewriting the whole table manually. It avoids the race conditions of a separate DELETE + INSERT.

---

## Time Travel

Because the log keeps history, you can query **old versions** of a table:

```sql
SELECT * FROM students VERSION AS OF 3;      -- by version number
SELECT * FROM students TIMESTAMP AS OF '2024-01-01';   -- by timestamp
SELECT * FROM students@v3;                    -- shorthand

DESCRIBE HISTORY students;   -- see all versions, operations, timestamps
```

**Restore** a table to a previous state:

```sql
RESTORE TABLE students TO VERSION AS OF 3;
```

> **Exam Tip:** `DESCRIBE HISTORY` shows the full version history (version number, timestamp, operation, user). Time travel is used to **audit changes, reproduce experiments, and roll back bad writes**. `RESTORE` reverts the table to an earlier version.

---

## Schema enforcement and evolution

- **Schema enforcement (schema-on-write)** — Delta **rejects** writes whose schema doesn't match the table (wrong column names, incompatible types, extra columns). This protects data quality.
- **Schema evolution** — you can *opt in* to allow new columns:
  ```sql
  -- SQL
  SET spark.databricks.delta.schema.autoMerge.enabled = true;
  ```
  ```python
  # PySpark
  df.write.mode("append").option("mergeSchema", "true").saveAsTable("t")
  ```

> **Exam Tip:** By default Delta **enforces** schema and fails a mismatched write. To add new columns you must **explicitly enable** schema evolution via `mergeSchema` (or `overwriteSchema` to change types). Don't assume schema changes are silently accepted.

---

## OPTIMIZE, Z-ORDER, and VACUUM — maintenance

- **`OPTIMIZE`** — compacts many small files into fewer large ones ("small file problem"), improving read performance.
  ```sql
  OPTIMIZE students;
  OPTIMIZE students ZORDER BY (id);
  ```
- **`ZORDER BY`** — co-locates related data in the same files based on the given column(s), speeding up queries that filter/join on those columns (data skipping).
- **`VACUUM`** — permanently deletes data files no longer referenced by the log **and older than the retention threshold (default 7 days)**. Reclaims storage.
  ```sql
  VACUUM students;                       -- default 7-day retention
  VACUUM students RETAIN 168 HOURS;      -- explicit
  ```

> **Exam Tip:** `VACUUM` removes **old, unreferenced** files older than the retention period — and doing so **breaks time travel to versions older than that retention window** (those files are physically gone). Default retention is **7 days**. `OPTIMIZE` fixes the small-file problem; `ZORDER` improves filtering on high-cardinality columns; `VACUUM` reclaims storage but limits how far back you can time-travel.

---

## Other useful Delta commands

```sql
DESCRIBE DETAIL students;    -- location, format, numFiles, size, partition columns
DESCRIBE EXTENDED students;  -- full metadata incl. managed/external, schema
DESCRIBE HISTORY students;   -- version history
CONVERT TO DELTA parquet.`/path/to/parquet_table`;  -- convert Parquet → Delta in place
```

> **Exam Tip:** `DESCRIBE DETAIL` tells you the number of files, size, and location; `DESCRIBE EXTENDED`/`DESCRIBE TABLE EXTENDED` shows whether a table is managed or external and its full schema. `CONVERT TO DELTA` upgrades an existing Parquet directory to Delta without rewriting the data.

---

## Quick Review

- **Delta table = Parquet data files + `_delta_log` transaction log.** The log enables ACID, time travel, schema enforcement.
- **ACID** on the lake: atomic, consistent, isolated, durable writes; safe concurrency.
- **Managed table**: DROP deletes data + metadata. **External table** (has `LOCATION`): DROP deletes **only metadata**, data stays.
- `CREATE OR REPLACE TABLE` = atomic full replace, **keeps history**. `INSERT OVERWRITE` replaces rows, keeps schema.
- **`MERGE INTO`** = atomic upsert (insert/update/delete) — the standard CDC/dedup pattern.
- **Time travel**: `VERSION AS OF` / `TIMESTAMP AS OF`; `DESCRIBE HISTORY` lists versions; `RESTORE` rolls back.
- **Schema enforcement** rejects mismatched writes by default; enable **`mergeSchema`** for evolution.
- **`OPTIMIZE`** compacts small files; **`ZORDER BY`** co-locates for faster filters; **`VACUUM`** deletes old files (default **7-day** retention) and **limits time travel** afterward.

---

## Further Learning — Docs & Videos

**Official documentation**
- What is Delta Lake: https://docs.databricks.com/en/delta/index.html
- Delta Lake tutorial: https://docs.databricks.com/en/delta/tutorial.html
- Managed vs external tables: https://docs.databricks.com/en/tables/managed-and-external.html
- Delta table time travel: https://docs.databricks.com/en/delta/history.html
- MERGE INTO (upsert): https://docs.databricks.com/en/delta/merge.html
- OPTIMIZE / Z-ORDER: https://docs.databricks.com/en/delta/optimize.html
- VACUUM: https://docs.databricks.com/en/delta/vacuum.html
- Schema enforcement & evolution: https://docs.databricks.com/en/tables/schema-enforcement.html

**Videos**
- Delta Lake official site & videos: https://delta.io/
- Delta Lake explained: https://www.youtube.com/results?search_query=delta+lake+explained+databricks+transaction+log
- Time travel & MERGE: https://www.youtube.com/results?search_query=databricks+delta+lake+time+travel+merge
- OPTIMIZE, ZORDER, VACUUM: https://www.youtube.com/results?search_query=databricks+optimize+zorder+vacuum

---

Next: **[04 — ELT with Spark SQL](04_ELT_with_Spark_SQL.md)**.
