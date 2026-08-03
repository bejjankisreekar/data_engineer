# 05 — Column Operations & Functions

> Prev: [Reading & Writing](04_Reading_and_Writing_Data.md) · Next: [Aggregations](06_Aggregations_and_Grouping.md)

`pyspark.sql.functions` (imported as `F`) is your standard library — several hundred functions that run at JVM speed inside the engine. **If `F` has it, never write a UDF for it** ([UDF economics](10_UDFs_and_Pandas_Integration.md)).

```python
from pyspark.sql import functions as F
```

---

## Level 1 — The everyday toolkit

### Strings

```python
df.withColumn("name_clean", F.trim(F.lower("name")))
df.withColumn("initial",    F.substring("name", 1, 1))
df.withColumn("full",       F.concat_ws(" ", "first_name", "last_name"))
df.withColumn("len",        F.length("name"))
df.filter(F.col("email").contains("@gmail"))
df.filter(F.col("name").startswith("A"))
df.withColumn("masked", F.regexp_replace("phone", r"\d(?=\d{4})", "*"))
df.withColumn("order_no", F.regexp_extract("raw", r"ORD-(\d+)", 1))
df.withColumn("parts", F.split("path", "/"))          # → array (file 09)
df.withColumn("padded", F.lpad("id", 8, "0"))
```

### Numbers

```python
F.round("amount", 2), F.floor("x"), F.ceil("x"), F.abs("x")
F.greatest("a", "b", "c"), F.least("a", "b")          # row-wise max/min across columns
```

### Dates & timestamps

```python
df.withColumn("today",     F.current_date())
df.withColumn("hire_date", F.to_date("hire_str", "dd-MM-yyyy"))
df.withColumn("year",      F.year("hire_date"))       # also month, dayofmonth, hour...
df.withColumn("tenure_d",  F.datediff(F.current_date(), "hire_date"))
df.withColumn("plus_30",   F.date_add("hire_date", 30))
df.withColumn("month_end", F.last_day("hire_date"))
df.withColumn("as_text",   F.date_format("hire_date", "MMM yyyy"))      # → 'Apr 2021'
df.withColumn("mon_start", F.date_trunc("month", "sold_at"))            # truncate timestamp
```

### Conditionals — when/otherwise (SQL's CASE)

```python
df.withColumn("band",
    F.when(F.col("salary") >= 65000, "Senior")
     .when(F.col("salary") >= 55000, "Mid")
     .otherwise("Entry"))
```

Conditions evaluate top-down, first match wins; missing `otherwise` → null for unmatched rows (deliberate sometimes, forgotten often).

---

## Level 2 — Null handling, properly

Nulls follow SQL's [three-valued logic](../../02_Databases/SQL/01_What_is_SQL.md) — every comparison with null is neither true nor false:

```python
df.filter(F.col("dept").isNull())
df.filter(F.col("dept").isNotNull())
df.filter(F.col("dept") != "IT")            # ⚠ silently DROPS null-dept rows!
df.filter((F.col("dept") != "IT") | F.col("dept").isNull())   # what you probably meant

# Null-safe equality (null == null → True):
df1.join(df2, df1["k"].eqNullSafe(df2["k"]))

# Replace / default
F.coalesce("dept", F.lit("Unknown"))        # first non-null argument
df.fillna({"dept": "Unknown", "salary": 0}) # per-column defaults
df.dropna(subset=["id"])                    # drop rows null in key columns
df.na.replace("N/A", None, subset=["dept"]) # turn sentinel strings INTO real nulls first
```

**`F.lit()`** wraps a Python literal as a column — needed whenever you mix constants into expressions: `F.when(F.col("x") > 0, F.lit("pos"))`, `df.withColumn("source", F.lit("SAP"))`.

### expr() — SQL snippets inside DataFrame code

```python
df.withColumn("band", F.expr("CASE WHEN salary >= 65000 THEN 'Senior' ELSE 'Other' END"))
df.filter(F.expr("salary BETWEEN 50000 AND 65000"))
```

Same engine, same plan — use whichever reads clearer; `expr` is also the escape hatch for SQL-only features.

---

## Level 3 — Pro corner

- **Sargability applies here too**: `F.year(F.col("d")) == 2026` defeats partition pruning/pushdown; `F.col("d").between("2026-01-01", "2026-12-31")` doesn't ([same rule as SQL](../../02_Databases/SQL/06_SQL_DQL.md)).
- **Chained `when` beats nested Python if-logic in a UDF by 10–100×** — before writing any custom function, spend five minutes in the [functions docs](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html); `F` almost certainly has it (`months_between`, `sequence`, `format_number`, `sha2`, `xxhash64`…).
- **Deterministic cleanup pipeline**: standardize nulls first (`na.replace` sentinels → null), then trim/case-normalize strings, then cast, then validate — order matters; casting `" 42 "` fails where casting `"42"` succeeds.
- **Date format strings are Java patterns** (`yyyy`, `MM`, `dd`, `HH`) — `mm` is minutes, not months: the classic silent bug. And parsing behavior changed in Spark 3 (`spark.sql.legacy.timeParserPolicy`) — pin formats explicitly.
- **Column expressions are data, exploit it**: build transformations programmatically —

```python
# trim every string column in one select
string_cols = [c for c, t in df.dtypes if t == "string"]
df.select(*[F.trim(F.col(c)).alias(c) if c in string_cols else F.col(c) for c in df.columns])
```

This metaprogramming style is how [metadata-driven pipelines](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) apply per-table rules from config.

- **Hashing for keys/dedupe/SCD change detection**: `F.sha2(F.concat_ws("||", *cols), 256)` — one column that fingerprints a row; the standard [SCD2](../../02_Databases/SQL/13_SQL_Warehouse.md) "did anything change?" comparator.

## Checkpoint

1. Clean a `phone` column: strip non-digits, null out anything ≠ 10 digits, mask all but last 4.
2. Why does `!= "IT"` lose rows, and what's the fix?
3. Compute each employee's tenure in whole months.

Next: collapsing rows into answers → [06 — Aggregations & Grouping](06_Aggregations_and_Grouping.md).

---

## Further Learning — Docs & Videos

**Documentation**
- pyspark.sql.functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html
- Column API: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/column.html

**Videos**
- PySpark column functions (withColumn, when, expr): https://www.youtube.com/results?search_query=pyspark+withcolumn+select+functions+tutorial
