# NoSQL — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Fundamentals

**Q1. 🔥 What does NoSQL stand for and mean?**
"**Not Only SQL**" — a family of non-relational databases optimized for horizontal scale, flexible schemas, and specific data shapes. It *complements* relational SQL rather than replacing it.

**Q2. 🔥 SQL vs NoSQL — the core difference in one line?**
SQL models data by its **structure** (fixed schema) then queries it flexibly with joins; NoSQL models data by its **access patterns** then stores it accordingly, usually without joins.

**Q3. 🔥 Name the four families of NoSQL with an example each.**
**Key-value** (Redis), **Document** (MongoDB/Cosmos DB), **Wide-column** (Cassandra), **Graph** (Neo4j).

**Q4. ⭐ When would you choose NoSQL, and when NOT?**
Choose NoSQL for known simple access patterns, nested/semi-structured data, and huge horizontal scale. Avoid it when you need ad-hoc joins/analytics or multi-entity ACID transactions and integrity over raw scale — use relational SQL there.

**Q5. ⭐ Is NoSQL "schemaless"?**
No. There's always a schema — it lives in the **application code and access patterns** instead of `CREATE TABLE`. Unmanaged "schemaless" data becomes an inconsistent swamp; mature teams add validators.

**Q6. 💡 Schema-on-write vs schema-on-read?**
Relational enforces the schema at insert time (schema-on-write, bad data rejected at the door). Most NoSQL stores accept any shape and impose meaning at read time (schema-on-read), pushing validation into the app/pipeline.

---

## Key-Value & Document

**Q7. 🔥 What is a key-value store best for?**
Fast O(1) lookups by a **known key**: caching, session state, counters, feature flags, leaderboards. Not for querying by value or joining.

**Q8. ⭐ Why is Redis so fast, and what's a risk?**
It's **in-memory** with efficient data structures — no disk seek on the hot path. Risk: RAM is volatile and limited, so treat it as rebuildable cache unless durability is configured.

**Q9. 🔥 Explain cache-aside and its main pitfall.**
App checks the cache first; on a miss it reads the DB and populates the cache. Main pitfall: **cache invalidation** — stale entries serve wrong data when the source changes; also stampede, penetration, and avalanche failures.

**Q10. 🔥 What is a document database and how does it differ from key-value?**
It stores queryable **JSON/BSON documents**; unlike key-value, you can **query and index fields inside** the value.

**Q11. 🔥 Embedding vs referencing — how do you decide?**
**Embed** small, bounded, read-together data owned by the parent; **reference** (store an ID) data that's large, shared, or unbounded. Rule: *data queried together is stored together.*

**Q12. ⭐ What's the unbounded-array anti-pattern?**
Embedding an ever-growing array (all orders in a customer doc) — it hits document size limits and slows reads. Fix with the **subset/bucket pattern**: embed the recent few, reference the rest.

**Q13. 💡 Is a single-document write atomic?**
Yes — a write to **one document is atomic**. Multi-document transactions exist in modern engines (MongoDB 4.0+, Cosmos DB within a partition) but are more limited/costly than relational ACID.

---

## Wide-Column & Graph

**Q14. ⭐ What is a wide-column store best for?**
Massive, **write-heavy**, high-volume data with known key-based access — time-series, IoT, event logs (Cassandra, HBase).

**Q15. 🔥 Partition key vs clustering key?**
The **partition key** decides which node data lives on and groups related rows; the **clustering key** sorts rows within a partition to enable fast range scans.

**Q16. 💡 Why are writes so fast in Cassandra?**
**LSM-tree** storage turns every write into a cheap **sequential append** (memtable + log), not a random in-place update. The cost shifts to reads and background compaction.

**Q17. 💡 What is a tombstone?**
A marker for a deleted row in append-only storage — the real removal happens later during compaction. Heavy deletes accumulate tombstones that degrade reads, so wide-column suits **append-mostly** data.

**Q18. ⭐ When do you choose a graph database?**
When **relationships and multi-hop traversals** are the core question — social networks, recommendations, fraud rings, knowledge graphs.

**Q19. 🔥 Why are deep-relationship queries faster in a graph than in SQL?**
**Index-free adjacency** — each node stores direct pointers to its neighbors, so each extra hop is a pointer walk, not another join over the whole table. Cost scales with the result touched, not the DB size.

**Q20. 💡 What's a supernode?**
A node with an enormous number of edges (a celebrity, a shared "USD" node). Traversals fan out through its millions of edges and blow up performance — the graph equivalent of a hot partition.

---

## CAP, Consistency & Scaling

**Q21. 🔥 State the CAP theorem.**
A **distributed** database can fully guarantee only **two of three**: **C**onsistency, **A**vailability, **P**artition tolerance — simultaneously.

**Q22. 🔥 Why is the real choice CP vs AP?**
Because network **partitions will happen**, partition tolerance is non-negotiable. So the real decision is what to sacrifice *during* a partition — **consistency (CP)** or **availability (AP)**.

**Q23. ⭐ ACID vs BASE?**
**ACID** = strict correctness (Atomicity, Consistency, Isolation, Durability) — relational. **BASE** = **B**asically **A**vailable, **S**oft state, **E**ventually consistent — many NoSQL, trading strictness for availability and scale.

**Q24. ⭐ What is eventual consistency?**
After a write, replicas may briefly disagree but **converge** if writes stop (usually milliseconds). Acceptable when staleness is cheap (likes, feeds); not for money.

**Q25. 💡 What does PACELC add over CAP?**
Even with **no** partition (**E**lse), a distributed system still trades **L**atency vs **C**onsistency. It's the everyday version of the trade-off; CAP only covers the partition case.

