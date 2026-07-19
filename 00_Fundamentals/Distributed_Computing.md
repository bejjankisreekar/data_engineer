# Distributed Computing

## The problem it solves

One machine has limits: only so much CPU, RAM, and disk. When data grows beyond what one machine can store or process in reasonable time, you have two options:

- **Scale UP (vertical scaling)** — buy a bigger machine. Works until it doesn't: cost grows faster than power, and there's a hard ceiling.
- **Scale OUT (horizontal scaling)** — buy *many* ordinary machines and make them work together. No ceiling: need more power, add more machines.

**Distributed computing = scale out.** A group of machines (a **cluster**) cooperating over a network to act like one giant computer.

---

## Analogy: counting votes

Imagine counting 10 million paper votes.

- One person counting alone = a single machine. Accurate but takes weeks.
- 1,000 people each counting one box, then reporting subtotals to a supervisor who adds them up = a cluster. Same result, hours instead of weeks.

That "split the work, do it in parallel, combine the results" pattern is the heart of every distributed system, including [Hadoop](Hadoop_Architecture.md) and [Spark](../06_PySpark/Spark_Architecture.md).

---

## Key vocabulary

| Term | Meaning |
|---|---|
| **Node** | One machine in the cluster |
| **Cluster** | The group of nodes working together |
| **Partition / split** | One chunk of the data, small enough for one node to handle |
| **Parallelism** | Many nodes processing different chunks at the same time |
| **Data locality** | Send the *computation to the data* (cheap) instead of moving data to the computation (expensive) |
| **Shuffle** | Redistributing data between nodes mid-job (e.g. for GROUP BY) — the expensive part |
| **Fault tolerance** | The cluster keeps working even when individual nodes fail |

---

## The three hard problems

Distributed systems must solve problems a single machine never has:

1. **Coordination** — who does which chunk? Who combines results?
   → Usually solved with a [master–slave architecture](Master_Slave_Architecture.md): one coordinator node, many worker nodes.

2. **Failure** — with 1,000 cheap machines, *something* is always broken.
   → Solved by replication (keep 3 copies of every data block) and by re-running failed tasks on another node.

3. **Data movement** — networks are slow compared to local disk/RAM.
   → Solved by data locality and by minimizing shuffles.

---

## Why this matters for big data

