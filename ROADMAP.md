# Azure Data Engineer — Roadmap (Zero to Everything)

A single, ordered path from *"I've never written code"* to *"I can pass DP‑700 (Fabric) / Databricks Associate and clear a 5‑year Azure Data Engineer interview."*

This is the **map**. The actual lessons live in the [category folders](README.md); this file tells you **what to learn, in what order, why, and how to know you're ready**. Every ✅ topic already has notes in this repo — the link takes you straight there. Every 🔜 topic is on the roadmap but not yet written.

> **How to use this file:** Work top to bottom. Don't skip a phase because it "looks easy" — each one is a prerequisite for the next. At the end of every phase there's a **Milestone** (something you can *do*, not just *know*). If you can't hit the milestone, stay in the phase.

---

## What does an Azure Data Engineer actually do?

You build the **pipelines and storage** that move raw data from source systems into clean, trusted, query-ready form — so analysts, dashboards, and ML models can use it. Day to day that means:

- **Ingest** data from databases, files, APIs, and event streams.
- **Store** it cheaply and reliably (data lake / lakehouse).
- **Transform** it (clean, join, aggregate) with SQL and Spark.
- **Orchestrate** the whole thing on a schedule, with monitoring and alerts.
- **Govern** it — security, access, quality, lineage, cost.

The Azure toolset for that: **ADLS, Data Factory, Databricks, Synapse/Fabric, Event Hubs, Purview, Key Vault**, plus **SQL, Python, PySpark, and Git** as the underlying skills.

---

## The 9 phases at a glance

| Phase | Theme | You'll be able to… |
|---|---|---|
| **0** | Foundations & mindset | Explain OLTP vs OLAP, distributed computing, why big data exists |
| **1** | SQL | Write joins, aggregates, subqueries, window functions from scratch |
| **2** | Python | Write scripts, functions, file/error handling, basic pandas |
| **3** | Cloud & Azure basics | Understand IaaS/PaaS/SaaS, pass AZ‑900 |
| **4** | Storage & file formats | Choose Parquet vs CSV, use ADLS, reason about a data lake |
| **5** | Data modeling & warehousing | Design a star schema, handle SCDs, know Kimball vs Inmon |
| **6** | PySpark & the lakehouse | Transform big data with Spark, use Delta Lake & the medallion architecture |
| **7** | Data engineering in practice | Build ETL/ELT pipelines, CDC, streaming, quality, governance |
| **8** | DevOps, certs & interviews | Use Git/CI-CD, pass DP‑700 & Databricks Associate, clear interviews |

---

# Phase 0 — Foundations & Mindset

**Goal:** understand the *ideas* every tool is built on, before touching any tool.

- ✅ [OLTP Storage](01_Foundations/Fundamentals/01_OLTP_Storage.md) — row-based, transaction-first (apps)
- ✅ [OLAP Storage](01_Foundations/Fundamentals/02_OLAP_Storage.md) — column-based, analysis-first (warehouses)
- ✅ [Distributed Computing](01_Foundations/Fundamentals/03_Distributed_Computing.md) — scale out vs scale up
- ✅ [Master–Slave Architecture](01_Foundations/Fundamentals/04_Master_Slave_Architecture.md) — the coordinator/worker pattern
- ✅ [Hadoop Architecture](01_Foundations/Fundamentals/05_Hadoop_Architecture.md) — HDFS/YARN/MapReduce
- ✅ [Big Data Evolution Timeline](01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md) — DB → warehouse → Hadoop → Spark → lakehouse
- ✅ [Foundations Q&A](01_Foundations/Fundamentals/Interview_Questions_and_Answers.md)

**Milestone:** explain, out loud, *why* analytics workloads don't run on the OLTP database, and *why* one big computer eventually loses to a cluster of small ones.

---

# Phase 1 — SQL (the non-negotiable skill)

**Goal:** SQL is ~40% of most data-engineering interviews. You must be fluent, not familiar.

