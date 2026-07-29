# Parquet

## What is Parquet?

Parquet is a columnar storage file format developed for Big Data.

Unlike CSV, data is stored column by column instead of row by row.

Analogy: imagine a library that, instead of shelving books individually, keeps a separate index card box for every single fact — one box just for "titles," one just for "authors," one just for "publish years." If someone only wants a list of publish years, they can flip through one box instead of pulling every book off every shelf. That's the advantage columnar storage gives over row storage.

---

## Row Storage

CSV

```
101 John IT 60000
102 Alice HR 50000
103 David IT 65000
```

---

## Column Storage

EmployeeID

```
101
102
103
```

Name

```
John
Alice
David
```

Department

```
IT
HR
IT
```

Salary

```
60000
50000
65000
```

---

## Why is this faster?

Suppose you only need Salary.

CSV

Reads entire file.

Parquet

Reads only Salary column.

Huge performance improvement.

---

## Advantages

- Highly compressed — repeated values (like a Department column full of "IT," "IT," "HR") squeeze down efficiently, since similar values are stored next to each other (see [Glossary](../../GLOSSARY.md#storage-and-files))
- Very fast
- Schema included — the file itself records what columns exist and their types, so no separate documentation is needed to read it
- Column pruning — a query only reads the specific columns it asks for, ignoring the rest of the table entirely
- Predicate pushdown — if a query filters for `Salary > 60000`, Parquet can skip entire chunks of data upfront, without reading each individual row and checking it one by one, because it keeps track of the minimum/maximum value stored in each chunk
- Great for analytics

For a side-by-side against the other row/columnar formats in this folder, see [File Format Comparison](06_File_Format_Comparison.md).

---

## Used In

Databricks

Spark

Azure Synapse

Data Lakes

Delta Lake

Machine Learning

---

## Azure Usage

Most Azure Data Engineering projects store data in Parquet format.

---
---

# Part 2 — Advanced

## Inside a Parquet file

```
┌─────────────────────────────────────────────┐
│ Row group 1 (target ~128 MB)                 │
│   Column chunk: EmployeeID                   │
│     Page 1 (~1 MB): encoded + compressed     │
│     Page 2 ...                               │
│   Column chunk: Name                         │
│   Column chunk: Salary                       │
├─────────────────────────────────────────────┤
│ Row group 2 ...                              │
├─────────────────────────────────────────────┤
│ FOOTER: schema, row group locations,         │
│         min/max/null-count stats PER column  │
│         chunk (and per page)                 │
└─────────────────────────────────────────────┘
```

How a query uses this: read footer → **column pruning** (only requested columns' chunks) → **predicate pushdown** (skip row groups whose min/max exclude the filter) → decode only surviving pages. A `SELECT SUM(amount) WHERE date='2026-07-19'` on a 1 TB dataset may physically read a few GB.

- **Encodings before compression**: dictionary (low-cardinality strings), RLE/bit-packing, delta — then snappy (default, fast) / zstd (smaller, modern choice) / gzip per page ([encoding theory](../../01_Foundations/Fundamentals/02_OLAP_Storage.md)).
- **Nested data** works (unlike naive columnar): structs flatten to dotted columns; arrays/maps use repetition/definition levels (the Dremel model) — so [JSON-shaped data](02_JSON.md) stores columnar too.
- Row-group size trades pruning granularity vs metadata overhead; the ~128 MB default aligns with one [Spark task](../../06_Programming/PySpark/Spark_Processing.md) per row group.

## Writing Parquet well (where pipelines go right or wrong)

- **File size**: target 100 MB–1 GB; thousands of KB-size files = footer-reading overhead dominating scans (the [small files problem](../../01_Foundations/Fundamentals/05_Hadoop_Architecture.md) reborn).
- **Sort/cluster before writing** on your dominant filter column — min/max skipping only excludes chunks if similar values are co-located; random order = useless statistics (why Delta `ZORDER`/liquid clustering exist).
- **Dictionary + high cardinality**: a column of UUIDs makes dictionaries explode and fall back — expected, but don't dictionary-sort on it.
- **Types**: write proper DECIMAL/timestamp logical types, not strings — "numbers as strings in Parquet" wastes the format ([type mapping tax](../../02_Databases/SQL/03_SQL_Data_Types.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Parquet is the storage layer of everything now

The quiet standardization: Delta Lake **is** Parquet files + a transaction log; Iceberg/Hudi wrap Parquet similarly; Snowflake/BigQuery export it; DuckDB/pandas/Polars read it natively; Power BI ingests it. Consequence: Parquet fluency is really *lakehouse* fluency — and "which table format" debates ([Delta vs Iceberg](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)) are about the metadata layer above identical Parquet bytes.

## Schema evolution at the Parquet level

Parquet files are immutable; "evolution" happens across files in a table: adding columns is safe (old files return nulls); renames are *new columns* physically (why Delta needs column-mapping mode to fake them); type changes require rewrites. The merge-on-read cost: a table of 10,000 files with drifted schemas makes every reader reconcile footers — periodic compaction/rewrite is schema hygiene, not just size hygiene.

## Reading Parquet like an investigator

When "the lake is slow," inspect the files, not just the query:

```python
import pyarrow.parquet as pq
meta = pq.ParquetFile("part-0001.parquet").metadata
meta.num_row_groups, meta.row_group(0).num_rows
meta.row_group(0).column(3).statistics      # min/max/nulls — is skipping even possible?
```

Diagnostics this answers: are files tiny (compaction needed)? one giant row group (no pruning)? statistics missing (writer misconfigured)? column order/types drifted across files? Databricks' `DESCRIBE DETAIL` / `OPTIMIZE` metrics answer the same at table level.

## Field-tested gotchas

- **Overwriting a Parquet folder non-atomically** (plain `overwrite` to the same path without a table format) leaves readers a window of half-deleted files — this failure mode *is* the sales pitch for [Delta](../../06_Programming/PySpark/Why_Spark_Why_Databricks.md).
- Timestamp interop: INT96 legacy timestamps vs `timestamp-millis/micros`, plus session timezones, produce hour-shifted data between engines — pin conventions, test round-trips.
- `coalesce(1)` to make "one nice Parquet file" serializes the write through one task and builds one giant row group — fine for samples, wrong for production ([write patterns](../../06_Programming/PySpark/Spark_Processing.md)).
- Column pruning dies through `SELECT *` views — the physical format can't save a logical habit ([views](../../02_Databases/SQL/10_SQL_Views.md), [DQL](../../02_Databases/SQL/06_SQL_DQL.md)).
- Predicate pushdown works on plain columns, not expressions: `WHERE CAST(ts AS DATE) = X` reads everything ([sargability](../../02_Databases/SQL/06_SQL_DQL.md) — the lake edition).

## Interview-grade Q&A

- *Walk through what happens when Spark reads Parquet with a filter.* Footer → prune columns → row-group stats vs predicate → skip groups → decode surviving pages → (with AQE) adapt downstream plan.
- *Why are many small Parquet files slow?* Per-file open/footer costs and per-file tasks dominate; compaction restores scan efficiency.
- *How does Parquet store nested JSON?* Dremel repetition/definition levels — arrays/structs become columnar streams, preserving pruning.
- *Parquet vs Delta?* Format vs table: Delta adds a transaction log over Parquet for ACID, MERGE, time travel, schema enforcement.
---

## Further Learning — Docs & Videos

**Documentation**
- Apache Parquet official site: https://parquet.apache.org/
- Parquet file format docs: https://parquet.apache.org/docs/
- Spark Parquet data source: https://spark.apache.org/docs/latest/sql-data-sources-parquet.html

**Videos**
- Apache Parquet explained (columnar storage): https://www.youtube.com/results?search_query=apache+parquet+explained+columnar+storage
- Why Parquet is fast: https://www.youtube.com/results?search_query=why+parquet+is+faster+than+csv
