# 12 — Delta Lake with PySpark

> Prev: [Spark SQL & Views](11_Spark_SQL_and_Views.md) · Next: [Structured Streaming](13_Structured_Streaming.md)

Delta Lake = [Parquet files](../02_File_formats/05_Parquet.md) + a **transaction log** (`_delta_log/`), giving lake storage database behavior: ACID commits, MERGE, time travel, schema enforcement ([why this matters](Why_Spark_Why_Databricks.md)). On Databricks, Delta is the default — `saveAsTable` already writes it. This file is the operations you'll use daily.

---

## Level 1 — Delta as a better table

```python
# Write / read — just a format
df.write.format("delta").mode("overwrite").saveAsTable("silver.employees")
df = spark.read.table("silver.employees")

# Schema is ENFORCED: appending a mismatched DataFrame fails loudly
bad.write.mode("append").saveAsTable("silver.employees")     # AnalysisException ✅

# Intentional evolution — additive columns
(df_with_new_col.write.mode("append")
   .option("mergeSchema", "true")
   .saveAsTable("silver.employees"))

# UPDATE / DELETE — impossible on plain Parquet, normal on Delta
spark.sql("UPDATE silver.employees SET dept = 'Tech' WHERE dept = 'IT'")
spark.sql("DELETE FROM silver.employees WHERE id = 99")
```

### Time travel and history

```python
spark.sql("DESCRIBE HISTORY silver.employees").select(
    "version", "timestamp", "operation", "operationMetrics").show(truncate=False)

old = spark.read.option("versionAsOf", 12).table("silver.employees")
old = spark.read.option("timestampAsOf", "2026-07-18").table("silver.employees")

spark.sql("RESTORE TABLE silver.employees TO VERSION AS OF 12")   # the undo button
```

Every write = a new version in the log. `DESCRIBE HISTORY`'s `operationMetrics` (rows written/deleted per commit) is your free [reconciliation feed](04_Reading_and_Writing_Data.md).

---

## Level 2 — MERGE: the daily-driver operation

The [upsert](../01_SQL/05_SQL_DML.md), Delta-style — the single most-run statement in lakehouse pipelines:

```python
from delta.tables import DeltaTable

target = DeltaTable.forName(spark, "silver.employees")

(target.alias("t")
 .merge(updates.alias("s"), "t.id = s.id")
 .whenMatchedUpdate(set={"salary": "s.salary", "dept": "s.dept",
                         "updated_at": "s.updated_at"})
 .whenMatchedDelete(condition="s.is_deleted = true")
 .whenNotMatchedInsertAll()
 .execute())
```

The three rules of production MERGE:

1. **Dedupe the source first** — duplicate keys in `updates` → "multiple source rows matched" error; apply the [latest-per-key window](08_Window_Functions.md) before merging.
2. **Idempotency check**: re-running the same MERGE with the same source converges (same end state) — which makes retries safe ([the property that matters](../04_ETL_ELT/01_ETL_vs_ELT.md)).
3. Narrow the match: `"t.id = s.id AND t.date >= '...'"` — a partition-pruned merge condition avoids scanning the whole target.

### Scoped atomic overwrite (the other idempotent load)

```python
(df_today.write.format("delta").mode("overwrite")
   .option("replaceWhere", "sale_date = '2026-07-19'")
   .saveAsTable("silver.sales"))          # rewrites exactly that day, atomically
```

### Maintenance

```python
spark.sql("OPTIMIZE silver.sales ZORDER BY (customer_id)")  # compact small files + co-locate
spark.sql("VACUUM silver.sales")                            # purge unreferenced files (default: >7 days old)
```

`OPTIMIZE` fixes [small files](Spark_Processing.md) from streaming/frequent MERGEs; Z-ORDER clusters a high-cardinality filter column for data skipping ([why](../00_Fundamentals/02_OLAP_Storage.md)). Newer Databricks: **liquid clustering** (`CLUSTER BY`) replaces both partitioning and Z-order for most new tables, and **predictive optimization** runs OPTIMIZE/VACUUM for you.

---

