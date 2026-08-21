# NoSQL in Data Engineering — Practical Scenarios

## Where NoSQL sits in a data engineer's world

As a data engineer you rarely *design* the NoSQL app database — that's the application team's job. Your job is to **get data out of NoSQL systems, into the lakehouse, and shaped for analytics** — and sometimes to **serve results back** into a NoSQL store for low-latency apps.

Analogy: the NoSQL store is a **busy shop till** — fast, operational, built for the cashier, not the accountant. Your pipelines are the **nightly (or streaming) run to the accounting office**: you copy the receipts out, flatten the messy handwriting into neat ledgers, and never make the accountant's heavy month-end reports run on the till while customers are waiting.

```mermaid
flowchart LR
    subgraph Operational (NoSQL)
      C[(Cosmos DB /<br/>MongoDB)]
    end
    C -->|Change Feed / CDC| I[Ingest<br/>Functions/ADF/Spark]
    I --> B[Bronze<br/>raw JSON in Delta]
    B --> S[Silver<br/>flattened & typed]
    S --> G[Gold<br/>star schema / OBT]
    G --> BI[Power BI]
    G -.serve back.-> C
```

---

## Scenario 1 — Ingesting a document store into the lakehouse

**Problem:** The app runs on Cosmos DB / MongoDB; analysts need it in the warehouse.

**Approach:**
1. **Land raw first (Bronze):** copy documents as-is (JSON) into Delta — never transform on the way in. Raw retention lets you reprocess when logic changes.
2. **Flatten & type (Silver):** explode nested objects and arrays into columns/rows, cast types, standardize the shape. This is where you handle the [schema-on-read](01_What_is_NoSQL.md) reality — the same field may be a string in some docs and an object in others.
3. **Model (Gold):** build the star schema / one-big-table for BI ([dimensional modeling](../Data_Modeling/03_Dimensional_Modeling.md)).

**Two ingestion modes:**
- **Batch/snapshot** — periodic full or bounded copy (Azure Data Factory copy activity, Spark read). Simple; higher latency; can be heavy on the source.
- **Change-based (CDC)** — read the **Cosmos DB Change Feed** / **MongoDB Change Streams** to capture only inserts/updates in near-real-time. Efficient and low-latency; the modern default.

---

## Scenario 2 — Flattening nested JSON (the daily grind)

NoSQL documents are nested; analytical tables are flat. This is the single most common hands-on NoSQL task for a data engineer.

Given documents like the customer in [03](03_Document_Databases.md), Spark flattens them:

```python
from pyspark.sql.functions import explode, col

flat = (raw_df
    .select(
        col("_id").alias("customer_id"),
        col("name"),
        col("preferences.theme").alias("theme"),      # nested object → column
        explode("addresses").alias("addr")             # array → one row per element
    )
    .select("customer_id", "name", "theme",
            col("addr.city").alias("city"),
            col("addr.pin").alias("pin")))
```

Key operations: **dot-notation** for nested fields, **`explode`** to turn arrays into rows, and **defensive handling** of missing/variant fields (a field absent in older documents). This is exactly the [unbounded-array / schema-versioning](07_NoSQL_Data_Modeling.md) reality landing on your desk.

---

## Scenario 3 — NoSQL as a serving layer (reverse ETL)

Sometimes data flows the *other* way: the lakehouse computes something and pushes it into a NoSQL store for a fast app.

- **Feature store** — the platform computes ML features in Spark nightly and writes them to **Redis/Cosmos DB** so the model can read a user's features in milliseconds at inference time.
- **Pre-computed aggregates** — compute "customer 360" or recommendation results in the warehouse, serve them from Cosmos DB to the app (no live analytics on the hot path).
- **Denormalized read models** — build query-optimized documents in the lake, load into Cosmos DB for the app to point-read.

This is the [pre-compute-and-store](07_NoSQL_Data_Modeling.md) idea across systems: heavy work in the lake, fast serving from NoSQL.

---

## Scenario 4 — Real-time ingestion from key-value / wide-column

- **IoT/clickstream** often lands first in **Cassandra / Cosmos DB** (fast writes), then streams to Delta for analytics — because the operational store is bad at cross-partition aggregation ([04](04_Wide_Column_Stores.md)).
- **Redis** frequently sits as a **cache in front of** your served data or a **buffer/queue** ahead of a streaming pipeline.

---

## Azure Usage

The canonical Azure pattern: **Cosmos DB → Change Feed → Azure Functions or Databricks (Structured Streaming) → Delta (Bronze/Silver/Gold) → Power BI.** Or, for zero-ETL analytics, **Azure Synapse Link** exposes a Cosmos DB **analytical store** that Synapse/Spark query directly — no pipeline, no RU impact on the app ([08](08_Azure_Cosmos_DB.md)). **Azure Data Factory** handles batch copies from Cosmos DB / MongoDB when streaming isn't needed.

---

## Real World Example

A ride-hailing company keeps live trip state in **Cosmos DB** (fast writes from millions of phones). The data team reads the **Change Feed** into **Databricks Structured Streaming**, lands raw trip JSON in **Bronze Delta**, flattens driver/rider/location objects into typed **Silver** tables, and builds a **Gold** trip-fact star schema for finance and operations dashboards. Separately, they compute driver-quality features in the lake and push them **back into Cosmos DB** so the dispatch app can read a driver's score in a single millisecond point-read. NoSQL feeds analytics *and* is fed by it.

