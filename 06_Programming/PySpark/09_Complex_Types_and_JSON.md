# 09 — Complex Types & JSON

> Prev: [Window Functions](08_Window_Functions.md) · Next: [UDFs & Pandas](10_UDFs_and_Pandas_Integration.md)

Real-world data is nested — API payloads, event streams, order-with-line-items documents ([JSON background](../../04_Storage_and_Formats/File_Formats/02_JSON.md)). PySpark handles nesting natively with three types: **struct** (named fields), **array** (ordered list), **map** (key→value).

```python
order = spark.read.json(sc.parallelize(['''
{"order_id": 501, "customer": {"id": 7, "city": "Hyderabad"},
 "items": [{"sku": "A1", "qty": 2, "price": 250.0},
           {"sku": "B9", "qty": 1, "price": 900.0}],
 "tags": ["priority", "gift"]}''']))
order.printSchema()
# order_id: long
# customer: struct<id:long, city:string>
# items: array<struct<sku:string, qty:long, price:double>>
# tags: array<string>
```

---

## Level 1 — Navigating nesting

```python
# Structs: dot paths
order.select("order_id", "customer.city")                     # flattens to a 'city' column
order.select(F.col("customer.id").alias("cust_id"))

# Arrays: index, size, membership
order.select(F.col("items")[0].alias("first_item"))
order.select(F.size("items"), F.array_contains("tags", "gift"))

# Explode: array → one row per element (grain change!)
lines = (order
    .select("order_id", F.col("customer.id").alias("cust_id"),
            F.explode("items").alias("item"))
    .select("order_id", "cust_id", "item.sku", "item.qty", "item.price"))
# order 501 → 2 rows, one per line item
```

`explode` drops rows whose array is null/empty; **`explode_outer`** keeps them (null item fields) — the left-join-vs-inner-join of arrays. `posexplode` adds the element's position.

### Building nested structures (the write direction)

```python
flat.select(
    "order_id",
    F.struct("cust_id", "city").alias("customer"),
    F.collect_list(F.struct("sku", "qty")).over(...)          # or via groupBy.agg
)
F.array(F.lit("a"), F.lit("b"))
F.create_map(F.lit("k"), F.col("v"))
```

`groupBy().agg(F.collect_list(F.struct(...)))` is the standard "re-nest line items under their order" move — the inverse of explode.

---

## Level 2 — JSON in columns (the Kafka/Event Hubs reality)

Streams deliver JSON as **strings**; you parse them in-flight:

```python
from pyspark.sql.types import *

payload_schema = StructType([
    StructField("event", StringType()),
    StructField("user_id", LongType()),
    StructField("props", MapType(StringType(), StringType())),
])

events = raw.withColumn("data", F.from_json(F.col("value").cast("string"), payload_schema))
            .select("data.*")                      # struct → top-level columns

# The reverse — serialize for output:
df.withColumn("json_out", F.to_json(F.struct("*")))

# Light-touch extraction without full schemas:
df.withColumn("os", F.get_json_object("payload", "$.device.os"))    # JSONPath, returns string
df.select(F.json_tuple("payload", "event", "user_id"))              # several fields at once
```

`from_json` + explicit schema is the production path (typed, fast); `get_json_object` is for exploration or grabbing one field from an otherwise-opaque blob. Rows that don't match the schema become null structs — instrument that like a [failed cast](03_Schemas_and_Data_Types.md).

### Map columns

```python
df.select(F.col("props")["experiment"])            # value by key
df.select(F.explode("props"))                      # → key, value rows
df.select(F.map_keys("props"), F.map_values("props"))
```

Maps are for *unpredictable* key sets; if keys are known and stable, structs are better (columnar pruning works per-field on structs, not on map values).

---

## Level 3 — Pro corner

### Higher-order functions — loops over arrays without exploding

Exploding, transforming, and re-collecting is expensive and grain-risky. HOFs run lambdas *inside* the array, per row:

```python
order.withColumn("line_totals", F.transform("items", lambda x: x.qty * x.price))
order.withColumn("total",       F.aggregate("items", F.lit(0.0),
                                            lambda acc, x: acc + x.qty * x.price))
order.withColumn("big_items",   F.filter("items", lambda x: x.price > 500))
order.withColumn("has_bulk",    F.exists("items", lambda x: x.qty >= 10))
F.zip_with, F.sort_array, F.array_distinct, F.flatten, F.arrays_zip   # the supporting cast
```

These run at engine speed — reach for them before explode/collect and *long* before a [UDF](10_UDFs_and_Pandas_Integration.md).

### Flattening strategy for deep schemas

For a 6-level-deep API payload, don't hand-write 40 selects — flatten programmatically (recursively walk `df.schema`, aliasing `a.b.c` → `a_b_c`), but **flatten to a declared depth, deliberately**: full auto-flattening of everything creates thousand-column tables nobody asked for ([gotcha](../../04_Storage_and_Formats/File_Formats/02_JSON.md)). Standard shape: promote the hot fields to columns, keep the remainder as one struct/variant column.

### VARIANT and schema drift

Databricks' `VARIANT` type (DBR 15+) stores JSON semi-parsed with path access (`payload:device.os`) — the [hybrid pattern](../../02_Databases/SQL/03_SQL_Data_Types.md): typed hot columns + variant long-tail, immune to producer drift. With files, Auto Loader's `schemaHints`/evolution handles additive drift at ingest ([reading file](04_Reading_and_Writing_Data.md)).

### Field-tested notes

- **Explode multiplies data** — a 1M-order table with 50-item arrays becomes 50M rows *before* your filter; filter/transform inside the array (HOFs) first, explode last, at the smallest possible width.
- **Two explodes in one select = accidental cross join** per row (items × tags) — explode one array at a time, or think hard about whether you mean the cartesian.
- Dots in *actual column names* (not struct paths) need backticks: ``F.col("`weird.name`")`` — a recurring confusion with flattened data.
- `select("data.*")` on a null struct produces all-null columns silently — count null structs after `from_json` as your parse-failure metric.
- Deep `getField` chains on structs are pruned efficiently by Parquet (nested column pruning) — but only if you *select paths*, not the whole struct then Python-side access.

## Checkpoint

1. From the `order` example: one row per line item with order_id, city, sku, line_total — nulls preserved for itemless orders.
2. Compute each order's total *without* exploding.
3. Parse a Kafka `value` JSON string into typed columns and count unparseable rows.

Next: when built-ins genuinely run out → [10 — UDFs & Pandas Integration](10_UDFs_and_Pandas_Integration.md).

---

## Further Learning — Docs & Videos

**Documentation**
- Complex types (array/map/struct): https://spark.apache.org/docs/latest/sql-ref-datatypes.html
- explode / from_json functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html

**Videos**
- PySpark explode, struct, from_json: https://www.youtube.com/results?search_query=pyspark+explode+struct+from_json+nested+data
