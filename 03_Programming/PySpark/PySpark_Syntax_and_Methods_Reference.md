# PySpark Syntax & Methods Reference

A practical, **heading-by-heading** guide: how to **read data from every file format**, how to **write it back**, and how to do **every common transformation** (filter, select, join, groupBy, window, …) — each with a short explanation, the syntax, and a runnable snippet. The numbered notes ([02 DataFrames](02_DataFrame_Basics.md) → [09 Complex Types](09_Complex_Types_and_JSON.md)) teach these in depth; this file is the fast look-up.

```python
from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import *
spark = SparkSession.builder.getOrCreate()   # on Databricks, `spark` already exists
```

> Every reader follows the same shape: `spark.read.format(<fmt>).option(<k>, <v>).load(<path>)`. The `.csv()`, `.json()`, `.parquet()` … methods are just shortcuts for it.

---

# Reading data

## How to read data from CSV

CSV is plain text with one row per line and values separated by a delimiter. It has **no built-in schema**, so you must tell Spark whether the first line is a header and what the column types are. In production **always pass an explicit schema** instead of `inferSchema` (which secretly scans the file twice and can guess types differently on different days).

```python
df = (spark.read
      .option("header", True)          # first row holds column names
      .option("sep", ",")              # delimiter — use "\t" for TSV
      .option("inferSchema", True)     # guess types (dev only; slow)
      .csv("/path/to/file.csv"))

# production version — explicit schema, no inference:
schema = "id INT, name STRING, amount DECIMAL(12,2), order_date DATE"
df = spark.read.option("header", True).schema(schema).csv("/path/*.csv")
```

**Options you'll actually use:**

| Option | What it does |
|---|---|
| `header` | `True` = first row is column names |
| `sep` | field delimiter (`,`, `;`, `\t`, `|`) |
| `inferSchema` | scan data to guess types (avoid in prod) |
| `schema` | supply types yourself (preferred) |
| `multiLine` | `True` if a field contains newlines |
| `quote` / `escape` | the quote char and how quotes inside a field are escaped |
| `nullValue` | string that means null (e.g. `"NA"`) |
| `dateFormat` / `timestampFormat` | how dates are written in the file |
| `mode` | bad-row handling: `PERMISSIVE` (default), `DROPMALFORMED`, `FAILFAST` |

---

## How to read data from JSON

JSON holds semi-structured, possibly nested data. Spark expects **one JSON object per line** by default (JSON Lines). If your file is a single pretty-printed object or an array spanning multiple lines, set `multiLine=True`. Spark infers a schema from the JSON, but you can pass one to be safe and fast.

```python
# JSON Lines — one object per line (the common big-data form)
df = spark.read.json("/path/to/file.json")

# a single multi-line JSON array or object
df = spark.read.option("multiLine", True).json("/path/to/pretty.json")

# enforce a schema (faster, predictable)
df = spark.read.schema("id INT, name STRING, addr STRUCT<city:STRING>").json(path)
```

