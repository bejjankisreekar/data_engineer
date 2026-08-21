# Azure Event Hubs

## What is it?

**Azure Event Hubs** is a **fully-managed, big-data event ingestion service** — a durable, partitioned event log in the cloud that can take in *millions of events per second* from many producers and let many consumers read them independently. It's Azure's answer to "where do I put a firehose of events so I can process them?"

It's the **front door** of most Azure streaming pipelines: apps, devices, and logs send events *to* Event Hubs, and processors like [Stream Analytics](04_Azure_Stream_Analytics.md) or [Spark Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md) read *from* it.

In one line: **Event Hubs = a managed, massively-scalable event log (Kafka-compatible) for ingesting streams into Azure.**

---

## Analogy: a conveyor belt at a sorting facility

Event Hubs is a **conveyor belt** at a parcel-sorting facility. Parcels (events) are dropped onto the belt continuously by many senders (producers). The belt is split into several **lanes** (partitions) so many workers can pick from it in parallel. Crucially, different **teams** (consumer groups) can each watch the *entire* belt independently — the billing team, the analytics team, and the archive team all see every parcel, each keeping their own place in line — without interfering with each other. The belt holds parcels for a set time (retention) before they roll off the end.

---

## Core concepts

```
Producers ──► ┌──────────── Event Hub ────────────┐
              │  Partition 0: e e e e e ►          │
              │  Partition 1: e e e ►              │  ◄─ Consumer Group A (analytics)
              │  Partition 2: e e e e e e ►        │  ◄─ Consumer Group B (archive)
              └───────────────────────────────────┘
```

| Concept | What it is |
|---|---|
| **Namespace** | The container/scoping unit that holds one or more event hubs (and a Kafka endpoint) |
| **Event Hub** | A single event log (analogous to a Kafka *topic*) |
| **Partition** | A parallel sub-log; ordering is guaranteed **within** a partition only |
| **Producer / Publisher** | Sends events (via AMQP, HTTPS, or the Kafka protocol) |
| **Consumer Group** | An independent "view" of the whole hub; each group tracks its own position |
| **Offset / Checkpoint** | A consumer's saved position, so it resumes where it left off |
| **Partition Key** | Routes related events to the same partition (preserves per-key order) |
| **Retention** | How long events are kept (then they expire) |

---

## Advantages

- **Massive scale** — millions of events/sec, elastic throughput.
- **Fully managed** — no brokers to patch or clusters to run (unlike self-hosted [Kafka](03_Apache_Kafka.md)).
- **Kafka-compatible** — existing Kafka apps connect by changing the connection string, no code rewrite.
- **Multiple independent consumers** — consumer groups let many pipelines read the same stream.
- **Event Hubs Capture** — auto-archive the stream to [ADLS/Blob](../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) as [Avro](../05_Storage_and_Formats/File_Formats/03_Avro.md), no code.
- **Deep Azure integration** — native inputs to Stream Analytics, Functions, Databricks; secured by Entra ID.

## Disadvantages

- **Not a message queue** — it's a *log* (pub/sub, replayable), not a per-message queue with per-message ack/delete; use **Service Bus** for that pattern.
- **Partition count is (mostly) fixed** — chosen up front; sizing partitions wrong limits parallelism (Premium/Dedicated relax this).
- **Retention limits** — Standard keeps events for a limited window (not an infinite store); use Capture for permanence.
- **Ordering only per partition** — no global ordering, same as Kafka.

---

## Tiers

| Tier | For | Throughput unit |
|---|---|---|
| **Basic** | Simple, low-volume | Throughput Units (TUs), 1 consumer group |
| **Standard** | Most workloads | Throughput Units (TUs), Capture, 20 consumer groups |
| **Premium** | Higher, isolated performance | Processing Units (PUs), better isolation |
| **Dedicated** | Massive, single-tenant | Capacity Units (CUs), highest scale |

A **Throughput Unit (TU)** ≈ 1 MB/s or 1000 events/s ingress, 2 MB/s egress — you scale by adding TUs (or enabling auto-inflate).

---

## Azure Usage

Typical pipeline shapes:

```
IoT devices ─► IoT Hub ─┐
Apps / logs ────────────┼─► Event Hubs ─► Stream Analytics ─► Power BI (live)
Clickstream ────────────┘                └─► Databricks (Delta) ─► lakehouse
                                          └─► Capture ─► ADLS (Avro, for batch/replay)
```

- **IoT Hub** is a superset of Event Hubs for devices (adds device management, two-way messaging) but exposes an Event Hubs-compatible endpoint.
- **Capture** writes the raw stream to ADLS automatically — the easiest way to get a durable Bronze copy for replay/batch.

---

## Real World Example

An e-commerce site streams every clickstream event — page views, add-to-cart, searches — into an **Event Hub** with 8 partitions, keyed by `session_id` so each user's journey stays ordered within a partition. Three **consumer groups** read the same stream independently: a **Stream Analytics** job powers a live "trending products" dashboard, a **Databricks** job lands events as Delta for the lakehouse, and **Event Hubs Capture** archives everything to ADLS as Avro for later reprocessing. On Black Friday, **auto-inflate** scales throughput units up automatically to absorb the traffic spike, then scales back down — no manual intervention, no dropped events.

---

## Partitions: the scaling and ordering lever

