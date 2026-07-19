# OLAP Storage (Online Analytical Processing)

## What is OLAP?

**OLAP = Online Analytical Processing.** It is the storage pattern built for **analysis**: scanning millions or billions of rows to answer questions like "total revenue by month by region for the last 3 years."

Where [OLTP](01_OLTP_Storage.md) serves the *application*, OLAP serves the *analyst*.

---

## Analogy: the accountant's annual report

The checkout till (OLTP) records each sale as it happens. The accountant (OLAP) doesn't care about any single sale — they want to sum up *all* sales, group them by store and month, and spot trends. They read enormous amounts of data but almost never change it.

---

## Key characteristics

| Characteristic | OLAP behavior |
|---|---|
| Workload | Few, large queries (aggregations, GROUP BY, joins over history) |
| Users | A handful of analysts / dashboards |
| Data volume per query | Huge — millions to billions of rows |
| Response time | Seconds to minutes is acceptable |
| Data state | Historical, loaded in batches (not live) |
| Writes | Bulk loads (e.g. nightly ETL), rarely single-row updates |
| Storage layout | **Column-based** |
| Schema design | Denormalized (star schema: fact + dimension tables) |

---

## Why column-based storage?

OLAP systems store each **column** together on disk:

```
id:     [1, 2, 3, ...]
name:   [Asha, Ravi, Meena, ...]
city:   [Hyderabad, Chennai, Pune, ...]
amount: [500, 750, 300, ...]
```

For a query like `SELECT SUM(amount) FROM sales`, the engine reads **only the `amount` column** and skips everything else. On a table with 50 columns, that can mean reading 2% of the data instead of 100%.

Bonus: values in one column are similar (all numbers, all city names), so they **compress extremely well** — less disk, less I/O, faster queries.

This is exactly why analytical file formats like [Parquet](../02_File_formats/05_Parquet.md) are columnar.

---

## The star schema (typical OLAP design)

```
        Dim_Date      Dim_Product
             \            /
              \          /
              Fact_Sales   ← millions of rows: one per sale
              /          \
             /            \
        Dim_Store      Dim_Customer
```

- **Fact table** — the numbers (amount, quantity), one row per event.
- **Dimension tables** — the descriptions (product name, store city, calendar date).

Denormalized and simple on purpose, so analysts can join and aggregate quickly.

---

## Examples of OLAP systems

- Data warehouses: Azure Synapse, Snowflake, BigQuery, Redshift, Databricks SQL
- OLAP engines/formats: Parquet + Spark, Delta Lake

---

## OLTP vs OLAP summary

| | OLTP | OLAP |
|---|---|---|
| Purpose | Run the business | Analyze the business |
| Typical query | "Insert order #1042" | "Average order value per region per quarter" |
| Rows touched | 1–10 | Millions+ |
| Storage layout | Row-based | Column-based |
| Latency target | Milliseconds | Seconds–minutes |
| Data freshness | Live | Batch-loaded history |
| Example systems | Azure SQL DB, MySQL | Synapse, Snowflake, Databricks |

---

## Where OLAP fits

```
OLTP Databases → ETL/ELT → Data Lake → Data Warehouse (OLAP) → BI / Reports
```

See [ETL vs ELT](../04_ETL_ELT) and [01_Data_Lake_vs_Warehouse_vs_Database.md](../03_Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) for how data travels from OLTP to OLAP.

---
---

# Part 2 — Advanced

## Inside a columnar file: how the speed actually happens

Columnar engines (and formats like [Parquet](../02_File_formats/05_Parquet.md)/ORC) layer several tricks:

1. **Encodings before compression**
   - **Dictionary encoding** — `["Hyderabad","Hyderabad","Chennai"]` → dictionary `{0:"Hyderabad",1:"Chennai"}` + values `[0,0,1]`.
   - **Run-length encoding (RLE)** — `[0,0,0,0,1,1]` → `(0×4)(1×2)`. Sorted low-cardinality columns compress absurdly well.
   - **Delta encoding** — timestamps stored as differences: `10:00:01, +2s, +1s...`
2. **Statistics + zone maps** — each block stores min/max per column. Query `WHERE order_date = '2026-07-01'` skips every block whose max < that date without reading it. This is **data skipping / partition pruning**.
3. **Vectorized execution** — the engine processes columns in CPU-cache-sized batches (e.g. 1,024 values) with SIMD instructions, instead of interpreting row by row. This is what Databricks **Photon**, DuckDB, and Snowflake's engine all do.

