# 11 — Spark SQL & Views

> Prev: [UDFs & Pandas](10_UDFs_and_Pandas_Integration.md) · Next: [Delta Lake](12_Delta_Lake_with_PySpark.md)

Everything in this series has a SQL spelling. `spark.sql("...")` and the DataFrame API compile to the **same plans** through the same optimizer ([Catalyst](What_Is_Apache_Spark.md)) — so the choice is readability and team skills, never performance. Your [entire 01_SQL folder](../../02_Databases/SQL/01_What_is_SQL.md) applies verbatim here.

---

## Level 1 — Bridging the two worlds

```python
# DataFrame → SQL: register a temporary view
emp.createOrReplaceTempView("emp")

result = spark.sql("""
    SELECT dept, AVG(salary) AS avg_salary
    FROM emp
    WHERE salary > 50000
    GROUP BY dept
    HAVING AVG(salary) > 55000
""")                                   # result is a normal DataFrame!

# ...and straight back to DataFrame API
result.filter(F.col("avg_salary") > 60000).show()
```

- **Temp view** — session-scoped name for a DataFrame; vanishes with the session; no data copied (it's a named [plan, like a SQL view](../../02_Databases/SQL/10_SQL_Views.md)).
- `createOrReplaceGlobalTempView("x")` — visible across sessions on the cluster as `global_temp.x` (rarely needed).
- Parameterized queries (Spark 3.4+): `spark.sql("SELECT * FROM emp WHERE dept = :d", args={"d": "IT"})` — prefer over f-strings ([injection](../../02_Databases/SQL/01_What_is_SQL.md), even in notebooks).

## Level 1 — Tables vs views vs files

```python
spark.sql("SELECT * FROM samples.tpch.orders")     # catalog table (persistent, governed)
spark.read.table("silver.sales")                   # same thing, DataFrame spelling
df.write.saveAsTable("silver.sales_new")           # create a catalog table
spark.sql("SELECT * FROM delta.`abfss://.../path`") # query a path directly, no registration
```

| Thing | Lives | Scope |
|---|---|---|
| Temp view | Session memory (a plan) | Your session |
| Catalog table | Storage + metastore/Unity Catalog | Everyone, governed |
| Path | Storage only | Whoever knows the path |

Production data belongs in **catalog tables** — names, permissions ([UC grants](../../02_Databases/SQL/12_SQL_DCL_TCL.md)), lineage; paths are for landing zones and plumbing.

---

## Level 2 — Working style: when SQL, when DataFrames

The pragmatic split most teams converge on:

- **SQL shines**: multi-join business logic reviewed by SQL-fluent analysts, gold-layer transformations (this is dbt's whole thesis — [ELT's T](../../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md)), ad-hoc exploration, anything a stakeholder must be able to read.
- **DataFrame API shines**: dynamic/parameterized logic (loops over configs — [metaprogramming](05_Column_Operations_and_Functions.md)), reusable tested functions, complex conditional pipelines, anything where Python's abstraction beats string concatenation.
- **Mixing is normal and free**: SQL for the readable core, DataFrame steps before/after. A common production shape:

```python
def clean(df):            # tested Python function, DataFrame in/out
    ...
clean(spark.read.table("bronze.orders")).createOrReplaceTempView("orders_clean")
gold = spark.sql(open("sql/daily_revenue.sql").read())     # reviewed SQL file in git
```

The anti-pattern is *building SQL strings with f-string logic* — the moment SQL needs `if`/loops, switch that part to the DataFrame API instead of templating strings.

### Catalog introspection

```python
spark.catalog.listTables("silver")
spark.catalog.listColumns("silver.sales")
spark.sql("DESCRIBE EXTENDED silver.sales").show(truncate=False)
spark.sql("SHOW PARTITIONS silver.sales")
```

---

## Level 3 — Pro corner

- **Three-level namespace** on Databricks: `catalog.schema.table` (Unity Catalog). Set defaults per session (`USE CATALOG dev; USE SCHEMA silver;`) and write code that takes catalog/schema as **parameters** — the same job must run against dev and prod namespaces unchanged ([environments](14_Performance_and_Best_Practices.md)).
- **Temp views are lazy plans, not materialized results**: referencing one five times re-runs its plan five times (same as [CTEs](../../02_Databases/SQL/09_SQL_Subqueries.md)). If an expensive intermediate is reused, `.cache()` the DataFrame or write a staging table — the view alone saves nothing.
- **Persistent SQL views** (`CREATE VIEW silver.v AS ...`) live in the catalog over tables — same [contract-layer role](../../02_Databases/SQL/10_SQL_Views.md) as warehouse views (gold views over silver Delta is the standard serving pattern), same discipline: explicit columns, no view-on-view lasagna.
- **Spark SQL dialect notes** for people arriving from T-SQL: `LIMIT` not `TOP`; backticks not brackets for identifiers; `!=` and `<=>` (null-safe equals); rich extras — `QUALIFY`, `GROUP BY ALL`, lambda HOFs in SQL (`transform(items, x -> x.qty)`), `TABLESAMPLE`. And Delta extensions: `MERGE`, `TIME TRAVEL (VERSION AS OF)`, `OPTIMIZE` ([next file](12_Delta_Lake_with_PySpark.md)).
- **`EXPLAIN` works in SQL too** (`EXPLAIN FORMATTED SELECT ...`) — same [plan-reading skill](What_Is_Apache_Spark.md), and the SQL tab of the Spark UI shows executed plans with real row counts.
- **ANSI mode** (default Spark 4 / recent DBRs): overflow and bad casts *error* instead of silently nulling — old SQL that "worked" may start failing honestly; `try_cast`/`try_divide` are the intentional-leniency spellings ([casting discipline](03_Schemas_and_Data_Types.md)).

## Checkpoint

1. Register bronze orders as a view, write the dedupe-latest-per-key as SQL (window + QUALIFY), and hand the result back to Python.
2. When would you *not* put logic in SQL? Give two concrete cases.
3. Why doesn't a temp view make anything faster?

Next: the table format everything runs on → [12 — Delta Lake with PySpark](12_Delta_Lake_with_PySpark.md).

---

## Further Learning — Docs & Videos

**Documentation**
- Spark SQL guide: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Getting started with Spark SQL: https://spark.apache.org/docs/latest/sql-getting-started.html

**Videos**
- Spark SQL and temp views explained: https://www.youtube.com/results?search_query=spark+sql+temp+view+global+temp+view