---

## Handling schema drift on ingest

Because the source is schema-flexible, your pipeline **will** meet documents that don't match yesterday's shape: new fields, renamed fields, a scalar that became an object, a missing array. Robust ingestion:
- lands **raw JSON in Bronze** so nothing is lost and you can reprocess,
- uses **schema evolution / permissive parsing** and captures unparseable records in a quarantine/`_corrupt_record` path rather than failing the whole job,
- **versions** the flattening logic to handle multiple `schemaVersion`s coexisting.

Never assume a NoSQL source's shape is stable — designing for drift is the job.

## Deletes, tombstones, and the change feed gap

A subtle trap: the **Cosmos DB Change Feed doesn't emit deletes** by default, and append-oriented stores use [tombstones](04_Wide_Column_Stores.md). So a record deleted in the source can silently **persist forever** in your lake. Handle this explicitly — soft-delete flags in the source, periodic reconciliation snapshots, or TTL-driven change events — or your "current state" tables drift from reality. This is a favorite "gotcha" question.

## Idempotent, exactly-once-ish loading

Change feeds and streams deliver **at-least-once**, so the same change can arrive twice (retries, restarts). Your load must be **idempotent** — typically a **`MERGE` (upsert) into Delta on a business key + version/timestamp** so replays don't create duplicates or overwrite newer data with older. This is the [idempotency](06_CAP_Theorem_and_Consistency.md) principle from CAP made concrete in a pipeline.

## Don't run analytics on the operational store

Pointing Power BI or heavy Spark jobs straight at the live Cosmos DB / MongoDB **steals throughput (RUs) from real users** and can throttle the app ([08](08_Azure_Cosmos_DB.md)). The rule: **replicate to an analytical surface** (Synapse Link analytical store, or Change Feed → Delta) and analyze *there*. Keeping the operational and analytical planes separate is a core architectural principle — and a common interview scenario.

---

## Polyglot pipelines and the "single source of truth" question

Real platforms pull from many stores — Postgres (orders), Cosmos DB (catalog), Redis (sessions), Kafka (events). The senior challenge is **reconciling them into one governed truth** in the lakehouse without the sources drifting apart. The durable pattern: treat each source's **change stream as the authoritative feed**, land everything raw, and resolve conflicts and definitions **once, in Silver/Gold** — rather than letting each app's private denormalized copy define reality. This is where [data modeling](../Data_Modeling/00_Data_Modeling_Learning_Path.md) discipline meets NoSQL's duplication reality.

## Reverse ETL needs the same rigor as forward ETL

Pushing lake results back into NoSQL serving stores (feature stores, read models) is powerful but under-governed in many teams — stale features silently degrade a model, a failed reverse load leaves the app showing yesterday's numbers. Treat reverse ETL as a **first-class pipeline**: freshness SLAs, idempotent upserts, monitoring, and lineage — not a fire-and-forget script. As ML and real-time personalization grow, reverse ETL into NoSQL is an increasingly central data-engineering responsibility.

## Know when the answer is "just use Postgres"

The most valuable senior instinct: **don't introduce a NoSQL store (or a pipeline off one) unless the access pattern and scale genuinely demand it.** A modest app with relational needs and a JSON column in Postgres often beats a Cosmos DB + Change Feed + Spark flattening pipeline you now have to operate forever. Every store you add is a lifetime of ingestion, drift-handling, and reconciliation. The best engineers *remove* systems as often as they add them.

## Interview-grade Q&A

- *How do you get data out of Cosmos DB / MongoDB for analytics?* Change Feed / Change Streams (CDC) into Delta, or batch copy via ADF, or zero-ETL via Synapse Link's analytical store.
- *Why not query the operational NoSQL store directly for BI?* It consumes the app's throughput (RUs) and can throttle real users; replicate to an analytical surface instead.
- *What's the hardest part of ingesting document data?* Flattening nested/variant JSON and handling schema drift — land raw in Bronze, explode/type in Silver, version the logic.
- *How do you make a change-feed load idempotent?* MERGE/upsert into Delta on a business key + version so at-least-once redeliveries don't duplicate or regress data.
- *What's the deletes gotcha with change feeds?* They often don't emit deletes, so deleted source records linger in the lake — handle via soft-deletes, TTL events, or reconciliation snapshots.
- *What is reverse ETL and where does NoSQL fit?* Pushing computed results from the lake into a fast serving store (Redis/Cosmos DB) for low-latency app reads — e.g., a feature store.

---

## Further Learning — Docs & Videos

**Documentation**
- Cosmos DB Change Feed: https://learn.microsoft.com/azure/cosmos-db/change-feed
- Synapse Link for Cosmos DB (HTAP): https://learn.microsoft.com/azure/cosmos-db/synapse-link
- Ingest & flatten JSON in Spark (Databricks): https://docs.databricks.com/en/semi-structured/json.html

**Videos**
- Cosmos DB Change Feed pipelines: https://www.youtube.com/results?search_query=cosmos+db+change+feed+databricks
- Flattening nested JSON in Spark: https://www.youtube.com/results?search_query=flatten+nested+json+pyspark
