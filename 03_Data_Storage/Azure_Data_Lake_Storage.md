# Azure Data Lake Storage (ADLS)

## What is it?

Azure Data Lake Storage (ADLS, specifically "Gen2") is [Azure Blob Storage](Azure_Blob_Storage.md) with extra features layered on top, purpose-built for large-scale data analytics. It's not a separate product you choose *instead of* Blob Storage — it's Blob Storage with a "big data" mode switched on.

If Blob Storage is a general-purpose filing cabinet, ADLS is that same filing cabinet fitted with proper labeled folder dividers and a sign-in sheet controlling exactly who can open which drawer.

---

## What ADLS adds on top of Blob Storage

| Feature | Why it matters |
|---|---|
| Hierarchical namespace | True nested folders (folder inside folder inside folder), instead of Blob Storage's flatter "container" structure. Faster to rename/move/organize large folder trees. |
| Fine-grained permissions | You can grant access down to an individual folder or file (like a company giving the finance team access to `/Finance/` but not `/HR/`), not just the whole storage account. |
| Built for analytics engines | Optimized specifically for high-throughput reading by tools like Spark, Databricks, and Synapse — the same engines used to process a [Data Lake's](Data_Lake_vs_Warehouse_vs_Database.md) raw data. |

---

## How data typically flows through ADLS

A common organizing pattern is the **medallion architecture** — three folder "layers" representing increasing levels of data quality:

```
Bronze (raw)        →  Data exactly as it arrived: untouched CSV, JSON, logs
Silver (cleaned)     →  Duplicate/bad records removed, types corrected
Gold (business-ready) →  Aggregated, modeled data ready for reporting
```

Analogy: Bronze is the delivery truck's cargo dumped at the loading dock. Silver is that cargo sorted and checked for damage. Gold is the finished product arranged on the store shelf, ready for a customer (in this case, a business analyst) to pick up.

---

## Advantages

- Massive scale (petabytes), low storage cost
- Handles any file type or format ([CSV](../02_File_formats/CSV.md), [JSON](../02_File_formats/JSON.md), [Parquet](../02_File_formats/Parquet.md), images, etc.)
- Folder-level security
- Deep integration with Azure's analytics tools (Databricks, Synapse, Data Factory)

---

## Limitations

- Not meant for fast, small, transactional updates — that's what a [SQL Database](../01_SQL/SQL_Database.md) is for
- Raw data still needs cleaning/transformation before it's useful for reporting — a data lake alone doesn't organize itself

---

## Azure Usage

- Azure Data Factory pipelines commonly land raw data into ADLS as a first step
- Azure Databricks and Synapse read directly from ADLS to process large datasets
- Often paired with [Delta Lake](../GLOSSARY.md) format to add reliability features on top of raw files

---

## Real World Example

A telecom company collects call-detail records from millions of phone calls every day. Raw records land in ADLS's Bronze folder exactly as the network equipment produced them. A nightly pipeline cleans obviously broken records (Silver), then aggregates call volume and duration by region and hour (Gold). Analysts and dashboards only ever query the Gold layer — they never need to touch the messy raw data directly.
