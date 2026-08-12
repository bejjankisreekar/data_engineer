# Hadoop Architecture

## What is Hadoop?

**Apache Hadoop** is the open-source framework (2006) that made big data practical. It applies [distributed computing](03_Distributed_Computing.md) to two problems at once:

1. **Storing** data too big for one machine → **HDFS**
2. **Processing** that data in parallel → **MapReduce** (managed by **YARN**)

It was inspired by Google's GFS and MapReduce papers, and its core bet was: use hundreds of **cheap commodity machines** and let the software handle their constant failures.

---

## The three core components

```
┌────────────────────────────────────────────┐
│           MapReduce  (processing)           │
├────────────────────────────────────────────┤
│           YARN  (resource management)       │
├────────────────────────────────────────────┤
│           HDFS  (distributed storage)       │
└────────────────────────────────────────────┘
```

---

## 1. HDFS — Hadoop Distributed File System

**Job:** store enormous files across many machines and survive machine failure.

How a 1 GB file is stored:

1. The file is chopped into **blocks** (default 128 MB → 8 blocks).
2. Each block is copied to **3 different DataNodes** (replication factor 3).
3. The **NameNode** remembers which blocks live where.

```
                ┌──────────────┐
                │   NameNode    │  MASTER — metadata only:
                │ (file → block │  "file.csv = blocks B1..B8,
                │    → node map)│   B1 lives on nodes 2,5,7"
                └──────┬───────┘
        ┌──────────┬───┴──────┬──────────┐
   ┌────▼────┐ ┌───▼─────┐ ┌──▼──────┐ ┌─▼───────┐
   │DataNode1│ │DataNode2│ │DataNode3│ │DataNode4│   WORKERS — hold the
   │ B1  B4  │ │ B1  B2  │ │ B2  B3  │ │ B1  B3  │   actual data blocks
   └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

- Classic [master–slave architecture](04_Master_Slave_Architecture.md): NameNode = master, DataNodes = workers.
- If DataNode3 dies, every block it held still exists on 2 other nodes; HDFS re-replicates to get back to 3 copies.
- The NameNode is protected by a **Standby NameNode** (it's otherwise a single point of failure).

---

## 2. YARN — Yet Another Resource Negotiator

**Job:** decide which application gets how much CPU/RAM on the cluster.

- **ResourceManager** (master) — receives job requests, allocates resources.
- **NodeManager** (one per worker) — launches and monitors **containers** (boxes of CPU + RAM) on its machine.

YARN made Hadoop a general platform: MapReduce, [Spark](../../03_Programming/PySpark/Spark_Architecture.md), Hive and others can all run on the same cluster, sharing resources.

---

## 3. MapReduce — the original processing engine

**Job:** process data in parallel using two simple phases.

Example: count word frequency across millions of documents.

```
Input blocks     MAP phase              SHUFFLE           REDUCE phase
(on each node)   (runs where data is)   (group by key)    (aggregate)

 block 1  ───▶  (cat,1)(dog,1)  ─┐
 block 2  ───▶  (cat,1)(cat,1)  ─┼──▶  cat:[1,1,1] ───▶  cat: 3
 block 3  ───▶  (dog,1)         ─┘     dog:[1,1]   ───▶  dog: 2
