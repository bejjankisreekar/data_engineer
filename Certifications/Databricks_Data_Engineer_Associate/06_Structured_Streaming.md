# 06 — Structured Streaming

*Domain: Incremental Data Processing (22%)*

---

## What it is

**Structured Streaming** is Spark's engine for processing data **incrementally and continuously** as it arrives, using the **same DataFrame API** as batch. You write essentially the same code as a batch query, and Spark treats the input as an **unbounded table** that grows over time — processing only the **new** data on each trigger.

**Analogy:** A batch query reads a finished book. A streaming query reads a book that's still being written — every time you check back, it reads only the pages added since last time, and remembers where it left off.

> **Exam Tip:** The key idea: Structured Streaming reprocesses **only new/incremental data**, not the whole dataset each run. It uses the same API as batch, so `spark.readStream` mirrors `spark.read`, and `df.writeStream` mirrors `df.write`.

---

## Reading and writing streams

```python
# Read a Delta table as a stream (source)
df = spark.readStream.table("bronze_table")
# or from files:
df = spark.readStream.format("cloudFiles")...   # Auto Loader (see file 07)

# Transform with the normal DataFrame API
result = df.filter(col("value") > 0).groupBy("key").count()

# Write the stream to a sink
(result.writeStream
    .option("checkpointLocation", "/path/to/checkpoint")
    .outputMode("append")
    .trigger(availableNow=True)
    .table("silver_table"))
```

- `spark.readStream` — start a streaming read (source).
- `df.writeStream` — start a streaming write (sink).
- The query runs **continuously** (or once per trigger) until stopped.

---

## Checkpointing and exactly-once guarantees

- **`checkpointLocation`** — a required directory where the stream stores its **progress/offsets** and state. It records exactly which data has been processed so the stream can **resume after failure** without reprocessing or losing data.
- Together with **write-ahead logs** and **idempotent sinks** (Delta), Structured Streaming provides **exactly-once** processing guarantees.
- **Each stream needs its own unique checkpoint location.** Never share one checkpoint between two streams.

> **Exam Tip:** The **checkpoint location** is what makes a stream **fault-tolerant and exactly-once**: it tracks processing progress (offsets) so a restarted stream continues from where it stopped. It cannot be shared across streams. Losing/deleting the checkpoint forces reprocessing from the beginning (or the source's earliest available data).

---

## Triggers — controlling execution timing

The **trigger** decides *when* Spark processes the next batch of new data:

| Trigger | Behavior |
|---|---|
| `processingTime="5 minutes"` | Micro-batch every fixed interval |
| `availableNow=True` | Process **all currently available** new data, then **stop** (batch-like incremental run) |
| `once=True` (legacy) | Process one batch of available data, then stop (superseded by `availableNow`) |
| *(default, no trigger)* | Micro-batch as fast as possible (continuous processing) |

> **Exam Tip:** **`Trigger.AvailableNow`** (`.trigger(availableNow=True)`) processes all available new data **in one or more batches and then stops** — ideal for **cost-efficient scheduled incremental jobs** (run every hour via a Job, catch up on everything new, shut down). It replaces the older `Trigger.Once`. A fixed **`processingTime`** interval keeps the stream running continuously.

---

## Output modes

The **output mode** controls what gets written to the sink on each trigger:

| Output mode | Writes | Use when |
|---|---|---|
| **`append`** (default) | Only **new rows** since last trigger | Simple pass-through, no aggregation changing past results |
| **`complete`** | The **entire** updated result table every time | Aggregations where the whole result must be rewritten |
| **`update`** | Only rows that **changed** since last trigger | Aggregations, upsert-style sinks |

> **Exam Tip:** For **aggregations that must show full running totals**, use **`complete`** (rewrites the entire result table each trigger). **`append`** only ever adds new rows and can't be used with aggregations that change previously emitted results (unless watermarking finalizes them). Match the output mode to whether past results can change.

---

## Unsupported operations & watermarking

- Some operations **cannot** run on streaming DataFrames without special handling: **sorting** (`orderBy`) the full stream, certain multi-aggregations, and some joins.
- **Watermarking** (`withWatermark`) tells Spark how long to wait for late-arriving data before finalizing a window/aggregation and dropping old state — bounding state size.

```python
df.withWatermark("event_time", "10 minutes").groupBy(window("event_time", "5 minutes")).count()
```

> **Exam Tip:** **Watermarking** handles **late-arriving data** and limits how much aggregation **state** Spark must keep in memory. Without it, stateful streaming aggregations would grow state unbounded. Full-stream `orderBy` is not supported on an append stream.

---

## Streaming from Delta tables

- Any Delta table can be a **streaming source** — the stream reads new committed rows incrementally (using the transaction log).
- **Caveat:** streaming from a Delta source expects **append-only** changes by default. Updates/deletes/overwrites on the source can break the stream unless you set options like `ignoreChanges` or `ignoreDeletes`.

> **Exam Tip:** Streaming reads of a Delta table assume the source is **append-only**. Operations that modify existing files (UPDATE, DELETE, MERGE, OVERWRITE) on the source table can fail the stream; options such as `ignoreChanges` allow the stream to continue (though they may reprocess whole files).

---

## Quick Review

- Structured Streaming processes **only new/incremental data**, using the **same DataFrame API** as batch (`readStream`/`writeStream`).
- **`checkpointLocation`** tracks offsets → **fault tolerance + exactly-once**; must be **unique per stream**; don't delete/share it.
- **Triggers**: `processingTime` (continuous interval), **`availableNow`** (process all new data then stop — best for scheduled incremental jobs), default (as fast as possible).
- **Output modes**: **`append`** (new rows), **`complete`** (full result each time — for aggregations), **`update`** (changed rows).
- **Watermarking** handles late data and bounds aggregation state; full-stream sorting is unsupported.
- Delta streaming sources are treated as **append-only**; use `ignoreChanges`/`ignoreDeletes` if the source is modified.

---

## Further Learning — Docs & Videos

**Official documentation**
- Structured Streaming concepts: https://docs.databricks.com/en/structured-streaming/index.html
- Streaming from Delta tables: https://docs.databricks.com/en/structured-streaming/delta-lake.html
- Checkpoints: https://docs.databricks.com/en/structured-streaming/query-recovery.html
- Triggers (AvailableNow): https://docs.databricks.com/en/structured-streaming/triggers.html
- Output modes & watermarks: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Structured Streaming explained: https://www.youtube.com/results?search_query=databricks+structured+streaming+tutorial
- Checkpoints & triggers: https://www.youtube.com/results?search_query=spark+structured+streaming+checkpoint+trigger+availablenow
- Output modes & watermarking: https://www.youtube.com/results?search_query=spark+streaming+output+mode+watermark

---

Next: **[07 — Auto Loader & Multi-Hop (Medallion)](07_Auto_Loader_and_Multi_Hop.md)**.
