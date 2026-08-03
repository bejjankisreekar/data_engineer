# 03 — Non-Relational Data on Azure

*Domain: Non-relational data on Azure (15–20%)*

---

## What it is

Non-relational (**NoSQL**) data doesn't fit neatly into fixed relational tables — it's semi-structured or unstructured, and prioritizes **scale, flexibility, and speed** over rigid schemas and joins. This domain covers Azure's **Storage** services and **Azure Cosmos DB**, plus knowing *when* non-relational beats relational.

---

## The NoSQL data-store types

| Type | Shape | Example use |
|---|---|---|
| **Key-value** | Simple key → value pairs | Session state, caching |
| **Document** | JSON-like documents | Catalogs, user profiles |
| **Column-family** | Rows with dynamic columns | Wide, sparse data at scale |
| **Graph** | Nodes + edges (relationships) | Social networks, fraud, recommendations |

> **Exam Tip:** Match the shape — *relationships between entities* → **graph**; *flexible JSON records* → **document**; *simple lookups/caching* → **key-value**.

---

## Azure Storage account services

An **Azure Storage account** provides four data services:

| Service | What it stores | Use for |
|---|---|---|
| **Blob Storage** | Unstructured objects (files) in containers | Images, video, backups, data-lake files ([Blob](../../05_Storage_and_Formats/Data_Storage/02_Azure_Blob_Storage.md)) |
| **File Storage** | Managed SMB/NFS file shares | Lift-and-shift shared drives |
| **Table Storage** | Key-value / NoSQL tables | Simple, cheap semi-structured data |
| **Queue Storage** | Messages between app components | Decoupling, async messaging |

**Blob access tiers** (cost vs access speed): **Hot** (frequent access) → **Cool** (infrequent, ~30+ days) → **Cold** → **Archive** (rarely accessed, lowest cost, retrieval latency).

**Azure Data Lake Storage Gen2** = Blob Storage + a **hierarchical namespace**, optimized for big-data analytics ([ADLS](../../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)).

> **Exam Tip:** Blob = unstructured object storage; **ADLS Gen2 = Blob with a hierarchical namespace for analytics**. Files = SMB share; Table = NoSQL key-value; Queue = messaging. For rarely-accessed data at lowest cost → **Archive** tier.

---

## Azure Cosmos DB

**Azure Cosmos DB** is a globally distributed, multi-model **NoSQL** (and now relational-optional) database built for **low latency at any scale**.

Key selling points (all commonly tested):
- **Global distribution** — replicate data to any Azure region; **turnkey multi-region**.
- **Single-digit-millisecond latency**, backed by SLAs.
- **Elastic scale** of throughput and storage.
- **Multiple APIs** — pick the interface your app already knows.
- **Five consistency levels** — Strong → Bounded Staleness → Session → Consistent Prefix → Eventual (trade consistency for latency/availability).

### Cosmos DB APIs

| API | For |
|---|---|
| **NoSQL (Core / SQL)** | The native, document API (default, most feature-rich) |
| **MongoDB** | Existing MongoDB apps |
| **Cassandra** | Column-family / existing Cassandra apps |
| **Gremlin** | Graph data |
| **Table** | Key-value (Azure Table Storage-compatible) |

> **Exam Tip:** If you need a **globally distributed, low-latency NoSQL** database → **Cosmos DB**. Pick the **API** by the existing data model/app: graph → Gremlin, Mongo app → MongoDB API, key-value → Table API, new/document → NoSQL (Core).

---

## When to choose non-relational

- Flexible/changing schema (semi-structured JSON).
- Massive scale and global distribution with low latency.
- Simple access patterns (key lookups) rather than complex multi-table joins.
- Unstructured content (media/files) → Blob/ADLS.

Choose **relational** instead when you need strong schema enforcement, complex joins, and ACID transactions across many tables.

---

## Quick Review

- NoSQL types: **key-value**, **document**, **column-family**, **graph** — match shape to scenario.
- Storage account = **Blob** (objects), **File** (SMB share), **Table** (NoSQL KV), **Queue** (messaging).
- **ADLS Gen2** = Blob + hierarchical namespace for analytics; blob tiers Hot→Cool→Cold→**Archive** (cheapest, rarely accessed).
- **Cosmos DB** = globally distributed, multi-model, single-digit-ms NoSQL with 5 consistency levels.
- Cosmos APIs: **NoSQL/Core** (document, default), **MongoDB**, **Cassandra**, **Gremlin** (graph), **Table** (key-value).
- Non-relational when: flexible schema, global scale/low latency, simple access patterns, unstructured content.

---

## Further Learning — Docs & Videos

- Explore non-relational data on Azure (Learn): https://learn.microsoft.com/en-us/training/paths/azure-data-fundamentals-explore-non-relational-data/
- Azure Cosmos DB overview: https://learn.microsoft.com/en-us/azure/cosmos-db/introduction
- Video search: https://www.youtube.com/results?search_query=dp-900+cosmos+db+azure+storage

---

Next: **[04 — Analytics Workloads on Azure](04_Analytics_Workloads_on_Azure.md)**.
