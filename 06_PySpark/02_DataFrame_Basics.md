# 02 — DataFrame Basics

> Prev: [Getting Started](01_Getting_Started_SparkSession.md) · Next: [Schemas & Data Types](03_Schemas_and_Data_Types.md)

## What is a DataFrame?

A **DataFrame** is Spark's main data structure: a **distributed table** — data organized into named, typed columns and rows, like a SQL table or a spreadsheet, but split into [partitions](Spark_Processing.md) that live spread across the machines of a cluster.

Analogy: a normal spreadsheet lives on one computer. A DataFrame is a spreadsheet **torn into chunks and handed to a whole team** — each machine holds and processes its own chunk, and Spark makes them look and behave like one single table to you.

Unpacking the definition:

- **Table-shaped** — named columns, each with a type (`name: string`, `salary: long`). You always know the structure; that's the schema ([file 03](03_Schemas_and_Data_Types.md)).
- **Distributed** — the rows physically live in partitions across many machines. A DataFrame of 10 billion rows is normal; no single machine ever holds all of it.
- **Immutable** — you never modify a DataFrame; every operation returns a *new* one. (This is what lets Spark optimize and recover from failures — [lineage](What_Is_Apache_Spark.md).)
- **Lazy** — a DataFrame is really a *plan* for producing data ("read this file, filter, add a column"), not the data itself. Nothing runs until an action like `show()` or `write` forces it.

How it compares to things you may already know:

| | pandas DataFrame | SQL table | Spark DataFrame |
|---|---|---|---|
| Lives | One machine's RAM | Database storage | Partitioned across a cluster |
| Size limit | Your RAM | Disk | Effectively none |
| Executes | Immediately | Per query | Lazily, on actions |
| Mutable? | Yes | Yes (DML) | No — every op returns a new one |

## What is the DataFrame API?

The **DataFrame API** is the set of methods you call *on* DataFrames to work with them — `select()`, `filter()`, `withColumn()`, `groupBy()`, `join()`, `orderBy()` and the rest of this series. It's Spark's high-level programming interface: instead of writing loops over rows, you **describe the result you want** by chaining operations, and Spark's optimizer ([Catalyst](What_Is_Apache_Spark.md)) figures out the most efficient way to execute that description across the cluster.

```python
# This is the DataFrame API in action — declarative chained methods, no loops:
result = (emp.filter(F.col("salary") > 50000)   # describe: keep these rows
             .withColumn("annual", F.col("salary") * 12)   # describe: add a column
             .groupBy("dept").agg(F.avg("annual")))        # describe: summarize
# Nothing has executed yet — result is an optimized PLAN until an action runs it.
```

Three facts about the API worth knowing from day one:

1. **It's declarative, like SQL** — you say *what*, the engine decides *how*. That's why the same rules apply (the optimizer may reorder your filters, and `spark.sql("...")` compiles to the identical plan — [file 11](11_Spark_SQL_and_Views.md)).
2. **It's the same API in every language** — Python (PySpark), Scala, Java, R all expose the same DataFrame API, and for DataFrame operations they're equally fast, because the API only *builds the plan*; execution happens in Spark's engine ([why PySpark isn't slower](What_Is_Apache_Spark.md)).
3. **It replaced the older RDD API** — RDDs (raw distributed collections with `map`/`reduce` functions) still exist underneath, but the DataFrame API is what you write today: it gives the optimizer visibility that RDD lambdas never could ([RDD vs DataFrame](What_Is_Apache_Spark.md)).

In short: the **DataFrame** is the *thing* (a distributed table-as-a-plan); the **DataFrame API** is the *vocabulary* you use to work with it. The rest of this file teaches that vocabulary's core verbs.

---

## Setup used below

```python
from pyspark.sql import functions as F      # THE import — you'll type this forever

emp = spark.createDataFrame(
    [(1, "Asha",  "IT",      60000, "2021-04-01"),
     (2, "Ravi",  "HR",      50000, "2019-07-15"),
     (3, "Meena", "IT",      65000, "2020-01-20"),
     (4, "John",  "Finance", 55000, "2022-11-05"),
     (5, "Sana",  None,      48000, "2023-02-10")],
    ["id", "name", "dept", "salary", "hire_date"])
```

---

## Level 1 — Inspecting a DataFrame

```python
emp.show()                 # print first 20 rows (action)
emp.show(2, truncate=False)
emp.printSchema()          # column names + types + nullability
emp.columns                # ['id', 'name', ...]
emp.count()                # number of rows (action — full scan!)
emp.describe("salary").show()   # count/mean/stddev/min/max
display(emp)               # Databricks-only: rich interactive table
```

