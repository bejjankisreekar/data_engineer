# 07 — Joins

> Prev: [Aggregations](06_Aggregations_and_Grouping.md) · Next: [Window Functions](08_Window_Functions.md)

Join *logic* is identical to [SQL joins](../01_SQL/07_SQL_Keys_and_Joins.md) — grain, fan-out, null keys, all of it transfers. What PySpark adds: syntax details that cause duplicate-column pain, and the **distributed cost model** (broadcast vs shuffle) that decides whether your join takes seconds or hours.

```python
emp  = spark.createDataFrame([(1,"Asha","IT"),(2,"Ravi","HR"),(3,"Meena",None)],
                             ["id","name","dept_code"])
dept = spark.createDataFrame([("IT","Technology"),("HR","People"),("FIN","Finance")],
                             ["dept_code","dept_name"])
```

---

## Level 1 — Syntax and join types

```python
# Same-named key: pass the name (or list) — result has ONE dept_code column ✅
emp.join(dept, on="dept_code", how="inner")
emp.join(dept, on=["dept_code"], how="left")

# Different names / complex conditions: expression form
orders.join(cust, orders["cust_id"] == cust["id"], "left")
```

| `how=` | Keeps |
|---|---|
| `inner` | matches only |
| `left` / `right` | all left / all right + matches |
| `full` (outer) | everything from both |
| `left_semi` | left rows **that have** a match — no right columns (SQL EXISTS) |
| `left_anti` | left rows **without** a match (SQL NOT EXISTS) |
| `cross` | cartesian product — `df1.crossJoin(df2)`, deliberate use only |

```python
# Semi/anti — the underused workhorses:
active_customers = customers.join(orders, "cust_id", "left_semi")     # has ≥1 order
never_ordered    = customers.join(orders, "cust_id", "left_anti")     # has none
```

Semi/anti never duplicate rows (no fan-out possible) and carry no right-side columns — prefer them over inner-join-then-distinct or [NOT IN traps](../01_SQL/09_SQL_Subqueries.md).

---

## Level 2 — The two classic PySpark join pains

### 1. Duplicate columns after expression joins

```python
j = orders.join(cust, orders["cust_id"] == cust["id"], "inner")
j.select("cust_id")        # fine
j.select("name")           # AMBIGUOUS error if both have 'name'!

# Fixes, best first:
cust2 = cust.select(F.col("id").alias("cust_id"), F.col("name").alias("cust_name"))
orders.join(cust2, "cust_id")                          # rename BEFORE joining (cleanest)
j.select(orders["name"], cust["name"].alias("cust_name"))   # qualify via parent df
j.drop(cust["id"])                                     # drop one side's column
```

Habit that prevents it entirely: **alias/prefix columns before joining** — one `select` with renames per side.

### 2. Null keys

Rows with null join keys match *nothing* — even other nulls (`null == null` is not true; [three-valued logic](../01_SQL/01_What_is_SQL.md)). In a left join they survive with null right-side columns; in an inner join they vanish silently. Decide explicitly: filter them, default them (`coalesce(key, lit(-1))` to an Unknown member — [warehouse pattern](../01_SQL/13_SQL_Warehouse.md)), or `eqNullSafe` if null-matches-null is truly intended.

### Grain check — the two-line insurance

```python
before = orders.count()
after  = orders.join(dim, "key", "left").count()
assert before == after, "join fanned out — dim has duplicate keys!"
```

A left join that *grows* the left side means the right side wasn't unique on the key ([fan-out](../01_SQL/07_SQL_Keys_and_Joins.md)) — dedupe the dimension first ([window pattern](08_Window_Functions.md)).

---

## Level 3 — Pro corner: how joins execute

### Broadcast vs shuffle (the performance decision)

- **Sort-merge join** (default for two big tables): *both* sides shuffle by key across the cluster — expensive but scales.
- **Broadcast hash join**: the small side is copied to every executor; the big side **never moves**. Automatic under `spark.sql.autoBroadcastJoinThreshold` (10 MB default; higher on Databricks), or forced:

```python
result = big_fact.join(F.broadcast(small_dim), "dept_code")
```

Dimension tables are almost always broadcast material. Verify with `result.explain()` — `BroadcastHashJoin` vs `SortMergeJoin` in the plan ([reading plans](What_Is_Apache_Spark.md)). AQE also converts to broadcast at runtime when a filtered side turns out small ([AQE](Spark_Processing.md)).

- Broadcasting something *too big* OOMs every executor at once — don't force-broadcast blindly; know the side's real size.

### Skewed joins

One hot key (one mega-customer, or millions of null-key rows) → one straggler task. Order of fixes: let AQE skew-handling work (on by default in Databricks) → broadcast the other side → handle the hot key separately (nulls especially: split, join non-null, union back) → salting ([full recipe](Spark_Processing.md)).

### Range and inequality joins

`orders.join(rates, (orders.ts >= rates.valid_from) & (orders.ts < rates.valid_to))` — the SCD2-lookup join. Naively this is O(n×m) per key group; Databricks optimizes some cases (range join hints: `.hint("range_join", 60)`), otherwise pre-bucket timestamps. Know that inequality joins *can't* broadcast-hash — they're the slow join family, budget accordingly.

### Field-tested notes

- **Join order in code doesn't matter** (optimizer reorders); join *strategy* and *pre-shrinking* do — filter and select columns **before** the join, not after.
- Chained multi-joins: build from the fact outward, checking counts at each step during development; one bad dimension poisons everything downstream.
- Self-joins need aliases: `a = df.alias("a"); b = df.alias("b"); a.join(b, F.col("a.mgr_id") == F.col("b.id"))`.
- The `USING`-style (`on="key"`) join coalesces the key column automatically in outer joins — expression-form outer joins leave you two half-null key columns to `coalesce` manually. Prefer `on="name"` whenever names align.

## Checkpoint

1. Employees with their dept names, keeping employees whose dept_code is null or unmatched, with a single `dept_code` column and no ambiguity.
2. Customers with zero orders in 2026 — which join type, and why not `NOT IN`?
3. Your fact-to-dim join takes 40 min; the dim is 200 MB after filtering to current rows. What do you try first, and how do you verify it worked?

Next: aggregates that don't collapse rows → [08 — Window Functions](08_Window_Functions.md).
