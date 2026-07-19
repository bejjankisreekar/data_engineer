# Data Pipelines

## What is a Data Pipeline?

A **Data Pipeline** is a series of automated steps that moves data from one or more sources to a destination, typically transforming it along the way — the general engineering concept that [ETL and ELT](01_ETL_vs_ELT.md) are two specific *patterns* of.

Analogy: an assembly line. Raw materials (source data) enter at one end; a sequence of stations each perform one step (extract, validate, transform, load); the finished product (analysis-ready data) comes out the other end, on a schedule, without a person manually pushing it through each station every time.

Every pipeline, regardless of tool, is built from the same handful of components:

| Component | Role |
|---|---|
| **Source** | Where data originates — a database, an API, a file drop, a message queue |
| **Extraction** | Pulling data out of the source |
| **Transformation** | Cleaning, reshaping, validating, enriching |
| **Orchestration** | Deciding *when* and *in what order* steps run, and what happens on failure |
| **Load / Sink** | Where the result lands — a warehouse, a lakehouse table, another system |
| **Monitoring** | Confirming the pipeline actually ran, and ran correctly |

---

## Batch vs Streaming pipelines

| | Batch | Streaming |
|---|---|---|
| Processes | A bounded chunk of data (yesterday's orders, this hour's files) | An unbounded, continuous flow of events as they arrive |
| Latency | Minutes to hours (whatever the schedule is) | Seconds to minutes |
| Typical trigger | A schedule (nightly at 2am) | Continuous, or a tight micro-batch interval |
| Example tool | [Azure Data Factory](02_Azure_Data_Factory.md) Copy Activity, a nightly Spark job | Kafka/Event Hubs + [Spark Structured Streaming](../06_PySpark/13_Structured_Streaming.md) |

Most "streaming" pipelines in real production estates are actually **incremental batch** — a streaming engine running on `trigger(availableNow=True)` on a schedule, getting streaming's exactly-once bookkeeping without paying for a 24/7 cluster. True continuous, always-on streaming is reserved for genuinely latency-sensitive use cases (fraud detection, live dashboards) — see the full trigger discussion in [Structured Streaming](../06_PySpark/13_Structured_Streaming.md).

---

## Real World Example

A ride-sharing company's pricing pipeline: every completed ride (source: an event from the mobile app) is extracted via a message queue, transformed (fare calculated, surge multiplier applied, currency normalized), and loaded into both a warehouse table (for finance reporting, batched hourly) and a real-time dashboard (for operations, streamed continuously) — two different pipelines, sharing one source, built for two different latency needs.

---

## Azure Usage

[Azure Data Factory](02_Azure_Data_Factory.md) and Databricks Workflows are the two most common pipeline-orchestration tools on Azure; dbt handles the transformation layer specifically inside a warehouse/lakehouse. See [Azure Data Factory](02_Azure_Data_Factory.md) for the Azure-specific building blocks (pipelines, activities, datasets, linked services, triggers).

---
---

# Part 2 — Advanced

## Pipeline design patterns

- **Sequential** — step B can't start until step A finishes (extract must complete before transform can begin on that data).
- **Parallel / fan-out** — one source feeds several independent downstream steps at once (the same extracted data loads into both a warehouse and a search index simultaneously).
- **Fan-in** — several independent upstream pipelines converge into one downstream step (five regional extracts all feed one consolidated load).
- **DAG-based orchestration** — most real pipelines are a **Directed Acyclic Graph** of tasks with dependencies, not a single straight line; the orchestrator's job is resolving that graph — running independent branches in parallel, respecting dependencies, and deciding what happens when one node fails.

```
extract_orders ──┐
                  ├──▶ merge_and_validate ──▶ load_to_warehouse
extract_customers ┘                       └─▶ load_to_search_index
```

## Idempotency — the property every pipeline needs

