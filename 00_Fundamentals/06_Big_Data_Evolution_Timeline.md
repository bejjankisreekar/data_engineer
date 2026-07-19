# Big Data Evolution Timeline

## Why learn the history?

Every modern tool (Spark, Databricks, Snowflake, Azure Data Lake) exists to fix a weakness of the tool before it. Knowing the sequence makes the "why" of each technology obvious — and it's a favorite interview topic.

---

## The timeline

```
1970s–1990s   Relational databases (OLTP)
1980s–2000s   Data warehouses (OLAP)
2003–2004     Google publishes GFS + MapReduce papers
2006          Hadoop (open-source big data)
2009–2014     Spark (in-memory processing)
2013          Databricks founded; cloud data lakes rise
2015–2020     Cloud warehouses (Snowflake, Synapse) + Delta Lake
2020+         Lakehouse era, streaming-first, AI workloads
```

---

## Era 1 — Relational databases (1970s–1990s)

- Data lived in **row-based [OLTP](01_OLTP_Storage.md) databases** (Oracle, SQL Server, MySQL).
- Perfect for running applications; fine for analysis while data was small.
- **Breaking point:** running heavy reports on the live database slowed the application down, and data volumes started outgrowing single machines.

## Era 2 — Data warehouses (1980s–2000s)

- Solution: copy data out of OLTP systems into a separate, analysis-optimized **[OLAP](02_OLAP_Storage.md) warehouse** (Teradata, later Netezza, Exadata).
- Introduced ETL, star schemas, columnar thinking.
- **Breaking point:** warehouses were expensive appliances, handled **structured data only**, and scaled up (bigger box), not out. The internet era brought logs, clickstreams, images — too big, too messy.

## Era 3 — Google's papers & Hadoop (2003–2012)

- Google faced web-scale data and published how it coped: **GFS** (2003, distributed storage) and **MapReduce** (2004, distributed processing).
- Yahoo engineers turned the ideas into open-source **[Hadoop](05_Hadoop_Architecture.md)** (2006): HDFS + MapReduce on cheap commodity machines — [scale out, not up](03_Distributed_Computing.md).
- Suddenly *any* company could store and process petabytes.
- **Breaking point:** MapReduce wrote to **disk between every step** → multi-stage jobs and machine learning were painfully slow; writing Java MapReduce code was painful; clusters were hard to operate.

## Era 4 — Spark (2009–2015)

- **[Apache Spark](../06_PySpark/What_Is_Apache_Spark.md)** (UC Berkeley, 2009; Apache top-level 2014) kept distributed processing but moved it **in-memory** — 10–100× faster than MapReduce.
- One engine for batch, SQL, streaming, and ML; friendly APIs in Python/Scala/SQL.
- Spark replaced MapReduce as the de facto processing engine (details: [Why_Spark_Why_Databricks.md](../06_PySpark/Why_Spark_Why_Databricks.md)).
- **Breaking point:** running your *own* Spark/Hadoop cluster was still heavy ops work.

## Era 5 — Cloud (2013–2020)