## Level 3 — Pro corner

### How the log actually works (interview classic)

`_delta_log/` holds numbered JSON commits (`000...012.json`) + periodic Parquet checkpoints; each commit lists files **added** and **removed**. A reader takes the latest checkpoint + subsequent commits = the exact file set of that version — that's why readers never see half-written data (uncommitted files simply aren't in the log) and why time travel is just "replay to an older commit." Writers use **optimistic concurrency**: conflicting simultaneous commits → one wins, the other gets `ConcurrentAppendException` and should retry ([lakehouse transactions](../01_SQL/12_SQL_DCL_TCL.md)). Two streams appending is fine; two jobs rewriting the same partition is a design smell.

### VACUUM vs time travel — the retention triangle

Time travel needs old files; VACUUM deletes old files. Defaults: `delta.deletedFileRetentionDuration` 7 days — VACUUM past that kills older time travel *and* any reader still on an old snapshot. Decide retention per table class (audit tables: long; churny staging: short), and never disable the safety check casually. Costs: skipping VACUUM on high-churn tables silently doubles/triples storage ([blob versioning interplay](../03_Data_Storage/02_Azure_Blob_Storage.md) — don't stack both).

### Constraints, CDF, and the features worth knowing exist

```python
spark.sql("ALTER TABLE silver.employees ADD CONSTRAINT pos_salary CHECK (salary > 0)")
spark.sql("ALTER TABLE silver.employees ALTER COLUMN id SET NOT NULL")
```

- **Change Data Feed** (`delta.enableChangeDataFeed = true`): read row-level changes between versions (`table_changes('t', 12, 15)`) — build incremental downstream loads without diffing ([CDC concepts](../04_ETL_ELT/01_ETL_vs_ELT.md)).
- **Deletion vectors**: DELETE/UPDATE mark rows instead of rewriting whole files — massive win for GDPR deletes on big tables.
- **Column mapping**: enables rename/drop column without rewriting data ([DDL note](../01_SQL/04_SQL_DDL.md)).
- **UniForm**: expose a Delta table with Iceberg metadata for cross-engine readers ([format war détente](../00_Fundamentals/06_Big_Data_Evolution_Timeline.md)).

### Field-tested notes

- **Streaming + MERGE = small-file factory** — schedule OPTIMIZE (or auto-compaction table properties: `delta.autoOptimize.*`).
- MERGE performance is a [join problem](07_Joins.md): source deduped and small → broadcast; match condition partition-scoped; target Z-ordered/clustered on the merge key.
- `overwriteSchema=true` with `mode("overwrite")` replaces the *schema itself* — powerful for intentional rebuilds, catastrophic as a copy-paste habit.
- DML on Delta is still big-data DML: an unpartitioned `DELETE WHERE date < X` on 10 TB rewrites files galore (pre-deletion-vectors) — design retention as partition drops or DV-enabled deletes.
- History is not a backup: `RESTORE` can't survive a VACUUM'd version and `_delta_log` corruption is real — critical tables still get [cross-account protection](../03_Data_Storage/02_Azure_Blob_Storage.md).

## Checkpoint

1. Implement a daily [SCD2](../01_SQL/13_SQL_Warehouse.md) dimension load with MERGE (expire changed rows, insert new versions).
2. A crashed job left the table... in what state, and why? What does the retry need to be safe?
3. Storage for a streaming target tripled in a month — the two likeliest causes and their fixes?

Next: continuous pipelines → [13 — Structured Streaming](13_Structured_Streaming.md).

---

## Further Learning — Docs & Videos

**Documentation**
- Delta Lake docs: https://docs.delta.io/latest/index.html
- Delta Lake quickstart: https://docs.delta.io/latest/quick-start.html
- Databricks Delta Lake: https://docs.databricks.com/en/delta/index.html

**Videos**
- Delta Lake with PySpark tutorial: https://www.youtube.com/results?search_query=delta+lake+pyspark+tutorial
- Delta Lake time travel and merge: https://www.youtube.com/results?search_query=delta+lake+time+travel+merge+pyspark