- ✅ [What is SQL](02_Databases/SQL/01_What_is_SQL.md) → [Database](02_Databases/SQL/02_SQL_Database.md) → [Data Types](02_Databases/SQL/03_SQL_Data_Types.md)
- ✅ [DDL](02_Databases/SQL/04_SQL_DDL.md) · [DML](02_Databases/SQL/05_SQL_DML.md) · [DQL](02_Databases/SQL/06_SQL_DQL.md)
- ✅ [Keys & Joins](02_Databases/SQL/07_SQL_Keys_and_Joins.md) — **master this**
- ✅ [Aggregates](02_Databases/SQL/08_SQL_Aggregate_Functions.md) · [Subqueries](02_Databases/SQL/09_SQL_Subqueries.md) · [Views](02_Databases/SQL/10_SQL_Views.md) · [Indexes](02_Databases/SQL/11_SQL_Indexes.md)
- ✅ [DCL & TCL](02_Databases/SQL/12_SQL_DCL_TCL.md) · [SQL Warehouse](02_Databases/SQL/13_SQL_Warehouse.md)
- ✅ [SQL Q&A](02_Databases/SQL/Interview_Questions_and_Answers.md) · [Practical Query Questions](02_Databases/SQL/Practical_SQL_Query_Interview_Questions.md)
- ✅ Interview extras: [Window Functions](Job%20Interviews/SQL/Window%20Functions.md) · [Query Optimization](Job%20Interviews/SQL/Query%20Optimization.md)

**Milestone:** given two tables, write — without help — a query using a JOIN, GROUP BY + HAVING, a subquery, and a window function (`ROW_NUMBER`/`RANK`).

---

# Phase 2 — Python (the glue language)

**Goal:** enough Python to script transformations and move into PySpark. You are **not** becoming a software engineer.

- ✅ [Python Learning Path](06_Programming/Python/00_Python_Learning_Path.md) — start here
- ✅ [Getting Started](06_Programming/Python/01_Getting_Started.md) → [Variables & Types](06_Programming/Python/02_Variables_and_Data_Types.md) → [Strings](06_Programming/Python/03_Strings.md)
- ✅ [Lists/Tuples/Sets](06_Programming/Python/04_Lists_Tuples_Sets.md) · [Dictionaries](06_Programming/Python/05_Dictionaries.md)
- ✅ [Conditionals & Loops](06_Programming/Python/06_Conditionals_and_Loops.md) · [Functions](06_Programming/Python/07_Functions.md) · [Comprehensions](06_Programming/Python/08_Comprehensions.md)
- ✅ [Files & Exceptions](06_Programming/Python/09_Files_and_Exceptions.md) · [Modules & venv](06_Programming/Python/10_Modules_and_Virtual_Environments.md)
- ✅ [Python for Data Engineering](06_Programming/Python/11_Python_for_Data_Engineering.md) — pandas + the bridge to Spark
- ✅ [Python Q&A](06_Programming/Python/Interview_Questions_and_Answers.md)

**Milestone:** write a script that reads a CSV, cleans a column, handles a bad row with `try/except`, and writes the result out — using a function and a comprehension.

---

# Phase 3 — Cloud & Azure Fundamentals

**Goal:** understand *where all of this runs*, and earn your first certification (AZ‑900) as an easy confidence win.

- ✅ [Public/Private/Hybrid Cloud](03_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md) · [IaaS/PaaS/SaaS](03_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md)
- ✅ [Cloud Concepts Q&A](03_Cloud/Cloud_Concepts/Interview_Questions_and_Answers.md)
- 🎓 **Certification:** [AZ‑900 track](Certifications/AZ_900/00_AZ900_Study_Guide_Overview.md) — 12 notes + mock exam

**Milestone:** pass the [AZ‑900 final mock exam](Certifications/AZ_900/12_Final_Mock_Exam.md) at 80%+.

---

# Phase 4 — Storage & File Formats

**Goal:** know where data physically lives and in what format — the foundation of every pipeline.

