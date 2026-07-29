# SQL — Query Optimization

## Overview
Optimization separates seniors from juniors. The approach: **read the execution plan → find the expensive operator → fix (index, rewrite, statistics, partitioning)**. Applies to Azure SQL, Synapse, and Spark SQL (with platform nuances).

---

## The methodology
1. **Read the execution plan** — look for table/index **scans**, **key lookups**, **hash/sort spills**, and bad **cardinality estimates**.
2. Identify the costly operator.
3. Apply the right lever, re-check the plan.

---

## Optimization levers (with WHY)
| Lever | Why |
|---|---|
| **Indexes** on WHERE/JOIN/ORDER BY | Avoid full scans |
| **Covering index** (INCLUDE columns) | Eliminate key lookups |
| **SARGable predicates** | Index can be used (`col = x`, not `FUNC(col)=x`) |
| Avoid `SELECT *` | Less IO, enables covering indexes |
| **Update statistics** | Optimizer picks better plans |
| **Filter early / push down** | Less data through the pipeline |
| **Pre-aggregate** into Gold tables | Reports hit small summaries |
| Partitioning | Prune large tables |

---

## SARGable — the classic trap
```sql
-- ❌ NOT SARGable (function on column → scan)
WHERE YEAR(order_date) = 2026
-- ✅ SARGable (index seek)
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01'
```

---

## Synapse-specific (dedicated pool)
- **Distribution:** HASH (large fact on join key), ROUND_ROBIN (staging), REPLICATE (small dims) — to **avoid data movement (shuffle)**.
- **Partitioning** by date for pruning + partition switching.
- **Materialized views** / **result-set caching** for repeated queries.
- Right **resource class** for load concurrency.

## Spark SQL-specific
- Partition pruning + `ZORDER`, broadcast small tables, AQE, avoid UDFs, `OPTIMIZE` small files.

---

## Scenario Questions
**S1. "Query slow after growth; plan shows a full scan."** Add covering index on filter/join cols; make predicate SARGable; consider partitioning.
**S2. "Synapse join is slow with lots of data movement."** Align **distribution keys** on join columns (HASH), REPLICATE small dims.
**S3. "Report recomputes the same aggregation constantly."** Pre-aggregate into a Gold table / materialized view.
**S4. "Plan changed and got slow overnight."** Stale statistics / parameter sniffing → update stats, `OPTIMIZE FOR`, recompile.

---

## Quick Revision
- ✔ Read the **execution plan** first
- ✔ Index WHERE/JOIN/ORDER BY; **covering** index kills key lookups
- ✔ **SARGable** predicates (no functions on indexed cols)
- ✔ No `SELECT *`; filter early; update **statistics**
- ✔ Synapse: **distribution** (HASH/REPLICATE/ROUND_ROBIN) to avoid data movement
- ✔ Spark: partition prune + ZORDER + broadcast + AQE
- ✔ Pre-aggregate hot reports

## Common Interview Mistakes
- Adding indexes blindly (hurts writes).
- Non-SARGable predicates.
- Ignoring statistics/parameter sniffing.
- In Synapse, wrong distribution → constant shuffles.

## Senior-Level Discussion
Seniors quantify from the plan (estimated vs actual rows, spills), choose indexing/distribution for the **access pattern**, and know the same "reduce data scanned + avoid shuffle" principle applies whether it's Azure SQL, Synapse, or Spark — just different mechanics.

## Related Topics
[SQL Interview Questions](SQL%20Interview%20Questions.md) · [Window Functions](Window%20Functions.md) · [Azure Synapse](../Azure%20Synapse/) · [Azure SQL](../Azure%20SQL/)
