# Azure Data Factory (ADF)

## What is it?

Azure Data Factory is Azure's tool for building, scheduling, and monitoring data pipelines — largely through a visual, drag-and-drop interface rather than writing code from scratch.

Analogy: if moving and transforming data is an assembly line, Data Factory is the control room where you design the assembly line's layout, set it running on a schedule, and watch a dashboard to confirm every station did its job.

---

## Core Building Blocks

| Term | What it means |
|---|---|
| Pipeline | The overall workflow — a sequence of steps (activities) that run in order |
| Activity | A single step inside a pipeline, e.g. "copy this file" or "run this transformation" |
| Dataset | A pointer to a specific piece of data an activity reads or writes (a table, a file, a folder) |
| Linked Service | The connection details for a data source or destination (like a saved login for a database or storage account) |
| Trigger | What starts a pipeline running — a schedule (every night at 2am), or an event (a new file arrives) |

---

## A Simple Example Pipeline

```
Trigger: every night at 2 AM
   ↓
Activity 1: Copy sales data from an on-premises SQL Database
   ↓
Activity 2: Copy the data into Azure Data Lake Storage (raw layer)
   ↓
Activity 3: Run a transformation (e.g. via Databricks) to clean the data
   ↓
Activity 4: Load the cleaned result into Azure Synapse Analytics
```

This is a textbook [ETL/ELT](01_ETL_vs_ELT.md) pipeline, built entirely by connecting boxes on a canvas rather than writing custom scripts for every step.

---

## Why not just write a script?

You could write a custom program to move and transform data instead. Data Factory earns its place by handling the parts every pipeline eventually needs, without you building them yourself:

- **Scheduling** — run automatically every night, every hour, or the moment a file lands
- **Monitoring** — a dashboard showing which runs succeeded, failed, or are still running
- **Retry logic** — automatically retry a step that failed due to a temporary network issue
- **Connectors** — pre-built connections to hundreds of data sources (SQL Server, Salesforce, SAP, Amazon S3, and more), so you don't write custom connection code for each one

---

## Copy Activity vs Mapping Data Flow

- **Copy Activity** — moves data from A to B with little or no transformation. Fast, simple, the workhorse of most pipelines.
- **Mapping Data Flow** — a visual way to define actual transformation logic (filtering rows, joining tables, aggregating values) without writing Spark code directly; ADF runs it on a Spark cluster behind the scenes.

---

## Azure Usage

Data Factory typically sits at the center of an Azure data platform, connecting:

- Source systems (on-premises databases, SaaS apps, APIs)
- [Azure Data Lake Storage](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) (raw storage)
- Azure Databricks (heavy transformation)
- Azure Synapse Analytics (final, query-ready warehouse)

---

## Real World Example

A logistics company has package-tracking data sitting in an old on-premises database that only their internal warehouse staff can query. Every night, a Data Factory pipeline copies that day's tracking data into Azure Data Lake Storage, triggers a Databricks job to calculate on-time delivery rates, and loads the result into Synapse — so that by the time the operations team arrives in the morning, a Power BI dashboard already shows yesterday's performance, without anyone manually running a single query.

---
---

# Part 2 — Advanced

## Integration Runtimes — where ADF's work physically happens

ADF itself is a control plane; an **Integration Runtime (IR)** is the compute that executes:

| IR type | Runs | Use |
|---|---|---|
| **Azure IR** | Microsoft-managed, serverless | Cloud-to-cloud copies, data flows |
| **Self-hosted IR (SHIR)** | An agent *you install* inside a private network | On-prem/VNet-locked sources — it dials **out**, so no inbound firewall holes ([hybrid connectivity](../../04_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md)) |
| **Azure-SSIS IR** | Managed SSIS cluster | Lift-and-shift of legacy SSIS packages |

SHIR realities: install ≥2 nodes for HA, size for concurrent copy jobs, patch it like the server it is — it's the piece of "serverless" ADF that is very much a server.

## Parameterization — one pipeline, not one per table

Naive ADF estates have 300 near-identical pipelines. Pros build **metadata-driven** ones:

```
Control table: source_table | watermark_col | target_path | is_active ...
Pipeline: Lookup (read control table)
          → ForEach table:
              Copy: @concat('SELECT * FROM ', item().source_table,
                     ' WHERE ', item().watermark_col, ' > ''', variables('wm'), '''')
              → Stored Proc: update watermark
```

Datasets and linked services take parameters too (one "any SQL table" dataset, one "any lake folder" dataset). Ten objects handle 500 tables — and adding a source becomes an INSERT into the control table, not a deployment ([incremental patterns](01_ETL_vs_ELT.md)).

## Control-flow toolbox beyond Copy

- **Lookup / Get Metadata** — read configs, check files exist.
- **ForEach** (watch the parallelism setting), **If / Switch / Until**.
- **Execute Pipeline** — compose parent/child; **Web/Webhook** — call APIs; **Stored Procedure** — push SQL work to the engine.
- Activity-level **retry, timeout, and `@activity().output`** chaining; failure paths via the red dependency arrows — build the *unhappy* path explicitly (alert → quarantine → mark control row failed).
- **Triggers**: schedule, tumbling-window (stateful, per-window backfillable — the right choice for incremental loads), and event-based (blob arrival).

