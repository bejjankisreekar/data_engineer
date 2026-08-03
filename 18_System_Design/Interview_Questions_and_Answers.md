# System Design — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. This module is about *approach* — the "answers" are reasoning patterns, not memorized designs.

---

## The framework

**Q1. 🔥 How do you approach a data system design question?**
Five steps: (1) **clarify requirements** (goal, latency, volume, consistency, consumers, budget), (2) **estimate scale**, (3) **sketch the architecture** (ingestion→storage→processing→serving→consumption), (4) **justify trade-offs** against requirements, (5) address **cross-cutting concerns** (reliability, quality, monitoring, security, cost).

**Q2. 🔥 What's the single most important first step?**
**Clarifying requirements** — especially batch vs real-time latency. Proposing tools before understanding requirements is the classic failure.

**Q3. ⭐ Why estimate scale early?**
Volume/throughput drive the architecture — single-node vs Spark, batch vs streaming, partition strategy, storage tier. "10 GB/day" and "10 TB/hour" are different systems.

**Q4. 🔥 What separates a strong answer from a weak one?**
Justified **trade-offs** tied to requirements ("batch because the SLA is daily") over tool name-dropping, plus proactively covering reliability, quality, cost, and governance.

**Q5. 💡 A prompt uses a tool you've never used — what now?**
Use the framework: reason about the *type* of component needed and map the unfamiliar tool to a category you know (it's probably an ingestion/storage/processing/serving choice). Designs are about roles, not brands.

---

## Batch design

**Q6. 🔥 When do you choose batch over streaming?**
When the SLA is minutes-to-days, data arrives as periodic files/extracts, and simplicity/cost matter more than latency — the analytics default.

**Q7. 🔥 Full load vs incremental — how and when?**
Incremental for scale, via a **watermark** column (`modified_date`) or **CDC**; full load only for small data. Track "what's new" explicitly.

**Q8. ⭐ How do you make a batch pipeline safe to rerun/backfill?**
Idempotency — MERGE/upsert on business keys or partition overwrite keyed to the run date.

**Q9. ⭐ How do you handle a slowly changing dimension?**
SCD2 (valid_from/valid_to/is_current) via Delta MERGE to preserve history.

**Q10. 🔥 Design a daily sales analytics platform (outline).**
Incremental ingest (ADF watermark + Auto Loader) → medallion on ADLS/Delta → Spark Bronze→Silver→Gold with SCD2 → Databricks SQL → Power BI; ADF orchestration with retries/alerts; quality gates, freshness SLA, governance, cost via job clusters. Justify batch + lakehouse + incremental.

---

## Streaming design

**Q11. 🔥 When do you genuinely need streaming?**
When a decision's value decays in seconds — fraud, live ops/alerting, IoT control, real-time personalization/pricing — not merely because "real-time sounds good."

**Q12. 🔥 Lambda vs Kappa architecture?**
Lambda = separate batch + speed layers (accurate + fast, but two codebases to sync); Kappa = one streaming path, reprocess by replaying the log (simpler, favored by the modern lakehouse).

**Q13. ⭐ How do you achieve exactly-once processing?**
Checkpointing (offset + state tracking) plus idempotent sinks (e.g., Delta MERGE).

**Q14. ⭐ How do you handle late-arriving data?**
Event-time windows with watermarks bounding how long to wait and how much state to keep.

**Q15. 💡 How do you scale a stream under load spikes?**
Partitioned ingestion (Event Hubs/Kafka partitions), autoscaling consumers, buffering; ordering is per-partition, so choose keys accordingly.

**Q16. 💡 What does "near-real-time" usually mean in practice?**
Often **micro-batch** (e.g., a 1-minute trigger), not full streaming — the right, lower-complexity choice for minute-level SLAs.

**Q17. 🔥 Design real-time fraud detection (outline).**
Event Hubs (partitioned) → Structured Streaming scoring with checkpointing/watermark (exactly-once) → low-latency store (Cosmos/Redis) + alert for the live path; all events also to Delta Bronze for training (Kappa). Justified by sub-second, no-loss requirements.

---

## Scenario / mixed

**Q18. ⭐ Design a platform serving both real-time ops and daily finance (e.g., ride-hailing).**
Hybrid: streaming path (Event Hubs → Structured Streaming → NoSQL/live Delta) for ops/surge; batch path (same stream → Bronze → nightly Silver/Gold star schema) for finance; serve app from Cosmos DB, analysts from Power BI. Justify by differing per-consumer latency needs; Kappa to reuse one codebase; strong PII governance.

**Q19. ⭐ How would you ingest 10M events/sec?**
Heavily partitioned Event Hubs/Kafka → streaming for threshold alerts → Delta/wide-column (Cassandra) store for append-heavy time-series; partition by `(entity_id, time_bucket)` to avoid hot partitions; batch aggregations for analytics; TTL/archive for cost.

**Q20. 💡 How do you de-risk migrating an on-prem warehouse to Azure?**
Self-hosted IR + ADF to extract; reimplement transforms in Spark/dbt on a lakehouse; run **parallel** with **reconciliation testing** (old vs new outputs) before cutover; repoint Power BI; add governance and cost controls.

**Q21. 💡 What's common to every good data design?**
Requirements-first, split by latency (batch default, streaming/micro-batch where justified), lakehouse + medallion backbone, storage matched to the access pattern, and cross-cutting reliability/quality/cost/governance/monitoring.

---

## Further Learning
- Back to the [Learning Path](00_System_Design_Learning_Path.md)
- Related: [Case Studies](04_Case_Studies.md) · [Streaming](../09_Streaming/00_Streaming_Learning_Path.md) · [Lakehouse](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Cost](../16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md)
