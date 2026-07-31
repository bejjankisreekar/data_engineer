# Streaming Fundamentals

## What is it?

**Stream processing** is handling data **continuously, one event at a time (or in tiny micro-batches), as it arrives** — instead of collecting it into a big pile and processing it later on a schedule. A "stream" is an unbounded, never-ending sequence of events: clicks, sensor readings, transactions, log lines.

The goal is **low latency**: reacting to data in seconds, not hours. Fraud detection, live dashboards, real-time recommendations, and IoT monitoring all need answers *now*, which batch can't provide.

In one line: **streaming = process each event as it happens; batch = process a collected chunk on a schedule.**

---

## Analogy: a river vs a reservoir

**Batch** is a **reservoir**: water (data) collects behind a dam, and once a day you open the gates and process the whole lot at once. Efficient, but everything waits for the scheduled release.

**Streaming** is a **river**: water flows past continuously, and you act on it *as it passes* — a water-quality sensor mid-river reacts to a pollutant in seconds, not tomorrow. The river never "ends," so you can never wait for "all the data" — you work on what's flowing by, right now.

---

## Batch vs Streaming

| | Batch | Streaming |
|---|---|---|
| Data | Bounded (a finite chunk) | Unbounded (never ends) |
| Latency | Minutes to hours | Milliseconds to seconds |
| Trigger | Schedule (e.g. nightly) | Event arrival, continuous |
| Question it answers | "What happened yesterday?" | "What is happening right now?" |
| Examples | Nightly warehouse load, monthly report | Fraud alerts, live dashboards, IoT |
| Cost/complexity | Simpler, cheaper | Harder, needs care (state, ordering, failures) |

Most real platforms use **both** — streaming for the fresh/reactive layer, batch for heavy historical reprocessing ([ETL vs ELT](../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md)).

---

## The event log: the core abstraction

Modern streaming is built on a **distributed, append-only log** (Event Hubs and Kafka both *are* this):

- Events are **appended** in order and **kept for a retention period**.
- The log is split into **partitions** for parallelism (order is guaranteed *within* a partition, not across).
- **Many consumers** read the same log **independently**, each tracking its own position (**offset**).
- Consumers are decoupled from producers — a slow or crashed consumer doesn't block the producer or other consumers.

This "one durable log, many independent readers" design is why streaming platforms scale and why they replaced older point-to-point queues.

---

## The three hard problems of streaming

Streaming is harder than batch because of three realities batch never faces:

**1. Time — event time vs processing time**
An event *happens* at one moment (event time) but is *processed* later (processing time), and the gap is unpredictable — a phone goes through a tunnel and its events arrive 5 minutes late, out of order. Correct streaming reasons about **event time**, not when the data showed up.

**2. Windows — how do you aggregate an infinite stream?**
You can't `GROUP BY` a stream that never ends, so you slice time into **windows**:

| Window | Shape | Example use |
|---|---|---|
| **Tumbling** | Fixed-size, non-overlapping | "Count per 1-minute bucket" |
| **Hopping / Sliding** | Fixed-size, overlapping | "5-min count, updated every 1 min" |
| **Session** | Gap-based, variable length | "Group activity until 30 min idle" |

**3. Late & out-of-order data — watermarks**
Because events arrive late, "when is a window *done*?" is genuinely hard. A **watermark** is the system's assertion: *"I don't expect events older than this timestamp anymore"* — it lets a window close and emit results while tolerating some lateness. Set it too tight and you drop late data; too loose and you hold state and delay results.

---

## Delivery semantics (a guaranteed interview question)

What happens to an event if something fails and retries?

| Guarantee | Meaning | Trade-off |
|---|---|---|
| **At-most-once** | Each event processed 0 or 1 times | Fast, but can **lose** data |
| **At-least-once** | Each event processed 1+ times | No loss, but can **duplicate** |
| **Exactly-once** | Each event effect applied exactly 1 time | Correct, but **hardest/costliest** |

"Exactly-once" is really **effectively-once**: achieved with idempotent writes + checkpoints/offsets + transactional sinks, not by magically never retrying. Understanding *why* it's hard — and that most systems default to at-least-once + idempotency — is what interviewers probe.

---

## Advantages of streaming

- **Real-time reaction** — alerts, fraud detection, live personalization.
- **Fresh dashboards** — see "now," not "yesterday."
- **Decoupling** — the event log separates producers from consumers, so systems scale independently.
- **Replay** — a durable log lets you reprocess history by resetting offsets.

## Disadvantages

- **Complexity** — state, windows, watermarks, ordering, and failure handling are genuinely hard.
- **Cost** — always-on compute vs batch's scheduled bursts.
- **Debugging** — a bug in a never-ending job is harder to reproduce than a batch rerun.
- **Overkill risk** — many "real-time" requirements are actually "every few minutes," which micro-batch or frequent batch serves more cheaply.

---

## Azure Usage

The Azure streaming stack:

| Role | Azure services |
|---|---|
| **Ingest / buffer** (the log) | **Event Hubs**, IoT Hub, or **Kafka** (self-managed / HDInsight / Confluent) |
| **Process** the stream | **Stream Analytics** (SQL), **Spark Structured Streaming** (Databricks), Azure Functions |
| **Serve** results | Power BI (real-time), ADLS/Delta, Azure SQL, **Cosmos DB**, alerts |
| **Modern unified** | **Microsoft Fabric Real-Time Intelligence** (Eventstream + Eventhouse/KQL) |

---

## Real World Example

