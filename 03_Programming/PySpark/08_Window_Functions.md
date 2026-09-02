# 08 — Window Functions

> Prev: [Joins](07_Joins.md) · Next: [Complex Types & JSON](09_Complex_Types_and_JSON.md)

A window function computes a value for **every row** using a *window* of related rows — without collapsing them like [groupBy](06_Aggregations_and_Grouping.md) does. Ranking, "latest per key," running totals, and change-over-time all live here. (SQL theory: [window coverage in SQL_DQL](../../02_Databases/SQL/06_SQL_DQL.md).)

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

---

## The pattern

Every window use has the same three parts:

```python
w = Window.partitionBy("dept").orderBy(F.desc("salary"))   # 1. define the window
emp.withColumn("rank_in_dept", F.row_number().over(w))     # 2. function .over(window)
# 3. every row keeps its identity + gains the computed column
```

### Ranking family

```python
w = Window.partitionBy("dept").orderBy(F.desc("salary"))
emp.select("name", "dept", "salary",
    F.row_number().over(w).alias("row_num"),     # ties → 1,2,3 (unique, arbitrary on ties)
    F.rank().over(w).alias("rank"),              # ties → 1,1,3
    F.dense_rank().over(w).alias("dense"))       # ties → 1,1,2
```

**Top-N per group** — the most-used pattern in data engineering:

```python
top3 = (emp.withColumn("rn", F.row_number().over(w))
           .filter(F.col("rn") <= 3)
           .drop("rn"))
```

### Offset family — lag / lead

```python
w = Window.partitionBy("store").orderBy("month")
sales.withColumn("prev_month", F.lag("revenue", 1).over(w))          # null for first row
     .withColumn("growth",     F.col("revenue") - F.col("prev_month"))
     .withColumn("next_month", F.lead("revenue", 1).over(w))
```

### Aggregates over windows

```python
w_dept = Window.partitionBy("dept")                 # no orderBy → whole partition
emp.withColumn("dept_avg", F.avg("salary").over(w_dept))
   .withColumn("vs_avg",   F.col("salary") - F.col("dept_avg"))
```

---

## Frames: running totals and moving averages

When a window has `orderBy`, aggregates default to *"start of partition up to current row"* — that's what makes running totals work:

```python
w_run = Window.partitionBy("store").orderBy("month")            # implicit frame: unboundedPreceding → currentRow
sales.withColumn("ytd", F.sum("revenue").over(w_run))

# Explicit frames:
w_3mo = (Window.partitionBy("store").orderBy("month")
         .rowsBetween(-2, 0))                                   # this row + 2 before
sales.withColumn("moving_3mo_avg", F.avg("revenue").over(w_3mo))

# rangeBetween works on VALUES not row positions (needs numeric/interval orderBy):
w_30d = (Window.partitionBy("cust").orderBy(F.col("ts").cast("long"))
         .rangeBetween(-30*86400, 0))                           # trailing 30 days by time
```

`rowsBetween` counts rows; `rangeBetween` counts order-key distance — the difference matters whenever data has gaps or duplicate keys.

### The dedupe pattern (memorize this one)

"Keep the latest version of each key" — the standard CDC/staging cleanup ([why it's needed](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md)):

```python
w = Window.partitionBy("business_key").orderBy(F.desc("updated_at"), F.desc("_ingest_file"))
latest = (raw.withColumn("rn", F.row_number().over(w))
             .filter("rn = 1").drop("rn"))
```

Note the **tiebreaker column** in orderBy — without it, two rows with the same `updated_at` are picked arbitrarily and non-reproducibly.

---

## Pro corner

- **`partitionBy` is mandatory in spirit**: a window without it pulls the *entire dataset into one task* — the silent single-node bottleneck ([gotcha](../../02_Databases/SQL/06_SQL_DQL.md)). If you truly need a global order (global row numbers), question the requirement first; `monotonically_increasing_id()` gives unique-but-not-sequential ids without the collapse.
- **Windows are shuffles**: each distinct `partitionBy` spec = one shuffle by those keys. Multiple window columns *sharing the same window spec* reuse one shuffle — define `w` once and reuse it; five different specs = five shuffles.
- **Windows vs groupBy+join**: "each row + its group average" via window beats aggregate-then-join-back (one shuffle vs two, no duplicate-column pain). Conversely, if you only need the collapsed result, `groupBy` is cheaper than window+distinct.
- **Skew applies**: a hot partition key (one customer with 100M events) makes one window task huge — same diagnosis and fixes as [join skew](Spark_Processing.md).
- **Sessionization** — the advanced interview classic (gaps-and-islands, [SQL version](../../02_Databases/SQL/06_SQL_DQL.md)):

```python
w = Window.partitionBy("user").orderBy("ts")
sessions = (events
    .withColumn("prev_ts", F.lag("ts").over(w))
    .withColumn("new_sess", (F.col("ts").cast("long") - F.col("prev_ts").cast("long") > 1800)
                             .cast("int"))
    .fillna({"new_sess": 1})
    .withColumn("session_id", F.sum("new_sess").over(w)))      # running sum of boundaries = session number
```

- **QUALIFY** (Databricks SQL) filters on window results directly — in SQL contexts it replaces the `rn`-subquery dance; DataFrame API still uses the filter-and-drop idiom.
- `first`/`last` **over an ordered window** are deterministic (unlike their [groupBy cousins](06_Aggregations_and_Grouping.md)) — but remember last's default frame ends at *currentRow*; add `.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)` to get the true partition-last.

## Checkpoint

1. For each customer: their orders, each order's amount, the running lifetime total, and days since their previous order.
2. Deduplicate a CDC feed to latest-per-key, deterministically.
3. Why is `Window.orderBy("ts")` without partitionBy dangerous on a billion rows?

Next: nested data — arrays, structs, JSON → [09 — Complex Types & JSON](09_Complex_Types_and_JSON.md).

---

## Further Learning — Docs & Videos

**Documentation**
- Window functions (Spark SQL): https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-window.html
- pyspark.sql.Window: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/window.html

**Videos**
- PySpark window functions (row_number, rank, lag, lead): https://www.youtube.com/results?search_query=pyspark+window+functions+row_number+rank+lag+lead
