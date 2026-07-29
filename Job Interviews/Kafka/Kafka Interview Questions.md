# Apache Kafka — Interview Questions

## Overview
Kafka is the industry-standard distributed streaming platform (topics, partitions, producers/consumers). Event Hubs is Kafka-compatible, so Kafka concepts transfer directly. Interviews test partitions, consumer groups, offsets, and delivery semantics.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Kafka? Core concepts? | 🟢 | ★★★★★ |
| 2 | Topic, partition, offset? | 🟡 | ★★★★★ |
| 3 | Producer, consumer, consumer group? | 🟡 | ★★★★★ |
| 4 | How is ordering guaranteed? | 🔴 | ★★★★☆ |
| 5 | Delivery semantics (at-most/at-least/exactly-once)? | 🔴 | ★★★★☆ |
| 6 | Replication & ISR? | 🔴 | ★★★☆☆ |
| 7 | Kafka vs Event Hubs? | 🟡 | ★★★★☆ |
| 8 | Retention & compaction? | 🟡 | ★★★☆☆ |
| 9 | How does Spark consume Kafka? | 🟡 | ★★★★☆ |
| 10 | Rebalancing? | 🔴 | ★★★☆☆ |

## Key Answers
- **Q2:** A **topic** is a named stream, split into **partitions** for parallelism; each message has a monotonic **offset** within a partition. Ordering is per-partition only.
- **Q3:** Producers write; consumers read; a **consumer group** shares partitions among its members (each partition consumed by one member in the group) for scale-out. Different groups read independently.
- **Q5:** At-most-once (may lose), at-least-once (may dup — default), **exactly-once** (transactions + idempotent producer). Downstream idempotency (e.g., Delta MERGE) achieves effective exactly-once.
- **Q7:** Event Hubs exposes a **Kafka endpoint**, so Kafka clients work against it — managed, less ops than self-hosting Kafka.

## Scenario Questions
- **"Scale consumers to keep up."** Add consumers up to the **partition count** (more consumers than partitions = idle ones).
- **"Guarantee no data loss."** Replication factor ≥3, `acks=all`, consumer checkpoint offsets, idempotent sink.
- **"Keep only the latest value per key."** Log **compaction**.

## Quick Revision
- ✔ Topic → **partitions** (parallelism) → **offsets** (per-partition order)
- ✔ **Consumer group** = scale-out; 1 partition → 1 consumer in a group
- ✔ Ordering **per partition** only; key routes related messages together
- ✔ At-least-once default; exactly-once via txns + idempotent sink
- ✔ Replication + **ISR** for durability
- ✔ Event Hubs = Kafka-compatible managed service

## Common Mistakes
- Expecting global ordering.
- More consumers than partitions (idle consumers).
- Assuming exactly-once without idempotency.

## Senior-Level
Seniors size partitions for throughput/consumers, tune acks/replication for durability, use keys for ordering, and achieve exactly-once via idempotent Delta sinks + checkpoints — mapping it all to Event Hubs on Azure.

## Related Topics
Event Hub, Stream Analytics, Azure Databricks, PySpark