- Storage and compute moved to the [cloud](../05_cloud/01_Public_Private_Hybrid_Cloud.md): S3 / [Azure Data Lake](../03_Data_Storage/03_Azure_Data_Lake_Storage.md) replaced HDFS; managed services replaced hand-run clusters.
- **Databricks** (founded 2013 by Spark's creators) offered Spark as a managed [SaaS/PaaS](../05_cloud/02_SaaS_PaaS_IaaS.md) platform.
- Cloud warehouses (Snowflake, BigQuery, Synapse) separated **storage from compute** — pay for each independently, scale instantly.
- **Breaking point:** companies now ran *two* copies of data — a lake (cheap, messy) and a warehouse (clean, expensive) — with pipelines constantly syncing them.

## Era 6 — The Lakehouse (2020+)

- **Delta Lake** (and Iceberg/Hudi) added warehouse features — ACID transactions, schema enforcement, time travel — directly **on top of data lake files** ([Parquet](../02_File_formats/05_Parquet.md)).
- Result: the **lakehouse** — one copy of data, lake prices, warehouse reliability. Databricks' core pitch.
- Current trends: streaming-first pipelines, governance (Unity Catalog), and AI/ML workloads on the same platform.

---

## One-line summary per era

| Era | Problem | Answer |
|---|---|---|
| Databases | Run the business | OLTP, rows, ACID |
| Warehouses | Analyze the business | OLAP, columns, ETL |
| Hadoop | Data too big for one machine | Scale out on cheap hardware |
| Spark | Disk-based processing too slow | In-memory distributed compute |
| Cloud | Clusters too hard to run | Managed, elastic, pay-as-you-go |
| Lakehouse | Lake + warehouse duplication | One platform on open formats |

---
---

# Part 2 — Advanced

## The architecture wars each era fought

### Lambda vs Kappa (2011–2016): how to serve both batch and real-time

- **Lambda architecture** — run *two* parallel pipelines: a batch layer (accurate, slow, e.g. Hadoop) and a speed layer (approximate, fast, e.g. Storm), merged at query time. It worked, but every business rule had to be written **twice** and kept in sync — a maintenance tax teams grew to hate.
- **Kappa architecture** — Jay Kreps' (Kafka creator) rebuttal: keep **one** streaming pipeline; when logic changes, replay the log from the beginning. Simpler, but demands a replayable log and stream-first thinking.
- **Where it landed:** modern lakehouse pipelines (Spark Structured Streaming + Delta) quietly unified the two — the *same code* runs in batch or streaming mode over the same tables. Lambda's problem dissolved rather than being won.

### The warehouse economics shift: storage/compute separation

Old MPP warehouses (Teradata, Netezza) coupled disks to nodes — growing storage meant buying compute, and one overloaded cluster served everyone. Snowflake's 2015-era insight: put data in cheap object storage, spin **independent compute clusters** over it per team. Consequences that now feel obvious:

- Idle compute can be **shut off** (the single biggest cost lever in cloud analytics).
- Workload isolation: data science can't slow down finance dashboards.
- Zero-copy clones / time travel become metadata operations, not data copies.

### The open table format war (2019–present): Delta vs Iceberg vs Hudi

Plain Parquet files in a lake can't do ACID, so three projects added a **transactional metadata layer** over them:

| | Delta Lake | Apache Iceberg | Apache Hudi |
|---|---|---|---|
| Origin | Databricks | Netflix | Uber |
| Transaction log | `_delta_log` JSON/parquet checkpoints | snapshot manifests | timeline + file groups |
| Sweet spot | Databricks/Spark ecosystems | Multi-engine neutrality (Trino, Flink, Snowflake) | Streaming upsert-heavy ingestion |

All three give: **ACID commits, schema evolution, time travel, hidden partitioning/data skipping.** The pro takeaway: the *format* matters less than the fact that the industry standardized on *open formats on object storage* — vendor lock-in moved up the stack, into catalogs and engines. (Interoperability efforts — Delta UniForm, Iceberg REST catalogs — are actively blurring the lines.)

## A decade of "one-liners" worth knowing the origin of

| Idea | Origin story |
|---|---|
| "Schema-on-read" | Hadoop era: dump raw now, impose structure at query time — the data lake's founding principle (and the source of "data swamps" when governance was skipped) |
| "Data gravity" | Data is heavy; compute moves to it — why every vendor wants to host your storage |
| "Medallion (bronze/silver/gold)" | Databricks' codification of raw → cleaned → business-ready layers in a lake ([ETL_vs_ELT](../04_ETL_ELT/01_ETL_vs_ELT.md)) |
| "ELT beat ETL" | Cheap elastic warehouse compute made "load raw, transform in SQL (dbt)" the default over pre-transforming in tools |

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Reading the timeline as a repeating cycle

Every era follows the same loop — **bottleneck → decoupling → new bottleneck**:

1. Compute was the bottleneck → Hadoop decoupled processing across machines → *operations* became the bottleneck.
2. Ops was the bottleneck → cloud decoupled infrastructure from teams → *data duplication/governance* became the bottleneck.
3. Duplication was the bottleneck → lakehouse decoupled table format from engine → today's bottlenecks: **governance, data quality, and cost**.

Pros use this lens to evaluate new tech: *"which coupling does this remove, and what new bottleneck will it create?"* — a far better filter than hype.

## The current frontier (2024–2026), briefly

- **Governance as the product** — Unity Catalog / Purview: lineage, fine-grained permissions, discovery. The hard problem is no longer processing terabytes; it's knowing what you have and who may see it.
- **Streaming-first CDC** — the default enterprise pattern is becoming: OLTP → log-based CDC → Kafka/Event Hubs → Delta, with batch as a special case of streaming.
- **Data mesh** (organizational, not technical) — domain teams own their data as *products* with contracts, instead of one central team owning one giant platform. Works at org scale; overkill for small teams.
- **AI workloads converge onto the lakehouse** — feature engineering, vector search, and LLM fine-tuning read the same governed tables; single-node engines (**DuckDB, Polars**) simultaneously ate the low end, shrinking "big data" to the truly big.
- **Small data counter-revolution** — a pro's most valuable 2026 skill: recognizing the 90% of workloads that *don't* need distributed anything ([when NOT to distribute](03_Distributed_Computing.md)).

## How to use history in interviews & design reviews

- *"Why does Databricks exist?"* → trace era 4→5: Spark solved speed, Databricks solved operations ([Why_Spark_Why_Databricks](../06_PySpark/Why_Spark_Why_Databricks.md)).
- *"Lake or warehouse?"* → era 6 answer: one lakehouse, unless the org already runs a mature warehouse and the migration cost outweighs duplication cost.
- *"Should we adopt X?"* → ask which era's problem X solves; adopting a solution to a problem you don't have is how teams end up running Kafka for 100 rows/day.
- Architecture reviews respect scars: name the *breaking point* a proposal inherits (e.g. "this re-couples storage and compute — we know how that movie ends").
