# 04 — ELT with Spark SQL

*Domain: ELT with Spark SQL and Python (29%) — the largest domain.*

---

## What it is

**ELT** = Extract, **Load**, **Transform**. You *load* raw data into the lakehouse first, then *transform* it in place using the platform's compute — the opposite order from classic ETL (transform before load). Databricks favors ELT because storage is cheap and Spark can transform data efficiently where it already sits.

This file covers doing that transformation with **Spark SQL**. The exam expects you to read and recognize correct SQL for querying files, creating tables/views, cleaning data, and handling nested/semi-structured data.

---

## Querying files directly

You can query files without first creating a table using the `format.`\`path\`` syntax:

```sql
SELECT * FROM json.`/path/to/data.json`;
SELECT * FROM parquet.`/path/to/dir`;
SELECT * FROM csv.`/path/to/file.csv`;
SELECT * FROM text.`/path/to/file`;
SELECT * FROM binaryFile.`/path/to/images`;
```

- Works well for **self-describing formats** (JSON, Parquet) that carry their own schema.
- For CSV (no schema/headers baked in) direct querying is limited — you usually need options, which requires the `read_files` function or an external-table/`USING` definition.

```sql
-- read_files (modern) handles options and directories, incl. CSV with header
SELECT * FROM read_files('/path/data.csv', format => 'csv', header => true);
```

> **Exam Tip:** `SELECT * FROM json.\`/path\`` queries files directly. This is ideal for **quick inspection of self-describing files**. For CSV you typically need explicit options (delimiter/header), so a plain `SELECT * FROM csv.\`...\`` may put everything in one column or mishandle headers.

### `_metadata` / corrupt records

- `SELECT *, _metadata.file_name FROM json.\`/path\`` — access file metadata (source file name, path, size, modification time).
- Adding a `_corrupt_record` column or `input_file_name()` helps trace bad rows to their source file.

---

## Creating tables from files

### CTAS (Create Table As Select)

```sql
CREATE TABLE clean_data AS
SELECT * FROM json.`/path/to/data`;
```

- CTAS **infers schema** from the query and creates a **Delta** table.
- CTAS does **not** support manual schema declaration or file options (delimiter, header). For those, use an **external table with options** first, then CTAS from it.

### External table with options (for CSV etc.)

```sql
CREATE TABLE raw_csv
  (name STRING, age INT)
USING CSV
OPTIONS (header = "true", delimiter = ",")
LOCATION '/path/to/csv';
```

> **Exam Tip:** A table created with `USING CSV` / `USING JSON` and a `LOCATION` is an **external table that points at the files but is *not* Delta** — it does not get Delta's ACID/performance features, and it's not a copy (it reads the files live). To get a *managed Delta* copy you do `CREATE TABLE clean USING DELTA AS SELECT * FROM raw_csv` (CTAS). Recognizing "USING CSV + LOCATION = non-Delta external table" is a common exam point.

---

## Views, Temp Views, and CTEs

| Object | Scope / Lifetime | Persisted? |
|---|---|---|
| **View** (`CREATE VIEW`) | Persisted in the metastore; available across sessions | Definition stored (a saved query); no data stored |
| **Temp View** (`CREATE TEMP VIEW`) | Tied to the **current SparkSession/notebook**; gone when it ends | No |
| **Global Temp View** (`CREATE GLOBAL TEMP VIEW`) | Available to **all sessions on the same cluster**; namespaced under `global_temp` | No |
| **CTE** (`WITH ... AS`) | Exists only within the **single query** it's defined in | No |

```sql
CREATE VIEW active_users AS SELECT * FROM users WHERE active = true;
CREATE TEMP VIEW temp_v AS SELECT * FROM source;
CREATE GLOBAL TEMP VIEW g_v AS SELECT * FROM source;  -- query via global_temp.g_v
WITH cte AS (SELECT * FROM t WHERE x > 0) SELECT count(*) FROM cte;
```

> **Exam Tip:** A **view** stores a query definition, not data — it re-runs each time. A **temp view** lives only for your session/notebook. A **global temp view** is shared across sessions on the same cluster (accessed via the `global_temp` database). A **CTE** exists only inside one statement. Know which survives a cluster restart (only a regular **view**/table — temp views do not).

---

## Cleaning and transforming data

### Deduplication

```sql
SELECT DISTINCT * FROM t;                       -- drop fully duplicate rows
SELECT DISTINCT(user_id) FROM t;                -- distinct on a column
-- dedupe keeping one row per key:
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ts DESC) AS rn
  FROM t
) WHERE rn = 1;
```

### Null handling & validation

```sql
SELECT count(*) FROM t WHERE email IS NULL;      -- count nulls
SELECT coalesce(nickname, name, 'unknown') FROM t;
-- constraint enforcement (Delta):
ALTER TABLE t ADD CONSTRAINT valid_age CHECK (age > 0);
```

> **Exam Tip:** `count(*)` counts all rows including nulls; `count(col)` counts **non-null** values of that column; `count(DISTINCT col)` counts distinct non-null values. Adding a **CHECK constraint** makes Delta reject rows that violate it — a common data-quality mechanism.

### Casting & timestamps

```sql
SELECT CAST(price AS DOUBLE), CAST(ts AS TIMESTAMP) FROM t;
SELECT date_format(ts, 'yyyy-MM-dd'), year(ts), to_date(str_col, 'yyyy-MM-dd') FROM t;
```

