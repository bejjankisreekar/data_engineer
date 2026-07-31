# 02 — Security, Governance & Lifecycle

*Domain: Implement and manage an analytics solution (30–35%)*

---

## What it is

The other half of "implement and manage": **who can access what** (security & governance) and **how solutions move from dev to production** (lifecycle management with Git and deployment pipelines). Background: [Data Governance & Security](../../05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) and [Git/CI-CD](../../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md).

---

## Access control layers (know the hierarchy)

Fabric secures data at several levels — a common source of exam questions:

| Level | Controls |
|---|---|
| **Workspace roles** | Broad access to *all* items in a workspace |
| **Item permissions** | Sharing a single item (e.g. a Lakehouse) with specific users |
| **OneLake data access roles** | Folder-level security within a Lakehouse's OneLake data |
| **SQL / warehouse granular security** | Object-, row-, column-level within the SQL engine |

### Workspace roles

| Role | Can do |
|---|---|
| **Admin** | Everything, incl. manage access & settings |
| **Member** | Add others (lower), edit content |
| **Contributor** | Create/edit items, run things — no access management |
| **Viewer** | Read/consume only |

> **Exam Tip:** **Viewer** can consume but not create/edit. **Contributor** builds items but can't manage access. To let someone build pipelines/notebooks but not grant others access → **Contributor**.

---

## Granular data security (SQL/warehouse)

- **Row-Level Security (RLS)** — restrict *which rows* a user sees (e.g. region-based) via security predicates.
- **Column-Level Security (CLS)** — restrict *which columns* a user can see.
- **Object-Level Security (OLS)** — hide entire tables/views from a user.
- **Dynamic Data Masking (DDM)** — mask column values (e.g. `xxxx-1234`) for unauthorized users without changing stored data.

> **Exam Tip:** RLS = rows, CLS = columns, OLS = whole objects, DDM = *masks* values (data still there, just hidden in output). "Show sales reps only their own region's rows" → **RLS**. "Hide the SSN column's real value from analysts" → **DDM** (or CLS to remove access entirely).

> **Exam Tip:** Security defined in a **Warehouse** (T-SQL RLS/CLS/DDM) applies when querying through the SQL engine. **OneLake data access roles** secure the underlying files at the lake level — different layers, sometimes both needed.

---

## Governance features

- **Sensitivity labels** — Microsoft Purview Information Protection labels (Confidential, etc.) that flow with data and exports.
- **Endorsement** — mark items as **Promoted** or **Certified** to signal trusted, quality data in the catalog.
- **Microsoft Purview integration** — cataloging, lineage, and data governance across OneLake.
- **Lineage view** — see how items depend on each other within a workspace.

> **Exam Tip:** To signal that a semantic model/lakehouse is trusted and official → **endorse** it (Certified > Promoted). To classify and protect sensitive data that follows it into exports → **sensitivity labels**.

---

## Lifecycle management: Git integration

- Connect a workspace to **Azure DevOps** or **GitHub** so items are **version-controlled**.
- Developers work in feature workspaces/branches, commit changes, and sync ([Git workflow](../../07_DevOps/Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md)).
- Supports code review via PRs and a source of truth for CI/CD.

## Lifecycle management: Deployment pipelines

- **Deployment pipelines** promote content across **Dev → Test → Prod** stages.
- **Deployment rules** parameterize stage-specific settings (e.g. point Test/Prod at different data sources) so the same items behave correctly per environment.

> **Exam Tip:** **Git** = version control & collaboration (source of truth, branches, PRs). **Deployment pipelines** = promote content between Dev/Test/Prod stages with rules. They're complementary — Git for *how code is versioned*, deployment pipelines for *how it's promoted*.

---

## Orchestration & scheduling

- **Data pipelines** orchestrate activities (Copy, Notebook, Dataflow, etc.) as a DAG with dependencies, and can be **scheduled** or triggered.
- **Notebooks** and **Dataflows** can be scheduled directly or run as pipeline activities.
- Triggers include schedule-based and (via pipelines/eventstreams) event-based patterns.

> **Exam Tip:** To run a multi-step ETL (copy → notebook transform → refresh) in order with dependencies and retries → a **Data pipeline**. To run a single notebook nightly → schedule the notebook or wrap it in a pipeline.

---

## Quick Review

- Access layers: **workspace roles** (broad) → **item permissions** → **OneLake data access roles** (folder) → **SQL granular** (RLS/CLS/OLS/DDM).
- Roles: **Admin** (all), **Member** (edit + add lower), **Contributor** (build, no access mgmt), **Viewer** (read).
- Granular: **RLS** = rows, **CLS** = columns, **OLS** = objects, **DDM** = masks values.
- Governance: **sensitivity labels** (Purview protection), **endorsement** (Promoted/Certified), **lineage**.
- Lifecycle: **Git** = version control/collaboration; **Deployment pipelines** = Dev→Test→Prod promotion with **deployment rules**.
- Orchestrate multi-step ETL with a **Data pipeline** (DAG, schedule, retries).

---

## Further Learning — Docs & Videos

- Fabric security overview: https://learn.microsoft.com/en-us/fabric/security/security-overview
- Git integration: https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration
- Deployment pipelines: https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines
- Video search: https://www.youtube.com/results?search_query=dp-700+fabric+security+deployment+pipelines

---

Next: **[03 — Ingest Data](03_Ingest_Data.md)**.
