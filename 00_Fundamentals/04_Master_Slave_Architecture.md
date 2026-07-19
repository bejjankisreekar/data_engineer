# Master–Slave Architecture

> Also called **master–worker**, **leader–follower**, or **driver–executor** in modern tools. Same idea, different names.

## What is it?

A design pattern for [distributed systems](03_Distributed_Computing.md): **one node coordinates** (the master), and **many nodes do the actual work** (the slaves/workers).

- The **master** never processes the data itself. It splits the job, assigns tasks, tracks progress, and handles failures.
- The **workers** each process their assigned chunk and report back.

---

## Analogy: a construction site

- **Master = site supervisor.** Holds the blueprint, decides who builds which wall, checks progress, reassigns work if someone calls in sick. Doesn't lay bricks.
- **Workers = the crew.** Each builds their assigned section and reports when done.

One supervisor can coordinate a huge crew — but if the supervisor disappears and there's no backup, the whole site stalls. That weakness has a name: **single point of failure (SPOF)**.

---

## Responsibilities

| Master node | Worker nodes |
|---|---|
| Accepts the job from the client | Execute assigned tasks |
| Splits work into tasks | Store / read their share of the data |
| Assigns tasks to workers | Send heartbeats ("I'm alive") |
| Monitors heartbeats, detects dead workers | Report results / status |
| Re-assigns tasks from failed workers | |
| Combines / finalizes results | |

---

## Where you'll see this pattern

| System | Master | Workers |
|---|---|---|
| HDFS ([Hadoop storage](05_Hadoop_Architecture.md)) | NameNode | DataNodes |
| YARN (Hadoop compute) | ResourceManager | NodeManagers |
| [Apache Spark](../06_PySpark/Spark_Architecture.md) | Driver | Executors |
| Kafka | Controller broker | Brokers |
| Databases (replication) | Primary | Replicas |

The pattern is everywhere — learn it once and every big data architecture diagram becomes readable.

---

## Strengths and weaknesses

**Strengths**
- Simple to reason about: one place makes all the decisions.
- Easy fault handling for workers: master just re-assigns their tasks.
- Scales workers horizontally: need more power → add more workers.

**Weaknesses**
- The master is a **single point of failure** → real systems run a standby master (e.g. HDFS Standby NameNode) that takes over automatically.
- The master can become a **bottleneck** if the cluster gets huge (too many workers to coordinate, too much metadata to track).

---

## Picture

```
                 ┌──────────────┐
     Client ───▶ │    MASTER     │  (plans, assigns, monitors — no data work)
                 └──────┬───────┘
        heartbeats ▲    │ tasks
          results  │    ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │Worker 1│  │Worker 2│  │Worker 3│  │Worker 4│   (do the actual work)
   └────────┘  └────────┘  └────────┘  └────────┘
```

> **Note on terminology:** the industry is moving away from "master/slave" toward *leader/follower* or *primary/replica* — you'll see both in docs and interviews.

---
---

# Part 2 — Advanced

## Making the master not die: High Availability (HA) patterns

The single point of failure is solved in layers:

1. **Active–passive standby** — a second master stays warm, replicating the active master's state. On failure it takes over.
   - HDFS: Active NameNode + **Standby NameNode**, sharing an edit log via **JournalNodes** (quorum of 3+).
2. **Leader election** — who decides the standby should take over? A coordination service (**ZooKeeper**, etcd) runs a quorum vote; whoever grabs the lock becomes leader.
3. **Fencing** — before promoting the standby, the old master must be *provably* stopped (its access revoked / node powered off), or you get **split-brain**: two masters accepting conflicting writes. This is the most feared failure mode in HA design.

```
        ZooKeeper quorum (3 nodes)
        "who holds the leader lock?"
          │ elects
   ┌──────▼──────┐    state replication    ┌─────────────┐
   │ ACTIVE master│ ─────────────────────▶ │STANDBY master│
   └─────────────┘   (fails → standby      └─────────────┘
                      wins election, old
                      master is fenced)
```

