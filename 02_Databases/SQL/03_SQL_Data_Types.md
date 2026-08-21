# SQL Data Types

## Why data types matter

Every column in a table must be given a **data type** when it's created — a rule about what kind of value it's allowed to hold. This is what stops someone from typing "banana" into a Salary column, or a date into a Name column.

Analogy: think of a paper form with labeled boxes — one box says "Date of Birth" and is clearly meant for a date, another says "Age" and is meant for a whole number. A data type is that label, enforced automatically by the database instead of left to whoever's filling out the form.

---

## Common Data Types

| Category | Type (T-SQL / general SQL) | Holds | Example |
|---|---|---|---|
| Whole numbers | `INT` | Whole numbers, no decimals | `60000` |
| Decimal numbers | `DECIMAL(p,s)` / `FLOAT` | Numbers with decimal places | `1999.50` |
| Short text | `VARCHAR(n)` | Text up to a set maximum length | `'John'` |
| Long text | `TEXT` | Very large amounts of text | An entire article |
| Date only | `DATE` | Calendar date | `2026-07-17` |
| Date and time | `DATETIME` | Date plus a time of day | `2026-07-17 14:30:00` |
| True/False | `BIT` (T-SQL) / `BOOLEAN` | Yes/no, true/false | `1` or `0` |
| Money | `MONEY` / `DECIMAL(19,4)` | Currency values | `5000.00` |

`VARCHAR(50)` means "text, up to 50 characters." If you try to store a 51-character name, the database rejects it — the same way a paper form's name box would run out of physical space.

---

## Why not just store everything as text?

You technically could store `"60000"` as text instead of a number — but then the database can no longer do numeric operations correctly. Sorting `"9"`, `"10"`, `"2"` as text gives you `"10", "2", "9"` (comparing character by character), while sorting them as numbers correctly gives `2, 9, 10`. Choosing the right data type isn't just bookkeeping — it changes how the data behaves.

---

## Data Types in Practice

```sql
CREATE TABLE Employee (
    EmployeeID INT,
    Name VARCHAR(50),
    HireDate DATE,
    Salary DECIMAL(10,2)
);
```

This table definition — using `CREATE`, covered in [04_SQL_DDL.md](04_SQL_DDL.md) — locks in the shape of every future row: `EmployeeID` must be a whole number, `Name` up to 50 characters of text, `HireDate` a calendar date, and `Salary` a decimal number with up to 2 digits after the point.

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both use T-SQL data types (`INT`, `VARCHAR`, `DATETIME2`, `DECIMAL`, and so on). When designing a table for a data warehouse, picking the smallest data type that safely fits the data (e.g. `INT` instead of a larger type, if values will never exceed a few million) reduces storage cost and speeds up queries across billions of rows.

---

## Real World Example

A hospital's patient records table stores `DateOfBirth` as a `DATE`, not text, specifically so the database can calculate a patient's current age automatically and correctly sort patients by birthday — something that would require constant manual correction if birthdates were just free-form text typed in however each staff member preferred.

---

## Precision, scale, and the money question

`DECIMAL(10,2)` = **precision** 10 total digits, **scale** 2 after the point → max `99,999,999.99`.

**Never store money in `FLOAT`.** Floating point is binary — it cannot represent `0.1` exactly:

```sql
SELECT CAST(0.1 AS FLOAT) + CAST(0.2 AS FLOAT);   -- 0.30000000000000004
```

Sum a million transactions in FLOAT and the pennies drift; auditors notice. Use `DECIMAL(19,4)` (exact) for money. FLOAT's legitimate home is scientific/sensor data where tiny relative error is fine and range matters.

## Sizes and why "smallest safe type" is a warehouse rule

| Type | Bytes | Range |
|---|---|---|
| `TINYINT` | 1 | 0–255 |
| `SMALLINT` | 2 | ±32K |
| `INT` | 4 | ±2.1 billion |
| `BIGINT` | 8 | ±9.2 quintillion |

Across 10 billion fact rows, INT vs BIGINT on one column = 40 GB difference — in storage, memory grants, and shuffle sizes. But: **ID columns that might outgrow INT go straight to BIGINT** — the emergency migration when an ID column overflows at 2.1 billion rows is a genuine on-call war story.

## Strings: VARCHAR vs NVARCHAR, and collations

