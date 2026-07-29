# Spark Architecture

## The big picture

A Spark application follows the classic [master–worker pattern](../../01_Foundations/Fundamentals/04_Master_Slave_Architecture.md):

```
                    ┌───────────────────────┐
   your code ────▶  │        DRIVER          │  (master: plans & coordinates)
                    │  - SparkSession        │
                    │  - builds the DAG      │
                    │  - schedules tasks     │
                    └──────────┬────────────┘
                               │ via Cluster Manager
             ┌─────────────────┼─────────────────┐
      ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
      │  EXECUTOR 1  │   │  EXECUTOR 2  │   │  EXECUTOR 3  │   (workers)
      │ cores + RAM  │   │ cores + RAM  │   │ cores + RAM  │
      │ task task    │   │ task task    │   │ task task    │
      │ [cache]      │   │ [cache]      │   │ [cache]      │
      └─────────────┘   └─────────────┘   └─────────────┘
```

---

## The components

### Driver (the master)

The process that runs your `main()` / notebook. It:

1. Creates the **SparkSession** — your entry point to Spark.
2. Turns your DataFrame code into a **logical plan → optimized plan → DAG** of stages and tasks.
3. Asks the cluster manager for executors.
4. **Schedules tasks** onto executor cores and tracks their progress.
5. Collects final results (or confirms the write finished).

The driver does *no heavy data processing itself* — if you call `.collect()` on a huge DataFrame you force all data into the driver's memory and crash it. Classic beginner mistake.

### Executors (the workers)

JVM processes on worker nodes. Each executor has a fixed number of **cores** and amount of **RAM**, and it:

- Runs **tasks** (one task = one partition of data on one core)
- Holds cached DataFrames in memory (`df.cache()`)
- Reports status/heartbeats to the driver

If an executor dies, the driver simply reruns its tasks elsewhere — [fault tolerance](../../01_Foundations/Fundamentals/03_Distributed_Computing.md) in action.

### Cluster Manager

Decides which physical machines provide the executors. Options:

| Cluster manager | Where you see it |
|---|---|
| **Standalone** | Simple built-in option |
| **YARN** | [Hadoop clusters](../../01_Foundations/Fundamentals/05_Hadoop_Architecture.md) |
| **Kubernetes** | Modern container platforms |
| **Databricks** | Manages all this for you — you just pick cluster size |

---

## How a job actually runs

```
Your code:   df.filter(...).groupBy("region").sum("amount").write.parquet(...)

1. JOB       created when the action (.write) fires
2. STAGES    the job splits at shuffle boundaries:
             Stage 1: read + filter          (narrow — no data movement)
             Stage 2: groupBy + sum          (wide — needs a shuffle)
3. TASKS     each stage = one task per partition
             200 partitions → 200 tasks, run in parallel across executor cores
```

- **Job** — one action.
- **Stage** — a group of tasks that can run without moving data between nodes. A **shuffle** (needed by groupBy, join, orderBy) ends one stage and starts the next.
- **Task** — the smallest unit: process one partition on one core.

More on lazy evaluation, transformations, and shuffles in [Spark_Processing.md](Spark_Processing.md).

---

## Worked example

Cluster: 3 executors × 4 cores = **12 cores total**.
Input: a file that splits into **48 partitions**.

- Stage runs 48 tasks; 12 run at a time → 4 "waves" of tasks.
- Want it faster? More executors (more cores) → more tasks in parallel.

This is [scale-out](../../01_Foundations/Fundamentals/03_Distributed_Computing.md) made concrete: performance is roughly `partitions processed in parallel = total executor cores`.

---

## Quick reference

| Term | One-liner |
|---|---|
| SparkSession | Your handle to the cluster (`spark`) |
| Driver | Plans and coordinates; runs your code |
| Executor | Does the work; holds cache |
| Cluster manager | Provides the machines |
| Job | One action's worth of work |
| Stage | Tasks between shuffles |
| Task | One partition on one core |
| DAG | The dependency graph of stages Spark builds from your code |

---
---

# Part 2 — Advanced

## Deploy modes: where does the driver live?

| Mode | Driver runs… | Used for |
|---|---|---|
| **Client mode** | In *your* process (notebook, laptop, edge node) | Interactive work — Databricks notebooks attach this way |
| **Cluster mode** | Inside the cluster, managed by the cluster manager | Production jobs — survives your laptop closing; manager can restart it |
| Local mode | Everything in one JVM (`local[*]`) | Unit tests, learning |

Corollary: in client mode, a flaky VPN kills your job; in cluster mode, logs live on the cluster — know where to look.

## Executor memory model (why OOM happens where it does)

