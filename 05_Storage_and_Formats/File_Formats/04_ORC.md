# ORC (Optimized Row Columnar)

## What is ORC?

ORC is a columnar file format, in the same family as [Parquet](05_Parquet.md) — data is stored column by column instead of row by row, and the schema is stored inside the file. ORC was created in the Hadoop/Hive ecosystem, while Parquet grew up around Spark; today the two formats solve the same problem in very similar ways.

---

## Column Storage, Refresher

EmployeeID column

```
101
102
103
```

Salary column

```
60000
50000
65000
```

Just like Parquet, if a query only needs the Salary column, ORC only has to read that column's data — not the entire table.

---

## What makes ORC distinct

- **Built-in indexes** — ORC stores lightweight statistics (min/max values, row counts) for chunks of each column, so a query can skip entire sections of a file that can't possibly contain a match. Think of it like a book's index telling you a topic definitely isn't on pages 50–90, so you never open those pages.
- **Strong compression** — ORC typically compresses slightly better than Parquet on similar data, at the cost of a bit more CPU time to read/write.
- **Deep Hive integration** — ORC was designed specifically to work well with Apache Hive, a SQL-like query engine for Hadoop.

---

## Advantages

- Highly compressed
- Fast for analytical queries (column pruning, like Parquet)
- Built-in indexing skips irrelevant data automatically
- Good for very large, append-heavy datasets

---

## Disadvantages

- Less universally supported outside the Hadoop/Hive ecosystem than Parquet
- Smaller community and tooling support in the Azure/Spark/Databricks world compared to Parquet
- Not human-readable

---

## Used In

- Apache Hive
- Hadoop-based data lakes
- Legacy big-data platforms migrating toward Azure

---

## Azure Usage

- Azure Synapse and Databricks can both read ORC files, mainly to support data migrated from existing Hadoop/Hive systems
- New Azure projects typically choose Parquet by default; ORC mainly shows up when importing from an existing on-premises Hadoop estate

---

## ORC vs Parquet, in one line

Both are columnar and serve the same purpose. Parquet has become the default choice in most new Azure/Spark/Databricks projects, while ORC is more common if your data already comes from a Hive/Hadoop system. See [06_File_Format_Comparison.md](06_File_Format_Comparison.md) for a full side-by-side.

---
---

# Part 2 — Advanced

## Inside an ORC file

```
┌────────────────────────────────────────┐
│ Stripe 1 (default ~64–256 MB)           │
│   Index data   (min/max per ~10k rows)  │
│   Row data     (columns, encoded)       │
│   Stripe footer(encodings, locations)   │
├────────────────────────────────────────┤
│ Stripe 2 ...                            │
├────────────────────────────────────────┤
│ File footer  (schema, stripe list,      │
│               column stats for file)    │
│ Postscript   (compression info)         │
└────────────────────────────────────────┘
```

Three levels of statistics — file, stripe, and **row group (every 10,000 rows)** — power predicate pushdown: `WHERE salary > 90000` skips any unit whose max < 90000. Same playbook as [Parquet's row groups/pages](05_Parquet.md) and the [zone maps idea](../../01_Foundations/Fundamentals/02_OLAP_Storage.md); ORC's finer-grained default indexing is its historical differentiator.

- **Encodings**: dictionary, RLE, delta — chosen per column chunk automatically.
- **Compression**: zlib/snappy/zstd applied *on top* of encodings.
- **Bloom filters** (optional, per column): probabilistic "value definitely absent" checks — worthwhile on selective point lookups (`WHERE order_id = X`) where min/max ranges are too wide to help.

## ORC ACID — the feature that previewed the lakehouse

Hive built full **transactional tables** on ORC years before Delta/Iceberg went mainstream: base files + **delta files** (insert/update/delete records) merged at read time, compacted in the background — conceptually the same mechanics Delta Lake later popularized ([evolution timeline](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)). If you inherit a Hive estate, know that "transactional ORC tables" cannot be read as plain ORC folders — they need Hive-aware readers or a migration step, a classic trap when lifting Hive data into [ADLS](../Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The honest ORC vs Parquet verdict

Benchmarks flip-flop by dataset and engine version; the differences that actually decide are ecosystem, not physics:

- **Engine investment** — Spark's vectorized readers, Delta Lake, Databricks Photon, Snowflake external tables, DuckDB: all optimize Parquet first. Hive/Trino treat ORC as a first-class citizen.
- **Table formats chose Parquet** — Delta *requires* it; Iceberg supports ORC but the ecosystem runs Parquet. That decided the war more than any benchmark.
- Compression: ORC often a few percent smaller; irrelevant next to a missed pushdown or oversized files.

Pro guidance: new work → Parquet/Delta, no debate. ORC expertise is **migration capital** — valuable precisely when moving a Hive estate to the lakehouse.

## Migrating ORC estates (the practical notes)

- Non-transactional ORC: Spark reads it natively — `spark.read.orc(...)` → write Delta; done in bulk with schema checks.
- Transactional Hive ORC: export via Hive (major compaction first) or Hive-ACID-aware readers; don't point Spark at the raw folders.
- Preserve partition layouts (`year=2026/...`) during conversion so downstream pruning survives; revisit [file sizing](../../03_Programming/PySpark/Spark_Processing.md) — Hive-era small files should be compacted in the same pass.
- Validate with row counts + column checksums per partition ([reconciliation habit](../../02_Databases/SQL/13_SQL_Warehouse.md)).

## Field-tested gotchas

- ORC's schema evolution is positional in older Hive versions — column *renames* via metadata could silently misalign data; verify by content, not just schema, after migrations.
- Mixed ORC versions in one folder (years of Hive writers) can break vectorized readers — fall back to non-vectorized to diagnose, then compact/rewrite.
- Bloom filters inflate file size and write time — add them for measured point-lookup patterns, not "just in case."
- Stats-based skipping only works if data is **sorted/clustered** on the filtered column within files — random layout = min/max ranges that never exclude anything (same reason [Z-ordering](../../03_Programming/PySpark/Spark_Processing.md) exists for Parquet/Delta).

## Interview-grade Q&A

- *How does ORC skip data?* Three-tier min/max stats (file/stripe/10k-row groups) + optional bloom filters evaluated against predicates before reading.
- *Why did Parquet win despite ORC's strong design?* Ecosystem gravity: Spark/Delta/warehouse vendors standardized on Parquet; table formats sealed it.
- *You inherit 200 TB of Hive ORC — plan?* Classify transactional vs plain, compact, bulk-convert to Delta preserving partitions, checksum-reconcile, then repoint consumers.
- *When would you still choose ORC today?* Staying on a Hive/Trino-centric platform where it's the native optimized path.

---

## Further Learning — Docs & Videos

**Documentation**
- Apache ORC official site: https://orc.apache.org/
- ORC specification: https://orc.apache.org/specification/
- Spark ORC data source: https://spark.apache.org/docs/latest/sql-data-sources-orc.html

**Videos**
- Apache ORC file format explained: https://www.youtube.com/results?search_query=apache+orc+file+format+explained