---

## Working with nested / semi-structured data (JSON)

Databricks SQL has rich support for nested structures — **frequently tested**.

- **Dot / colon syntax** to traverse:
  - `col.field` — access a field of a **struct**.
  - `col:field` — access a field inside a **JSON string** column.
- **`from_json`** — parse a JSON string column into a struct using a schema.
- **`schema_of_json`** — infer the schema of a JSON string.
- **`explode`** — turn each element of an **array** into its own row.
- **`:` path + array index** — e.g., `data:items[0]:name`.

```sql
SELECT data:store:name FROM json_strings;          -- colon: navigate JSON string
SELECT profile.address.city FROM parsed;           -- dot: navigate struct
SELECT explode(items) AS item FROM orders;         -- array → one row per element
SELECT from_json(raw, 'name STRING, age INT') FROM t;
```

> **Exam Tip:** Use the **colon `:`** operator on a **string column that contains JSON**; use the **dot `.`** operator on a **struct-typed column**. `explode()` flattens an array into multiple rows (one per element). `from_json()` converts a JSON string into a struct you can then navigate with dots.

### Higher-order functions on arrays

```sql
SELECT transform(nums, x -> x * 2) FROM t;          -- apply to each element
SELECT filter(nums, x -> x > 10) FROM t;            -- keep matching elements
SELECT exists(nums, x -> x > 100) FROM t;           -- boolean: any match?
SELECT reduce(nums, 0, (acc, x) -> acc + x) FROM t; -- aggregate
```

> **Exam Tip:** **Higher-order functions** (`transform`, `filter`, `exists`, `reduce`) operate on **array columns without exploding them** — they apply a lambda to each element in place. Recognize the `x -> expression` lambda syntax.

---

## Joins and set operations

```sql
SELECT * FROM a JOIN b ON a.id = b.id;             -- inner (default)
SELECT * FROM a LEFT JOIN b ON a.id = b.id;
SELECT * FROM a UNION SELECT * FROM b;              -- combine, dedup
SELECT * FROM a UNION ALL SELECT * FROM b;          -- combine, keep dupes
SELECT * FROM a INTERSECT SELECT * FROM b;
SELECT * FROM a EXCEPT SELECT * FROM b;             -- rows in a not in b
```

### PIVOT

```sql
SELECT * FROM t
PIVOT (sum(amount) FOR month IN ('Jan','Feb','Mar'));
```

> **Exam Tip:** `UNION` removes duplicates; `UNION ALL` keeps them (and is faster). `PIVOT` reshapes rows into columns — used to build wide summary tables from long data.

---

## SQL UDFs

```sql
CREATE FUNCTION discount(price DOUBLE)
RETURNS DOUBLE
RETURN price * 0.9;

SELECT discount(price) FROM t;
```

- SQL UDFs are **persisted in the metastore**, governed by Unity Catalog permissions, and can be reused across queries/sessions.

> **Exam Tip:** A **SQL UDF** is created with `CREATE FUNCTION ... RETURNS ... RETURN ...`, is stored in the catalog (so it's reusable and governed), and generally performs better than a Python UDF because it stays within Spark SQL's optimizer.

---

## Quick Review

- **ELT** = load raw first, transform in place. Query files directly: `SELECT * FROM json.\`/path\``.
- **CTAS** infers schema and makes a **Delta** table, but **can't set file options** — use `USING CSV ... OPTIONS ... LOCATION` (a **non-Delta external table**) for CSV, then CTAS from it.
- **View** = stored query (survives restart); **temp view** = session-scoped; **global temp view** = cluster-scoped via `global_temp`; **CTE** = single-query only.
- `count(*)` counts all rows; `count(col)` counts non-null. **CHECK constraints** enforce data quality.
- Nested data: **`:`** for JSON-string columns, **`.`** for structs; **`explode`** flattens arrays; **`from_json`** parses. **Higher-order functions** (`transform/filter/exists/reduce`) process arrays in place.
- `UNION` dedups, `UNION ALL` keeps dupes; `PIVOT` rows→columns.
- **SQL UDFs** (`CREATE FUNCTION`) are persisted, governed, and reusable.

---

## Further Learning — Docs & Videos

**Official documentation**
- Query data / SQL reference: https://docs.databricks.com/en/sql/language-manual/index.html
- Query files with `read_files`: https://docs.databricks.com/en/query/formats/index.html
- CREATE TABLE: https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-create-table.html
- Views: https://docs.databricks.com/en/views/index.html
- Query semi-structured JSON: https://docs.databricks.com/en/semi-structured/json.html
- Higher-order functions: https://docs.databricks.com/en/optimizations/higher-order-lambda-functions.html
- SQL UDFs: https://docs.databricks.com/en/udf/sql.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Spark SQL on Databricks: https://www.youtube.com/results?search_query=databricks+spark+sql+elt+tutorial
- Querying JSON / nested data: https://www.youtube.com/results?search_query=databricks+sql+json+explode+from_json
- CTAS & views: https://www.youtube.com/results?search_query=databricks+ctas+temp+view+global+temp+view

---

Next: **[05 — ELT with PySpark & Python](05_ELT_with_PySpark_and_Python.md)**.
