# Avro

## What is Avro?

Avro is a row-based file format built for systems that write a lot of data quickly and need the structure of that data to change safely over time.

Like [Parquet](05_Parquet.md), Avro stores its schema (the list of columns and their types) inside the file. Unlike Parquet, Avro stores data row-by-row rather than column-by-column — the same layout as [CSV](01_CSV.md), just in a compact binary form instead of plain text.

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

Avro is optimized for **writing whole records quickly and evolving schema over time** (streaming). Parquet is optimized for **reading specific columns quickly across huge datasets** (analytics). See [06_File_Format_Comparison.md](06_File_Format_Comparison.md) for the full picture.

---
---

# Part 2 — Advanced

## The schema, concretely

Avro schemas are JSON documents; the data itself is compact binary (no field names repeated per record — unlike [JSON](02_JSON.md)):

```json
{
  "type": "record", "name": "Employee", "namespace": "com.acme.hr",
  "fields": [
    {"name": "EmployeeID", "type": "long"},
    {"name": "Name",       "type": "string"},
    {"name": "Department", "type": ["null", "string"], "default": null},
    {"name": "Salary",     "type": {"type": "bytes", "logicalType": "decimal", "precision": 10, "scale": 2}}
  ]
}
```

Details that matter: nullable = a **union with null** (`["null","string"]`) plus a default; **logical types** layer dates/timestamps/decimals over base types (check what your consumer honors — decimals-as-bytes have burned many pipelines); an Avro *file* embeds the schema in its header, but a Kafka *message* does not — which leads to…

## Schema Registry — the production pattern

Sending the schema with every Kafka message would waste most of the bandwidth. Instead:

```
Producer ──registers schema──▶ Schema Registry (id: 42)
Producer ──sends──▶ [magic byte][schema id 42][binary avro payload]
Consumer ──fetches schema 42 (cached)──▶ decodes payload
```

The registry (Confluent SR, Azure Schema Registry in Event Hubs) becomes the **enforcement point**: producers registering an incompatible schema get *rejected at publish time* — turning "consumer crashed at 2am" into "producer build failed at 2pm." That shift-left is the entire operational value.

## Evolution rules — what's actually safe

Compatibility is checked between writer schema and reader schema:

| Change | Backward compatible? (new reader, old data) |
|---|---|
| Add field **with default** | ✅ |
| Add field without default | ❌ — old records can't supply it |
| Remove field that had a default | ✅ |
| Rename field | ❌ directly — use `aliases` |
| Widen type (int→long, float→double) | ✅ (promotion rules) |
| Change type otherwise | ❌ |

Registry modes: `BACKWARD` (new readers read old data — the common default; lets consumers upgrade first), `FORWARD` (old readers read new data), `FULL` (both). The team decision "which mode, per topic" *is* your streaming data contract.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Where Avro sits in a modern Azure stream

```
App → Event Hubs/Kafka (Avro + Schema Registry)
        → Spark Structured Streaming (from_avro with registry lookup)
          → bronze Delta (raw)  → silver typed Delta
```

Avro owns the **in-flight** leg; it stops being the storage format at the first Delta write ([Parquet](05_Parquet.md) columnar wins at rest). The legacy pattern of landing `.avro` files in the lake ("Event Hubs Capture") persists in many estates — treat those as bronze input, convert promptly; querying raw Avro folders analytically pays row-format prices on every scan.

## Avro vs Protobuf — the streaming format rivalry

The real-world alternative isn't Parquet (different layer) but **Protobuf** (and JSON Schema) on the wire:

| | Avro | Protobuf |
|---|---|---|
| Schema handling | Resolved at runtime (registry/file header) | Compiled into code (codegen) |
| Evolution ergonomics | Rich resolution rules, defaults | Field-number discipline, `optional` semantics |
| Ecosystem | Kafka/data engineering heartland | gRPC/microservices heartland |

Both work with schema registries; teams usually inherit whichever their platform standardized on. The senior point: **the registry + compatibility policy matters far more than which binary format you picked.**

## Field-tested gotchas

- **Union type sprawl** — lazily typing fields as `["null","string","long"]` pushes the type decision onto every consumer forever; unions beyond nullable are a smell.
- **Default ≠ business default** — `"default": null` satisfies evolution rules but downstream still must decide what null *means*; evolution-safe is not semantics-safe.
- Timestamp logical types: `timestamp-millis` vs `-micros` mismatches between producer libs and Spark readers shift or truncate times silently ([timezone discipline](../../02_Databases/SQL/03_SQL_Data_Types.md)).
- Event Hubs Capture writes Avro with the *payload as a bytes field* (body) — you still must parse the body (often JSON inside Avro!); many pipelines double-parse without realizing.
- One registry per environment, schemas promoted with code — a prod producer pointing at the dev registry is a subtle, recurring outage.

## Interview-grade Q&A

- *Why Avro for Kafka but Parquet for the lake?* Write-optimized whole-record row format + registry-governed evolution in flight; read-optimized columnar at rest ([row vs column](../../01_Foundations/Fundamentals/01_OLTP_Storage.md)).
- *How does a consumer decode a message written with an older schema?* Schema resolution: reader schema + writer schema (fetched by id) reconciled via defaults/promotions.
- *What makes a schema change "safe"?* Compatible under the topic's registry mode — e.g. BACKWARD: only additions-with-defaults and removals-of-defaulted fields.
- *Where does schema enforcement belong in streaming?* At produce time via the registry — reject bad schemas before they enter the pipe, not after consumers crash.

---

## Further Learning — Docs & Videos

**Documentation**
- Apache Avro official docs: https://avro.apache.org/docs/
- Avro specification: https://avro.apache.org/docs/current/specification/
- Spark Avro data source: https://spark.apache.org/docs/latest/sql-data-sources-avro.html

**Videos**
- Apache Avro explained (row-based, schema evolution): https://www.youtube.com/results?search_query=apache+avro+explained+schema+evolution
- Avro vs Parquet vs ORC: https://www.youtube.com/results?search_query=avro+vs+parquet+vs+orc