- ✅ [Data Lake vs Warehouse vs Database](04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)
- ✅ [Azure Blob Storage](04_Storage_and_Formats/Data_Storage/02_Azure_Blob_Storage.md) · [Azure Data Lake Storage (ADLS)](04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)
- ✅ File formats: [CSV](04_Storage_and_Formats/File_Formats/01_CSV.md) · [JSON](04_Storage_and_Formats/File_Formats/02_JSON.md) · [Avro](04_Storage_and_Formats/File_Formats/03_Avro.md) · [ORC](04_Storage_and_Formats/File_Formats/04_ORC.md) · [Parquet](04_Storage_and_Formats/File_Formats/05_Parquet.md) · [Comparison](04_Storage_and_Formats/File_Formats/06_File_Format_Comparison.md)
- ✅ **Lakehouse formats:** [Delta Lake](04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) · [Delta Table](04_Storage_and_Formats/Lakehouse/02_Delta_Table.md) · [Lakehouse Architecture](04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)
- ✅ Q&A: [Data Storage](04_Storage_and_Formats/Data_Storage/Interview_Questions_and_Answers.md) · [File Formats](04_Storage_and_Formats/File_Formats/Interview_Questions_and_Answers.md) · [Lakehouse](04_Storage_and_Formats/Lakehouse/Interview_Questions_and_Answers.md)

**Milestone:** explain why analytics uses Parquet over CSV, and what Delta Lake adds on top of Parquet (transaction log → ACID, updates, time travel).

---

# Phase 5 — Data Modeling & Warehousing

**Goal:** design *how* data is structured — the skill that separates a pipeline plumber from a data engineer.

- ✅ [Data Modeling Learning Path](02_Databases/Data_Modeling/00_Data_Modeling_Learning_Path.md)
- ✅ [Fundamentals](02_Databases/Data_Modeling/01_Data_Modeling_Fundamentals.md) · [Normalization](02_Databases/Data_Modeling/02_Normalization_and_Denormalization.md)
- ✅ [Dimensional Modeling](02_Databases/Data_Modeling/03_Dimensional_Modeling.md) — **star schema, facts, dimensions, grain**
- ✅ [Slowly Changing Dimensions](02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) — SCD types 0–6
- ✅ [Data Vault & Modern Modeling](02_Databases/Data_Modeling/05_Data_Vault_and_Modern_Modeling.md)
- ✅ Warehousing: [Fundamentals](02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md) · [Data Mart](02_Databases/Data_Warehousing/02_Data_Mart.md) · [Data Mesh](02_Databases/Data_Warehousing/03_Data_Mesh.md) · [Data Fabric](02_Databases/Data_Warehousing/04_Data_Fabric_and_Architecture_Comparison.md)
- ✅ [Data Modeling Q&A](02_Databases/Data_Modeling/Interview_Questions_and_Answers.md)

**Milestone:** given a business ("an online store"), design a star schema — name the fact table, its grain, and 3–4 dimensions, and explain how you'd handle a customer changing address (SCD2).

---

# Phase 6 — PySpark & the Lakehouse (the core engineering skill)

**Goal:** process data at scale. This is the heart of the modern Azure DE role (Databricks).

**Concept track — understand Spark before coding it:**
- ✅ [What is Apache Spark?](06_Programming/PySpark/What_Is_Apache_Spark.md) · [Spark Architecture](06_Programming/PySpark/Spark_Architecture.md) · [Spark Processing](06_Programming/PySpark/Spark_Processing.md) · [Why Spark? Why Databricks?](06_Programming/PySpark/Why_Spark_Why_Databricks.md)

**The platform track — Databricks (do this alongside the coding track):**
- ✅ [Databricks module (08)](08_Databricks/00_Databricks_Learning_Path.md) — [What is Databricks](08_Databricks/01_What_is_Databricks.md) · [Clusters](08_Databricks/02_Clusters_and_Compute.md) · [Notebooks/Jobs](08_Databricks/03_Notebooks_Repos_and_Jobs.md) · [Unity Catalog](08_Databricks/04_Unity_Catalog.md) · [DLT](08_Databricks/05_Delta_Live_Tables.md) · [Auto Loader](08_Databricks/06_Auto_Loader_and_Ingestion.md)

