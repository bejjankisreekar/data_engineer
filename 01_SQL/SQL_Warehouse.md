# SQL Warehouse (Data Warehouse)

## What is a SQL Warehouse?

A SQL Warehouse stores huge amounts of historical business data for reporting and analytics.

Analogy: if a [SQL Database](SQL_Database.md) is a shop's cash register — recording each individual sale the instant it happens — a warehouse is the head office's year-end report, pulling together every till receipt from every store to answer big-picture questions like "which region sold the most this quarter?"

Unlike a SQL Database, data is rarely updated.

Instead, it is continuously loaded from different systems.

Example sources:

- ERP
- CRM
- HRMS
- Sales System
- Website Logs
- APIs

All data is combined into one place.

---

## Why use a Warehouse?

To answer business questions like:

- Total sales this year
- Best selling products
- Monthly revenue
- Customer growth
- Profit trends

---

## Example

Imagine Amazon.

Orders Table

10 million rows

Customers Table

2 million rows

Products Table

500,000 rows

The warehouse combines all of them for analysis.

---

## Typical Workflow

Applications
        ↓
SQL Databases
        ↓
ETL / ELT
        ↓
SQL Warehouse
        ↓
Power BI
        ↓
Reports

---

## Characteristics

- Read-heavy
- Historical data
- Optimized for analytics — this pattern is called OLAP (Online Analytical Processing), covered in the [Glossary](../GLOSSARY.md#databases-and-transactions)
- Large datasets
- Star schema — one central "facts" table (e.g. Sales) surrounded by smaller lookup tables (e.g. Products, Customers, Dates), connected the same way described in [Keys and Joins](SQL_Keys_and_Joins.md)
- Snowflake schema — like a star schema, but the lookup tables are broken down further into their own sub-tables

---

## Azure SQL Warehouse

Modern equivalent:

Azure Synapse Analytics

or

Microsoft Fabric Warehouse

---

## Advantages

- Very fast reporting
- Handles billions of rows
- Excellent for BI
- Historical analysis
- Business intelligence

---

## Example Query

Total sales per month

```sql
SELECT
Month,
SUM(SalesAmount)
FROM Sales
GROUP BY Month;
```

---

## Where does this data come from?

A warehouse doesn't collect its own data — it's filled by pipelines that pull data in from elsewhere. See [ETL vs ELT](../04_ETL_ELT/ETL_vs_ELT.md) for the two common ways this data-loading happens, and [Data Lake vs Warehouse vs Database](../03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md) for how a warehouse fits alongside raw storage.

## SQL Database vs Warehouse

| SQL Database | SQL Warehouse |
|--------------|---------------|
|OLTP|OLAP|
|Current data|Historical data|
|Many updates|Few updates|
|Small to medium|Very large|
|Applications|Analytics|
|Fast transactions|Fast reporting|

---

## Real World Example

Hospital

Database

- New patient
- Doctor appointment
- Billing

Warehouse

- Total patients this year
- Disease trends
- Revenue analysis
- Insurance claims

---
---

# Part 2 — Advanced

> Deep foundations for this note live in [OLAP_Storage.md](../00_Fundamentals/OLAP_Storage.md) (columnar internals, star schema mechanics, SCDs). This part focuses on the warehouse as a *system you design and load*.

## Designing the star, step by step (Kimball's four questions)

Worked example — retail sales:

1. **Pick the business process** → "a completed sale."
2. **Declare the grain** → *one row per product per order line* (the most important sentence in the design; every fact must be true at this grain — see [join grain](SQL_Keys_and_Joins.md)).
3. **Choose dimensions** → Date, Product, Store, Customer, Promotion (the "by" words in business questions: sales *by store by month*).
4. **Choose facts** → quantity, unit_price, line_amount — numeric, additive at the grain.

```
Dim_Date ───┐                ┌─── Dim_Product
            │                │
         Fact_Sales(line grain): date_key, product_key,
            │     store_key, customer_key, promo_key,
            │     quantity, line_amount
Dim_Store ──┘                └─── Dim_Customer
```

Rules that separate clean stars from messy ones: facts contain **keys + numbers only** (text descriptions live in dimensions); dimension attributes are denormalized flat ("Category" as a column, not a sub-table); every fact-dimension relationship goes through a **surrogate key**; unknown/late dimension members get a `-1 'Unknown'` row so facts never orphan.

## Loading the warehouse — the nightly choreography

```
1. Extract to staging          (raw copies, no transforms — auditable)
2. Load/refresh DIMENSIONS     (MERGE; SCD2 expiry+insert for changed attributes)
3. Look up surrogate keys      (business key → current surrogate)
4. Load FACTS                  (append/MERGE at grain; unknown keys → -1)
5. Validate                    (row counts vs source, orphan checks, sum reconciliation)
6. Swap/publish + refresh BI extracts
```

Dimensions **always load before facts** (referential order without [enforced FKs](SQL_Keys_and_Joins.md)); every step is [idempotent](SQL_DML.md) so a 3am retry converges instead of duplicating; late-arriving facts MERGE into old partitions rather than being dropped.

## MPP: how Synapse-class warehouses distribute your tables

An MPP warehouse spreads each table across many compute nodes ([distributed computing](../00_Fundamentals/Distributed_Computing.md)); *how* you spread it decides join cost:

| Distribution | What | Use for |
|---|---|---|
| **HASH(key)** | Rows routed by key hash | Big fact tables — hash on the most-joined key |
| **ROUND_ROBIN** | Even spray, no key | Staging/loading tables |
| **REPLICATE** | Full copy on every node | Small dimensions (< ~2 GB) — kills data movement |

The performance killer is **data movement**: joining two large tables hash-distributed on *different* keys forces a network re-shuffle per query (the same shuffle economics as [Spark](../06_PySpark/Spark_Processing.md)). Fact hashed on `order_key` + replicated dimensions = star joins with near-zero movement.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Warehouse vs lakehouse — the 2026 decision, honestly

The [lakehouse](../00_Fundamentals/Big_Data_Evolution_Timeline.md) (Delta + Databricks SQL / Fabric) now covers most classic warehouse duties. What tips the decision:

- **Toward lakehouse**: diverse data (semi-structured, streaming, ML features), one copy of data serving engineering + BI, open formats, spend control via decoupled storage.
- **Toward classic warehouse** (Synapse/Snowflake/Fabric WH): SQL-only teams, mature BI estates, thousands of concurrent small queries, strict per-query SLAs.
- The common enterprise landing point: **medallion lakehouse as the source of truth, gold layer exposed via SQL endpoint or a slim serving warehouse** — dimensional modeling survives intact either way; only the storage engine changed. Kimball outlived his critics again.

## Semantic layer & metric governance

The warehouse's last mile is *definitions*, not tables: "revenue" (gross? net of returns? recognized?) must mean one thing across every dashboard. Mature stacks put metrics in a **semantic layer** — Power BI semantic models, dbt metrics, Cube — sitting on gold [views](SQL_Views.md). The warehouse pro's real KPI: two executives can no longer bring two different "revenue" numbers to the same meeting.

## Performance pathologies specific to warehouses

- **The monster dashboard query** — 14 joins because the BI tool joined *everything*; fix with pre-joined gold views/OBT, not heroic tuning.
- **Concurrency cliffs** — one warehouse sized for the nightly load serving 500 analysts at 9am; fix with workload isolation (separate compute for load vs BI — the [storage/compute separation](../00_Fundamentals/OLAP_Storage.md) dividend).
- **Snapshot fact explosion** — daily snapshot of 100M accounts = 36B rows/year; mitigate with monthly grain + current-daily hybrid, or accumulating snapshots.
- **SCD2 dimension bloat** — a "slowly" changing dimension changing hourly (bad source data, e.g. whitespace churn) multiplies rows; hash-compare meaningful columns only.
- Everything in [OLAP physical design](../00_Fundamentals/OLAP_Storage.md) — partitioning, clustering, file sizing — applies verbatim.

## Field-tested gotchas

- A fact table's grain drifting ("we'll just add header-level discounts to the line table") silently double-counts — allocate to grain or model a second fact.
- Time zones in Dim_Date: pick the business's reporting timezone explicitly, or "daily" totals differ from source systems forever ([timestamp discipline](SQL_Data_Types.md)).
- Reconciliation is a feature, not a chore: automated source-vs-warehouse row/sum checks per load catch the silent-loss bugs auditors otherwise find first.
- History rewrites (restated financials, GDPR erasure) need designed procedures — SCD2 + append-only makes "change the past" a project, not an UPDATE.

## Interview-grade Q&A

- *Walk me through designing a warehouse for ride-sharing.* Process = completed trip; grain = one row per trip; dims = rider, driver, date/time, city/geo, vehicle; facts = fare, distance, duration, tip; SCD2 on driver/city attributes.
- *Why surrogate keys in dimensions?* Stable joins independent of source keys, enable SCD2 history, compact fact rows.
- *Fact table types?* Transaction, periodic snapshot, accumulating snapshot — chosen by the question pattern (events vs levels vs process durations).
- *How do you distribute tables in an MPP warehouse?* Hash big facts on the dominant join key, replicate small dims, round-robin staging — minimizing per-query data movement.