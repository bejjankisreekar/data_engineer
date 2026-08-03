# Dedicated vs Serverless SQL Pools

## What is it?

Azure Synapse offers **two very different SQL engines**, and knowing which is which — and the **MPP internals** of the dedicated one — is one of the most tested topics in Azure Data Engineer interviews.

- **Dedicated SQL pool** — a **provisioned** Massively Parallel Processing (**MPP**) data warehouse. You buy compute (DWUs), load data into distributed tables, and get fast, high-concurrency SQL. (This is the former *SQL Data Warehouse*.)
- **Serverless SQL pool** — a **pay-per-query** engine that runs T-SQL directly over files in the [data lake](../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md), with no provisioning and no storage of its own.

In one line: **dedicated = a provisioned MPP warehouse you load and serve BI from; serverless = ad-hoc T-SQL over lake files, billed per terabyte scanned.**

---

## Analogy: owning a warehouse vs renting a reading room

A **dedicated SQL pool** is like **owning a distribution warehouse**: you stock the shelves in advance (load data), organize them by a system so forklifts don't collide (distribution), and it's instantly ready to fulfill many orders at once — but you pay rent whether or not anyone's shopping. A **serverless SQL pool** is like a **pay-per-visit reading room over a public archive**: you don't own or stock anything; you walk in, read the documents where they sit (files in the lake), and pay only for the pages you actually pull. Great for occasional research, wrong for running a high-volume storefront.

---

## Side-by-side

| | **Dedicated SQL pool** | **Serverless SQL pool** |
|---|---|---|
| Provisioning | You provision compute (DWUs) | None — always available |
| Storage | Data **loaded & stored** in the pool (distributed) | **No storage** — reads files in the lake in place |
| Billing | Per **DWU-hour while online** (pause to stop) | Per **TB scanned** by queries |
| Performance | Fast, high concurrency, predictable | Depends on file layout; not for high concurrency |
| Best for | Governed BI, star schemas, many concurrent users | Ad-hoc exploration, logical warehouse, one-off queries |
| Table model | MPP with distribution & indexing | External tables / `OPENROWSET` over files |
| Data formats | Its own columnstore storage | Parquet, CSV, JSON, Delta in the lake |

---

## Dedicated pool: the MPP architecture

This is the heart of the topic. A dedicated pool spreads data and work across many nodes:

```
                 ┌──────────────┐
   Query  ─────► │ CONTROL NODE │  ← plans the query, coordinates
                 └──────┬───────┘
        ┌───────────────┼───────────────┐
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │Compute 1│     │Compute 2│ ... │Compute N│   ← run query pieces in parallel
   └────┬────┘     └────┬────┘     └────┬────┘
     distributions   distributions   distributions   ← data is split into 60 buckets
```

- The **control node** receives your SQL, builds a distributed plan, and coordinates.
- **Compute nodes** do the work in parallel (more DWUs = more compute nodes).
- Data is physically split into **60 distributions** (buckets), spread across the compute nodes. How you split it — the **distribution strategy** — decides performance.

---

## Distribution strategies (the #1 dedicated-pool interview topic)

How a table's rows are assigned to the 60 distributions:

| Strategy | How rows are placed | Use for |
|---|---|---|
| **Hash** | By hashing a chosen column | **Large fact tables** — pick a high-cardinality, frequently-joined column as the hash key |
| **Round-robin** | Evenly, at random | Staging/loading tables, or when no good hash key exists |
| **Replicated** | Full copy of the table on every node | **Small dimension tables** (< ~2 GB) |

**Why it matters — data movement (shuffle):** when a join's two tables are distributed on the *same* key, matching rows are already co-located and the join is fast. When they're not, Synapse must **shuffle** data across nodes ([shuffle recap](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)) — the main cause of slow MPP queries. Good distribution design = minimize data movement.

**The classic star-schema recipe:** hash-distribute large fact tables on their common join key; replicate small dimensions so every node has them locally — joins then need little or no shuffle.

---

## Advantages

**Dedicated:**
- High performance and concurrency for governed BI at scale.
- Predictable, tunable via distribution, indexing, partitioning, statistics.
- Workload management (resource classes) to prioritize queries.

