# Apache Kafka

## What is it?

**Apache Kafka** is the open-source **distributed event streaming platform** that essentially defined the category. It's a durable, partitioned, replicated **commit log** that producers write events to and consumers read from — at massive scale, with strong durability. Most streaming concepts (topics, partitions, offsets, consumer groups) come from Kafka, and [Event Hubs](02_Azure_Event_Hubs.md) is Kafka-compatible precisely because Kafka is the de-facto standard.

In one line: **Kafka = the open-source, self-managed distributed log that most of the streaming world is built on (or modeled after).**

---

## Analogy: a newspaper subscription system

Kafka is like a **newspaper publisher**. Journalists (producers) publish articles into different **sections** (topics) — Sports, Finance, Weather. Each section is printed across several **presses** (partitions) for speed. Subscribers (consumers) subscribe to sections and read at their own pace, each remembering which edition they last read (offset). Many subscribers read the *same* paper independently, and back-issues are kept in the archive (retention) so a new subscriber can start from last week. The publisher doesn't care who reads or how fast — it just keeps printing.

---

## Core concepts

```
Producers ──► Topic "orders"
              ├─ Partition 0: [o0 o1 o2 o3 ►]     (each partition = ordered, immutable log)
              ├─ Partition 1: [o0 o1 o2 ►]
              └─ Partition 2: [o0 o1 o2 o3 o4 ►]
                        replicated across Brokers (fault tolerance)

Consumer Group "billing":  C1 reads P0,  C2 reads P1+P2   (partitions split across the group)
Consumer Group "analytics": reads all partitions independently, own offsets
```

| Concept | What it is |
|---|---|
| **Topic** | A named stream of events (like an Event Hub) |
| **Partition** | An ordered, immutable sub-log; parallelism + ordering unit |
| **Offset** | A message's position in a partition; consumers track their own |
| **Broker** | A Kafka server; a cluster is many brokers |
| **Producer** | Writes events (chooses partition via key or round-robin) |
| **Consumer / Consumer Group** | Reads events; within a group, partitions are split across consumers |
| **Replication factor** | Copies of each partition across brokers for fault tolerance |
| **Leader / Follower & ISR** | One broker leads a partition, others replicate (in-sync replicas) |
| **Retention / Log compaction** | Keep by time/size, or keep only the latest value per key |

---

## Advantages

- **Battle-tested at scale** — runs the streaming backbones of huge companies.
- **Durable & fault-tolerant** — replication means broker failures don't lose data.
- **High throughput, low latency** — sequential disk writes + zero-copy make it very fast.
- **Rich ecosystem** — Kafka Connect (connectors), Schema Registry, Kafka Streams / ksqlDB (processing).
- **Open-source & portable** — runs anywhere (on-prem, any cloud); no vendor lock-in.
- **Replayable** — reset offsets to reprocess history (the [Kappa](01_Streaming_Fundamentals.md) enabler).

## Disadvantages

- **Operational burden** — self-managing a Kafka cluster (brokers, storage, upgrades, rebalancing) is real work — the main reason teams pick managed [Event Hubs](02_Azure_Event_Hubs.md) or Confluent Cloud.
- **Complexity** — many tuning knobs (acks, replication, retention, partitions).
- **Not a database** — it's a log, not a queryable store; you land data elsewhere to query it.
- **Ordering only per partition** — same global-ordering limitation as all logs.

---

## Azure Usage

You rarely run raw Kafka on Azure by hand. Options, cheapest-effort first:

| Option | What it is |
|---|---|
| **Event Hubs (Kafka endpoint)** | Managed, speaks the Kafka protocol — Kafka apps connect unchanged. Most common on Azure. |
| **Confluent Cloud (Azure Marketplace)** | Fully-managed Kafka + full ecosystem (Schema Registry, Connect, ksqlDB) |
| **Kafka on HDInsight** | Managed Kafka clusters you still size/operate |
| **Self-managed (AKS/VMs)** | Full control, full operational responsibility |

Downstream, Kafka/Event Hubs feeds **Databricks (Structured Streaming)**, **Stream Analytics**, or **Fabric Eventstream**, landing in Delta/ADLS/Cosmos DB.

---

## Real World Example

A bank builds its transaction backbone on Kafka: every card swipe is published to an `transactions` topic, partitioned by `account_id` so each account's events stay ordered. Multiple independent consumer groups process the *same* stream — a **fraud-detection** service scores transactions in real time, a **ledger** service updates balances, and a **Databricks** job lands them into the lakehouse. With a **replication factor of 3**, a broker can fail mid-day without losing a single transaction, and because Kafka retains the log, when the fraud team ships a new model they **reset offsets** and replay a week of history through it — no re-ingestion needed.

---
---

# Part 2 — Advanced

## Delivery guarantees & `acks`

Kafka's producer `acks` setting drives durability vs latency:
- `acks=0` — fire and forget (fastest, can lose data → at-most-once).
- `acks=1` — leader confirms (balanced).
- `acks=all` — leader + all in-sync replicas confirm (safest, no loss on single-broker failure).

Combined with **idempotent producers** and **transactions**, Kafka supports **exactly-once semantics (EOS)** end to end — but as always, "exactly-once" means idempotent/transactional writes + committed offsets, not the absence of retries ([delivery semantics](01_Streaming_Fundamentals.md)).

## Replication, leaders & ISR

