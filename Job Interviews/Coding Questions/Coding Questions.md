# Coding Questions — Azure Data Engineer

## Overview
DE coding rounds mix **SQL query problems**, **PySpark transformations**, and **Python data manipulation**. Rarely LeetCode-hard algorithms — more "solve this data problem." Below are the common ones with solutions.

> Full SQL query bank: see `01_SQL/Practical_SQL_Query_Interview_Questions.md` (55 solved with explanations).

---

## SQL (most common)
See the dedicated bank, but the must-knows:
- Second/Nth highest salary → `DENSE_RANK`
- Top-N per group → `ROW_NUMBER/RANK OVER (PARTITION BY ...)`
- Remove duplicates → `ROW_NUMBER = 1`
- Running total → `SUM() OVER (ORDER BY ...)`
- Records in A not in B → `NOT EXISTS`
- Consecutive streaks → gaps-and-islands

---

## PySpark coding problems

### 1. Deduplicate keeping latest per key
```python
from pyspark.sql import functions as F, Window
w = Window.partitionBy("id").orderBy(F.col("updated_at").desc())
latest = df.withColumn("rn", F.row_number().over(w)).filter("rn=1").drop("rn")
```

### 2. Word count
```python
(df.select(F.explode(F.split(F.col("line"), " ")).alias("word"))
   .groupBy("word").count().orderBy(F.desc("count")))
```

### 3. Running total per customer
```python
w = Window.partitionBy("customer_id").orderBy("order_date") \
          .rowsBetween(Window.unboundedPreceding, Window.currentRow)
df.withColumn("running_total", F.sum("amount").over(w))
```

### 4. Flatten nested JSON
```python
df.select("id", F.explode("items").alias("item")) \
  .select("id", "item.sku", "item.qty")
```

### 5. Join + broadcast the small dimension
```python
from pyspark.sql.functions import broadcast
fact.join(broadcast(dim), "dim_id", "left")
```

### 6. Pivot
```python
df.groupBy("product").pivot("month").sum("amount")
```

### 7. Handle nulls / data quality
```python
clean = (df.na.drop(subset=["id"])
           .na.fill({"amount": 0})
           .dropDuplicates(["id"]))
```

---

## Python coding problems

### 8. Deduplicate a list preserving order
```python
def dedupe(items):
    return list(dict.fromkeys(items))
```

### 9. Word frequency
```python
from collections import Counter
Counter(text.lower().split())
```

### 10. Parse & flatten JSON
```python
import json
data = json.loads(raw)
rows = [{"id": r["id"], "sku": i["sku"]} for r in data for i in r["items"]]
```

### 11. Read a large file efficiently (generator)
```python
def read_lines(path):
    with open(path) as f:
        for line in f:          # streams, doesn't load all into memory
            yield line.strip()
```

### 12. Group by key
```python
from collections import defaultdict
groups = defaultdict(list)
for r in rows:
    groups[r["city"]].append(r)
```

---

## How to approach a coding round
1. **Clarify** input/output, edge cases (nulls, duplicates, empty).
2. State the approach **before** coding.
3. Prefer **built-in/vectorized** ops (SQL window, Spark functions) over loops/UDFs.
4. Handle **nulls, duplicates, and empties** explicitly.
5. Mention **scale** (would this work on 1TB? → Spark, partitioning).

## Quick Revision
- ✔ SQL: DENSE_RANK, ROW_NUMBER, window sums, NOT EXISTS, gaps-and-islands
- ✔ PySpark: Window dedup, explode, broadcast, pivot, na.drop/fill
- ✔ Python: `dict.fromkeys` dedup, `Counter`, json flatten, generators
- ✔ Prefer built-ins over UDFs/loops
- ✔ Always handle nulls/dupes/empties

## Common Mistakes
- Writing Python UDFs where Spark built-ins exist.
- `collect()` on big data.
- Ignoring nulls/duplicates/edge cases.
- Not clarifying requirements first.

## Related Topics
SQL, PySpark, Python, Scenario Based Questions
