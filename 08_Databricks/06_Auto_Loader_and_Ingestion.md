# Auto Loader & Incremental Ingestion

## What is it?

**Auto Loader** is a Databricks feature that **incrementally and efficiently ingests new files** as they land in cloud storage — automatically detecting which files are new, without you tracking them or reprocessing everything each run. It's the standard way to load the **Bronze** layer of a [medallion pipeline](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) from a stream of arriving files.

Under the hood it's a Structured Streaming source (`cloudFiles`) that remembers what it has already processed via a checkpoint, so each run picks up only the new files — exactly-once, at scale.

In one line: **Auto Loader = "process only the new files that arrived, automatically" — incremental file ingestion done right.**

---

## Analogy: the mailroom that only opens new mail

Imagine a mailroom that receives thousands of letters a day into one big inbox. The naïve approach is to re-read *every* letter each morning to find the new ones — slow and wasteful as the pile grows. **Auto Loader is a clerk who keeps a checklist of every letter already handled**: each morning they open *only* the letters not on the list, process them, and tick them off. The pile can grow to millions of letters and the morning's work still only touches what actually arrived overnight.

---

## The problem it solves

You have files landing continuously in ADLS (hourly exports, event dumps, uploads). You need each file processed **exactly once**, cheaply, even as the folder accumulates millions of files. The naïve options all fail:

- **List the whole directory every run** → gets slower forever as files accumulate.
- **Track processed files yourself** → fragile, custom bookkeeping that breaks.
- **Reprocess everything** → duplicates and wasted compute.

Auto Loader solves all three: it tracks state in a checkpoint and scales file discovery.

---

## Example

```python
df = (spark.readStream
      .format("cloudFiles")                         # ← Auto Loader
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/chk/schema")
      .load("abfss://landing@acct.dfs.core.windows.net/orders/"))

(df.writeStream
   .option("checkpointLocation", "/chk/orders")     # ← remembers processed files
   .trigger(availableNow=True)                       # process all new, then stop
   .toTable("bronze.orders"))
```

Run it hourly and it ingests only the files that arrived since last run — no manual tracking. Inside [DLT](05_Delta_Live_Tables.md), the same source powers a streaming Bronze table.

---

## File discovery: directory listing vs file notification

Auto Loader finds new files two ways:

| Mode | How it works | Best for |
|---|---|---|
| **Directory listing** (default) | Lists the storage directory, diffing against state | Simpler setup, low-to-moderate file volumes |
| **File notification** | Subscribes to cloud events (Azure Event Grid + Queue) fired when a file lands | Very high file volumes, lower latency, avoids listing cost |

File notification scales to millions of files because it reacts to events instead of scanning the directory — the pro choice at scale.

---

## Schema inference & evolution

Auto Loader can **infer** the schema from incoming files and **evolve** it as new columns appear:

- `cloudFiles.schemaLocation` — where the inferred schema is stored.
- `cloudFiles.schemaEvolutionMode` — how to react to new columns (add them, rescue them, or fail).
- **Rescued data column** (`_rescued_data`) — a safety net that captures fields that don't match the expected schema instead of dropping them silently.

This means a new upstream field doesn't crash the pipeline *or* vanish unnoticed — it's handled by policy.

---

## Advantages

- **Incremental & exactly-once** — processes only new files, no duplicates, via checkpoint state.
- **Scales to millions of files** — file-notification mode avoids ever-slower directory listings.
- **Schema inference & evolution** — adapts to changing files with a rescue-column safety net.
- **Simple** — a format string and a checkpoint replace fragile custom bookkeeping.
- **Streaming or scheduled** — `trigger(availableNow=True)` gives batch-style incremental runs; continuous gives low latency.

## Disadvantages

- **Checkpoint is critical state** — deleting/moving it causes reprocessing or data loss; treat it carefully.
- **Databricks-specific** — `cloudFiles` isn't portable to plain open-source Spark.
- **Notification-mode setup** — Event Grid + Queue resources and permissions add configuration.
- **Not for in-place edits** — it's for *new files arriving*, not files being modified in place.

---

## Azure Usage

- **Source:** files in **ADLS Gen2** (the landing/Bronze zone).
- **File notification:** uses **Azure Event Grid** + **Storage Queue** to get notified on blob-created events.
- **`COPY INTO`** — a simpler **SQL** alternative for *smaller, less frequent* batch loads (idempotent, retriable). Rule of thumb: `COPY INTO` for thousands of files or occasional loads; **Auto Loader** for millions of files or continuous ingestion.
- Frequently wrapped inside a **[DLT](05_Delta_Live_Tables.md)** streaming table for the Bronze layer.

---

## Real World Example

A retailer's point-of-sale systems drop a JSON file per store per hour into ADLS — tens of thousands of small files a day, growing forever. Their first pipeline listed the whole directory each run and got slower every week until the hourly job overran its window. Switching to Auto Loader in **file-notification mode**, ingestion reacts to each blob-created event, so run time is proportional to *new* files, not the total. When stores started sending an extra `loyalty_id` field, **schema evolution** added the column automatically and older records simply show null — no pipeline crash, no lost data, no 3 a.m. page.

