# Notebooks, Repos & Jobs

## What is it?

This note covers the three things you actually *work in* on Databricks:

- **Notebooks** — the interactive documents where you write and run code.
- **Repos** — Git integration, so notebooks live in version control like real code.
- **Jobs / Workflows** — the orchestrator that runs notebooks (and other tasks) on a schedule, in order, with retries and alerts.

Together they're the developer loop: **write** in a notebook, **version** it with Repos, **productionize** it as a Job.

---

## Analogy: recipe card → cookbook → restaurant service

A **notebook** is a single **recipe card** you scribble and taste as you go — write a step, run it, see the result, adjust. **Repos** turn your pile of cards into a **version-controlled cookbook** — every edit tracked, branches for experiments, nothing lost. A **Job** is the **restaurant's nightly service**: the recipes run in the right order, at the right time, every night, and if a dish fails someone gets paged — no chef standing there clicking "run."

---

## Notebooks

A notebook is a document of **cells**, each runnable, mixing languages and prose.

```python
# A Python cell
df = spark.read.table("sales")

# %sql — switch language per cell with magic commands
%sql
SELECT region, sum(amount) FROM sales GROUP BY region

# %md — documentation cells
# %run ./setup — run another notebook
```

Key features:
- **Multi-language** — `%python`, `%sql`, `%scala`, `%r`, `%md`, `%sh` per cell.
- **`dbutils`** — the utility toolbelt: `dbutils.fs` (files), `dbutils.widgets` (parameters), `dbutils.secrets` (Key Vault-backed secrets), `dbutils.notebook` (call other notebooks).
- **Widgets** — input parameters (`dbutils.widgets.text("date","")`) so one notebook is reusable across dates/environments.
- **Collaboration** — real-time co-editing, comments, version history.

---

## Repos (Git integration)

Repos connect a Databricks folder to a Git provider (Azure DevOps, GitHub, GitLab). This is how notebooks stop being clickware and become **engineered software**:

- Branch, commit, push, pull, open PRs — the [Git workflow](../07_DevOps/Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md) you already know.
- Separate **dev / staging / prod** by checking out different branches per workspace.
- Enables **CI/CD**: a pipeline tests and deploys notebooks on merge ([CI/CD](../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md)).

Without Repos, "version control" is the notebook's built-in revision history — fine for solo work, inadequate for a team.

---

## Jobs / Workflows (orchestration)

A **Job** (in the Workflows UI) runs one or more **tasks** on a schedule or trigger. This is Databricks' built-in orchestrator.

```
Job: "Nightly Sales Pipeline"   (trigger: cron 0 2 * * *)
  Task 1: ingest_bronze   (notebook)  ──┐
  Task 2: clean_silver    (notebook)  ◄─┘ depends on Task 1
  Task 3: aggregate_gold  (notebook)  ◄── depends on Task 2
  on failure → retry 2×, then email/Teams alert
```

A task can be a notebook, a Python script/wheel, a JAR, a SQL query, a DLT pipeline, or `dbt`. Tasks form a **DAG** ([DAG concept](../06_Data_Engineering/ETL_ELT/03_Data_Pipelines.md)) with dependencies, so steps run in order and in parallel where possible. Features: retries, timeouts, alerts, parameters, and running on cheap **job clusters** ([why](02_Clusters_and_Compute.md)).

---

## Advantages

- **Fast feedback** — notebooks let you run and see results cell by cell.
- **Mixed languages** — SQL and Python in one document, ideal for data work.
- **Real version control** — Repos bring branching, PRs, and CI/CD.
- **Built-in orchestration** — Jobs cover most pipelines without a separate tool like Airflow.
- **Parameterized & reusable** — widgets + job parameters make one notebook serve many runs.

## Disadvantages

- **Notebooks encourage bad habits** — hidden state, out-of-order runs, giant untested cells.
- **Harder to unit-test** than plain `.py` modules — extract logic into functions/libraries for testing.
- **Jobs orchestration is Databricks-only** — cross-system pipelines may still need Airflow/ADF.
- **Widget/secret misuse** — plaintext secrets in notebooks is a real, common security bug.

---

## Azure Usage

- **Secrets** — back Databricks secret scopes with **Azure Key Vault**; read via `dbutils.secrets.get()` so credentials never appear in code ([governance](../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)).
- **ADF ↔ Databricks** — Azure Data Factory can trigger a Databricks notebook/job as a pipeline activity, passing parameters — common when ADF owns ingestion and Databricks owns transformation.
- **Azure DevOps Repos** — the usual Git backend for Databricks Repos and CI/CD.

---

## Real World Example

An analyst prototypes a churn report in a notebook — SQL cells to explore, Python cells to shape the data — tweaking cells until the numbers look right. Once validated, the team moves it into a **Repo**, refactors the logic into tested functions on a feature branch, and opens a PR. After merge, a **Job** runs it nightly on a job cluster: ingest → transform → write the Gold table, with a 2× retry and a Teams alert on failure. Key Vault holds the source database password, read via `dbutils.secrets` — so the credential is never in the notebook. The prototype became a governed production pipeline without leaving Databricks.

---
---

