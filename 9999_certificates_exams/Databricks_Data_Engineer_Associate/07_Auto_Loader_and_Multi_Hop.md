# 07 — Auto Loader & the Multi-Hop (Medallion) Architecture

*Domain: Incremental Data Processing (22%)*

---

## Part A — Auto Loader

### What it is

**Auto Loader** is Databricks' feature for **incrementally and efficiently ingesting new files** as they land in cloud storage — without you tracking which files have already been processed. It's built on Structured Streaming and uses the special format **`cloudFiles`**.

```python
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/path/to/schema")
    .load("/path/to/incoming/files")
    .writeStream
    .option("checkpointLocation", "/path/to/checkpoint")
    .table("bronze"))
```

### Why it beats manual file listing

- It **automatically detects and processes only new files** — no reprocessing of already-ingested files, no custom bookkeeping.
- It **scales to millions of files** and handles schema inference and evolution.
- Exactly-once ingestion via checkpointing.

> **Exam Tip:** **Auto Loader** = incremental **file ingestion** using `format("cloudFiles")`. It automatically keeps track of which files have been loaded (so it never reprocesses them) and can handle schema inference/evolution. If a scenario asks how to efficiently ingest continuously-arriving files into a Delta table, the answer is **Auto Loader**, not a manual `spark.read` loop.

### File-detection modes

- **Directory listing mode** (default) — lists the directory to find new files. Simple, no cloud setup.
- **File notification mode** — subscribes to cloud notification/queue services (e.g., SNS/SQS, Event Grid) to be *told* about new files. Scales better for very high file volumes / large directories.

> **Exam Tip:** For extremely large numbers of incoming files, **file notification mode** scales better than directory listing (no need to re-list a huge directory). Auto Loader can switch between them via `cloudFiles.useNotifications`.

### Schema handling

- `cloudFiles.schemaLocation` — where Auto Loader stores the **inferred schema** and tracks its evolution.
- **Schema evolution** — when new columns appear, Auto Loader can add them (and by default will fail-and-restart the stream to pick up the new schema, then continue). A **rescued data column** (`_rescued_data`) captures values that don't fit the schema.

> **Exam Tip:** Auto Loader stores the schema in `schemaLocation` and can **evolve** it as new columns appear; unexpected/mismatched data is captured in the **`_rescued_data`** column rather than being dropped.

---

## Part B — The Multi-Hop / Medallion Architecture

### What it is

The **Medallion (multi-hop) architecture** is a data-design pattern that refines data through progressive quality layers — **Bronze → Silver → Gold** — each a set of Delta tables. Data flows one direction, getting cleaner and more business-ready at each hop.

```
Raw files → [ Bronze ] → [ Silver ] → [ Gold ] → BI / ML
```

| Layer | Contents | Purpose |
|---|---|---|
| **Bronze** | **Raw**, ingested data, exactly as received (plus ingestion metadata like source file, load time) | Preserve a complete, replayable history of raw data; the landing zone |
| **Silver** | **Cleaned, filtered, conformed, deduplicated, validated** data; joined/enriched | A queryable, trustworthy "single source of truth" for the enterprise |
| **Gold** | **Business-level aggregates**, curated tables for specific use cases (reports, dashboards, ML features) | Optimized, project-specific analytics/reporting |

> **Exam Tip:** Memorize the three layers cold:
> - **Bronze = raw** (as-ingested, minimal/no transformation, keeps everything).
> - **Silver = cleaned/validated/joined** (quality enforced, deduped, enriched).
> - **Gold = aggregated/business-ready** (summaries, KPIs, report-specific tables).
> Questions describe a table ("deduplicated and joined customer data") and ask which layer — match the description to the definition.

### Why this pattern

- **Reprocessing** — because Bronze keeps raw data, you can rebuild Silver/Gold if logic changes.
- **Incremental & streaming** — each hop can be a streaming query (Auto Loader → Bronze, then stream Bronze → Silver → Gold), giving near-real-time refined data.
- **Data quality** — validation/enforcement happens progressively; downstream consumers trust Silver/Gold.
- **Separation of concerns** — raw ingestion, cleaning, and business logic are distinct, testable stages.

### How Auto Loader + streaming + medallion fit together

A typical incremental pipeline:

1. **Auto Loader** ingests raw files → **Bronze** Delta table (streaming, append).
2. A **streaming** read of Bronze cleans/dedupes/joins → **Silver** Delta table.
3. A **streaming or batch** aggregation of Silver → **Gold** tables for BI.

Each hop has its **own checkpoint**. This whole flow is exactly what **Delta Live Tables** (next file) automates declaratively.

> **Exam Tip:** Auto Loader typically feeds the **Bronze** layer (raw ingestion). Transformations between layers are Structured Streaming (or batch) jobs, each with its own checkpoint. **Delta Live Tables** is the managed framework that builds this multi-hop pipeline for you.

---

## Quick Review

- **Auto Loader** = incremental file ingestion via **`format("cloudFiles")`**; auto-tracks processed files (no reprocessing), scales to millions of files, infers/evolves schema (`schemaLocation`, `_rescued_data`).
- **Directory listing** mode (default, simple) vs **file notification** mode (scales for huge file counts).
- **Medallion / multi-hop**: **Bronze** (raw as-ingested) → **Silver** (clean/dedupe/validate/join) → **Gold** (business aggregates).
- Bronze preserves raw data so downstream layers can be **rebuilt**; each hop can be a streaming query with its **own checkpoint**.
- Auto Loader → Bronze is the canonical ingestion pattern; **DLT** automates the whole multi-hop flow.

---

## Further Learning — Docs & Videos

**Official documentation**
- Auto Loader: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/index.html
- Auto Loader schema inference & evolution: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/schema.html
- Auto Loader file detection modes: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes.html
- Medallion architecture: https://docs.databricks.com/en/lakehouse/medallion.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Auto Loader explained: https://www.youtube.com/results?search_query=databricks+auto+loader+cloudfiles+tutorial
- Medallion / bronze silver gold: https://www.youtube.com/results?search_query=databricks+medallion+architecture+bronze+silver+gold
- Incremental ingestion pipeline: https://www.youtube.com/results?search_query=databricks+auto+loader+medallion+pipeline

---

Next: **[08 — Delta Live Tables (DLT)](08_Delta_Live_Tables.md)**.
