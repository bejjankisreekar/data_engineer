# JSON (JavaScript Object Notation)

## What is JSON?

JSON stores data as key-value pairs — a label ("key") paired with its value, like a name tag paired with the name written on it (`"Name": "John"`).

Analogy: think of a form with labeled boxes, except some boxes can contain an entire smaller form nested inside them (an "address" box that itself contains "city" and "country" boxes). [CSV](01_CSV.md) can only handle a single flat grid — JSON can handle that nesting.

Example

```json
{
  "EmployeeID":101,
  "Name":"John",
  "Department":"IT",
  "Salary":60000
}
```

Multiple records

```json
[
  {
    "EmployeeID":101,
    "Name":"John"
  },
  {
    "EmployeeID":102,
    "Name":"Alice"
  }
]
```

---

## Advantages

- Flexible
- Supports nested objects
- Supports arrays
- Widely used in APIs

---

## Example

Customer

```json
{
"name":"John",
"address":{
"city":"New York",
"country":"USA"
}
}
```

CSV cannot store nested structures like this.

---

## Used In

- REST APIs
- Configuration files
- Event data
- IoT
- Web applications

---

## Azure Usage

ADF

Databricks

Synapse

Event Hub

Cosmos DB

---

## Where JSON Fits

JSON is the standard shape for data moving between web applications and APIs, but it's rarely the format used for long-term analytical storage — see [File Format Comparison](06_File_Format_Comparison.md) for what it's typically converted into ([Parquet](05_Parquet.md), usually) before large-scale analysis.

---
---

# Part 2 — Advanced

## JSON vs JSON Lines — the distinction that decides splittability

Two different things share the name:

```json
// Standard JSON: ONE array wrapping everything — one parser must read it ALL
[ {"id":1}, {"id":2}, ... 50 million more ... ]
```

```
// JSON Lines (NDJSON): one complete JSON object PER LINE
{"id":1,"event":"click"}
{"id":2,"event":"view"}
```

Big data tooling wants **JSON Lines**: each line parses independently, so files split across [Spark tasks](../06_PySpark/Spark_Processing.md) and a corrupt record kills one line, not the file. Spark's reader assumes JSON Lines by default (`multiLine=True` switches to whole-file parsing — and, like CSV, makes files non-splittable). Kafka events, app logs, and API export dumps are JSON Lines almost universally.

## Working with nested JSON in Spark — the daily verbs

```python
df = spark.read.schema(schema).json(".../events/")

flat = (df
  .select(
     "id",
     F.col("address.city").alias("city"),            # dot-path into structs
     F.explode("items").alias("item"))               # array → one row per element
  .select("id", "city", "item.sku", "item.qty"))
```

- **`explode`** turns arrays into rows (grain change! — row counts multiply, [same math as joins](../01_SQL/07_SQL_Keys_and_Joins.md)); `explode_outer` keeps parents with empty arrays.
- **`from_json`/`to_json`** parse JSON *strings inside columns* — the standard first step for Kafka/Event Hub payloads.
- Deep schemas: define once with `StructType`, or store the DDL string; never let inference guess event schemas in production (same reasoning as [CSV](01_CSV.md)).

## Semi-structured columns: keeping JSON *as* JSON

Sometimes flattening everything is wrong (the payload's long tail changes weekly). Modern engines store JSON natively and query into it:

| Engine | Type/feature | Query syntax |
|---|---|---|
| Databricks (DBR 15+) | **VARIANT** | `payload:device.os` |
| Snowflake | VARIANT | `payload:device.os::string` |
| PostgreSQL | JSONB (indexable!) | `payload->'device'->>'os'` |
| SQL Server / Azure SQL | JSON functions (`JSON_VALUE`) | `JSON_VALUE(payload,'$.device.os')` |

The hybrid pattern pros converge on: **promote the queried-hot fields to typed columns; keep the full payload in a variant/string column** for the unforeseen question ([data types note](../01_SQL/03_SQL_Data_Types.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Schema drift — JSON's superpower and your operational problem

Producers add fields without asking; JSON happily carries them. Your choices, worst to best:

1. **Ignore unknown fields** — silent data loss when the new field matters.
2. **Fail on unknown fields** — every app release breaks the pipeline.
3. **Schema evolution with capture** — read with the known schema *plus* keep raw payload (variant column / bronze files); auto-evolve additive changes (Databricks Auto Loader's `mergeSchema`/schema hints do exactly this), alert on type *conflicts* rather than additions.

The organizational fix outranks the technical one: a **data contract** with the producing team — agreed schema, versioned changes, deprecation windows. JSON's flexibility is where contracts go to die unless someone writes them down.

## JSON's sharp edges at the data layer

- **Numbers are not typed** — `1e309` overflows, big integers exceed JavaScript's 2^53 and arrive rounded from JS producers (IDs as strings, always); `0.1` is still binary floating point. Money in JSON = string + DECIMAL on parse.
- **No dates** — everything is a string; enforce ISO-8601 with timezone (`2026-07-19T14:30:00+05:30`) in the contract or inherit a [timezone archaeology project](../01_SQL/03_SQL_Data_Types.md).
- **Key duplication is legal-ish** — `{"a":1,"a":2}` parses differently per library. Reject at the boundary.
- **null vs absent-key vs empty-string** are three different facts; decide what each means for every consumer (the [three-valued logic](../01_SQL/01_What_is_SQL.md) problem, now with a third state).

## Performance reality

JSON is the most expensive mainstream format to read at scale: text parsing per record, keys repeated in every record (`"EmployeeID":` 50 million times), no column pruning, ~2–5× Parquet's size even gzipped. Numbers to carry in your head: parsing JSON is commonly **10× the CPU** of reading the same data as Parquet. Hence the invariant pipeline shape: `API/Kafka (JSON) → bronze (raw JSON, immutable) → silver (typed Parquet/Delta)` — JSON at the edges, columnar in the middle ([medallion](../04_ETL_ELT/01_ETL_vs_ELT.md)).

## Field-tested gotchas

- A single pretty-printed (multi-line) file in a JSON-Lines folder poisons the read — producers must not mix; validate.
- `explode` on a null array drops the whole row silently — `explode_outer` unless you mean inner-join semantics.
- Spark's corrupt-record column only appears if the schema includes it — configure `columnNameOfCorruptRecord` *and* add it to the schema, or bad records vanish.
- Deeply nested `SELECT *` into Parquet can create thousand-column schemas nobody wanted — flatten deliberately, at declared depth.
- Compressed `.json.gz` from vendors: same splittability trap as [CSV](01_CSV.md) — many medium files beat one giant one.

## Interview-grade Q&A

- *JSON vs JSON Lines?* Array-wrapped single document vs record-per-line; only the latter splits for parallel processing.
- *How do you handle a payload whose schema changes weekly?* Bronze raw retention + typed promotion of hot fields + additive auto-evolution + drift alerts + a producer contract.
- *Why do JSON numeric IDs arrive corrupted?* JS producers round beyond 2^53 — contract them as strings.
- *Why not store analytics tables as JSON?* Per-record parsing, repeated keys, no pruning/pushdown — 10× the cost of columnar for every query, forever.