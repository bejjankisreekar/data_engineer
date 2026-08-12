# Delta Lake

## What is it?

**Delta Lake** is an open-source **storage layer** that sits on top of a [data lake](../Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) and gives it the reliability of a database. It doesn't replace your files — it wraps your ordinary [Parquet](../File_Formats/05_Parquet.md) files with a **transaction log** so that a folder of files behaves like a real table: with transactions, updates, deletes, and history.

In one line: **Delta Lake = Parquet files + a transaction log (`_delta_log`) that makes them behave like a database table.**

The problem it solves: a plain data lake is just files in a folder. If two jobs write at once, or a job crashes halfway, you get half-written files, duplicate rows, and readers seeing a broken state. There is no `UPDATE`, no `DELETE`, no "undo." Delta Lake fixes exactly this.

---

## Analogy: a bank ledger vs a pile of receipts

A plain data lake is a **shoebox full of receipts** — you can throw more in, but there's no running total, no way to correct a mistake without rifling through everything, and if someone knocks the box over mid-count you have no idea what's true.

Delta Lake adds a **bank ledger** next to the shoebox. Every change is written as a line in the ledger *first* ("added 100 rows", "deleted these 3", "corrected that one"). The receipts (Parquet files) still exist, but the **ledger is the source of truth** about which receipts are currently valid. To know the balance, you read the ledger — instantly, consistently, and you can even read yesterday's balance by stopping partway down the page.

---

## Example

A folder that is a Delta table looks like this:

```
/sales/
├── _delta_log/                 ← the transaction log (the "ledger")
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   └── 00000000000000000002.json
├── part-0000-....snappy.parquet   ← the actual data (Parquet)
├── part-0001-....snappy.parquet
└── part-0002-....snappy.parquet
```

The `.parquet` files hold the data. The `_delta_log/` folder holds the JSON commit files — one per transaction — that say which Parquet files are part of the table *right now*. Reading the table means reading the log to find the valid files, then reading those files.

```python
# Writing a Delta table is almost identical to writing Parquet —
# you just change the format string.
df.write.format("delta").save("/sales")

# But now you can do things Parquet alone can't:
spark.sql("DELETE FROM sales WHERE region = 'test'")
spark.sql("UPDATE sales SET amount = 0 WHERE amount IS NULL")
```

---

## Advantages

- **ACID transactions** — writes either fully succeed or fully fail; readers never see half-written data ([ACID recap](../../02_Databases/SQL/12_SQL_DCL_TCL.md)).
- **Updates & deletes** — real `UPDATE`, `DELETE`, and `MERGE` (upsert) on lake files, which raw Parquet cannot do.
- **Time travel** — read the table as it was at any past version or timestamp.
- **Schema enforcement** — rejects writes whose columns/types don't match, preventing silent corruption.
- **Schema evolution** — deliberately add new columns over time without rewriting everything.
- **Open format** — it's still Parquet underneath; no proprietary lock-in, readable by Spark, Trino, Fabric, DuckDB, and more.
- **Batch + streaming on one table** — the same Delta table can be a streaming sink and a streaming source.

## Disadvantages

- **Small-file & log overhead** — many tiny commits create many tiny files and a long log; needs periodic `OPTIMIZE` and `VACUUM` maintenance.
- **Not for OLTP** — it's built for analytics-scale batch/stream writes, not thousands of single-row transactions per second ([why](../../01_Foundations/Fundamentals/01_OLTP_Storage.md)).
- **Engine support varies** — best inside Spark/Databricks; other engines support a subset of features.
- **Concurrency is optimistic** — two jobs writing the *same* files can conflict and force a retry.

---

## Azure Usage

| Where | How Delta Lake shows up |
|---|---|
| **Azure Databricks** | The default table format; the foundation of the [lakehouse](03_Lakehouse_Architecture.md) and Unity Catalog. |
| **Microsoft Fabric** | OneLake stores everything as Delta by default; Fabric Warehouse and Lakehouse both write Delta. |
| **Azure Synapse (Spark)** | Synapse Spark pools read and write Delta on [ADLS](../Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md). |
| **ADLS Gen2** | The physical storage the Delta files (and `_delta_log`) actually live in. |

---

## Real World Example

A retailer lands raw orders into a data lake every hour. Before Delta, a late-arriving correction ("cancel order #55") meant rewriting an entire day's Parquet partition by hand, and analysts sometimes queried the table *while* it was being rewritten and got duplicate or missing rows. After moving to Delta Lake, the correction is a one-line `MERGE`, the write is atomic (analysts never see a half-state), and when finance later asks "what did yesterday's numbers look like *before* the correction?", the team answers with a single time-travel query instead of restoring a backup.

