# File Format Comparison

## Why so many formats?

Each format in this folder was designed to solve a different problem. There's no single "best" format — the right choice depends on what you're about to do with the data: share it with a person, send it through an API, log it at high speed, or analyze billions of rows.

---

## Quick Reference

| Format | Storage Layout | Human Readable | Schema Included | Best For |
|---|---|---|---|---|
| [CSV](01_CSV.md) | Row-based | Yes | No | Simple sharing, Excel exports, small datasets |
| [JSON](02_JSON.md) | Row-based (nested) | Yes | No | APIs, config files, nested/flexible data |
| [Avro](03_Avro.md) | Row-based | No | Yes | Streaming, logging, fast writes, evolving schemas |
| [ORC](04_ORC.md) | Columnar | No | Yes | Large analytical datasets from the Hive/Hadoop world |
| [Parquet](05_Parquet.md) | Columnar | No | Yes | Large analytical datasets, the default for Azure/Spark/Databricks |

---

## The two big questions to ask

**1. Will a human ever need to open this file directly?**
If yes (a report someone downloads and opens in Excel, a small config file someone hand-edits), lean toward CSV or JSON. Columnar binary formats like Parquet and ORC are not readable outside specialized tools.

**2. Are you writing records one at a time, or querying millions of records at once?**
- Writing constantly, one record at a time (app logs, sensor data, streaming events): row-based formats like Avro fit naturally.
- Querying a huge table but only needing a handful of columns (analytics, reporting, BI dashboards): columnar formats like Parquet or ORC are dramatically faster, because they skip reading columns you don't need.

---

## A typical pipeline uses more than one format

It's common for the *same* data to pass through several formats on its journey:

```
Source App               →  JSON (API response)
Streaming Ingestion       →  Avro (Kafka / Event Hubs)
Data Lake (raw layer)     →  Parquet (converted for analytics)
Reporting / BI            →  Read directly from Parquet
```

Nobody picks one format for an entire company — the format changes as the data moves from "being produced" to "being analyzed."

---

## Real World Example

A retail company's website logs every click as JSON (flexible, easy for developers to produce). Those click events stream through Kafka as Avro (efficient for high-volume writes). Once a day, a pipeline converts a day's worth of Avro files into a single Parquet file in the data lake, because analysts querying "average time on page last month" only need two or three columns out of dozens — and Parquet lets them read just those columns instead of the whole log.

---
---

# Part 2 — Advanced

## The numbers behind the recommendations

Representative figures for the *same* 10 GB of tabular data (orders of magnitude, not benchmarks):

| Format | Size on disk | "Sum one column" scan | Splittable when compressed? |
|---|---|---|---|
| CSV | 10 GB (2 GB gzipped) | Reads/parses all 10 GB | gzip: ❌ |
| JSON Lines | 15–25 GB | Reads/parses everything, keys included | gzip: ❌ |
| Avro (snappy) | 3–4 GB | Reads all rows (row format) | ✅ |
| Parquet/ORC (snappy/zstd) | 1–2 GB | Reads ~one column ± skipped chunks — often < 100 MB | ✅ (natively chunked) |

Two structural reasons, worth internalizing once: **(1)** text formats re-parse characters and repeat field names per record; binary formats don't. **(2)** row formats must read whole records; columnar formats read requested columns and use min/max stats to skip chunks ([columnar internals](../00_Fundamentals/02_OLAP_Storage.md), [Parquet anatomy](05_Parquet.md)).

## The decision tree pros actually use

```
Is a human hand-editing/opening it?            → CSV (small) / JSON (config)
Is it crossing an API/app boundary?            → JSON (the lingua franca)
Is it in-flight on a message bus at volume?    → Avro (or Protobuf) + Schema Registry
Is it at rest for analytics?                   → Parquet — inside Delta/Iceberg, not bare
Is it a Hive-era estate you inherited?         → ORC (until migrated)
```