Inside one executor JVM (simplified, Spark's unified memory manager):

```
┌──────────────────────────────────────────┐
│ Reserved (~300MB)                         │
│ User memory (~40%)      ← your objects,   │
│                           UDF overhead    │
│ Unified region (~60%)                     │
│   ├─ Execution memory  ← joins, sorts,    │
│   │                      aggregations     │
│   └─ Storage memory    ← cache/broadcast  │
│      (borrow from each other dynamically; │
│       execution can evict cached blocks)  │
└──────────────────────────────────────────┘
   + off-heap (Tungsten) + Python worker memory (PySpark UDFs live OUTSIDE the JVM heap!)
```

Practical readings:

- **Executor OOM during a join/aggregation** → too few partitions (each task's slice too big) or skew — repartition/salt before throwing RAM at it.
- **"Memory" errors in PySpark UDF-heavy jobs** are often the *Python* worker, controlled by `spark.executor.memoryOverhead` / `spark.executor.pyspark.memory` — invisible if you only stare at JVM settings.
- When execution memory runs short, Spark **spills to disk** — the job survives but crawls; spill metrics in the UI are your early-warning sign.

## Sizing executors: the classic recipe

For a node with 16 cores / 64 GB (leave 1 core + ~1 GB for the OS/daemons):

- **~5 cores per executor** is the sweet spot (HDFS/ADLS client throughput degrades beyond that; too many cores also share one heap badly) → 3 executors × 5 cores.
- Memory: 63 GB / 3 ≈ 21 GB → minus ~10% overhead → `--executor-memory 19g`.
- **1-core executors** waste broadcast/cache reuse (each executor holds its own copy); **15-core executors** get GC pauses and HDFS throttling. Databricks autoscaling mostly hides this, but the reasoning still explains job behavior.

## Dynamic allocation & the shuffle problem

**Dynamic allocation** grows/shrinks executor count with the task backlog — the basis of Databricks autoscaling. The catch: a departing executor holds **shuffle files** other stages still need. Solutions: an external/remote shuffle service, or decommissioning that migrates shuffle blocks first. This single issue is why "just autoscale everything" occasionally re-runs whole stages ("FetchFailed" → stage retry).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The Spark UI — where every real investigation starts

| Tab | Question it answers |
|---|---|
| **Jobs/Stages** | Which stage eats the time? Straggler tasks? (max task time ≫ median = **skew**) |
| **Stage detail** | Shuffle read/write sizes, **spill** (memory/disk) per task |
| **SQL/DataFrame** | The physical plan as executed — with real row counts per operator (AQE-updated) |
| **Executors** | Dead executors, GC time (>10% = memory pressure), storage used |
| **Storage** | What's actually cached, and how much of it *fit* |

Pro reflex on any slow job: UI → find the dominant stage → look at its shuffle + skew + spill numbers *before* touching any config.

## Failure semantics — what dies when?

- **Task fails** → retried (default 4×) on another executor; only then the stage fails.
- **Executor dies** → its tasks rerun elsewhere; lost cached partitions recompute via lineage; lost *shuffle output* forces partial stage re-execution.
- **Driver dies** → application over. The driver is the [master and SPOF](../../01_Foundations/Fundamentals/04_Master_Slave_Architecture.md); production HA = orchestrator retries + **idempotent jobs**, not driver resurrection.
- **`FetchFailedException`** in logs = an executor asked a dead peer for shuffle data — the visible symptom of executor churn (spot VM eviction, OOM kills).

## How Databricks maps onto this architecture

- **Control plane** (Databricks' account) hosts the UI/API/job scheduler; **compute plane** (your subscription) runs driver + executor VMs — data never transits the control plane.
- Cluster types: **all-purpose** (interactive, shared, expensive to forget on) vs **job clusters** (spun per run, die after — the production default) vs **SQL warehouses** (Photon-powered, for BI) vs **serverless** (Databricks-managed compute plane, seconds to start).
- **Photon** replaces the JVM execution layer with vectorized C++ — same plans, same API, ~2–4× on SQL-shaped work; you enable it per cluster, not per query.
- Driver node size matters on Databricks too: huge `collect()`s, many concurrent notebook users, and Delta transaction planning all land on the driver.

## Field-tested gotchas

- **Everything serialized between driver and executors must be picklable/serializable** — a lambda closing over a DB connection object fails at run time, on the cluster, not on your laptop.
- Too-large broadcast (default threshold 10 MB, sometimes raised to GBs) can OOM *every* executor simultaneously — the failure looks like a cluster-wide crash.
- One giant executor per node ≠ faster: GC pauses scale superlinearly with heap; several mid-size executors usually beat one 200 GB monster.
- Logs for a dead executor live on that node — centralize (cluster log delivery to [ADLS](../../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)) or the evidence disappears with the VM.

## Interview-grade Q&A

- *Client vs cluster mode?* Where the driver runs: with you (interactive, fragile) vs in the cluster (production, supervised).
- *An executor keeps OOM-ing — first three suspects?* Skewed partition, under-partitioned shuffle (too much per task), oversized broadcast. RAM increase is the fourth resort.
- *What exactly does the cluster manager NOT do?* Task scheduling — that's the driver. The manager only leases containers/VMs (resource arbitration).
- *Why are job clusters preferred in production?* Clean known state per run, right-sized per workload, auto-terminate — no shared-state bugs or idle burn.

---

## Further Learning — Docs & Videos

**Documentation**
- Spark cluster mode overview: https://spark.apache.org/docs/latest/cluster-overview.html
- Driver, executors, and cluster manager: https://spark.apache.org/docs/latest/cluster-overview.html#components
- Databricks architecture: https://docs.databricks.com/en/getting-started/overview.html

**Videos**
- Spark architecture explained (driver, executors, DAG): https://www.youtube.com/results?search_query=spark+architecture+driver+executor+dag+explained
