# 00_Fundamentals — Interview Questions & Answers

## How to use this file

This file pairs with the six notes in this folder and drills the material the way an interviewer actually asks about it. Questions come in two flavors, often mixed within the same section:

- **THEORY** — definitions, comparisons, and "explain X" questions (e.g. "OLTP vs OLAP?"). These check whether you understand the concept, not just the buzzword.
- **PRACTICAL / SCENARIO** — "design this," "walk me through what happens when X fails," "why did this architecture choice get made" questions. These check whether you can *apply* the concept, not just recite it.

Every question explains *why* an interviewer asks it, and every answer explains *why* it's correct — the reasoning is often what's actually being evaluated.

Two difficulty tags are used, roughly matching the Basics/Advanced/Pro structure of the source notes:

- **[Frequently Asked]** — core concepts almost every data engineering interview touches: OLTP vs OLAP, scale up vs scale out, the master-slave pattern, why Hadoop lost popularity, the big data evolution story.
- **[Senior/Experienced]** — deeper, Pro-level questions: MVCC/isolation levels, CAP theorem, split-brain and fencing, HDFS internals, Lambda vs Kappa. Expect these once you claim 3+ years of experience.

Untagged questions sit in between — solid mid-level material everyone should be able to answer.

---

## Table of Contents

1. [OLTP Storage](#1-oltp-storage)
2. [OLAP Storage](#2-olap-storage)
3. [Distributed Computing](#3-distributed-computing)
4. [Master–Slave Architecture](#4-masterslave-architecture)
5. [Hadoop Architecture](#5-hadoop-architecture)
6. [Big Data Evolution Timeline](#6-big-data-evolution-timeline)
7. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. OLTP Storage

*(full notes: [01_OLTP_Storage.md](01_OLTP_Storage.md))*

#### Q1. What is OLTP, and what kind of workload is it optimized for? **[Frequently Asked]**
*Why interviewers ask this:* A universal opener — checks baseline vocabulary before going anywhere deeper.
**Answer:** OLTP (Online Transaction Processing) is the storage pattern behind everyday applications — systems recording transactions as they happen: an order placed, a payment made, a login. It's optimized for many small, fast reads and writes with perfect accuracy — thousands of users touching a few rows each, in milliseconds, all at once. This is correct because it names both the *workload shape* (many small operations) and the *guarantee* (accuracy under concurrency), which together define what makes a database "OLTP" rather than just "a database."

#### Q2. Why do OLTP databases store data row-by-row instead of column-by-column? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether you connect a storage decision to the actual access pattern it serves, not just memorized trivia.
**Answer:** An application asking "fetch order #2" or "insert this new order" needs the *entire record* in one go — every column for that one row. Row-based storage keeps a full row physically together on disk, so reading or writing one record is one contiguous operation. Column storage would scatter that single row's fields across separate column files, making a single-row fetch slower, not faster. This is correct because it matches the storage layout to the actual query shape (whole records, few at a time) rather than analytical scans (few columns, many rows) — the opposite shape that justifies [OLAP's](02_OLAP_Storage.md) columnar layout.

#### Q3. Explain ACID with a real-world example. **[Frequently Asked]**
*Why interviewers ask this:* Nearly guaranteed in some form — checks that you can explain each letter concretely, not just recite the acronym.
**Answer:** ACID is the safety guarantee OLTP systems make about transactions: **Atomic** — a ₹500 transfer either fully happens (debit + credit) or not at all, never half; **Consistent** — the database always moves from one valid state to another (e.g. a balance can never go negative if that violates a rule); **Isolated** — two people booking the last seat at the same time can't both succeed; **Durable** — once confirmed, the data survives a crash or power cut. This is correct because each letter maps to a distinct failure mode a real banking/booking system must prevent, which is why the interviewer wants an example, not just the expansion of the acronym.

#### Q4. How does a database make a single-row lookup fast on a table with 100 million rows?
*Why interviewers ask this:* Checks whether "fast" is understood mechanically, not just asserted.
**Answer:** Through a **B-tree index** — a sorted, balanced tree built over the lookup column. Instead of scanning all 100 million rows, the engine walks the tree from root to leaf, typically in 3–4 page reads, landing directly on the matching row. Without an index, the same lookup is a full table scan — checking every row. This is correct because it explains the actual data structure behind "milliseconds," which is what separates a real understanding from a hand-wave about "the database being optimized."

#### Q5. What is the Write-Ahead Log (WAL), and why does it matter to a data engineer? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether you understand durability mechanically, and whether you know the WAL's second life as a data-engineering tool (CDC).
**Answer:** Instead of writing changes straight to the data files, the database first appends the change to a sequential **Write-Ahead Log**, then updates data pages in memory (flushed to disk later). Sequential appends are much faster than random writes, giving fast commits; after a crash, the database replays the log to recover every committed transaction — this *is* the "Durable" guarantee in ACID. For a data engineer, this matters because **CDC (Change Data Capture)** tools like Debezium read this exact log to stream every insert/update/delete out to a lake, far cheaper than repeatedly polling the source table with queries. This is correct because it connects a database-internals fact to a concrete data-engineering technique that depends on it.

#### Q6. What is MVCC, and how does it let readers and writers avoid blocking each other? **[Senior/Experienced]**
*Why interviewers ask this:* A step beyond "what is ACID" — checks whether you understand *how* isolation is achieved under real concurrency, not just that it's promised.
**Answer:** Multi-Version Concurrency Control keeps *multiple versions* of a row instead of locking it for readers. A reader sees a consistent snapshot as of when its transaction started; a writer creates a new version rather than overwriting the old one in place. This means a long-running `SELECT` doesn't block a concurrent `UPDATE`, and vice versa — PostgreSQL, Oracle, and SQL Server (via RCSI) all implement this. The trade-off: very long transactions force the database to retain old row versions, causing bloat (PostgreSQL) or version-store growth (SQL Server). This is correct because it explains the actual mechanism (versioning, not locking) that delivers isolation without serializing all access.

#### Q7. Why should a data engineer never run analytics queries directly against the production OLTP database? **[Frequently Asked]**
*Why interviewers ask this:* A very common practical scenario — checks real-world judgment, not just definitions.
**Answer:** A heavy analytical scan competes with the application for locks and, critically, evicts the application's frequently-used data from the buffer pool cache — slowing down both the report *and* the live app it's supposed to leave alone. Row storage also means a `SELECT *`-style analytical scan reads every column even if only a few are needed. The correct pattern is to extract from a **read replica**, off-peak, incrementally (via a watermark or log-based CDC) — never a full-table scan against the primary at 9am. This is correct because it identifies the actual resource contention (cache + locks) rather than a vague "it's slow," and gives the concrete alternative interviewers are listening for.

#### Q8. How would you extract 1 TB of data from a live OLTP system without degrading the application? **[Senior/Experienced]**
*Why interviewers ask this:* A hands-on scenario that separates candidates who've actually operated a pipeline against production from those who've only read about ETL.
**Answer:** Four things together: extract from a **read replica**, not the primary; pull **incrementally** using a watermark (`WHERE modified_at > last_run`) or, better, **log-based CDC** reading the WAL directly, rather than a full scan every run; schedule during **off-peak** hours; and use **partitioned parallel reads** (bounded by a key range) rather than one giant single-threaded query. This is correct because each piece addresses a distinct risk — replica avoids primary contention, incremental avoids re-scanning unchanged data, off-peak avoids user-facing slowdown, and partitioning avoids one connection hogging resources.

---

## 2. OLAP Storage

*(full notes: [02_OLAP_Storage.md](02_OLAP_Storage.md))*

#### Q9. What is OLAP, and how is it different from OLTP? **[Frequently Asked]**
*Why interviewers ask this:* The single most common comparison question in data engineering interviews — a near-guaranteed ask.
**Answer:** OLAP (Online Analytical Processing) is the storage pattern built for analysis — scanning millions or billions of rows to answer questions like "total revenue by region last year." Where OLTP serves the *application* with many small fast transactions on row-based storage, OLAP serves the *analyst* with few, large aggregation queries on column-based storage, tolerating seconds-to-minutes response time over historical, batch-loaded data. This is correct because it contrasts workload shape, storage layout, and freshness together — the three axes interviewers expect in a complete answer, not just "OLAP is for reporting."

#### Q10. Why is columnar storage faster for analytical queries? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether you can explain the *mechanism*, since "columnar is faster" alone is a memorized non-answer.
**Answer:** A query like `SELECT SUM(amount) FROM sales` only needs the `amount` column. Columnar storage keeps each column's values contiguous on disk, so the engine reads only that one column — on a 50-column table, that can mean reading ~2% of the bytes instead of 100%. Columns also compress far better than rows, since similar values (all numbers, all city names) sit next to each other, enabling techniques like dictionary and run-length encoding. This is correct because it names both the pruning benefit (skip unneeded columns) and the compression benefit (similar values compress better) — the two independent reasons columnar wins, not just one.

#### Q11. Explain the star schema — what are fact and dimension tables?
*Why interviewers ask this:* Core warehouse-modeling vocabulary that comes up in nearly every SQL/warehouse discussion.
**Answer:** A star schema has one central **fact table** holding the numbers — one row per event (e.g. one row per sale, with amount and quantity) — surrounded by **dimension tables** holding the descriptions (product name, store city, calendar date). It's deliberately denormalized so an analyst can join the fact to a handful of dimensions and aggregate quickly, instead of navigating many normalized tables. This is correct because it captures both *what* each table type holds and *why* the design is intentionally denormalized — for query simplicity, at the cost of some duplicated dimension text.

#### Q12. How would you handle a customer's address changing in a dimension table, while preserving historical reporting accuracy? **[Frequently Asked]**
*Why interviewers ask this:* One of the most common warehouse-modeling interview questions — tests whether you know Slowly Changing Dimensions by name and by mechanism.
**Answer:** This is the Slowly Changing Dimension (SCD) problem. **Type 1** simply overwrites the old value — history is lost, fine when the old value never mattered. **Type 2** — the default choice — adds a *new row* for the customer with `valid_from`/`valid_to`/`is_current` columns, so a sale made before the move still joins to the customer's old city. **Type 3** keeps just a `previous_value` column, rarely enough for most needs. Facts join dimensions using a meaningless **surrogate key** (not the natural business key), which is what makes Type 2's multiple rows per customer possible without breaking joins. This is correct because it names the standard technique (SCD Type 2) and explains *why* surrogate keys are a prerequisite for it, which is the detail that separates a memorized answer from an understood one.

#### Q13. Why is running a single-row `UPDATE` considered an anti-pattern in a data warehouse? **[Senior/Experienced]**
*Why interviewers ask this:* Checks understanding of the physical file layer underneath OLAP engines, not just the logical model.
**Answer:** Columnar analytical files (Parquet, ORC) are immutable once written — there's no in-place edit at the storage layer. A single-row `UPDATE` therefore means rewriting an entire file (or micro-partition) just to change one value, which is enormously wasteful at analytical scale. OLAP writes are meant to be **bulk and append-mostly** — nightly/hourly batch loads, streaming micro-batches, or `MERGE` for upserts — not row-by-row DML. This is correct because it ties the "anti-pattern" claim to the actual physical constraint (file immutability) rather than just asserting warehouses are "bad at updates."

#### Q14. What physical design choices most affect OLAP query performance? **[Senior/Experienced]**
*Why interviewers ask this:* A "how would you tune this" question that tests hands-on warehouse experience.
**Answer:** Four levers matter most: **partitioning** (splitting a table by a column, e.g. year/month, so queries prune whole folders — a one-month query on 3 years of monthly-partitioned data reads 1/36 of the data); **clustering/sort order** (ordering data *within* files, e.g. Z-ORDER on a high-cardinality filter column, so min/max statistics can actually skip blocks); **file sizing** (targeting 100 MB–1 GB files to avoid the small-files problem); and **materialized views/pre-aggregates** for expensive, repeatedly-run rollups. The anti-pattern to flag: partitioning by a high-cardinality column like `customer_id` creates millions of tiny folders — partition low-cardinality columns, cluster high-cardinality ones. This is correct because it separates the two techniques that are often confused (partitioning vs. clustering) and names the specific failure mode of getting them backwards.

#### Q15. Why do modern cloud warehouses separate storage from compute? **[Senior/Experienced]**
*Why interviewers ask this:* Checks understanding of the architectural shift that defines Snowflake/Databricks SQL/BigQuery, a common "why does X exist" question.
**Answer:** Older MPP warehouses (Teradata, Netezza) coupled storage to compute nodes — growing storage capacity meant buying more compute too, and one shared cluster served every workload, so one team's heavy query could slow down another's. Separating them puts data in cheap object storage while compute clusters spin up independently per workload: idle compute can be shut off entirely (the single biggest cost lever in cloud analytics), and one team's load doesn't contend with another's. This is correct because it names the actual coupling that was removed and the two concrete benefits (elastic cost, workload isolation) that resulted — the general pattern of "which coupling did this remove" that also explains most other big-data architecture shifts.

---

## 3. Distributed Computing

*(full notes: [03_Distributed_Computing.md](03_Distributed_Computing.md))*

#### Q16. What's the difference between scaling up and scaling out? **[Frequently Asked]**
*Why interviewers ask this:* Foundational vocabulary — almost every architecture discussion eventually needs this distinction.
**Answer:** **Scaling up** (vertical) means buying a bigger single machine — simple, but with a hard ceiling and cost that grows faster than the power gained. **Scaling out** (horizontal) means using many ordinary machines working together as a cluster — no ceiling, but it introduces coordination, failure handling, and network overhead that a single machine never has. Distributed computing *is* scaling out. This is correct because it states both the benefit and the cost of each approach, which is what a "compare X and Y" question is actually testing — not just which one "wins."

#### Q17. What are the three hard problems every distributed system must solve that a single machine never faces? **[Frequently Asked]**
*Why interviewers ask this:* Checks whether you understand distributed systems as a category of *new* problems, not just "more machines."
**Answer:** **Coordination** — who does which chunk of work, and who combines the results (usually solved with a [master-slave pattern](04_Master_Slave_Architecture.md)); **failure** — with hundreds of cheap machines, something is always broken, solved by replication and re-running failed tasks elsewhere; and **data movement** — networks are slow compared to local disk/RAM, solved by data locality (send computation to the data) and minimizing shuffles. This is correct because these three categories cover essentially every distributed-systems technique discussed elsewhere in this course — they're the "why" behind replication, task retries, and shuffle optimization all at once.

#### Q18. What is data skew, and how would you fix it in a distributed job?
*Why interviewers ask this:* A very common practical scenario question — "your job is stuck at 99% for an hour" is a classic prompt.
**Answer:** Data skew is when one partition holds far more data than the others — e.g. splitting 1 TB by `customer_id` where one mega-customer owns 40% of the rows, so one worker gets 400 GB while the rest get a few GB each. The job appears "99% done" for a long time because every other task finished quickly while the one skewed task keeps grinding. Fixes: **salting** the hot key (append a random suffix to spread it across partitions, aggregate in two steps), **broadcasting** the smaller side of a join instead of shuffling both sides, or **pre-aggregating** before the shuffle happens. This is correct because it identifies the mechanism (uneven partition size) rather than just the symptom (job looks stuck), and gives concrete fixes rather than "add more resources."

#### Q19. Explain the CAP theorem in plain terms. **[Senior/Experienced]**
*Why interviewers ask this:* A classic distributed-systems theory question, often used to filter for genuine depth beyond tool-specific knowledge.
**Answer:** During a network **P**artition (some nodes can't talk to others), a system must choose between **C**onsistency (every read sees the latest write) and **A**vailability (every request gets *an* answer, even if possibly stale). **CP** systems reject requests rather than serve stale data (HDFS NameNode, ZooKeeper); **AP** systems keep answering and reconcile later — "eventual consistency" (Cassandra, DynamoDB). Notably, modern cloud object stores like S3/ADLS are now strongly consistent for reads-after-write, a real improvement over early S3 behavior that used to silently break pipelines. This is correct because it states the actual trade-off (not "pick 2 of 3," a common misphrasing) and grounds it in real systems on each side.

#### Q20. What is a quorum, and why does it matter for distributed coordination? **[Senior/Experienced]**
*Why interviewers ask this:* Tests understanding of how distributed systems agree on anything at all despite node failures — a step beyond just naming CAP.
**Answer:** A quorum is a *majority* of nodes that must agree before an operation counts as successful — e.g. in a 5-node system, a quorum of 3 lets the system keep operating correctly even if 2 nodes fail. Consensus protocols like **Paxos**, **Raft**, and ZooKeeper's **ZAB** use quorums to let a majority agree on a value (like "who is the leader") even while a minority of nodes crash or lose connectivity. This is correct because it explains *why* quorums specifically (not just "voting") guarantee correctness: any two quorums in the same system must overlap by at least one node, which prevents two conflicting decisions from both winning.

#### Q21. What delivery guarantees exist for retried work in a distributed pipeline, and how do you get "exactly-once" in practice? **[Senior/Experienced]**
*Why interviewers ask this:* One of the most important practical questions in the entire course — nearly every real production incident traces back to getting this wrong.
**Answer:** Three levels: **at-most-once** (fire and forget — may silently lose data), **at-least-once** (retry until acknowledged — may duplicate data, and is the common default in most systems), and **effectively exactly-once**, which isn't a separate delivery mechanism but *at-least-once plus idempotent writes* — MERGE by key, transactional sinks, or deduping by an event ID. The professional default is to assume at-least-once everywhere and design every pipeline to be idempotent, so a retried run converges to the same result instead of duplicating rows. This is correct because true "exactly-once" delivery at the network layer is essentially impossible to guarantee in a distributed system — the practical answer is always this combination, which is exactly what interviewers are checking you know.

#### Q22. When would you decide NOT to use a distributed system like Spark for a workload? **[Senior/Experienced]**
*Why interviewers ask this:* A judgment question that separates engineers who reach for the biggest tool by default from those who match tool to problem.
**Answer:** Distribution buys scale but pays for it in coordination overhead, shuffles, and operational complexity. A dataset that comfortably fits in RAM on one modern machine (tens of GB) will often run *faster and cheaper* on a single-node tool like DuckDB, Polars, or pandas than on a Spark cluster, because there's no cluster startup time, no network shuffle, and no coordination tax. The right question isn't "how do I use the cluster" but "do I need a cluster at all." This is correct because it demonstrates cost-aware engineering judgment, which is exactly what's being tested — reflexively distributing everything is a beginner tell, not a sign of expertise.

---

## 4. Master–Slave Architecture

*(full notes: [04_Master_Slave_Architecture.md](04_Master_Slave_Architecture.md))*

#### Q23. Explain the master-slave (leader-follower) pattern and name three real systems that use it. **[Frequently Asked]**
*Why interviewers ask this:* One of the most universally applicable patterns in big data — understanding it once makes almost every architecture diagram readable.
**Answer:** One node (the master/leader) coordinates — it splits work into tasks, assigns them, tracks progress, and handles failures, but never processes data itself. Many worker nodes execute their assigned chunk and report back. Real examples: HDFS (NameNode = master, DataNodes = workers), Spark (Driver = master, Executors = workers), and YARN (ResourceManager = master, NodeManagers = workers). This is correct because it states the master's defining property — it coordinates but doesn't do the data work itself — which is the detail most rote answers miss, and it grounds the pattern in concrete systems rather than only the abstract description.

#### Q24. What is a single point of failure, and how does master-slave architecture create one? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether you see the pattern's core weakness, not just its mechanics.
**Answer:** A single point of failure (SPOF) is a component whose failure brings down the whole system. In master-slave architecture, the master is the SPOF — if it disappears with no backup, the whole cluster stalls even though every worker is still healthy, because nobody is left to coordinate them. Real systems mitigate this with a **standby master** (e.g. HDFS's Standby NameNode) that takes over automatically. This is correct because it names the exact node that's fragile (not "the system" vaguely) and the standard fix, which is the natural follow-up an interviewer expects.

#### Q25. How does HDFS prevent split-brain when failing over from an active to a standby NameNode? **[Senior/Experienced]**
*Why interviewers ask this:* A deep, specific question that filters for candidates who've actually studied HA design, not just heard the term "failover."
**Answer:** Three pieces work together: a coordination service (ZooKeeper) runs a **leader election** — a quorum vote decides who holds the "leader" lock; the active and standby NameNodes share an edit log via **JournalNodes** so the standby's state stays current; and critically, before the standby is promoted, the old master must be **fenced** — provably stopped (access revoked, forcibly powered off) — or you risk **split-brain**, where two nodes both believe they're the leader and accept conflicting writes simultaneously. This is correct because it names fencing specifically as the step that *prevents* split-brain, not just failover in general — omitting fencing is exactly how real split-brain incidents happen.

#### Q26. Synchronous vs asynchronous replication — what's the trade-off? **[Senior/Experienced]**
*Why interviewers ask this:* Connects a database-internals concept to business-facing vocabulary (RPO/RTO) that non-engineers also understand — a favorite for testing communication as well as knowledge.
**Answer:** **Synchronous** replication makes the commit wait until the replica confirms the write — this guarantees zero data loss on failover, at the cost of higher write latency (and the write stalls if the replica is slow). **Asynchronous** replication returns the commit immediately, keeping writes fast, but a failover can lose the last few seconds of writes that hadn't yet reached the replica — a non-zero **RPO** (Recoverable Point Objective, how much data you may lose). Kafka's `acks=all` + `min.insync.replicas` is a practical semi-sync middle ground. This is correct because it frames the choice in terms stakeholders actually care about (RPO) rather than just "sync is safer," and names the real middle-ground option instead of presenting it as a binary choice.

#### Q27. Is the Spark driver a single point of failure? How is that risk actually handled in production? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether master-slave theory connects to a tool the candidate actually uses daily.
**Answer:** Yes — the Spark driver is a per-application master, and in most deployments it is *not* highly available: if the driver dies, the entire job dies with it. The real mitigation isn't driver HA (which most setups don't have) — it's the **orchestrator's retry policy** plus designing every job to be **idempotent**, so a retried run converges to the same correct result instead of duplicating data. This is correct because it resists the tempting-but-wrong answer ("Spark has driver failover") and instead names the actual production practice, which is a strong signal of hands-on experience.

#### Q28. When would you choose a masterless (peer-to-peer) design over master-slave? **[Senior/Experienced]**
*Why interviewers ask this:* Checks whether the candidate knows master-slave isn't the only pattern, and can reason about when the alternative is actually better.
**Answer:** Masterless systems like Cassandra or DynamoDB make every node equal — data placement uses consistent hashing on a ring, cluster state spreads via gossip protocol, and consistency is tunable per query (with N replicas, read quorum R + write quorum W where R+W>N gives strong reads). They trade away a single source of truth (conflict resolution — last-write-wins, vector clocks — becomes the application's problem) for the removal of any single bottleneck or SPOF. The right fit is write-heavy, always-on, globally distributed workloads where availability during a partition matters more than simple, centralized consistency. This is correct because it states the actual trade-off (simplicity vs. availability) rather than declaring one pattern universally better, which is what a mature answer to a "when would you choose X" question should do.

---

## 5. Hadoop Architecture

*(full notes: [05_Hadoop_Architecture.md](05_Hadoop_Architecture.md))*

#### Q29. What are the three core components of Hadoop, and what does each do? **[Frequently Asked]**
*Why interviewers ask this:* A guaranteed baseline question if Hadoop comes up at all — checks that the candidate knows Hadoop is three things, not one monolithic product.
**Answer:** **HDFS** (Hadoop Distributed File System) handles storage — splitting files into blocks (default 128 MB) and replicating each block 3× across DataNodes. **YARN** (Yet Another Resource Negotiator) handles resource management — deciding which application gets how much CPU/RAM on the cluster. **MapReduce** was the original processing engine, running jobs in Map → Shuffle → Reduce phases on top of YARN. This is correct because it separates storage, resource management, and processing as three distinct layers, which is exactly the architecture diagram interviewers expect and the reason Hadoop could later host Spark and Hive on the same YARN-managed cluster.

#### Q30. Walk me through what happens when a DataNode fails in HDFS. **[Frequently Asked]**
*Why interviewers ask this:* A step-by-step scenario question that tests whether the candidate understands the fault-tolerance mechanism, not just that "HDFS is fault tolerant."
**Answer:** The NameNode expects periodic heartbeats from every DataNode; when a DataNode misses heartbeats for a threshold period (roughly 10 minutes by default), the NameNode marks it dead. Because every block was already replicated 3× across different DataNodes, the blocks that lived on the dead node still exist on two surviving nodes — nothing is lost. The NameNode then triggers **re-replication**, copying those blocks to other healthy DataNodes to restore the replication factor back to 3. This is correct because it walks the actual sequence (heartbeat timeout → dead node detection → re-replication) rather than a vague "it recovers automatically," which is what a "walk me through" question is specifically testing.

#### Q31. Why does the "small files problem" hurt Hadoop clusters so badly? **[Senior/Experienced]**
*Why interviewers ask this:* A well-known, specific gotcha that tests real operational knowledge of Hadoop, often used to filter candidates who only know the theory.
**Answer:** Every file/block object costs roughly 150 bytes of NameNode heap memory — the *metadata*, not the data. Storing 1 TB as 10 million 100 KB files costs ~20 million NameNode objects (~3 GB+ of heap), versus the same 1 TB as 8,000 files at 128 MB each costing only ~16,000 objects. Beyond memory pressure, it also makes MapReduce/Spark spawn one task per file, drowning the job in scheduling overhead. The fix is compaction — targeting 100 MB–1 GB files, using container formats, or running `OPTIMIZE` on modern Delta tables. This is correct because it gives the actual numbers behind "kills the NameNode" rather than just asserting it, and it names the concrete fix, which is what distinguishes a memorized fact from applied understanding.

#### Q32. What was the fundamental limitation of MapReduce that Spark was built to fix? **[Frequently Asked]**
*Why interviewers ask this:* Bridges Hadoop to the rest of the course's PySpark content — a very likely interview transition point.
**Answer:** MapReduce writes its results **to disk after every stage** — Map writes to disk, Shuffle reads and writes to disk, Reduce writes to disk again. A multi-step pipeline means repeated disk round-trips at every stage, which is reliable but slow, especially for iterative workloads like machine learning that pass over the same data dozens of times. Spark kept the same distributed, scale-out philosophy but moved intermediate data **in-memory**, avoiding those disk round-trips — 10–100× faster on multi-stage and iterative jobs. This is correct because it identifies the specific mechanical cause (disk I/O between every stage) rather than a vague "MapReduce was slow," which is the level of precision this question is testing for.

#### Q33. Why did on-prem Hadoop adoption decline, honestly? **[Senior/Experienced]**
*Why interviewers ask this:* A "tell me the real story" question that filters for candidates with genuine industry perspective versus textbook knowledge.
**Answer:** Three real reasons: **coupled storage and compute** — adding disk meant buying CPU too, so clusters were sized for peak load and sat idle overnight, an economics problem cloud object storage plus elastic compute broke; **operational weight** — Kerberos, Ranger, ZooKeeper, NameNode HA, and version-matrix upgrades required a full-time platform team before any business insight shipped; and **cost** — HDFS's 3× replication is expensive compared to object storage's roughly 1.4× erasure-coded pricing. What survived wasn't the distribution model but the *ideas* — scale-out, data locality (which became data skipping), and the Hive Metastore (which evolved into Unity Catalog/Glue). This is correct because it gives concrete, named failure points rather than a vague "it was replaced by the cloud," which shows real awareness of *why* the market moved, not just that it did.

#### Q34. How would you plan a migration from an on-prem Hadoop cluster to Azure? **[Senior/Experienced]**
*Why interviewers ask this:* A real consulting/architecture scenario, common in senior interviews for candidates claiming migration experience.
**Answer:** Map each piece to its Azure landing zone: HDFS data moves to ADLS Gen2 (via distcp or ADF copy); Hive tables become Delta tables governed by Unity Catalog (Hive SQL ports roughly 90% cleanly to Spark SQL); MapReduce/Hive jobs move to Spark on Databricks; Oozie workflows become Data Factory or Databricks Workflows pipelines. The professional sequence is **data first, engines second, pipelines last** — and running old and new systems in parallel with reconciliation checks (row counts, checksums per partition) before cutover, rather than a risky big-bang switch. This is correct because it gives a concrete, ordered migration plan with a named risk-mitigation step (parallel run + reconciliation), which is what separates a real migration answer from a list of tool names.

---

## 6. Big Data Evolution Timeline

*(full notes: [06_Big_Data_Evolution_Timeline.md](06_Big_Data_Evolution_Timeline.md))*

#### Q35. Walk me through the evolution from relational databases to the modern lakehouse. **[Frequently Asked]**
*Why interviewers ask this:* One of the most common "tell the story" questions in data engineering interviews — checks whether the candidate understands *why* each technology exists, not just its name.
**Answer:** Relational **databases** (1970s–90s) ran the business on row-based OLTP systems, but heavy reports slowed the live application down. **Data warehouses** (1980s–2000s) solved that by copying data into a separate OLAP system, but were expensive, structured-data-only appliances that scaled up, not out — unable to handle the internet era's logs and clickstreams. **Hadoop** (2006) applied Google's GFS/MapReduce ideas to scale out on cheap commodity machines, but MapReduce's disk-heavy processing was slow. **Spark** (2009–2015) fixed that with in-memory processing. **Cloud** platforms (2013–2020) then removed the operational burden of running clusters yourself, with Databricks offering Spark as a managed service — but this left companies syncing two copies of data, a lake and a warehouse. The **lakehouse** (2020+) collapsed that duplication by adding warehouse-grade features (ACID, schema enforcement, time travel) directly on top of lake files via Delta/Iceberg. This is correct because each step names the specific *breaking point* that motivated the next technology — the actual mechanism of the story, not just a chronological list of names.

#### Q36. Why does Databricks exist — what problem does it solve that raw open-source Spark doesn't? **[Frequently Asked]**
*Why interviewers ask this:* A very commonly asked "why does this company/product exist" question, testing whether the candidate separates the technology from the business.
**Answer:** Tracing the timeline: Spark (era 4) solved the *speed* problem — in-memory processing beat MapReduce's disk-bound approach. But running your own Spark cluster was still heavy operational work — provisioning, patching, scaling, securing it yourself. Databricks (founded 2013, by Spark's original creators) solved that *operations* problem — offering Spark as a managed platform. This is correct because it correctly separates what Spark itself provides (the engine) from what Databricks adds on top (the operational platform), which is the exact distinction interviewers are checking for when they ask "isn't Spark free?"

#### Q37. What is Lambda architecture, and why did most teams move away from it? **[Senior/Experienced]**
*Why interviewers ask this:* A deeper architectural-history question that tests whether the candidate understands streaming's evolution, not just batch concepts.
**Answer:** Lambda architecture ran *two* parallel pipelines to serve both batch and real-time needs — a slow, accurate batch layer (e.g. Hadoop) and a fast, approximate speed layer (e.g. Storm), merged at query time. It worked, but every business rule had to be implemented **twice** and kept in sync between the two pipelines — a maintenance tax teams grew to hate. Kappa architecture proposed keeping just *one* streaming pipeline, replaying the log from the start whenever logic changed. In practice, neither "won" outright — modern lakehouse pipelines (Spark Structured Streaming over Delta) run the *same code* in batch or streaming mode over the same tables, dissolving the original problem rather than picking a side. This is correct because it explains what actually happened to Lambda's problem (it was made obsolete by unification, not "solved" by choosing Kappa), which is a more nuanced and accurate answer than most candidates give.

#### Q38. Delta Lake, Iceberg, and Hudi all solve the same problem — what is it, and how do they differ? **[Senior/Experienced]**
*Why interviewers ask this:* Tests currency with the modern "table format war," a frequent topic in 2024+ data engineering interviews.
**Answer:** Plain Parquet files sitting in a lake have no ACID transactions, no schema enforcement, and no time travel — just files. Delta Lake (from Databricks), Apache Iceberg (from Netflix), and Apache Hudi (from Uber) each add a transactional metadata layer on top of Parquet to fix this — Delta via a JSON/Parquet checkpoint log (`_delta_log`), Iceberg via snapshot manifests (aimed at multi-engine neutrality across Trino/Flink/Snowflake), and Hudi via a timeline of file groups (aimed at streaming, upsert-heavy ingestion). All three deliver ACID commits, schema evolution, time travel, and data skipping. The pro-level point: which specific format wins matters less than the fact the industry standardized on *open formats on object storage* — vendor lock-in moved up the stack into catalogs and engines instead. This is correct because it doesn't just list three names — it explains what problem they share and their distinct sweet spots, plus the higher-level trend (open formats) that the format choice sits inside.

#### Q39. How do you decide whether a team actually needs a new piece of big-data technology, versus adopting it because it's trendy? **[Senior/Experienced]**
*Why interviewers ask this:* A judgment/architecture-review question aimed squarely at senior candidates — tests decision-making framework, not tool trivia.
**Answer:** Every era in the big data timeline followed the same loop: a real bottleneck forced a decoupling, which then created a *new* bottleneck the next technology addressed (compute-bound → Hadoop decoupled processing → operations became the bottleneck → cloud decoupled infrastructure → data duplication/governance became the bottleneck → lakehouse decoupled table format from engine). The senior habit is to ask, for any proposed adoption: *which coupling does this remove, and what new bottleneck will it create?* — and to name the actual breaking point a proposal inherits (e.g. "this re-couples storage and compute — we know how that story ends"). Adopting a solution to a problem you don't actually have is how teams end up running Kafka for a workload of 100 rows a day. This is correct because it gives a transferable framework rather than a case-by-case opinion, which is exactly what separates a senior answer from a junior one on an open-ended judgment question.

---

## Rapid-Fire Round

- Q: What does OLTP stand for? — A: Online Transaction Processing.
- Q: What does OLAP stand for? — A: Online Analytical Processing.
- Q: Row storage or column storage — which is better for `SELECT SUM(amount)` on 50 columns? — A: Column storage; it reads only the needed column.
- Q: What are the four ACID guarantees? — A: Atomicity, Consistency, Isolation, Durability.
- Q: What's the default HDFS replication factor? — A: 3.
- Q: What's the default HDFS block size? — A: 128 MB.
- Q: Scale up or scale out — which has no hard ceiling? — A: Scale out (horizontal/distributed).
- Q: In master-slave architecture, which node processes the actual data? — A: The workers/slaves, never the master.
- Q: What's the classic weakness of a single master node? — A: It's a single point of failure (SPOF).
- Q: What does a Standby NameNode protect against? — A: The Active NameNode being a single point of failure.
- Q: What are the three components of Hadoop? — A: HDFS (storage), YARN (resource management), MapReduce (processing).
- Q: Why was MapReduce slow for multi-step jobs? — A: It wrote results to disk after every stage.
- Q: What made Spark faster than MapReduce? — A: In-memory processing instead of disk round-trips at every stage.
- Q: Who founded Databricks, and when? — A: Spark's original creators, in 2013.
- Q: What does a lakehouse add on top of plain Parquet files in a lake? — A: A transactional table format (e.g. Delta Lake) giving ACID, schema enforcement, and time travel.
- Q: Under the CAP theorem, what must you choose between during a network partition? — A: Consistency and Availability.
- Q: What is data skew? — A: An uneven distribution of data across partitions, causing one worker to do disproportionately more work.
- Q: SCD Type 2 — what does it preserve that Type 1 does not? — A: History (via new rows with validity date ranges).
- Q: What is a quorum? — A: A majority of nodes that must agree before an operation is considered successful.
- Q: What replaced Lambda architecture's dual-pipeline problem in most modern stacks? — A: Unified batch/streaming pipelines (e.g. Spark Structured Streaming over Delta) running the same code both ways.

Back to the notes: [00_Fundamentals folder](.) · Continue the series: [01_SQL Interview Questions](../01_SQL/Interview_Questions_and_Answers.md) (if created)