## The build-vs-buy line inside ADF

Copy Activity: unbeatable for movement (parallelized, resumable, ~100 connectors). **Mapping Data Flows**: visual Spark — fine for simple joins/derivations, but complex logic in a GUI becomes untestable spaghetti. The widely-used enterprise pattern: **ADF for extract/orchestrate/load, Databricks notebooks (or dbt) for transform** — code where logic lives, boxes where plumbing lives ([why Databricks](../../08_Databricks/02_Why_Spark_Why_Databricks.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## ADF in production: CI/CD and environments

The portal's "Publish" button doesn't scale past one developer. The grown-up setup:

- Git-integrated workspace (feature branches → PR review of the pipeline *JSON*).
- ARM/Bicep export (or the newer direct JSON deployment) promoted **dev → test → prod** by pipeline, with per-environment parameter files (linked service endpoints, Key Vault names).
- **All secrets in Key Vault**, referenced by linked services; ADF's **managed identity** granted narrowly on storage/SQL ([identity as perimeter](../../04_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md)) — connection strings pasted into linked services are a security-review finding.
- Naming conventions + folders from day one; a 400-pipeline factory without them is unmaintainable archaeology.

## Monitoring beyond the green ticks

The monitor tab shows *runs*; production needs *outcomes*:

- Ship diagnostics to **Log Analytics**; alert on failure *and* on **absence** ("nightly load hasn't succeeded by 6am" — silent-no-run is the worse failure).
- Track **rows copied vs rows expected** per run in the control table ([reconciliation habit](../../02_Databases/SQL/13_SQL_Warehouse.md)) — a green Copy that moved 0 rows is a data incident wearing a success icon.
- Cost watch: Data Flows bill Spark cluster-minutes (cold-start included); high-frequency tumbling windows multiply activity-run charges; SHIR concurrency limits queue silently — all visible in run details if someone looks.

## ADF vs the field (placement, honestly)

- **ADF / Fabric Data Factory** — best-in-class managed connectors + hybrid movement; orchestration adequate; transforms weak. (Fabric's Data Factory is its successor generation — skills transfer nearly 1:1.)
- **Databricks Workflows** — natural when everything is already notebooks/Delta; no SHIR equivalent for on-prem pulls.
- **Airflow** — maximum control-flow expressiveness, code-first, you operate it.
- The common enterprise answer is **ADF triggering Databricks**: ADF owns extraction (especially on-prem via SHIR) and scheduling; Databricks owns transformation. Choosing *one* tool for everything usually means using its weakest third.

## Field-tested gotchas

- ForEach default parallelism + a target database = accidental DoS on the source; set batch count deliberately ([connection limits](../../02_Databases/SQL/02_SQL_Database.md)).
- Tumbling-window triggers hold state — deleting/recreating one re-fires history unless you set the start date consciously; schedule triggers on a deleted-then-redeployed factory can double-fire against the old instance until cleaned up.
- Copy Activity's implicit type mapping (`String` → everything) quietly forfeits [type fidelity](../../02_Databases/SQL/03_SQL_Data_Types.md) — define explicit mappings or land to Parquet with a declared schema.
- The `Set Variable`-in-ForEach race: variables are pipeline-scoped, parallel iterations overwrite each other — use item-scoped expressions instead.
- SHIR credential storage is per-node — replacing a SHIR machine without exporting credentials strands every on-prem linked service.

## Interview-grade Q&A

- *How does ADF reach an on-prem SQL Server securely?* Self-hosted IR inside the network making outbound-only connections; credentials in Key Vault; managed identity everywhere cloud-side.
- *Design ADF for 500 source tables.* Metadata-driven: control table + parameterized datasets/linked services + Lookup-ForEach-Copy + transactional watermark updates — ten reusable objects, not 500 pipelines.
- *ADF or Databricks for transformation?* Movement and orchestration in ADF; non-trivial transforms as code in Databricks/dbt — testability and code review beat canvas boxes.
- *A pipeline is "green" but the dashboard is stale — where do you look?* Trigger actually firing? Rows-copied metrics? Downstream activity skipped on a dependency condition? Absence-alerts exist precisely because green-but-empty happens.

---

## Further Learning — Docs & Videos

**Documentation**
- Azure Data Factory overview: https://learn.microsoft.com/en-us/azure/data-factory/introduction
- ADF pipelines & activities: https://learn.microsoft.com/en-us/azure/data-factory/concepts-pipelines-activities
- Mapping data flows: https://learn.microsoft.com/en-us/azure/data-factory/concepts-data-flow-overview

**Videos**
- Azure Data Factory tutorial for beginners: https://www.youtube.com/results?search_query=azure+data+factory+tutorial+for+beginners
- ADF end-to-end pipeline: https://www.youtube.com/results?search_query=azure+data+factory+end+to+end+pipeline