---
---

# Part 2 — Advanced

## How the transaction log actually works

The `_delta_log` is an **ordered list of commits**. Each commit is a JSON file (`000...N.json`) containing *actions*:

- `add` — a Parquet file is now part of the table (with its stats: row count, min/max per column).
- `remove` — a Parquet file is no longer part of the table (tombstoned, not physically deleted yet).
- `metaData` — the schema and partitioning.
- `commitInfo` — who/what/when, the operation (`MERGE`, `DELETE`, …).

The **current state of the table = replay every commit in order**, applying adds and removes. This is why an `UPDATE` doesn't edit a Parquet file in place (Parquet is immutable): Delta writes *new* files with the updated rows, then commits a transaction that `remove`s the old files and `add`s the new ones. Old files stay on disk (that's what makes time travel possible) until `VACUUM` cleans them.

To avoid replaying thousands of JSON files, Delta writes a **checkpoint** (a Parquet summary of the whole state) every 10 commits, so a reader loads the latest checkpoint + a few JSON files after it.

## ACID via optimistic concurrency

Delta uses **optimistic concurrency control**: a writer reads the current version (say v10), does its work, then tries to commit `000...11.json`. Because cloud object stores guarantee only one writer can create a given filename, only one wins the race for `11`. The loser re-reads v11, checks whether its changes still make sense (did the other writer touch the same files?), and if not, retries as v12. This gives **serializable isolation** without a traditional lock server — perfect for object storage.

## Time travel

Because old files are tombstoned rather than deleted, you can read any prior version:

```sql
SELECT * FROM sales VERSION AS OF 8;
SELECT * FROM sales TIMESTAMP AS OF '2026-07-30 00:00:00';
```

Uses: reproducing a report exactly, debugging "what changed", rolling back a bad load (`RESTORE TABLE ... VERSION AS OF`), and auditing.

### How far back can you go? (history retention)

**By default a Delta table keeps its history for 30 days** — you can time-travel and see `DESCRIBE HISTORY` entries for the last month. **This is configurable**: set it to any interval you need (7 days, 90 days, a year…).

```sql
-- Keep 60 days of history instead of the default 30
ALTER TABLE sales
SET TBLPROPERTIES ('delta.logRetentionDuration' = 'interval 60 days');
```

**The nuance that trips people up — two clocks, not one:**

| Property | Default | Controls |
|---|---|---|
| `delta.logRetentionDuration` | **30 days** | How long the **history log** (`DESCRIBE HISTORY`, version metadata) is kept |
| `delta.deletedFileRetentionDuration` | **7 days** | How long the **old data files** survive before `VACUUM` can delete them |

To *actually query* data 30+ days back, you must raise **both** — the 30-day log alone isn't enough, because `VACUUM` can remove the underlying data files after just 7 days. Increasing retention keeps more history but **costs more storage** (old file versions pile up), so raise it deliberately, not "just in case."

```sql
-- To reliably time-travel ~90 days back, extend BOTH clocks:
ALTER TABLE sales SET TBLPROPERTIES (
  'delta.logRetentionDuration'         = 'interval 90 days',
  'delta.deletedFileRetentionDuration' = 'interval 90 days'
);
```

## Schema enforcement vs evolution

- **Enforcement (default):** a write whose schema doesn't match the table is *rejected* — the guardrail that keeps a bad upstream change from corrupting the table.
- **Evolution (opt-in):** `mergeSchema` / `ALTER TABLE ADD COLUMN` lets the schema grow *on purpose*. New columns backfill as `NULL` for old rows. See [SCD & schema evolution](../../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md).

## Delta vs plain Parquet vs other table formats

| | Plain Parquet | Delta Lake | Iceberg / Hudi |
|---|---|---|---|
| ACID transactions | ❌ | ✅ | ✅ |
| Update / Delete / Merge | ❌ (rewrite by hand) | ✅ | ✅ |
| Time travel | ❌ | ✅ | ✅ |
| Schema enforcement | ❌ | ✅ | ✅ |
| Underlying files | Parquet | Parquet | Parquet/ORC |
| Best-supported engine | Everything | Spark / Databricks / Fabric | Trino / Flink / Spark |

Delta, Iceberg, and Hudi solve the *same* problem (the "open table format"); Delta dominates the Databricks/Azure world, so it's the one to know here.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The maintenance jobs nobody warns you about

