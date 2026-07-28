# 12 — Most Asked & Tricky Exam Questions

These are the commonly-confused pairs and "gotcha" scenarios where most points are lost. Each is written as a trap the exam actually sets. Learn the *distinction*, not just the fact.

---

## Trap 1 — Managed vs External table on DROP

> You run `DROP TABLE sales`. Later you find the Parquet files still in the storage location. What happened?

**Answer:** `sales` was an **external** table — dropping it removes only the **metadata**; the data files remain. A **managed** table's DROP deletes **both** metadata and data. The tell: an external table was created with a `LOCATION` clause.

**Remember:** `LOCATION` → external → DROP keeps data. No `LOCATION` → managed → DROP deletes data.

---

## Trap 2 — `%run` vs `dbutils.notebook.run()`

> You need helper functions defined in `utils` notebook to be usable in your current notebook. Which do you use?

**Answer:** **`%run ./utils`** — it executes inline and shares variables/functions. `dbutils.notebook.run("utils", ...)` runs it as a **separate** execution and returns only a **string**; its variables are **not** available in your notebook.

**Remember:** Need shared functions/config → `%run`. Need to orchestrate/parameterize an independent notebook and get a return value → `dbutils.notebook.run()`.

---

## Trap 3 — Terminate vs Delete a cluster

> You terminate a cluster to save cost. Can you get it back with the same configuration?

**Answer:** **Yes.** Terminate stops compute but **retains the configuration** — you can restart it. Only **Delete** removes the configuration permanently.

---

## Trap 4 — `CREATE OR REPLACE TABLE` vs `INSERT OVERWRITE` vs `DROP`+`CREATE`

> You want to fully replace a table's data atomically while keeping its version history.

**Answer:** **`CREATE OR REPLACE TABLE ... AS SELECT`** — atomic replace that **retains history** (old versions still reachable via time travel). `INSERT OVERWRITE` also replaces data (keeps schema, requires the table to exist). **`DROP` + `CREATE`** loses all history and is not atomic.

**Remember:** Need history preserved → CREATE OR REPLACE or INSERT OVERWRITE, **not** DROP+CREATE.

---

## Trap 5 — Transformations vs Actions (lazy evaluation)

> `df.select(...).filter(...)` runs and takes 0.1 seconds. Did it process the data?

**Answer:** **No.** `select` and `filter` are **lazy transformations** — nothing executes until an **action** (`count`, `show`, `collect`, `write`, `display`) is called. The 0.1s was just building the plan.

**Actions:** `show`, `display`, `collect`, `count`, `take`, `first`, `write/save`.
**Transformations (lazy):** `select`, `filter/where`, `withColumn`, `groupBy`, `join`, `distinct`, `orderBy`, `drop`.

---

## Trap 6 — Colon `:` vs Dot `.` for nested data

> Column `payload` is a **string containing JSON**. How do you extract `payload`'s `user.name`?

**Answer:** Use the **colon** operator on a JSON **string** column: `payload:user.name` (colon to enter the JSON, then navigate). The **dot** operator is for a column already typed as a **struct**. If you first `from_json(payload, schema)` into a struct, then you use dots.

---

## Trap 7 — Auto Loader vs COPY INTO vs manual read

> New JSON files arrive continuously in a folder; you must ingest only new ones efficiently at scale.

**Answer:** **Auto Loader** (`format("cloudFiles")`) — it incrementally detects and loads **only new files**, tracks processed files automatically, and scales to millions of files. A manual `spark.read` loop reprocesses everything. `COPY INTO` is idempotent for smaller/occasional batch loads but Auto Loader is the streaming-scale answer.

---

## Trap 8 — Trigger.AvailableNow vs Trigger.ProcessingTime

> You want a job that runs hourly, processes all new data since last run, then shuts down to save cost.

**Answer:** **`Trigger.AvailableNow`** — processes all available new data in batches, then **stops**. A fixed `processingTime` interval would keep the stream **running continuously**, costing more.

---

## Trap 9 — Output modes for streaming aggregations

> Your stream computes a running count per key. Which output mode?

**Answer:** **`complete`** (rewrites the whole result each trigger) — because past aggregate values change. **`append`** only ever adds new rows and can't emit updated aggregates (without watermark finalization). **`update`** emits only changed rows (fine for upsert sinks).

---

## Trap 10 — Bronze / Silver / Gold identification

> A table described as "raw ingested events exactly as received, with a load-timestamp column." Which layer?

**Answer:** **Bronze** (raw, as-ingested). "Cleaned, deduplicated, joined, validated" → **Silver**. "Aggregated business KPIs / report-ready" → **Gold**.

---

## Trap 11 — DLT expectations: keep vs drop vs fail

> `CONSTRAINT c EXPECT (id IS NOT NULL)` with no `ON VIOLATION`. What happens to a row where `id` is null?

