# 02 — Integration Patterns

## Why patterns?

Data integration problems repeat, so the industry has named **patterns** — proven designs for moving and combining data. Knowing them lets you name a solution instantly in an interview ("that's a metadata-driven incremental load with a watermark") instead of describing it from scratch.

---

## Ingestion patterns

### 1. Full load
Reload the entire source each run. Simple and self-correcting, but slow/expensive and hard on the source at scale. Fine for small/reference tables.

### 2. Incremental load (watermark)
Load only rows changed since last run using a **high-water-mark** (e.g., `max(modified_date)`) stored in a control table.
```
read old watermark → extract WHERE modified > watermark → load → store new watermark
```
The standard for large sources. Must be **idempotent** (MERGE / partition overwrite) so a retry doesn't duplicate.

### 3. Change Data Capture (CDC)
Capture inserts/updates/**deletes** from the source's change log/stream (covered fully in [03_Change_Data_Capture](03_Change_Data_Capture.md)). Lowest-latency incremental option; handles deletes (watermark alone can't).

### 4. Snapshot + diff
Compare today's full snapshot to yesterday's to derive changes when the source has no reliable modified column or CDC.

---

## Movement & structure patterns

### Metadata-driven (config-driven) framework — the senior favorite
One **generic** pipeline driven by a **control table** (`source, target, load_type, watermark_column, ...`). A lookup reads the config, a loop iterates, and a parameterized activity runs per row. Onboarding a new table = **one config row**, not a new pipeline. Scales to hundreds of tables with one codebase.

### Medallion (multi-hop)
Bronze (raw) → Silver (clean/conform/join) → Gold (curated). Each hop is an integration step; raw retention enables reprocessing.

### Fan-in / fan-out
**Fan-in** = many sources → one target (consolidation). **Fan-out** = one source → many targets (distribution). Watch fan-out for duplicate/consistency issues.

### Landing → staging → curated
Land raw immutably, stage for transformation/validation, publish curated. Keeps raw for audit/replay and isolates messy transforms.

---

## Reliability patterns

| Pattern | Purpose |
|---|---|
| **Idempotency** (MERGE / partition overwrite) | Safe re-runs, no duplicates |
| **Watermark / checkpoint** | Resume from where you stopped |
| **Retry with backoff** | Survive transient source/network failures |
| **Dead-letter / quarantine** | Route bad records aside instead of failing the whole load |
| **Circuit breaker / throttling** | Don't overwhelm a fragile source |
| **Replayability** | Reprocess a date/partition window after a bug |

---

## Consistency & delivery semantics
- **At-least-once** (default for many streams) → possible duplicates → make the sink **idempotent**.
- **Exactly-once** → checkpoint + idempotent sink (e.g., Structured Streaming + Delta MERGE).
- **Ordering** — guaranteed only **within a partition/key** in Event Hub/Kafka; use a partition key for related events.

---

## Choosing a pattern
| Situation | Pattern |
|---|---|
| Small reference table | Full load |
| Large table with a modified column | Incremental (watermark) |
| Need updates + deletes, low latency | CDC + MERGE |
| Hundreds of tables | Metadata-driven framework |
| Real-time events | Streaming + checkpoint |
| No reliable change column | Snapshot + diff |

---

## Pro / Interview notes
- Lead with **metadata-driven + incremental + idempotent** — it signals production experience.
- Always pair a movement pattern with a **reliability** pattern (retries, quarantine, replay).
- **Common mistakes:** full loads at scale, non-idempotent appends, watermark on a non-source column (`getdate()`), ignoring deletes (use CDC).

---

## Quick Review
- ✔ Ingestion: **full · incremental (watermark) · CDC · snapshot+diff**
- ✔ **Metadata-driven** framework = one pipeline + control table (senior signal)
- ✔ Medallion, landing→staging→curated, fan-in/out
- ✔ Reliability: **idempotency, watermark/checkpoint, retry, dead-letter, replay**
- ✔ Delivery: at-least-once (+ idempotent sink) vs exactly-once; ordering per partition

## Further Learning — Docs & Videos
- Enterprise integration patterns: https://www.enterpriseintegrationpatterns.com/
- Incremental copy (ADF): https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-overview
- Video — incremental & metadata-driven pipelines: https://www.youtube.com/results?search_query=metadata+driven+incremental+pipeline+adf

Next: **[03 — Change Data Capture (CDC)](03_Change_Data_Capture.md)**.
