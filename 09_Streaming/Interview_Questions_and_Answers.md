# Streaming — Interview Questions & Answers

Covers the whole module: [Fundamentals](01_Streaming_Fundamentals.md), [Event Hubs](02_Azure_Event_Hubs.md), [Kafka](03_Apache_Kafka.md), [Stream Analytics](04_Azure_Stream_Analytics.md). Tagged **[Theory]** / **[Scenario]**, ⭐ = very frequently asked. See also the interview folders: [Event Hub](../Job%20Interviews/Event%20Hub/Event%20Hub%20Interview%20Questions.md) · [Kafka](../Job%20Interviews/Kafka/Kafka%20Interview%20Questions.md) · [Stream Analytics](../Job%20Interviews/Stream%20Analytics/Stream%20Analytics%20Interview%20Questions.md).

---

## Fundamentals

**1. ⭐ [Theory] Batch vs streaming?**
Batch processes a bounded chunk of data on a schedule — high latency (minutes to hours), simpler, answers "what happened?" Streaming processes an unbounded stream of events continuously — low latency (ms to seconds), harder (state, windows, ordering, failures), answers "what is happening now?" Most platforms use both.

**2. ⭐ [Theory] Event time vs processing time?**
Event time is when the event actually occurred; processing time is when the system handled it. They differ unpredictably because events arrive late and out of order. Correct streaming aggregates on **event time** and uses **watermarks** to tolerate lateness — otherwise results are wrong whenever data is delayed.

**3. ⭐ [Theory] Explain window types.**
Tumbling (fixed-size, non-overlapping — count per minute), hopping/sliding (fixed-size, overlapping — 5-min count every minute), and session (gap-based, variable — activity until idle). Windows are how you aggregate an infinite stream over time.

**4. [Theory] What is a watermark?**
The system's assertion that "no events older than this timestamp are expected anymore." It lets a window close and emit results while tolerating some late data. Tight watermark = low latency but drops late events; loose = more correct but higher latency and more state — a business trade-off.

**5. ⭐ [Theory] At-least-once vs exactly-once delivery?**
At-least-once guarantees no loss but may duplicate; exactly-once applies each effect once. Exactly-once is really "effectively once," achieved with replayable offsets + checkpointed state + idempotent/transactional sinks — not by avoiding retries. Most systems default to at-least-once + idempotent writes.

**6. [Theory] Lambda vs Kappa architecture?**
Lambda runs two pipelines — a fast streaming speed layer and an accurate batch layer — merged at serving (duplicate logic). Kappa runs one streaming pipeline and reprocesses history by replaying the log (one codebase) — the modern default with lakehouse + Structured Streaming.

**7. [Scenario] The business wants a "real-time" dashboard. What do you ask?**
"How real-time, really?" True sub-second needs (fraud, safety) justify streaming; "should feel fresh" usually means 1–5 minute micro-batch, which is far cheaper and simpler. Matching latency to the actual requirement avoids over-engineering.

**8. [Theory] Where is event ordering guaranteed?**
Only **within a partition**, and only if a stable partition key routes related events together. There's no global ordering across partitions — so the partition key is a correctness decision, not just a scaling one.

---

## Event Hubs

**9. ⭐ [Theory] What is Azure Event Hubs?**
A fully-managed, partitioned, Kafka-compatible event-ingestion log that takes in millions of events/sec and lets many consumer groups read the stream independently — the front door of most Azure streaming pipelines.

**10. ⭐ [Theory] Event Hubs vs Service Bus vs Event Grid?**
Event Hubs = high-throughput replayable event **stream** (telemetry, clickstream, big data). Service Bus = enterprise **message queue** (per-message ack, ordering, dead-letter — commands/workflows). Event Grid = lightweight **event routing** (reactive notifications like "blob created → run function").

**11. [Theory] What are consumer groups?**
Independent views of the whole event hub — each downstream app gets its own consumer group and tracks its own offset, so multiple pipelines read the same stream without interfering.

**12. [Scenario] Why does partition count matter, and can you change it later?**
It caps consumer parallelism (no more concurrent readers than partitions) and defines ordering scope. On Standard tier it's mostly fixed at creation, so size for peak future load; too few throttles throughput, and a skewed key creates a hot partition.

**13. ⭐ [Theory] What is Event Hubs Capture?**
Automatic, no-code archival of the stream to ADLS/Blob as Avro — an easy durable Bronze/replay copy that supports later batch reprocessing (the Kappa replay story).

**14. [Scenario] A Kafka team is moving to Azure but doesn't want to run Kafka. Options?**
Use the Event Hubs **Kafka endpoint** — their Kafka producers/consumers connect by changing the bootstrap servers and auth, no code rewrite — getting managed Kafka semantics without operating a cluster. (Confluent Cloud on Azure is the alternative for the full ecosystem.)

---

## Kafka

**15. ⭐ [Theory] What is Apache Kafka?**
An open-source distributed, partitioned, replicated commit log for high-throughput event streaming — the de-facto standard that defined topics, partitions, offsets, and consumer groups.