```

- **Map** — each node transforms its local chunk into key–value pairs (data locality: code goes to the data).
- **Shuffle** — pairs with the same key are moved to the same node (the expensive network step).
- **Reduce** — each node aggregates the values for its keys.

**The catch:** MapReduce writes results **to disk after every stage**. A multi-step job = read disk, process, write disk, repeat. Reliable, but *slow* — this weakness is exactly what Spark fixed (see [Why_Spark_Why_Databricks.md](../../08_Databricks/02_Why_Spark_Why_Databricks.md)).

---

## The Hadoop ecosystem (names you'll hear)

| Tool | Purpose |
|---|---|
| **Hive** | SQL on top of Hadoop (queries compile to MapReduce/Spark jobs) |
| **Pig** | Scripting language for data flows |
| **HBase** | NoSQL database on HDFS |
| **Sqoop** | Import/export between databases and HDFS |
| **Oozie** | Job scheduling |
| **Zookeeper** | Cluster coordination |

---

## Hadoop today

On-prem Hadoop clusters are fading, but the ideas live on everywhere:

- HDFS → cloud data lakes ([Azure Data Lake Storage](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md), S3)
- MapReduce → [Spark](../../03_Programming/PySpark/What_Is_Apache_Spark.md)
- YARN → Kubernetes / managed cloud clusters (Databricks)
- Hive → Databricks SQL, Synapse, Snowflake

Understanding Hadoop is understanding *why* modern tools look the way they do — see [06_Big_Data_Evolution_Timeline.md](06_Big_Data_Evolution_Timeline.md).

---
---

# Part 2 — Advanced

## HDFS internals worth knowing

**Read path:** client asks NameNode "where is block B1?" → gets a list of DataNodes sorted by proximity → streams the block **directly from the DataNode** (data never flows through the NameNode).

**Write path:** client gets a pipeline of 3 DataNodes → streams the block to DN1, which forwards to DN2, which forwards to DN3 → acks flow back. One network hop per replica, chained.

**Rack awareness:** replicas are placed as *(local node, same rack, different rack)* — so losing an entire rack (top-of-rack switch failure) still leaves a copy elsewhere.

**NameNode memory math (why small files kill Hadoop):** every file/block object costs ~150 bytes of NameNode **heap**. 100 million small files ≈ 30+ GB of metadata RAM, regardless of data size:

| Scenario | Files | Blocks | NameNode objects |
|---|---|---|---|
| 1 TB as 8,000 × 128 MB files | 8k | 8k | ~16k ✅ |
| 1 TB as 10 million × 100 KB files | 10M | 10M | ~20M ❌ |

This is the **small files problem** — it also makes MapReduce/Spark spawn one task per file, drowning in scheduling overhead. Fixes: compact files (aim 128 MB–1 GB), use container formats, or in modern stacks run `OPTIMIZE` on Delta tables.

**Erasure Coding (Hadoop 3):** instead of 3× replication (200% overhead), stripe data + parity like RAID (e.g. RS-6-3: 6 data + 3 parity = survives 3 failures at 50% overhead). Trade-off: reconstruction is CPU/network heavy → used for cold data.

## YARN scheduling in practice

The ResourceManager doesn't run jobs — per application it launches an **ApplicationMaster** (in a container) which then negotiates containers for that job's tasks. RM stays lightweight; this is [master delegation](04_Master_Slave_Architecture.md) in action.

Schedulers decide who gets the cluster:

| Scheduler | Policy | Used when |
|---|---|---|
| FIFO | First job takes everything | Toy clusters |
| **Capacity** | Queues with guaranteed % (e.g. etl=60%, adhoc=40%) | Multi-team enterprises |
| **Fair** | All running jobs converge to equal shares | Interactive/shared use |

Concepts that carried into every modern platform: **preemption** (killing containers of over-quota jobs), **speculative execution** (duplicate slow tasks), and resource **containers** (fixed CPU+RAM boxes — the ancestor of Kubernetes pods and Spark executor sizing).

## MapReduce anatomy (one level deeper)

```
InputSplit → Map → [combiner] → partition → sort/spill → SHUFFLE → merge → Reduce → output
```

- **Combiner** — a "mini-reduce" on the map side: turn `(cat,1)(cat,1)(cat,1)` into `(cat,3)` *before* the network. Same idea as Spark's map-side pre-aggregation.
- **Partitioner** — `hash(key) % numReducers` decides which reducer gets a key; a skewed key = one hot reducer (the original **data skew** problem).
- Every arrow above that touches disk is the latency Spark later removed.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Why on-prem Hadoop actually declined (the honest postmortem)

1. **Coupled storage & compute** — to add disk you bought CPUs too; clusters were sized for peak and idle at night. Cloud object storage + elastic compute broke that economics.
2. **Operational weight** — Kerberos, Ranger, ZooKeeper, NameNode HA, version-matrix upgrades: a full-time platform team before the first insight shipped.
3. **HDFS ≠ cheap** at 3× replication vs object storage's ~1.4× erasure-coded pricing.
4. The vendors tell the story: Cloudera+Hortonworks merged (2019); the market moved to Databricks/Snowflake/cloud-native.

**What survived:** the *ideas* (scale-out, data locality→data skipping, YARN→K8s, Hive Metastore→Unity Catalog/Glue) and the *formats* (Parquet/ORC came from this ecosystem).

## Hive & the metastore — the sleeper legacy

Hive's lasting gift isn't its engine; it's the **metastore**: a central map of "table name → schema → files/partitions on storage." Spark, Presto/Trino, Flink all speak it. Its modern descendants (Unity Catalog, AWS Glue Catalog) are direct evolutions — when you `SELECT` a Delta table in Databricks, you're living in Hive's conceptual house.

**Hive-style partitioning** (`/sales/year=2026/month=07/`) is still the on-disk layout convention of the entire lake world — and its classic trap survives too: partition by too fine a key and you recreate the small-files problem.

## Migration patterns (asked in every architecture interview)

| On-prem piece | Azure landing zone |
|---|---|
| HDFS data | [ADLS Gen2](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) (distcp/ADF copy) |
| Hive tables | Delta tables + Unity Catalog |
| MapReduce/Hive jobs | Spark on [Databricks](../../08_Databricks/02_Why_Spark_Why_Databricks.md) (Hive SQL ports ~90% cleanly to Spark SQL) |
| Oozie workflows | [Data Factory](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) / Databricks Workflows |
| HBase | Cosmos DB / HBase on VMs |

Pro tip: migrate *data first, engines second, pipelines last* — and run old + new in parallel with reconciliation checks (row counts, checksums per partition) before cutover.

## Field-tested gotchas

- A **NameNode restart** on a huge cluster can take tens of minutes (block report storm) — plan maintenance windows around it.
- **Default replication ≠ durability policy**: temp/scratch dirs at 3× waste petabytes; archival data at 3× wastes money EC would save.
- **Speculative execution + non-idempotent output** = duplicated side effects. Only safe with committed/atomic output protocols.
- Benchmarks lie: `wordcount` performance says nothing about your 14-join Hive query. Model *your* workload.

## Interview-grade Q&A

- *Why 128 MB blocks?* Large enough to amortize seek/metadata overhead, small enough for parallelism — balances NameNode memory vs task granularity.
- *What happens when a DataNode dies?* Missed heartbeats (~10 min) → NameNode marks it dead → re-replicates its blocks from surviving copies to restore replication factor.
- *Small files problem?* Metadata bloat on the NameNode + one task per file overhead; fix by compaction/containers.
- *Is Hadoop dead?* The distribution model is; the architecture lives on renamed — object storage + Spark + a catalog *is* Hadoop's design, cloud-corrected.

---

## Further Learning — Docs & Videos

**Documentation**
- Apache Hadoop official site: https://hadoop.apache.org/
- HDFS architecture guide: https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html
- YARN architecture: https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html
- MapReduce tutorial: https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html

**Videos**
- Hadoop architecture explained (HDFS/YARN/MapReduce): https://www.youtube.com/results?search_query=hadoop+architecture+hdfs+yarn+mapreduce+explained
- Hadoop in 10 minutes: https://www.youtube.com/results?search_query=hadoop+explained+for+beginners