**Coding track — read 00→15 in order:**
- ✅ [00 Learning Path](06_Programming/PySpark/00_PySpark_Learning_Path.md) → [01 SparkSession](06_Programming/PySpark/01_Getting_Started_SparkSession.md) → [02 DataFrames](06_Programming/PySpark/02_DataFrame_Basics.md) → [03 Schemas](06_Programming/PySpark/03_Schemas_and_Data_Types.md)
- ✅ [04 Read/Write](06_Programming/PySpark/04_Reading_and_Writing_Data.md) · [05 Columns](06_Programming/PySpark/05_Column_Operations_and_Functions.md) · [06 Aggregations](06_Programming/PySpark/06_Aggregations_and_Grouping.md) · [07 Joins](06_Programming/PySpark/07_Joins.md) · [08 Windows](06_Programming/PySpark/08_Window_Functions.md)
- ✅ [09 Complex Types/JSON](06_Programming/PySpark/09_Complex_Types_and_JSON.md) · [10 UDFs](06_Programming/PySpark/10_UDFs_and_Pandas_Integration.md) · [11 Spark SQL](06_Programming/PySpark/11_Spark_SQL_and_Views.md)
- ✅ [12 Delta Lake with PySpark](06_Programming/PySpark/12_Delta_Lake_with_PySpark.md) — **MERGE, time travel, OPTIMIZE**
- ✅ [13 Structured Streaming](06_Programming/PySpark/13_Structured_Streaming.md) · [14 Performance](06_Programming/PySpark/14_Performance_and_Best_Practices.md) · [15 RDDs](06_Programming/PySpark/15_RDDs_The_Foundation.md)
- ✅ [PySpark Q&A (78 questions)](06_Programming/PySpark/Interview_Questions_and_Answers.md) — the largest set in the repo

**Tie it together:** [Lakehouse Architecture + Medallion (Bronze/Silver/Gold)](04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)

**Milestone:** write a PySpark job that reads raw files into Bronze, cleans/dedupes into Silver, aggregates into a Gold Delta table, and uses a `MERGE` to upsert. Explain a shuffle and how you'd fix a slow join.

---

# Phase 7 — Data Engineering in Practice

**Goal:** the actual job — moving, integrating, streaming, and trusting data.

- ✅ **ETL/ELT:** [ETL vs ELT](05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) · [Azure Data Factory](05_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) · [Data Pipelines](05_Data_Engineering/ETL_ELT/03_Data_Pipelines.md)
- ✅ **Integration:** [Fundamentals](05_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md) · [Patterns](05_Data_Engineering/Data_Integration/02_Integration_Patterns.md) · [Change Data Capture](05_Data_Engineering/Data_Integration/03_Change_Data_Capture.md) · [Azure Integration Services](05_Data_Engineering/Data_Integration/04_Azure_Integration_Services.md)
- ✅ **Governance & Security:** [Data Governance & Security](05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) — RBAC, Key Vault, Purview, Unity Catalog, GDPR
- ✅ **Quality:** [Data Quality Fundamentals](05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) — expectations, quarantine, observability
- ✅ Q&A: [ETL/ELT](05_Data_Engineering/ETL_ELT/Interview_Questions_and_Answers.md) · [Integration](05_Data_Engineering/Data_Integration/Interview_Questions_and_Answers.md) · [Governance](05_Data_Engineering/Data_Governance/Interview_Questions_and_Answers.md) · [Quality](05_Data_Engineering/Data_Quality/Interview_Questions_and_Answers.md)

- ✅ **Streaming:** [Streaming module (09)](09_Streaming/00_Streaming_Learning_Path.md) — [Fundamentals](09_Streaming/01_Streaming_Fundamentals.md) · [Event Hubs](09_Streaming/02_Azure_Event_Hubs.md) · [Kafka](09_Streaming/03_Apache_Kafka.md) · [Stream Analytics](09_Streaming/04_Azure_Stream_Analytics.md)

- ✅ **Synapse & Fabric:** [Synapse & Fabric module (10)](10_Synapse_and_Fabric/00_Learning_Path.md) — [Synapse](10_Synapse_and_Fabric/01_Azure_Synapse_Analytics.md) · [SQL pools/MPP](10_Synapse_and_Fabric/02_Dedicated_vs_Serverless_SQL_Pools.md) · [Fabric](10_Synapse_and_Fabric/03_Microsoft_Fabric.md) · [decision guide](10_Synapse_and_Fabric/04_Synapse_vs_Fabric_vs_Databricks.md)

