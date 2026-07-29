# Azure Event Hubs — Interview Questions

## Overview
Event Hubs is Azure's big-data streaming ingestion service (a managed, Kafka-compatible event pipeline). It buffers millions of events/sec for real-time pipelines (Stream Analytics, Databricks, Functions). Interviews test partitions, consumer groups, throughput units, and delivery semantics.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Event Hubs? Use cases? | 🟢 | ★★★★★ |
| 2 | Partitions — role & how many? | 🔴 | ★★★★★ |
| 3 | Consumer groups? | 🟡 | ★★★★★ |
| 4 | Throughput Units / Processing Units? | 🟡 | ★★★★☆ |
| 5 | Event Hubs vs Kafka? | 🟡 | ★★★★☆ |
| 6 | Event Hubs vs Service Bus vs Event Grid? | 🔴 | ★★★★☆ |
| 7 | Delivery guarantee & checkpointing? | 🔴 | ★★★★☆ |
| 8 | Capture feature? | 🟡 | ★★★☆☆ |
| 9 | How does Databricks consume Event Hubs? | 🟡 | ★★★★☆ |
| 10 | Ordering guarantees? | 🟡 | ★★★☆☆ |

## Key Answers
- **Q2:** Partitions enable **parallel consumption** and scale; ordering is guaranteed **within a partition** only. Choose partition count up front (hard to change) based on peak throughput/consumers. A **partition key** routes related events to the same partition (keeps their order).
- **Q3:** A **consumer group** is an independent view/cursor over the stream, letting multiple apps read the same events at their own pace (e.g., one for Stream Analytics, one for Databricks).
- **Q6 (trap):** **Event Hubs** = high-throughput event **streaming/telemetry**. **Service Bus** = enterprise **messaging** (queues/topics, transactions, ordering). **Event Grid** = **reactive event routing** (pub/sub for discrete events). Know which fits.
- **Q7:** At-least-once delivery; consumers **checkpoint** offsets so they resume without loss (dedupe for exactly-once).

## Scenario Questions
- **"Ingest 1M IoT events/sec into the lakehouse."** Event Hubs (enough partitions/TUs) → Databricks Structured Streaming (checkpointed) → Bronze Delta.
- **"Two teams need the same stream."** Separate **consumer groups**.
- **"Land raw events to storage automatically."** Enable **Capture** (auto-writes to ADLS/Blob as Avro).

## Quick Revision
- ✔ Event Hubs = high-throughput streaming ingestion (Kafka-compatible)
- ✔ **Partitions** = parallelism; order **within a partition** only
- ✔ **Consumer groups** = independent readers of the same stream
- ✔ Scale via **Throughput/Processing Units**
- ✔ At-least-once + **checkpoint** offsets
- ✔ **Capture** auto-lands raw to ADLS
- ✔ Hubs (stream) vs Service Bus (messaging) vs Event Grid (events)

## Common Mistakes
- Expecting global ordering (it's per-partition).
- Too few partitions → throughput ceiling.
- Confusing Event Hubs / Service Bus / Event Grid.

## Senior-Level
Seniors size partitions/TUs for peak load, use partition keys for ordering, design consumer groups per downstream, checkpoint for reliable exactly-once with idempotent sinks, and choose Hubs vs Service Bus vs Event Grid deliberately.

## Related Topics
Stream Analytics, Kafka, Azure Databricks, Azure Functions, ADLS Gen2
