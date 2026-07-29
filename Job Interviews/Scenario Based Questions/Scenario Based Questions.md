# Scenario-Based Questions — Azure Data Engineer (5+ yr)

## Overview
This is where senior candidates are separated from juniors. The interviewer describes a production situation; they expect a **structured** answer: **diagnose → options → recommended design → trade-offs → cost/security/monitoring**. Below are the most common scenarios with model answers.

> **The framework for every scenario:** (1) clarify requirements/SLA, (2) diagnose the bottleneck/constraint, (3) give the recommended design, (4) mention trade-offs, (5) cover cost + security + monitoring + failure handling.

---

## Performance & Optimization

### 🔴 1. "A pipeline that took 1 hour now takes 8 hours. Optimize it." ★★★★★
- **Diagnose first** (don't guess): is it ADF orchestration or Databricks compute? Sequential ForEach? Full loads? Spark UI shows skew/shuffle/small files?
- **ADF side:** parallelize ForEach, incremental (watermark), source partitioning, more DIUs, staged COPY to warehouse, scale SHIR.
- **Databricks side:** fix **skew** (salt/AQE/broadcast), `OPTIMIZE`+`ZORDER`, right shuffle partitions, broadcast small dims, Photon, avoid small files and `collect()`.
- **Structural:** switch full → **incremental**; separate small vs huge tables.

### 🔴 2. "Databricks job randomly OOMs." ★★★★☆
`collect()`/`toPandas()` on big data, driver too small, huge broadcast, or skew causing a fat partition. Fix: write to Delta instead of collecting, remove over-broadcast, handle skew, right-size the driver.

### 🔴 3. "Query on a 2 TB table times out." ★★★★☆
Partition prune (date) + `ZORDER` on filter columns; Synapse: align **distribution keys** (HASH/REPLICATE) to avoid data movement; pre-aggregate into Gold; check statistics; SARGable predicates.

---

## Design & Architecture

### 🔴 4. "Design an end-to-end Azure data platform for batch + streaming." ★★★★★
```
Batch:  Sources -> ADF (ingest, SHIR for on-prem) -> ADLS Bronze (Delta)
        -> Databricks (Silver/Gold) -> Synapse/SQL -> Power BI
Stream: Event Hub/Kafka -> Databricks Structured Streaming (checkpoint) -> Bronze/Silver Delta
Cross:  Key Vault (secrets) + Managed Identity + Unity Catalog (governance/lineage)
        + Azure Monitor/Log Analytics (observability) + DevOps CI/CD (ARM + Asset Bundles)
```
Justify each choice; mention medallion, incremental/idempotent loads, cost (job clusters/pause pools), security (MSI/private endpoints), and monitoring/alerting.

### 🔴 5. "Ingest 500 tables from on-prem SQL with minimal maintenance." ★★★★★
**Metadata-driven framework:** control table (source, load type, watermark, target) → ADF Lookup + parallel ForEach + parameterized Copy → Databricks transforms. **Self-Hosted IR** (HA) for on-prem, Key Vault secrets, incremental watermark. New table = one config row.

### 🟡 6. "Files land in ADLS at random times; process on arrival." ★★★★☆
**Storage Event Trigger** (ADF) or **Auto Loader** (Databricks) — incremental, checkpointed, idempotent. Avoid re-listing the whole folder.

---

## Reliability & Data Quality

### 🔴 7. "A rerun duplicates data. Make it safe." ★★★★★
Make loads **idempotent**: load to a staging partition then **MERGE** on the business key, or overwrite the target **partition** for the run window (delete-by-window + insert). Never blind-append.

### 🔴 8. "Bad data reached Gold and broke a report." ★★★★☆
Add **data-quality gates** (DLT expectations / Great Expectations) at Silver; quarantine bad rows; **RESTORE** the Gold Delta table to a prior version (time travel); backfill after fix.

### 🟡 9. "Source schema changed and broke the pipeline." ★★★★☆
Land raw with **schema evolution** (Auto Loader `_rescued_data` / Delta `mergeSchema`); don't hard-map volatile sources; alert on new/changed columns.

### 🔴 10. "Late-arriving/out-of-order events." ★★★★☆
Streaming: **watermarking** + event-time windows; batch: reprocess by **partition window**; idempotent upserts so replays don't duplicate.

---

## Cost & Security

### 🔴 11. "Azure spend doubled. Cut it without hurting SLAs." ★★★★★
Databricks: **job clusters** + auto-terminate + autoscale + **spot** + Photon (finish faster) + pools; kill idle all-purpose clusters. ADF: kill Data Flow debug clusters, right-size DIUs, go incremental. Synapse: **pause** idle dedicated pools, serverless for ad-hoc. Storage: lifecycle tiering + compaction.

### 🔴 12. "Secure the platform for an audit." ★★★★★
**Managed Identity + RBAC** (no keys), **Key Vault** for secrets, **private endpoints + firewall** (no public traffic), **Unity Catalog** (fine-grained access + lineage + audit), **Purview** (classification/PII), diagnostic logs to **Log Analytics**, CMK if required.

---

## Migration

### 🔴 13. "Migrate an on-prem Hadoop/warehouse to Azure." ★★★★☆
Phased: assess → land raw in ADLS (Data Box/AzCopy for bulk) → rebuild transforms in Databricks (Delta medallion) → serve via Synapse/Power BI → validate row counts/reconciliation → cut over. Run parallel during validation. Mention SSIS → Azure-SSIS IR then modernize.

### 🟡 14. "Migrate 200 SSIS packages under a deadline." ★★★☆☆
Lift-and-shift to **Azure-SSIS IR** first (fast, low risk), then incrementally modernize hot packages to native ADF/Databricks.

---

## Monitoring & Troubleshooting

### 🟡 15. "A nightly pipeline fails ~10% of runs. Debug it." ★★★★☆
Check ADF Monitor / Spark UI for the failing activity/stage; look for **throttling (429)**, source maintenance windows, transient network; add **retries + alerts**; persist error details to a log table for pattern analysis; make it idempotent so retries are safe.

### 🟡 16. "How do you monitor the whole platform?" ★★★★☆
Diagnostic settings from ADF/Databricks/Synapse → **Log Analytics**; **Azure Monitor alerts** on failures/duration/cost; job-level alerts; data-quality metrics; SLA dashboards.

---

## Quick Revision — scenario reflexes
- ✔ Slow → **diagnose (UI) first**, then parallelism/incremental/skew/partition/broadcast
- ✔ Many tables → **metadata-driven** framework
- ✔ File arrival → **Event Trigger / Auto Loader**
- ✔ Rerun safety → **idempotent (MERGE / partition overwrite)**
- ✔ Bad data → **quality gates + quarantine + Delta RESTORE**
- ✔ Late data → **watermark / partition reprocess**
- ✔ Cost → **job clusters, pause pools, spot, lifecycle, incremental**
- ✔ Security → **MSI + Key Vault + private endpoints + Unity Catalog + Purview**
- ✔ Migration → **phased, land raw, rebuild, reconcile, cut over**

## Common Interview Mistakes
- Jumping to a fix without diagnosing.
- Ignoring cost/security/monitoring in a design answer.
- Full loads / non-idempotent pipelines.
- No mention of failure handling or observability.

## Senior-Level Discussion
The 5+ yr signal is **structure + trade-offs + non-functionals**. Always: clarify SLA, diagnose with evidence (Spark UI/Monitor), recommend a concrete design, state trade-offs, and cover cost, security, monitoring, and failure/replay. Reference real patterns (metadata-driven, medallion, MERGE idempotency) — that's what lands senior roles.

## Related Topics
Azure Data Factory, Azure Databricks, PySpark, Delta Lake, ADLS Gen2, CI-CD
