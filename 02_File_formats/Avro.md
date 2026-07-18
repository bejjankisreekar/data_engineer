# Avro

## What is Avro?

Avro is a row-based file format built for systems that write a lot of data quickly and need the structure of that data to change safely over time.

Like [Parquet](Parquet.md), Avro stores its schema (the list of columns and their types) inside the file. Unlike Parquet, Avro stores data row-by-row rather than column-by-column — the same layout as [CSV](CSV.md), just in a compact binary form instead of plain text.

---

## Row Storage, Refresher

Avro (conceptually)

```
101, John, IT, 60000
102, Alice, HR, 50000
103, David, IT, 65000
```

Each full row is written together, one after another. That makes Avro efficient when you need to write or read *entire records* — the opposite scenario from Parquet's "I only need one column out of fifty."

---

## Why "schema evolution" matters

Analogy: imagine a paper form that a company has used for years to register new employees. One day, HR adds a new field: "Emergency Contact." Old, already-filed forms don't have that field — but new forms do. A good filing system needs to handle both old and new forms without breaking.

That's exactly the problem Avro solves for data. Systems that produce a constant stream of records (like an app logging every user click) evolve over time — new fields get added, some get removed. Avro lets old and new versions of a schema coexist, so a reader built for the new schema can still make sense of records written under the old one, and vice versa.

---

## Advantages

- Compact, efficient binary format
- Fast to write (good for streaming and logging systems)
- Schema travels with the data
- Excellent schema evolution support (add/remove/rename fields safely)
- Language-independent (Java, Python, and others can all read it)

---

## Disadvantages

- Not human-readable (unlike CSV/JSON)
- Slower than Parquet for analytical queries that only need a few columns
- Less common in BI/reporting tools than Parquet

---

## Used In

- Apache Kafka (streaming message data)
- Event logging pipelines
- Systems where records are written constantly and schemas change over time

---

## Azure Usage

- Azure Event Hubs and Kafka-compatible streaming pipelines often produce Avro-encoded messages
- Azure Data Factory and Databricks can both read and write Avro files
- Commonly used as a "landing" format for streaming data before it's converted to Parquet for analytics

---

## Avro vs Parquet, in one line

Avro is optimized for **writing whole records quickly and evolving schema over time** (streaming). Parquet is optimized for **reading specific columns quickly across huge datasets** (analytics). See [File_Format_Comparison.md](File_Format_Comparison.md) for the full picture.