# Part 2 — Advanced

## Notebook-scoped vs cluster libraries

Installing a package with `%pip install` inside a notebook is **notebook-scoped** — isolated to that session, reproducible, and the modern default. **Cluster libraries** install for every notebook on the cluster (heavier, shared, risk of conflicts). Prefer notebook-scoped for reproducibility; use cluster libraries only for genuinely shared dependencies.

## Parameterization: widgets + job parameters

Widgets turn a notebook into a function. A job passes parameters (e.g. `run_date`) into the widget, so the *same* notebook backfills any date:

```python
dbutils.widgets.text("run_date", "")
run_date = dbutils.widgets.get("run_date")
df = spark.read.table("bronze").where(f"load_date = '{run_date}'")
```

This is how one notebook serves dev/prod and daily/backfill runs — parameterize, don't copy-paste.

## Job orchestration patterns

- **Task dependencies** build a DAG — fan-out (one task → many parallel) and fan-in (many → one).
- **Conditional / branching tasks** run based on prior results.
- **Job-to-job triggers** — one job's completion kicks off another (file-arrival or table-update triggers too).
- **`foreachBatch` / task values** pass small results between tasks.

## Repos & CI/CD

The production loop: develop on a branch in a Repo → PR with automated tests (extract logic into a Python library and run `pytest`) → merge → a CI/CD pipeline (Azure DevOps/GitHub Actions) deploys to the prod workspace and updates the Job definition (often via **Databricks Asset Bundles**, the modern deploy format). See [Production Best Practices & CI/CD](../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Notebooks are for developing; libraries are for testing

The senior habit: notebooks orchestrate, but **business logic lives in importable Python modules** (packaged as a wheel, versioned in the Repo) that can be unit-tested with `pytest` in CI. A pipeline of 2,000-line notebooks with no tests is a liability; the same logic as tested functions called by thin notebooks is maintainable. "Can this be unit-tested?" is the question that separates prototype from production.

## Hidden state — the notebook's original sin

Running cells out of order creates results that depend on execution history, not on the code — reproducible on your screen, broken for the next person and in a scheduled run (which always runs top to bottom). Discipline: "Run All" from a fresh cluster before trusting a notebook, and never rely on a variable defined in a cell you've since edited.

## Databricks Jobs vs a dedicated orchestrator

Databricks Workflows handles Databricks-centric pipelines well and cheaply. But when orchestration spans many systems (an ADF copy, then Databricks, then a Synapse proc, then a Power BI refresh), a tool-agnostic orchestrator (**Airflow**, or ADF as the top-level conductor) is the better conductor, calling Databricks jobs as one step. Choosing the orchestration layer is an architecture decision, not a default.

## Field-tested gotchas

- **Secrets in plaintext** — hardcoded keys/passwords in notebooks; use Key Vault-backed secret scopes and `dbutils.secrets`.
- **Out-of-order cell execution** — "works on my screen," fails in the scheduled top-to-bottom run.
- **Untestable mega-notebooks** — no functions, no tests; refactor logic into libraries.
- **Interactive cluster in the job** — job tasks should run on job clusters, not a shared interactive one.
- **No parameterization** — copy-pasting a notebook per environment/date instead of using widgets/params.

## Interview-grade Q&A

- *How do you orchestrate pipelines in Databricks?* Jobs/Workflows: tasks (notebook/script/SQL/DLT/dbt) arranged as a DAG with dependencies, schedules/triggers, retries, and alerts, running on job clusters.
- *How do you handle secrets?* Secret scopes backed by Azure Key Vault, read at runtime via `dbutils.secrets.get()` — never hardcoded in the notebook.
- *How do you make a notebook reusable across dates/environments?* Widgets + job parameters, so the same notebook is parameterized instead of copied.
- *How do notebooks fit version control and CI/CD?* Databricks Repos connect to Git for branching/PRs; CI/CD (Azure DevOps/GitHub Actions, Asset Bundles) tests and deploys to workspaces.
- *When would you use Airflow/ADF instead of Databricks Workflows?* When orchestration spans multiple systems beyond Databricks; a tool-agnostic conductor calls Databricks jobs as one step.

---

## Related Notes

- **Prev:** [Clusters & Compute](02_Clusters_and_Compute.md) · **Next:** [Unity Catalog](04_Unity_Catalog.md)
- **Orchestration concept:** [Data Pipelines](../06_Data_Engineering/ETL_ELT/03_Data_Pipelines.md) · **CI/CD:** [Production Best Practices](../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md)
- **Cert:** [Production Pipelines & Jobs](../Certifications/Databricks_Data_Engineer_Associate/09_Production_Pipelines_Jobs.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Notebooks: https://learn.microsoft.com/en-us/azure/databricks/notebooks/
- Jobs / Workflows: https://learn.microsoft.com/en-us/azure/databricks/jobs/
- Databricks Repos: https://learn.microsoft.com/en-us/azure/databricks/repos/

**Videos**
- Databricks Workflows / Jobs: https://www.youtube.com/results?search_query=databricks+workflows+jobs+tutorial
- Databricks Repos Git integration: https://www.youtube.com/results?search_query=databricks+repos+git
