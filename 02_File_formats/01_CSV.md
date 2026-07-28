# CSV (Comma Separated Values)

## What is CSV?

CSV is a plain text file where each row is separated by a new line and columns are separated by commas.

Analogy: it's exactly what you'd get if you took a spreadsheet and stripped away all the formatting — no colors, no formulas, no cell merging — leaving just the raw values separated by commas. That simplicity is exactly why almost every tool on earth can open a CSV file.

Example:

```csv
EmployeeID,Name,Department,Salary
101,John,IT,60000
102,Alice,HR,50000
103,David,Finance,55000
```

---

## Advantages

- Easy to read
- Human readable
- Supported everywhere
- Small learning curve

---

## Disadvantages

- No compression
- No schema
- No nested data
- Large file size

---

## Used In

- Excel exports
- Data sharing
- Small datasets
- Import/Export

---

## Azure Usage

ADF

Databricks

Synapse

Power BI

All can read CSV files.

---

## Where CSV Fits

CSV is usually where a data journey *starts* (a raw export from an old system) rather than where it stays. See [File Format Comparison](06_File_Format_Comparison.md) for how CSV compares to [JSON](02_JSON.md), [Avro](03_Avro.md), [ORC](04_ORC.md), and [Parquet](05_Parquet.md), and when it's worth converting away from it.

---
---

# Part 2 — Advanced

## The dialect problem: "CSV" is not one format

There is a spec (RFC 4180) — and almost nothing follows it fully. Every producing system chooses its own answers to:

| Question | Common variants |
|---|---|
| Delimiter | `,` `;` (European Excel!) `\t` `|` |
| Quoting | `"value"` when needed / always / never |
| Escaping a quote inside a value | `""` (RFC) or `\"` |
| Line endings | `\n` vs `\r\n` (breaks naive parsers cross-OS) |
| Header row | present / absent / repeated per chunk |
| NULL representation | empty string, `NULL`, `\N`, `NA`, `null` |
| Encoding | UTF-8, UTF-8-with-BOM (Excel!), Windows-1252, UTF-16 |

**Embedded delimiters and newlines** are the classic breakers: `"Smith, John"` and multi-line address fields split rows for any parser that just splits on commas. Never parse CSV with `split(',')` — use a real parser (Spark's reader, Python `csv`, pandas) and *configure the dialect explicitly*:

```python
df = (spark.read.format("csv")
      .option("header", True)
      .option("quote", '"').option("escape", '"')
      .option("multiLine", True)          # only if values contain newlines — see gotchas
      .option("encoding", "UTF-8")
      .schema(explicit_schema)            # NEVER inferSchema in production
      .load("abfss://raw@lake.dfs.core.windows.net/exports/"))
```

## Why explicit schema, always

`inferSchema=True` reads the data an extra time and *guesses* per file: `00042` becomes integer 42 (leading zeros gone — ruinous for postal codes/[phone numbers](../01_SQL/03_SQL_Data_Types.md)), `1e5` becomes a float, a column that's all-numeric today becomes string tomorrow when one "N/A" appears — and your pipeline breaks or, worse, doesn't. Production rule: **schema is a contract you declare, not a guess the engine makes.**

## Compression and splittability

Plain CSV compresses ~80–90% with gzip — but a `.csv.gz` file is **not splittable**: one 10 GB gzip = one Spark task reading it alone ([parallelism](../06_PySpark/Spark_Processing.md) gone). Options:

- **bzip2/zstd(seekable)** — splittable but slower/rarer.
- Many medium gzip files (~100–250 MB) — parallelism via file count, the pragmatic landing-zone pattern.
- Convert to [Parquet](05_Parquet.md) at the first pipeline hop — the real answer.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Operating a CSV ingestion boundary (the checklist)

CSV is where *other people's* systems meet your pipeline, so defend accordingly:

1. **Validate structure before load** — column count and header names against the contract; quarantine files that differ, don't "best-effort" them.
2. **Permissive-with-capture parsing** — Spark's `mode=PERMISSIVE` + `columnNameOfCorruptRecord` lands broken rows in a `_corrupt_record` column: load the good, quarantine the bad, alert on the ratio.
3. **Keep the raw file immutable** in the bronze/landing zone — you *will* need to re-parse with fixed options ([medallion](../04_ETL_ELT/01_ETL_vs_ELT.md)).
4. **Row-count reconciliation** — lines in file (minus header) vs rows loaded, every file, automated ([aggregates as instrumentation](../01_SQL/08_SQL_Aggregate_Functions.md)).
5. Convert to Parquet/Delta immediately; CSV's job ends at the door.

## The Excel factor

Half of enterprise CSVs are born or edited in Excel; know its fingerprints: UTF-8 **BOM** (`ï»¿` glued to your first header name), locale semicolon delimiters, dates silently reformatted (`03/07/2026` — March or July?), long numeric IDs mangled to scientific notation (`9.78002E+12`), leading zeros stripped. Two pro defenses: dates are ISO-8601 (`2026-07-19`) or they're rejected; identifiers are quoted strings end-to-end.

## Field-tested gotchas

- `multiLine=True` in Spark makes files **non-splittable** (a quoted newline could span split boundaries) — a quiet parallelism killer on big files; prefer producers that escape newlines.
- Header drift mid-feed (source adds a column in June) silently shifts positional loads — that's why validation is by *name and position*, not position alone.
- `NULL` vs empty-string is a real distinction lost by default in many writers — agree the token (`\N` or explicit config) with the producer, or "" customers appear.
- A trailing comma on some rows = ragged rows; PERMISSIVE mode hides it until sums don't reconcile. Count columns per row in validation.
- Idempotent re-loads need a file-level key — filename + checksum in an audit table; the same export re-delivered must not double-load ([idempotency](../01_SQL/05_SQL_DML.md)).

## Interview-grade Q&A

- *Why is CSV bad for analytics at scale?* Row-oriented text: no column pruning, no predicate pushdown, no types, poor compression splittability — every query parses everything ([columnar contrast](../00_Fundamentals/02_OLAP_Storage.md)).
- *A CSV load's row count doesn't match the source — first suspects?* Unescaped quotes/newlines splitting or merging rows, header/ragged-row handling, encoding mangling.
- *How do you make CSV ingestion robust?* Explicit schema + dialect options, permissive-with-quarantine parsing, structural validation, raw retention, immediate conversion.
- *gzip CSV vs Parquet for a 10 GB daily feed?* gzip CSV: one reader task, no pruning. Parquet: splittable, columnar, typed — convert on arrival.
---

## Further Learning — Docs & Videos

**Documentation**
- RFC 4180 — CSV format spec: https://www.rfc-editor.org/rfc/rfc4180
- Reading CSV in Spark: https://spark.apache.org/docs/latest/sql-data-sources-csv.html
- Pandas read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

**Videos**
- CSV file format explained: https://www.youtube.com/results?search_query=csv+file+format+explained+data+engineering
