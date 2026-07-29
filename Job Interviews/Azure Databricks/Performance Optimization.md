# Databricks / Spark — Performance Optimization

## Overview
The single most important 5+ yr topic. Interviewers give a slow job and expect a **methodical, Spark-UI-driven** tuning approach — not random "add more nodes." Master the levers below and the reasoning for each.

---

## The optimization methodology (say this)
1. **Read the Spark UI first** — find the slow **stage**; look at task duration distribution, shuffle read/write, spill.
2. Classify the bottleneck: **skew**, **shuffle**, **small files / too many partitions**, **spill (memory)**, **under-parallelism**, or **full scan (no pruning)**.
3. Apply the matching lever. Measure again.

---

## Key levers (with WHY)

| Problem | Symptom in Spark UI | Fix |
|---|---|---|
| **Data skew** | One task runs 10× longer | Salting, **AQE skew join**, broadcast small side |
| **Big shuffle** | High shuffle read/write | Broadcast small table, reduce wide ops, filter early |
| **Small files** | Many tiny tasks, slow reads | `OPTIMIZE`, optimized writes/auto-compaction |
| **Spill to disk** | "Spill (memory/disk)" > 0 | More memory, fewer partitions, avoid huge shuffles |
| **Under-parallel** | Few tasks, idle cores | Tune `spark.sql.shuffle.partitions`, repartition |
| **Full scan** | Reads whole table | **Partition pruning** + `ZORDER` + predicate pushdown |
| **Slow SQL** | CPU-bound scans | Enable **Photon** |

---

## Broadcast join (favorite question)
When one table is small (< ~10–100MB), broadcast it to every executor to **avoid the shuffle** of a large join.
```python
from pyspark.sql.functions import broadcast
result = big_fact.join(broadcast(small_dim), "dim_id")
# or: spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 50*1024*1024)
```
**Why:** shuffle join redistributes both sides by key (expensive); broadcast ships the small side once and joins locally.

## Cache vs Persist (favorite comparison)
- `cache()` = `persist(MEMORY_AND_DISK)` (default storage level).
- `persist(level)` = choose the storage level (MEMORY_ONLY, DISK_ONLY, etc.).
- Use when a DataFrame is **reused multiple times**; don't cache one-shot data (wastes memory).
**Trap:** Caching is lazy — materialized on the next action.

## AQE (Adaptive Query Execution)
Runtime re-optimization (on by default in modern DBR): **coalesces** shuffle partitions, **handles skew joins**, **switches** join strategy based on actual stats. Mention it whenever asked about shuffle/skew tuning.

## Partitioning vs ZORDER
- **Partitioning** (physical folders) — on a **low-cardinality** column (date). Enables partition pruning.
- **ZORDER** — multi-dimensional clustering for **high-cardinality** filter columns; improves data skipping within files.
**Trap:** Partitioning on high-cardinality (e.g., user_id) → millions of tiny folders = disaster.

---

## Scenario Questions
**S1. "Job was 30 min, now 3 hrs after 5× data growth."** Spark UI → likely **skew** or **small files** or lost **pruning**. Fix skew (AQE/salt/broadcast), `OPTIMIZE`+`ZORDER`, verify partition filter still applies, scale shuffle partitions.
**S2. "One join key has 80% of rows."** Classic skew → salt the key, or rely on **AQE skew join**, or broadcast if the other side is small.
**S3. "Driver OOM."** Someone called `collect()`/`toPandas()` on big data, or too many broadcast tables. Avoid collecting; write to Delta instead.
**S4. "Too many small output files downstream."** Enable **optimized writes/auto-compaction**, or `repartition` before write, or scheduled `OPTIMIZE`.

---

## Quick Revision
- ✔ **Spark UI first** — diagnose before tuning
- ✔ **Broadcast** small table → kills shuffle
- ✔ **Skew** → salt / AQE skew join / broadcast
- ✔ **cache/persist** only for reused DataFrames (cache = MEMORY_AND_DISK)
- ✔ **AQE** = runtime coalesce + skew + join switch
- ✔ **Partition (low-card) + ZORDER (high-card)** ; `OPTIMIZE` small files
- ✔ **Photon** for SQL/scan-heavy jobs
- ✔ Never `collect()` big data

## Common Interview Mistakes
- "Add more nodes" as the universal fix (won't fix skew/small files).
- Over-partitioning on high-cardinality columns.
- Caching everything.
- Ignoring the Spark UI.

## Senior-Level Discussion
Seniors give a **decision tree** keyed to Spark UI symptoms, quantify (shuffle GB, task skew ratio, spill), and weigh **cost vs speed** (Photon/bigger cluster finishes faster but costs DBUs — net cheaper if runtime drops enough). They mention **file sizing (~128MB–1GB target)**, **broadcast thresholds**, and **AQE** knobs.

## Related Topics
[Spark Architecture](Spark%20Architecture.md) · [PySpark](../PySpark/) · [Partitioning](../PySpark/Partitioning.md) · [Delta Lake](Delta%20Lake.md)
