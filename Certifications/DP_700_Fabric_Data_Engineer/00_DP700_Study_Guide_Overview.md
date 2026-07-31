# DP-700: Microsoft Fabric Data Engineer Associate — Study Guide

This folder is a complete, self-contained course to **learn, practice, and pass** the *DP-700: Microsoft Certified: Fabric Data Engineer Associate* exam. Read this file first — it's the map for everything else here.

---

## What is this certification?

**DP-700** is the **associate-level flagship** for data engineering on **Microsoft Fabric** — the credential that effectively **replaced the retired DP-203** (Azure Data Engineer Associate) as Microsoft's forward-looking data-engineering cert. It proves you can **ingest, transform, and serve data** in Fabric, and **secure, monitor, and optimize** an analytics solution built on **OneLake**.

It is a **practical, scenario-heavy** exam. You'll choose the right Fabric item for a task, recognize correct code (PySpark, Spark SQL, T-SQL, KQL), design load patterns, and troubleshoot/optimize.

- **Level:** Associate. Recommended: hands-on Fabric experience + comfort with SQL, PySpark, and data-engineering concepts.
- **Duration:** ~120 minutes.
- **Questions:** ~40–60, multiple-choice/multiple-select, drag-drop, case studies.
- **Passing score:** **700 / 1000** (scaled).
- **Cost:** ~$165 USD.
- **Delivery:** Online proctored or test center.
- **Validity:** Associate certs expire; renew annually (free online renewal).

> **Exam Tip:** DP-700 assumes **Fabric + OneLake + Delta** as the world. Answers favor the *Fabric-native, least-effort* option — Dataflow Gen2 or a pipeline copy for low-code ingestion, notebooks/Spark for complex transforms, Eventstream for streaming, deployment pipelines + Git for lifecycle. Know **which Fabric item** solves each scenario.

---

## Recommended prerequisites (from this repo)

DP-700 sits on top of nearly everything in this repo. Shore up these first:
- [Microsoft Fabric](../../10_Synapse_and_Fabric/03_Microsoft_Fabric.md) & [Synapse](../../10_Synapse_and_Fabric/01_Azure_Synapse_Analytics.md) — the platform
- [Lakehouse Architecture](../../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md), [Delta Lake](../../04_Storage_and_Formats/Lakehouse/01_Delta_Lake.md) & [Delta Table](../../04_Storage_and_Formats/Lakehouse/02_Delta_Table.md)
- [PySpark](../../06_Programming/PySpark/00_PySpark_Learning_Path.md) & [SQL](../../02_Databases/SQL/01_What_is_SQL.md)
- [Streaming](../../09_Streaming/00_Streaming_Learning_Path.md) — for Eventstream/Eventhouse
- [Data Governance](../../05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) & [Git/CI-CD](../../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md)

---

## The three exam domains (official weighting)

The three domains are **roughly equal** — study all three thoroughly; none is a small "easy win."

| # | Domain | Weight | Covered in |
|---|---|---|---|
| 1 | **Implement and manage an analytics solution** | 30–35% | [01](01_Fabric_and_Workspace_Fundamentals.md), [02](02_Security_Governance_and_Lifecycle.md) |
| 2 | **Ingest and transform data** | 30–35% | [03](03_Ingest_Data.md), [04](04_Transform_Data.md) |
| 3 | **Monitor and optimize an analytics solution** | 30–35% | [05](05_Monitor_and_Optimize.md) |

---

## Reading order

| # | File | Domain |
|---|---|---|
| 00 | This study guide | — |
| 01 | [Fabric & Workspace Fundamentals](01_Fabric_and_Workspace_Fundamentals.md) | Implement & manage |
| 02 | [Security, Governance & Lifecycle](02_Security_Governance_and_Lifecycle.md) | Implement & manage |
| 03 | [Ingest Data](03_Ingest_Data.md) | Ingest & transform |
| 04 | [Transform Data](04_Transform_Data.md) | Ingest & transform |
| 05 | [Monitor & Optimize](05_Monitor_and_Optimize.md) | Monitor & optimize |
| 06 | [Practice Questions by Domain](06_Practice_Questions_by_Domain.md) | All — practice |
| 07 | [Most Asked & Tricky Questions](07_Most_Asked_and_Tricky_Questions.md) | All — the traps |
| 08 | [Final Mock Exam](08_Final_Mock_Exam.md) | All — timed simulation |

**Suggested study plan (~2–3 weeks, ~1 hour/day):**
1. **Days 1–3:** Files 01–02 (platform, workspaces, security, lifecycle).
2. **Days 4–7:** Files 03–04 (ingestion + transformation — the code-heavy core; do the snippets by hand).
3. **Days 8–10:** File 05 (monitoring + optimization).
4. **Days 11–12:** File 06 (practice by domain).
5. **Day 13:** File 07 (traps & confusions).
6. **Day 14:** File 08 (full timed mock).

---

## How each note is structured

Every domain file (01–05) follows the same shape:
1. **What it is** — the concept and the Fabric items involved.
2. **The details the exam tests** — which item for which job, correct syntax, comparisons.
3. **Exam Tip callouts** — flagged at known wrong-answer sources.
4. **Quick Review** — a bullet summary for same-day re-reading.

---

## Exam-day strategy

- **Time budget:** ~2 min/question, but case studies eat time — budget for them.
- **"Which item?" questions** — map the need: low-code batch ingest → **Data pipeline (Copy)** or **Dataflow Gen2**; complex transform → **Notebook/Spark**; SQL warehouse → **Warehouse**; streaming → **Eventstream + Eventhouse**; reference external data without copying → **Shortcut**; near-real-time replica of an operational DB → **Mirroring**.
- **"Least effort / most efficient" wording** → pick the managed, Fabric-native, lowest-code option that still meets the requirement.
- **Read code carefully** — one keyword (`MERGE` vs `INSERT`, `mergeSchema`, window type, distribution) often decides it.
- **Default to Delta + OneLake** guarantees unless told otherwise.
- **No penalty for guessing** — never leave blanks.

Start here: **[01 — Fabric & Workspace Fundamentals](01_Fabric_and_Workspace_Fundamentals.md)**.
