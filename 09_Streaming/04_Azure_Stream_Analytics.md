# Azure Stream Analytics

## What is it?

**Azure Stream Analytics (ASA)** is a **fully-managed, SQL-based stream-processing service**. You point it at a streaming **input** (usually [Event Hubs](02_Azure_Event_Hubs.md) or IoT Hub), write a **SQL-like query** with windowing and filtering, and it continuously processes events and writes results to an **output** (Power BI, ADLS, SQL, Cosmos DB, and more) — all without managing any infrastructure or writing Spark.

If [Event Hubs/Kafka](02_Azure_Event_Hubs.md) is the *pipe* that buffers events, Stream Analytics is a *processor* that computes on the stream — the low-code option, versus [Spark Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md) for code-heavy needs.

In one line: **Stream Analytics = real-time stream processing written in SQL, fully managed, input → query → output.**

---

## Analogy: a smart filter on the conveyor belt

If [Event Hubs](02_Azure_Event_Hubs.md) is the conveyor belt of parcels, Stream Analytics is a **smart inspection station** you bolt onto the belt. You give it simple written instructions ("every minute, count parcels per city; flag any over 20 kg"), and it watches the belt continuously, does the counting and flagging in real time, and drops the results into whichever bin you choose (a dashboard, a database, a file). You never build or maintain the machine — you just write the rules in a language you already know: **SQL**.

---

## The model: input → query → output

```
INPUTS                    QUERY (SQL)                    OUTPUTS
─────────                 ────────────                   ────────
Event Hubs   ─┐           SELECT city,                   ┌─► Power BI (live dashboard)
IoT Hub      ─┼─► ASA ─►    COUNT(*) AS rides       ─────┼─► ADLS / Delta
Blob (ref)   ─┘           INTO OutputDashboard           ├─► Azure SQL
                          FROM RideInput TIMESTAMP BY t  ├─► Cosmos DB
                          GROUP BY city,                 └─► Service Bus / Functions
                            TumblingWindow(minute, 1)
```

- **Inputs** — streaming (Event Hubs, IoT Hub) + **reference data** (static/slowly-changing lookup from Blob/SQL to enrich the stream).
- **Query** — a T-SQL dialect with streaming extensions (windows, `TIMESTAMP BY`, temporal joins).
- **Outputs** — many sinks; **Power BI** for live dashboards is the signature one.

---

## Windowing functions (the heart of ASA)

ASA aggregates the infinite stream using [window functions](01_Streaming_Fundamentals.md):

| Window | Behaviour | Example |
|---|---|---|
| **Tumbling** | Fixed, non-overlapping buckets | Count per 1 minute |
| **Hopping** | Fixed size, overlaps by a hop | 5-min count every 1 min |
| **Sliding** | Emits when events enter/leave the window | Alert when >10 events in any 30s |
| **Session** | Groups activity until an idle gap | User activity until 2 min idle |
| **Snapshot** | Groups events with the same timestamp | Point-in-time aggregation |

`TIMESTAMP BY` tells ASA to use **event time** (a field in the data) instead of arrival time — essential for correct results with late/out-of-order data.

---

## Advantages

- **SQL, not code** — anyone who knows [SQL](../02_Databases/SQL/01_What_is_SQL.md) can build a streaming job; fast to develop.
- **Fully managed & serverless** — no clusters; scale with **Streaming Units (SUs)**.
- **Native Azure integration** — one-click inputs/outputs for Event Hubs, IoT Hub, Power BI, ADLS, SQL, Cosmos DB.
- **Built-in temporal features** — windows, `TIMESTAMP BY`, temporal joins, late-arrival policies out of the box.
- **Reference data joins** — enrich the stream with lookup data easily.
- **Built-in ML functions** — e.g. anomaly detection with a single function call.

## Disadvantages

- **Less flexible than Spark/Flink** — complex logic, custom libraries, or heavy transformations hit the SQL model's limits.
- **Azure-locked** — the query language and service are Azure-specific (unlike portable Spark/Kafka).
- **Cost at scale** — SUs for high-throughput, always-on jobs add up; heavy workloads may be cheaper on Databricks.
- **Debugging** — testing streaming SQL and diagnosing watermark/late-data behaviour takes practice.

---

## Azure Usage

- **Streaming Units (SUs)** — the compute/throughput unit you scale; more SUs = more parallel processing. Partition-aligned queries parallelize best.
- **Late arrival & out-of-order policies** — configurable tolerances that set the watermark behaviour (how long to wait for late events, how to handle out-of-order).
- **Where it fits:** the low-code processor in the Azure streaming stack. Reach for **Databricks Structured Streaming** instead when you need complex logic, custom code/libraries, ML pipelines, or lakehouse-native writes; reach for **Fabric Real-Time Intelligence / Eventstream** for the newer unified experience.

---

## Real World Example

A smart-building system streams temperature and occupancy from thousands of sensors into **IoT Hub**. A **Stream Analytics** job reads the stream `TIMESTAMP BY reading_time`, joins it against **reference data** (a Blob file mapping each sensor to a room and floor), and uses a **tumbling 5-minute window** to compute average temperature per floor. When a floor's average exceeds a threshold, it writes an alert to **Service Bus** (triggering HVAC adjustment) *and* streams the live averages to a **Power BI** dashboard for facilities staff — the entire pipeline is ~15 lines of SQL and zero managed infrastructure. When a batch of sensor readings arrives late from a flaky gateway, the configured 30-second late-arrival policy still counts them in the correct window.

---

## Reference data joins — enriching the stream