A ride-hailing app needs surge pricing that reacts within seconds to demand. Every ride request and driver location becomes an **event** streamed into **Event Hubs**. A **Stream Analytics** job aggregates requests per neighbourhood in a **tumbling 1-minute window**, using **event time** so a request delayed by a flaky mobile connection still counts in the right minute (a **watermark** tolerates ~30 seconds of lateness before closing the window). When demand outstrips nearby drivers, it emits a surge multiplier to the pricing service and a live ops dashboard — all within seconds of the requests happening, something a nightly batch job could never do.

---
---

# Part 2 — Advanced

## Lambda vs Kappa architecture

Two classic ways to combine batch and streaming:

- **Lambda** — run **two** pipelines: a *speed layer* (streaming, fast but approximate) and a *batch layer* (slow but accurate/complete), then merge them at serving time. Robust, but you maintain the *same logic twice* in two codebases — the well-known Lambda tax.
- **Kappa** — run **one** streaming pipeline for everything; reprocess history by **replaying the log** through the same code. Simpler (one codebase), and increasingly practical now that logs (Kafka/Event Hubs) and engines (Spark/Flink) can replay at scale. The lakehouse + Structured Streaming makes Kappa the modern default for many teams.

## Stateful vs stateless processing

- **Stateless** — each event handled independently (filter, map, enrich with static reference data). Easy, scales trivially.
- **Stateful** — the result depends on *past* events (windowed counts, running totals, sessionization, dedup). Requires the engine to **store state** reliably (checkpointed), which is where most streaming complexity and failure-recovery logic lives ([checkpoints](../06_Programming/PySpark/13_Structured_Streaming.md)).

## Backpressure & throughput

When events arrive faster than consumers can process, systems need **backpressure** — slowing intake or buffering — so they degrade gracefully instead of crashing or running out of memory. Partitioning is the main lever: more partitions → more parallel consumers → higher throughput, up to the point where a downstream sink becomes the bottleneck.

## Ordering guarantees

Order is guaranteed only **within a partition**, and only if a stable **partition key** routes related events together (e.g. all events for one `device_id` to the same partition). Across partitions there is no global order. Choosing the partition key is therefore a correctness decision, not just a scaling one — the wrong key scatters an entity's events across partitions and destroys per-entity ordering.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## "Real-time" is a requirement to interrogate, not accept

The most valuable question a senior asks is *"how real-time, really?"* True sub-second needs (fraud, trading, safety) justify streaming's cost and complexity. "The dashboard should feel fresh" usually means 1–5 minute micro-batch — far cheaper and simpler. Building a full streaming stack for a requirement that frequent batch would satisfy is one of the most common (and expensive) over-engineering mistakes in data platforms.

## Exactly-once is a system property, not a checkbox

You don't "turn on" exactly-once. You compose it: **replayable source** (offsets you can rewind) + **checkpointed state** + **idempotent or transactional sink**. Break any link and you're back to at-least-once. The pro designs the *sink* for idempotency (upserts keyed by event id, transactional Delta writes) rather than trusting the framework to make duplicates impossible — because at-least-once + idempotent write is how "exactly-once" actually ships.

## Event time and watermarks decide correctness under lateness

The watermark is a **latency-vs-completeness dial**. Tight watermark → low latency, but late events are dropped or sent to a side output. Loose watermark → more correct, but more state held and higher latency. There's no universally right setting — it's a business call ("how late can data be and still matter?"). Teams that ignore this ship dashboards that silently under-count during network blips.

## Field-tested gotchas

- **Processing time masquerading as event time** — aggregations wrong whenever data is late; always window on event time for correctness.
- **Wrong partition key** — related events scattered across partitions, per-entity ordering and stateful logic broken.
- **Unbounded state** — a session/dedup job with no watermark or TTL grows state forever and OOMs.
- **Sink is the bottleneck** — scaling ingestion partitions won't help if the database/API you write to can't keep up; design the sink first.
- **Streaming for a batch problem** — always-on cost and complexity for freshness nobody needed.
- **Assuming exactly-once for free** — most defaults are at-least-once; make writes idempotent.

## Interview-grade Q&A

- *Batch vs streaming?* Batch processes a bounded chunk on a schedule (high latency, simple); streaming processes an unbounded event stream continuously (low latency, complex — state, windows, ordering).
- *Event time vs processing time?* When the event actually happened vs when it was processed; correct streaming aggregates on event time and uses watermarks to tolerate late/out-of-order arrivals.
- *Explain window types.* Tumbling (fixed, non-overlapping), hopping/sliding (fixed, overlapping), session (gap-based, variable) — how you aggregate an infinite stream over time.
- *At-least-once vs exactly-once?* At-least-once may duplicate (no loss); exactly-once applies each effect once — achieved via replayable offsets + checkpoints + idempotent/transactional sinks, not by avoiding retries.
- *Lambda vs Kappa?* Lambda runs separate batch and speed layers (duplicate logic); Kappa runs one streaming pipeline and replays the log for reprocessing (one codebase, modern default).
- *Where is ordering guaranteed?* Only within a partition, via a stable partition key — never globally across partitions.

---

## Related Notes

- **Next:** [Azure Event Hubs](02_Azure_Event_Hubs.md)
- **Spark side:** [Structured Streaming](../06_Programming/PySpark/13_Structured_Streaming.md)
- **Context:** [ETL vs ELT](../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) · [Data Integration Fundamentals](../05_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md) · [Change Data Capture](../05_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Stream processing (Azure architecture): https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/real-time-processing
- Windowing (Stream Analytics): https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-window-functions

**Videos**
- Batch vs stream processing: https://www.youtube.com/results?search_query=batch+vs+stream+processing+explained
- Event time watermarks streaming: https://www.youtube.com/results?search_query=event+time+watermark+streaming
