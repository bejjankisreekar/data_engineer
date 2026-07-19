# 01 — Getting Started & the SparkSession

> Series: [PySpark Learning Path](00_PySpark_Learning_Path.md) · Next: [DataFrame Basics](02_DataFrame_Basics.md)

## What is PySpark?

**PySpark = the Python API for Apache Spark.** You write Python; Spark turns it into a distributed execution plan that runs across a cluster ([how, exactly](What_Is_Apache_Spark.md)). Your Python code *builds the plan* — the heavy lifting happens in Spark's JVM engine, which is why PySpark DataFrame code is just as fast as Scala.

---

## Level 1 — Running PySpark (pick one)

### Option A: Local machine (learning)

```bash
pip install pyspark          # needs Java 11/17 installed (JAVA_HOME set)
```

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
         .appName("learning")
         .master("local[*]")        # run locally, use all CPU cores
         .getOrCreate())

df = spark.range(5)                 # tiny test DataFrame: numbers 0-4
df.show()
```

`local[*]` means "pretend this machine is a cluster" — perfect for learning; every concept transfers unchanged to a real cluster.

### Option B: Databricks / Fabric notebook (the job environment)

Nothing to install — a `spark` session **already exists** in every notebook. You never call `.builder` there; just use `spark` directly. (Databricks Community Edition is free and the easiest zero-setup practice environment.)

### Option C: `spark-submit` (production jobs)

```bash
spark-submit --master <cluster> my_job.py
```

How standalone scripts reach a cluster — covered properly in [file 14](14_Performance_and_Best_Practices.md).

---

## Level 2 — Understanding the SparkSession

The `SparkSession` is your **handle to the whole engine**: it holds the connection to the cluster, the configuration, and the catalog of tables.

```python
spark.version                          # e.g. '3.5.1'
spark.sparkContext.defaultParallelism # how many cores Spark sees

# Configuration — read and set
spark.conf.get("spark.sql.shuffle.partitions")     # '200' default
spark.conf.set("spark.sql.session.timeZone", "UTC")

# The catalog — what tables/views exist
spark.catalog.listDatabases()
```

Things worth knowing immediately:

- **One session per application.** `getOrCreate()` returns the existing one if it exists — calling it twice doesn't make two clusters.
- Everything you do starts from `spark.`: `spark.read...`, `spark.sql(...)`, `spark.createDataFrame(...)`, `spark.range(...)`.
- The session lives on the **driver** ([architecture](Spark_Architecture.md)); closing your notebook/script ends the application.

### Your first real program

```python
data = [("Asha", "IT", 60000), ("Ravi", "HR", 50000), ("Meena", "IT", 65000)]
df = spark.createDataFrame(data, ["name", "dept", "salary"])

df.show()
# +-----+----+------+
# | name|dept|salary|
# +-----+----+------+
# | Asha|  IT| 60000|
# ...

df.filter(df.salary > 55000).show()          # nothing ran until .show() — lazy!
```

That laziness is the single most important behavior to internalize: **transformations describe, actions execute** ([why](Spark_Processing.md)).

---

## Level 3 — Pro corner

- **SparkSession vs SparkContext**: `SparkContext` (`spark.sparkContext`) is the older, lower-level entry point (RDDs); `SparkSession` wraps it plus SQL/catalog. New code touches SparkContext almost never.
- **Spark Connect** (Spark 3.4+/Databricks serverless): your Python process becomes a thin client speaking gRPC to a remote driver — same API, but `sparkContext` and some RDD APIs are unavailable. If a notebook errors on `sparkContext`, you're probably on serverless.
- **Configs have three timings**: cluster-startup configs (executor memory — can't change in session), session configs (`spark.conf.set` — shuffle partitions, timezone), and per-operation options. Setting a startup config from a notebook silently does nothing — a classic confusion.
- **Set the timezone explicitly** (`spark.sql.session.timeZone`) in every production job — timestamp bugs from inherited cluster timezones are endemic ([why](../01_SQL/03_SQL_Data_Types.md)).
- Local `local[*]` uses threads, not processes — some cluster-only behaviors (serialization bugs, real shuffles across machines) won't reproduce locally. "Works on my laptop" is necessary, not sufficient ([testing](14_Performance_and_Best_Practices.md)).

## Checkpoint — you should now be able to

1. Start (or locate) a SparkSession in your environment.
2. Explain why `df.filter(...)` alone does nothing.
3. Create a small DataFrame from a Python list and show it.

Next: the operations you'll use every single day → [02 — DataFrame Basics](02_DataFrame_Basics.md).