A pipeline step is **idempotent** if running it twice produces the same correct result as running it once — critical because orchestrators retry failed steps, and a half-completed run followed by a blind retry must never duplicate data. The concrete patterns (MERGE by key, scoped atomic overwrite, staging-plus-swap) are covered in depth in [ETL vs ELT](01_ETL_vs_ELT.md#part-3--pro-level-what-10-year-engineers-know) and [Delta Lake MERGE](../06_PySpark/12_Delta_Lake_with_PySpark.md) — every pipeline, batch or streaming, needs one of these patterns at its write step.

## Orchestration tools, at a glance

| Tool | Style | Sweet spot |
|---|---|---|
| **Azure Data Factory** | Visual, drag-and-drop, metadata-driven | Movement + hybrid/on-prem connectivity ([detail](02_Azure_Data_Factory.md)) |
| **Databricks Workflows / Lakeflow** | Code-first, notebook/Delta-native | Teams already living in Databricks |
| **Apache Airflow** | Code-first Python DAGs | Maximum orchestration flexibility, self-operated |
| **dbt** | SQL-model-based, transformation-only | The "T" specifically, inside a warehouse/lakehouse (not extraction or scheduling) |
| **Dagster / Prefect** | Code-first, asset/data-aware orchestration | Teams wanting stronger data-lineage-aware scheduling than Airflow's task-centric model |

## Trigger types

- **Schedule-based** — runs at a fixed time/interval (nightly at 2am).
- **Event-based** — runs in response to something happening (a new file lands in a landing zone, a message arrives on a queue).
- **Sensor/dependency-based** — waits for an upstream condition (another pipeline's success, a file's existence) before starting.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Observability: the difference between "ran" and "worked"

A pipeline showing green/succeeded is not the same as a pipeline that did the right thing — a run that copied zero rows, or silently skipped a downstream step due to a dependency condition, still reports success. Production-grade pipelines instrument three things beyond the run status itself:

- **Row-count / volume reconciliation** — expected vs. actual rows moved, logged every run and alerted on deviation ([the instrumentation habit](../01_SQL/08_SQL_Aggregate_Functions.md)).
- **Freshness / absence alerting** — "the nightly load hasn't succeeded by 6am" is often a *worse* failure than a loud crash, because nobody notices until a stakeholder asks why yesterday's numbers look stale.
- **Lineage** — knowing which downstream tables/reports a given pipeline feeds, so an upstream failure's blast radius is knowable in seconds, not discovered by a confused analyst hours later.

## Failure handling patterns

- **Retry with exponential backoff + jitter** — the default response to transient failures (a network blip, a momentary source-system lock); backing off avoids retry storms that turn one flaky dependency into a cascading outage.
- **Dead-letter queue** — records that repeatedly fail processing are diverted to a quarantine location instead of blocking the whole batch or being silently dropped; someone reviews the dead-letter queue rather than losing the data entirely.
- **Circuit breaker** — after repeated failures calling a downstream system, a pipeline temporarily stops trying (instead of hammering an already-struggling dependency) and resumes after a cooldown.
- Critically: **distinguish pipeline failure from data failure**. A transient infrastructure issue should retry; a genuinely malformed input batch should not blindly retry the same way, since that just reprocesses (and can duplicate) the same bad data — this distinction is exactly what separates a pipeline that self-heals from one that quietly corrupts itself on every bad day.

## Pipeline-as-code and CI/CD

Mature teams treat pipeline definitions the same as application code: version-controlled, code-reviewed, and promoted through dev → test → prod via CI/CD rather than edited by hand in a portal. See [Azure Data Factory's CI/CD section](02_Azure_Data_Factory.md#part-3--pro-level-what-10-year-engineers-know) for the concrete Azure pattern (git-integrated workspace, ARM/Bicep deployment, environment-parameterized linked services) — the same discipline applies whether the orchestrator is ADF, Airflow, or Databricks Workflows.

## Field-tested gotchas

- **"It ran" is not a test** — a pipeline with no data-quality assertions doesn't "work," it just hasn't been caught failing yet; quality gates belong at every layer boundary, not just at the very end.
- **Hardcoded environment values** (a dev database connection string baked into a "temporary" pipeline) are the most common reason a pipeline that worked in testing corrupts production data the first time it's promoted — parameterize environment from day one.
- **A backfill is a production event, not a rerun button** — replaying months of historical data through a pipeline sized for one day's volume can overwhelm downstream systems or a source database; throttle and partition backfills deliberately, and warn downstream consumers before running one.
- **Silent partial success** — a fan-out pipeline where one of three parallel downstream loads fails while the other two succeed can report an ambiguous overall status unless the orchestrator's failure semantics are explicitly understood and tested.

## Interview-grade Q&A

- *What are the core components of a data pipeline?* Source, extraction, transformation, orchestration, load/sink, monitoring.
- *Batch vs streaming — how do you decide?* Match the pattern to the actual latency requirement; most "streaming" needs are really well served by scheduled incremental batch, reserving true continuous streaming for genuinely latency-sensitive cases.
- *What makes a pipeline idempotent, and why does it matter?* Safe to re-run without duplicating/corrupting data — matters because orchestrators retry failed runs, and a non-idempotent pipeline turns every retry into a potential data-quality incident.
- *How do you handle a step that keeps failing on bad input data?* Route it to a dead-letter queue rather than blind-retrying (which reprocesses the same bad record) or silently dropping it — quarantine and alert, don't loop.
- *What's the difference between a pipeline succeeding and a pipeline being correct?* Success is a run-status flag; correctness requires row-count reconciliation, freshness monitoring, and data-quality assertions — a "green" pipeline can still have moved zero rows or skipped a downstream step.

Back to the folder: [ETL vs ELT](01_ETL_vs_ELT.md) · [Azure Data Factory](02_Azure_Data_Factory.md)
