# OLTP Storage (Online Transaction Processing)

## What is OLTP?

**OLTP = Online Transaction Processing.** It is the storage pattern behind everyday applications — the systems that record *transactions* as they happen: an order placed, a payment made, a seat booked, a password changed.

An OLTP system's job is to handle **many small reads and writes, very fast, with perfect accuracy**.

---

## Analogy: the checkout till

Think of the checkout till at a supermarket. It processes one customer at a time, each purchase is small, it must never lose or double-charge a sale, and there are hundreds of tills running at once across all stores. That is OLTP: lots of small, quick, correct transactions happening simultaneously.

---

## Key characteristics

| Characteristic | OLTP behavior |
|---|---|
| Workload | Many small transactions (INSERT, UPDATE, DELETE, single-row SELECT) |
| Users | Thousands of app users / customers at the same time |
| Data volume per query | Tiny — a few rows |
| Response time | Milliseconds |
| Data state | Current, live, always up to date |
| Storage layout | **Row-based** — a whole record is stored together |
| Schema design | Normalized (data split into many related tables to avoid duplication) |
| Correctness | ACID transactions (Atomic, Consistent, Isolated, Durable) |

---

## Why row-based storage?

OLTP databases store data **row by row** on disk:

```
Row 1: [id=1, name=Asha,  city=Hyderabad, amount=500]
Row 2: [id=2, name=Ravi,  city=Chennai,   amount=750]
Row 3: [id=3, name=Meena, city=Pune,      amount=300]
```

When the app says "fetch order #2" or "insert a new order," the database reads or writes **one complete row in one go**. That's exactly what applications need — the full record for one customer, one order, one login.

(Contrast this with [OLAP storage](02_OLAP_Storage.md), which stores data column by column.)

---

## ACID — the safety guarantee

OLTP systems promise **ACID** transactions:

- **Atomic** — a transfer of ₹500 either fully happens (debit + credit) or not at all. Never half.
- **Consistent** — the database always moves from one valid state to another.
- **Isolated** — two people booking the last seat at the same time can't both get it.
- **Durable** — once confirmed, the data survives a crash or power cut.

---

## Examples of OLTP systems

- Azure SQL Database, PostgreSQL, MySQL, SQL Server, Oracle
- The database behind an e-commerce site, a banking app, a booking system

---

## OLTP vs OLAP at a glance

| | OLTP | OLAP |
|---|---|---|
| Question it answers | "What's in *this* customer's cart?" | "What were total sales by region last year?" |
| Query touches | A few rows | Millions of rows |
| Optimized for | Fast writes + point reads | Fast aggregation over huge scans |
| Storage | Row-based | Column-based |

Full detail on the other side: [02_OLAP_Storage.md](02_OLAP_Storage.md).

---

## Where OLTP fits in a data pipeline

```
Users → Application → OLTP Database (live transactions)
                            ↓  (extracted by ETL/ELT)
                      Data Lake / Warehouse (OLAP, for analysis)
```

OLTP systems are usually the **source** of a data engineer's pipelines: the business runs on them, and we copy their data out for analytics — see [01_Data_Lake_vs_Warehouse_vs_Database.md](../../04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md).

---
---

# Part 2 — Advanced

## How OLTP databases are fast: the B-tree index

An OLTP query like `SELECT * FROM orders WHERE order_id = 1042` cannot afford to scan the whole table. Databases build a **B-tree index** — a sorted, balanced tree over the key:

```
                [ 500 | 1000 ]                ← root page
               /       |       \
        [1..499]  [500..999]  [1000..1500]    ← intermediate pages
          ...         ...      → leaf page containing row 1042
```

Finding any row among 100 million takes **3–4 page reads** instead of millions. This is why point lookups are milliseconds. (Deep dive: [11_SQL_Indexes.md](../../02_Databases/SQL/11_SQL_Indexes.md).)

## How OLTP databases survive crashes: the WAL

Databases don't write your change to the data files first. They append it to a **Write-Ahead Log (WAL / transaction log)** — a sequential file — and only then update data pages in memory (flushed later).

- Sequential appends are far faster than random writes → fast commits.
- After a crash, the database **replays the log** to recover every committed transaction — that's the **D** (Durable) in ACID.
- Data engineers care because **CDC (Change Data Capture)** tools like Debezium and Fivetran *read this log* to stream every insert/update/delete into the lake — far cheaper than repeatedly querying the source table.

