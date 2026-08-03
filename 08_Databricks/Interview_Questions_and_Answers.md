# Azure Databricks — Interview Questions & Answers

Covers the whole module: [Platform](01_What_is_Databricks.md), [Clusters](03_Clusters_and_Compute.md), [Notebooks/Repos/Jobs](04_Notebooks_Repos_and_Jobs.md), [Unity Catalog](06_Unity_Catalog.md), [DLT](08_Delta_Live_Tables.md), [Auto Loader](09_Auto_Loader_and_Ingestion.md). Tagged **[Theory]** / **[Scenario]**, ⭐ = very frequently asked. See also the [Databricks interview folder](../Job%20Interviews/Azure%20Databricks/Databricks%20Interview%20Questions.md) and [Performance Optimization](../Job%20Interviews/Azure%20Databricks/Performance%20Optimization.md).

---

## Platform & architecture

**1. ⭐ [Theory] What is Azure Databricks?**
A managed, Azure-integrated Apache Spark + Delta Lake platform that unifies data engineering, analytics, and ML on one lakehouse. It bundles managed clusters, notebooks, Delta Lake, Unity Catalog governance, and Jobs orchestration, integrated with Entra ID, ADLS, and Key Vault.

**2. ⭐ [Theory] Explain the control plane vs data plane.**
The **control plane** (managed by Databricks in their cloud) holds the web UI, notebook source, job/cluster orchestration, and Unity Catalog metadata. The **data plane** (in *your* Azure subscription) runs the actual cluster VMs and holds your data in your storage/VNet. So orchestration is Databricks-managed, but compute and data stay in your account — the core security answer.

**3. [Scenario] Security asks, "Does Databricks have access to our data?" What do you say?**
Data and compute live in the data plane inside our own subscription and network; the control plane only orchestrates and stores metadata, not our data. We further harden with VNet injection, Private Link, secure cluster connectivity (no public worker IPs), and customer-managed keys.

**4. [Theory] Databricks vs open-source Spark?**
Databricks *is* Spark, plus managed cluster lifecycle, Photon (vectorized engine), Delta optimizations (liquid clustering, deletion vectors), Unity Catalog, DLT, Auto Loader, Databricks SQL, and MLflow — you get Spark without running the infrastructure.

**5. [Theory] What is the Databricks Runtime (DBR)?**
A pre-built image bundling a specific Spark version, Delta, and libraries that a cluster runs. Variants include standard, ML (adds ML libraries), and Photon. Pin versions for production reproducibility.

---

## Clusters & compute

**6. ⭐ [Theory] All-purpose vs job cluster?**
All-purpose (interactive) clusters stay up for humans — development, ad-hoc, shared work. A job cluster is created for a single job run and destroyed when it finishes, making it far cheaper for scheduled production work. Rule: interactive clusters for people, job clusters for jobs.

**7. ⭐ [Scenario] Your Databricks bill is too high. How do you cut it?**
Move scheduled jobs to job clusters (not always-on interactive ones), set aggressive auto-termination, right-size VM types to the workload, use instance pools to cut startup cost, use spot workers with on-demand fallback (never spot driver), and enforce it all with cluster policies. Read the Spark UI to right-size instead of guessing.

**8. [Theory] What is Photon?**
A native C++ vectorized execution engine that speeds up SQL/DataFrame operations (scans, joins, aggregations). It costs more DBUs/hour but often finishes faster, lowering total cost. It doesn't accelerate arbitrary Python UDFs.

**9. [Scenario] A job is slow, so a junior doubles the number of workers and it's still slow. Why?**
Likely skew or a giant shuffle — one bottleneck task doesn't get faster with more small workers. Diagnose in the Spark UI (task spill, one long task, big shuffle read) and fix the job (broadcast the small side, repartition, mitigate skew) rather than throwing compute at it.

**10. [Theory] What are instance pools and cluster policies?**
Instance pools keep warm idle VMs so clusters start in seconds instead of minutes. Cluster policies constrain what users can create (VM types, autoscale limits, auto-termination, tags) — how a platform team controls cost and security at scale.

**11. [Theory] When do you use a SQL warehouse instead of a cluster?**
For BI/SQL serving — dashboards, high-concurrency SQL, Power BI — where you want fast startup (serverless), high concurrency, and result caching. Clusters are for Spark engineering work.

---

## Notebooks, Repos & Jobs

**12. ⭐ [Theory] How do you orchestrate pipelines in Databricks?**
With Jobs/Workflows: tasks (notebook, script, SQL, DLT, or dbt) arranged as a DAG with dependencies, run on a schedule or trigger, on job clusters, with retries, timeouts, and alerts.

**13. ⭐ [Scenario] How do you handle a database password in a notebook?**
Never hardcode it. Store it in a secret scope backed by Azure Key Vault and read it at runtime with `dbutils.secrets.get()`, so the credential never appears in code or output.

**14. [Scenario] How do you make one notebook run for any date (dev/prod, daily/backfill)?**
Parameterize with widgets (`dbutils.widgets`) and pass values as job parameters, so the same notebook serves every environment and date instead of copy-pasting variants.