## Replication: sync vs async (the master's other job)

When the master also owns data (primary database), it replicates to followers:

| Mode | Guarantee | Cost |
|---|---|---|
| **Synchronous** | Commit waits until replica confirms → zero data loss on failover | Higher write latency; stalls if replica is slow |
| **Asynchronous** | Commit returns immediately | Failover may lose the last seconds of writes (**RPO > 0**) |
| **Semi-sync / quorum** | Wait for *k of n* replicas | The practical middle ground (Kafka `acks=all` + `min.insync.replicas`) |

Two pro vocabulary terms: **RPO** (how much data you may lose) and **RTO** (how long failover takes). Business stakeholders understand these even when they don't know what a replica is.

## Scaling the master itself

When one coordinator can't cope:

- **Federation** — multiple masters, each owning a namespace slice (HDFS Federation: NameNode A owns `/sales`, B owns `/logs`).
- **Delegation** — master hands per-job coordination to sub-masters (YARN: ResourceManager spawns an **ApplicationMaster** per job — so the RM only does high-level arbitration).
- **Metadata sharding** — the "master" becomes a distributed service itself (e.g. cloud object stores' metadata layers).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The alternative: masterless (peer-to-peer) architectures

Not everything has a master. **Cassandra / DynamoDB-style** systems make every node equal:

- Data placement by **consistent hashing** on a ring — any node can accept any request and route it.
- Cluster state spreads by **gossip protocol** (each node periodically exchanges state with random peers).
- Consistency is **tunable per query**: with N=3 replicas, read quorum R + write quorum W where `R + W > N` gives strong reads (e.g. W=2, R=2).

Trade-off vs master-based: no single bottleneck or SPOF, but no single source of truth either — conflict resolution (last-write-wins, vector clocks, CRDTs) becomes your problem.

| | Master-based | Masterless |
|---|---|---|
| Metadata truth | One place (simple) | Emergent (complex) |
| Failure of "the" node | Failover event | Non-event |
| Consistency | Easy to reason about | Tunable, subtle |
| Examples | HDFS, Spark, Kafka(+controller) | Cassandra, Dynamo, Riak |

## Where the pattern hides in your daily tools

- A **Spark driver** is a per-application master — and in most deployments it is *not* HA: driver dies → job dies → your orchestrator's **retry policy is the real HA layer**. Design jobs to be re-runnable (idempotent).
- **Kafka** replaced its ZooKeeper dependency with **KRaft** (built-in Raft consensus) — same leader/follower idea, one less system to operate.
- **Databricks** hides all of this: its control plane is the "master of masters" managing your clusters' drivers.

## Field-tested gotchas

- **Heartbeat tuning is a trade-off**: aggressive timeouts → false failovers during GC pauses ("the 30-second stop-the-world that fired a failover" is a classic postmortem); lazy timeouts → minutes of downtime.
- **Test failover on purpose** (chaos engineering). An HA setup that has never failed over in anger usually doesn't work.
- **The master's metadata is the crown jewel** — losing HDFS NameNode metadata means the cluster's blocks become meaningless bytes. Back up the metadata separately from the data.
- Monitoring the master ≠ monitoring the cluster: track *worker-perceived* master health (are heartbeats being acknowledged?), not just "process is up."

## Interview-grade Q&A

- *What is split-brain and how is it prevented?* Two nodes both believing they're leader after a partition; prevented by quorum-based election + fencing the old leader.
- *Sync vs async replication?* Sync = no data loss, slower writes; async = fast writes, possible loss on failover. Choose per RPO.
- *Is the Spark driver a SPOF?* Yes, per application — mitigated by cluster-mode supervision/retries and idempotent job design, not by driver HA.
- *When would you choose a masterless design?* Write-heavy, always-on, globally distributed workloads where availability beats single-source-of-truth simplicity.