A Delta table left alone slowly rots. Two chores keep it healthy:

- **`OPTIMIZE`** compacts many small files into fewer large ones (streaming and frequent MERGEs produce lots of tiny files — the "small file problem" that wrecks scan performance). `OPTIMIZE ... ZORDER BY (col)` additionally co-locates related data so queries skip more files.
- **`VACUUM`** physically deletes tombstoned files older than a retention window (default 7 days). **Gotcha:** `VACUUM` with a short retention *breaks time travel and can corrupt in-flight readers/streams* — the 7-day default exists for a reason; don't shorten it to "save space" without understanding what you're cutting off.

## Liquid clustering & deletion vectors (modern Delta)

- **Deletion vectors** turn a `DELETE`/`UPDATE` from "rewrite whole files" into "write a small bitmap marking deleted rows" — a *merge-on-read* optimization that makes deletes far cheaper; the rows are physically removed later at `OPTIMIZE`.
- **Liquid clustering** replaces rigid Hive-style partitioning + Z-ordering with an adaptive clustering scheme, avoiding the classic "over-partitioned table with millions of tiny partitions" disaster.

## Concurrency conflicts in practice

Optimistic concurrency is beautiful until two streams `MERGE` into the same table and thrash on retries. Field fixes: partition so writers touch disjoint files, funnel concurrent writes through `foreachBatch`, or serialize the writers. A `ConcurrentAppendException` in the logs is the classic symptom — it's a design smell, not a random error.

## The "one table, many engines" endgame

The strategic reason Delta matters: the *same* physical table is read by Spark (engineering), a SQL warehouse endpoint (BI), a stream (real-time), and DuckDB/Trino (ad-hoc) — **one copy, one set of permissions** via the catalog. When evaluating any platform, the pro asks: *does it read/write open Delta in **my** storage, or ingest into **its** proprietary store?* That single question predicts lock-in ([lock-in gradient](../../04_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md)).

## Field-tested gotchas

- **Time travel is not a backup.** `VACUUM` eventually deletes old versions; retention ≠ disaster recovery. Keep real backups.
- **Tiny-batch streaming = file explosion.** A stream committing every few seconds needs auto-compaction/optimized writes on, or nightly `OPTIMIZE`, or the table becomes millions of KB-sized files.
- **`overwrite` vs `MERGE`.** Beginners "fix" data with a full `overwrite`, silently discarding history and other writers' concurrent work. Prefer `MERGE` for upserts.
- **Log growth.** Very high commit rates make the `_delta_log` huge; checkpoints help, but ultra-chatty writers still need batching.

## Interview-grade Q&A

- *What is Delta Lake in one sentence?* An open storage layer that adds ACID transactions, updates/deletes, and time travel to Parquet files on a data lake, via a transaction log.
- *How does it get ACID on object storage with no locks?* Optimistic concurrency + the object store's atomic "create-if-not-exists" on the next log filename — only one writer can claim commit N.
- *How does an UPDATE work if Parquet is immutable?* It writes new files with the changed rows and commits a transaction that removes the old files and adds the new ones (or, modernly, writes a deletion vector).
- *Delta vs Parquet?* Parquet is a file format; Delta is a *table* format wrapping Parquet with a log to add transactions, DML, and history.
- *What breaks if you VACUUM too aggressively?* Time travel to older versions and any running readers/streams that still reference tombstoned files.

---

## Related Notes

- **Next:** [Delta Table](02_Delta_Table.md) — the table itself: managed vs external, MERGE, OPTIMIZE, VACUUM in practice.
- **Architecture:** [Lakehouse Architecture](03_Lakehouse_Architecture.md) — how Delta enables the medallion lakehouse.
- **Hands-on code:** [12 — Delta Lake with PySpark](../../03_Programming/PySpark/12_Delta_Lake_with_PySpark.md) — MERGE, time travel, OPTIMIZE in real PySpark.
- **Context:** [Data Lake vs Warehouse vs Database](../Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) · [Parquet](../File_Formats/05_Parquet.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Delta Lake official docs: https://docs.delta.io/latest/index.html
- What is Delta Lake? (Databricks): https://learn.microsoft.com/en-us/azure/databricks/delta/
- Delta transaction log protocol: https://github.com/delta-io/delta/blob/master/PROTOCOL.md

**Videos**
- Delta Lake explained: https://www.youtube.com/results?search_query=delta+lake+explained
- Delta Lake transaction log deep dive: https://www.youtube.com/results?search_query=delta+lake+transaction+log