**15. [Theory] How do notebooks fit into version control and CI/CD?**
Databricks Repos connect a workspace folder to Git (Azure DevOps/GitHub) for branching and PRs. CI/CD pipelines run tests and deploy to workspaces — often via Databricks Asset Bundles — with business logic extracted into unit-tested Python libraries.

**16. [Scenario] When would you use ADF or Airflow instead of Databricks Workflows?**
When orchestration spans multiple systems beyond Databricks (an ADF copy, a Synapse proc, a Power BI refresh). A tool-agnostic conductor (ADF/Airflow) runs the top-level pipeline and calls Databricks jobs as one step.

---

## Unity Catalog

**17. ⭐ [Theory] What is Unity Catalog?**
Databricks' centralized governance layer — one org-wide model for access control, metadata, lineage, discovery, and audit across all workspaces, replacing scattered per-workspace Hive metastores.

**18. ⭐ [Theory] Explain the three-level namespace.**
`catalog.schema.table`. Unity Catalog adds the **catalog** level above the legacy Hive two-level `schema.table`, enabling clean dev/prod or domain separation, all under a regional metastore.

**19. [Theory] How does Unity Catalog do fine-grained security?**
SQL `GRANT`/`REVOKE` at table level, plus column masking and row filters defined once and enforced on every query. Identity comes from Microsoft Entra ID groups synced via SCIM.

**20. [Scenario] Auditors need to know who can see PII and where a Gold metric came from. How does UC help?**
Column masking hides PII from unauthorized groups; row filters restrict rows by region/tenant; automatic column-level lineage shows the Gold metric's upstream source columns; and every access is logged for audit — all under one permission model tied to Entra ID.

**21. [Theory] How does UC govern raw file paths, and what does it replace?**
Via storage credentials (a managed identity) plus external locations over ADLS, replacing insecure DBFS mounts (which are deprecated).

---

## DLT & Auto Loader

**22. ⭐ [Theory] What are Delta Live Tables (DLT)?**
A declarative pipeline framework: you define each table as a function of upstream tables plus quality rules, and DLT builds the DAG, processes incrementally, manages compute, enforces expectations, and handles recovery. (Rebranded as Lakeflow Declarative Pipelines.)

**23. [Theory] What are DLT expectations?**
Inline data-quality rules: `expect` (warn, keep row), `expect_or_drop` (drop bad rows, keep running), `expect_or_fail` (fail the run). Violations are tracked as monitorable metrics.

**24. [Theory] Streaming table vs materialized view in DLT?**
A streaming table ingests append-only incremental data, each record processed once (great for Bronze). A materialized view is the full result of a query, recomputed (incrementally where possible) when inputs change (great for Gold aggregates).

**25. ⭐ [Theory] What is Auto Loader and what problem does it solve?**
A Databricks source (`cloudFiles`) that incrementally ingests only newly-arrived files exactly-once via a checkpoint, scaling to millions of files without ever-slower directory scans — the standard way to load Bronze.

**26. [Theory] Auto Loader: directory listing vs file notification?**
Directory listing diffs the directory each run (simple, moderate volumes). File notification reacts to Azure Event Grid + Queue storage events (scales to millions of files, lower latency, more setup).

**27. [Scenario] Upstream starts sending a new column. What happens with Auto Loader?**
With schema evolution enabled, the new column is added automatically (older rows null), and anything that doesn't fit lands in the `_rescued_data` column instead of being silently dropped — so the pipeline neither crashes nor loses data. Monitor `_rescued_data` to catch drift.

**28. [Scenario] Auto Loader vs COPY INTO — which and why?**
COPY INTO is a simple idempotent SQL batch load for modest/occasional volumes; Auto Loader is for high-volume, continuous, schema-evolving ingestion. Thousands of files/occasional → COPY INTO; millions/continuous → Auto Loader.

**29. [Scenario] Someone deleted the checkpoint folder to "clean up." What happens?**
The stream loses its processed-file state — it reprocesses everything from scratch (duplicates) or, depending on setup, loses progress. The checkpoint is critical production state, one per stream, never hand-edited or deleted.

---

## Putting it together

**30. [Scenario] Design a Databricks ingestion-to-serving pipeline for hourly sales files.**
Auto Loader (`availableNow` triggered, hourly) ingests new files into a DLT Bronze streaming table; DLT Silver applies `expect_or_drop` quality rules and dedupes; DLT Gold builds materialized-view aggregates. Tables are governed by Unity Catalog; the pipeline runs on job/managed compute; Power BI reads Gold via a SQL warehouse. Secrets come from Key Vault; the whole thing is versioned in a Repo and deployed via CI/CD.

---

## Related Notes

- Module: [00 Learning Path](00_Databricks_Learning_Path.md) → [01](01_What_is_Databricks.md) · [02](03_Clusters_and_Compute.md) · [03](04_Notebooks_Repos_and_Jobs.md) · [04](06_Unity_Catalog.md) · [05](08_Delta_Live_Tables.md) · [06](09_Auto_Loader_and_Ingestion.md)
- [Lakehouse](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Delta Lake](../05_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) · [PySpark](../03_Programming/PySpark/00_PySpark_Learning_Path.md)
- Cert track: [Databricks Data Engineer Associate](../Certifications/Databricks_Data_Engineer_Associate/00_Study_Guide_Overview.md)
