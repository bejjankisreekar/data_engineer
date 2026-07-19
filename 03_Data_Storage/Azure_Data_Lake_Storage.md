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

---
---

# Part 2 — Advanced

## Why the hierarchical namespace actually matters (not just "nicer folders")

In flat blob storage, `folder/file.parquet` is a *naming illusion* — "renaming a folder" of 100,000 files means 100,000 copy+delete operations, and a crash mid-way leaves half-renamed chaos. With HNS enabled:

- **Directory operations are atomic metadata operations** — rename/move/delete a directory in one call. Spark's job-commit protocols exploit exactly this: write to `_temporary/`, atomically move into place — faster *and* safer commits.
- **POSIX-style ACLs** exist per file/directory (below), because directories are now real objects.
- The ABFS driver (`abfss://container@account.dfs.core.windows.net/path`) is tuned for analytics I/O patterns.

Cost of admission: HNS is set **at account creation** and can't be toggled off casually; a handful of blob features lag on HNS accounts — check the matrix before designing around edge features.

## Security model: RBAC + ACLs, layered

Two systems evaluate together:

| Layer | Granularity | Typical use |
|---|---|---|
| **Azure RBAC** | Account/container | Broad platform roles: "engineering SPN = Data Contributor on the lake" |
| **POSIX ACLs** | Directory/file (r/w/x) | Fine partitions: `/finance/` readable by finance group only |

Rules that prevent months of pain: RBAC *data-plane* roles bypass ACL checks (Contributor sees everything — scope it!); ACLs are **not inherited retroactively** — set **default ACLs** on directories *before* data lands, or face a recursive re-ACL job over millions of files; grant to **groups, never users** ([DCL principles](../01_SQL/SQL_DCL_TCL.md)). Modern twist: with Unity Catalog, engines increasingly access the lake via the catalog's credential — table-level grants in UC replace most per-folder ACL surgery for tabular data.

## Zone layout — a reference design

```
abfss://bronze@lake.../  source_system/dataset/ingest_date=2026-07-19/...   (raw, immutable, as-arrived)
abfss://silver@lake.../  domain/entity/                                     (typed Delta, deduped, conformed)
abfss://gold@lake.../    domain/mart/                                       (aggregated, business-modeled)
+ landing/ (pre-validation quarantine)   + checkpoints/ (streaming state — never versioned/tiered!)
```

Conventions that pay off: separate *containers* per zone (clean ACL + lifecycle boundaries); bronze keeps source-native formats, silver onward is **Delta only**; partition folders use `key=value` (Hive-style) so engines prune ([partitioning](../06_PySpark/Spark_Processing.md)); nothing writes to a zone it doesn't own.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The lake is a filesystem; the lakehouse is a database on it

Everything hard about lakes traces to one fact: **storage doesn't know about tables**. Raw ADLS gives you no transactions, no schema enforcement, no discovery — folders of files. The stack that fixes it: Delta's transaction log (table semantics — [why Delta](../06_PySpark/Why_Spark_Why_Databricks.md)) + Unity Catalog (names, permissions, lineage) + zones (quality contracts). A "data swamp" is precisely a lake run without those three ([schema-on-read's dark side](../00_Fundamentals/Big_Data_Evolution_Timeline.md)). When someone proposes "just drop files in the lake," the pro question is: *which table, which contract, which owner?*

## Performance engineering on ADLS

- **File size dominates** — target 100 MB–1 GB; the [small-files problem](../00_Fundamentals/Hadoop_Architecture.md) reappears here with per-file open + transaction costs; `OPTIMIZE` regularly.
- **Partition for pruning, cluster for skipping** — date-partition at sensible cardinality, Z-order/liquid-cluster high-cardinality filters ([OLAP physical design](../00_Fundamentals/OLAP_Storage.md)).
- **Listing is not free** — millions-of-files directory listings throttle jobs; incremental discovery (Auto Loader file notifications) beats re-listing bronze every run.
- **Throughput = parallelism** — sustained reads scale with concurrent connections across files ([blob contract](Azure_Blob_Storage.md)); one giant file caps you at low parallelism.
- Co-locate compute and storage region; cross-region "temporary" reads become permanent egress bills ([cloud economics](../05_cloud/Public_Private_Hybrid_Cloud.md)).

## Operating the lake

- **Retention & GDPR**: "right to erasure" on an append-only bronze is a designed capability — deletion vectors/rewrites in Delta plus lifecycle deletes in raw; decide the mechanism before the first PII lands.
- **Cost hygiene**: lifecycle policies per zone (bronze → cool/archive; checkpoints exempt), `VACUUM` old Delta versions, transaction-cost monitoring for small-write storms.
- **Disaster thinking**: pipelines-as-code + immutable bronze often means *re-derivation* beats geo-replicating silver/gold — protect sources and code above derived data ([redundancy classes](Azure_Blob_Storage.md)).
- **Access telemetry**: storage logs → who read `/finance/` — auditors will ask ([auditing](../01_SQL/SQL_DCL_TCL.md)).

## Field-tested gotchas

- Streaming **checkpoint folders** must be excluded from lifecycle tiering and blob versioning — tiered/mutated checkpoints quietly kill streaming jobs.
- Recursive ACL fixes on deep trees run for hours and can partially apply — model ACLs on containers/top dirs with default ACLs from day one instead.
- `abfss://` vs legacy `wasbs://`: mixed drivers in one estate cause subtle auth/commit differences — standardize on ABFS.
- Two writers to the same *path* without a table format silently interleave files — every governed path should be a Delta table or single-writer-owned.
- Timestamp-named "versioned folders" (`/v2_final_new/`) are the human small-files problem — table format + time travel replaces folder archaeology.

## Interview-grade Q&A

- *Blob vs ADLS Gen2?* Same service; HNS adds atomic directory ops, POSIX ACLs, and the ABFS analytics driver — the difference between object storage and a lake-grade filesystem.
- *Design the folder/security layout for a multi-team lake.* Zone containers, domain directories, group-based default ACLs + scoped RBAC, Delta everywhere past bronze, UC grants for tables.
- *Why is renaming a directory cheap in ADLS but expensive in plain blob?* HNS makes it one metadata op vs N copy+deletes — and Spark's atomic commit relies on it.
- *Your lake queries got slow over six months — hypotheses?* Small-file accumulation (no OPTIMIZE), partition explosion, listing overhead growth, stats/clustering drift — all measurable, all fixable.
