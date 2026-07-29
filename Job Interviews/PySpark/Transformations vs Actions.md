# Transformations vs Actions

## Overview
The core of Spark's lazy execution model. Transformations build a plan; actions run it. This distinction drives performance reasoning and is asked in almost every PySpark interview.

---

## The distinction
| | Transformations | Actions |
|---|---|---|
| Execution | **Lazy** — build DAG, run nothing | **Eager** — trigger the job |
| Returns | A new DataFrame/RDD | A value / writes output |
| Examples | `select`, `filter`, `withColumn`, `groupBy`, `join`, `distinct`, `orderBy`, `drop` | `count`, `collect`, `show`, `take`, `first`, `write`, `save`, `foreach` |

**Why lazy?** Spark waits until an action, then Catalyst optimizes the *whole* chain (predicate pushdown, column pruning, join reordering) before executing — far more efficient than running each step eagerly.

---

## Narrow vs wide (a sub-question)
- **Narrow** (`select`, `filter`, `withColumn`) — no shuffle, stays within partition.
- **Wide** (`groupBy`, `join`, `distinct`, `orderBy`, `repartition`) — **shuffle**, stage boundary.

---

## Code / behavior
```python
df2 = df.filter("amount > 100").select("id","amount")  # nothing runs yet
df2.count()      # ACTION → now the whole chain executes
df2.write.format("delta").save("/gold/x")  # ACTION
```
```python
df.explain(True)  # inspect the plan without running (still lazy)
```

---

## Quick Revision
- ✔ Transformations = lazy plan; Actions = execute
- ✔ Actions: `count/collect/show/take/first/write`
- ✔ Laziness enables **Catalyst** optimization
- ✔ Narrow = no shuffle; Wide = shuffle (stage boundary)
- ✔ `explain()` shows the plan without an action

## Common Interview Mistakes
- Believing `filter`/`select` execute immediately.
- Calling multiple actions on an uncached reused DataFrame (recomputes each time → cache it).

## Senior-Level Discussion
Seniors point out that repeated actions on an uncached DataFrame recompute the full lineage each time — so they `cache()` reused results, and they read `explain()` to confirm pushdown/pruning happened.

## Related Topics
[PySpark Interview Questions](PySpark%20Interview%20Questions.md) · [Spark Architecture](../Azure%20Databricks/Spark%20Architecture.md) · [Partitioning](Partitioning.md)
