# Orchestration — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Fundamentals

**Q1. 🔥 What is data orchestration, and how is it different from transformation?**
Orchestration **coordinates** tasks — order, scheduling, dependencies, retries, alerting (the control plane). Transformation is the actual data work (the data plane). ADF/Airflow orchestrate; Spark/Databricks/dbt transform. Keep them separate.

**Q2. 🔥 What is a DAG?**
A **Directed Acyclic Graph** of tasks: directed (dependencies have order), acyclic (no loops, so runs terminate). Every orchestrator runs a DAG.

**Q3. 🔥 Why must orchestrated tasks be idempotent?**
Because retries and backfills can run a task more than once for the same data. Idempotent tasks (MERGE/upsert, partition overwrite) produce the same result on a rerun; non-idempotent ones (blind append, "add N") double-count.

**Q4. ⭐ What features should an orchestrator provide?**
Scheduling, dependencies, retries, timeouts, alerting, backfill, and observability (run history/logs/lineage).

**Q5. 💡 How do you handle a failing task?**
Retries with backoff for transient errors, alert on failure (always), quarantine bad rows, timeouts for hangs, and a deliberate fail-fast vs continue policy per branch.

**Q6. ⭐ Batch vs event-driven orchestration?**
Batch runs on a schedule/interval; event-driven runs when something happens (file lands, message arrives). Use event-driven for low-latency ingestion, batch for periodic loads.

---

## Azure Data Factory

**Q7. 🔥 Schedule trigger vs tumbling-window trigger?**
Schedule is **stateless** — fires at a clock time, no memory. Tumbling window is **stateful** per time slice: supports window dependencies, per-window retries, concurrency control, and **backfill**. Prefer tumbling for ordered/backfillable data pipelines.

**Q8. 🔥 How do you pull data from an on-prem source in ADF?**
A **Self-hosted Integration Runtime** installed near the source, giving secure connectivity to on-prem/private-network systems.

**Q9. 🔥 How would you design an ADF pipeline to load 200 tables?**
**Metadata-driven**: one parameterized pipeline + a config/control table + a `ForEach` loop — add a table to config, no new pipeline. DRY and scalable.

**Q10. ⭐ Name the activity dependency conditions.**
Success, Failure, Completion, Skipped — used to build success chains and failure/alert paths.

**Q11. ⭐ Where do you store secrets in ADF?**
In **Azure Key Vault**, referenced by linked services — never inline in the pipeline.

**Q12. 💡 How do you do incremental loads in ADF?**
Watermark pattern: Lookup last watermark → Copy `WHERE modified_date > @watermark` → update watermark. Or source-side **CDC**.

**Q13. 💡 How is ADF deployed across dev/test/prod?**
Git integration → publish generates **ARM templates** → release pipeline promotes with per-environment parameters.

---

## Databricks Workflows & DLT

**Q14. 🔥 Job cluster vs all-purpose cluster?**
Job clusters are **ephemeral**, created per run and auto-terminated — cheaper and isolated, right for scheduled jobs. All-purpose clusters are interactive/shared for dev and costly if left running.

**Q15. ⭐ ADF vs Databricks Workflows — when each?**
ADF for broad Azure ingestion and low-code orchestration across services; Workflows for Databricks-centric transform DAGs (notebooks/DLT/dbt). Often combined: ADF triggers a Databricks job.

**Q16. ⭐ What is a "repair run"?**
Re-running only the **failed tasks** of a job rather than the whole DAG — saves time and compute on large pipelines.

**Q17. 💡 What is Delta Live Tables and how does it relate to orchestration?**
A declarative pipeline framework: you write transformations + data-quality expectations, and DLT auto-builds the dependency graph, incremental processing, retries, and monitoring. Use DLT for quality-gated table pipelines; Workflows for arbitrary task orchestration.

**Q18. 💡 How do you deploy Databricks jobs as code?**
Define as JSON/YAML and deploy via Databricks CLI/REST/Terraform/**Asset Bundles** through CI/CD — versioned and reproducible, not manual UI clicks.

---

## Apache Airflow

**Q19. 🔥 What is Airflow and why is it popular?**
An open-source orchestrator where pipelines are **Python-defined DAGs** — flexible, version-controllable, testable, with a huge operator ecosystem. The de facto industry standard.

**Q20. 🔥 What is a DAG in Airflow, and how are dependencies set?**
A Python file defining tasks and their order; dependencies with `a >> b` (or `set_upstream`/`set_downstream`).

**Q21. ⭐ Operator vs sensor?**
An **operator** performs an action (`PythonOperator`, `DatabricksRunNowOperator`); a **sensor** waits for a condition (file exists, partition ready, another DAG done) before downstream tasks proceed.

**Q22. ⭐ What does `catchup` control?**
Whether Airflow **backfills** all missed intervals when a DAG is deployed with a past `start_date`. Set `False` to avoid an accidental backfill flood.

**Q23. 💡 What is XCom, and what is it *not* for?**
A mechanism to pass **small** values between tasks. Not for large datasets — pass those through storage (ADLS/Delta) and hand references via XCom.

**Q24. 💡 Does Airflow process big data itself?**
Usually not — it **orchestrates and triggers** external compute (Databricks/Spark/warehouse) and waits on results. Tasks should be idempotent because backfills rerun intervals.

**Q25. 💡 Airflow vs ADF vs Databricks Workflows — pick one, when?**
Airflow: complex, dynamic, code-first, cross-system DAGs. ADF: Azure-native ingestion, low-code, fully managed. Workflows: Databricks-centric transforms. Real platforms mix them.

---

## Scenario

**Q26. 🔥 "Ingest daily files + trigger a Spark transform + refresh a dashboard, with alerting." Design it.**
Trigger (tumbling window / schedule or file-event) → Copy/Auto Loader to Bronze → Databricks (or DLT) Bronze→Silver→Gold with idempotent MERGE → refresh Power BI → success/failure dependency paths, retries, and a failure→alert activity; logs to Azure Monitor with an alert on failed runs.

**Q27. 💡 A nightly job failed at 3 AM on step 4 of 6. What happens and what do you want?**
You want: an **alert** fired immediately, **retries** already attempted for transient causes, the ability to **repair/rerun from the failed step** (not re-run 1–3), **idempotency** so the rerun is safe, and run **logs/lineage** to diagnose. If those exist, it's a self-healing or quick-fix situation, not a rebuild.

---

## Further Learning
- Back to the [Learning Path](00_Orchestration_Learning_Path.md)
- Related: [ADF basics](../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) · [Monitoring](../12_Monitoring_and_Observability/00_Monitoring_Learning_Path.md) · [DataOps](../14_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)
