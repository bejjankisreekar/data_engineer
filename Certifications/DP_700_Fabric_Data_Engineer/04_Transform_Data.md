# 04 — Transform Data

*Domain: Ingest and transform data (30–35%)*

---

## What it is

Turning raw ingested data into clean, modeled, query-ready tables — with the right engine (**Spark**, **T-SQL**, or **KQL**) and the right techniques (dedup, aggregation, joins, upserts, [SCD](../../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md)). This is the most code-heavy part of the exam. Foundations: [PySpark](../../06_Programming/PySpark/00_PySpark_Learning_Path.md), [Spark SQL](../../06_Programming/PySpark/11_Spark_SQL_and_Views.md), [Delta Table](../../04_Storage_and_Formats/Lakehouse/02_Delta_Table.md).

---

## Which engine to transform with

| Engine | Where | Best for |
|---|---|---|
| **Spark (PySpark / Spark SQL)** | Notebook, Lakehouse | Complex, large-scale, programmatic transforms; ML |
| **T-SQL** | Warehouse / SQL endpoint | Set-based SQL transforms, SQL-first teams |
| **KQL** | Eventhouse | Real-time/telemetry analytics |
| **Dataflow Gen2 (Power Query)** | Dataflow | Low-code transforms |

> **Exam Tip:** Same data, different engine by team/need: heavy programmatic logic → **Spark notebook**; set-based SQL in a warehouse → **T-SQL**; real-time telemetry → **KQL**; low-code/business-user → **Dataflow Gen2**. All read/write the same OneLake Delta.

---

## Core transformation techniques

- **Deduplication** — `dropDuplicates()` / `ROW_NUMBER()` window keep-latest ([Window Functions](../../06_Programming/PySpark/08_Window_Functions.md)).
- **Handling nulls** — `fillna()`, `COALESCE`, filtering ([Column Ops](../../06_Programming/PySpark/05_Column_Operations_and_Functions.md)).
- **Aggregation / grouping** — `groupBy().agg()` / `GROUP BY` ([Aggregations](../../06_Programming/PySpark/06_Aggregations_and_Grouping.md)).
- **Joins** — combine tables; mind fan-out and broadcast ([Joins](../../06_Programming/PySpark/07_Joins.md)).
- **Denormalization** — flatten star/normalized data into wide tables for BI.
- **Late-arriving / out-of-order data** — watermarks in streaming; reprocessing in batch.

---

## The MERGE / upsert pattern (heavily tested)

`MERGE` on a Delta table does insert-or-update-or-delete in one atomic operation — the backbone of incremental loads and SCD.

```python
from delta.tables import DeltaTable
target = DeltaTable.forName(spark, "silver.customers")
(target.alias("t")
  .merge(updates.alias("s"), "t.customer_id = s.customer_id")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())
```

```sql
-- T-SQL / Spark SQL equivalent
MERGE INTO silver.customers t
USING updates s ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

> **Exam Tip:** For **upserts** (apply new + changed rows) → `MERGE`, not a full `overwrite` (which loses history and other writers' work). `MERGE` also powers **SCD Type 2**: close the old row (`is_current=false`, set `end_date`) and insert a new current row.

---

## Slowly Changing Dimensions (SCD)

| Type | Behavior |
|---|---|
| **SCD 1** | Overwrite — no history |
| **SCD 2** | New row per change — full history (start/end dates, `is_current` flag) |
| **SCD 3** | Limited history in extra columns |

Full note: [Slowly Changing Dimensions](../../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md).

> **Exam Tip:** "Keep full history of dimension changes" → **SCD Type 2** (implemented with `MERGE`). "Only keep current values" → **SCD Type 1** (overwrite).

---

## Streaming transformations & windowing

For streaming transforms (Spark Structured Streaming or KQL), aggregate over **windows** ([Streaming Fundamentals](../../09_Streaming/01_Streaming_Fundamentals.md)):
- **Tumbling** (fixed, non-overlapping), **hopping/sliding** (overlapping), **session** (gap-based).
- Use **event time** + **watermarks** to handle late/out-of-order data correctly.

> **Exam Tip:** Aggregating a stream needs a **window** (you can't `GROUP BY` an infinite stream). "Count events per minute" → **tumbling** window on event time.

---

## Fabric Warehouse loading transforms

- **`CREATE TABLE AS SELECT (CTAS)`** — create and populate a table from a query in one step.
- **`COPY INTO`** — high-throughput bulk load from files into a Warehouse table.
- **`INSERT ... SELECT`** — set-based transform-and-load.

> **Exam Tip:** In a **Warehouse**, `CTAS` and `COPY INTO` are the idiomatic load/transform commands. Unlike a Lakehouse (Spark-written), a Warehouse supports full T-SQL DML (`INSERT/UPDATE/DELETE/MERGE`).

---

## Quick Review

- Transform engines: **Spark** (complex/large), **T-SQL** (Warehouse, set-based), **KQL** (real-time), **Dataflow Gen2** (low-code) — all on OneLake Delta.
- Techniques: dedup (window/`dropDuplicates`), null handling, aggregation, joins, denormalization.
- **`MERGE`** = upsert (insert+update+delete atomically) — the core incremental/SCD tool; prefer over `overwrite`.
- **SCD 1** overwrite (no history); **SCD 2** new row per change (full history via `MERGE`).
- Streaming transforms use **windows** (tumbling/hopping/session) on **event time** with **watermarks**.
- Warehouse loads: **CTAS**, **COPY INTO**, `INSERT...SELECT`; Warehouse supports full T-SQL DML, Lakehouse is Spark-written.

---

## Further Learning — Docs & Videos

- Transform data in Fabric: https://learn.microsoft.com/en-us/fabric/data-engineering/
- Delta MERGE: https://learn.microsoft.com/en-us/azure/databricks/delta/merge
- Video search: https://www.youtube.com/results?search_query=dp-700+fabric+transform+spark+merge+scd

---

Next: **[05 — Monitor & Optimize](05_Monitor_and_Optimize.md)**.
