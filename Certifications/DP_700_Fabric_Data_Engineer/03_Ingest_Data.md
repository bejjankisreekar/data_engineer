# 03 — Ingest Data

*Domain: Ingest and transform data (30–35%)*

---

## What it is

Getting data **into** Fabric — batch and streaming — and choosing the **right tool** for each ingestion scenario. This is where the "which item?" decisions matter most. Concepts build on [Data Integration](../../06_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md), [Integration Patterns](../../06_Data_Engineering/Data_Integration/02_Integration_Patterns.md), and [Streaming](../../09_Streaming/00_Streaming_Learning_Path.md).

---

## The batch ingestion tools — which to use

| Tool | Nature | Best for |
|---|---|---|
| **Data pipeline — Copy activity** | Low-code, high-scale copy | Moving large volumes from many sources into OneLake, orchestration |
| **Dataflow Gen2** | Power Query, low-code transform-on-ingest | Business-user/light transforms during ingest, many connectors |
| **Notebook (Spark)** | Code (PySpark/Spark SQL) | Complex/custom transforms, large-scale engineering |
| **T-SQL (Warehouse)** | `COPY INTO` / `CREATE TABLE AS` | SQL-first loading into a Warehouse |
| **Shortcut** | Reference, no copy | Data already in ADLS/S3/GCS or another workspace |
| **Mirroring** | Live replica | Operational DBs (Azure SQL, Cosmos, Snowflake) with zero ETL |

> **Exam Tip:** The decision ladder — *just reference existing lake files* → **Shortcut** (no ingestion at all); *replicate an operational DB live* → **Mirroring**; *low-code copy/orchestrate at scale* → **pipeline Copy activity**; *low-code transform during ingest* → **Dataflow Gen2**; *complex code transforms* → **Notebook/Spark**.

> **Exam Tip:** **Copy activity vs Dataflow Gen2** — Copy is for *moving* data efficiently at scale (minimal transform); Dataflow Gen2 is for *transforming* during ingest with Power Query. For "ingest with heavy transformations, low-code" → **Dataflow Gen2**; for "move lots of data fast, then transform elsewhere" → **Copy**.

---

## Loading patterns (design questions)

- **Full load** — reload the entire dataset each run. Simple; expensive at scale.
- **Incremental load** — load only new/changed data since last run (by watermark/timestamp, or [CDC](../../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)). Efficient; the default for large sources.
- **Batch vs streaming** — scheduled chunks vs continuous ([Streaming Fundamentals](../../09_Streaming/01_Streaming_Fundamentals.md)).
- **Medallion (Bronze/Silver/Gold)** — land raw → clean/conform → model, each layer a set of Delta tables ([Lakehouse](../../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)).

> **Exam Tip:** "Only load rows changed since yesterday" → **incremental load** with a watermark column (e.g. `LastModified > @lastRun`). Full loads are for small dims or first loads.

---

## Streaming ingestion in Fabric

**Real-Time Intelligence** handles streaming ([Stream Analytics parallels](../../09_Streaming/04_Azure_Stream_Analytics.md)):

| Item | Role |
|---|---|
| **Eventstream** | No-code ingest & routing of streaming events (from Event Hubs, IoT Hub, Kafka, sample data) to destinations |
| **Eventhouse / KQL Database** | Stores and analyzes real-time/telemetry data with **KQL** |
| **Spark Structured Streaming** (Notebook) | Code-based streaming into Lakehouse Delta tables |

- Eventstream **sources**: Azure Event Hubs, IoT Hub, Kafka, CDC feeds, sample data.
- Eventstream **destinations**: Eventhouse (KQL), Lakehouse, Derived stream, custom endpoint, Activator (alerts).

> **Exam Tip:** For **no-code** real-time ingest and routing → **Eventstream**. For **querying** real-time data with KQL → **Eventhouse/KQL database**. For **code-based** streaming into Delta with custom logic → **Spark Structured Streaming** in a notebook.

---

## Reading & writing data in a notebook (Spark)

```python
# Read from a Lakehouse table (Delta)
df = spark.read.table("bronze.sales")

# Read files via a relative Lakehouse path or a shortcut
df = spark.read.format("parquet").load("Files/landing/sales/")

# Write a managed Delta table into the Lakehouse
df.write.mode("append").saveAsTable("silver.sales")

# Auto Loader-style incremental file ingestion (Structured Streaming)
(spark.readStream.format("cloudFiles")
   .option("cloudFiles.format", "json")
   .load("Files/landing/")
   .writeStream.option("checkpointLocation", "Files/_chk/sales")
   .trigger(availableNow=True).toTable("bronze.sales"))
```

The PySpark you learned applies unchanged ([Reading & Writing Data](../../03_Programming/PySpark/04_Reading_and_Writing_Data.md), [Structured Streaming](../../03_Programming/PySpark/13_Structured_Streaming.md)).

---

## Quick Review

- Batch ingest tools: **Copy activity** (move at scale), **Dataflow Gen2** (low-code transform), **Notebook/Spark** (complex), **T-SQL** (Warehouse load), **Shortcut** (reference, no copy), **Mirroring** (live DB replica).
- **Shortcut vs Mirroring:** shortcut references files in place; mirroring replicates an operational database live.
- **Copy vs Dataflow Gen2:** Copy moves data efficiently; Dataflow Gen2 transforms during ingest (Power Query).
- Load patterns: **full** vs **incremental** (watermark/CDC); **batch** vs **streaming**; **medallion**.
- Streaming: **Eventstream** (no-code ingest/route), **Eventhouse/KQL** (analyze), **Spark Structured Streaming** (code).

---

## Further Learning — Docs & Videos

- Get data into Fabric (ingestion): https://learn.microsoft.com/en-us/fabric/data-factory/
- Eventstreams: https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview
- Video search: https://www.youtube.com/results?search_query=dp-700+fabric+ingest+pipeline+dataflow+eventstream

---

Next: **[04 — Transform Data](04_Transform_Data.md)**.