- ✅ **Orchestration:** [Orchestration module (12)](12_Orchestration/00_Orchestration_Learning_Path.md) — DAGs, [ADF triggers](12_Orchestration/02_ADF_Orchestration.md), [Databricks Workflows](12_Orchestration/03_Databricks_Workflows.md), [Apache Airflow](12_Orchestration/04_Apache_Airflow.md)
- ✅ **Monitoring & Observability:** [Monitoring module (13)](13_Monitoring_and_Observability/00_Monitoring_Learning_Path.md) — [Azure Monitor/KQL](13_Monitoring_and_Observability/02_Azure_Monitor_and_Log_Analytics.md), [reliability](13_Monitoring_and_Observability/03_Pipeline_Reliability.md), [data observability](13_Monitoring_and_Observability/04_Data_Observability.md)
- ✅ **dbt:** [dbt module (14)](14_dbt/00_dbt_Learning_Path.md) — models, tests, docs, [snapshots/SCD2](14_dbt/04_Snapshots_Seeds_Macros.md), [dbt in Azure](14_dbt/05_dbt_in_Azure.md)
- ✅ **Testing & DataOps:** [Testing module (15)](15_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md) — [pipeline testing](15_Testing_and_DataOps/01_Testing_Data_Pipelines.md), [data quality tests](15_Testing_and_DataOps/02_Data_Quality_Testing.md), [data contracts](15_Testing_and_DataOps/03_Data_Contracts.md), [CI/CD for data](15_Testing_and_DataOps/04_DataOps_and_CICD_for_Data.md)
- ✅ **Cost & Performance:** [Cost module (16)](16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md) — [FinOps](16_Cost_and_Performance/01_Cost_Fundamentals_FinOps.md), [Databricks cost](16_Cost_and_Performance/02_Databricks_Cost_Optimization.md), [performance tuning](16_Cost_and_Performance/04_Performance_Optimization.md)
- ✅ **Power BI for engineers:** [Power BI module (17)](17_Power_BI_for_Engineers/00_Power_BI_Learning_Path.md) — semantic models, [star schema](17_Power_BI_for_Engineers/02_Semantic_Model_and_Star_Schema.md), DAX, [Direct Lake serving](17_Power_BI_for_Engineers/04_Serving_from_the_Lakehouse.md)

**Milestone:** whiteboard an end-to-end pipeline for a real scenario ("ingest daily sales files + a live order stream, serve a finance dashboard") naming the Azure service at each hop and where you'd put quality checks and governance. Then **build it** — see the [Projects module (11)](11_Projects/00_Projects_Learning_Path.md).

---

# Phase 8 — DevOps, Certifications & Interviews

**Goal:** work like a professional and prove it on paper and in the room.

**DevOps / Git:**
- ✅ [Git & GitHub track (00→10)](07_DevOps/Git_GitHub/00_Git_GitHub_Learning_Path.md) — version control, branching, remotes, [CI/CD](07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md), troubleshooting

**Certifications (recommended order):**
1. 🎓 [AZ‑900 — Azure Fundamentals](Certifications/AZ_900/00_AZ900_Study_Guide_Overview.md) *(done in Phase 3)* — broad Azure fundamentals
2. 🎓 [DP‑900 — Azure Data Fundamentals](Certifications/DP_900/00_DP900_Study_Guide_Overview.md) — the data counterpart to AZ‑900; easy foundational win
3. 🎓 [Databricks Data Engineer Associate](Certifications/Databricks_Data_Engineer_Associate/00_Study_Guide_Overview.md) — Delta, ELT, streaming, Auto Loader, DLT, Unity Catalog, + mock exam
4. 🎓 [DP‑700 — Fabric Data Engineer Associate](Certifications/DP_700_Fabric_Data_Engineer/00_DP700_Study_Guide_Overview.md) — **the flagship**; replaced the retired DP‑203. Ingest/transform/serve + secure/monitor/optimize on Fabric
> **Note:** DP‑203 (Azure Data Engineer Associate) was **retired in 2025** and replaced by **DP‑700 (Fabric Data Engineer)** — study DP‑700, not DP‑203.

**System design (the senior interview filter):**
- ✅ [System Design module (18)](18_System_Design/00_System_Design_Learning_Path.md) — the [design framework](18_System_Design/01_Design_Framework.md), [batch](18_System_Design/02_Batch_Pipeline_Design.md) & [streaming/real-time](18_System_Design/03_Streaming_and_Realtime_Design.md) design, [case studies](18_System_Design/04_Case_Studies.md)

