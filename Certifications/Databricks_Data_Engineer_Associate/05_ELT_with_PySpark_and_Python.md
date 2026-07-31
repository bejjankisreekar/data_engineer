# 05 — ELT with PySpark & Python

*Domain: ELT with Spark SQL and Python (29%) — the largest domain.*

---

## What it is

**PySpark** is the Python API for Apache Spark. On Databricks you use it to build the same ELT logic as Spark SQL, but programmatically with the **DataFrame API** — useful when you need Python control flow, reusable functions, parameterization, or complex transformations. The exam expects you to recognize correct PySpark syntax and understand how it relates to SQL.

---

## The DataFrame

A **DataFrame** is a distributed table of rows with a named, typed schema — Spark's core structured data abstraction. You build a query as a chain of **transformations** and trigger execution with an **action**.

```python
df = spark.read.table("students")            # read a table into a DataFrame
df = spark.read.format("csv").option("header", True).load("/path")
df.write.mode("append").saveAsTable("target")
```

### `spark` — the SparkSession

`spark` is the pre-created entry point (`SparkSession`) in every notebook. Use it to read tables, run SQL, and create DataFrames.

```python
spark.sql("SELECT * FROM students WHERE value > 3")   # run SQL, returns a DataFrame
spark.table("students")                                # same as spark.read.table
spark.createDataFrame([(1, "a"), (2, "b")], ["id", "name"])
```

> **Exam Tip:** `spark.sql("...")` runs a SQL string and **returns a DataFrame** — you can freely mix SQL and DataFrame code. `spark.table("name")` and `spark.read.table("name")` both load a registered table.

---

## Transformations vs Actions (lazy evaluation)

**This is a core, commonly-tested Spark concept.**

- **Transformations** are **lazy** — they build up a plan but do **not** execute. Examples: `select`, `filter`/`where`, `withColumn`, `groupBy`, `join`, `orderBy`, `distinct`, `drop`.
- **Actions** **trigger execution** of the whole plan. Examples: `show()`, `display()`, `collect()`, `count()`, `take()`, `first()`, `write`/`save`.

> **Exam Tip:** Spark uses **lazy evaluation**: nothing runs until an **action** is called. Chaining `.select().filter()` does no work; `.count()` or `.show()` triggers it. This lets Spark's Catalyst optimizer plan the most efficient execution. Know which calls are transformations (lazy) vs actions (eager).

### Narrow vs wide transformations

- **Narrow** (e.g., `select`, `filter`, `withColumn`) — each input partition contributes to one output partition; **no shuffle**.
- **Wide** (e.g., `groupBy`, `join`, `distinct`, `orderBy`) — data must be **shuffled** across the cluster; more expensive.

---

## Common DataFrame operations

```python
from pyspark.sql.functions import col, lit, when, count, avg, to_date, explode

df.select("id", "name")
df.select(col("value") * 2)
df.filter(col("value") > 3)              # same as .where(...)
df.where("value > 3")                     # SQL-string predicate also works
df.withColumn("doubled", col("value") * 2)      # add/replace a column
df.withColumnRenamed("value", "score")
df.drop("temp_col")
df.distinct()                             # or df.dropDuplicates(["id"])
df.orderBy(col("value").desc())
df.limit(10)
```

### Aggregations

```python
df.groupBy("dept").agg(count("*").alias("n"), avg("salary").alias("avg_sal"))
df.groupBy("dept").count()
```

### Conditional logic

```python
df.withColumn("grade",
    when(col("score") >= 90, "A")
    .when(col("score") >= 80, "B")
    .otherwise("C"))
```

> **Exam Tip:** `withColumn("new", expr)` returns a **new DataFrame** with the added/replaced column (DataFrames are immutable — the original is unchanged). `col("x")` references a column; `lit(5)` wraps a literal value. `when(...).otherwise(...)` is the DataFrame equivalent of SQL `CASE WHEN`.

---

## Reading and writing data

### Reading

```python
spark.read.format("json").load("/path")
spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/path")
spark.read.table("db.table")
spark.read.parquet("/path")
```

### Writing — save modes (heavily tested)

```python
df.write.mode("append").saveAsTable("t")       # add rows
df.write.mode("overwrite").saveAsTable("t")     # replace all data
df.write.format("delta").mode("append").save("/path")   # write to a path
```

| Save mode | Behavior |
|---|---|
| `append` | Add new rows to existing data |
| `overwrite` | Replace all existing data |
| `error` / `errorifexists` (default) | Fail if the table/path already exists |
| `ignore` | Do nothing if it already exists |

