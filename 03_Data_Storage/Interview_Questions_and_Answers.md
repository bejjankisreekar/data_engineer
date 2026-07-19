# 03_Data_Storage — Interview Questions & Answers

## How to use this file

This file pairs with the three notes in this folder and drills the material the way an interviewer actually asks about it. Questions come in two flavors, often mixed within the same section:

- **THEORY** — definitions, comparisons, and "explain X" questions (e.g. "Blob vs ADLS Gen2?"). These check whether you understand the concept, not just the buzzword.
- **PRACTICAL / SCENARIO** — "design this," "a client says X, what do you check," "walk me through securing Y" questions. These check whether you can *apply* the concept under the ambiguity of a real project — the kind senior candidates get asked once the interviewer is satisfied on theory.

Every question also explains *why* an interviewer asks it, not just what to answer — the reasoning behind a question is often what the interviewer is actually listening for.

Two difficulty tags are used, roughly matching the Basics/Advanced/Pro structure of the source notes:

- **[Frequently Asked]** — core concepts almost every data engineering interview touches: Blob vs ADLS, hierarchical namespace, access tiers, medallion architecture, lake vs warehouse vs database.
- **[Senior/Experienced]** — deeper, Pro-level questions: redundancy and RPO/RTO trade-offs, RBAC + ACL layering, lifecycle traps, the lakehouse pattern, migration realities. Expect these once you claim 3+ years of experience.

Untagged questions sit in between — solid mid-level material everyone should be able to answer.

---

## Table of Contents