Streams are usually skinny (`sensor_id`, `value`) and need enrichment (which room? which customer tier?). ASA joins the fast stream against **reference data** — a static or slowly-refreshed lookup from Blob or SQL — so output carries business context. The reference dataset is held in memory and periodically refreshed; it's the idiomatic way to turn raw events into meaningful, dimensional output without a separate pipeline.

## Temporal joins

ASA can join **two streams** on time proximity with `DATEDIFF` inside the `JOIN` — e.g. match a `click` event to an `impression` event within 10 seconds. This "join events that happened near each other in time" is a genuinely streaming operation with no batch equivalent, used for attribution, correlation, and detecting sequences.

## Event ordering, watermarks & late data

ASA exposes the [streaming time problem](01_Streaming_Fundamentals.md) as concrete settings:
- **Late arrival tolerance** — how long to wait for events whose event-time is in the past.
- **Out-of-order tolerance** — how much reordering to buffer/absorb.
- **`TIMESTAMP BY`** — declares the event-time column.

These directly set the latency-vs-completeness trade-off. Too tight → correct-looking dashboards that silently drop late data; too loose → higher latency and more buffering.

## Scaling with Streaming Units and partitions

Throughput scales with **SUs**, but ASA parallelizes best when the query is **partition-aligned** — the input partition key flows through `PARTITION BY` so each partition is processed independently ("embarrassingly parallel"). A query that forces a cross-partition shuffle (e.g. aggregating across all partitions) limits parallelism. Aligning the query to input partitions is the main ASA performance lever.

---

## Stream Analytics vs Structured Streaming vs Flink — pick by complexity

The mature framing isn't "which is best" but "how complex is the logic?":
- **Stream Analytics** — simple-to-moderate: filtering, windowed aggregates, enrichment, alerting, live dashboards. Fastest to ship, lowest ops.
- **Spark Structured Streaming (Databricks)** — complex logic, custom code/UDFs/libraries, ML, and lakehouse-native writes; unifies with your batch code.
- **Apache Flink (Fabric RTI / self-managed)** — the most powerful for sophisticated event-time processing and very low latency at scale.

The senior chooses ASA for the many *simple* streaming jobs (and saves the org from over-building on Spark for a 15-line SQL problem), and reserves Databricks/Flink for genuinely complex ones. Using a heavyweight engine for a job ASA handles in SQL is a common over-engineering tax.

## Partition alignment is the real scaling secret

Throwing SUs at a job that isn't partition-aligned wastes money — ASA can't parallelize past a cross-partition bottleneck. The pro designs the whole path to keep the partition key consistent (Event Hubs partition → ASA `PARTITION BY` → partitioned output) so scaling SUs actually scales throughput linearly. Diagnosing "added SUs, no speedup" almost always leads back to partition alignment.

## The newer world: Fabric Real-Time Intelligence

Microsoft is unifying streaming under **Fabric Real-Time Intelligence** — **Eventstream** (no-code ingestion/routing, a spiritual successor to ASA's model) landing into **Eventhouse/KQL** databases for real-time analytics. Stream Analytics remains widely deployed and interview-relevant, but a current engineer should know Fabric RTI is where Microsoft is investing, and mention it when discussing "the modern Azure streaming stack."

## Field-tested gotchas

- **Arrival time instead of event time** — forgetting `TIMESTAMP BY` makes windowed results wrong under any lateness.
- **Non-partition-aligned query** — adding SUs doesn't help; the query serializes on a shuffle.
- **Over-tight late-arrival policy** — silently dropping late events and under-counting during network blips.
- **Forcing complex logic into ASA SQL** — some jobs belong in Databricks/Flink; don't contort SQL.
- **Reference data too large / stale** — huge or rarely-refreshed lookups hurt performance and correctness.

## Interview-grade Q&A

- *What is Azure Stream Analytics?* A fully-managed, SQL-based stream-processing service: streaming input (Event Hubs/IoT Hub) → SQL query with windows → output (Power BI, ADLS, SQL, Cosmos DB), no infrastructure to manage.
- *ASA vs Spark Structured Streaming?* ASA is low-code SQL for simple-to-moderate streaming (fast, managed, Azure-native); Structured Streaming is code-based for complex logic, custom libraries, ML, and lakehouse writes — choose by complexity.
- *What windowing does ASA support?* Tumbling, hopping, sliding, session, and snapshot windows — how it aggregates an unbounded stream over time.
- *What is `TIMESTAMP BY` and why does it matter?* It declares the event-time column so aggregation uses event time (not arrival time), which is required for correctness with late/out-of-order data.
- *What is reference data in ASA?* A static/slowly-changing lookup (Blob/SQL) joined to the stream to enrich skinny events with business context.
- *How do you scale ASA?* Add Streaming Units and keep the query partition-aligned so processing parallelizes across input partitions.

---

## Related Notes

- **Prev:** [Apache Kafka](03_Apache_Kafka.md) · **Module start:** [Learning Path](00_Streaming_Learning_Path.md)
- **Input from:** [Event Hubs](02_Azure_Event_Hubs.md) · **Alternative processor:** [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)
- **Concepts:** [Streaming Fundamentals](01_Streaming_Fundamentals.md) · **SQL basis:** [What is SQL](../02_Databases/SQL/01_What_is_SQL.md)
- **Interview:** [Stream Analytics Q&A](../Job%20Interviews/Stream%20Analytics/Stream%20Analytics%20Interview%20Questions.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Stream Analytics overview: https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-introduction
- Window functions: https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-window-functions
- Fabric Real-Time Intelligence: https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview

**Videos**
- Azure Stream Analytics explained: https://www.youtube.com/results?search_query=azure+stream+analytics+explained
- Stream Analytics windowing functions: https://www.youtube.com/results?search_query=azure+stream+analytics+windowing
