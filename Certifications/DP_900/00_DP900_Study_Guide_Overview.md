# DP-900: Microsoft Azure Data Fundamentals — Study Guide

This folder is a complete, self-contained course to **learn, practice, and pass** the *DP-900: Microsoft Azure Data Fundamentals* exam. Read this file first — it's the map for everything else here.

---

## What is this certification?

**DP-900** proves you understand **core data concepts** and how they're implemented with **Azure data services** — relational, non-relational, and analytics. It's the **data counterpart to [AZ-900](../AZ_900/00_AZ900_Study_Guide_Overview.md)**: a broad, foundational, no-code exam that's the ideal entry point into the Azure data-engineering path and a natural stepping stone toward the associate-level [DP-700](../DP_700_Fabric_Data_Engineer/00_DP700_Study_Guide_Overview.md).

It is a **conceptual, breadth-first** exam. You won't write queries or build pipelines — you'll be asked *what* a service is for, *which* service fits a scenario, and *how* core data concepts work.

- **Level:** Fundamentals (entry-level). No prerequisites.
- **Duration:** ~45–60 minutes.
- **Questions:** ~40–60, multiple-choice/multiple-select (plus drag-drop, hotspot, and "yes/no" series).
- **Passing score:** **700 / 1000** (scaled — not a raw 70%).
- **Cost:** ~$99 USD.
- **Delivery:** Online proctored or test center.
- **Validity:** Fundamentals certs **do not expire**.

> **Exam Tip:** DP-900 rewards **recognition, not depth**. You need to know what each service *is for* and pick the right one — not configure it. If two answers seem right, choose the one that is *purpose-built* for the scenario (e.g., Cosmos DB for global low-latency NoSQL, Synapse/Fabric for analytics).

---

## The four exam domains (official weighting)

| # | Domain | Weight | Covered in |
|---|---|---|---|
| 1 | **Core data concepts** | 25–30% | [01](01_Core_Data_Concepts.md) |
| 2 | **Relational data on Azure** | 20–25% | [02](02_Relational_Data_on_Azure.md) |
| 3 | **Non-relational data on Azure** | 15–20% | [03](03_Non_Relational_Data_on_Azure.md) |
| 4 | **Analytics workloads on Azure** | 25–30% | [04](04_Analytics_Workloads_on_Azure.md) |

Domains 1 and 4 are the biggest — core concepts and analytics together are more than half the exam. Domain 4 leans on services this repo covers in depth ([Synapse/Fabric](../../10_Synapse_and_Fabric/00_Learning_Path.md), [Databricks](../../08_Databricks/00_Databricks_Learning_Path.md), [ADF](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md), Power BI).

---

## Reading order

| # | File | Domain |
|---|---|---|
| 00 | This study guide | — |
| 01 | [Core Data Concepts](01_Core_Data_Concepts.md) | Core data concepts |
| 02 | [Relational Data on Azure](02_Relational_Data_on_Azure.md) | Relational data |
| 03 | [Non-Relational Data on Azure](03_Non_Relational_Data_on_Azure.md) | Non-relational data |
| 04 | [Analytics Workloads on Azure](04_Analytics_Workloads_on_Azure.md) | Analytics workloads |
| 05 | [Practice Questions by Domain](05_Practice_Questions_by_Domain.md) | All — practice |
| 06 | [Most Asked & Tricky Questions](06_Most_Asked_and_Tricky_Questions.md) | All — the traps |
| 07 | [Final Mock Exam](07_Final_Mock_Exam.md) | All — timed simulation |
| 08 | [Exam Dump: Practice Set](08_Exam_Dump_Practice_Set.md) | All — 30 extra exam-style Q&A |

**Suggested study plan (~1 week, ~1 hour/day):**
1. **Day 1:** File 01 — core concepts (the vocabulary everything else uses).
2. **Day 2:** File 02 — relational services.
3. **Day 3:** File 03 — non-relational (Storage + Cosmos DB).
4. **Days 4–5:** File 04 — analytics (the biggest service-heavy domain).
5. **Day 6:** Files 05 + 06 — practice and traps.
6. **Day 7:** File 07 — full timed mock.

---

## How each note is structured

Every topic file (01–04) follows the same shape:
1. **What it is** — plain-language definition, often with an analogy.
2. **The details the exam tests** — the specific services, comparisons, and "which fits" decisions.
3. **Exam Tip callouts** — flagged wherever a concept causes wrong answers.
4. **Quick Review** — a bullet summary for same-day re-reading.

---

## Exam-day mechanics and strategy

- **Time budget** is generous — read carefully, don't rush.
- **Question styles:** single-answer, multiple-select ("select all that apply"), drag-and-drop matching, hotspot, and **yes/no statement series** (each statement scored independently — don't let one wrong one bias the others).
- **"Which service?" questions** — map the keyword: *global, low latency, NoSQL* → Cosmos DB; *relational PaaS* → Azure SQL Database; *huge analytics storage* → ADLS Gen2; *warehouse/analytics* → Synapse/Fabric; *pipelines/ETL* → Data Factory; *dashboards* → Power BI.
- **No penalty for guessing** — never leave a question blank.
- **Beware absolute words** in yes/no items ("always", "never", "only") — often the tell for a false statement.

Start here: **[01 — Core Data Concepts](01_Core_Data_Concepts.md)**.
