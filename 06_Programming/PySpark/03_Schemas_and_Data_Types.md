# 03 — Schemas & Data Types

> Prev: [DataFrame Basics](02_DataFrame_Basics.md) · Next: [Reading & Writing Data](04_Reading_and_Writing_Data.md)

A schema is the DataFrame's contract: column names, types, and nullability. In production PySpark, **you declare schemas; you don't let Spark guess** ([why inference is dangerous](../../04_Storage_and_Formats/File_Formats/01_CSV.md)).

---

## Level 1 — Types and how to see them

```python
emp.printSchema()
# root
#  |-- id: long (nullable = true)
#  |-- name: string (nullable = true)
#  |-- salary: long (nullable = true)

emp.dtypes        # [('id', 'bigint'), ('name', 'string'), ...]
```

The types you'll use constantly (from `pyspark.sql.types`):

| PySpark type | Holds | SQL equivalent |
|---|---|---|
| `StringType()` | text | VARCHAR |
| `IntegerType()` / `LongType()` | 32-bit / 64-bit ints | INT / BIGINT |
| `DoubleType()` / `FloatType()` | floating point | FLOAT |
| `DecimalType(10,2)` | exact decimals — **money** | DECIMAL ([why not float](../../02_Databases/SQL/03_SQL_Data_Types.md)) |
| `BooleanType()` | True/False | BIT/BOOLEAN |
| `DateType()` | date only | DATE |
| `TimestampType()` | date+time (session-timezone-aware) | DATETIME2 |
| `ArrayType`, `MapType`, `StructType` | nested — [file 09](09_Complex_Types_and_JSON.md) | — |

## Level 1 — Casting

```python
emp2 = (emp
  .withColumn("salary", F.col("salary").cast("decimal(10,2)"))
  .withColumn("hire_date", F.to_date("hire_date", "yyyy-MM-dd"))
  .withColumn("id", F.col("id").cast("int")))
```

`cast` accepts type objects or SQL strings (`"int"`, `"decimal(10,2)"`) — the string form is the common idiom. **A failed cast produces `null`, not an error** — that silence is important (see Level 3).

---

## Level 2 — Defining schemas explicitly

### The StructType way (programmatic)

```python
from pyspark.sql.types import (StructType, StructField, StringType,
                               IntegerType, DecimalType, DateType)

emp_schema = StructType([
    StructField("id",        IntegerType(),      nullable=False),
    StructField("name",      StringType(),       nullable=True),
    StructField("dept",      StringType(),       nullable=True),
    StructField("salary",    DecimalType(10, 2), nullable=True),
    StructField("hire_date", DateType(),         nullable=True),
])

df = spark.read.schema(emp_schema).csv("path/", header=True)
```

### The DDL-string way (concise, increasingly preferred)

```python
ddl = "id INT NOT NULL, name STRING, dept STRING, salary DECIMAL(10,2), hire_date DATE"
df = spark.read.schema(ddl).csv("path/", header=True)
```

Both are equivalent; DDL strings read better in review and can be stored in config files. You can convert an existing schema: `df.schema.simpleString()` / and reuse one: `spark.read.schema(other_df.schema)`.

### createDataFrame with a schema

```python
data = [(1, "Asha", "IT")]
spark.createDataFrame(data, schema="id INT, name STRING, dept STRING")
```

Without a schema, Spark infers from the Python objects — fine for tests, never for pipelines.

---

## Level 3 — Pro corner

### Nullability is documentation, not enforcement

`nullable=False` in a schema does **not** make Spark reject nulls on read — it's metadata the optimizer may use. Real enforcement happens at the table layer: Delta `NOT NULL`/`CHECK` constraints ([file 12](12_Delta_Lake_with_PySpark.md)) or explicit validation filters. Don't design as if StructField nullability protects you.

### Silent-null casting — instrument it

```python
# Production casting pattern: cast AND count the casualties
raw_count  = df.count()
typed      = df.withColumn("amount_d", F.col("amount").cast("decimal(18,4)"))
bad        = typed.filter(F.col("amount").isNotNull() & F.col("amount_d").isNull())
# 'bad' rows had values that LOOKED numeric but weren't — quarantine + alert, don't drop silently
```

`try_cast` (Spark 3.4+/Databricks) makes intent explicit; under ANSI mode (Spark 4 default) plain `cast` *errors* instead of nulling — know which behavior your runtime has.

### Dates, timestamps, and the timezone trap

- `TimestampType` values are stored as UTC instants and **rendered in the session timezone** — two notebooks with different `spark.sql.session.timeZone` show different clock times for the same data. Pin it ([session config](01_Getting_Started_SparkSession.md)).
- `TimestampNTZ` (Spark 3.4+) = "no timezone" wall-clock — matches how many databases store DATETIME; use it for round-trips where you don't want conversion.
- Parsing: `F.to_date`/`F.to_timestamp` with an explicit format; without one, unparseable strings → null (same silent-failure discipline as casts).

### Schema drift and evolution

At ingestion boundaries, compare incoming vs expected schema and act deliberately ([drift policy](../../04_Storage_and_Formats/File_Formats/02_JSON.md)):

```python
expected = set(emp_schema.fieldNames())
actual   = set(df.columns)
if actual - expected: ...   # new columns: log/alert, optionally auto-evolve (Delta mergeSchema)
if expected - actual: ...   # missing columns: usually fail-fast
```

Delta's `mergeSchema`/`overwriteSchema` and Auto Loader's schema evolution formalize this at the table layer ([files 04](04_Reading_and_Writing_Data.md) and [12](12_Delta_Lake_with_PySpark.md)).

### Field-tested notes

- **Decimal precision math**: operations widen precision (`DECIMAL(10,2) * DECIMAL(10,2)` → bigger) and can overflow to null at the 38-digit cap — watch multi-step money math; round intermediates deliberately.
- Long chains of Python ints default to `LongType`; JDBC targets expecting INT will need casts on write ([type mapping tax](../../02_Databases/SQL/03_SQL_Data_Types.md)).
- Reuse one schema definition module across jobs (`schemas.py`) — ten jobs each hand-typing the "same" schema *will* drift.

## Checkpoint

1. Write the DDL string for a sales table: sale_id BIGINT, sku STRING, qty INT, price DECIMAL(9,2), sold_at TIMESTAMP.
2. What does a failed cast produce, and how do you catch it in production?
3. Why doesn't `nullable=False` protect you?

Next: getting real data in and out → [04 — Reading & Writing Data](04_Reading_and_Writing_Data.md).

---

## Further Learning — Docs & Videos

**Documentation**
- PySpark data types: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/data_types.html
- Spark SQL data types reference: https://spark.apache.org/docs/latest/sql-ref-datatypes.html

**Videos**
- PySpark schema and StructType explained: https://www.youtube.com/results?search_query=pyspark+schema+structtype+explained
