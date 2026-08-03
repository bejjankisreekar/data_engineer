# Delta Table

## What is it?

A **Delta table** is a table stored in the [Delta Lake](01_Delta_Lake.md) format — a folder of [Parquet](../File_Formats/05_Parquet.md) files plus a `_delta_log` transaction log — that you can query and modify with SQL or DataFrame code as if it were an ordinary database table.

If [Delta Lake](01_Delta_Lake.md) is the *technology* (the storage layer and its rules), a **Delta table** is the *thing you actually use* every day: the object you `SELECT` from, `MERGE` into, `OPTIMIZE`, and time-travel through.

In one line: **a Delta table is a database-like table whose data lives as open Parquet files in a data lake, with a log that makes it transactional.**

---

## Analogy: a shared, versioned spreadsheet

A plain Parquet folder is like a **flat CSV** emailed around — to change one number, someone re-saves the whole file, and nobody knows which copy is current.

A Delta table is like a **shared cloud spreadsheet with version history**: many people can edit safely, every change is tracked, you can open any past version, and you never see a half-saved state. Same familiar "table" you query — but with a full history and safe concurrent edits underneath.

---

## Example

```sql
-- Create a Delta table
CREATE TABLE sales (
    order_id   INT,
    customer   STRING,
    amount     DOUBLE,
    order_date DATE
) USING DELTA;

-- Insert, update, delete — all the DML a database gives you
INSERT INTO sales VALUES (1, 'Acme', 250.0, '2026-07-31');
UPDATE sales SET amount = 300.0 WHERE order_id = 1;
DELETE FROM sales WHERE amount IS NULL;

-- Upsert (the killer feature): insert new, update existing, in one atomic op
MERGE INTO sales AS t
USING updates AS s
ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- Look at the table's history and travel back in time
DESCRIBE HISTORY sales;
SELECT * FROM sales VERSION AS OF 3;
```

The DataFrame equivalents live in the [PySpark Delta coding note](../../03_Programming/PySpark/12_Delta_Lake_with_PySpark.md).

---

## Managed vs External (Unmanaged) tables

This is the single most-tested distinction about Delta tables:

| | **Managed table** | **External (unmanaged) table** |
|---|---|---|
| Who owns the storage location | The catalog/metastore chooses it | **You** specify the `LOCATION` |
| `DROP TABLE` deletes the data files? | **Yes** — metadata *and* files | **No** — only the metadata; files remain |
| Typical use | Curated tables fully governed by the platform | Data shared with other tools, or you want control of the path |
| Create syntax | `CREATE TABLE t USING DELTA` | `CREATE TABLE t USING DELTA LOCATION '/mnt/…'` |

**The classic mistake:** running `DROP TABLE` on a *managed* table expecting the files to survive — they don't. If you need the files to outlive the table definition, make it **external**.

---

## Advantages

- **Full DML** — `INSERT`, `UPDATE`, `DELETE`, and `MERGE`/upsert, which raw lake files can't do.
- **Atomic & concurrent-safe** — readers never see partial writes; multiple writers coordinate via the log.
- **History & rollback** — `DESCRIBE HISTORY`, time travel, and `RESTORE` to undo a bad load.
- **Schema safety** — enforcement blocks bad writes; evolution adds columns on purpose.
- **Streaming + batch** — the same table can be both a streaming sink and source.

## Disadvantages

- **Needs upkeep** — `OPTIMIZE` and `VACUUM` must run, or performance and cost drift.
- **Small writes hurt** — many tiny commits → many tiny files.
- **Not OLTP** — no point in using it for high-frequency single-row transactions.

---

## Azure Usage

| Where | Delta table role |
|---|---|
| **Azure Databricks** | Default table type; registered in the Hive metastore or **Unity Catalog** (`catalog.schema.table`). |
| **Microsoft Fabric** | Lakehouse and Warehouse tables are Delta in OneLake; queryable by the SQL endpoint. |
| **Azure Synapse** | Spark pools create/read Delta tables; serverless SQL can query them. |

---

## Real World Example

A subscription business keeps a `customers` Delta table as its silver-layer source of truth. Every night, a job receives a feed of new signups *and* profile edits mixed together. Instead of figuring out which rows are new versus changed, one `MERGE` handles both: matched rows update, unmatched rows insert — atomically, so the dashboards reading the table at midnight never catch it mid-update. When a bad feed once doubled a day's rows, the on-call engineer ran `RESTORE TABLE customers VERSION AS OF <yesterday>` and the table was clean again in seconds — no backup restore, no downtime.

---
---

# Part 2 — Advanced

## The MERGE pattern (upserts & SCD)

`MERGE` is why teams adopt Delta tables. It powers:

- **Upserts** — insert-or-update in one pass (the example above).
- **[SCD Type 2](../../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md)** — close the old row (set `end_date`, `is_current = false`) and insert a new current row, so history is preserved.
- **[CDC](../../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) apply** — replay inserts/updates/deletes from a source database's change stream onto the table.

`MERGE` is a **shuffle- and rewrite-heavy** operation: it must find matching files, rewrite them, and commit. On big tables, partitioning/clustering the join key and narrowing the match condition (e.g. only recent partitions) is the difference between minutes and hours.

## Table maintenance in practice

