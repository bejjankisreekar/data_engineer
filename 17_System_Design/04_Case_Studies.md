# System Design Case Studies

## How to use this note

Below are several full "design an X" walkthroughs using the [5-step framework](01_Design_Framework.md). Read them for the **reasoning pattern**, not to memorize answers — the interviewer will change the constraints, and your job is to re-derive from requirements. Each is deliberately compact; in a real interview you'd expand the section the interviewer pushes on.

---

## Case 1 — "Design the data platform for a ride-hailing app"

**1. Requirements:** live trip tracking + surge pricing (real-time), plus analytics for finance/ops (batch). Millions of trips/day; drivers, riders, trips, payments. Consumers: an ops dashboard (live), finance reports (daily), a pricing model (real-time features).

**2. Scale:** high write volume from phones (100k+ events/sec peak); TBs/day retained.

**3. Architecture:**
- **Live path:** phone events → **Event Hubs** → **Structured Streaming** → surge features in **Cosmos DB/Redis** (ms reads) + live ops **Delta** table.
- **Batch path:** the same stream lands **Bronze Delta** (Kappa); nightly Spark builds Silver/Gold star schemas (trip facts, driver/rider dims with SCD2).
- **Serve:** Databricks SQL/Fabric → Power BI for finance; Cosmos DB for the app.
- **Orchestrate/govern:** ADF/Workflows; Unity Catalog for PII (rider location!) and lineage.

**4. Trade-offs:** hybrid (streaming for surge/ops, batch for finance) because latency needs differ by consumer; Kappa to avoid dual codebases; NoSQL serving for live ms reads; lakehouse for cheap TB-scale history.

**5. Cross-cutting:** PII governance (location/payment), exactly-once for payments, freshness alerts, cost via job clusters + tiered storage.

---

## Case 2 — "Ingest 10M events/sec from IoT sensors"

**1. Requirements:** massive sensor telemetry; mostly analytical (trends, anomalies), some real-time alerting on thresholds; append-heavy, rarely updated.

**2. Scale:** 10M events/sec — extreme write throughput; enormous retained volume.

**3. Architecture:**
- **Ingest:** **Event Hubs/Kafka** (heavily partitioned) — built for this firehose.
- **Real-time alerting:** Structured Streaming/Stream Analytics filters threshold breaches → alert.
- **Store:** stream → **Delta Bronze** (or a wide-column store like **Cassandra** for the hot operational reads, given the append-heavy, key-based pattern — [wide-column](../02_Databases/NoSQL/04_Wide_Column_Stores.md)).
- **Process:** batch aggregations (per-sensor, per-hour) into Gold for analytics.

**4. Trade-offs:** wide-column/Delta for append-heavy time-series (not relational — wrong for this scale/pattern); partition by `(sensor_id, time_bucket)` to avoid hot partitions; batch for the analytics (trends don't need sub-second), streaming only for alerting.

**5. Cross-cutting:** partition-key design is make-or-break; time-bucket to bound partition growth; tier/expire old data (TTL + archive) for cost.

---

## Case 3 — "Migrate a nightly on-prem SQL warehouse to Azure"

**1. Requirements:** existing on-prem SQL Server warehouse; move to Azure with minimal disruption; keep the nightly batch; enable future scale and semi-structured data.

**2. Scale:** moderate/growing; known tables and reports.

**3. Architecture:**
- **Ingest:** **Self-hosted Integration Runtime** + ADF to pull from on-prem SQL → ADLS ([ADF](../11_Orchestration/02_ADF_Orchestration.md)).
- **Store/process:** medallion on ADLS/Delta; reimplement transforms in Spark/**dbt**.
- **Serve:** Synapse/Fabric or Databricks SQL → existing Power BI reports repointed.

**4. Trade-offs:** lift to a lakehouse (not just Azure SQL) for future semi-structured data + cheaper scale; dbt for tested, documented transforms replacing opaque stored procs; phased migration (run parallel, validate, cut over).

**5. Cross-cutting:** reconciliation testing (old vs new outputs — [audit-helper](../13_dbt/04_Snapshots_Seeds_Macros.md)), governance via Unity Catalog, cost via serverless/job clusters.

---

## Case 4 — "Design a near-real-time analytics dashboard"

**1. Requirements:** business wants a dashboard updating every **~1–5 minutes** (not sub-second) on orders; moderate volume.

**2. Scale:** thousands of events/min.

**3. Architecture:** this is the **micro-batch sweet spot** — **Auto Loader** or Structured Streaming with a **1-minute trigger** → Delta Gold → Power BI (DirectQuery or Direct Lake for freshness). No need for a full streaming stack.

**4. Trade-offs:** micro-batch over true streaming — meets the minutes SLA at far lower complexity/cost; Direct Lake/DirectQuery so the dashboard reflects new micro-batches without a long refresh.

**5. Cross-cutting:** trigger interval tunes the cost/freshness trade; monitor stream lag; OPTIMIZE to control small files from frequent micro-batches.

**Lesson:** "near-real-time" often means **micro-batch**, not full streaming — recognizing that is a senior distinction.

---

## The pattern across all cases

Notice the repeated moves, regardless of domain:
1. **Split by latency need** — batch for analytics, streaming/micro-batch only where value decays fast.
2. **Lakehouse + medallion** as the analytical backbone.
3. **Right storage for the access pattern** — relational, wide-column, or NoSQL serving as the pattern dictates.
4. **Always** address partitioning, idempotency, governance, cost, and monitoring.

Internalize the moves; the specific tools are interchangeable.

---

## Interview-grade Q&A

- *A prompt names a tool you've never used — what do you do?* Fall back to the framework: clarify requirements, reason about the *type* of component needed (ingestion/storage/processing), and map to something you know while noting the unfamiliar tool likely fills that role.
- *How do you handle "make it real-time"?* Pin down the actual latency: sub-second → streaming; minutes → micro-batch; hourly/daily → batch. Don't over-engineer.
- *When would you use a NoSQL/wide-column store in a design?* For append-heavy time-series/IoT at scale (wide-column) or low-latency key-based serving (key-value/document) — matched to the access pattern, not by default.
- *How do you de-risk a warehouse migration?* Phased/parallel run with reconciliation testing (old vs new outputs) before cutover, plus governance and cost planning.
- *What's common to every good design?* Requirements-first, split by latency, lakehouse+medallion backbone, storage matched to access pattern, and cross-cutting concerns addressed.

---

## Further Learning — Docs & Videos
- Azure Architecture Center — scenarios: https://learn.microsoft.com/azure/architecture/browse/?azure_categories=databases
- Big data architectures: https://learn.microsoft.com/azure/architecture/data-guide/big-data/
- Video — data engineering system design case studies: https://www.youtube.com/results?search_query=data+engineering+system+design+case+study
