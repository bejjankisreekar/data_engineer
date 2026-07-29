# Snowflake — Interview Questions

## Overview
Snowflake is a cloud data warehouse with **separated storage and compute** (virtual warehouses). Often compared with Synapse/Databricks. Interviews test its architecture, virtual warehouses, micro-partitions, and time travel.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | Snowflake architecture (3 layers)? | 🔴 | ★★★★★ |
| 2 | Virtual warehouses — what/scaling? | 🟡 | ★★★★★ |
| 3 | Separation of storage & compute — why it matters? | 🟡 | ★★★★★ |
| 4 | Micro-partitions & clustering? | 🔴 | ★★★★☆ |
| 5 | Time travel & fail-safe? | 🟡 | ★★★★☆ |
| 6 | Zero-copy cloning? | 🟡 | ★★★☆☆ |
| 7 | Snowflake vs Synapse vs Databricks? | 🔴 | ★★★★☆ |
| 8 | How is it billed? Cost control? | 🟡 | ★★★★☆ |
| 9 | Snowpipe (ingestion)? | 🟡 | ★★★☆☆ |

## Key Answers
- **Q1:** Three layers: **Storage** (columnar, compressed, cloud object store), **Compute** (independent virtual warehouses), **Cloud Services** (metadata, optimizer, security). Layers scale independently.
- **Q2/Q3:** A **virtual warehouse** is an independent compute cluster; multiple can hit the same data with no contention, scale up (bigger) or out (multi-cluster for concurrency), and auto-suspend/resume — you pay only when running.
- **Q4:** Data stored in **micro-partitions** (auto, ~50–500MB) with metadata enabling pruning; **clustering keys** improve pruning on large tables.
- **Q6:** **Zero-copy clone** creates instant table/db copies sharing storage (metadata pointers) — great for dev/test without duplicating data.

## Scenario Questions
- **"BI and ETL contend for compute."** Separate **virtual warehouses** per workload — no contention.
- **"Recover a dropped table."** **Time travel** (up to retention) then `UNDROP`; fail-safe beyond that.
- **"Cost is high."** Auto-suspend idle warehouses, right-size, separate workloads, avoid always-on.
- **"Continuous file ingestion."** **Snowpipe** (auto-ingest).

## Quick Revision
- ✔ 3 layers: **storage / compute / cloud services** (independent scaling)
- ✔ **Virtual warehouses** = isolated compute; auto-suspend/resume
- ✔ **Micro-partitions** + clustering for pruning
- ✔ **Time travel** + fail-safe; **zero-copy clone**
- ✔ Pay per compute time → suspend idle warehouses
- ✔ Snowpipe = continuous ingestion

## Common Mistakes
- Thinking storage and compute scale together (they're separate).
- Leaving warehouses running (cost).
- Confusing time travel vs fail-safe.

## Senior-Level
Seniors leverage separated compute (per-workload warehouses), auto-suspend for cost, micro-partition pruning + clustering for performance, zero-copy clones for dev, and compare Snowflake vs Databricks (lakehouse/ML/open) vs Synapse (Azure-native) by workload and ecosystem.

## Related Topics
Azure Synapse, Data Warehousing, SQL, Lakehouse