**Q26. 💡 How do quorums tune consistency?**
With **N** replicas, **W** write-acks, **R** read-nodes: if **R + W > N**, reads are guaranteed to overlap the latest write (strong-ish). Lower R/W → faster but possibly stale. This is Cassandra's ONE/QUORUM/ALL.

**Q27. 💡 Replication vs sharding?**
**Replication copies** data across nodes (durability, availability, read scale); **sharding splits** data across nodes by a partition key (capacity/write scale). Real systems do both.

---

## Data Modeling

**Q28. 🔥 How does NoSQL modeling differ from relational modeling?**
Relational: model the data's structure, then query flexibly. NoSQL: **list access patterns first**, then shape data (often one structure per query) to serve them without joins.

**Q29. ⭐ Why duplicate/denormalize data in NoSQL?**
No joins — pre-assembling answers makes each read a **single fast operation**; duplication also captures **point-in-time snapshots** (e.g., the price at purchase time).

**Q30. ⭐ What's the downside of denormalization and how do you manage it?**
**Write amplification** and drift risk. Decide per field whether it's a **snapshot** (leave it) or a **live mirror** (must fan out updates, often via a change feed).

**Q31. 💡 Name three NoSQL schema-design patterns.**
**Subset**, **Bucket**, **Computed** (also Extended-Reference, Outlier, Schema-Versioning).

**Q32. 🔥 What's the most common NoSQL modeling mistake?**
Modeling it **like relational** — many collections cross-referenced at read time — causing N+1 query storms with none of the denormalization benefit.

---

## Azure Cosmos DB

**Q33. 🔥 What is Azure Cosmos DB?**
A **globally distributed, multi-model, fully managed** NoSQL database with **tunable consistency** and elastic **RU-based** throughput; exposes NoSQL, MongoDB, Cassandra, Gremlin, and Table APIs.

**Q34. 🔥 What are Request Units (RUs)?**
The normalized **currency of throughput** (CPU/memory/IO combined). Every operation costs RUs; you provision RU/s per container and get **throttled (HTTP 429)** if you exceed it. A 1 KB point-read ≈ 1 RU.

**Q35. 🔥 How do you choose a good partition key?**
**High cardinality** (even distribution), **groups query-together data** into one partition (cheap single-partition reads), and **spreads writes** to avoid a hot partition.

**Q36. ⭐ Name the five Cosmos DB consistency levels and the default.**
**Strong, Bounded Staleness, Session (default), Consistent Prefix, Eventual** — a direct dial on the CAP/latency trade-off.

**Q37. 🔥 How do you analyze Cosmos DB data without hurting the app?**
Use **Azure Synapse Link**'s analytical store (auto-synced columnar copy, **no RU impact**), or read the **Change Feed** into a Delta lakehouse. Never run heavy BI against the transactional container.

**Q38. ⭐ What is the Change Feed used for?**
Near-real-time **CDC out of Cosmos DB** — streaming inserts/updates to a lakehouse, triggering functions, or fanning out denormalized updates. (Note: it doesn't emit deletes by default.)

**Q39. 💡 Provisioned vs Autoscale vs Serverless throughput?**
**Provisioned** fixed RU/s for steady load; **Autoscale** scales within a floor–10× ceiling for spiky load; **Serverless** pay-per-request for dev/low/bursty workloads.

---

## Data Engineering Practice

**Q40. 🔥 How do you ingest a document store into the lakehouse?**
Land raw JSON in **Bronze**, **flatten/type** nested docs in **Silver** (explode arrays, dot-notation for objects, handle drift), model a **Gold** star schema — fed by Change Feed/CDC or batch copy.

**Q41. ⭐ What's the hardest part of ingesting NoSQL data?**
**Flattening nested/variant JSON and handling schema drift** — fields that appear/disappear or change type across documents. Land raw, parse permissively, version the flattening logic.

**Q42. 💡 How do you make a change-feed load idempotent?**
**MERGE/upsert** into Delta on a **business key + version/timestamp**, so at-least-once redeliveries don't create duplicates or overwrite newer data with older.

**Q43. 💡 What's the deletes gotcha with change feeds?**
Change feeds often **don't emit deletes**, so deleted source records linger in the lake. Handle via soft-delete flags, TTL-driven events, or periodic reconciliation snapshots.

**Q44. ⭐ What is reverse ETL and where does NoSQL fit?**
Pushing computed results from the lake **back into a fast serving store** (Redis/Cosmos DB) — e.g., a **feature store** or pre-computed "customer 360" — so apps get millisecond point-reads.

**Q45. 💡 A senior instinct question: when is the right answer "just use Postgres"?**
When the access pattern and scale **don't genuinely demand** NoSQL. A JSON column in Postgres often beats a Cosmos DB + Change Feed + Spark-flattening pipeline you must operate forever. Every store added is a lifetime of ingestion, drift-handling, and reconciliation.

---

## Quick-fire lightning round

- *NoSQL = ?* Not Only SQL.
- *Four families?* Key-value, document, wide-column, graph.
- *No joins → so you…?* Denormalize / duplicate / embed.
- *CAP under partition?* Choose CP or AP.
- *Cosmos DB throughput currency?* Request Units (RU/s).
- *Cosmos DB default consistency?* Session.
- *Fastest Cosmos DB operation?* Point read (id + partition key).
- *Get data out of Cosmos DB?* Change Feed or Synapse Link.
- *Cassandra write speed reason?* LSM-tree appends.
- *Graph traversal speed reason?* Index-free adjacency.
- *Biggest NoSQL design decision?* The partition key.

---

## Further Learning
- Back to the [Learning Path](00_NoSQL_Learning_Path.md)
- Compare with [SQL Interview Q&A](../SQL/Interview_Questions_and_Answers.md) and [Data Modeling Q&A](../Data_Modeling/Interview_Questions_and_Answers.md)
