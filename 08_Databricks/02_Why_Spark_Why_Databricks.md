# Why Spark? Why Databricks?

Two separate questions, often confused:

- **Why Spark?** — why this *engine* beat Hadoop MapReduce.
- **Why Databricks?** — why companies pay for a *platform* around a free engine.

---

## Why Spark?

Context: by ~2012 everyone ran [Hadoop](../01_Foundations/Fundamentals/05_Hadoop_Architecture.md), and everyone had the same complaints.

### The MapReduce pain

| Pain | Detail |
|---|---|
| **Slow** | Wrote to disk after *every* map/reduce stage; a 10-step pipeline = 10 disk round-trips |
| **Awful for iteration** | ML algorithms loop over data dozens of times → dozens of disk cycles |
| **Hard to write** | Verbose Java; even "word count" was ~60 lines |
| **Fragmented** | Separate tools for SQL (Hive), streaming (Storm), ML (Mahout) — separate skills, clusters, glue code |

### The Spark answers

| MapReduce pain | Spark answer |
|---|---|
| Disk between stages | **In-memory** intermediate data → 10–100× faster |
| Iteration is slow | `cache()` keeps the dataset in RAM across iterations — ML becomes practical |
| Verbose Java | **PySpark / SQL / Scala** — word count in ~3 lines |
| Tool sprawl | **One engine**: batch + SQL + streaming + ML ([What_Is_Apache_Spark.md](../03_Programming/PySpark/What_Is_Apache_Spark.md)) |
| Dumb execution | **Lazy evaluation + Catalyst optimizer** — plans the whole job before running ([Spark_Processing.md](../03_Programming/PySpark/Spark_Processing.md)) |

Spark kept the good parts of Hadoop thinking — [scale-out on clusters](../01_Foundations/Fundamentals/03_Distributed_Computing.md), fault tolerance, data locality — and fixed the speed and usability. By ~2016 it had effectively replaced MapReduce.

**Interview one-liner:** *"Spark is preferred over MapReduce because it processes data in memory rather than writing to disk between stages, offers high-level APIs in Python/SQL, and unifies batch, streaming, and ML in one engine — making it typically 10–100× faster and far easier to develop with."*

---

## Why Databricks?

Spark is free. So why pay?

**Because running Spark yourself is an ops job, not a data job.** You'd need to: provision clusters, configure memory/cores, patch versions, secure it, monitor it, scale it up for the nightly load and *remember to scale it back down*, and give analysts some way to use it.

**Databricks** — founded 2013 by Spark's original creators — sells exactly that: **Spark as a managed cloud platform** (a [PaaS/SaaS](../04_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md) running on Azure/AWS/GCP; on Azure it's the first-party service *Azure Databricks*).

### What Databricks adds on top of open-source Spark

| Layer | What you get |
|---|---|
| **Managed clusters** | Click → cluster in minutes; **auto-scaling** and **auto-terminate** (huge cost saver) |
| **Optimized runtime** | Databricks' Spark build + Photon engine — faster than stock Spark |
| **Notebooks** | Collaborative workspace; Python + SQL in one place; scheduling built in |
| **Delta Lake** | ACID transactions, schema enforcement, time travel *on data lake files* → the **lakehouse** ([evolution timeline](../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)) |
| **Workflows** | Native job orchestration (often triggered from [Data Factory](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md)) |
| **Unity Catalog** | Central governance: permissions, lineage, data discovery |
| **SQL Warehouses** | BI/analyst-friendly SQL endpoints on the same data |
| **ML tooling** | MLflow, feature store, GPU clusters |

### The pitch in one sentence

> Spark answers *"how do we process huge data fast?"* — Databricks answers *"how does our whole team do that without hiring a cluster-operations department?"*

---

## Spark vs Databricks — keep them straight

| | Apache Spark | Databricks |
|---|---|---|
| What it is | Open-source processing **engine** | Commercial **platform** built around Spark |
| Cost | Free | Pay per compute (DBUs) + cloud VMs |
| You manage | Everything (clusters, tuning, security) | Almost nothing — managed service |
| Storage | None (reads external storage) | None either — your data stays in [ADLS](../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md)/S3; Delta Lake adds the table layer |
| Made by | Apache community | Company founded by Spark's creators |

---

## The numbers behind "10–100× faster" (so you can defend the claim)

The famous benchmark: Spark sorted 100 TB (Daytona GraySort, 2014) in **23 minutes on 206 nodes** — the prior MapReduce record was 72 minutes on 2,100 nodes. ~3× faster on ~1/10 the machines. The "100×" figure comes from **iterative** workloads (ML), where MapReduce pays the full disk round-trip *per iteration* and Spark pays it once, then iterates over cached RAM. Honest phrasing for reviews: *disk-bound single-pass jobs see small gains; iterative and multi-stage pipelines see order-of-magnitude gains.*

## What you'd actually build without Databricks (the DIY bill)

To match a Databricks workspace on raw Azure you would assemble: VM provisioning + images (IaaS), Spark version/patch management, an orchestrator, a notebook service (JupyterHub) + auth, a metastore (Hive on a DB you run), secrets management, cluster autoscaling logic, log collection, per-team cost attribution, and a governance/permissions layer. Each is a solved problem — the *integration* is a permanent platform team. That team's salary total is the number to compare against DBUs, not the $0 license.

## How Databricks pricing actually works

`cost per hour = VM price (Azure bill) + DBUs consumed × DBU rate (Databricks bill)`

