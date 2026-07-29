# 05_ETL_ELT — Interview Questions & Answers

## How to use this file

This folder has only two notes, so this file goes deep rather than wide — theory questions on ETL/ELT trade-offs and Data Factory concepts, mixed with practical design/scenario questions ("design a pipeline for 500 tables," "your nightly job failed at 60%, what does the table look like"). Every question states what it's testing; every answer explains why it's correct.

- **[Frequently Asked]** — core concepts nearly every data engineering interview touches: ETL vs. ELT, ADF's building blocks, Copy Activity vs. Mapping Data Flow, incremental loading, medallion architecture.
- **[Senior/Experienced]** — deeper Pro-level material: metadata-driven pipelines, CI/CD for ADF, idempotent watermarks, data quality as pipeline code, EtLT for compliance.

---

## Table of Contents

1. [ETL vs ELT](#1-etl-vs-elt)
2. [Azure Data Factory](#2-azure-data-factory)
3. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. ETL vs ELT

*(full notes: [01_ETL_vs_ELT.md](01_ETL_vs_ELT.md))*

#### Q1. What is the difference between ETL and ELT? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental, near-guaranteed data engineering interview questions.
**Answer:** Both involve the same three logical steps — Extract, Transform, Load — but differ in **where** the Transform step happens. In ETL, data is cleaned and reshaped on a separate processing server *before* it ever reaches the destination, so the warehouse only ever receives finished data. In ELT, raw data is loaded into the destination *first* and transformed there afterward, using the destination's own processing power. This is correct because it identifies the single actual difference (the position of the T relative to the L) rather than treating them as two unrelated pipeline architectures — everything else (why choose one, what tools support which) follows from that one distinction.

#### Q2. Why do most modern Azure projects default to ELT rather than ETL? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether the candidate understands the underlying economic shift, not just which acronym is "trendier."
**Answer:** Modern cloud warehouses (Synapse, Snowflake, Databricks SQL) have elastic, on-demand compute that can absorb heavy transformation workloads far more cheaply than maintaining a separate ETL processing server. ELT also keeps raw, untransformed data available alongside the transformed result, so if the cleaning logic needs to change later, the source data doesn't need to be re-extracted — only re-transformed from what's already landed. This is correct because it names the actual economic and operational drivers (elastic destination compute, raw data retention for iteration) rather than asserting ELT is simply "newer and better."

#### Q3. When would you still choose ETL over ELT today? **[Frequently Asked]**
*Why interviewers ask this:* Tests judgment — a good answer resists blanket "ELT always wins" tribalism, which is a common weak-answer trap.
**Answer:** Three real cases: **compliance/PII** — sensitive data must be masked or tokenized *before* it lands anywhere broadly accessible, which is a transform-before-load step required by law, sometimes called "EtLT"; **transfer economics** — when moving all raw data over a limited or expensive link (e.g. a slow on-prem-to-cloud connection) is prohibitively costly, filtering/reducing at the source before transfer makes sense; and cases where the destination genuinely lacks spare processing power. This is correct because it names concrete, still-current scenarios rather than treating ETL as purely a legacy pattern — a nuanced answer here signals real production experience.

#### Q4. Explain the medallion architecture (bronze/silver/gold) and what "contract" each layer represents. **[Frequently Asked]**
*Why interviewers ask this:* One of the most common lakehouse/ELT architecture questions across the industry.
**Answer:** **Bronze** holds data exactly as it arrived — untouched, immutable, source-native — with the contract that nothing is ever lost and reprocessing is always possible. **Silver** is typed, deduplicated, and conformed — the contract is one clean row per business fact, safe to build further logic on. **Gold** is aggregated and dimensionally modeled with business definitions applied — the contract is that the numbers match the business's actual definitions and are ready for BI. This is correct because it frames each layer as a specific, testable *quality promise* rather than just a folder-naming convention — which is the detail that matters, since consumers decide what they can safely build on based on which layer they're reading from.

#### Q5. Design an incremental load for a 2 TB orders table that updates constantly. **[Senior/Experienced]**
*Why interviewers ask this:* A realistic, high-value design question that tests whether the candidate can assemble the full incremental-loading toolbox correctly.
**Answer:** Use **log-based CDC** (reading the database's transaction log, e.g. via Debezium or native CDC) rather than a polling watermark, since CDC also captures deletes that a `modified_at` watermark would silently miss. Stream the change events into a **bronze** append-only layer, then apply them to silver via **MERGE** keyed on the business key, including a dedupe window to collapse multiple changes to the same row within a batch. The watermark or CDC offset must be committed **transactionally with the load itself** — committing it before the load risks data loss on crash, committing it after risks duplicates on retry. Late-arriving facts should `MERGE` into the appropriate (possibly older) partition rather than being dropped. This is correct because it assembles every piece of a genuinely production-grade incremental design — CDC over polling, transactional watermarking, dedupe, and late-data handling — rather than a single technique in isolation.

#### Q6. Your nightly pipeline failed 60% of the way through and the orchestrator automatically retried it. What determines whether the table ends up correct? **[Senior/Experienced]**
*Why interviewers ask this:* A very common scenario-based question testing idempotency, arguably the single most important production-pipeline property.
**Answer:** The pipeline must be **idempotent** — every step safe to re-run without duplicating or corrupting data. This means: `MERGE` by business key (or a scoped delete-then-reload for the specific batch/date, done atomically), rather than a blind append; and — critically — distinguishing **pipeline failure** (a transient issue where retrying is correct) from **data failure** (a bad input where retrying would just reprocess and duplicate the same bad data). Treating both cases identically as "just re-run it" is exactly how duplicate-day incidents happen in production. This is correct because it names both the structural fix (idempotent writes) and the operational judgment call (which failure type actually warrants a blind retry) that the scenario is testing.

#### Q7. What makes a data pipeline "production-grade" versus just "it ran successfully once"? **[Senior/Experienced]**
*Why interviewers ask this:* An open-ended maturity question, common in senior interviews, testing whether the candidate thinks beyond the happy path.
**Answer:** Idempotent steps (safe to re-run); automated data-quality gates that fail loudly or quarantine bad data rather than silently passing it downstream (schema tests, integrity tests, business-rule tests); lineage and state tracking (a control table recording exactly what loaded through when, not tribal knowledge); alerting tied to actual data contracts (not just "the job succeeded" — a job that copied zero rows and reported success is a data incident wearing a success icon); and a real backfill story (replaying historical dates safely, at controlled throttle). This is correct because it lists concrete, checkable properties rather than a vague "it's reliable" — each one is something a reviewer can actually verify in a design.

#### Q8. Where does a tool like dbt fit into the ETL/ELT picture? **[Senior/Experienced]**
*Why interviewers ask this:* Tests currency with the modern ELT tooling ecosystem, increasingly common as dbt adoption has grown.
**Answer:** dbt is the industrialized version of ELT's "T" — instead of hand-managed, ad-hoc transformation scripts, dbt lets teams write transformations as versioned SQL models in git, with built-in tests, documentation, and lineage tracking, running the actual transformation using the destination warehouse/lakehouse's own compute (true to the "T happens at the destination" definition of ELT). This is correct because it correctly places dbt as a tool that *implements* the ELT pattern rather than something separate from it — a common point of confusion for candidates who've heard the name without understanding where it sits architecturally.

---

## 2. Azure Data Factory

*(full notes: [02_Azure_Data_Factory.md](02_Azure_Data_Factory.md))*

#### Q9. What are the core building blocks of an Azure Data Factory pipeline? **[Frequently Asked]**
*Why interviewers ask this:* A baseline vocabulary question, almost guaranteed if ADF comes up at all.
**Answer:** A **pipeline** is the overall workflow — an ordered sequence of activities. An **activity** is a single step (e.g. "copy this file," "run this transformation"). A **dataset** points to a specific piece of data an activity reads or writes. A **linked service** holds the connection details for a source/destination (like a saved credential). A **trigger** starts the pipeline running — on a schedule, or in response to an event like a new file arriving. This is correct because it separates the five concepts cleanly by role — pipeline (orchestration), activity (a step), dataset (data), linked service (connection), trigger (start condition) — which is exactly how ADF itself models them.

#### Q10. What's the difference between Copy Activity and a Mapping Data Flow, and when would you use each? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether the candidate knows ADF isn't just a copy tool, and understands the trade-off between its two transformation approaches.
**Answer:** **Copy Activity** moves data from A to B with little or no transformation — fast, simple, parallelized, resumable, and the workhorse of most pipelines. **Mapping Data Flow** provides a visual way to define actual transformation logic (filtering, joins, aggregations) without writing Spark code directly, running the logic on a Spark cluster behind the scenes. The practical trade-off: Data Flows work well for simple derivations, but complex logic built purely in a GUI becomes difficult to test and review — which is why many enterprise teams use ADF for extraction/orchestration/loading and push non-trivial transformation logic to code-based tools (Databricks notebooks or dbt) instead. This is correct because it states both what each does *and* the practical limitation (testability of GUI-built complex logic) that drives real architectural decisions, not just a feature comparison.

#### Q11. Design an Azure Data Factory setup to incrementally load 500 source tables without building 500 separate pipelines. **[Senior/Experienced]**
*Why interviewers ask this:* A very common senior-level ADF design question testing whether the candidate knows the metadata-driven pattern.
**Answer:** Build a **control table** (source_table, watermark_column, target_path, is_active, etc.) and a single parameterized pipeline: a **Lookup** activity reads the control table, a **ForEach** activity iterates over the rows, and inside it a **Copy** activity uses a dynamically constructed query (`SELECT * FROM @{item().source_table} WHERE @{item().watermark_col} > '@{variables('wm')}'`) followed by a **Stored Procedure** activity that updates the watermark. Datasets and linked services are themselves parameterized ("any SQL table," "any lake folder") so the same objects serve every source. This is correct because it replaces 500 near-identical pipelines with roughly ten reusable objects, and — critically — adding a new source becomes an `INSERT` into the control table rather than a deployment, which is the actual operational win this pattern delivers.

#### Q12. How does Azure Data Factory securely connect to an on-premises SQL Server without opening any inbound firewall ports? **[Frequently Asked]**
*Why interviewers ask this:* A very common hybrid-connectivity question testing real understanding of the Self-Hosted Integration Runtime.
**Answer:** Through a **Self-Hosted Integration Runtime (SHIR)** — a lightweight agent installed *inside* the on-premises network that makes **outbound-only** connections to Azure, polling for work rather than requiring anything to reach in through the firewall. Credentials for the on-prem source are stored securely (in Key Vault, referenced by the linked service), and cloud-side connections use ADF's managed identity rather than stored secrets. This is correct because it identifies the specific mechanism (the SHIR dials out, so no inbound rule is ever needed) that makes the "no open firewall ports" requirement possible, rather than a vague "ADF connects securely."

#### Q13. Why would a company use both ADF and Databricks together instead of picking just one tool? **[Senior/Experienced]**
*Why interviewers ask this:* Tests architectural placement judgment — a common "why not just use one tool" trap question.
**Answer:** ADF has best-in-class managed connectors and hybrid movement capability (including the SHIR for on-prem sources) but comparatively weak transformation tooling; Databricks has no equivalent for reaching on-prem sources but excellent code-based transformation and Spark compute. The common enterprise pattern is **ADF triggering Databricks**: ADF owns extraction, orchestration, and scheduling, while Databricks owns the actual transformation logic as tested, reviewable code. Choosing just one tool for everything usually means accepting its weakest capability for some part of the job. This is correct because it names the specific complementary strengths (connectors/hybrid movement vs. transformation compute) rather than treating the combination as arbitrary convention.

#### Q14. An ADF pipeline shows a green "succeeded" status, but the downstream Power BI dashboard is showing stale data. Where do you look? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic troubleshooting scenario that tests whether the candidate knows "green" doesn't mean "correct" in orchestration tools.
**Answer:** A run can succeed while doing nothing useful — check whether the **trigger actually fired** (vs. simply not running that day), whether the **Copy Activity's rows-copied metric** is genuinely nonzero (a copy that moved 0 rows still reports success), and whether a **downstream activity was silently skipped** due to a dependency condition evaluating differently than expected. This is exactly why production pipelines should alert on absence ("the nightly load hasn't succeeded by 6am") and track rows-copied against an expected range in a control table, not just watch for green checkmarks. This is correct because it identifies the specific failure mode (a "successful" run that did nothing) and the concrete metrics that would actually catch it, which is what separates monitoring *runs* from monitoring *outcomes*.

#### Q15. What belongs in a proper CI/CD setup for Azure Data Factory, beyond just clicking "Publish" in the portal? **[Senior/Experienced]**
*Why interviewers ask this:* Tests production maturity — the portal's default workflow doesn't scale past one developer, and interviewers want to know if the candidate has operated ADF at team scale.
**Answer:** A git-integrated ADF workspace with feature branches and pull-request review of the pipeline JSON; ARM/Bicep export (or direct JSON deployment) promoted through dev → test → prod with per-environment parameter files (different linked service endpoints, Key Vault names per environment); **all secrets stored in Key Vault**, referenced by linked services, with ADF's managed identity granted narrowly scoped access — never connection strings pasted directly into linked service configuration; and enforced naming/folder conventions from day one, since an unorganized 400-pipeline factory becomes unmaintainable archaeology. This is correct because it lists the concrete practices (git-backed review, environment promotion, Key Vault + managed identity, naming discipline) that separate a real production ADF setup from a single-developer portal workflow.

#### Q16. A ForEach activity iterating over 500 source tables is accidentally overwhelming a source database. What went wrong, and how do you fix it? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic operational gotcha, testing whether the candidate understands ADF's default parallelism behavior.
**Answer:** ADF's `ForEach` activity runs its iterations in parallel by default, so 500 iterations each opening a connection to the same source database can behave like an accidental denial-of-service against it. The fix is deliberately setting the **batch count** (the ForEach's parallelism/degree-of-concurrency setting) to a value the source can actually sustain, rather than leaving it at the default. This is correct because it names the specific default behavior (parallel-by-default ForEach) that causes the problem, and the specific configuration (batch count) that fixes it — a concrete diagnosis rather than "add throttling."

---

## Rapid-Fire Round

- Q: ETL vs ELT — what's the one actual difference between them? — A: Where the Transform step happens — before loading (ETL) or after (ELT).
- Q: Why do most modern cloud projects default to ELT? — A: Elastic destination compute + raw data retention for iterating on transform logic later.
- Q: When would you still choose ETL today? — A: PII/compliance masking before broad-access storage, or reducing data before an expensive/limited transfer link.
- Q: Name the three medallion layers in order. — A: Bronze, Silver, Gold.
- Q: What does log-based CDC catch that a `modified_at` watermark misses? — A: Deletes.
- Q: What must be true about a load for a retry to be safe? — A: It must be idempotent.
- Q: What are ADF's five core building blocks? — A: Pipeline, Activity, Dataset, Linked Service, Trigger.
- Q: Copy Activity or Mapping Data Flow — which runs on a Spark cluster behind the scenes? — A: Mapping Data Flow.
- Q: What lets ADF reach an on-prem database with no inbound firewall rule? — A: A Self-Hosted Integration Runtime (SHIR), which connects outbound only.
- Q: What's the metadata-driven alternative to building 500 near-identical ADF pipelines? — A: One parameterized pipeline driven by a control table (Lookup → ForEach → Copy).
- Q: Where should ADF pipeline secrets be stored? — A: Azure Key Vault, referenced by linked services — never hardcoded.
- Q: Why is "the pipeline shows green" not sufficient monitoring? — A: A run can succeed while copying zero rows or skipping a downstream step silently.
- Q: What ADF ForEach setting prevents accidentally overwhelming a source database? — A: The batch count (parallelism) setting.
- Q: Where does dbt fit in ETL/ELT? — A: It's the industrialized "T" of ELT — versioned, tested SQL transformation models running on the destination's own compute.

Back to the folder: [05_ETL_ELT notes](.) · Related: [04_Data_Storage Interview Q&A](../../04_Storage_and_Formats/Data_Storage/Interview_Questions_and_Answers.md)

---

## Further Learning — Docs & Videos

**Documentation**
- ETL/ELT concepts (Databricks): https://www.databricks.com/glossary/elt
- ADF documentation: https://learn.microsoft.com/en-us/azure/data-factory/

**Videos**
- ETL/ELT & ADF interview questions: https://www.youtube.com/results?search_query=etl+elt+azure+data+factory+interview+questions
