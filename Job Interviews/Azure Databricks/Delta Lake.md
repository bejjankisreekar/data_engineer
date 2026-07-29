# Delta Lake (Databricks)

## Overview
Delta Lake is the open storage layer that adds **ACID transactions, time travel, schema enforcement, and performance optimizations** on top of Parquet. It's the default table format on Databricks and the foundation of the lakehouse. See also the dedicated [Delta Lake](../Delta%20Lake/) folder for the full deep-dive.

---

## Top questions (quick answers)

**Q. What makes a Delta table?** Parquet data files + a `_delta_log` transaction log (JSON commits + Parquet checkpoints). The log is the source of truth → enables ACID, time travel, concurrency.

**Q. Key features?** ACID, time travel, schema enforcement/evolution, `MERGE` (upsert/CDC), `OPTIMIZE`+`ZORDER`, `VACUUM`, streaming source/sink, unified batch+streaming.

**Q. How does time travel work?** The log keeps versions. `VERSION AS OF` / `TIMESTAMP AS OF`; `DESCRIBE HISTORY`; `RESTORE`. Broken after `VACUUM` removes old files.

**Q. MERGE use case?** Upserts / SCD / CDC in one atomic op:
```sql
MERGE INTO target t USING updates u ON t.id=u.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Q. OPTIMIZE vs ZORDER vs VACUUM?**
- `OPTIMIZE` = compact small files (fixes small-file problem).
- `ZORDER BY (col)` = co-locate data for faster filters (data skipping).
- `VACUUM` = delete unreferenced files older than retention (default 7 days) → reclaims storage, limits time travel.

**Q. Schema enforcement vs evolution?** Enforcement rejects mismatched writes by default; evolution (`mergeSchema`/`overwriteSchema`) opts in to add/change columns.

**Q. How does Delta give ACID on a lake?** Optimistic concurrency via the transaction log — atomic commits, snapshot isolation for readers.

---

## Scenario Questions
**S1. "Slow Delta queries filtering on customer_id."** → `OPTIMIZE t ZORDER BY (customer_id)` + ensure partitioning by a low-cardinality column (e.g., date), enable data skipping.
**S2. "Small-file problem from streaming writes."** → `OPTIMIZE` (or auto-optimize/optimized writes), tune trigger, compact.
**S3. "Need SCD Type 2 dimension."** → `MERGE` with `WHEN MATCHED ... UPDATE` (close old row) + `WHEN NOT MATCHED ... INSERT` (new version).
**S4. "Accidental bad overwrite last night."** → `RESTORE TABLE t TO VERSION AS OF n` (time travel), if within VACUUM retention.

---

## Code Examples
```sql
-- History & time travel
DESCRIBE HISTORY sales.orders;
SELECT * FROM sales.orders VERSION AS OF 12;
RESTORE TABLE sales.orders TO VERSION AS OF 12;

-- Convert existing Parquet to Delta
CONVERT TO DELTA parquet.`/mnt/data/orders`;
```
```python
# Schema evolution on append
(df.write.format("delta").mode("append")
   .option("mergeSchema","true").saveAsTable("sales.orders"))
```

---

## Quick Revision
- ✔ Delta = Parquet + `_delta_log` → ACID, time travel, schema, concurrency
- ✔ `MERGE` = atomic upsert/CDC/SCD
- ✔ `OPTIMIZE`(compact) · `ZORDER`(skipping) · `VACUUM`(cleanup, 7-day default)
- ✔ Time travel: `VERSION/TIMESTAMP AS OF`, `RESTORE`, `DESCRIBE HISTORY`
- ✔ Schema **enforced** by default; evolve with `mergeSchema`

## Common Interview Mistakes
- Forgetting `VACUUM` breaks time travel beyond retention.
- Over-partitioning (many tiny files) instead of ZORDER.
- Thinking Delta is a separate DB — it's files + a log on ADLS.

## Senior-Level Discussion
Seniors discuss **partition strategy vs ZORDER**, **optimized writes/auto-compaction**, **MERGE performance** (partition pruning on the join), **concurrency conflicts** (retry/serializable isolation), and **retention/GDPR deletes** via `DELETE` + `VACUUM`.

## Related Topics
[Delta Lake (full)](../Delta%20Lake/) · [Databricks Interview Questions](Databricks%20Interview%20Questions.md) · [Lakehouse](../Lakehouse/) · [Performance Optimization](Performance%20Optimization.md)
