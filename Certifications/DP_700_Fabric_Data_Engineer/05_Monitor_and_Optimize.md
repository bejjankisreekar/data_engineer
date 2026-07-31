# 05 — Monitor & Optimize

*Domain: Monitor and optimize an analytics solution (30–35%)*

---

## What it is

The full third of the exam devoted to **operations**: watching runs, catching and fixing errors, and making pipelines/tables/queries faster and cheaper. Foundations: [Performance & Best Practices](../../06_Programming/PySpark/14_Performance_and_Best_Practices.md), [Delta Lake maintenance](../../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md), [Data Quality](../../05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md).

---

## Monitoring tools

| Tool | What it shows |
|---|---|
| **Monitoring hub** | Central view of all item runs (pipelines, notebooks, dataflows, Spark) — status, duration, history |
| **Fabric Capacity Metrics app** | Capacity Unit consumption, throttling, top-consuming items |
| **Run/refresh history** | Per-item history of successes/failures |
| **Spark UI / application details** | Spark job stages, tasks, spills, skew for a notebook run |
| **Data Activator (Activator)** | Trigger alerts/actions on conditions in data/eventstreams |

> **Exam Tip:** To see **all runs across the workspace** in one place → **Monitoring hub**. To diagnose **capacity throttling / who's consuming CUs** → **Capacity Metrics app**. To trigger an **alert when a metric crosses a threshold** → **Data Activator**.

---

## Diagnosing errors

- **Pipeline failures** — inspect the failed activity's error + input/output; use retries, timeouts, and failure paths.
- **Notebook/Spark errors** — read the stack trace and Spark UI (OOM → memory/skew; `AnalysisException` → schema/column issue).
- **Dataflow Gen2** — refresh history shows step-level errors.
- **Eventstream** — check source connectivity, schema mismatches, and destination errors.
- **T-SQL** — query errors, permission issues, or capacity throttling.

> **Exam Tip:** A pipeline should be **resilient**: configure **retry**, **timeout**, and **on-failure** activities rather than letting one transient error kill the whole run. Idempotent steps make retries safe.

---

## Optimizing the Lakehouse (Spark / Delta)

The Delta maintenance you learned applies ([Delta Lake](../../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md), [Delta Table](../../04_Storage_and_Formats/Lakehouse/02_Delta_Table.md)):

- **`OPTIMIZE`** — compact many small files into fewer large ones (fixes the small-file problem from streaming/frequent writes).
- **V-Order** — Fabric's write-time optimization that sorts/encodes Parquet for fast reads (especially **Direct Lake** and Power BI); often on by default.
- **`VACUUM`** — remove old tombstoned files (mind the retention window / time-travel trade-off).
- **Partitioning / liquid clustering** — reduce data scanned; don't over-partition.
- **Spark tuning** — right-size the pool, avoid skew and unnecessary shuffles, broadcast small joins ([Performance](../../06_Programming/PySpark/14_Performance_and_Best_Practices.md)).

> **Exam Tip:** Slow queries on a table with **millions of tiny files** → run **`OPTIMIZE`** (compaction). For fast Direct Lake / Power BI reads → ensure **V-Order** is applied. `VACUUM` reclaims storage but can break time travel if retention is too short.

---

## Optimizing the Warehouse (T-SQL)

- **Statistics** — the query optimizer needs current column statistics for good plans; stale stats = bad plans.
- **V-Order** — applies to Warehouse Delta output too, aiding read performance.
- **Result-set size & query design** — filter early, avoid `SELECT *`, model appropriately.
- **Cold vs warm cache** — first runs can be slower before caching.

> **Exam Tip:** Warehouse queries suddenly slow after a big load → **update statistics**. It's the T-SQL analog of the Lakehouse's file-compaction lever.

---

## Optimizing streaming (Eventstream / Eventhouse)

- Ensure adequate **throughput/partitioning** upstream (Event Hubs/Eventstream) so processing parallelizes.
- Tune **windowing** and **watermarks** for the latency-vs-completeness trade-off ([Streaming Fundamentals](../../09_Streaming/01_Streaming_Fundamentals.md)).
- Watch **Eventhouse** ingestion and caching policies for KQL query speed.

---

## Optimizing capacity & cost

- Use the **Capacity Metrics app** to find heavy items and **smoothing/bursting/throttling** patterns.
- **Right-size the F SKU**; **pause** capacity when unused; schedule heavy jobs off-peak.
- Reduce compute: incremental (not full) loads, compacted files, efficient queries, appropriate Spark pool sizes.

> **Exam Tip:** "Workloads are being throttled" → the **capacity is overloaded**: scale up the F SKU, spread/stagger heavy jobs, and use the Capacity Metrics app to identify the top consumer. Full loads and tiny-file tables are common hidden CU hogs.

---

## Quick Review

- Monitor with the **Monitoring hub** (all runs), **Capacity Metrics app** (CU/throttling), **Spark UI** (job internals), **Data Activator** (alerts).
- Make pipelines resilient: **retries, timeouts, on-failure paths**, idempotent steps.
- Lakehouse optimize: **`OPTIMIZE`** (compact small files), **V-Order** (fast Direct Lake/BI reads), **`VACUUM`** (reclaim, mind retention), partition/cluster sensibly, tune Spark.
- Warehouse optimize: **update statistics**, V-Order, filter early.
- Streaming optimize: partitioning/throughput, windowing/watermarks, Eventhouse policies.
- Throttling → **capacity** overloaded: scale F SKU, stagger jobs, find the top consumer.

---

## Further Learning — Docs & Videos

- Monitoring hub: https://learn.microsoft.com/en-us/fabric/admin/monitoring-hub
- V-Order / Delta optimization in Fabric: https://learn.microsoft.com/en-us/fabric/data-engineering/delta-optimization-and-v-order
- Capacity Metrics app: https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app
- Video search: https://www.youtube.com/results?search_query=dp-700+fabric+monitor+optimize+capacity

---

Next: **[06 — Practice Questions by Domain](06_Practice_Questions_by_Domain.md)**.