## Level 1 — The core verbs

```python
# SELECT — choose/rename columns
emp.select("name", "salary")
emp.select(F.col("name").alias("employee_name"))

# FILTER — keep rows (filter and where are identical)
emp.filter(emp.salary > 55000)
emp.filter((F.col("dept") == "IT") & (F.col("salary") > 60000))   # & | ~ , NOT and/or/not!
emp.where("dept = 'IT' and salary > 60000")                       # SQL string works too

# NEW / CHANGED COLUMNS
emp.withColumn("annual", F.col("salary") * 12)
emp.withColumn("salary", F.col("salary") + 5000)      # same name = replace
emp.withColumnRenamed("dept", "department")

# DROP, SORT, LIMIT, DISTINCT
emp.drop("hire_date")
emp.orderBy(F.col("salary").desc())
emp.orderBy("dept", F.desc("salary"))
emp.limit(3)
emp.select("dept").distinct()
```

Everything above is a **transformation** — it returns a *new* DataFrame (they're immutable; nothing modifies in place) and runs nothing until an action (`show`, `count`, `collect`, `write`).

### Chaining — how real code looks

```python
result = (emp
    .filter(F.col("salary") > 50000)
    .withColumn("annual", F.col("salary") * 12)
    .select("name", "dept", "annual")
    .orderBy(F.desc("annual")))

result.show()
```

The parentheses-around-the-chain style is the idiom — readable, diffable, no `\` line continuations.

---

## Level 2 — The details that separate working code from lucky code

### Three ways to reference a column — and when each breaks

```python
emp.salary                 # attribute style — breaks on names with spaces or reserved words
emp["salary"]              # bracket style — safe with any name
F.col("salary")            # unbound reference — required inside functions, safest habit
```

Default to `F.col()`. In joins with duplicate column names, you'll need `df1["salary"]` disambiguation ([joins file](07_Joins.md)).

### Actions that bite

```python
emp.collect()      # brings ALL rows to the driver as Python objects — OOM on real data!
emp.take(5)        # safe: just 5 rows
emp.first()
emp.toPandas()     # entire DataFrame → pandas on the driver — same danger as collect
```

Rule: `collect()`/`toPandas()` only after you've aggregated/limited to something small ([driver OOM](Spark_Architecture.md)).

### Rows are Row objects

```python
row = emp.first()
row.name, row["salary"]        # field access
row.asDict()                   # {'id': 1, 'name': 'Asha', ...}
```

### withColumns / select for many columns

```python
# Adding many columns one withColumn at a time is slow to PLAN (not run) — batch them:
emp.withColumns({"annual": F.col("salary")*12, "tax": F.col("salary")*0.1})   # Spark 3.3+
```

---

## Level 3 — Pro corner

- **`count()` is not free** — it triggers a full job. Don't sprinkle counts through production code as progress prints; compute once into a variable if needed, or rely on write metrics ([observability](14_Performance_and_Best_Practices.md)).
- **Immutability enables the optimizer**: because each step returns a new logical plan, Catalyst can rewrite the whole chain ([how](What_Is_Apache_Spark.md)). Your 8 chained calls usually compile into 1–2 physical stages — chains are *not* 8 passes over the data.
- **`orderBy` on big data is expensive** (global sort = shuffle to one ordering). Sort at the end, on reduced data — or not at all if the consumer (BI tool, downstream table) doesn't need it.
- **`distinct()` is a shuffle** of every selected column; `dropDuplicates(["id"])` on a key subset is usually what you actually mean — and a window-dedupe is more controllable still ([pattern](08_Window_Functions.md)).
- **`limit(n)` then `collect()`** is the safe inspection pair; `show()` internally does `limit(20)` — that's why it's always fast even on huge tables.
- Column name hygiene: spaces/dots in names (common from Excel [CSVs](../02_File_formats/01_CSV.md)) break attribute access and complicate everything — `withColumnRenamed` or a cleanup loop over `df.columns` first thing after ingest.

## Checkpoint

1. From `emp`, get non-null-dept employees earning 50–64k, with a `monthly` column, sorted by dept then salary desc — in one chain.
2. Explain why `emp.withColumn(...)` doesn't change `emp`.
3. Explain when `collect()` is safe.

Next: controlling types and structure → [03 — Schemas & Data Types](03_Schemas_and_Data_Types.md).