**Portfolio (do this in parallel — it matters more than any single cert):**
- ✅ [Projects module (11)](11_Projects/00_Projects_Learning_Path.md) — build the three end-to-end projects and [present them well](11_Projects/05_Portfolio_and_GitHub_Presentation.md)

**Interview prep:** see the dedicated track below.

**Milestone:** pass the [Databricks Associate mock exam](Certifications/Databricks_Data_Engineer_Associate/13_Final_Mock_Exam.md), and complete a mock interview covering SQL + PySpark + one **[system-design](18_System_Design/00_System_Design_Learning_Path.md)** architecture question — with a **[portfolio project](11_Projects/00_Projects_Learning_Path.md)** on GitHub to walk through.

---

<a id="interview-prep-track"></a>
# Interview Prep Track (runs alongside Phases 5–8)

The **[Job Interviews handbook](Job%20Interviews/README.md)** — 31 focused topic folders for a 5+ year Azure DE. Map them to the phases:

| Area | Folders |
|---|---|
| **Core coding** | [PySpark](Job%20Interviews/PySpark/PySpark%20Interview%20Questions.md) · [Python](Job%20Interviews/Python/Python%20Interview%20Questions.md) · [SQL](Job%20Interviews/SQL/SQL%20Interview%20Questions.md) · [Coding Questions](Job%20Interviews/Coding%20Questions/Coding%20Questions.md) |
| **Databricks / lakehouse** | [Databricks](Job%20Interviews/Azure%20Databricks/Databricks%20Interview%20Questions.md) · [Delta Lake](Job%20Interviews/Delta%20Lake/Delta%20Lake%20Interview%20Questions.md) · [Lakehouse](Job%20Interviews/Lakehouse/Lakehouse%20Interview%20Questions.md) · [Performance Optimization](Job%20Interviews/Azure%20Databricks/Performance%20Optimization.md) |
| **Azure services** | [Data Factory](Job%20Interviews/Azure%20Data%20Factory/ADF%20Interview%20Questions.md) · [Synapse](Job%20Interviews/Azure%20Synapse/Synapse%20Interview%20Questions.md) · [Azure SQL](Job%20Interviews/Azure%20SQL/Azure%20SQL%20Interview%20Questions.md) · [Functions](Job%20Interviews/Azure%20Functions/Azure%20Functions%20Interview%20Questions.md) · [Purview](Job%20Interviews/Azure%20Purview/Azure%20Purview%20Interview%20Questions.md) |
| **Streaming** | [Event Hub](Job%20Interviews/Event%20Hub/Event%20Hub%20Interview%20Questions.md) · [Kafka](Job%20Interviews/Kafka/Kafka%20Interview%20Questions.md) · [Stream Analytics](Job%20Interviews/Stream%20Analytics/Stream%20Analytics%20Interview%20Questions.md) |
| **Data platform** | [Data Lake](Job%20Interviews/Data%20Lake/Data%20Lake%20Interview%20Questions.md) · [Data Warehousing](Job%20Interviews/Data%20Warehousing/Data%20Warehousing%20Interview%20Questions.md) · [Snowflake](Job%20Interviews/Snowflake/Snowflake%20Interview%20Questions.md) · [ETL vs ELT](Job%20Interviews/ETL%20vs%20ELT/ETL%20vs%20ELT%20Interview%20Questions.md) |
| **DevOps / IaC** | [Git](Job%20Interviews/Git/Git%20Interview%20Questions.md) · [CI-CD](Job%20Interviews/CI-CD/CICD%20Interview%20Questions.md) · [Docker](Job%20Interviews/Docker/Docker%20Interview%20Questions.md) · [Kubernetes](Job%20Interviews/Kubernetes/Kubernetes%20Interview%20Questions.md) · [Terraform](Job%20Interviews/Terraform/Terraform%20Interview%20Questions.md) · [ARM Templates](Job%20Interviews/ARM%20Templates/ARM%20Templates%20Interview%20Questions.md) · [Azure DevOps](Job%20Interviews/Azure%20DevOps/Azure%20DevOps%20Interview%20Questions.md) |
| **Reporting** | [Power BI](Job%20Interviews/Power%20BI/Power%20BI%20Interview%20Questions.md) |
| **Behavioural / mixed** | [Scenario Based](Job%20Interviews/Scenario%20Based%20Questions/Scenario%20Based%20Questions.md) · [HR](Job%20Interviews/HR%20Interview/HR%20Interview%20Questions.md) · [Cheat Sheets](Job%20Interviews/Cheat%20Sheets/Cheat%20Sheets.md) |

