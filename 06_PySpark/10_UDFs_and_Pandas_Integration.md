# 10 — UDFs & Pandas Integration

> Prev: [Complex Types & JSON](09_Complex_Types_and_JSON.md) · Next: [Spark SQL & Views](11_Spark_SQL_and_Views.md)

A **UDF (User-Defined Function)** runs your Python inside Spark's engine. It's the escape hatch when [built-ins](05_Column_Operations_and_Functions.md) and [higher-order functions](09_Complex_Types_and_JSON.md) genuinely can't express the logic — and it's the most abused performance foot-gun in PySpark. Learn the mechanics *and* the discipline.

---

## Level 1 — Plain Python UDFs

```python
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

def grade(salary: int) -> str:
    if salary is None:       return None       # YOU handle nulls — Spark won't
    if salary >= 65000:      return "A"
    if salary >= 55000:      return "B"
    return "C"

grade_udf = F.udf(grade, StringType())          # must declare the return type
emp.withColumn("grade", grade_udf("salary")).show()

# Decorator form
@F.udf(returnType=StringType())
def grade(salary): ...

# Register for SQL use too
spark.udf.register("grade_sql", grade, StringType())
spark.sql("SELECT grade_sql(salary) FROM emp_view")
```

### What it costs

For every row: serialize the value → ship to a **Python worker process** outside the JVM → run your function → ship back. That's **10–100× slower** than a built-in, and the UDF is a black box to the optimizer — no pushdown through it, breaks whole-stage codegen ([engine internals](What_Is_Apache_Spark.md)). This example UDF should of course be [`F.when` chains](05_Column_Operations_and_Functions.md) — it's shown as mechanics, not as a recommendation.

---

## Level 2 — Pandas UDFs (the fast kind)

**Pandas UDFs (vectorized UDFs)** move data in **Arrow batches**: your function receives whole `pandas.Series`, not single values — typically 5–20× faster than row UDFs, and the only sane choice when you need pandas/scipy/sklearn logic:

```python
import pandas as pd

@F.pandas_udf("double")
def zscore(v: pd.Series) -> pd.Series:          # Series in → Series out, vectorized
    return (v - v.mean()) / v.std()             # careful: per-BATCH stats! see below

emp.withColumn("z", zscore("salary"))
```

⚠ That example has a subtle bug worth learning from: each *batch* computes its own mean — for true group-wise stats use a [window](08_Window_Functions.md) or grouped operations:

```python
# applyInPandas — full pandas DataFrame per GROUP (the powerful one)
def detrend(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf["sales_detrended"] = pdf["sales"] - pdf["sales"].rolling(7, min_periods=1).mean()
    return pdf

result = (daily_sales.groupBy("store")
          .applyInPandas(detrend, schema="store string, date date, sales double, sales_detrended double"))
```

`applyInPandas` = "split-apply-combine with real pandas per group" — the standard bridge for per-group model scoring, forecasting, and any pandas-native algorithm. Each *group* must fit in one executor's memory — that's the contract.

```python
# mapInPandas — batches of the whole DataFrame (no grouping), e.g. batch API calls / model inference
def predict(batches):
    model = load_model()                        # once per partition, not per row!
    for pdf in batches:
        pdf["score"] = model.predict(pdf[features])
        yield pdf
df.mapInPandas(predict, schema=out_schema)
```

---

## Level 3 — Pro corner

### The decision ladder (recite in interviews)

1. **Built-in `F.*` functions / SQL expressions** — always first; the catalog is bigger than you think.
2. **Higher-order functions** for array logic.
3. **`pandas_udf` / `applyInPandas`** — vectorized, for genuinely custom math or pandas-ecosystem libraries.
4. **Row UDF** — last resort; leave a comment justifying it.

Each step down costs performance and optimizer visibility; each step up costs expressiveness. Most "we need a UDF" moments dissolve at step 1 with ten minutes of docs reading.

### Engineering UDFs that survive production

- **Handle nulls first line** — a null crashing your Python throws opaquely from an executor, failing tasks 4 retries deep.
- **Wrong declared return type = silent nulls**, not errors — `udf(f, IntegerType())` returning a float nulls out. Test the round-trip.
- **Expensive setup goes outside the per-row path**: initialize models/regex/compiled objects once per partition (mapInPandas generator pattern above, or `functools.lru_cache`), never per call.
- **Everything the closure captures ships to workers** — a UDF referencing a 2 GB dict pickles it into every task; broadcast big lookup structures instead: `bc = spark.sparkContext.broadcast(big_dict)`, then `bc.value` inside.
- **Nondeterministic UDFs** (random, time, API calls) can run more than once per row (retries, speculative execution) — mark `.asNondeterministic()` and design [idempotently](../04_ETL_ELT/01_ETL_vs_ELT.md).
- Photon does **not** accelerate Python UDFs — UDF-heavy jobs on Photon clusters pay premium DBUs for nothing ([cost note](Why_Spark_Why_Databricks.md)).

### toPandas / createDataFrame — the other pandas bridge

```python
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)   # on by default in Databricks
small_pdf = big_df.filter(...).groupBy(...).agg(...).toPandas()      # AGGREGATE FIRST — lands on driver!
back = spark.createDataFrame(small_pdf)
```

`toPandas()` is [collect() in a suit](02_DataFrame_Basics.md) — reduce to thousands of rows first. For "pandas API at scale" there's also `pyspark.pandas` (`import pyspark.pandas as ps`) — pandas syntax over Spark execution; handy for porting code, but native DataFrame API remains the professional default (fewer semantic surprises, e.g. ordering and index behavior).

## Checkpoint

1. Standardize product names with a custom fuzzy-match against a 50k-row reference list — which mechanism, and where does the reference data live?
2. Why did `@F.udf(IntegerType())` over a function returning `np.float64` produce all nulls?
3. Score 2B rows with a sklearn model — sketch the mapInPandas solution and its memory contract.

Next: mixing SQL with DataFrames → [11 — Spark SQL & Views](11_Spark_SQL_and_Views.md).

---

## Further Learning — Docs & Videos

**Documentation**
- PySpark UDFs: https://spark.apache.org/docs/latest/api/python/user_guide/sql/udf.html
- Pandas UDFs (vectorized): https://spark.apache.org/docs/latest/api/python/user_guide/sql/arrow_pandas.html

**Videos**
- PySpark UDF vs Pandas UDF explained: https://www.youtube.com/results?search_query=pyspark+udf+vs+pandas+udf+explained
