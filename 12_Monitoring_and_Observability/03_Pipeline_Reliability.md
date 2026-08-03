# Pipeline Reliability

## What is pipeline reliability?

Reliability is designing pipelines that **keep producing correct data despite failures** — transient network blips, late sources, bad records, reruns — without waking a human every time. Monitoring tells you something broke; reliability engineering means it *mostly doesn't*, and when it does, it recovers cleanly.

Analogy: a reliable pipeline is a **commercial airliner**, not a paper plane. Planes fail all the time — an engine, a sensor — yet keep flying because of **redundancy, checklists, and graceful degradation**. You build the same into pipelines: retries, idempotency, quarantine, and safe reruns, so one failure isn't a crash.

---

## The reliability toolkit

| Technique | Protects against | How |
|---|---|---|
| **Retries with backoff** | Transient errors (network, throttling) | Auto-retry N times with increasing delay |
| **Idempotency** | Double-processing on rerun/retry | MERGE/upsert, partition overwrite — see below |
| **Timeouts** | Hung tasks blocking the DAG | Kill and fail a task that runs too long |
| **Dead-letter / quarantine** | One poison record killing the batch | Route bad rows aside, keep going, alert on volume |
| **Checkpointing** | Loss/duplication in streaming | Track processed offsets ([Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)) |
| **Circuit breaking** | Hammering a failing dependency | Stop calling a source that's clearly down |
| **Backfill capability** | Missed/corrupted historical windows | Re-run a date range safely (needs idempotency) |

---

## Idempotency — the foundation of safe reruns

If retries and backfills can run a task twice, the task **must** be idempotent — twice = once.

```python
# ❌ not idempotent: a rerun duplicates the day's rows
df.write.format("delta").mode("append").save(path)

# ✅ idempotent: rerunning batch_date replaces exactly that partition
(df.write.format("delta").mode("overwrite")
   .option("replaceWhere", f"batch_date = '{batch_date}'")
   .save(path))

# ✅ idempotent: upsert on the business key
target.merge(source, "t.id = s.id").whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

This is the single most important reliability property — and a recurring interview theme from [Orchestration](../11_Orchestration/01_Orchestration_Fundamentals.md) and [Project 1](../18_Projects/02_Project_1_Batch_Medallion_Pipeline.md).

---

## Handling bad data without stopping the world

A single malformed record shouldn't fail a 10-million-row batch. The **quarantine pattern**:

```python
good = df.filter(is_valid_condition)
bad  = df.filter(~is_valid_condition)

bad.write.format("delta").mode("append").save(quarantine_path)   # keep for inspection
good.write.format("delta").mode("append").save(silver_path)       # pipeline continues
# then: alert if bad-row COUNT or RATIO exceeds a threshold
```

You lose nothing (bad rows are stored, not dropped), the pipeline stays up, and you're alerted only when badness is *significant*. Straight from [Data Quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md).

---

## Designing for recovery, not just prevention

Failures are inevitable, so optimize **recovery**:

- **Rerun from the point of failure** — orchestrators support repair/rerun-from-failed-task ([Workflows](../11_Orchestration/03_Databricks_Workflows.md)); design tasks so a partial run + rerun = a correct full run.
- **Small, restartable units** — many small idempotent tasks recover better than one giant monolith.
- **Separate ingest from transform** — raw Bronze is your safety net: if Silver/Gold logic is wrong, reprocess from Bronze without re-hitting the source.
- **Deterministic partitions per run** (by date/window) so a rerun cleanly replaces its own output.

---

## Freshness & completeness SLAs

Two data-specific reliability targets to track and alert on:

- **Freshness** — "the sales table has today's data by 6 AM." Alert if the latest partition/timestamp is older than the SLA.
- **Completeness** — "all N expected source files/partitions arrived." Alert on a missing expected input, even if the job "succeeded" on what did arrive.

These catch the **silent** failures (green job, stale or partial data) that pure operational monitoring misses.

---

## Interview-grade Q&A

- *How do you make a pipeline safe to rerun?* Idempotency — MERGE/upsert or partition overwrite keyed to the run — so retries/backfills don't duplicate data.
- *A single bad record appears in a huge batch — what happens?* Quarantine it (route aside, keep processing), store it for inspection, and alert only if the bad-row ratio crosses a threshold — never fail the whole batch on one row.
- *How do you handle transient failures?* Retries with exponential backoff and timeouts; escalate to an alert only after retries are exhausted.
- *Why keep a raw Bronze layer for reliability?* It's the safety net — reprocess Silver/Gold from Bronze after a logic fix without re-reading the source.
- *How do you detect a "successful but stale" pipeline?* Freshness and completeness checks with alerts, independent of job success status.
- *Prevention vs recovery — which matters?* Both, but since failure is inevitable, design for fast, safe recovery (rerun-from-failure, small idempotent units).

---

## Further Learning — Docs & Videos
- Reliable data pipelines (dbt/industry patterns): https://www.getdbt.com/blog/data-reliability-engineering
- Delta MERGE & replaceWhere: https://docs.databricks.com/en/delta/selective-overwrite.html
- Video — building reliable data pipelines: https://www.youtube.com/results?search_query=building+reliable+data+pipelines+idempotency