**Serverless:**
- Zero provisioning, instantly available, pay only for what you scan.
- Query the lake in place — no load step, works on Parquet/CSV/JSON/Delta.
- Ideal for exploration and a "logical warehouse" (views over lake files).

## Disadvantages

**Dedicated:**
- Always-on cost while online — must pause to save money.
- A load step and distribution design are required; bad distribution = slow.

**Serverless:**
- Not for high-concurrency, low-latency BI.
- Cost scales with (badly-laid-out) data scanned — poor file layout gets expensive.
- Fewer optimization levers than a provisioned warehouse.

---

## Azure Usage

- **DWU (Data Warehouse Unit)** — the dedicated pool's unit of provisioned compute; scale up for more speed/concurrency, pause to stop billing.
- **Loading** — use **`COPY INTO`** (modern, simplest) or **PolyBase** to bulk-load from the lake; use **CTAS** (`CREATE TABLE AS SELECT`) to transform-and-redistribute inside the pool.
- **Serverless** — query via `OPENROWSET(...)` or external tables; commonly used to build **views** that give a SQL layer over the lake for Power BI or exploration.
- **Statistics** — keep column statistics updated; the MPP optimizer relies on them to plan distribution-aware joins.

---

## Real World Example

A bank's reporting warehouse lives in a Synapse **dedicated SQL pool**. The 2-billion-row `fact_transactions` table is **hash-distributed on `account_id`**, and the `dim_account` table (a few hundred MB) is **replicated** to every node — so the daily "spend by account segment" join runs with almost no data movement. Staging tables from the nightly load are **round-robin** distributed (fast, even loads) and then transformed into the distributed fact table with **CTAS**. Analysts who occasionally want to poke at raw upstream files don't touch the pool at all — they run **serverless** queries straight over the Parquet in ADLS, paying only for the terabytes scanned. The dedicated pool is **paused from 8 pm to 6 am**, cutting its bill by ~40% with no impact on business-hours reporting.

---
---

# Part 2 — Advanced

## Table design in a dedicated pool

Beyond distribution, three more levers:
- **Indexing** — **Clustered Columnstore Index (CCI)** is the default and best for large analytical tables (compression + fast scans, [columnar](../01_Foundations/Fundamentals/02_OLAP_Storage.md)); **heap** or **clustered index** suit small or lookup-heavy tables.
- **Partitioning** — split a table by a column (usually date) so queries prune and loads/deletes target one partition. Don't over-partition — with 60 distributions already, too many partitions makes tiny, inefficient row groups.
- **Statistics** — the optimizer needs current column stats to choose good plans; stale stats are a top cause of bad MPP performance.

## Minimizing data movement

Data movement (DMS — Data Movement Service) is the MPP tax. It happens when a join/aggregation needs rows that live on different distributions. Reduce it by: aligning fact-table hash keys with the columns you join on, replicating small dimensions, and avoiding hashing on a low-cardinality or skewed column (which piles rows onto a few distributions — **data skew**, the other MPP killer). Reading the query plan for "ShuffleMove"/"BroadcastMove" operations is how you diagnose it.

## Resource classes & workload management

Dedicated pools control concurrency via **resource classes / workload groups** — they allocate memory and priority to queries. A big load or transform gets a larger resource class (more memory, fewer concurrent slots); many small BI queries get a smaller one (less memory, high concurrency). This is how you stop one heavy query from starving the dashboards.

## Serverless as a logical warehouse

Serverless shines as a **logical/virtual warehouse**: define external tables or views over lake files ([medallion](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) gold Parquet/Delta), and BI tools query those views with T-SQL — no data copied into a warehouse. It's a low-cost way to serve SQL over the lakehouse when full dedicated-pool performance isn't needed. File layout (partitioning, Parquet, not-too-many-small-files) directly controls both speed and cost, since you pay per byte scanned.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Distribution design is where MPP warehouses live or die