Note what's *not* a criterion: loyalty. The same dataset legitimately changes format at each hop — formats are optimized for a **position in the pipeline**, not for a company.

## The missing row: table formats

This folder compares *file* formats; production lakes wrap the columnar ones in a **table format** — Delta Lake / Iceberg / Hudi — adding the transaction log, ACID commits, schema enforcement, and time travel that raw folders of files lack ([why that matters](../06_PySpark/Why_Spark_Why_Databricks.md), [format war](../00_Fundamentals/06_Big_Data_Evolution_Timeline.md)). Interview one-liner: *"Parquet is how bytes are laid out; Delta is how a set of Parquet files behaves like a database table."*

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Cost framing — formats are money

On pay-per-scan engines and object storage, format choice is a line item: 10 GB CSV scanned by 50 daily queries = 500 GB/day billed scans; the same data as partitioned Parquet might bill 5 GB/day — a ~100× recurring difference from a one-time conversion job. Storage tells the same story (10 GB → 1.5 GB). When pitching a "boring" conversion pipeline to stakeholders, pitch it in currency, not milliseconds.

## Conversion boundaries are validation boundaries

Every format hop is where corruption either gets caught or gets laundered into "clean" data. The professional pattern at each conversion:

- **Reconcile counts and checksums** across the boundary (rows in = rows out + quarantined; [SQL instrumentation](../01_SQL/08_SQL_Aggregate_Functions.md)).
- **Resolve types explicitly** — CSV/JSON's stringly-typed values become real DECIMAL/TIMESTAMP here, per declared schema, never by inference ([type mapping tax](../01_SQL/03_SQL_Data_Types.md)).
- **Keep the raw** — bronze retains the original bytes; conversions are re-runnable, so parser bugs are recoverable ([medallion](../04_ETL_ELT/01_ETL_vs_ELT.md)).
- Make the conversion [idempotent](../01_SQL/05_SQL_DML.md) — the same input file re-processed must not double its rows.

## Choosing when requirements conflict (the senior tiebreakers)

- *Analysts want CSV exports; engineering wants Parquet* → both: Parquet is the system of record, CSV is a generated **product** at the edge.
- *Streaming team wants JSON "for debuggability"* → Avro/registry for the pipe, a JSON tap/console consumer for humans; debuggability is a tool concern, not a wire-format concern.
- *"Let's standardize the whole company on one format"* → resist; standardize **per layer** (JSON at APIs, Avro in flight, Delta at rest) and standardize the *contracts* between layers instead.
- Vendor sends whatever they send → your boundary, your rules: land as-is in bronze, convert immediately, validate loudly ([CSV defense checklist](01_CSV.md)).

## Field-tested gotchas

- The pipeline example above says "a single Parquet file" — at real scale that's an anti-pattern; write *appropriately sized multiple* files per partition ([file sizing](../06_PySpark/Spark_Processing.md)).
- Compressed text (`.csv.gz`, `.json.gz`) silently serializes reads to one task per file — the most common "why is my 8-node cluster idle" answer.
- Format conversions can silently lose precision (JSON floats → double, INT96 timestamps, CSV leading zeros) — round-trip tests on edge values belong in CI.
- "Human readable" stops being true at a million rows — past exploration size, *tooling* (DuckDB, `parquet-tools`) reads binary formats more faithfully than eyes read text.

## Interview-grade Q&A

- *Design the format journey for clickstream analytics.* JSON at the app → Avro + registry through Event Hubs/Kafka → bronze raw → silver/gold Delta (Parquet), partitioned by date, compacted.
- *One dataset, four formats — why?* Each hop optimizes a different bottleneck: producer ergonomics, wire efficiency + evolution, audit/rawness, scan performance.
- *What does a table format add over Parquet?* Transactions, concurrent-writer safety, schema enforcement/evolution, time travel, MERGE — database semantics over files.
- *How do you justify a format migration to management?* Scan-cost and storage numbers before/after, plus incident classes eliminated (partial writes, schema drift) — money and risk, not elegance.