## How OLTP handles many users at once: MVCC & isolation levels

**MVCC (Multi-Version Concurrency Control):** instead of readers blocking writers, the database keeps *multiple versions* of a row. Readers see a consistent snapshot; writers create a new version. PostgreSQL, Oracle, SQL Server (with RCSI) all do this.

The **isolation level** controls how much concurrent transactions can "see" of each other:

| Isolation level | Prevents | Cost |
|---|---|---|
| Read Uncommitted | nothing (dirty reads possible) | cheapest |
| Read Committed *(common default)* | dirty reads | low |
| Repeatable Read | + non-repeatable reads | medium |
| Serializable | + phantoms (acts like one-at-a-time) | highest |

**Example anomaly (non-repeatable read):** you read a balance = ₹500; another transaction commits an update; you read again inside the *same* transaction and get ₹300. Repeatable Read prevents this by holding your snapshot.

## Normalization in 30 seconds

OLTP schemas are normalized to avoid duplicate facts:

- **1NF** — no repeating groups; each cell atomic.
- **2NF** — every column depends on the *whole* primary key.
- **3NF** — no column depends on another non-key column (store `city → pincode` mapping once, in its own table).

Result: updates touch one place; no risk of two rows disagreeing about a customer's address. The price: reads need joins — which is exactly why [OLAP](02_OLAP_Storage.md) denormalizes.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Scaling OLTP when one box isn't enough

1. **Read replicas** — async copies serve read traffic; writes still go to the primary. Watch out for **replication lag**: a user may write and not see their own write on a replica.
2. **Sharding** — split rows across databases by a key (e.g. customer_id % 16). Powerful but painful: cross-shard joins and transactions become application problems. Choose shard keys to avoid **hot shards** (e.g. sharding by date puts *all* today's writes on one shard — bad).
3. **CQRS** — separate the write model (normalized OLTP) from read models (denormalized projections) fed by events.

## Locking, deadlocks, and why your ETL job gets killed

- Writers take **row/page locks**; two transactions locking rows in opposite order → **deadlock**; the database kills one ("deadlock victim").
- A naive full-table extract (`SELECT * FROM orders`) at 9am can escalate locks or trip long-running-snapshot limits on a busy OLTP system. Pro habits:
  - Extract from a **read replica**, never the primary.
  - Pull **incrementally** (`WHERE modified_at > last_watermark`) or via **CDC**, not full scans.
  - Never run analytics SQL directly on production OLTP — that's the entire reason warehouses exist.

## Field-tested gotchas

- **Auto-increment keys ≠ gap-free**: rollbacks burn IDs. Never build business logic on ID continuity.
- **`updated_at` watermarks miss hard deletes** — you need CDC or soft deletes (`is_deleted` flag) to capture them downstream.
- **Long transactions are poison** under MVCC: they force the DB to retain old row versions (PostgreSQL bloat, SQL Server version store growth).
- **Connection pooling** (e.g. PgBouncer, HikariCP) matters more than CPU for high-concurrency apps — each connection has real memory cost.

## Interview-grade Q&A

- *Why not run reports on the OLTP DB?* Lock contention + cache pollution + row storage reads all columns → slows both the report and the app.
- *How would you extract 1 TB from OLTP without hurting it?* Replica + incremental watermark or log-based CDC + off-peak batches + partitioned reads.
- *What's the difference between ACID and BASE?* ACID = strict transactional guarantees (OLTP). BASE (Basically Available, Soft state, Eventually consistent) = the looser model many distributed NoSQL stores use for availability at scale.

---

## Further Learning — Docs & Videos

**Documentation**
- What is OLTP? (IBM): https://www.ibm.com/topics/oltp
- OLTP overview (Azure Architecture Center): https://learn.microsoft.com/en-us/azure/architecture/data-guide/relational-data/online-transaction-processing
- Row-oriented vs column-oriented storage: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/

**Videos**
- OLTP vs OLAP explained: https://www.youtube.com/results?search_query=oltp+vs+olap+explained
- What is OLTP (transactional systems): https://www.youtube.com/results?search_query=what+is+oltp+database