Nested fields become **structs/arrays** — flatten them with dot access (`F.col("addr.city")`) and `explode` (see the [Complex Types](#how-to-work-with-nested-data-structs-arrays-json) section below).

---

## How to read data from Parquet

Parquet is a **columnar, compressed** format and the standard for analytics. The schema is **stored inside the file**, so there's nothing to configure — Spark reads types automatically, and it only reads the columns your query needs (column pruning), which makes it far faster than CSV.

```python
df = spark.read.parquet("/path/to/folder/")     # reads all part-*.parquet files
df = spark.read.parquet("/a.parquet", "/b.parquet")   # specific files
```

Because a "Parquet dataset" is usually a **folder** of part-files (one per Spark partition), you point at the folder, not a single file.

---

## How to read data from ORC

ORC is another **columnar** format (born in the Hadoop/Hive world), similar in spirit to Parquet. Like Parquet it carries its own schema, so reading needs no options.

```python
df = spark.read.orc("/path/to/folder/")
```

Use Parquet by default in the Azure/Databricks world; you'll meet ORC mainly with existing Hive tables.

---

## How to read data from Avro

Avro is a **row-based** format built for fast writes and schema evolution (common as the on-the-wire format for Kafka/Event Hubs). It needs the `spark-avro` package (bundled in Databricks), so it's read via the generic `.format("avro")`.

```python
df = spark.read.format("avro").load("/path/to/folder/")
```

Rule of thumb: **Avro for streaming/ingest** (write-heavy), **Parquet for analytics** (read-heavy).

---

## How to read data from Delta

Delta is Parquet **plus a transaction log** — it gives you ACID, updates/deletes, and time travel. On Databricks it's the default table format. You can read it by **path** or by its **catalog name**, and you can read an **older version** of the table.

```python
df = spark.read.format("delta").load("/path/to/delta")       # by path
df = spark.read.table("catalog.schema.table")                # by Unity Catalog name

# time travel — read the table as it was earlier
df = spark.read.format("delta").option("versionAsOf", 5).load(path)
df = spark.read.format("delta").option("timestampAsOf", "2026-08-01").load(path)
```

See [12 — Delta Lake with PySpark](12_Delta_Lake_with_PySpark.md).

---

## How to read data from a text file

Reads raw lines with **no parsing** — one row per line in a single column called `value`. Useful for logs or custom formats you'll parse yourself with string functions.

```python
df = spark.read.text("/path/")                         # column "value", one row per line
df = spark.read.option("wholetext", True).text(path)   # whole file as ONE row
```

---

## How to read data from a database (JDBC)

Use JDBC to pull from relational databases (Azure SQL, PostgreSQL, MySQL…). Give it the connection URL, the table (or a query), and credentials. For big tables, add the **partitioning options** so the read is split across executors instead of pulled on a single connection.

```python
df = (spark.read.format("jdbc")
      .option("url", "jdbc:sqlserver://host:1433;database=db")
      .option("dbtable", "dbo.orders")           # or .option("query", "SELECT ... WHERE ...")
      .option("user", user).option("password", pwd)
      # parallel read — splits id 1..1,000,000 into 8 chunks:
      .option("partitionColumn", "id")
      .option("lowerBound", 1).option("upperBound", 1000000)
      .option("numPartitions", 8)
      .load())
```

Never hard-code the password — pull it from a **secret scope / Key Vault**.

---

## How to read many files, folders, or partitioned data

Real pipelines rarely read one file. You can pass a **list**, a **glob**, or turn on **recursive** lookup; and when data is laid out in `col=value` folders, Spark can recover those as columns.

```python
spark.read.csv(["/a.csv", "/b.csv"])                          # a list of paths
spark.read.parquet("/data/year=2026/month=*/")                # glob pattern
spark.read.option("recursiveFileLookup", True).parquet("/data/")   # walk sub-folders
spark.read.option("pathGlobFilter", "*.csv").text("/data/")   # filter by file name

# partition-discovery: /data/year=2026/... keeps `year` as a column
spark.read.option("basePath", "/data/").parquet("/data/year=2026/")

df.withColumn("_source_file", F.input_file_name())            # track where each row came from
```

---

# Writing data

## How to write a DataFrame out

Writing mirrors reading: pick a `format`, a **save mode** (what to do if the target exists), and options like `partitionBy`. Delta is the default on Databricks.

```python
(df.write
   .format("delta")                 # delta | parquet | csv | json | orc | avro
   .mode("overwrite")               # see table below
   .option("header", True)          # format-specific options (e.g. CSV header)
   .partitionBy("year", "month")    # physical folder partitioning for pruning
   .save("/path/out"))

df.write.saveAsTable("catalog.schema.table")                 # register in the catalog
df.write.format("delta").option("overwriteSchema", True).mode("overwrite").save(p)
df.coalesce(1).write.mode("overwrite").csv("/out")           # single file (small data only)
```

| Save mode | If data already exists |
|---|---|
| `error` / `errorifexists` (default) | throw an error |
| `append` | add the new rows |
| `overwrite` | replace everything |
| `ignore` | silently skip the write |

---

# Transformations

> Transformations are **lazy** — they build a plan and run nothing until an **action** (`show`, `count`, `write`, `collect`) triggers the job. So you chain them freely and Spark optimizes the whole chain at the end.

## How to look at a DataFrame (actions)

Before transforming, these let you inspect data and shape. Note these are **actions** (they run the job).

```python
df.show(20, truncate=False)     # print rows at full width
df.printSchema()                # column names + types as a tree
df.count()                      # number of rows
df.columns ; df.dtypes          # names ; (name, type) pairs
df.describe().show()            # count/mean/stddev/min/max for numeric columns
df.limit(100).collect()         # pull rows to the driver — ALWAYS bound with limit first
```

## How to select columns

Pick or compute the columns you want. There are four ways to name a column — `"c"`, `df.c`, `df["c"]`, `F.col("c")` — use `F.col()` when you need to apply functions.

```python
df.select("id", "name")
df.select(F.col("amount").alias("amt"))                       # rename in place
df.select("*", (F.col("qty") * F.col("price")).alias("total"))  # keep all + add one
df.selectExpr("id", "amount * 1.1 AS amount_with_tax")        # SQL-string expressions
```

## How to filter rows (`filter` / `where`)

`filter` and `where` are the same. Combine conditions with `&` (and), `|` (or), `~` (not) — and **wrap each condition in parentheses**, or Python's operator precedence will break it.

```python
df.filter(F.col("amount") > 100)
df.where("amount > 100 AND region = 'WEST'")                  # SQL-string form
df.filter((F.col("amount") > 100) & (F.col("region") == "WEST"))   # AND (note parens!)
df.filter((F.col("status") == "A") | (F.col("status") == "B"))     # OR

df.filter(F.col("region").isin("WEST", "EAST"))               # IN
df.filter(F.col("amount").between(10, 100))                   # inclusive range
df.filter(F.col("name").like("A%"))                           # SQL LIKE (% and _)
df.filter(F.col("name").rlike("^A.*z$"))                      # regex
df.filter(F.col("name").contains("mith"))
df.filter(F.col("email").isNull())                            # or .isNotNull()
```

## How to add, rename, and drop columns

```python
df.withColumn("total", F.col("qty") * F.col("price"))         # add or replace a column
df.withColumnRenamed("old_name", "new_name")
df.drop("col1", "col2")                                       # remove columns
df.withColumn("amount", F.col("amount").cast("double"))       # change a column's type
```

## How to transform column values (functions)

Import `functions as F` for the toolbox. Prefer these built-ins over UDFs — Spark can optimize them.

```python
# conditional logic
df.withColumn("grade", F.when(F.col("score") >= 90, "A")
                        .when(F.col("score") >= 80, "B")
                        .otherwise("C"))
F.coalesce("phone", "mobile", F.lit("unknown"))               # first non-null

# strings
F.upper(c) ; F.lower(c) ; F.trim(c) ; F.length(c)
F.concat_ws("-", "year", "month", "day")                      # join with separator
F.substring("name", 1, 3)                                     # (start is 1-indexed, length)
F.split("csv", ",")                                           # -> array
F.regexp_replace("phone", "[^0-9]", "")                       # strip non-digits
F.regexp_extract("email", r"@(.+)$", 1)                       # capture group

# dates
F.to_date("s", "yyyy-MM-dd") ; F.to_timestamp("s")
F.date_format("ts", "yyyy-MM")
F.year(c) ; F.month(c) ; F.dayofmonth(c)
F.datediff("end", "start") ; F.date_add("d", 7) ; F.add_months("d", 3)

# numbers
F.round("x", 2) ; F.ceil("x") ; F.floor("x") ; F.abs("x")
```

## How to handle nulls

```python
df.na.drop()                          # drop rows with ANY null
df.na.drop(subset=["email"])          # drop where email is null
df.na.fill(0)                         # fill numeric nulls with 0
df.na.fill({"email": "n/a", "amount": 0})
df.na.replace(["", "N/A"], None)      # replace bad values with null
```

## How to remove duplicates

```python
df.distinct()                         # unique whole rows
df.dropDuplicates(["email"])          # unique by a subset (keeps an ARBITRARY row)
```
To keep a **specific** row per key (e.g. the latest), use a window with `row_number()` — see below.

## How to sort and limit

```python
df.orderBy("amount")                              # ascending
df.orderBy(F.col("amount").desc())                # descending
df.sort(F.col("region").asc(), F.col("amount").desc())   # multi-key
df.limit(10)
```

## How to aggregate and group

`groupBy(...).agg(...)` is the workhorse. Filtering *after* aggregation is the SQL `HAVING`.

```python
df.groupBy("region").count()
df.groupBy("region").agg(
    F.sum("amount").alias("total"),
    F.avg("amount").alias("avg_amt"),
    F.countDistinct("customer_id").alias("customers"),
    F.collect_set("product").alias("distinct_products"),
)
df.agg(F.sum("amount"))                                        # whole-DF aggregate, no group
df.groupBy("region").pivot("year").sum("amount")              # pivot years into columns
df.groupBy("region").agg(F.sum("amount").alias("t")).filter("t > 1000")   # HAVING
```

## How to join DataFrames

```python
a.join(b, on="id", how="inner")                               # single shared key
a.join(b, on=["id", "region"], how="left")                    # multiple keys
a.join(b, a.id == b.cust_id, how="inner")                     # explicit condition
a.join(F.broadcast(dim), "id", "left")                        # broadcast the small side (no shuffle)
```

| `how` | Keeps |
|---|---|
| `inner` (default) | only matching rows |
| `left` / `right` / `outer` | all of one/other/both sides, nulls where no match |
| `left_semi` | left rows that **have** a match (no right columns) |
| `left_anti` | left rows with **no** match — perfect for "what's missing" |
| `cross` | Cartesian product |

Joining on `a.id == b.id` leaves two `id` columns; join `on="id"` (string) to keep just one.

## How to use window functions

Windows compute across a group of rows **without collapsing them** (ranking, running totals, previous-row lookups). Define a `Window`, then apply a function `.over(w)`.

```python
w = Window.partitionBy("region").orderBy(F.col("amount").desc())

df.withColumn("rn",   F.row_number().over(w))     # 1,2,3 — unique
df.withColumn("rank", F.rank().over(w))           # 1,1,3 — ties share, gaps
df.withColumn("prev", F.lag("amount", 1).over(w)) # previous row's value

# running total (frame = start of partition to current row)
wr = Window.partitionBy("region").orderBy("date").rowsBetween(Window.unboundedPreceding, 0)
df.withColumn("running_total", F.sum("amount").over(wr))

# keep only the latest row per key (the dedupe pattern)
w2 = Window.partitionBy("order_id").orderBy(F.col("_ingest_ts").desc())
df.withColumn("_rn", F.row_number().over(w2)).filter("_rn = 1").drop("_rn")
```

## How to work with nested data (structs, arrays, JSON)

```python
F.col("addr.city")                         # read a struct field with dot notation
F.col("tags")[0]                           # array element by index
df.select("id", F.explode("tags").alias("tag"))    # array -> one row per element
df.withColumn("parsed", F.from_json("json_str", "id INT, name STRING"))   # JSON string -> struct
df.withColumn("json_str", F.to_json(F.struct("id", "name")))              # struct -> JSON string
F.size("tags") ; F.array_contains("tags", "x")
```
See [09 — Complex Types & JSON](09_Complex_Types_and_JSON.md).

## How to combine DataFrames (set operations)

```python
a.unionByName(b)               # stack rows, matching by column NAME (safer than union)
a.union(b)                     # stack rows by column POSITION
a.intersect(b)                 # rows in both
a.exceptAll(b)                 # rows in a not in b
```

## How to run SQL instead

The DataFrame API and SQL compile to the **same** plan — mix freely.

```python
df.createOrReplaceTempView("orders")
spark.sql("SELECT region, SUM(amount) FROM orders GROUP BY region").show()
```

## How to write your own function (UDF) — last resort

Only when no built-in `F.*` exists. Plain Python UDFs are slow (row-by-row); prefer a vectorized `pandas_udf`.

```python
from pyspark.sql.functions import udf, pandas_udf
@udf("string")
def clean(s): return s.strip().upper() if s else None
df.withColumn("c", clean("name"))

@pandas_udf("double")                       # vectorized — much faster
def scale(x): return x * 1.1
df.withColumn("y", scale("amount"))
```

---

## Transformations vs actions (why nothing runs until it does)

| Transformations (lazy — build the plan) | Actions (trigger execution) |
|---|---|
| `select`, `filter`/`where`, `withColumn`, `drop` | `show`, `count`, `collect`, `take`, `first` |
| `groupBy().agg`, `join`, `orderBy`, `distinct` | `write.*`, `save`, `saveAsTable` |
| `union`, `repartition`, `withColumnRenamed` | `toPandas`, `describe`, `foreach` |

`df.filter(...).select(...)` does no work until you call `.show()` or `.write`. See [Spark Processing](Spark_Processing.md).

## Everyday gotchas

- **`&` / `|` need parentheses**: `df.filter((a > 1) & (b < 2))`.
- **`==`, not `=`**, for equality.
- **`inferSchema` is slow and unstable** — declare a schema in production.
- **`collect()` / `toPandas()` pull everything to the driver** — bound with `.limit()` first.
- **`join` on `a.id == b.id`** duplicates the key column — join `on="id"` instead.
- **`dropDuplicates(["k"])` keeps an arbitrary row** — use a window + `row_number()` to choose which.
- **A "Parquet/Delta file" is usually a folder** of part-files — point at the folder.

---

## Related notes
- Deep-dives: [02 DataFrames](02_DataFrame_Basics.md) · [03 Schemas](03_Schemas_and_Data_Types.md) · [04 Read/Write](04_Reading_and_Writing_Data.md) · [05 Columns & Functions](05_Column_Operations_and_Functions.md) · [06 Aggregations](06_Aggregations_and_Grouping.md) · [07 Joins](07_Joins.md) · [08 Windows](08_Window_Functions.md) · [09 Complex Types](09_Complex_Types_and_JSON.md)
- Concepts: [Spark Processing](Spark_Processing.md) (lazy eval, shuffles) · [14 Performance](14_Performance_and_Best_Practices.md)
- Q&A: [PySpark Interview Questions & Answers](Interview_Questions_and_Answers.md)
