# 13 — Structured Streaming

> Prev: [Delta Lake](12_Delta_Lake_with_PySpark.md) · Next: [Performance & Best Practices](14_Performance_and_Best_Practices.md)

Structured Streaming's core idea: **a stream is an unbounded table**, and your existing DataFrame code runs on it incrementally. Same API, same optimizer — `read` becomes `readStream`, `write` becomes `writeStream`, and Spark keeps processing new data forever ([why this unified batch and streaming](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md)).

---

## A first stream

```python
# Source: files landing in a folder (Auto Loader on Databricks)
events = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "abfss://chk@lake.../schemas/events")
    .load("abfss://landing@lake.../events/"))

# Transformations: IDENTICAL to batch — filters, columns, joins to static dims...
clean = (events
    .filter(F.col("event_type").isNotNull())
    .withColumn("event_date", F.to_date("ts")))

# Sink + the streaming-specific choices
query = (clean.writeStream
    .format("delta")
    .option("checkpointLocation", "abfss://chk@lake.../events_bronze")   # NON-NEGOTIABLE
    .outputMode("append")
    .trigger(availableNow=True)          # see trigger table below
    .toTable("bronze.events"))

query.awaitTermination()                 # scripts; notebooks can just let it run
```

Three new concepts and that's genuinely most of it:

| Concept | Meaning |
|---|---|
| **Checkpoint** | The stream's memory: which input has been processed, plus any state. One folder **per query**, never shared, never deleted casually — delete it and the stream starts over (or duplicates). |
| **Output mode** | `append` (new rows only — the normal one), `complete` (rewrite full aggregate result), `update` (changed rows) |
| **Trigger** | The heartbeat — see *Triggers, aggregations, and watermarks* below |

### Kafka / Event Hubs source

```python
raw = (spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "...:9093")
    .option("subscribe", "orders")
    .option("startingOffsets", "earliest")
    .load())
# value is BINARY → cast and parse (file 09)
orders = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("d")).select("d.*")
```

---

## Triggers, aggregations, and watermarks

### Triggers — how often the stream fires

```python
.trigger(availableNow=True)                    # process ALL pending, then STOP — "incremental batch"
.trigger(processingTime="1 minute")            # micro-batch every minute, forever
# (default: next micro-batch as soon as the previous finishes)
```

**`availableNow` is the workhorse**: schedule it hourly/nightly and you get *incremental batch* — streaming's bookkeeping (exactly-once, no reprocessing) with batch's costs (cluster runs only while working). Most "streaming" pipelines in production are exactly this. Continuous 24/7 clusters are for genuine minutes-matter latency.

### Streaming aggregations need watermarks

Aggregating a stream means keeping **state** (running counts per key/window). Without a bound, state grows forever — the **watermark** declares how late data may arrive, letting Spark finalize and drop old state:

```python
counts = (events
    .withWatermark("ts", "30 minutes")                     # accept data ≤30 min late
    .groupBy(F.window("ts", "5 minutes"), "region")        # tumbling 5-min windows
    .agg(F.count("*").alias("events")))

(counts.writeStream.outputMode("append")                    # append emits a window only once FINALIZED
    .option("checkpointLocation", chk).toTable("gold.event_counts"))
```

Consequences to internalize: events later than the watermark are **dropped** (measure your real lateness before choosing!); `append` mode emits each window only after the watermark passes (built-in latency = window + lateness); `F.window()` gives tumbling/sliding time buckets. Deduplication uses the same state machinery: `df.withWatermark("ts", "1 hour").dropDuplicates(["event_id"])`.

### foreachBatch — the escape hatch that runs your batch code per micro-batch

```python
def upsert(batch_df, batch_id):
    (DeltaTable.forName(spark, "silver.orders").alias("t")
     .merge(batch_df.dropDuplicates(["order_id"]).alias("s"), "t.order_id = s.order_id")
     .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())

(orders.writeStream.foreachBatch(upsert)
    .option("checkpointLocation", chk).trigger(availableNow=True).start())
```

**Streaming MERGE** — the standard CDC-to-silver pattern ([MERGE rules apply](12_Delta_Lake_with_PySpark.md)). Inside `foreachBatch` you have a normal DataFrame and can do anything — write to two tables, call JDBC — but *you* own idempotency then (use `batch_id`, and note multi-sink writes aren't atomic across sinks).

---

## Pro corner

- **Exactly-once, spelled out**: replayable source (Kafka offsets / file lists) + checkpoint (what's been read) + transactional sink (Delta) = end-to-end exactly-once *for the default single-sink path*. Every deviation (foreachBatch to two places, non-transactional sinks) drops you to at-least-once — design [idempotent](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) anyway.
- **Checkpoints are married to the query's logic**: changing the aggregation/schema/key of a stateful query makes the old checkpoint unusable (or wrong). Plan "how do we evolve this stream" *before* production: usually new checkpoint + backfill, or foreachBatch with versioned logic.
- **Monitoring**: `query.lastProgress` (per-batch JSON: input rows, duration, state size, watermark lag) — ship it to logs/metrics; the two alarms that matter are **backlog growth** (processing slower than arrival) and **state size growth** (watermark not dropping state — check event-time skew or a stuck source partition).
- **Stateful skew**: `groupBy(user_id)` state with one bot user = one giant state partition — same [skew playbook](Spark_Processing.md), plus consider whether the key needs sub-bucketing.
- **Stream-stream joins** exist (both sides watermarked, bounded buffers) but are the hardest feature to operate — prefer stream-static joins (stream × Delta dim, refreshed by its own pipeline) whenever the use case allows; it's also 90% of real needs.
- **DLT / Lakeflow Declarative Pipelines**: Databricks' managed layer over all of this (declare tables + expectations; it owns checkpoints, retries, compaction). Worth adopting once hand-rolled streams multiply — concepts here transfer 1:1.
- Small files: streaming's [signature failure mode](12_Delta_Lake_with_PySpark.md) — enable auto-compaction or scheduled OPTIMIZE from day one, and keep checkpoint folders out of lifecycle/tiering policies ([storage gotcha](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md)).

## Checkpoint

1. Build the incremental-batch pipeline: JSON landing → Auto Loader → dedupe → MERGE to silver, hourly, exactly-once. Which trigger, and where does dedupe happen?
2. Your 10-min windowed counts never appear in the output table. Two likeliest causes?
3. Why can't you just fix a bug in a stateful stream and restart on the same checkpoint?

Next, the capstone: making it all fast and production-worthy → [14 — Performance & Best Practices](14_Performance_and_Best_Practices.md).

---

## Further Learning — Docs & Videos

**Documentation**
- Structured Streaming programming guide: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- Databricks Structured Streaming: https://docs.databricks.com/en/structured-streaming/index.html

**Videos**
- Spark Structured Streaming tutorial: https://www.youtube.com/results?search_query=spark+structured+streaming+pyspark+tutorial
