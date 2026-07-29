# ADF — Scenario-Based Questions

## Overview
Scenario questions are where 5+ yr candidates win or lose ADF interviews. The interviewer gives a production situation and expects a structured answer: **diagnose → options → recommended design → trade-offs → cost/security/monitoring**.

---

## Scenarios with model answers

### 🔴 S1. Pipeline runs 8 hours, must finish in 2. ★★★★★
**Diagnose:** Sequential ForEach? Full loads? Under-provisioned DIUs? SHIR bottleneck? Slow warehouse sink?
**Fix:**
- Parallelize ForEach (`isSequential=false`, tune `batchCount`).
- Switch full → **incremental (watermark/CDC)**.
- **Source partitioning** on big tables to split one copy into parallel streams.
- Increase **DIUs** and **parallelCopies** on Copy.
- Warehouse load via **staged COPY/PolyBase**, not row inserts.
- Scale **SHIR** to multiple nodes if it's CPU/network-bound.
- Separate "many small tables" from "few huge tables" into different concurrency lanes.

### 🔴 S2. Load 500 tables from on-prem SQL to ADLS, minimal maintenance. ★★★★★
**Metadata-driven framework:** control table (`SourceTable, LoadType, WatermarkColumn, TargetPath`) → `Lookup` → `ForEach` (parallel) → parameterized `Copy` → update watermark. New table = new row. **Self-Hosted IR** (HA) for on-prem. Secrets in **Key Vault**.

### 🟡 S3. Files land in ADLS randomly; process each on arrival. ★★★★☆
**Storage Event Trigger** (Blob created) → pass `@triggerBody().fileName` → pipeline processes that file. Add dedupe/idempotency so re-fired events don't double-load.

### 🔴 S4. Need to reprocess last 30 days after a logic bug. ★★★★☆
Use **Tumbling Window trigger** with **backfill** (start date in the past) — it replays each daily window with its own parameters. Or a `Until`/`ForEach` over a date array calling the parameterized pipeline per day. Ensure each run **overwrites its partition** (idempotent).

### 🟡 S5. Source schema changes occasionally (new columns). ★★★☆☆
Enable **schema drift** in Mapping Data Flow (`allowSchemaDrift`), or land as-is to Parquet/Delta and evolve schema downstream in Databricks (`mergeSchema`). Don't hard-map columns for volatile sources.

### 🟡 S6. Copy fails midway; rerunning duplicates data. ★★★★☆
Make it **idempotent**: load into a **staging partition** then swap/MERGE on key, or delete-by-watermark-window before insert. Never append blindly.

### 🔴 S7. Secure ADF end-to-end (auditor requirement). ★★★★★
**Managed Identity + RBAC** (no keys), **Key Vault** for any remaining secrets, **Managed VNet + Private Endpoints** (no public traffic), **RBAC on the factory**, **diagnostic logs to Log Analytics**, and **customer-managed keys** if mandated.

### 🟡 S8. Cost spiked last month. Find and fix. ★★★★☆
Check: leftover **Data Flow debug** clusters, oversized DIUs, too many activity runs (chatty pipelines), full instead of incremental loads, always-on Data Flows. Fix with metadata-driven consolidation, right-sized DIU/vCores, and Copy-over-DataFlow for simple moves.

### 🟡 S9. One table's daily load must wait for another pipeline to finish. ★★★☆☆
**Execute Pipeline** activity (parent-child), or **Tumbling Window trigger dependencies**, or a **dependency flag** in the control table checked by a `Until` loop. Prefer trigger dependencies for clean lineage.

### 🔴 S10. Migrate 200 SSIS packages to Azure with a deadline. ★★★☆☆
Short term: **Azure-SSIS IR** lift-and-shift (fastest, keeps logic). Then incrementally **modernize** hot packages to native ADF/Databricks. Sell it as phased de-risking.

---

## Quick Revision — scenario reflexes
- ✔ Slow pipeline → parallelism + incremental + partitioning + staged load
- ✔ Many tables → **metadata-driven** control table
- ✔ File arrival → **Storage Event Trigger**
- ✔ Backfill/replay → **Tumbling Window**
- ✔ Rerun safety → **idempotent** (staging + MERGE / partition overwrite)
- ✔ Security → **MSI + Key Vault + Private Endpoints**
- ✔ Cost → kill debug clusters, right-size DIUs, go incremental

## Related Topics
[ADF Interview Questions](ADF%20Interview%20Questions.md) · [ADF Architecture](ADF%20Architecture.md) · [Scenario Based Questions](../Scenario%20Based%20Questions/)
