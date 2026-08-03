# Storage & Query Cost

## The two ways storage costs you

1. **Storing the bytes** — GB stored × the storage tier's price (usually a small part of the bill).
2. **Scanning the bytes** — the *real* cost driver: every query that reads data burns **compute time** (and, in some engines, is billed directly per byte scanned). **How you lay data out determines how much gets scanned**, which drives most query cost.

So storage optimization is really two jobs: **store cold data cheaply**, and **lay hot data out so queries scan as little as possible**.

---

## ADLS storage tiers (store cold data cheaply)

Azure Storage / ADLS Gen2 offers **access tiers** priced for how often you read data ([ADLS](../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)):

| Tier | Storage cost | Read cost | Use for |
|---|---|---|---|
| **Hot** | Highest | Lowest | Actively queried data |
| **Cool** | Lower | Higher | Infrequently accessed (30+ days) |
| **Cold** | Lower still | Higher | Rarely accessed (90+ days) |
| **Archive** | Cheapest | Retrieval takes hours | Compliance/backup |

**Lifecycle management policies** auto-move blobs to cheaper tiers as they age (e.g., Bronze raw → Cool after 30 days → Archive after a year). This is easy, automatic savings on the long tail of data you must keep but rarely read.

---

## The #1 query-cost lever: scan less data

Two file-layout techniques let engines **skip** data instead of reading it:

### Partitioning (partition pruning)
Physically split a table by a low-cardinality column (usually **date**) into folders. A query filtered on that column reads only the relevant folders:

```python
df.write.partitionBy("event_date").format("delta").save(path)
# query with WHERE event_date = '2026-08-02' → reads ONE folder, not the whole table
```

**Partition pruning** can turn a full-table scan into reading 0.3% of the data. But **don't over-partition** — partitioning by a high-cardinality column (e.g., `user_id`) creates millions of tiny files and *hurts*. Rule: partition by columns you **filter on**, with **reasonable cardinality** (date is the classic).

### File skipping & Z-ordering (Delta)
Delta stores **min/max stats per file**, so it skips files that can't contain matching rows. **`OPTIMIZE ... ZORDER BY (col)`** co-locates related values so skipping is even more effective for that column:

```sql
OPTIMIZE sales ZORDER BY (customer_id);
```

Great for high-cardinality filter columns that you *can't* partition by. See [Delta](../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md).

---

## The small-file problem (compaction)

Thousands of tiny files (from frequent streaming micro-batches or over-partitioning) are expensive: the engine spends more time **opening files** than reading data, and cloud storage charges per operation. The fix is **compaction**:

```sql
OPTIMIZE sales;          -- compacts small files into ~optimal-sized ones
VACUUM sales;            -- removes old, unreferenced files (reclaim storage)
```

Target file sizes around **128 MB–1 GB**. "Too many small files" is one of the most common real performance/cost problems — and a frequent interview topic.

---

## Choosing formats (scan less, compress more)

- **Columnar formats (Parquet/Delta)** let queries read only the **columns** they need (column pruning) and compress far better than CSV/JSON — less storage *and* less scan. Prefer them for analytics ([File Formats](../04_Storage_and_Formats/File_Formats/06_File_Format_Comparison.md)).
- Reading a 200-column table's 3 columns from Parquet touches ~1.5% of the bytes CSV would.

---

## Cost models of the analytical engines

Different serving engines bill differently — know the currency:

| Engine | Billed by | Optimize by |
|---|---|---|
| **Databricks SQL** | Cluster/warehouse time (DBUs) | Scan less, right-size warehouse, auto-stop |
| **Synapse Dedicated SQL** | Provisioned **DWUs** (per hour, on) | **Pause** when idle; scale DWUs to load |
| **Synapse Serverless SQL** | **Per TB of data processed** | Scan less (partition/prune/columnar) — data-scanned = money |
| **Cosmos DB** | **RUs** (Request Units) | Good partition keys, point reads ([Cosmos](../02_Databases/NoSQL/08_Azure_Cosmos_DB.md)) |
| **Fabric** | **Capacity Units (CUs)** | Right-size capacity, smooth bursty load |

Synapse Serverless charging **per TB scanned** makes partition pruning literally a line-item saving — a favorite interview example of "layout = cost."

---

## Interview-grade Q&A

- *What drives query cost more, storing or scanning data?* Scanning — how much data a query reads (compute time, or per-TB billing) usually dwarfs storage cost.
- *How do you make queries scan less?* Partition pruning (partition by filtered, sensible-cardinality columns like date), Delta file skipping + Z-ordering, and columnar formats for column pruning.
- *What's the danger of over-partitioning?* High-cardinality partitioning creates millions of tiny files — slower and costlier; partition only by columns you filter on with reasonable cardinality.
- *What's the small-file problem and the fix?* Too many tiny files cost more to open than to read; fix with `OPTIMIZE`/compaction (target 128 MB–1 GB) and `VACUUM`.
- *How do ADLS access tiers save money?* Move rarely-read data to Cool/Cold/Archive via lifecycle policies — cheaper storage for the long tail.
- *How is Synapse Serverless billed and how do you optimize it?* Per TB of data processed — minimize scanned data via partitioning, pruning, and columnar formats.
- *How do you cut Synapse Dedicated pool cost?* Pause it when idle and scale DWUs to the workload.

---

## Further Learning — Docs & Videos
- ADLS access tiers & lifecycle: https://learn.microsoft.com/azure/storage/blobs/access-tiers-overview
- Delta OPTIMIZE & Z-order: https://learn.microsoft.com/azure/databricks/delta/optimize
- Synapse serverless cost control: https://learn.microsoft.com/azure/synapse-analytics/sql/data-processed
- Video — partitioning & file skipping: https://www.youtube.com/results?search_query=delta+lake+partitioning+zorder+optimize