**16. ⭐ [Theory] Kafka vs Event Hubs?**
Same log/partition/consumer-group model. Kafka is OSS/self-managed with a rich ecosystem (Connect, Schema Registry, Streams/ksqlDB) and full control; Event Hubs is fully managed and Kafka-protocol compatible. On Azure, managed (Event Hubs/Confluent) usually wins unless you need Kafka-specific features or on-prem.

**17. [Theory] How does Kafka guarantee durability?**
Each partition is replicated across brokers with a leader and in-sync replicas (ISR). `acks=all` plus `min.insync.replicas` ensures a write is confirmed by multiple replicas, so it survives a broker failure; a failed leader is replaced by an ISR.

**18. [Theory] What is log compaction?**
A retention mode that keeps only the latest value per key, discarding older versions — turning a topic into a durable "current state per key" store, ideal for changelog/CDC topics and cache rebuilds.

**19. [Theory] What is Kafka Connect and Schema Registry?**
Connect provides pre-built connectors to move data in/out of Kafka without custom code (including CDC via Debezium). Schema Registry enforces and evolves message schemas (Avro) so a producer change can't silently break consumers.

**20. [Scenario] Does Kafka still need ZooKeeper?**
No — modern Kafka uses **KRaft** mode (Kafka Raft) for metadata/coordination, removing the ZooKeeper dependency for a simpler, more scalable architecture.

**21. [Scenario] Should we self-host Kafka or use managed?**
Default to managed (Event Hubs Kafka endpoint / Confluent Cloud) — self-hosting means owning broker sizing, capacity, rebalancing, upgrades, and failovers, i.e. staffing a platform team. Self-host only for concrete reasons: specific ecosystem needs, on-prem, data residency, or cost at extreme scale.

---

## Stream Analytics

**22. ⭐ [Theory] What is Azure Stream Analytics?**
A fully-managed, SQL-based stream-processing service: a streaming input (Event Hubs/IoT Hub) → a SQL query with windowing → an output (Power BI, ADLS, SQL, Cosmos DB), with no infrastructure to manage.

**23. ⭐ [Theory] Stream Analytics vs Spark Structured Streaming?**
ASA is low-code SQL, fully managed, ideal for simple-to-moderate jobs (filter, windowed aggregate, enrich, alert, live dashboard). Structured Streaming is code-based for complex logic, custom libraries, ML, and lakehouse-native writes. Choose by complexity — don't over-build on Spark for a 15-line SQL problem.

**24. [Theory] What does `TIMESTAMP BY` do?**
Declares the event-time column so ASA aggregates on event time instead of arrival time — required for correct windowed results when data is late or out of order.

**25. [Theory] What is reference data in ASA?**
A static or slowly-changing lookup (from Blob/SQL) joined to the fast stream to enrich skinny events (e.g. map `sensor_id` → room/floor) with business context, held in memory and periodically refreshed.

**26. [Scenario] You added Streaming Units but the ASA job didn't get faster. Why?**
The query likely isn't partition-aligned — a cross-partition shuffle serializes processing, so more SUs don't help. Keep the partition key consistent (input partition → `PARTITION BY` → partitioned output) so processing parallelizes across partitions.

**27. [Theory] What is a temporal join?**
A join of two streams on time proximity (e.g. match a click to an impression within 10 seconds using `DATEDIFF` in the JOIN) — a genuinely streaming operation with no batch equivalent, used for attribution and correlation.

---

## Putting it together

**28. ⭐ [Scenario] Design a real-time pipeline for IoT sensor alerts and a live dashboard.**
Devices → **IoT Hub/Event Hubs** (partitioned by `device_id`). A **Stream Analytics** job reads `TIMESTAMP BY reading_time`, joins **reference data** for device→location, and uses a **tumbling window** to aggregate per location; it outputs alerts to **Service Bus** and live metrics to **Power BI**. **Event Hubs Capture** archives raw events to ADLS as the Bronze/replay layer. For heavier logic or lakehouse writes, swap the processor for **Databricks Structured Streaming**. Choose the late-arrival policy from how late data can be and still matter.

**29. [Scenario] How do you get exactly-once end to end?**
Use a replayable source (Event Hubs/Kafka offsets) + checkpointed stream state + an idempotent or transactional sink (e.g. Delta MERGE keyed by event id). "Exactly-once" is composed from these; it's not a single switch, and at the external-sink boundary it depends on the sink's idempotency.

**30. [Theory] What's the modern Azure streaming stack in one breath?**
Ingest with Event Hubs/IoT Hub (or Kafka), process with Stream Analytics (SQL) or Databricks Structured Streaming (code), serve to Power BI / Delta / Cosmos DB — with **Microsoft Fabric Real-Time Intelligence** (Eventstream + Eventhouse/KQL) as the newer unified direction.

---

## Related Notes

- Module: [00 Learning Path](00_Streaming_Learning_Path.md) → [01](01_Streaming_Fundamentals.md) · [02](02_Azure_Event_Hubs.md) · [03](03_Apache_Kafka.md) · [04](04_Azure_Stream_Analytics.md)
- [Structured Streaming](../06_Programming/PySpark/13_Structured_Streaming.md) · [Change Data Capture](../05_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) · [Lakehouse](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)
