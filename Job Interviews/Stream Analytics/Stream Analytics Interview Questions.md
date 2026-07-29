# Azure Stream Analytics — Interview Questions

## Overview
Azure Stream Analytics (ASA) is a managed real-time stream-processing service using a SQL-like language over streaming inputs (Event Hubs/IoT Hub) with windowing, writing to sinks (ADLS, SQL, Power BI). Interviews test windowing functions, event/processing time, and when to use ASA vs Databricks streaming.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Stream Analytics? Inputs/outputs? | 🟢 | ★★★★★ |
| 2 | Windowing types (Tumbling/Hopping/Sliding/Session)? | 🔴 | ★★★★★ |
| 3 | Event time vs processing time? | 🔴 | ★★★★☆ |
| 4 | Watermarks / late arrival handling? | 🔴 | ★★★★☆ |
| 5 | ASA vs Databricks Structured Streaming? | 🟡 | ★★★★☆ |
| 6 | Streaming Units (scaling)? | 🟡 | ★★★☆☆ |
| 7 | Exactly-once / checkpointing? | 🟡 | ★★★☆☆ |
| 8 | Reference data joins? | 🟡 | ★★★☆☆ |

## Key Answers
- **Q2 (key):** **Tumbling** = fixed, non-overlapping windows (each event in one). **Hopping** = fixed size, overlapping by a hop (event in several). **Sliding** = window moves with events, emits on change. **Session** = groups bursts separated by a gap. Know the difference — the top ASA question.
- **Q3:** **Event time** = when the event happened (in the payload); **processing time** = when ASA saw it. Use event time for correctness with out-of-order data.
- **Q5:** ASA = quick, SQL-based, low-ops for standard real-time aggregations/alerts. **Databricks streaming** = code-heavy, complex transforms, ML, lakehouse integration. Choose by complexity.

## Scenario Questions
- **"Average temperature per device every 5 minutes."** Tumbling window (5 min) GROUP BY device.
- **"Alert on 3 failed logins within 1 minute."** Sliding/hopping window count with a threshold.
- **"Enrich stream with device metadata."** **Reference data** join (static blob/SQL lookup).
- **"Complex ML transform on the stream."** Prefer **Databricks** over ASA.

## Quick Revision
- ✔ ASA = managed SQL-like real-time processing
- ✔ Windows: **Tumbling** (non-overlap) · **Hopping** (overlap) · **Sliding** (on change) · **Session** (gap-based)
- ✔ **Event time** for correctness; watermarks handle late data
- ✔ Scale via **Streaming Units**
- ✔ ASA (simple/SQL) vs Databricks (complex/code)

## Common Mistakes
- Confusing tumbling vs hopping vs sliding.
- Using processing time when event time matters.
- Forcing complex logic into ASA (use Databricks).

## Senior-Level
Seniors pick windowing + event-time semantics for correctness, tune Streaming Units, handle late data with watermarks, and choose ASA vs Databricks by transform complexity and lakehouse needs.

## Related Topics
Event Hub, Kafka, Azure Databricks, Power BI