Everything about dedicated-pool performance traces back to two enemies: **data movement** (shuffle) and **data skew**. The senior designs the schema to defeat both — hash facts on the true join/aggregation key, replicate small dimensions, round-robin only staging, and never hash on a skewed/low-cardinality column. A pool that "got slow as it grew" is almost always a distribution problem, not a DWU problem — and throwing DWUs at a shuffle-bound query wastes money. This mirrors the [join/shuffle discipline](../03_Programming/PySpark/07_Joins.md) in Spark; the physics are the same.

## Pay-per-scan makes file layout a cost control

With serverless, a badly-laid-out lake (giant CSVs, millions of tiny files, no partition pruning) turns every query into a full, expensive scan. The pro treats **Parquet + sensible partitioning + compaction** as a *cost* feature, not just a speed one — because serverless bills the bytes read. "Convert this CSV zone to partitioned Parquet" often cuts both query time and the bill by an order of magnitude.

## Use both engines deliberately

The mature pattern isn't "dedicated vs serverless" — it's **both, by role**: serverless for exploration, data discovery, and light logical-warehouse serving; dedicated for the governed, high-concurrency BI that justifies provisioned compute. Forcing everything into one engine (all ad-hoc scans into the pricey pool, or all high-concurrency BI onto per-scan serverless) is the common mistake. Match engine to workload.

## Field-tested gotchas

- **Hashing on a low-cardinality/skewed column** — piles rows onto a few of the 60 distributions; severe skew and slow queries.
- **Not replicating small dimensions** — forces shuffles on every star-schema join.
- **Over-partitioning** — with 60 distributions, too many partitions create tiny row groups that hurt columnstore efficiency.
- **Stale statistics** — the optimizer plans badly; refresh stats after big loads.
- **Serverless over unpartitioned giant files** — full scans, surprising bills; convert to partitioned Parquet.
- **Leaving the dedicated pool online 24/7** — pay for idle compute; pause it.

## Interview-grade Q&A

- *Dedicated vs serverless SQL pool?* Dedicated is a provisioned MPP warehouse that stores data in distributed tables for high-concurrency BI (always-on cost); serverless runs T-SQL over lake files in place, billed per TB scanned, ideal for ad-hoc/logical-warehouse use.
- *Explain MPP in a dedicated pool.* A control node plans the query; multiple compute nodes execute in parallel over 60 data distributions; more DWUs add compute. Performance hinges on minimizing cross-distribution data movement.
- *What are the distribution strategies and when to use each?* Hash (large fact tables, on a high-cardinality join key), round-robin (staging/loads or no good key), replicated (small dimensions copied to every node) — chosen to minimize shuffle.
- *What causes slow dedicated-pool queries?* Data movement (misaligned distribution keys, non-replicated small dims) and data skew (hashing a skewed/low-cardinality column), plus stale statistics.
- *How do you load a dedicated pool?* `COPY INTO` or PolyBase from the lake for bulk load; CTAS to transform and redistribute within the pool.
- *How does serverless control cost?* It bills per TB scanned, so Parquet + partition pruning + compaction directly reduce both runtime and cost.

---

## Related Notes

- **Prev:** [Azure Synapse Analytics](01_Azure_Synapse_Analytics.md) · **Next:** [Microsoft Fabric](03_Microsoft_Fabric.md)
- **Foundations:** [OLAP/Columnar Storage](../01_Foundations/Fundamentals/02_OLAP_Storage.md) · [Distributed Computing](../01_Foundations/Fundamentals/03_Distributed_Computing.md) · [Dimensional Modeling](../02_Databases/Data_Modeling/03_Dimensional_Modeling.md)
- **Same physics in Spark:** [Joins](../03_Programming/PySpark/07_Joins.md) · [Performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)
- **Interview:** [Synapse Q&A](../Job%20Interviews/Azure%20Synapse/Synapse%20Interview%20Questions.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Table distribution guidance: https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-tables-distribute
- Serverless SQL pool: https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/on-demand-workspace-overview
- Dedicated SQL pool architecture: https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/massively-parallel-processing-mpp-architecture

**Videos**
- Synapse distribution (hash/round-robin/replicated): https://www.youtube.com/results?search_query=synapse+hash+round+robin+replicated+distribution
- Serverless SQL pool tutorial: https://www.youtube.com/results?search_query=synapse+serverless+sql+pool+tutorial
