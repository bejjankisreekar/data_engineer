# Databricks Certified Data Engineer Associate — Study Guide

This folder is a complete, self-contained course to **learn, practice, and pass** the *Databricks Certified Data Engineer Associate* exam. Read this file first — it's the map for everything else here.

---

## What is this certification?

The **Databricks Certified Data Engineer Associate** proves you can use the Databricks Lakehouse Platform to complete introductory data engineering tasks: building ETL/ELT pipelines with Spark SQL and Python, working with Delta Lake, doing incremental/streaming ingestion, orchestrating production jobs, and applying basic data governance with Unity Catalog.

It is a **practical, tool-specific** exam (unlike a broad fundamentals cert). You need to recognize correct syntax, know what each Databricks feature does, and choose the right tool for a scenario. You will **not** write long programs, but you *will* be shown code snippets and asked which one is correct, what a command does, or what output/behavior results.

- **Level:** Associate (entry-level for the Databricks data-engineering track). Next step up is the *Data Engineer Professional*.
- **Duration:** 90 minutes.
- **Questions:** 45 scored multiple-choice/multiple-select questions (some versions include a few unscored pilot questions).
- **Passing score:** 70% (you must get roughly 32 of 45 correct — treat it as a hard 70%).
- **Cost:** ~$200 USD (one retake typically requires re-paying).
- **Delivery:** Online proctored (webcam + ID + room scan). No notes, no second screen.
- **Prerequisites:** None required, but ~6 months of hands-on Databricks experience is recommended.
- **Validity:** 2 years — Databricks role-based certs expire and must be renewed.
- **Language / SQL dialect:** Spark SQL and PySpark (Python). No Scala/R needed to pass.

> **Exam Tip:** The exam is written against **Databricks on the Lakehouse with Unity Catalog and Delta Live Tables**. Answers assume Delta Lake is the *default* table format, not Parquet.

---

## The five exam domains (official weighting)

Study time should roughly match the weights. Databricks publishes these percentages:

| # | Domain | Weight | Covered in this folder |
|---|---|---|---|
| 1 | **Databricks Lakehouse Platform** | 24% | [01](01_Lakehouse_Platform_Fundamentals.md), [02](02_Workspace_Clusters_Notebooks_Repos.md), [03](03_Delta_Lake_Fundamentals.md) |
| 2 | **ELT with Spark SQL and Python** | 29% | [04](04_ELT_with_Spark_SQL.md), [05](05_ELT_with_PySpark_and_Python.md) |
| 3 | **Incremental Data Processing** | 22% | [06](06_Structured_Streaming.md), [07](07_Auto_Loader_and_Multi_Hop.md), [08](08_Delta_Live_Tables.md) |
| 4 | **Production Pipelines** | 16% | [09](09_Production_Pipelines_Jobs.md) |
| 5 | **Data Governance** | 9% | [10](10_Data_Governance_Unity_Catalog.md) |

Domains 1 and 2 together are over half the exam — Delta Lake and Spark-SQL/PySpark ELT are where most points live. Governance is the smallest but the easiest to score full marks on if you learn Unity Catalog's object hierarchy.

---

## Reading order

| # | File | Domain |
|---|---|---|
| 01 | [Lakehouse Platform Fundamentals](01_Lakehouse_Platform_Fundamentals.md) | Lakehouse Platform |
| 02 | [Workspace, Clusters, Notebooks & Repos](02_Workspace_Clusters_Notebooks_Repos.md) | Lakehouse Platform |
| 03 | [Delta Lake Fundamentals](03_Delta_Lake_Fundamentals.md) | Lakehouse Platform |
| 04 | [ELT with Spark SQL](04_ELT_with_Spark_SQL.md) | ELT with Spark SQL & Python |
| 05 | [ELT with PySpark & Python](05_ELT_with_PySpark_and_Python.md) | ELT with Spark SQL & Python |
| 06 | [Structured Streaming](06_Structured_Streaming.md) | Incremental Data Processing |
| 07 | [Auto Loader & Multi-Hop (Medallion)](07_Auto_Loader_and_Multi_Hop.md) | Incremental Data Processing |
| 08 | [Delta Live Tables (DLT)](08_Delta_Live_Tables.md) | Incremental Data Processing |
| 09 | [Production Pipelines — Jobs & Orchestration](09_Production_Pipelines_Jobs.md) | Production Pipelines |
| 10 | [Data Governance — Unity Catalog](10_Data_Governance_Unity_Catalog.md) | Data Governance |
| 11 | [Practice Questions by Domain](11_Practice_Questions_by_Domain.md) | All — practice |
| 12 | [Most Asked & Tricky Questions](12_Most_Asked_and_Tricky_Exam_Questions.md) | All — the traps |
| 13 | [Final Mock Exam](13_Final_Mock_Exam.md) | All — timed simulation |

**Suggested study plan (~2 weeks, ~1 hour/day):**

1. **Days 1–3:** Files 01–03 (platform + Delta Lake) — the foundation everything builds on.
2. **Days 4–6:** Files 04–05 (Spark SQL + PySpark ELT) — the largest domain; do the code snippets by hand.
3. **Days 7–9:** Files 06–08 (streaming, Auto Loader, DLT) — the incremental-processing core.
4. **Day 10:** File 09 (Jobs/production).
5. **Day 11:** File 10 (Unity Catalog governance).
6. **Day 12:** File 11 — practice questions by domain; re-read any topic you miss.
7. **Day 13:** File 12 — the traps and commonly-confused pairs.
8. **Day 14:** File 13 — full timed mock exam under real conditions.

---

## How each note is structured

Every topic file (01–10) follows the same shape:

1. **What it is** — plain-language definition with a real-world analogy.
2. **The details the exam actually tests** — the specific commands, behaviors, and comparisons Databricks asks about.
3. **Exam Tip callouts** — flagged inline wherever a concept is a known source of wrong answers.
4. **Quick Review** — a bullet summary at the end of each file for same-day re-reading.

---

## Exam-day mechanics and strategy

- **Time budget:** 90 minutes / 45 questions = 2 minutes each — comfortable. Flag hard ones and return.
- **Read code carefully.** Many questions hinge on one keyword: `MERGE` vs `INSERT`, `overwrite` vs `append`, `CREATE TABLE` vs `CREATE OR REPLACE TABLE`, managed vs external table, `display()` vs `.collect()`.
- **Watch for "which is correct syntax" questions.** Eliminate options with wrong function names or wrong argument order first.
- **"Least effort / most cost-effective / best-fit" questions** — pick the *managed* Databricks feature (Auto Loader over manual file listing, DLT over hand-written streaming, Jobs over external schedulers) unless the scenario says otherwise.
- **Default to Delta.** If a question doesn't state a format, assume Delta Lake and its guarantees (ACID, time travel, schema enforcement).
- **No penalty for guessing** — never leave a question blank.
- **Multiple-select questions** say "Select TWO" / "Select all that apply" — count your selections.

---

## What "detail" means for this exam

This is a **recognition and application** exam: know *what* each feature does, *what* the correct syntax looks like, and *which* feature fits a scenario. It does not test deep Spark internals (Catalyst optimizer stages, shuffle mechanics) at the Associate level — that's the Professional exam. This course is written at the right altitude: thorough on every fact the Associate exam can ask, without engineering-depth tangents it won't touch.

Start here: **[01 — Lakehouse Platform Fundamentals](01_Lakehouse_Platform_Fundamentals.md)**.
