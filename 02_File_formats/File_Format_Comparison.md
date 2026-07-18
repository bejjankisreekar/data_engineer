# File Format Comparison

## Why so many formats?

Each format in this folder was designed to solve a different problem. There's no single "best" format — the right choice depends on what you're about to do with the data: share it with a person, send it through an API, log it at high speed, or analyze billions of rows.

---

## Quick Reference

| Format | Storage Layout | Human Readable | Schema Included | Best For |
|---|---|---|---|---|
| [CSV](CSV.md) | Row-based | Yes | No | Simple sharing, Excel exports, small datasets |
| [JSON](JSON.md) | Row-based (nested) | Yes | No | APIs, config files, nested/flexible data |
| [Avro](Avro.md) | Row-based | No | Yes | Streaming, logging, fast writes, evolving schemas |
| [ORC](ORC.md) | Columnar | No | Yes | Large analytical datasets from the Hive/Hadoop world |
| [Parquet](Parquet.md) | Columnar | No | Yes | Large analytical datasets, the default for Azure/Spark/Databricks |

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
