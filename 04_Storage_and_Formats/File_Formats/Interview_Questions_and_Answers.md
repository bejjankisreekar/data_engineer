# 02_File_formats — Interview Questions & Answers

## How to use this file

This file mixes THEORY questions (why row vs. columnar, when to use which format, how schema evolution works) with PRACTICAL questions (PySpark read/write code, debugging a broken load, choosing a format for a scenario). Every question states what it's testing; every answer explains why it's correct, not just what the answer is.

- **[Frequently Asked]** — the comparisons that come up in nearly every data engineering interview: row vs. columnar, CSV vs. Parquet, why Parquet is the default, what predicate pushdown means.
- **[Senior/Experienced]** — Pro-level material: file internals (row groups, stripes), schema registries, the small-files problem, table formats.

---

## Table of Contents

1. [CSV](#1-csv)
2. [JSON](#2-json)
3. [Avro](#3-avro)
4. [ORC](#4-orc)
5. [Parquet](#5-parquet)
6. [File Format Comparison](#6-file-format-comparison)
7. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. CSV

*(full notes: [01_CSV.md](01_CSV.md))*

#### Q1. Why is CSV a poor choice for large-scale analytics, even though it's the most universally supported format? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether "CSV is bad for big data" is backed by a real mechanical reason, not just repeated folklore.
**Answer:** CSV is row-oriented plain text: every query must parse every character of every row, there's no column pruning (reading two columns costs the same as reading all fifty), no predicate pushdown (nothing can be skipped without reading it), and no native types (everything is a string until parsed). It also compresses and splits poorly compared to binary columnar formats. This is correct because it names the four concrete capabilities CSV lacks — pruning, pushdown, typing, splittable compression — that a columnar format like [Parquet](05_Parquet.md) provides, rather than a vague "it's inefficient."

#### Q2. Why should you never use `inferSchema=True` when reading CSV files in a production pipeline? **[Frequently Asked]**
*Why interviewers ask this:* A very common practical PySpark question that also tests data-quality thinking.
**Answer:** Schema inference reads the file an extra time and *guesses* per file — a column like `"00042"` becomes the integer `42` (losing leading zeros, ruinous for postal codes or phone numbers), a column that's numeric today can silently become a string tomorrow the moment one row contains `"N/A"`, and different files in the same folder can infer *different* schemas entirely. The production rule is that schema is a contract you declare explicitly (`spark.read.schema(explicit_schema).csv(...)`), never a guess the engine makes. This is correct because it gives concrete failure examples of inference going wrong, which is what distinguishes a real understanding from repeating "always specify a schema" as an unexplained rule.

#### Q3. A CSV file with an address field like `"Smith, John"` is breaking your pipeline's row count. What's happening, and how do you fix it? **[Frequently Asked]**
*Why interviewers ask this:* Tests real parsing knowledge rather than assuming CSV is "just comma-split."
**Answer:** A naive parser that just splits on commas treats the comma inside the quoted value as a field delimiter, splitting one row into two (or merging rows if a field contains an unescaped newline). The fix is to never parse CSV with a raw `split(',')` — use a real CSV parser configured with the correct quote and escape characters:
```python
df = (spark.read.format("csv")
      .option("header", True)
      .option("quote", '"').option("escape", '"')
      .schema(explicit_schema)
      .load("path/"))
```
This is correct because it identifies the exact failure mechanism (a delimiter character appearing *inside* a quoted value) and the concrete fix (a properly configured parser respecting quoting), rather than "CSV is fragile."

#### Q4. Why is a `.csv.gz` file a parallelism killer in Spark, even though gzip compresses it well? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of splittability, a genuinely important and often-missed performance concept.
**Answer:** Gzip is not a splittable compression format — decompression must start from the beginning of the file, so a single 10 GB `.csv.gz` file can only be read by **one task**, regardless of how many executors the cluster has. The fixes are to use a splittable codec like seekable zstd/bzip2, land many medium-sized gzip files (~100–250 MB each) instead of one giant file, or — the real answer — convert to Parquet at the first pipeline hop, which is natively chunked and splittable. This is correct because it names the actual mechanism (gzip requires sequential decompression from the start) that causes the parallelism loss, not just "gzip is bad."

#### Q5. Design a robust CSV ingestion boundary for a pipeline receiving files from an external vendor. **[Senior/Experienced]**
*Why interviewers ask this:* A realistic "design this ingestion" scenario testing production hardening habits.
**Answer:** Five layers: validate file structure (column count and header names) against a known contract before loading, quarantining files that differ rather than best-effort loading them; use permissive parsing with corrupt-record capture (`mode=PERMISSIVE` + `columnNameOfCorruptRecord`) so bad rows land in a separate column instead of silently vanishing; keep the raw file immutable in a bronze/landing zone so a parsing bug can always be re-run with corrected options; reconcile row counts (lines in the file minus header vs. rows actually loaded) automatically on every file; and convert to Parquet/Delta immediately — CSV's job ends at the ingestion door. This is correct because it treats CSV as an *untrusted external boundary* requiring validation and raw retention, which is the professional posture toward any format you don't control the production of.

---

## 2. JSON

*(full notes: [02_JSON.md](02_JSON.md))*

#### Q6. What's the difference between standard JSON and JSON Lines (NDJSON), and why does big data tooling prefer JSON Lines? **[Frequently Asked]**
*Why interviewers ask this:* A very commonly asked distinction, since the two are easily confused and behave completely differently at scale.
**Answer:** Standard JSON wraps every record in one giant array — `[ {...}, {...}, ... ]` — which means a single parser must read the entire file before it can process any record. JSON Lines writes one complete JSON object per line, so each line parses independently: files split cleanly across parallel tasks, and a corrupt record only breaks one line instead of the whole file. Spark's JSON reader assumes JSON Lines by default; Kafka events, app logs, and API dumps are almost universally JSON Lines. This is correct because it explains *why* the distinction matters for distributed processing (independent parseability = splittability), not just that two formats exist.

#### Q7. Write PySpark code to flatten a nested JSON structure with a `customer.address.city` path and an `items` array into a flat table with one row per line item.
*Why interviewers ask this:* A very common hands-on question testing dot-path navigation and `explode`.
**Answer:**
```python
flat = (df
    .select(
        "order_id",
        F.col("customer.address.city").alias("city"),   # dot-path into nested structs
        F.explode("items").alias("item"))                # array -> one row per element
    .select("order_id", "city", "item.sku", "item.qty"))
```
This is correct because struct fields are accessed with dot-notation directly in `select`, and `explode` is the operation that turns an array column into multiple rows — one per array element — which is also why row counts multiply after an explode, the same grain-change math as a one-to-many join.

#### Q8. A stream of JSON events has a schema that changes weekly as the producing team adds new fields. How do you keep the pipeline from breaking? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real schema-drift handling, a genuinely common production problem with streaming JSON.
**Answer:** Three things together: keep the **raw JSON payload retained in bronze** so nothing is ever truly lost even if parsing choices change later; **promote known, queried-hot fields to typed columns** while allowing additive schema evolution to be auto-merged (e.g. Databricks Auto Loader's `mergeSchema`), alerting only on genuine type *conflicts* rather than every new field; and — the fix that outranks the technical ones — establish a **data contract** with the producing team (agreed schema, versioned changes, deprecation windows), since JSON's flexibility is exactly where undocumented contracts silently rot. This is correct because it layers a technical safety net (bronze retention, additive auto-evolution) with the organizational fix that actually prevents the problem recurring.

#### Q9. Why do numeric IDs sometimes arrive corrupted or rounded when parsing JSON produced by a JavaScript system? **[Senior/Experienced]**
*Why interviewers ask this:* A specific, high-value gotcha that tests deep familiarity with JSON's actual limitations, not textbook knowledge.
**Answer:** JSON numbers aren't typed, and JavaScript — the language JSON's spec is native to — represents all numbers as IEEE-754 doubles, which can only exactly represent integers up to 2^53. A big numeric ID (e.g. a 19-digit Twitter-style snowflake ID) produced by a JS-based system silently rounds once it exceeds that ceiling. The fix is contractually requiring producers to send large IDs as **strings**, not numbers. This is correct because it identifies the specific root cause (JavaScript's double-precision number representation, not "JSON numbers are unreliable" in general) and the concrete contract-level fix.

#### Q10. Why is reading JSON at scale roughly 10× more CPU-expensive than reading the equivalent data as Parquet? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether the candidate can quantify the cost of a design choice, not just qualify it as "slower."
**Answer:** JSON repeats every field name in every record (`"EmployeeID":` written out 50 million times for 50 million rows), requires per-character text parsing for every value, and has no column pruning — a query needing two fields out of fifty still parses all fifty. Parquet stores the schema once, encodes values in a compact binary columnar layout, and reads only the requested columns. This is correct because it names the structural reasons (repeated keys, text parsing, no pruning) behind the cost multiplier rather than presenting the number as an unexplained fact — which is exactly why the standard pipeline shape lands JSON only at the edges (`API/Kafka → bronze raw JSON → silver typed Parquet/Delta`).

---

## 3. Avro

*(full notes: [03_Avro.md](03_Avro.md))*

#### Q11. Why is Avro the standard format for Kafka/Event Hubs messages, while Parquet is the standard for the data lake? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common streaming-architecture questions, testing whether the candidate connects format choice to the actual access pattern at each stage.
**Answer:** Avro is row-based and optimized for writing/reading **whole records quickly** with strong schema-evolution support — exactly what a stream of individual events needs, since each message is written and consumed as one complete unit. Parquet is columnar and optimized for reading **specific columns across huge historical datasets** — exactly what analytical queries at rest need. Using Avro at rest for analytics or Parquet for streaming would apply each format's strength to the wrong problem. This is correct because it maps each format's design (row-oriented write-optimized vs. column-oriented read-optimized) to the actual workload shape at that stage of the pipeline, rather than treating format choice as arbitrary convention.

#### Q12. What is a Schema Registry, and why does it matter for a Kafka pipeline using Avro? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real streaming-architecture experience beyond just knowing Avro's name.
**Answer:** Sending the full schema with every Kafka message would waste most of the bandwidth, so instead a producer registers its schema once with a Schema Registry and sends only a small schema ID with each message; consumers fetch and cache the schema by ID to decode. Critically, the registry becomes the **enforcement point** — a producer registering an incompatible schema change is rejected *at publish time*, turning what would be "a consumer crashed at 2am" into "a producer's build failed at 2pm," a shift-left that catches breaking changes before they ever reach the pipe. This is correct because it explains both the bandwidth-saving mechanism and the (more important) governance role the registry plays, which is the detail that separates knowing Avro exists from understanding why it's operated the way it is.

#### Q13. What Avro schema changes are backward compatible (a new reader can still read old data), and which are not? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real understanding of schema evolution rules, not just "Avro supports evolution."
**Answer:** Backward-compatible changes: adding a field *with a default value* (old records simply supply the default), and removing a field that had a default. Not backward compatible: adding a field with no default (old records can't supply a value for it), and directly renaming a field (though Avro's `aliases` mechanism can work around this). This is correct because it distinguishes the specific rule (defaults are what make additions/removals safe) rather than a blanket "Avro handles schema changes," and it names the exact escape hatch (`aliases`) for the rename case that otherwise breaks compatibility.

---

## 4. ORC

*(full notes: [04_ORC.md](04_ORC.md))*

#### Q14. What is ORC, and how does it compare to Parquet? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether the candidate knows ORC is a real alternative, not just an obscure name, and understands why Parquet still won.
**Answer:** ORC is a columnar file format from the Hadoop/Hive ecosystem, functionally very similar to Parquet — both store data column-by-column, embed schema, and support predicate pushdown via min/max statistics. ORC has finer-grained built-in indexing (statistics down to every 10,000-row group) and often compresses slightly better, but Parquet became the default in modern Azure/Spark/Databricks projects because the entire ecosystem — Delta Lake requires it, Photon optimizes it first, most warehouse vendors export it — standardized around it. This is correct because it acknowledges ORC's genuine technical strengths while correctly identifying *ecosystem standardization*, not raw performance, as the deciding factor — a nuance that shows real awareness rather than a one-sided "Parquet is just better."

#### Q15. You inherit 200 TB of data in Hive-managed transactional ORC tables. What's your migration plan to Delta on Azure? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic senior-level migration scenario testing whether the candidate knows the specific trap in transactional ORC.
**Answer:** First classify the tables — plain ORC folders can be read natively by Spark (`spark.read.orc(...)`) and bulk-converted directly, but **transactional Hive ORC tables cannot be read as plain ORC folders**; they store base files plus delta (insert/update/delete) files merged at read time, requiring a Hive-aware export or a major compaction first. From there: preserve the existing partition layout during conversion so downstream pruning survives, compact small Hive-era files in the same pass, and validate with row counts and column checksums per partition before repointing consumers. This is correct because it flags the specific trap (transactional ORC ≠ readable as plain files) that a migration plan ignoring it would fail on, which is exactly what this scenario is testing for.

---

## 5. Parquet

*(full notes: [05_Parquet.md](05_Parquet.md))*

#### Q16. Why is Parquet the default file format for nearly all modern Azure/Spark/Databricks data engineering projects? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental "why does this exist" questions in the entire course.
**Answer:** Parquet is columnar, so analytical queries touching a handful of columns out of dozens read only those columns' bytes; it embeds its own schema so no external documentation is needed; it supports **predicate pushdown** via per-chunk min/max statistics, letting a query skip entire blocks of data without reading them; and similar values stored contiguously compress far better than row-oriented storage. On top of the file format itself, Delta Lake, Iceberg, and Hudi all use Parquet as their underlying storage, making Parquet fluency effectively lakehouse fluency. This is correct because it lists the concrete mechanisms (pruning, embedded schema, pushdown, compression) rather than a vague "it's optimized for analytics," and connects the file format to the table formats built on top of it.

#### Q17. Walk through exactly what happens when Spark reads a Parquet file with a `WHERE` filter on one column. **[Senior/Experienced]**
*Why interviewers ask this:* A "walk me through" question testing whether the candidate understands the internal read path, a strong signal of real depth.
**Answer:** Spark first reads the file's **footer**, which lists the schema, row-group locations, and per-column-chunk min/max/null-count statistics; using **column pruning**, it identifies and reads only the column chunks the query actually needs; using **predicate pushdown**, it compares the filter against each row group's min/max stats and skips any row group whose range can't possibly contain a match; finally it decodes only the surviving pages. On a 1 TB dataset, a well-filtered aggregate query might physically read only a few GB as a result. This is correct because it walks the actual sequence (footer → prune columns → skip row groups via stats → decode survivors) in order, which is precisely what "walk me through" is testing rather than a summary of Parquet's benefits.

#### Q18. Why can thousands of tiny Parquet files be slower to query than one large file, even though the total data volume is identical? **[Senior/Experienced]**
*Why interviewers ask this:* The classic "small files problem," extremely common in real lake operations and a favorite performance-debugging question.
**Answer:** Every file has fixed overhead — opening the file, reading its footer, and scheduling a task for it — and that overhead is paid *per file*, regardless of how small the file is. Thousands of KB-sized files multiply that fixed cost thousands of times over, dominating total scan time even though the actual data volume hasn't changed. The fix is compaction: targeting 100 MB–1 GB files (e.g. via Delta's `OPTIMIZE`) instead of many tiny ones. This is correct because it identifies the fixed per-file cost as the actual mechanism, distinguishing it from a data-volume problem — a distinction that matters because the fix (compaction) doesn't reduce data, it reduces file *count*.

#### Q19. What happens if you `coalesce(1)` before writing a large Parquet DataFrame "to make one nice file"? **[Senior/Experienced]**
*Why interviewers ask this:* A common but subtly wrong pattern candidates reach for — tests whether they understand the actual cost.
**Answer:** `coalesce(1)` forces the entire write to be serialized through a single task on one executor, and builds one giant row group with no internal parallelism — fine for a small sample export, but a serious anti-pattern at production scale, since it eliminates the parallel write and defeats the row-group-level pruning granularity that makes Parquet fast to *read* later. The correct approach for production writes is letting the data write as multiple appropriately-sized files (targeting 100 MB–1 GB each) via a controlled `repartition(n)` if file count needs adjusting, not collapsing to one file. This is correct because it names the specific cost (serialized single-task write, oversized row group) rather than just "don't do that," which is what a practical follow-up question would probe for.

---

## 6. File Format Comparison

*(full notes: [06_File_Format_Comparison.md](06_File_Format_Comparison.md))*

#### Q20. Design the format journey for a clickstream analytics pipeline, from the web app to the BI dashboard. **[Frequently Asked]**
*Why interviewers ask this:* A comprehensive scenario question that ties every format in this folder together — a very common "design this pipeline" prompt.
**Answer:** The web app emits click events as **JSON** (the natural, flexible format for API/app boundaries); events stream through Kafka/Event Hubs as **Avro with a schema registry** (write-optimized, evolution-governed, efficient on the wire); a pipeline lands the raw Avro/JSON as-is into a **bronze** layer (immutable, for re-processing if parsing changes); the data is then converted into **Parquet inside Delta Lake** for silver/gold, partitioned by date and periodically compacted, which is what BI tools and analysts query directly. This is correct because each format is matched to the actual bottleneck at that specific hop — producer ergonomics (JSON), wire efficiency plus evolution (Avro), and scan performance at rest (Parquet/Delta) — rather than picking one format for the whole pipeline.

#### Q21. Why shouldn't a company try to "standardize on one file format" across its entire data platform? **[Senior/Experienced]**
*Why interviewers ask this:* Tests architectural judgment — a senior-level pushback question against a tempting-sounding but wrong simplification.
**Answer:** Each format is optimized for a specific *position* in the pipeline, not for organizational consistency: JSON is right at API boundaries because it's the universal web lingua franca; Avro is right in-flight on a message bus because it's write-optimized with strong evolution support; Parquet (inside a table format) is right at rest because it's read-optimized for analytics. Forcing one format everywhere means using the wrong tool at some stage — e.g. querying raw JSON at rest pays roughly 10× the CPU of Parquet for the same data. The better standardization target is the **contracts between layers** (agreed schemas, versioning), not the byte format itself. This is correct because it reframes "standardization" onto the thing that actually needs to be consistent (data contracts) rather than the format, which is a genuinely senior distinction.

#### Q22. What does a table format like Delta Lake add on top of Parquet, and why is that addition necessary? **[Senior/Experienced]**
*Why interviewers ask this:* Tests the Parquet-vs-Delta distinction, one of the most frequently asked modern lakehouse questions.
**Answer:** Parquet is purely a *file format* — how bytes are laid out on disk. A table format like Delta Lake adds a **transaction log** on top of a set of Parquet files, giving them database-like behavior: ACID commits (a reader never sees a half-written result), concurrent-writer safety, schema enforcement and evolution, time travel, and `MERGE`/upsert support — none of which raw Parquet files provide on their own. Without a table format, a plain `overwrite` to a Parquet folder is not atomic and can leave readers looking at a half-deleted directory mid-write. This is correct because it draws the exact line the interview one-liner captures: "Parquet is how bytes are laid out; Delta is how a set of Parquet files behaves like a database table."

---

## Rapid-Fire Round

- Q: Row-based or columnar — which format is best for "read two columns out of fifty"? — A: Columnar (Parquet/ORC).
- Q: Row-based or columnar — which is best for "write one full record per event, fast"? — A: Row-based (Avro).
- Q: JSON vs JSON Lines — which splits across parallel Spark tasks? — A: JSON Lines (one object per line).
- Q: What does predicate pushdown let a query engine do? — A: Skip entire blocks/row-groups of data using min/max stats, without reading them.
- Q: Why is gzip-compressed CSV a parallelism problem? — A: It's not splittable — one file = one task.
- Q: What's the recommended target file size for Parquet files? — A: 100 MB–1 GB.
- Q: What causes the "small files problem"? — A: Fixed per-file overhead (open, footer read, task scheduling) multiplied across too many tiny files.
- Q: What does a Schema Registry do for Avro/Kafka? — A: Enforces schema compatibility at publish time and lets consumers decode by schema ID instead of the full schema per message.
- Q: What Avro schema change is always safe for backward compatibility? — A: Adding a field with a default value.
- Q: ORC or Parquet — which did the table-format ecosystem (Delta) standardize on? — A: Parquet.
- Q: What does Delta Lake add on top of plain Parquet files? — A: A transaction log giving ACID, schema enforcement, time travel, and MERGE.
- Q: Should you ever use `inferSchema=True` in a production CSV/JSON pipeline? — A: No — always declare an explicit schema.
- Q: What's the standard pipeline shape for JSON data? — A: JSON at the edges (API/Kafka), converted to typed Parquet/Delta at rest.
- Q: Why does `coalesce(1)` hurt a large production Parquet write? — A: Serializes the write to one task and builds one oversized, unpruneable row group.

Back to the folder: [02_File_formats notes](.) · Related: [01_SQL Interview Q&A](../../02_Databases/SQL/Interview_Questions_and_Answers.md)

---

## Further Learning — Docs & Videos

**Documentation**
- File format comparison (Databricks): https://www.databricks.com/glossary/what-is-parquet
- When to use which format (Azure): https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/

**Videos**
- File format interview questions (Parquet/Avro/ORC): https://www.youtube.com/results?search_query=parquet+avro+orc+interview+questions
