# Streaming — Learning Path

Everything so far in this repo has mostly been **batch**: data arrives in files or tables, and a pipeline processes it on a schedule. **Streaming** is the other half of data engineering — processing data **as it happens**, event by event, with latency measured in seconds instead of hours.

This module teaches the streaming world an Azure Data Engineer must know: the **concepts** (what makes streaming different and hard), and the three **tools** that show up in every Azure DE interview — **Event Hubs**, **Kafka**, and **Stream Analytics**.

> **Where Spark Structured Streaming fits:** the Databricks/Spark side of streaming already lives in [PySpark 13 — Structured Streaming](../06_Programming/PySpark/13_Structured_Streaming.md). This module is the **ingestion + Azure-services** side; the two are complementary and cross-linked throughout.

---

## Prerequisites

- [ETL vs ELT](../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) & [Data Pipelines](../05_Data_Engineering/ETL_ELT/03_Data_Pipelines.md) — batch vs streaming, DAGs, idempotency
- [Data Integration Fundamentals](../05_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md) — where streaming sits among integration styles
- [Structured Streaming](../06_Programming/PySpark/13_Structured_Streaming.md) — helpful but not required; this module re-introduces the concepts

---

## The map

| # | Note | What it covers |
|---|---|---|
| 01 | [Streaming Fundamentals](01_Streaming_Fundamentals.md) | Batch vs stream, event streams, windows, watermarks, delivery semantics, Lambda vs Kappa |
| 02 | [Azure Event Hubs](02_Azure_Event_Hubs.md) | Azure's managed event ingestion — partitions, consumer groups, throughput, Capture, Kafka endpoint |
| 03 | [Apache Kafka](03_Apache_Kafka.md) | The open-source streaming platform — topics, brokers, offsets, replication, exactly-once, ecosystem |
| 04 | [Azure Stream Analytics](04_Azure_Stream_Analytics.md) | SQL-based stream processing — inputs/outputs, windowing functions, reference data, SUs |
| — | [Interview Q&A](Interview_Questions_and_Answers.md) | Q&A across the whole module |

---

## Suggested route

- **Just the concepts:** read [01](01_Streaming_Fundamentals.md) — it stands alone and demystifies the hard parts (windows, watermarks, exactly-once).
- **Azure-focused:** 01 → 02 (Event Hubs) → 04 (Stream Analytics). That's the core Azure streaming stack.
- **Kafka shops / broad interviews:** all of 01–04. Event Hubs and Kafka are close cousins — learn both, they compare constantly.

**Milestone for the module:** explain why "exactly-once" is hard, describe a tumbling vs sliding window, choose Event Hubs vs Kafka for a scenario, and sketch a real-time pipeline (source → Event Hubs → Stream Analytics/Spark → sink) with the right delivery guarantee.

---

## How the pieces fit together

```
 Producers (apps, IoT, logs, clickstream)
        │  events, continuously
        ▼
 ┌─────────────────────────────┐
 │  INGEST / BUFFER            │   Event Hubs  ≈  Kafka
 │  (a durable, partitioned log)│   (managed)      (OSS / self-managed)
 └──────────────┬──────────────┘
                │  many consumers read independently
                ▼
 ┌─────────────────────────────┐
 │  STREAM PROCESSING          │   Stream Analytics (SQL)
 │  (windows, joins, aggregates)│   or Spark Structured Streaming
 └──────────────┬──────────────┘
                ▼
   Sinks: Delta/ADLS, SQL, Power BI, Cosmos DB, alerts
```

- **Event Hubs / Kafka** = the *pipe* that durably buffers events and lets many consumers read them.
- **Stream Analytics / Spark** = the *processor* that does the actual computation on the stream.
- Keeping "the pipe" and "the processor" separate is the mental model that makes streaming click.
