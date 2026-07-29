# Azure Functions — Interview Questions

## Overview
Azure Functions is serverless, event-driven compute — small code that runs on triggers (HTTP, timer, blob, Event Hub) and scales to zero. In DE it's used for lightweight ingestion, event reactions, custom API calls, and glue that doesn't warrant Spark.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What are Azure Functions? Serverless meaning? | 🟢 | ★★★★★ |
| 2 | Triggers & bindings? | 🟡 | ★★★★★ |
| 3 | Hosting plans (Consumption/Premium/Dedicated)? | 🔴 | ★★★★☆ |
| 4 | Cold start — what/mitigation? | 🔴 | ★★★★☆ |
| 5 | Where do Functions fit vs ADF/Databricks? | 🟡 | ★★★★☆ |
| 6 | Durable Functions? | 🔴 | ★★★☆☆ |
| 7 | How do you secure a Function (MSI/Key Vault)? | 🟡 | ★★★★☆ |
| 8 | Stateless design & scaling? | 🟡 | ★★★☆☆ |

## Key Answers
- **Q1:** Event-triggered code, no server management, **pay per execution**, auto-scales (to zero). Great for small, spiky, event-driven tasks.
- **Q2:** **Triggers** start a function (HTTP/timer/blob/Event Hub/queue); **bindings** declaratively connect inputs/outputs (e.g., read blob, write to Cosmos) without boilerplate.
- **Q4:** **Cold start** = latency when scaling from zero; mitigate with **Premium plan** (pre-warmed instances) or keep-warm.
- **Q5:** Functions for **lightweight/event glue** (call an API, react to a file, small transforms). For heavy data → Databricks; for orchestration → ADF.

## Scenario Questions
- **"Call a REST API hourly and land JSON."** Timer-triggered Function → write to ADLS (or ADF Copy for larger). 
- **"React the instant a file lands."** Blob-trigger Function (or ADF Storage Event Trigger).
- **"Low-latency API with no cold starts."** Premium plan (pre-warmed).

## Quick Revision
- ✔ Serverless, event-driven, pay-per-execution, scales to zero
- ✔ **Triggers** start; **bindings** wire I/O
- ✔ Plans: Consumption (cheap, cold starts) · **Premium** (warm) · Dedicated
- ✔ **Cold start** mitigated by Premium/keep-warm
- ✔ Functions = light glue; Databricks = heavy compute; ADF = orchestration
- ✔ Secure with **Managed Identity + Key Vault**

## Common Mistakes
- Using Functions for heavy data processing (use Spark).
- Ignoring cold starts for latency-sensitive APIs.
- Storing secrets in app settings plaintext (use Key Vault).

## Senior-Level
Seniors use Functions for event-driven glue, pick plans by latency/cost, mitigate cold starts, use Durable Functions for stateful orchestrations, and secure with MSI/Key Vault — reserving Spark/ADF for heavy or orchestrated work.

## Related Topics
Event Hub, Azure Data Factory, Python, ADLS Gen2