```sql
OPTIMIZE sales;                          -- compact small files into big ones
OPTIMIZE sales ZORDER BY (customer);     -- + co-locate by a common filter column
VACUUM sales;                            -- delete tombstoned files older than 7 days
DESCRIBE DETAIL sales;                   -- file count, size, partitioning
DESCRIBE HISTORY sales;                  -- every operation, version, timestamp
```

- **`OPTIMIZE`** fixes the small-file problem (streaming/frequent MERGE creates many tiny files that slow scans).
- **`ZORDER`** (or modern **liquid clustering**) skips more files when you filter on the clustered column.
- **`VACUUM`** reclaims storage — but see the retention gotcha in [Delta Lake, Part 3](01_Delta_Lake.md).

## Change Data Feed (CDF)

A Delta table can emit its own row-level changes:

```sql
ALTER TABLE sales SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
SELECT * FROM table_changes('sales', 5);   -- what changed since version 5
```

Downstream jobs read *only the deltas* instead of rescanning the whole table — the foundation of incremental medallion pipelines ([CDF & CDC](../../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)).

## Partitioning a Delta table

Partitioning splits the table into subfolders by a column (`PARTITIONED BY (order_date)`), so queries filtering on that column read fewer files. Rules of thumb:

- Partition on a **low-cardinality, commonly-filtered** column (date is the classic).
- **Never** partition on a high-cardinality key (customer_id) → millions of tiny partitions, a performance disaster.
- Modern advice: prefer **liquid clustering** over manual partitioning for most tables — it adapts and avoids the over-partitioning trap.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Managed vs external is a governance decision, not a syntax detail

The choice determines *who can delete your data*. Managed tables let the platform (Unity Catalog) own the full lifecycle — clean, governed, but a `DROP` is destructive. External tables keep the path under your control — essential when another engine (Fabric, Trino, a downstream team) also reads those files, or when you must guarantee that dropping a table definition never touches the bytes. Getting this wrong is how teams lose data to a "harmless" cleanup script.

## MERGE performance is where lakehouses live or die

The recurring production fire is a nightly `MERGE` that gets slower every week as the table grows. Fixes the pros reach for: **match only touched partitions** (`AND t.order_date >= current_date - 7`), **cluster/partition the merge key**, enable **deletion vectors** (merge-on-read so matched files aren't fully rewritten), and watch for **skew** on the join key. A `MERGE` that rewrites the whole table every night is a design bug, not a Delta limitation.

## Concurrency: design writers to not collide

Delta's optimistic concurrency means two jobs writing overlapping files throw `ConcurrentAppendException` and retry. On a table with many concurrent writers, partition so each writer owns disjoint files, or serialize through a single `foreachBatch`. "It works in dev" with one writer and falls over in prod with ten is the classic trajectory.

## Field-tested gotchas

- **`DROP TABLE` on a managed table deletes the files.** The #1 accidental data-loss cause. Know which kind you have (`DESCRIBE DETAIL` → `location`).
- **Time travel ≠ backup.** `VACUUM` eventually removes old versions; keep independent backups for DR.
- **`overwrite` throws away history and concurrent writes.** Use `MERGE` for corrections, not a blind full overwrite.
- **Unpartitioned huge table + frequent point deletes** = full-table rewrites. Enable deletion vectors and cluster the filter columns.
- **Streaming into a table with no compaction** silently rots it into millions of tiny files — turn on optimized writes / auto-compaction.

## Interview-grade Q&A

- *Managed vs external Delta table — the practical difference?* `DROP TABLE` deletes the data files for a managed table but only the metadata for an external one; external tables let you (or other engines) own the storage path.
- *What does MERGE give you that INSERT/UPDATE can't?* Insert-or-update (upsert) plus delete in a single atomic operation — the backbone of CDC apply and SCD2.
- *Your nightly MERGE keeps getting slower — why and what do you do?* It's rewriting more files as the table grows; constrain the match to recent partitions, cluster/partition the merge key, enable deletion vectors, and check for join-key skew.
- *How do you undo a bad load?* `RESTORE TABLE t VERSION AS OF <good_version>` (or `TIMESTAMP AS OF`), which is possible because old files are tombstoned, not immediately deleted.
- *Why not partition a Delta table by customer_id?* High cardinality creates millions of tiny partitions/files, destroying scan performance; partition on low-cardinality date-like columns or use liquid clustering.

---

## Related Notes

- **Prev:** [Delta Lake](01_Delta_Lake.md) — the storage layer and transaction log this table is built on.
- **Next:** [Lakehouse Architecture](03_Lakehouse_Architecture.md) — how Delta tables form the bronze/silver/gold medallion.
- **Hands-on code:** [12 — Delta Lake with PySpark](../../03_Programming/PySpark/12_Delta_Lake_with_PySpark.md)
- **Modeling:** [Slowly Changing Dimensions](../../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) · [Change Data Capture](../../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Delta table batch reads & writes: https://docs.delta.io/latest/delta-batch.html
- MERGE / upsert into Delta: https://docs.delta.io/latest/delta-update.html
- Managed vs external tables (Databricks): https://learn.microsoft.com/en-us/azure/databricks/tables/

**Videos**
- Delta table MERGE / upsert explained: https://www.youtube.com/results?search_query=delta+lake+merge+upsert
- Managed vs external tables Databricks: https://www.youtube.com/results?search_query=managed+vs+external+table+databricks
