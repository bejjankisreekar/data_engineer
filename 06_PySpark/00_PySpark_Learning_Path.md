# PySpark Learning Path — Read Me First

This folder teaches **PySpark from zero to pro**. Files are numbered in reading order — each builds on the previous one. Every file has runnable code examples.

## The two tracks in this folder

**Concept track** (the *why* and *how it works inside*) — read alongside the numbered series:

- [What_Is_Apache_Spark.md](What_Is_Apache_Spark.md) — what Spark is, why it exists
- [Spark_Architecture.md](Spark_Architecture.md) — driver, executors, jobs/stages/tasks
- [Spark_Processing.md](Spark_Processing.md) — partitions, lazy evaluation, shuffles
- [Why_Spark_Why_Databricks.md](Why_Spark_Why_Databricks.md) — the business case

**Coding track** (the *how to actually write it*) — the numbered series:

| # | File | You'll learn |
|---|---|---|
| 01 | [Getting_Started_SparkSession](01_Getting_Started_SparkSession.md) | Install, run, and understand your entry point |
| 02 | [DataFrame_Basics](02_DataFrame_Basics.md) | Create, inspect, select, filter, sort — the daily verbs |
| 03 | [Schemas_and_Data_Types](03_Schemas_and_Data_Types.md) | Defining and controlling structure |
| 04 | [Reading_and_Writing_Data](04_Reading_and_Writing_Data.md) | CSV/JSON/Parquet/Delta/JDBC in and out |
| 05 | [Column_Operations_and_Functions](05_Column_Operations_and_Functions.md) | Strings, dates, conditionals, nulls, casting |
| 06 | [Aggregations_and_Grouping](06_Aggregations_and_Grouping.md) | groupBy, agg, pivot, rollup |
| 07 | [Joins](07_Joins.md) | Every join type + broadcast + dedupe patterns |
| 08 | [Window_Functions](08_Window_Functions.md) | Ranking, lag/lead, running totals |
| 09 | [Complex_Types_and_JSON](09_Complex_Types_and_JSON.md) | Arrays, structs, maps, explode, from_json |
| 10 | [UDFs_and_Pandas_Integration](10_UDFs_and_Pandas_Integration.md) | Custom functions and the pandas bridge |
| 11 | [Spark_SQL_and_Views](11_Spark_SQL_and_Views.md) | Mixing SQL and DataFrames |
| 12 | [Delta_Lake_with_PySpark](12_Delta_Lake_with_PySpark.md) | MERGE, time travel, OPTIMIZE |
| 13 | [Structured_Streaming](13_Structured_Streaming.md) | Real-time pipelines |
| 14 | [Performance_and_Best_Practices](14_Performance_and_Best_Practices.md) | Tuning, testing, production habits |
| 15 | [RDDs_The_Foundation](15_RDDs_The_Foundation.md) | The structure underneath DataFrames — map/reduce, lineage, when to still use RDDs |

## Suggested route by experience level

- **Complete beginner**: read [What_Is_Apache_Spark](What_Is_Apache_Spark.md) Part 1, then files 01–08 in order, practicing each. That's a working data engineer's daily toolkit.
- **Know pandas/SQL already**: skim 01–02, read 03–08 properly (the distributed differences hide there), then 09–14.
- **Interview prep**: the concept track fully + files 07, 08, 12, 14, 15 + every "Pro corner" section.

File 15 (RDDs) sits after the main series on purpose — it's the "under the hood" layer, and it lands much better once you've already seen what the DataFrame API abstracts away. If you truly want RDDs first (some courses/certifications teach it that way), it's self-contained and can be read any time after file 01.

## Prerequisites

- Basic Python (variables, functions, lists/dicts, imports)
- Basic SQL ([01_SQL folder](../01_SQL/01_What_is_SQL.md)) — PySpark constantly mirrors SQL concepts
- The [OLTP](../00_Fundamentals/01_OLTP_Storage.md)/[OLAP](../00_Fundamentals/02_OLAP_Storage.md) distinction helps everything make sense

## The sample data used throughout

Most examples in this series use a small `employees` / `departments` / `sales` dataset so you can focus on the operations, not the data. Each file's first code block creates what it needs — every example is copy-paste runnable on a local PySpark or a free Databricks Community / Fabric notebook.

---

## Further Learning — Docs & Videos

**Documentation**
- PySpark documentation: https://spark.apache.org/docs/latest/api/python/index.html
- PySpark getting started: https://spark.apache.org/docs/latest/api/python/getting_started/index.html
- Databricks PySpark guide: https://docs.databricks.com/en/pyspark/index.html

**Videos**
- PySpark full course for beginners: https://www.youtube.com/results?search_query=pyspark+full+course+for+beginners
- PySpark tutorial for data engineers: https://www.youtube.com/results?search_query=pyspark+tutorial+data+engineering
