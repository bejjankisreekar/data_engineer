# ETL vs ELT

## What problem are we solving?

Data rarely starts out where it needs to end up, or in the shape it needs to be in. A sales system might record amounts in cents, in five different regional formats, across three different databases — but a business report needs one clean, consistent "Total Sales" number. Getting from messy source data to a clean, usable result requires three steps, always in this order of *concept*, if not always execution:

1. **Extract** — pull the data out of its source (a database, an API, a file)
2. **Transform** — clean it, reshape it, calculate new values, fix errors
3. **Load** — write the result into its final destination (usually a [data warehouse](../01_SQL/SQL_Warehouse.md))

The only real difference between ETL and ELT is **where** step 2 happens — before loading, or after.

---

## ETL: Extract, Transform, Load

```
Source  →  Extract  →  Transform (on a separate processing server)  →  Load  →  Warehouse
```

Data is cleaned and reshaped *before* it ever reaches the warehouse. The warehouse only ever receives finished, ready-to-use data.

Analogy: a caterer prepping ingredients (washing, chopping, cooking) in their own kitchen *before* driving the finished dishes to the event venue. The venue only ever sees the finished meal.

**Why choose ETL:**
- The destination warehouse has limited processing power
- You need to filter out sensitive data (e.g. remove personal information) before it's ever stored in the destination
- The transformation logic is well-established and doesn't change often

---

## ELT: Extract, Load, Transform

```
Source  →  Extract  →  Load (raw)  →  Warehouse  →  Transform (using the warehouse's own power)
```

Raw data is loaded into the destination *first*, and transformed there afterward, using the destination's own processing power.

Analogy: the caterer drives raw, unprepped ingredients straight to the event venue, which has its own large, powerful kitchen — chopping and cooking happen on-site, right before serving.

**Why choose ELT:**
- Modern cloud warehouses (Synapse, Snowflake, BigQuery) have enormous processing power to spare
- You want to keep a copy of the raw, untransformed data available for later (in case the cleaning logic needs to change)
- Faster to get data "in" and iterate on the transformation logic afterward

---

## Side-by-Side

| | ETL | ELT |
|---|---|---|
| Transform happens | Before loading | After loading |
| Needs separate processing step | Yes | No — uses destination's own power |
| Raw data kept? | Often discarded | Usually kept alongside transformed data |
| Common era | Traditional on-premises warehouses | Modern cloud warehouses and data lakes |

---

## Azure Usage

[Azure Data Factory](Azure_Data_Factory.md) can build either pattern:
- **ETL**: use Data Factory's Mapping Data Flows (or Azure Databricks) to transform data mid-pipeline, before writing to Synapse.
- **ELT**: use Data Factory purely to copy raw data into a [Data Lake](../03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md) or Synapse, then run transformation queries inside Synapse itself.

Most new Azure projects lean toward ELT, because cloud warehouses like Synapse are built to handle heavy transformation workloads efficiently.

---

## Real World Example

A retail chain collects sales data from 500 stores nightly.

- Under **ETL**, a separate server cleans and standardizes every store's data (fixing currency formats, removing test transactions) before any of it touches the warehouse.
- Under **ELT**, all 500 stores' raw data is loaded into the warehouse first, and a set of scheduled queries inside the warehouse itself does the cleaning — keeping the original raw records around in case a mistake in the cleaning logic needs to be corrected later.