**Answer:** The row is **kept** in the table, and the violation is **recorded** in the pipeline's data-quality metrics. To remove such rows use **`ON VIOLATION DROP ROW`**; to stop the pipeline use **`ON VIOLATION FAIL UPDATE`**.

| Clause | Bad rows |
|---|---|
| `EXPECT` (default) | Kept + tracked |
| `EXPECT ... ON VIOLATION DROP ROW` | Dropped, pipeline continues |
| `EXPECT ... ON VIOLATION FAIL UPDATE` | Pipeline fails |

---

## Trap 12 — Streaming table vs Materialized view in DLT

> Which DLT table type processes only **new** data incrementally?

**Answer:** A **streaming live table** (`STREAMING` / `spark.readStream`). A **materialized view** (a plain `LIVE TABLE` without `STREAMING`) is **recomputed** from all source data each update.

---

## Trap 13 — VACUUM and time travel

> After `VACUUM`, why does `SELECT ... VERSION AS OF 2` now fail?

**Answer:** `VACUUM` **physically deleted** the old data files (unreferenced and older than the retention period, default **7 days**). Time travel to versions whose files were removed no longer works. `VACUUM` reclaims storage at the cost of deep history.

---

## Trap 14 — Cluster vs SQL Warehouse

> An analyst wants to run BI dashboards and SQL queries with optimized SQL compute. What do they use?

**Answer:** A **SQL Warehouse** (Databricks SQL), **not** an all-purpose cluster. Clusters are for notebooks/jobs; SQL Warehouses power the SQL/BI persona.

---

## Trap 15 — Unity Catalog privilege chain

> A user has `SELECT` on `main.sales.orders` but queries fail with a permission error. Why?

**Answer:** They're missing **`USE CATALOG`** on `main` and/or **`USE SCHEMA`** on `sales`. Querying a table requires the full chain: `USE CATALOG` + `USE SCHEMA` + `SELECT`.

---

## Trap 16 — Three-level vs two-level namespace

> A query uses `prod.finance.ledger`. What does the three-part name tell you?

**Answer:** It's a **Unity Catalog** reference: `catalog.schema.table`. The legacy Hive metastore uses only two levels (`schema.table`). Three parts = UC.

---

## Trap 17 — Python UDF vs built-in function performance

> Your pipeline is slow; profiling shows a Python UDF doing string uppercasing on every row. Fix?

**Answer:** Replace the Python UDF with the **built-in** function `upper()` (or a SQL UDF). Python UDFs serialize data between the JVM and Python and are **opaque to the Catalyst optimizer**, so they're much slower.

---

## Trap 18 — Job cluster vs all-purpose cluster cost

> A nightly job runs on an all-purpose cluster that's left running 24/7. How to cut cost with no logic change?

**Answer:** Run the job on a **job cluster** (auto-created at start, **auto-terminated** at end). The all-purpose cluster was billing continuously even when idle.

---

## Trap 19 — Checkpoint sharing

> Two streaming queries were pointed at the **same** checkpoint location. What's the problem?

**Answer:** Each stream must have its **own unique** checkpoint location. Sharing one corrupts offset tracking and breaks both streams' exactly-once guarantees.

---

## Trap 20 — Schema enforcement surprise

> An append with an extra column fails. The developer expected the column to be added. Why did it fail?

**Answer:** Delta **enforces schema by default** and rejects the mismatched write. To add new columns you must **opt in** with `mergeSchema` (`.option("mergeSchema","true")` or `SET spark.databricks.delta.schema.autoMerge.enabled=true`).

---

## Rapid-fire fact recall (memorize cold)

| Question | Answer |
|---|---|
| Default VACUUM retention | 7 days |
| Delta table = ? | Parquet files + `_delta_log` |
| Upsert command | `MERGE INTO` |
| Show table version history | `DESCRIBE HISTORY` |
| Managed vs external DROP | Managed deletes data; external keeps it |
| Trigger that runs-then-stops | `availableNow` |
| Auto Loader format string | `cloudFiles` |
| Medallion order | Bronze → Silver → Gold |
| DLT dependency reference | `LIVE.` / `dlt.read()` |
| DLT drop-bad-rows | `ON VIOLATION DROP ROW` |
| UC namespace | `catalog.schema.table` (3 levels) |
| Governs unstructured files in UC | Volume |
| Query-a-table privilege chain | USE CATALOG + USE SCHEMA + SELECT |
| BI/SQL compute | SQL Warehouse |
| Faster SQL, no code change | Photon |
| Production cluster type | Job cluster |
| Re-run only failed job tasks | Repair run |
| Read job parameter in notebook | `dbutils.widgets.get()` |
| Default DataFrame save mode | errorifexists |
| Shares variables between notebooks | `%run` |

---

Next: **[13 — Final Mock Exam](13_Final_Mock_Exam.md)**.