1. [Data Lake vs Data Warehouse vs Database](#1-data-lake-vs-data-warehouse-vs-database)
2. [Azure Blob Storage](#2-azure-blob-storage)
3. [Azure Data Lake Storage (ADLS Gen2)](#3-azure-data-lake-storage-adls-gen2)
4. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. Data Lake vs Data Warehouse vs Database

*(full notes: [01_Data_Lake_vs_Warehouse_vs_Database.md](01_Data_Lake_vs_Warehouse_vs_Database.md))*

#### Q1. What's the fundamental difference between a database, a data lake, and a data warehouse? **[Frequently Asked]**
*Why interviewers ask this:* It's the single most common opener in a data-storage interview — it separates candidates who've memorized product names from those who understand the underlying problem each pattern solves.
**Answer:** A **database** stores current, structured, transactional data and is optimized for fast, small reads/writes (OLTP) — think a checkout till recording "this customer bought these items right now." A **data lake** stores data of any shape (structured, semi-structured, unstructured) in its raw, as-arrived form, optimized for cheap storage at scale — the loading dock where every delivery is dropped off unsorted. A **data warehouse** stores cleaned, structured, business-modeled data optimized for fast analytical queries (OLAP) — the store shelves an analyst shops from. They are usually used together: applications write to databases, raw exports land in the lake, and only the data worth analyzing gets transformed into the warehouse. This is correct because each pattern trades off differently on data shape, freshness, and query speed — no single system is good at all three simultaneously.

#### Q2. When would you choose a data lake over a data warehouse for a given workload? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether you can map a real requirement to the right storage pattern instead of defaulting to "warehouse for everything" or "lake for everything."
**Answer:** Choose the lake when you need to "keep everything and decide later" — logs, images, ML training corpora, raw API dumps, or any data whose shape or use case isn't fully known yet — because the lake accepts any format cheaply with no upfront schema design. Choose the warehouse (or a lakehouse gold layer) when the workload is governed BI dashboards, finance reporting, or high-concurrency small analytical queries where speed and structure matter more than flexibility. The anti-patterns are instructive too: a warehouse used as a raw file dump causes a cost explosion, and a lake with no contracts or owners becomes a "data swamp." The reasoning is correct because it optimizes for what each engine is actually built for — flexible cheap storage vs. governed, query-optimized structure — rather than forcing one tool to do both jobs.

#### Q3. Walk me through how data actually moves from an OLTP database to a BI dashboard.
*Why interviewers ask this:* Checks whether you understand the full pipeline, not just the endpoints — this is effectively "describe a modern data platform" in one answer.
**Answer:** Change Data Capture (CDC) reads the database's transaction log and streams inserts/updates/deletes out — log-based, not repeated polling queries (see [SQL Database](../01_SQL/02_SQL_Database.md)). That stream lands as raw files in the data lake's bronze layer, exactly as captured. An ELT pipeline then transforms it in place: bronze (raw) → silver (typed, deduplicated, conformed) → gold (aggregated, business-modeled) — the medallion architecture (see [ETL vs ELT](../04_ETL_ELT/01_ETL_vs_ELT.md)). Gold feeds a semantic layer or BI tool like Power BI. A less obvious arrow completes the loop: **reverse ETL** pushes gold aggregates back into operational systems, e.g. enriching a CRM with a customer's lifetime-value score. Every hop should be idempotent so re-runs don't duplicate data. This is correct because it names the actual mechanisms (CDC, ELT, medallion, reverse ETL) rather than a vague "data flows from source to dashboard" hand-wave, which is what separates a working answer from a memorized diagram.

#### Q4. What is a lakehouse, and why did it emerge? **[Senior/Experienced]**
*Why interviewers ask this:* Standard senior-level question — checks whether you understand the architectural problem the lakehouse solves, not just that it's a trendy term.
**Answer:** Running a lake and a warehouse side by side means keeping two copies of the same data in sync — a pipeline forever "syncing the truth," with duplication cost and reconciliation risk. The lakehouse collapses the two: cheap object storage, holding open file formats (Parquet), plus a **table format** (Delta or Iceberg) that adds ACID transactions, schema enforcement, and time travel, plus a SQL engine and catalog on top (Databricks SQL, Microsoft Fabric). The result is warehouse-grade behavior at lake-storage economics — one copy of data serving BI, Spark engineering, streaming, and ML from the same physical table. It's correct because it doesn't discard warehouse discipline (dimensional modeling, quality gates, governance still matter) — it only merges the storage engine, which is the actual bottleneck the pattern fixes.

#### Q5. Your client's BI team and Spark engineering team maintain two separate copies of the same customer data — one in the warehouse, one in the lake. How would you consolidate this? **[Senior/Experienced]**
*Why interviewers ask this:* A real consulting scenario — tests whether you can apply the lakehouse concept as an actual recommendation with a rollout plan, not just recite the definition.
**Answer:** First quantify the duplication tax: every extra copy is storage cost + a sync pipeline + reconciliation work + "which number is right?" meetings — that's usually the business case for change. Then propose moving to a lakehouse pattern on the *existing* lake storage: put a table format (Delta/Iceberg) over the data already in ADLS, govern it through a catalog (e.g. Unity Catalog) so both Spark and a SQL warehouse endpoint read the same physical table under one set of permissions. Migrate by workload, not everything at once — new bronze/silver pipelines move first, BI marts move last, and both paths run in parallel with reconciliation until trust transfers to the single copy. This is correct because it treats consolidation as an incremental, measurable migration rather than a risky big-bang cutover, and it targets the actual cost driver (copies and pipelines), not just "add a lakehouse."

#### Q6. What turns a data lake into a "data swamp," and how do you prevent it? **[Frequently Asked]**
*Why interviewers ask this:* A very common follow-up once a candidate praises the lake's "store first, decide later" flexibility — it checks whether you know that flexibility has a failure mode.
**Answer:** A swamp is a lake with no contracts, no catalog, and no owners — files land with no ownership metadata (source system, ingest date, schema version), so nobody can tell what's safe to query, what's stale, or who's responsible when it breaks. It's prevented by table formats (Delta/Iceberg give schema enforcement and versioning instead of "just files"), zone layering with quality gates (bronze/silver/gold, each a contract boundary), and a governed catalog that tracks ownership and lineage. "We'll clean it later" without documenting the raw data is exactly how a swamp starts. This is correct because a lake's core strength — accepting anything with no upfront structure — is also its risk; discipline and tooling are what keep flexibility from becoming chaos.

#### Q7. How would you plan a migration from a legacy data warehouse to a lakehouse architecture? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real project experience — migrations are where most of the risk (and most interview stories) actually live, far more than greenfield design.
**Answer:** Move *workloads*, not everything at once: build new bronze/silver pipelines on the lakehouse first, since they're lower risk and don't touch reporting; migrate BI marts last, once the platform is proven. Run the old and new paths in parallel with reconciliation until trust transfers to the new numbers — never cut BI over on day one. For database-fed pipelines, start the offload with read-replicas and CDC, never a big-bang extract, and resist the urge to replicate the OLTP schema as-is — the operational schema is not the analytics model; build toward a proper star schema (see [SQL Warehouse](../01_SQL/13_SQL_Warehouse.md)). This is correct because migrations fail most often from doing too much at once and skipping reconciliation, not from picking the wrong target architecture.

#### Q8. Two dashboards report different revenue numbers for the same day — one from the warehouse, one from a Databricks notebook. What's going on, and how do you fix it? **[Senior/Experienced]**
*Why interviewers ask this:* A classic "field-tested gotcha" scenario — checks whether you've actually operated a mixed lake/warehouse estate rather than just designed one on a whiteboard.
**Answer:** The same metric computed independently in two engines drifts — different timezone handling, different null-handling rules, and different floating-point summation order are the usual suspects, even against "the same" underlying data. Reconciling the two numbers after the fact is a losing game long-term. The fix is a single-definition **semantic layer**: one place where "revenue" is defined once (the calculation, the filters, the grain) and every tool — warehouse SQL and lakehouse Spark alike — reads that definition rather than reimplementing it. Enforcing gold/serving layers as a contract boundary (BI tools should never point at silver "temporarily") also prevents drift from creeping in upstream. This is correct because it treats the root cause (duplicated logic across engines) instead of chasing each discrepancy manually, which never scales past the first few dashboards.

#### Q9. When is a classic data warehouse still the right call over a lakehouse? **[Frequently Asked]**
*Why interviewers ask this:* Checks that you're not a one-pattern zealot — good architects know when *not* to adopt the newer pattern.
**Answer:** When the organization is SQL-only with a mature, stable BI estate, has high-concurrency small analytical queries, and has no real ML or streaming pressure pushing it toward native file access — in that case the migration cost of moving to a lakehouse exceeds the cost of the duplication it would remove. Lake-first companies that think they need "a warehouse" often actually need governance and modeling discipline applied to the lake they already have, not a second platform. This is correct because architecture decisions should be driven by workload fit and total cost, not by chasing the newer pattern for its own sake.

---

## 2. Azure Blob Storage

*(full notes: [02_Azure_Blob_Storage.md](02_Azure_Blob_Storage.md))*

#### Q10. What is Azure Blob Storage, and what problem does it solve compared to a traditional file server? **[Frequently Asked]**
*Why interviewers ask this:* A warm-up question to confirm baseline cloud-storage literacy before going deeper.
**Answer:** Blob Storage is Microsoft's general-purpose cloud storage for files ("blob" = Binary Large OBject) — an endlessly expandable filing cabinet organized as storage account → container → blob. Compared to a self-managed file server, it offers scale (kilobytes to petabytes with no hardware to buy), durability (Azure automatically replicates data across hardware, optionally across regions), accessibility (reachable over the internet by any authorized caller, no server to stand up), and pay-as-you-go pricing (pay for what you store and access, not fixed capacity). This is correct because it directly maps each Blob Storage property to the operational burden it removes from running physical storage yourself.

#### Q11. Explain the Hot, Cool, and Archive access tiers, and how you'd decide which to use for a given dataset.
*Why interviewers ask this:* Tests whether you understand tiering as a cost-vs-latency trade-off, not just three arbitrary labels.
**Answer:** The tiers trade storage cost against access cost and latency: **Hot** is for frequently accessed data (cheapest to read, most expensive to store — "papers on your desk"); **Cool** is for data accessed every few weeks or months (cheaper to store, costs more per read — "papers in a nearby drawer"); **Archive** is for data rarely accessed but kept for compliance or history (cheapest to store, slow and costly to retrieve — "boxes in long-term storage"). A real example: an insurance company keeps active claims in Hot while they're being processed, then moves settled claims to Archive once regulations require years of retention but nobody expects to reopen them. The decision comes down to modeling *actual* access patterns before picking a tier, since a "cost-saving" archive that's scanned monthly ends up costing more than Hot due to per-GB read and rehydration charges. This is correct because tiering is fundamentally a bet on future access frequency, and getting that bet wrong inverts the expected savings.

#### Q12. Walk through LRS vs ZRS vs GRS vs RA-GRS — how do you choose the right redundancy option for a workload? **[Senior/Experienced]**
*Why interviewers ask this:* A staple Pro-level question — checks whether you can reason about blast radius and cost together instead of defaulting to "always pick the most redundant option."
**Answer:**

| Option | Copies | Survives | Rough cost |
|---|---|---|---|
| LRS | 3 in one datacenter | Disk/rack failure | baseline |
| ZRS | 3 across availability zones | Datacenter/zone loss | ~1.25x |
| GRS / GZRS | +3 async-copied to paired region | Regional disaster | ~2x |
| RA-GRS / RA-GZRS | + read access to the secondary | Region loss, with read continuity | ~2x |

The choice is per data class, not per account: rebuildable derived data (silver/gold tables you can regenerate from bronze and code) can sit on LRS or ZRS, since re-derivation is cheaper than paying for geo-replication. Irreplaceable source data — the one copy you can never regenerate — justifies ZRS+GRS with a rehearsed failover process. Geo-replication is asynchronous, so regional failover can still lose the last few minutes of writes (RPO > 0) — failover is something you initiate and rehearse, not an automatic guarantee. This is correct because redundancy spend should track what's actually irreplaceable, not be applied uniformly regardless of whether the data can be rebuilt.

#### Q13. Why can't you edit a blob in place, and why does this matter for formats like Parquet and Delta? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether you understand the object-storage contract deeply enough to explain *why* modern table formats are built the way they are, rather than just naming them.
**Answer:** Object storage's contract is immutable-per-write: there's no in-place edit and no append to a block blob — a "rename" is really a copy-then-delete under the hood. This is exactly why [Parquet files are immutable](../02_File_formats/05_Parquet.md) and why table formats like Delta do versioned-file commits (write new files, then atomically update a transaction log pointing at them) instead of trying to update bytes within a file. Consistency is strong (read-after-write), which is what makes this pattern safe — a reader never sees a half-written file. This is correct because it traces the design of the entire modern lakehouse stack back to a single low-level fact about how object storage behaves, which is the kind of reasoning interviewers are checking for at this level.

#### Q14. A client says their Blob Storage costs tripled last quarter with no obvious change in usage. What do you check? **[Senior/Experienced]**
*Why interviewers ask this:* A very realistic scenario question — cost surprises are one of the most common real-world storage incidents, and this checks whether you know where the money actually goes.
**Answer:** Check, in order: (1) **transaction costs** — millions of small writes or reads (often from small files) bill per-operation, not per-GB, and this is the classic silent cost driver; (2) **tier-read and early-deletion charges** — data moved to Cool/Archive to save money but then read or deleted early incurs per-GB retrieval fees and early-deletion penalties that can exceed the storage savings; (3) **rehydration** — anything pulled back out of Archive costs real money and takes hours; (4) **egress** — cross-region reads (e.g. compute in a different region than storage) add per-GB transfer fees; (5) **versioning/soft-delete bloat** — on churn-heavy paths like streaming checkpoints or Delta logs, blob versioning silently multiplies stored bytes if scoped too broadly. Per-container inventory reports and cost tags are how you'd actually locate the culprit rather than guessing. This is correct because Blob Storage pricing has several dimensions beyond "GB stored," and a tripled bill almost always traces to one of these operational costs rather than genuine data growth.

#### Q15. How should a Databricks or Azure Data Factory pipeline authenticate to Blob Storage in production? **[Frequently Asked]**
*Why interviewers ask this:* Security-hygiene basics that come up in almost every cloud data engineering interview — checks that you don't default to "put a key in the config."
**Answer:** Ranked best to last-resort: (1) **Entra ID + RBAC roles** (e.g. `Storage Blob Data Reader/Contributor`) granted to the pipeline's **managed identity** — no secret to leak, since the identity is the service itself; (2) **user-delegation SAS** — a time-boxed, scoped link backed by Entra, useful for external sharing; (3) account SAS/keys — legacy, should be rotated and vaulted with a plan to retire them, never hardcoded or pasted into notebook cells (SAS tokens in git history are effectively leaked credentials). Public blob access should be disabled at the account level from day one, since a public container is one of the most common cloud data-breach causes. This is correct because managed identity removes the entire class of "credential got leaked" incidents by eliminating the credential a human or script needs to handle.

#### Q16. Design a lifecycle policy for a folder of raw log files: move to Cool after 30 days, Archive after 180 days, delete after 7 years.
*Why interviewers ask this:* A practical, hands-on question to check you can translate a retention requirement directly into a working Azure lifecycle rule, not just describe the concept in the abstract.
**Answer:**

```json
{ "rules": [{ "name": "age-out-raw", "type": "Lifecycle",
  "definition": { "filters": { "prefixMatch": ["raw/"] },
    "actions": { "baseBlob": {
      "tierToCool":    { "daysAfterModificationGreaterThan": 30 },
      "tierToArchive": { "daysAfterModificationGreaterThan": 180 },
      "delete":        { "daysAfterModificationGreaterThan": 2555 } } } } }] }
```

The rule targets the `raw/` prefix and lets policy — not a person — move blobs through tiers automatically based on days since last modification (2555 days ≈ 7 years). Before deploying this, confirm nothing under `raw/` is actively queried on a recurring basis (e.g. streaming checkpoints or files a pipeline still reads), since anything tiered to Archive that's needed on demand incurs hours of rehydration latency and extra fees — model access patterns first, then automate. This is correct because it encodes the retention requirement as declarative, auditable policy rather than a manual or script-driven process that someone has to remember to run.

#### Q17. What's the difference between soft delete, blob versioning, and immutability (WORM) policies? **[Senior/Experienced]**
*Why interviewers ask this:* Checks whether you know the "oops" safety net options exist and, more importantly, what each one is actually for — conflating them is a common mistake.
**Answer:** **Soft delete** (at blob and container level) is a recycle bin with a retention window — the baseline protection to enable everywhere, since it's cheap insurance against accidental deletes. **Blob versioning** keeps the prior version on every overwrite, protecting against bad pipeline overwrites — but on churn-heavy paths like streaming checkpoints or Delta transaction logs, version bloat quietly multiplies storage cost, so it should be scoped deliberately rather than turned on globally. **Immutability policies (WORM — write once, read many)** are time-locked or legal-hold protections where *nobody*, including admins, can delete or modify data until the lock expires — the tool for regulatory/audit zones, not general-purpose protection. None of these substitute for cross-account backup on truly critical data, since an attacker or script with sufficient permissions can still purge within a single account — separating accounts or subscriptions is the last line of defense. This is correct because each mechanism protects against a different failure mode (accidental delete, accidental overwrite, malicious/compliance-mandated deletion), and picking the wrong one leaves a real gap.

---

## 3. Azure Data Lake Storage (ADLS Gen2)

*(full notes: [03_Azure_Data_Lake_Storage.md](03_Azure_Data_Lake_Storage.md))*

#### Q18. What is ADLS Gen2, and how is it different from plain Blob Storage? **[Frequently Asked]**
*Why interviewers ask this:* Probably the single most asked question in this entire file — it's the fastest way to check whether a candidate actually understands the relationship between the two services rather than treating them as unrelated products.
**Answer:** ADLS Gen2 is not a separate product — it's [Azure Blob Storage](02_Azure_Blob_Storage.md) with a "big data" mode switched on. Enabling **hierarchical namespace (HNS)** on a storage account adds true nested folders (instead of Blob's flatter container structure), fine-grained folder/file-level permissions, and an analytics-tuned driver (`abfss://`) used by Spark, Databricks, and Synapse. If Blob Storage is a general-purpose filing cabinet, ADLS is that same cabinet with labeled folder dividers and a sign-in sheet controlling exactly who opens which drawer. This is correct because understanding ADLS as "Blob + HNS," not as a competing service, is what lets you reason correctly about every other ADLS question — cost, security, and performance all inherit from the underlying Blob Storage contract.

#### Q19. What is hierarchical namespace, and why does it matter beyond "nicer folders"? **[Frequently Asked]**
*Why interviewers ask this:* Distinguishes candidates who've only read a marketing description of ADLS from those who understand the actual engineering consequence.
**Answer:** In flat blob storage, `folder/file.parquet` is a naming illusion — there's no real folder object, so "renaming a folder" of 100,000 files means 100,000 individual copy+delete operations, and a crash mid-way leaves half-renamed chaos. With HNS enabled, directories are real objects, so rename/move/delete of a directory is a single **atomic metadata operation**. This is exactly what Spark's job-commit protocols rely on: writing to a `_temporary/` directory and atomically moving it into place on success — faster and safer commits than flat storage could ever provide. HNS also makes POSIX-style ACLs possible, since there's now a real directory to attach permissions to. The cost of admission: HNS is set at account creation and isn't casually reversible, and a handful of Blob features lag behind on HNS accounts. This is correct because the "atomic directory operation" property isn't a convenience feature — it's the mechanism that makes safe, concurrent, crash-resistant writes possible at all in a lake.

#### Q20. Explain the medallion architecture (bronze/silver/gold) — what happens at each layer? **[Frequently Asked]**
*Why interviewers ask this:* One of the most universally asked lake-architecture questions — almost every data engineering interview touches this, since it's the default organizing pattern for lakes and lakehouses alike.
**Answer:** **Bronze** holds data exactly as it arrived — untouched CSV, JSON, logs, no transformation, immutable and source-native. **Silver** removes duplicate/bad records and corrects types — cleaned but not yet business-modeled. **Gold** is aggregated, business-ready data shaped for reporting. A telecom example: call-detail records land in bronze exactly as network equipment produced them; a nightly pipeline cleans obviously broken records into silver, then aggregates call volume and duration by region and hour into gold; analysts and dashboards only ever query gold, never touching the messy raw data directly. This is correct because each layer represents a genuine trust and quality boundary, not just a folder-naming convention — consumers downstream can rely on gold's guarantees without knowing anything about how bronze was produced.

#### Q21. Design the folder and security layout for a multi-team lake where finance and HR need isolated access, and the platform team needs broad oversight. **[Senior/Experienced]**
*Why interviewers ask this:* A hands-on design question that combines zone layout, ACLs, and RBAC into one scenario — exactly the kind of question that separates candidates who've operated a real multi-team lake from those who've only read about ADLS.
**Answer:** Use separate **containers per medallion zone** (bronze/silver/gold/landing) so each zone has its own clean ACL and lifecycle boundary, then organize by domain within each: `abfss://silver@lake.../finance/`, `abfss://silver@lake.../hr/`, etc. — an example reference layout:

```
abfss://bronze@lake.../  source_system/dataset/ingest_date=2026-07-19/...
abfss://silver@lake.../  domain/entity/            (finance/, hr/, ...)
abfss://gold@lake.../    domain/mart/
```

Set **default ACLs** on each domain directory (e.g. `finance/`) before any data lands, granting read/write to Entra ID **groups** (never individual users) — `finance-readers`, `finance-writers` — so ACLs apply automatically to everything written afterward instead of requiring a recursive re-ACL job later. Layer broad **RBAC** roles on top for platform-wide concerns: an engineering service principal gets `Storage Blob Data Contributor` at the account or container level for pipeline operations, while day-to-day analyst access is scoped through the finer-grained ACLs. Remember RBAC Contributor roles bypass ACL checks entirely, so scope them narrowly — a platform-wide Contributor role silently defeats the folder-level isolation you just built. This is correct because it establishes isolation *before* data lands (avoiding a retroactive ACL fix) and uses each access-control layer for what it's actually good at — RBAC for broad platform roles, ACLs for fine per-team partitions.

#### Q22. Walk through how you'd secure a folder so only the finance team can read it. **[Senior/Experienced]**
*Why interviewers ask this:* The classic "make it concrete" follow-up to any ADLS security discussion — checks whether you can execute the RBAC/ACL layering in practice, step by step.
**Answer:** First, confirm the finance data lives under its own directory, e.g. `abfss://silver@lake.../finance/`, ideally decided before data first lands there. Create (or use) an Entra ID group, `finance-readers`, containing the individuals and service principals that need access — never grant to individual users directly, per standard DCL principle (see [SQL DCL and TCL](../01_SQL/12_SQL_DCL_TCL.md)). Set a **default ACL** on the `finance/` directory granting that group read+execute, so the permission applies automatically to every file and subfolder created underneath it going forward — setting it only on existing files means anything written later is unprotected. Separately, check that no broad RBAC role (like `Storage Blob Data Contributor` at the account level) is granted to a group that shouldn't see finance data, since RBAC data-plane roles bypass ACL checks entirely and would silently override the folder-level restriction. Finally, verify with storage access logs that only `finance-readers` members are actually reading that path, since auditors will ask. This is correct because ACLs alone aren't sufficient if a broader RBAC grant exists that bypasses them — real security here requires checking both layers together, not just configuring one.

#### Q23. A client's ADLS-backed queries have gotten steadily slower over the last six months with no code changes. What do you check? **[Senior/Experienced]**
*Why interviewers ask this:* A very common "diagnose a degrading system" scenario — tests structured troubleshooting rather than a single guessed answer.
**Answer:** Work through the usual suspects in order: (1) **small-file accumulation** — if nobody's running `OPTIMIZE` regularly, file counts creep up and per-file open + transaction overhead dominates (target 100 MB-1 GB files); (2) **partition explosion** — over-granular partitioning (e.g. partitioning by minute instead of day) creates too many small partitions and directories; (3) **listing overhead growth** — millions-of-files directory listings throttle jobs, especially if the pipeline re-lists bronze on every run instead of using incremental discovery (e.g. Auto Loader file notifications); (4) **stats/clustering drift** — as data grows, Z-order/liquid-clustering benefits decay if maintenance jobs aren't re-run. All four are measurable (file-count and size metrics, partition counts, listing duration, query plans) and all are fixable operationally without a redesign. This is correct because "queries got slower" almost always traces to file/partition hygiene rather than a fundamental architecture problem, and checking the measurable symptoms first avoids an expensive premature redesign.

#### Q24. Why is renaming a directory cheap in ADLS Gen2 but expensive in plain Blob Storage? **[Frequently Asked]**
*Why interviewers ask this:* A concrete, technical version of the HNS question that interviewers use to check whether the candidate really understands the mechanism, not just the marketing line.
**Answer:** Plain Blob Storage has no real directory object — `folder/file` is just a naming convention within a flat container, so renaming a folder means copying every individual blob under the new name and deleting the old ones (N operations for N files), with no atomicity guarantee if it's interrupted partway. ADLS Gen2's hierarchical namespace makes directories real, addressable objects, so a rename or move is a single atomic metadata operation regardless of how many files sit underneath. This directly enables Spark's atomic commit protocol, which writes to a temporary directory and renames it into place on success — a pattern that's fast and crash-safe on ADLS but would be neither on flat blob storage. This is correct because it's the same underlying HNS mechanism (real directory objects, atomic metadata ops) driving both the folder-rename behavior and the reliability of analytics engines' commit protocols — they're not two separate facts.

#### Q25. What's the difference between a data lake being "just a filesystem" and a lakehouse being "a database on it"? **[Senior/Experienced]**
*Why interviewers ask this:* A Pro-level conceptual question that checks whether the candidate can articulate *why* raw ADLS alone isn't sufficient for production analytics — a common gap even among people who use lakes daily.
**Answer:** Storage itself doesn't know about tables — raw ADLS gives you folders of files with no transactions, no schema enforcement, and no discovery mechanism. Everything hard about operating a lake traces back to that one fact. The stack that fixes it: a table format like Delta adds a transaction log giving table semantics (ACID, schema enforcement, time travel — see [Why Spark? Why Databricks?](../06_PySpark/Why_Spark_Why_Databricks.md)); a catalog (e.g. Unity Catalog) adds names, permissions, and lineage; and zone layering (bronze/silver/gold) adds quality contracts between stages. A "data swamp" is precisely a lake run without those three things. When someone proposes "just drop files in the lake," the senior response is to ask: which table, which contract, which owner? This is correct because it reframes the lakehouse not as a new product but as the minimum set of guarantees that turns a raw filesystem into something safe to build production analytics on.

#### Q26. How do you handle a GDPR "right to erasure" request against an append-only bronze layer? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic compliance scenario that checks whether the candidate has thought through the tension between "immutable, append-only raw data" (a lake design principle) and legal deletion obligations — a genuine architectural conflict, not a trick question.
**Answer:** This has to be a designed capability decided *before* the first PII lands, not an afterthought. In a Delta-based bronze layer, deletion is handled through deletion vectors or targeted rewrites of the affected files (Delta supports row-level `DELETE` even though the underlying files are immutable-per-write — a new file version is committed that excludes the deleted rows), combined with lifecycle-based deletion for older raw files outside Delta. Decide up front which mechanism owns erasure for each dataset, and confirm it also cascades correctly through silver/gold if the same PII was propagated downstream. This is correct because "immutable raw data" and "must be erasable" aren't actually contradictory once you separate the physical immutability of individual file writes (an object-storage property) from the logical mutability a table format provides on top of them.

---

## Rapid-Fire Round

- Q: What does "blob" stand for? — A: Binary Large OBject.
- Q: What's the organizational unit inside a Blob Storage account, similar to a folder? — A: A container.
- Q: Which access tier has the fastest retrieval but the highest storage cost? — A: Hot.
- Q: Can Archive-tier data be queried instantly? — A: No — it must be rehydrated first, which takes hours and incurs extra fees.
- Q: What is ADLS Gen2 built on top of? — A: Azure Blob Storage, with hierarchical namespace (HNS) enabled.
- Q: What does HNS stand for, and what does it enable? — A: Hierarchical Namespace; true nested folders with atomic directory operations and POSIX ACLs.
- Q: What URI scheme do analytics engines use to read from ADLS Gen2? — A: `abfss://`
- Q: Name the three medallion layers in order. — A: Bronze, Silver, Gold.
- Q: Which medallion layer do BI dashboards typically query? — A: Gold.
- Q: RBAC or POSIX ACLs — which grants "finance group reads `/finance/`, nothing else"? — A: POSIX ACLs — fine-grained, directory-level.
- Q: Which redundancy option protects against a full region outage with read access to the secondary? — A: RA-GRS / RA-GZRS.
- Q: What does OLTP stand for, and what is it optimized for? — A: Online Transaction Processing; fast, small, frequent read/write operations.
- Q: What does OLAP stand for, and what is it optimized for? — A: Online Analytical Processing; large, complex queries over historical data.
- Q: What table format gives a data lake ACID transactions? — A: Delta Lake (or Iceberg).
- Q: What's the recommended target file size on ADLS/Delta to avoid the small-files problem? — A: Roughly 100 MB-1 GB.