The "big data" insight of the 2000s (Google's GFS/MapReduce papers → [Hadoop](Hadoop_Architecture.md)) was:

> Instead of one expensive supercomputer, use hundreds of **cheap commodity machines**, accept that they fail constantly, and build the *software* to handle failure automatically.

Everything a data engineer touches at scale — HDFS, Spark, Kafka, Snowflake, Azure Data Lake — is a distributed system built on these ideas. See the full story in [Big_Data_Evolution_Timeline.md](Big_Data_Evolution_Timeline.md).

---

## Simple picture

```
                 ┌────────────┐
                 │ Coordinator │  ← splits the job, tracks progress
                 └─────┬──────┘
       ┌───────────┬───┴───────┬───────────┐
   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
   │Worker 1│   │Worker 2│   │Worker 3│   │Worker 4│   ← each processes its own chunk
   └───────┘   └───────┘   └───────┘   └───────┘
                 (results combined at the end)
```

---
---

# Part 2 — Advanced

## The cost hierarchy every distributed design obeys

```
CPU cache   ~1 ns      │ fastest
RAM         ~100 ns    │
SSD         ~100 µs    │
Network     ~0.5–10 ms │
Cross-region network   ▼ slowest (+ egress fees in cloud)
```

Every big data optimization is a restatement of one rule: **do work where the data already is; move as few bytes as possible.** Data locality, partition pruning, broadcast joins, columnar formats — all of them exist to climb this hierarchy.

## Amdahl's law — why 100 machines ≠ 100× faster

If 10% of a job is inherently serial (a final merge, a driver-side step), then even with infinite workers the maximum speed-up is 10×. Practical corollaries:

- The **slowest task decides the stage time** — one straggler node holds up 999 finished ones.
- **Speculative execution** fights stragglers: the coordinator launches a duplicate of a slow task on another node and takes whichever finishes first (Hadoop and Spark both do this).

## Data skew — the classic real-world failure

Split 1 TB by `customer_id` and one mega-customer owns 40% of rows → one worker gets 400 GB while others get 2 GB. The job is "99% done" for hours.

Fixes pros reach for: **salting** keys (append a random suffix to split the hot key, aggregate in two steps), broadcast the small side of a join, or pre-aggregate before shuffling. (Concrete Spark techniques: [Spark_Processing.md](../06_PySpark/Spark_Processing.md).)

## Coordination and consensus

Distributed systems need agreement on "who is the leader?" and "what is the current state?" even while nodes crash:

- **Heartbeats + timeouts** detect failure (imperfectly — a slow node looks identical to a dead one).
- **Consensus protocols** — **Paxos**, **Raft**, ZooKeeper's **ZAB** — let a majority (**quorum**) of nodes agree on a value even if a minority fails. A 5-node quorum system survives 2 failures.
- **Split-brain** — the nightmare where a network partition creates *two* leaders both accepting writes. Quorums + **fencing** (old leader is forcibly blocked) prevent it.

## The CAP theorem

During a network **P**artition, a system must choose between **C**onsistency (every read sees the latest write) and **A**vailability (every request gets an answer):

| Choice | Behavior during partition | Examples |
|---|---|---|
| **CP** | Reject requests rather than serve stale data | HDFS NameNode, ZooKeeper, Spanner-style DBs |
| **AP** | Keep answering, reconcile later ("eventual consistency") | Cassandra, DynamoDB (tunable), DNS |

Cloud object stores (S3, [ADLS](../03_Data_Storage/Azure_Data_Lake_Storage.md)) are now **strongly consistent** for reads-after-write — a real change from early S3 that used to break pipelines.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Delivery semantics — the "exactly-once" question

When work is retried after failures, the same record can be processed twice:

- **At-most-once** — fire and forget; may lose data.
- **At-least-once** — retry until acknowledged; may duplicate data. *(the common default)*
- **Effectively exactly-once** — at-least-once **+ idempotent writes** (MERGE by key, transactional sinks, dedupe by event id).

Pro reflex: assume at-least-once everywhere and make every pipeline **idempotent** — re-running any day/batch must produce the same result, not double rows.

## MPP vs MapReduce-style engines

- **MPP warehouses** (Synapse Dedicated, Teradata, Redshift): long-lived tightly-coupled nodes, pipelined execution, brilliant for SQL, historically fragile if a node dies mid-query.
- **DAG engines** ([Spark](../06_PySpark/Spark_Architecture.md)): stage-by-stage with recoverable intermediate state — slower per-query than ideal MPP, but resilient and general-purpose. Modern systems blur the line (Photon, AQE).

## When NOT to distribute

Distribution buys scale and pays in coordination overhead, shuffles, and operational complexity. A 50 GB dataset fits in RAM on one modern machine — DuckDB/Polars/pandas will beat a Spark cluster on it, in both speed and cost. The pro question is never "how do I use the cluster?" but **"do I need a cluster at all?"**

## Field-tested gotchas

- **Retries without idempotency** are the #1 source of duplicated data in real pipelines.
- **Timeouts too low** turn a slow-but-healthy system into a cascading failure (retry storms). Use exponential backoff + jitter.
- **Clock skew** across nodes breaks naive event ordering — order by log offsets or logical clocks, not wall time.
- **"It works on 1 GB"** proves nothing about 1 TB: skew, shuffle spills, and small-file explosions only appear at scale. Test with production-shaped data.

## Interview-grade Q&A

- *Scale up vs scale out?* Up = bigger machine (simple, ceiling-limited). Out = more machines (unlimited, but adds coordination/failure/network problems).
- *What is a quorum?* A majority of nodes that must agree before an operation counts — lets the system make progress despite minority failures.
- *How do you handle a straggler task?* Speculative execution; if it's skew-driven, fix the partitioning/salting instead.
- *CAP in one line?* Under a network partition you can't have both perfect consistency and full availability — pick per use case.
