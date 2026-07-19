# 04 — Reading & Writing Data

> Prev: [Schemas & Data Types](03_Schemas_and_Data_Types.md) · Next: [Column Operations](05_Column_Operations_and_Functions.md)

Spark computes; storage stores ([the division](What_Is_Apache_Spark.md)). This file is the bridge: `spark.read` in, `df.write` out — across every format in the [02_File_formats folder](../02_File_formats/06_File_Format_Comparison.md).

---

## Level 1 — Reading

```python
# General shape:  spark.read .format(...) .option(...) .schema(...) .load(path)
# Shortcuts exist per format:

df = spark.read.csv("path/file.csv", header=True, schema=ddl)          # CSV
df = spark.read.json("path/events/")                                   # JSON Lines
df = spark.read.parquet("path/table/")                                 # Parquet
df = spark.read.format("delta").load("path/delta_table/")              # Delta
df = spark.read.table("catalog.schema.orders")                         # catalog table (Databricks)
```

Paths can be a file, a **folder** (reads every file inside), or a glob (`"path/2026-07-*.csv"`). On Azure, paths look like `abfss://container@account.dfs.core.windows.net/folder/` ([ADLS](../03_Data_Storage/03_Azure_Data_Lake_Storage.md)).

### The options you'll actually use

```python
(spark.read.format("csv")
   .option("header", True)
   .option("sep", ";")                     # delimiter
   .option("quote", '"').option("escape", '"')
   .option("nullValue", "NULL")
   .option("mode", "PERMISSIVE")           # or DROPMALFORMED / FAILFAST
   .schema(my_schema)                      # ALWAYS in production (03)
   .load("abfss://raw@lake.dfs.core.windows.net/sales/"))
```

The full CSV/JSON defense checklist lives in [01_CSV.md](../02_File_formats/01_CSV.md) / [02_JSON.md](../02_File_formats/02_JSON.md).

## Level 1 — Writing

```python
(df.write
   .format("parquet")                # or "delta", "csv", "json"
   .mode("overwrite")                # error (default) | overwrite | append | ignore
   .save("abfss://silver@lake.dfs.core.windows.net/sales/"))

df.write.mode("append").saveAsTable("silver.sales")     # write as a catalog table
```

**Modes**: `error` (fail if exists — the safe default), `overwrite` (replace), `append` (add), `ignore` (silently skip — almost never what you want).

Note: Spark writes a *folder* of part-files, never one file — that's the [parallelism](Spark_Processing.md) showing. It's normal and correct.

---

## Level 2 — The patterns production code uses

### Partitioned writes (pruning for readers)

```python
(df.write.format("delta")
   .partitionBy("year", "month")          # folder-per-value layout
   .mode("append")
   .save(path))
# → path/year=2026/month=07/part-....parquet
```

Readers filtering on `year`/`month` skip whole folders. Only partition **low-cardinality** columns ([why](../00_Fundamentals/02_OLAP_Storage.md)) — date parts yes, customer_id never.

### Controlling output file count

```python
df.repartition(8).write...        # 8 files (full shuffle to redistribute evenly)
df.coalesce(1).write...           # 1 file — ONLY for small exports; serializes the write
```

Target 100 MB–1 GB per file ([file sizing](Spark_Processing.md)).

### Reading databases over JDBC

```python
jdbc_df = (spark.read.format("jdbc")
    .option("url", "jdbc:sqlserver://server.database.windows.net;database=sales")
    .option("dbtable", "(SELECT * FROM orders WHERE modified_at > '2026-07-18') src")
    .option("user", user).option("password", pwd)      # from a secret scope, never literal!
    # parallel read — REQUIRED for big tables, else one task does everything:
    .option("partitionColumn", "order_id")
    .option("lowerBound", 1).option("upperBound", 10_000_000)
    .option("numPartitions", 8)
    .load())
```

Without `partitionColumn/numPartitions`, JDBC reads are **single-threaded** — the most common "why is extraction slow" answer. Bound `numPartitions` respectfully ([don't DoS the source](../01_SQL/02_SQL_Database.md)).

### Incremental file ingestion (Databricks Auto Loader)

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", chk + "/schema")
      .load("abfss://landing@lake.dfs.core.windows.net/events/"))
```

Processes only *new* files, tracks state, handles schema evolution — the production replacement for "re-list the folder and figure out what's new" ([streaming file](13_Structured_Streaming.md)).

---

## Level 3 — Pro corner

- **Plain `overwrite` to a path is not atomic** for readers on non-Delta formats — a reader mid-crash sees half a folder. Delta makes overwrite transactional; that alone justifies it as your default format ([12](12_Delta_Lake_with_PySpark.md)).
- **Scoped overwrite** beats full overwrite for daily loads: `.option("replaceWhere", "date = '2026-07-19'")` (Delta) rewrites one partition atomically and is naturally [idempotent](../04_ETL_ELT/01_ETL_vs_ELT.md).
- **Never hardcode credentials** — Databricks secret scopes / Key Vault (`dbutils.secrets.get`), or better, storage access via managed identity/UC so code has *no* secrets ([identity](../05_cloud/02_SaaS_PaaS_IaaS.md)).
- **Reading fewer bytes beats every other optimization**: select columns early, filter on partition columns in the *same* expression form they're stored (`F.col("year") == 2026`, not a cast of it), and let [Parquet pushdown](../02_File_formats/05_Parquet.md) work.
- `badRecordsPath` (Databricks) / `columnNameOfCorruptRecord` capture unparseable rows to a quarantine location instead of dropping them — wire the quarantine count to an alert ([boundary validation](../02_File_formats/06_File_Format_Comparison.md)).
- **Row-count reconciliation on every boundary write**: `written = df.count()` is a job of its own — prefer Delta's commit metrics (`DESCRIBE HISTORY` operationMetrics) or streaming query progress for free counts.

## Checkpoint

1. Read a folder of ;-delimited CSVs with an explicit schema, quarantining bad rows.
2. Write it as Delta partitioned by ingest date, ~8 files per partition.
3. Why is a naive JDBC read slow, and what's the fix?

Next: shaping the data itself → [05 — Column Operations & Functions](05_Column_Operations_and_Functions.md).