---

# The complete skills checklist

Tick these off before calling yourself job-ready:

**Languages & querying**
- [ ] SQL: joins, aggregates, subqueries, window functions, CTEs, query tuning
- [ ] Python: functions, comprehensions, files, exceptions, pandas basics
- [ ] PySpark: DataFrames, joins, windows, UDFs, Spark SQL, performance tuning

**Storage & formats**
- [ ] ADLS Gen2 / Blob; hot/cool/archive tiers; redundancy
- [ ] Parquet vs CSV/JSON/Avro/ORC — when and why
- [ ] Delta Lake: transaction log, ACID, time travel, `MERGE`, `OPTIMIZE`/`VACUUM`
- [ ] Lakehouse + medallion (Bronze/Silver/Gold)

**Modeling**
- [ ] Normalization + star/snowflake schema, facts/dimensions/grain
- [ ] Slowly Changing Dimensions (esp. SCD2)
- [ ] Kimball vs Inmon; data mart / mesh / fabric awareness

**Pipelines & platform**
- [ ] ETL vs ELT; batch vs streaming
- [ ] Azure Data Factory (pipelines, triggers, linked services, IR)
- [ ] Databricks (clusters, notebooks, jobs, Unity Catalog, DLT, Auto Loader)
- [ ] Change Data Capture; Structured Streaming; Event Hubs / Kafka
- [ ] Synapse / Microsoft Fabric awareness

**Cross-cutting**
- [ ] Data quality (validation, quarantine, expectations, observability)
- [ ] Governance & security (RBAC/ACL, Key Vault, Managed Identity, Purview, GDPR)
- [ ] Git + CI/CD; basic Docker/Terraform awareness
- [ ] Cost & performance optimization

**Proof**
- [ ] AZ‑900 passed
- [ ] Databricks Data Engineer Associate passed
- [ ] DP‑900 passed
- [ ] DP‑700 (Fabric Data Engineer) passed
- [ ] 1–2 end-to-end portfolio projects on GitHub

---

# Azure service cheat-sheet (what tool for what job)

| Job | Azure service |
|---|---|
| Store raw data cheaply | **ADLS Gen2** / Blob Storage |
| Orchestrate/ingest (low-code) | **Azure Data Factory** |
| Big-data transform (Spark) | **Azure Databricks** |
| SQL analytics / warehouse | **Synapse Analytics** / **Microsoft Fabric** |
| Table format for the lakehouse | **Delta Lake** |
| Streaming ingest | **Event Hubs** (Kafka-compatible) |
| Stream processing | **Stream Analytics** / Spark Structured Streaming |
| Secrets management | **Azure Key Vault** |
| Identity & access | **Microsoft Entra ID** + RBAC |
| Governance / catalog / lineage | **Microsoft Purview** / **Unity Catalog** |
| Reporting / BI | **Power BI** |
| Serverless glue code | **Azure Functions** |
| CI/CD | **Azure DevOps** / GitHub Actions |

---

# Suggested pace

This is guidance, not a rule — go at the speed the milestones allow.

| If you have… | Realistic timeline |
|---|---|
| ~2 hrs/day, non-technical start | **6–9 months** to job-ready |
| Full-time study | **3–4 months** |
| Already know SQL + Python | Skip to Phase 4; **2–3 months** |

**Golden rules:**
1. **Don't collect tutorials — hit milestones.** Knowing ≠ doing.
2. **SQL and PySpark are the two skills that get you hired.** Over-invest there.
3. **Build 1–2 real projects.** A medallion pipeline on public data beats ten certificates on a résumé.
4. **Read the interview Q&A files as you go**, not the night before — they reveal what "understood" really means.

---

*This roadmap indexes the notes in this repository. Start at [Phase 0](#phase-0--foundations--mindset) and, when in doubt, open the [README](README.md) for the full file-by-file table of contents.*