---
---

# Part 2 — Advanced

## Checkpoints are the source of truth

Auto Loader (like all [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)) records processed-file state and stream progress in the **checkpoint location**. This is what guarantees exactly-once and enables resume-after-failure. Consequences: never point two streams at the same checkpoint, never hand-edit it, and understand that *deleting* it means "reprocess everything from scratch." The checkpoint is production state, not a temp folder.

## `trigger(availableNow=True)` — incremental batch

You don't need an always-on stream. `availableNow=True` processes all files available *now* in one micro-batch series, then stops — giving you cheap, scheduled, incremental batch loads with streaming's exactly-once guarantees. This is the most common Auto Loader pattern for hourly/daily pipelines: the economics of batch with the correctness of streaming.

## Rescued data — never lose a field silently

The `_rescued_data` column captures any incoming field that doesn't fit the current schema (type mismatch, unexpected column). Instead of the classic silent data-loss bug (a renamed upstream field quietly dropped for weeks), the value is preserved in `_rescued_data` for inspection. Monitoring this column tells you when upstream schemas drift.

## Auto Loader vs `COPY INTO` vs plain read

- **Plain `spark.read`** — reprocesses everything each run; fine for a fixed one-off load, wrong for continuous arrival.
- **`COPY INTO`** — idempotent SQL batch load, tracks loaded files; good for modest volumes and simple ELT.
- **Auto Loader** — the scalable, low-latency, schema-evolving choice for high-volume continuous ingestion.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Ingestion latency vs cost is a dial, not a default

`availableNow` triggered runs (hourly/daily) minimize cost; continuous streaming minimizes latency; file-notification mode cuts both listing cost and latency at high volume. The pro picks the point on that dial from the *business* need — "dashboards can be an hour stale" means triggered batch, not an always-on cluster burning DBUs for latency nobody asked for. Matching ingestion cadence to requirements is where real money is saved.

## The small-file problem starts at ingestion

Auto Loader faithfully ingests whatever arrives — including millions of tiny files, which then produce a poorly-laid-out Bronze table that's slow to query ([small-file problem](../05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md)). The fix isn't in Auto Loader; it's **compacting downstream** (`OPTIMIZE`, or letting Silver rewrite into well-sized files) and not partitioning Bronze to death. Think about file layout at every hop, not just ingestion.

## File-notification mode: powerful but operationally heavier

At millions of files, notification mode is the right call — but it introduces Event Grid + Queue resources that need permissions, monitoring, and cleanup, and orphaned notification queues are a real operational smell. Adopt it when directory listing genuinely can't keep up, and own the extra plumbing deliberately.

## Field-tested gotchas

- **Deleting/moving the checkpoint** — silently causes full reprocessing (duplicates) or data loss.
- **Two streams sharing one checkpoint** — corrupts state; one checkpoint per stream.
- **Ignoring `_rescued_data`** — upstream schema drift hides there unmonitored.
- **Using Auto Loader for modified-in-place files** — it's for *new files arriving*, not edits to existing ones.
- **Continuous stream where triggered batch would do** — paying for always-on latency the business doesn't need.
- **Tiny-file flood straight into an unmanaged Bronze** — compact downstream or queries crawl.

## Interview-grade Q&A

- *What is Auto Loader and what problem does it solve?* A Databricks source (`cloudFiles`) that incrementally ingests only newly-arrived files exactly-once via a checkpoint, scaling to millions of files without ever-slower directory scans.
- *Directory listing vs file notification?* Listing diffs the directory each run (simple, moderate volumes); notification reacts to cloud storage events via Event Grid + Queue (scales to millions, lower latency, more setup).
- *How does it handle changing schemas?* Schema inference plus evolution modes, with a `_rescued_data` column capturing fields that don't fit — so new columns don't crash the pipeline or vanish silently.
- *Auto Loader vs COPY INTO?* COPY INTO is a simple idempotent SQL batch load for modest volumes; Auto Loader is for high-volume, continuous, schema-evolving ingestion.
- *Why is the checkpoint so important?* It stores processed-file state and stream progress — the basis of exactly-once and resume; deleting it forces full reprocessing.

---

## Related Notes

- **Prev:** [Delta Live Tables](05_Delta_Live_Tables.md) · **Module start:** [Learning Path](00_Databricks_Learning_Path.md)
- **Streaming:** [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md) · **Bronze layer:** [Lakehouse Architecture](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)
- **Integration patterns:** [Integration Patterns](../06_Data_Engineering/Data_Integration/02_Integration_Patterns.md)
- **Cert:** [Auto Loader & Multi-Hop](../Certifications/Databricks_Data_Engineer_Associate/07_Auto_Loader_and_Multi_Hop.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Auto Loader: https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/
- COPY INTO: https://learn.microsoft.com/en-us/azure/databricks/ingestion/copy-into/

**Videos**
- Databricks Auto Loader explained: https://www.youtube.com/results?search_query=databricks+auto+loader+explained
- Auto Loader vs COPY INTO: https://www.youtube.com/results?search_query=databricks+auto+loader+vs+copy+into
