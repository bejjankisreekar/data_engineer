# 09 — Production Pipelines: Jobs & Orchestration

*Domain: Production Pipelines (16%)*

---

## What it is

**Databricks Jobs** (part of **Workflows**) is the built-in **orchestration** service for running data pipelines in production on a schedule or trigger. A **Job** is a collection of one or more **tasks** arranged as a dependency graph (DAG), each task running a notebook, script, DLT pipeline, SQL query, or JAR. Jobs handle scheduling, dependencies, retries, alerts, and monitoring — so you don't need an external orchestrator like Airflow for most Databricks work.

> **Exam Tip:** **Databricks Workflows/Jobs** is the native orchestration tool. Prefer it over external schedulers for orchestrating Databricks pipelines. A Job is the unit of scheduling; **tasks** are the steps inside it.

---

## Jobs and tasks

- A **Job** can contain **multiple tasks** with **dependencies** — task B runs only after task A succeeds. This forms a **multi-task DAG**.
- Each **task** can be a different type: notebook, Python script, Python wheel, JAR, SQL task, **DLT pipeline task**, dbt task, or "Run Job" (nesting a job).
- Tasks can pass values between each other and share job parameters.

> **Exam Tip:** A single Job can chain multiple tasks with dependencies (a DAG) — e.g., ingest → transform → aggregate → notify. You configure the order via each task's **"Depends on"** setting. Tasks can run **sequentially or in parallel** depending on their dependencies.

---

## Clusters for Jobs

- **Job cluster** — created when the job starts and **terminated when it ends**. Recommended for production: isolated, cheaper, fresh state each run.
- **All-purpose cluster** — can be used but is more expensive and less isolated; not recommended for scheduled production jobs.
- **Shared job cluster** — multiple tasks in the same job run can share one job cluster to save startup cost.

> **Exam Tip:** Use **job clusters** for scheduled production jobs (auto-created, auto-terminated → lower cost). Using an all-purpose cluster for a scheduled job wastes money because it stays running.

---

## Scheduling and triggers

Jobs can run:

- **On a schedule** — using **cron syntax** (e.g., every hour, daily at 2 AM) with a chosen time zone.
- **File arrival trigger** — run when new files land in a location.
- **Continuous** — keep a job running, restarting on completion (for near-real-time).
- **Manually / via API / via REST or CLI**.
- **Triggered by another job** ("Run Job" task).

> **Exam Tip:** Databricks Jobs support **cron-based schedules** and **file-arrival triggers**. For near-real-time you can set a job to **continuous**. Know that scheduling is built in — you don't need cron on an external server.

---

## Reliability: retries, alerts, monitoring

- **Retries** — configure automatic retries per task (max retries, retry interval) so transient failures self-heal.
- **Timeouts** — cap how long a task may run.
- **Alerts / notifications** — email or system (Slack, PagerDuty, webhooks) notifications on **start, success, failure, or duration threshold**.
- **Job run history / monitoring** — the Jobs UI shows each run's status, duration, task-level logs, and lineage; you can view/repair failed runs.
- **Repair run** — re-run only the **failed tasks** of a job instead of the whole job (saves time/cost).

> **Exam Tip:** Configure **automatic retries** to recover from transient failures, and **email/notification alerts** on failure to be informed. **Repair run** re-executes only the failed (and downstream) tasks — you don't rerun successful upstream tasks. These reliability features are commonly tested for the Production Pipelines domain.

---

## Parameters and passing values

- **Job parameters / task parameters** — pass values into notebooks at runtime (read via `dbutils.widgets.get(...)`).
- **Task values** (`dbutils.jobs.taskValues.set/get`) — pass small values from one task to a downstream task.

> **Exam Tip:** Notebooks read job-passed parameters with **`dbutils.widgets.get("param")`**. This is how one job definition runs for `dev`/`staging`/`prod` by passing different parameter values.

---

## DLT pipelines as job tasks

- A **DLT pipeline** can be scheduled and orchestrated as a **task inside a Job** — combining DLT's declarative processing with Workflows' scheduling and dependency management.

---

## Access control on jobs

Jobs support permission levels (via ACLs / Unity Catalog):

- **Can View**, **Can Manage Run**, **Can Manage**, and an **Owner**.
- The **owner/run-as identity** determines whose permissions the job uses when accessing data.

> **Exam Tip:** A job runs **as a specific identity** ("run as"), and that identity's permissions govern what data the job can read/write. Job permission levels (Can View / Can Manage Run / Can Manage / Owner) control who can see and operate the job.

---

## Quick Review

- **Jobs/Workflows** = native orchestration; a **Job** contains **tasks** in a dependency **DAG** (sequential or parallel).
- Task types: notebook, script, wheel, JAR, SQL, **DLT pipeline**, dbt, "Run Job".
- Use **job clusters** (auto-created/terminated) for production; all-purpose clusters cost more.
- Scheduling: **cron**, **file-arrival trigger**, **continuous**, manual/API.
- Reliability: **retries**, **timeouts**, **alerts/notifications** on failure, run history, **Repair run** (rerun only failed tasks).
- Parameters via **`dbutils.widgets.get`**; task-to-task values via `taskValues`.
- Jobs **run as an identity**; permission levels: Can View / Can Manage Run / Can Manage / Owner.

---

## Further Learning — Docs & Videos

**Official documentation**
- Databricks Jobs / Workflows: https://docs.databricks.com/en/jobs/index.html
- Create and run jobs: https://docs.databricks.com/en/jobs/create-run-jobs.html
- Schedule & triggers: https://docs.databricks.com/en/jobs/schedule.html
- Retries & notifications: https://docs.databricks.com/en/jobs/settings.html
- Repair a failed job run: https://docs.databricks.com/en/jobs/repair-job-failures.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Databricks Workflows / Jobs tutorial: https://www.youtube.com/results?search_query=databricks+workflows+jobs+tutorial
- Multi-task jobs & dependencies: https://www.youtube.com/results?search_query=databricks+multi+task+job+dependencies
- Job scheduling, retries, alerts: https://www.youtube.com/results?search_query=databricks+job+schedule+retry+alert

---

Next: **[10 — Data Governance: Unity Catalog](10_Data_Governance_Unity_Catalog.md)**.