- **DBU** = Databricks Unit, a normalized compute-consumption unit; every VM type has a DBU/hour rating.
- Rates differ by **workload type** (Jobs compute is materially cheaper than All-Purpose — running production on interactive clusters is throwing money away) and **tier** (Standard/Premium).
- Serverless SKUs bundle the VM into one rate.
- The levers that matter, ranked: job vs all-purpose clusters → auto-terminate → right-sizing/autoscale bounds → **spot instances for workers** (never the driver) → Photon (higher DBU rate, usually net-cheaper because jobs finish 2–4× sooner).

## Delta Lake — why it's the load-bearing feature

Plain Parquet-on-a-lake fails in specific, painful ways; Delta's `_delta_log` (an ordered transaction log of JSON/checkpoint files) fixes each:

| Lake pain without Delta | Delta answer |
|---|---|
| Job dies mid-write → readers see half the files | **Atomic commits** — a write either appears in the log or never happened |
| Two jobs write at once → corruption | **Optimistic concurrency** — conflicting commit retries/fails cleanly |
| "Who changed the schema?" | **Schema enforcement + evolution** (`mergeSchema` when intended) |
| Bad deploy corrupted yesterday's data | **Time travel** — `VERSION AS OF` / `RESTORE` |
| Upserts require rewrite-everything logic | **MERGE INTO** |
| Millions of small files | `OPTIMIZE` + Z-ORDER ([processing notes](../03_Programming/PySpark/Spark_Processing.md)) |

This is the "lakehouse" in one table: warehouse guarantees, lake economics ([evolution timeline](../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)).

---

## Databricks vs the field — the real decision matrix

| | Databricks | Snowflake | MS Fabric | Synapse Spark |
|---|---|---|---|---|
| Center of gravity | Spark/lakehouse, code-first | SQL warehouse, SQL-first | Power BI-centric suite | Azure-native Spark (aging) |
| Data engineering & streaming | Excellent | Improving (Snowpark) | Moderate | Basic |
| ML/AI platform | Strong (MLflow, GPUs) | Growing | Growing | Weak |
| Pure-SQL analyst experience | Good (SQL warehouses) | Excellent | Excellent (PBI) | OK |
| Lock-in surface | Open formats, proprietary runtime | Proprietary storage engine* | Deep Microsoft | Low but stagnant |

*Snowflake now reads/writes Iceberg, narrowing the gap. Honest guidance: heavy transformation/streaming/ML → Databricks; SQL-analyst-dominated shops → Snowflake; Power-BI-first orgs on a budget → Fabric. Large enterprises frequently run **Databricks for engineering + a warehouse for serving**, and that's fine.

## When Databricks is the wrong answer

- Data < ~100 GB and batch-shaped → DuckDB/Polars on one VM, or just Azure SQL ([when not to distribute](../01_Foundations/Fundamentals/03_Distributed_Computing.md)).
- Pure EL copy with no transformation → [ADF](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) alone.
- One dashboard refresh per day → a serverless SQL query beats a cluster spin-up.
- Teams with zero Python/Spark skills and no runway to learn — a tool nobody can operate is a liability, not an asset.

## Operating Databricks like a pro (the checklist)

- **Cluster policies** — enforce auto-terminate, node-type allowlists, spot-for-workers, tag requirements; without them every user hand-rolls an expensive snowflake cluster.
- **Job clusters + Workflows** for production; all-purpose clusters are for humans. Retries + idempotent jobs ([exactly-once](../03_Programming/PySpark/Spark_Processing.md)) instead of driver HA.
- **Unity Catalog from day one** — retrofitting governance across hive_metastore workspaces is months of migration pain. Three-level namespace (`catalog.schema.table`), central grants, lineage.
- **Environments as code** — workspace/IaC via Terraform, notebooks in Git (Repos), promote dev→prod through CI, never by "cloning the notebook."
- **Watch the driver** — big `collect()`s, giant `display()`s, and 40 users on one shared cluster all melt the same node.

## Field-tested gotchas

- Photon accelerates SQL/DataFrame ops, **not** Python UDFs — a UDF-heavy job pays Photon's premium DBU rate for nothing.
- `VACUUM` defaults to a 7-day retention: time travel silently stops working past it, and *disabling* the safety check to vacuum aggressively can break concurrent readers.
- Autoscaling bounds of 2–100 workers ≠ intelligence: a skewed job will scale to 100 nodes where 99 idle behind one straggler — fix skew first.
- The classic bill-shock trio: forgotten all-purpose cluster, streaming job restarted in a crash-loop all weekend, and `display()` on an unfiltered TB-scale table.

## Interview-grade Q&A

- *Sell Databricks to a CFO in two sentences.* "We pay to delete an infrastructure team's worth of undifferentiated work and get governed, elastic compute that turns itself off. The bill scales with use, not with peak capacity."
- *Spark is free — what exactly are we buying?* Operations (managed clusters), performance (Photon/optimized runtime), collaboration (notebooks/workflows), and governance (Unity Catalog) — the four things raw Spark ships without.
- *Delta vs Parquet in one line?* Parquet is a file format; Delta is Parquet **plus a transaction log** — ACID, MERGE, time travel, schema control.
- *How do you keep Databricks costs sane?* Policies enforcing job clusters/auto-terminate/spot, Photon for SQL-shaped load, right-sized autoscale bounds, and cost tags reviewed monthly.

---

## Further Learning — Docs & Videos

**Documentation**
- Why Databricks (Lakehouse): https://www.databricks.com/product/data-intelligence-platform
- Spark vs Hadoop MapReduce: https://www.databricks.com/glossary/hadoop-vs-spark
- Databricks documentation: https://docs.databricks.com/en/introduction/index.html

**Videos**
- Why Spark and Databricks: https://www.youtube.com/results?search_query=why+apache+spark+and+databricks
- Spark vs Hadoop: https://www.youtube.com/results?search_query=spark+vs+hadoop+mapreduce