**Worked example:** `SELECT SUM(amount) FROM sales WHERE region='East'` on 1 billion rows / 50 columns:
row store reads ~all bytes; column store reads 2 columns → ~4% of bytes → dictionary-encodes `region` → skips blocks whose min/max exclude 'East' → SIMD-sums the rest. That's how "minutes" becomes "seconds."

## Dimensional modeling beyond the star

- **Snowflake schema** — dimensions normalized into sub-dimensions (Product → Category → Department). Saves space, costs joins; most teams stay with stars.
- **Fact table types**: *transaction* facts (one row per event), *periodic snapshot* (one row per account per day), *accumulating snapshot* (one row per order, updated as it moves through stages).
- **Slowly Changing Dimensions (SCD)** — what to do when a customer moves city:
  - **Type 1**: overwrite (history lost)
  - **Type 2**: add a new row with `valid_from`/`valid_to`/`is_current` (history kept — the default choice)
  - **Type 3**: keep a `previous_city` column (rarely enough)
- **Surrogate keys** — facts join dimensions on meaningless integers, not business keys, so Type 2 history and source-system changes don't break joins.

## Loading patterns

OLAP writes are **bulk, append-mostly**: nightly/hourly batch loads, micro-batches from streaming, `MERGE` for upserts. Single-row `UPDATE`s are an anti-pattern — columnar files are immutable, so an update = rewrite of a whole file/micro-partition.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Physical design decisions that make or break performance

| Lever | What it does | Example |
|---|---|---|
| **Partitioning** | Splits table by a column so queries prune whole folders | Partition sales by `year/month`; a one-month query reads 1/36 of 3 years of data |
| **Clustering / sort order** | Orders data *within* files so min/max skipping works | Z-ORDER on `customer_id` in Delta; cluster keys in Snowflake |
| **File sizing** | Avoids the small-files problem | Target 100 MB–1 GB files; thousands of 1 MB files destroy scan performance |
| **Materialized views / aggregates** | Precompute expensive rollups | Daily revenue by region maintained automatically, dashboards hit that |

**Anti-pattern:** partitioning by a high-cardinality column (e.g. `customer_id`) → millions of tiny folders/files. Partition low-cardinality (date), cluster high-cardinality.

## Modern OLAP architecture notes

- **Separation of storage & compute** (Snowflake, Databricks SQL, BigQuery): storage is cheap object storage; compute clusters spin up per workload and scale independently. Two teams can query the same data on separate compute without contention.
- **The lakehouse** collapses "lake + warehouse" into one: Delta/Iceberg tables on the lake give ACID + schema enforcement, and a SQL engine on top serves BI ([06_Big_Data_Evolution_Timeline.md](06_Big_Data_Evolution_Timeline.md)).
- **Approximate algorithms** — `APPROX_COUNT_DISTINCT` (HyperLogLog) answers "unique users last year" in ~2% error at a fraction of the cost. Pros reach for it on dashboards.
- **Concurrency profile is inverted vs OLTP**: a warehouse handles *few hundred* concurrent queries, not 100k transactions — size and queue accordingly (e.g. Snowflake multi-cluster warehouses, Databricks SQL autoscaling).

## Field-tested gotchas

- `SELECT *` in OLAP is self-sabotage — it defeats column pruning. Name your columns.
- **GROUP BY high-cardinality keys** (e.g. by user_id over billions of rows) is a shuffle monster — pre-aggregate or bucket first.
- Late-arriving data breaks naive date partitions — design loads to `MERGE` into older partitions, and make pipelines **idempotent** (re-running a day must not double-count).
- Cost surprises: in pay-per-scan engines (BigQuery), an unpartitioned full scan can cost real money; in cluster engines, an idle running warehouse burns credits. Governance is part of the job.

## Interview-grade Q&A

- *Why is columnar faster for analytics?* Reads only needed columns, compresses better, enables vectorized execution and block skipping.
- *Star vs snowflake schema?* Star denormalizes dimensions for fewer joins; snowflake normalizes them. Star is the default for BI.
- *How do you store customer history when attributes change?* SCD Type 2 with surrogate keys and validity ranges.
- *Why are single-row updates bad in a warehouse?* Immutable columnar files → each update rewrites a file; batch `MERGE` instead.