> **Exam Tip:** `saveAsTable` writes to a **managed/registered table**; `save(path)` writes to a **path**. The default save mode is **`errorifexists`** — a plain write fails if the target already exists. Use `mode("append")` to add and `mode("overwrite")` to replace. For schema changes on overwrite, add `.option("overwriteSchema", "true")`.

---

## Temp views from DataFrames (bridging Python ↔ SQL)

```python
df.createOrReplaceTempView("my_temp_view")     # session-scoped
df.createOrReplaceGlobalTempView("g_view")     # cluster-scoped (global_temp.g_view)
spark.sql("SELECT * FROM my_temp_view WHERE value > 3")
```

> **Exam Tip:** `createOrReplaceTempView` registers a DataFrame as a **temporary view** you can then query with `spark.sql(...)`. It's the standard way to move from the DataFrame API into SQL. It is session-scoped and disappears when the notebook/session ends.

---

## Inspecting DataFrames

```python
df.printSchema()          # show column names and types
df.schema                 # StructType object
df.columns                # list of column names
df.dtypes                 # list of (name, type)
df.show(5)                # print first 5 rows (an action)
display(df)               # Databricks rich interactive display (an action)
df.count()                # number of rows (an action)
df.collect()              # bring ALL rows to the driver as a list (action — careful!)
df.take(3)                # first 3 rows to driver
```

> **Exam Tip:** `collect()` pulls the **entire** DataFrame into the driver's memory — dangerous for large data (can OOM the driver). Prefer `show()`/`display()`/`take()`/`limit()` for inspection. `display()` is the Databricks-specific rich renderer with built-in charting.

---

## Python UDFs vs built-in / SQL functions

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(returnType=StringType())
def to_upper(s):
    return s.upper() if s else None

df.withColumn("upper_name", to_upper(col("name")))
```

> **Exam Tip:** **Python UDFs are slower** than built-in Spark SQL functions because data must be serialized between the JVM and Python (and they're a black box to the Catalyst optimizer). **Prefer built-in functions** (`pyspark.sql.functions`) or **SQL UDFs** whenever possible. Use Python UDFs only when no built-in exists.

---

## Parameterizing notebooks with widgets

```python
dbutils.widgets.text("env", "dev")
env = dbutils.widgets.get("env")             # read a passed-in parameter
```

Widgets let Jobs pass parameters into a notebook at runtime — the standard way to make a notebook reusable across environments.

---

## Quick Review

- **DataFrame** = distributed typed table; build with lazy **transformations**, execute with **actions**.
- **Lazy evaluation**: `select/filter/withColumn/groupBy/join` do nothing until an **action** (`count/show/collect/write`) runs.
- **Narrow** transforms (no shuffle) vs **wide** transforms (`groupBy/join/distinct` = shuffle).
- DataFrames are **immutable** — `withColumn`, `filter`, etc. return **new** DataFrames.
- Save modes: **`append`**, **`overwrite`**, default **`errorifexists`**, `ignore`. `saveAsTable` (table) vs `save` (path).
- `spark.sql(...)` returns a DataFrame; `createOrReplaceTempView` bridges DataFrame → SQL.
- `collect()` brings all rows to the driver — avoid on big data; use `show/display/take`.
- **Prefer built-in / SQL functions over Python UDFs** (UDFs are slower, opaque to the optimizer).
- **Widgets** parameterize notebooks for Jobs.

---

## Further Learning — Docs & Videos

**Official documentation**
- PySpark on Databricks: https://docs.databricks.com/en/pyspark/index.html
- DataFrames intro: https://docs.databricks.com/en/getting-started/dataframes.html
- PySpark API reference: https://spark.apache.org/docs/latest/api/python/index.html
- Transformations & lazy evaluation: https://spark.apache.org/docs/latest/rdd-programming-guide.html#transformations
- Save modes / write: https://docs.databricks.com/en/delta/tutorial.html
- Python UDFs: https://docs.databricks.com/en/udf/python.html
- Widgets: https://docs.databricks.com/en/notebooks/widgets.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- PySpark DataFrame tutorial: https://www.youtube.com/results?search_query=databricks+pyspark+dataframe+tutorial
- Transformations vs actions (lazy evaluation): https://www.youtube.com/results?search_query=spark+transformations+vs+actions+lazy+evaluation
- Narrow vs wide transformations / shuffle: https://www.youtube.com/results?search_query=spark+narrow+vs+wide+transformation+shuffle

---

Next: **[06 — Structured Streaming](06_Structured_Streaming.md)**.