- `VARCHAR` = 1 byte/char (Latin-ish); `NVARCHAR` = Unicode (2 bytes/char in SQL Server) — names in Telugu, emojis in product reviews: NVARCHAR territory. PostgreSQL's `text/varchar` is UTF-8 natively.
- **Collation** decides sorting/comparison rules: case sensitivity (`_CI_` vs `_CS_`), accent sensitivity, language ordering. Joining two columns with different collations forces conversions (killing index use) or errors — a classic cross-database integration bug.
- `VARCHAR(MAX)`/`TEXT` types can't be fully indexed and get stored off-row — don't default long text into every column "just in case."

## Dates, times, and time zones (where pipelines quietly break)

- Prefer `DATETIME2` over legacy `DATETIME` in SQL Server (more precision, wider range, same-or-less storage).
- **`DATETIMEOFFSET` / `timestamptz`** store the UTC offset; naive `DATETIME` does not — "2026-03-29 02:30" in a DST-switching zone is ambiguous *forever* once stored naive.
- The professional convention: **store UTC everywhere, convert at the display edge.** Mirror it in Spark (`spark.sql.session.timeZone`) — mismatched session timezones between the extract job and the load job shift every timestamp by hours, and nobody notices until a "daily" report splits days at 05:30.

---

## Implicit conversion — the silent performance killer

When types mismatch, SQL converts automatically — and if the conversion lands on the *column* side, indexes die:

```sql
-- OrderNumber is VARCHAR(20), query passes a number:
WHERE OrderNumber = 12345
-- engine must CAST every row's OrderNumber to INT → full scan, index useless
```

The fix is passing the right type (`= '12345'`). Watch for it in execution plans (`CONVERT_IMPLICIT`) — it's among the most common real-world OLTP slowdowns, and application ORMs generate it constantly (e.g. .NET sending NVARCHAR parameters against VARCHAR columns).

## Type systems across your stack — the mapping tax

Every pipeline hop is a type-conversion boundary; know the lossy edges:

| Boundary | Classic loss |
|---|---|
| SQL `DECIMAL(38,x)` → [Parquet](../../05_Storage_and_Formats/File_Formats/05_Parquet.md)/Spark | Overflow or precision truncation past Spark's `Decimal(38)` limits |
| SQL `DATETIME2(7)` → Parquet timestamp | Precision drop (100ns → µs/ms) |
| [CSV](../../05_Storage_and_Formats/File_Formats/01_CSV.md) → anything | *Everything is a string*; leading zeros, "NULL" vs empty, scientific notation all bite |
| JSON numbers → SQL | JavaScript's 2^53 integer ceiling silently rounds big IDs |
| Oracle `NUMBER` → SQL Server | Unbounded precision must be pinned or truncated |

Pro habit: define the **canonical schema once** (in the lakehouse contract), and treat every source type as suspect until mapped explicitly — schema inference is for exploration, never production.

## Semi-structured types — the modern middle ground

Modern engines let a typed table carry an untyped column: SQL Server/Postgres `JSON`/`JSONB`, Databricks `VARIANT`, Snowflake `VARIANT`. The pattern that works: land the raw JSON blob beside extracted, *typed* hot columns (promote the fields you query into real columns; keep the blob for the long tail). Full detail in [02_JSON.md](../../05_Storage_and_Formats/File_Formats/02_JSON.md).

## Field-tested gotchas

- `BIT`/`BOOLEAN` columns holding 0/1/NULL are **three-state** — "NOT active" filters silently drop the NULLs ([three-valued logic](01_What_is_SQL.md)).
- Phone numbers, postal codes, order "numbers" are **text, not numbers** — leading zeros matter and arithmetic on them is meaningless.
- `VARCHAR(255)` cargo-culting: size columns to the domain (`ISO country = CHAR(2)`); oversized strings inflate memory grants in some engines even when unused.
- GUIDs as clustered primary keys fragment B-trees badly (random inserts) — sequential IDs or `NEWSEQUENTIALID()` if you must.

## Interview-grade Q&A

- *Why DECIMAL for money, not FLOAT?* Exact base-10 representation; FLOAT accumulates binary rounding error.
- *What's an implicit conversion and why is it slow?* Auto-CAST applied to the column side of a predicate defeats index seeks → scans.
- *How do you handle time zones in a global pipeline?* Store UTC (offset-aware types at edges), convert at presentation, pin session timezones in every engine.
- *NVARCHAR always, to be safe?* No — it doubles storage for known-ASCII codes/keys; choose per column's real domain.

---

## Further Learning — Docs & Videos

**Documentation**
- SQL data types (W3Schools): https://www.w3schools.com/sql/sql_datatypes.asp
- PostgreSQL data types: https://www.postgresql.org/docs/current/datatype.html

**Videos**
- SQL data types explained: https://www.youtube.com/results?search_query=sql+data+types+explained