Each partition has one **leader** broker (handles reads/writes) and **follower** replicas. The **in-sync replica (ISR)** set is the replicas caught up with the leader. If the leader fails, an ISR is promoted — no data loss as long as an ISR survives. `min.insync.replicas` controls how many replicas must ack an `acks=all` write, trading availability for durability.

## The Kafka ecosystem

Kafka is more than the broker:
- **Kafka Connect** — pre-built connectors to move data in/out (databases, S3, Elasticsearch) without custom code, including **CDC** via Debezium ([CDC](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)).
- **Schema Registry** — enforces and evolves message schemas ([Avro](../05_Storage_and_Formats/File_Formats/03_Avro.md)), preventing producers from breaking consumers.
- **Kafka Streams / ksqlDB** — stream processing (joins, windows, aggregations) directly on Kafka, SQL-like.

## Log compaction

Beyond time/size retention, Kafka can **compact** a topic — keep only the *latest* value per key, discarding older versions. This turns a topic into a durable "current state per key" store — ideal for changelog/CDC topics and rebuilding caches. It's a distinctive Kafka capability worth naming in interviews.

## ZooKeeper → KRaft

Older Kafka used **ZooKeeper** for cluster metadata/coordination; modern Kafka replaces it with **KRaft** (Kafka Raft), removing the ZooKeeper dependency for a simpler, more scalable architecture. If asked "does Kafka need ZooKeeper?", the current answer is "no — KRaft mode is the modern default."

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The real Kafka question is "managed or self-managed?"

Kafka's technology is rarely the hard part — **operating** it is. Running your own cluster means owning broker sizing, disk/retention capacity, partition rebalancing, upgrades, and 3 a.m. failovers. The senior default on Azure is **managed** (Event Hubs Kafka endpoint or Confluent Cloud) unless there's a concrete reason for self-management (specific ecosystem features, on-prem, cost at extreme scale, or hard data-residency). Choosing to self-host Kafka is choosing to staff a platform team for it — a deliberate decision, not a default.

## Partition count is a capacity-planning commitment

Like Event Hubs, partition count caps consumer parallelism and is painful to change (increasing it breaks key-based ordering for existing data). Over-partitioning wastes broker resources and increases end-to-end latency and rebalance time; under-partitioning caps throughput. The pro sizes partitions from target throughput ÷ per-consumer throughput, with headroom — and treats it as a design decision, not a default of 1.

## Exactly-once is real in Kafka, but scoped

Kafka genuinely supports transactional exactly-once *within Kafka* (read-process-write across topics). The moment you write to an **external** sink (a database, an API), EOS depends on that sink's idempotency/transaction support — Kafka can't make an arbitrary external write exactly-once by itself. Know the boundary: EOS holds inside the Kafka ecosystem; at the edge, you design idempotent sinks.

## Field-tested gotchas

- **Self-hosting without the team** — a Kafka cluster nobody's trained to operate becomes an outage waiting to happen; prefer managed.
- **`acks=1` where `acks=all` was needed** — silent data loss on leader failure for critical topics.
- **Skewed partition key** — a hot partition throttles throughput while others idle.
- **No Schema Registry** — a producer changes a field and silently breaks every consumer; enforce schemas.
- **Treating Kafka as long-term storage/DB** — it's a log; land data in a queryable store for analytics.
- **Increasing partitions on a keyed topic** — reshuffles key→partition mapping and breaks per-key ordering for old data.

## Interview-grade Q&A

- *What is Kafka?* An open-source distributed, partitioned, replicated commit log for high-throughput event streaming — the de-facto standard that defined topics/partitions/offsets/consumer groups.
- *Kafka vs Event Hubs?* Same log model; Kafka is OSS/self-managed with a rich ecosystem (Connect, Schema Registry, Streams), Event Hubs is fully managed and Kafka-protocol compatible — on Azure, managed usually wins unless you need Kafka-specific features.
- *How does Kafka guarantee durability?* Partition replication across brokers with a leader + in-sync replicas; `acks=all` + `min.insync.replicas` ensures writes survive broker failure.
- *What is a consumer group?* A set of consumers that split a topic's partitions among themselves for parallel processing; different groups read the same topic independently with their own offsets.
- *What is log compaction?* Retention that keeps only the latest value per key, turning a topic into a durable current-state store — ideal for changelogs/CDC.
- *Does Kafka still need ZooKeeper?* No — modern Kafka uses KRaft mode, removing the ZooKeeper dependency.

---

## Related Notes

- **Prev:** [Azure Event Hubs](02_Azure_Event_Hubs.md) · **Next:** [Azure Stream Analytics](04_Azure_Stream_Analytics.md)
- **Concepts:** [Streaming Fundamentals](01_Streaming_Fundamentals.md) · **Process with:** [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)
- **Related:** [Change Data Capture (Debezium)](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) · [Avro & Schema Registry](../05_Storage_and_Formats/File_Formats/03_Avro.md)
- **Interview:** [Kafka Q&A](../Job%20Interviews/Kafka/Kafka%20Interview%20Questions.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Apache Kafka docs: https://kafka.apache.org/documentation/
- Event Hubs for Kafka: https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview
- Confluent intro to Kafka: https://developer.confluent.io/what-is-apache-kafka/

**Videos**
- Apache Kafka explained: https://www.youtube.com/results?search_query=apache+kafka+explained
- Kafka in 100 seconds / fundamentals: https://www.youtube.com/results?search_query=kafka+fundamentals+partitions+consumer+groups