Partition count sets the **maximum consumer parallelism** — you can't have more active concurrent readers (in one consumer group) than partitions. Choose a **partition key** that spreads load evenly *and* keeps related events together (`device_id`, `customer_id`). Pitfalls: too few partitions caps throughput; a skewed key ("hot partition") overloads one lane; no key means round-robin (good balance, but loses per-entity ordering). Partition count is hard to change after creation on Standard, so size it for future load.

## Consumer groups & checkpointing

Each consumer group is an independent cursor over the whole hub. Within a group, the modern SDK/Event Processor balances partitions across consumer instances and **checkpoints** each consumer's offset (to Blob storage) so a crash resumes without reprocessing everything. Rule: **one consumer group per downstream application** — sharing a group across unrelated apps causes them to steal partitions from each other.

## Event Hubs vs Service Bus vs Event Grid

A classic Azure comparison — pick by *messaging shape*:

| Service | Shape | Use for |
|---|---|---|
| **Event Hubs** | High-throughput event **stream** (log, replayable) | Telemetry, clickstream, big-data ingestion |
| **Service Bus** | Enterprise **message queue** (per-message, ordering, transactions, dead-letter) | Commands, orders, workflows needing guaranteed per-message handling |
| **Event Grid** | Lightweight **event routing** (reactive, pub/sub of discrete events) | "A blob was created" → trigger a function |

Event Hubs is for *streams of data*; Service Bus is for *messages/commands*; Event Grid is for *reactive event notifications*.

## The Kafka endpoint

Event Hubs exposes a **Kafka-compatible endpoint** (protocol 1.0+), so Kafka producers/consumers, Kafka Connect, and frameworks like Spark's Kafka source work against Event Hubs by only changing the bootstrap servers and auth. This lets teams get **managed Kafka semantics** without running Kafka — a common reason to pick Event Hubs over self-hosted Kafka on Azure.

---

## Capture is the cheapest path to a replayable Bronze layer

Turning on **Event Hubs Capture** gives you, for free and with no code, a durable Avro copy of the raw stream in ADLS — which *is* your [Bronze layer](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) and your replay source. The pro pattern: process the live stream for low-latency needs *and* let Capture archive everything, so you can rebuild downstream tables by reprocessing the archive when logic changes — the [Kappa](01_Streaming_Fundamentals.md) replay story, made easy on Azure.

## Partition sizing is a one-way door — plan for peak

Because Standard-tier partition count is fixed at creation and caps parallelism forever, under-provisioning partitions is a mistake you live with. The field rule: estimate *peak* future concurrency and set partitions with headroom (a common default is 4–32 depending on scale), since you can always run fewer consumers than partitions but never more. Premium/Dedicated allow more flexibility, but the "size for peak up front" instinct still applies.

## Throughput units vs the real bottleneck

Teams scale TUs when throttled, but the bottleneck is often **downstream** (the processor or sink can't keep up) or a **hot partition** (skewed key), not raw ingress capacity. Diagnose *where* the backpressure is before buying TUs — auto-inflate handles genuine ingress spikes, but it won't fix a skewed key or a slow database sink.

## Field-tested gotchas

- **Treating Event Hubs like a queue** — expecting per-message delete/ack; it's a replayable log. Use Service Bus for true queue semantics.
- **Too few partitions** — silently caps consumer parallelism; can't be raised easily on Standard.
- **Hot partition from a skewed key** — one lane overloaded while others idle; choose a high-cardinality, even key.
- **Sharing one consumer group across apps** — they rebalance and steal partitions from each other; one group per app.
- **Forgetting retention** — assuming events persist forever; enable Capture for durability.

## Interview-grade Q&A

- *What is Event Hubs?* A fully-managed, partitioned, Kafka-compatible event-ingestion log for streaming millions of events/sec into Azure, read independently by many consumer groups.
- *Event Hubs vs Kafka?* Same log/partition/consumer-group model; Event Hubs is fully managed (no brokers) and Kafka-protocol compatible, while Kafka is OSS/self-managed with a richer ecosystem and more control.
- *Event Hubs vs Service Bus?* Event Hubs is a high-throughput replayable *stream* (telemetry, big data); Service Bus is an enterprise *message queue* (per-message ack, ordering, dead-letter) for commands/workflows.
- *What are consumer groups?* Independent views of the whole hub — each downstream app gets its own group and offset so multiple pipelines read the same stream without interfering.
- *What is Capture?* Automatic archival of the stream to ADLS/Blob as Avro with no code — an easy durable Bronze/replay copy.
- *Why does partition count matter?* It caps consumer parallelism and defines ordering scope; it's mostly fixed at creation, so size for peak.

---

## Related Notes

- **Prev:** [Streaming Fundamentals](01_Streaming_Fundamentals.md) · **Next:** [Apache Kafka](03_Apache_Kafka.md)
- **Process it with:** [Stream Analytics](04_Azure_Stream_Analytics.md) · [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)
- **Land it in:** [ADLS](../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) · [Lakehouse/Bronze](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)
- **Interview:** [Event Hub Q&A](../Job%20Interviews/Event%20Hub/Event%20Hub%20Interview%20Questions.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Event Hubs overview: https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about
- Event Hubs Capture: https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview
- Event Hubs for Kafka: https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview

**Videos**
- Azure Event Hubs explained: https://www.youtube.com/results?search_query=azure+event+hubs+explained
- Event Hubs vs Service Bus vs Event Grid: https://www.youtube.com/results?search_query=event+hubs+vs+service+bus+vs+event+grid
