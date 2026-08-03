# AZ-900: Microsoft Azure Fundamentals — Study Guide

This folder is a complete, self-contained course to **learn, practice, and pass** the AZ-900 exam. Read this file first — it's the map for everything else here.

---

## What is AZ-900?

**AZ-900 (Microsoft Azure Fundamentals)** is Microsoft's entry-level certification proving you understand core cloud concepts and how they're implemented in Azure. It is **not** a hands-on engineering exam — you won't be asked to write code or configure a real resource. It tests whether you know *what* Azure services exist, *what problem each solves*, and *how they compare to each other*. That makes it a breadth exam, not a depth exam: wide vocabulary beats deep expertise here.

- **No prerequisites.** Anyone can sit it — it's the recommended starting point before any role-based Azure certification (Administrator AZ-104, Developer AZ-204, Data Engineer DP-203, Security SC-900, etc.).
- **Duration:** 85 minutes (includes time for the pre-exam survey/tutorial).
- **Questions:** roughly 40–60, mostly multiple choice (single answer), some multi-select, some drag-and-drop/matching, occasionally a short case-study style set.
- **Passing score:** 700 out of 1000 (scaled scoring — this is *not* "70% of questions correct"; some questions are weighted more than others and some are unscored pilot questions).
- **Cost:** ~$99 USD (varies by country; often discounted/free via student programs, Microsoft Learn events, or employer vouchers).
- **Delivery:** in person at a Pearson VUE test center, or online proctored from home (webcam + ID check, room scan required).
- **Validity:** Fundamentals certifications don't expire (unlike role-based certs, which need renewal).

---

## The three exam domains (Skills Measured)

Microsoft publishes an official weighting — study time should roughly match it:

| Domain | Weight | Covered in this folder |
|---|---|---|
| **Describe cloud concepts** | 25–30% | [01_Cloud_Concepts.md](01_Cloud_Concepts.md) |
| **Describe Azure architecture and services** | 35–40% | [02](02_Azure_Architecture_Fundamentals.md) – [06](06_Identity_Access_Security.md) |
| **Describe Azure management and governance** | 30–35% | [07](07_Cost_Management.md) – [09](09_Monitoring_and_Management_Tools.md) |

The middle domain is the largest because it covers the most ground: architecture fundamentals, compute, networking, storage, and identity/security are each their own file in this course.

---

## Reading order

| # | File | Domain |
|---|---|---|
| 01 | [Cloud Concepts](01_Cloud_Concepts.md) | Cloud concepts |
| 02 | [Azure Architecture Fundamentals](02_Azure_Architecture_Fundamentals.md) | Architecture & services |
| 03 | [Azure Compute Services](03_Azure_Compute_Services.md) | Architecture & services |
| 04 | [Azure Networking Services](04_Azure_Networking_Services.md) | Architecture & services |
| 05 | [Azure Storage Services](05_Azure_Storage_Services.md) | Architecture & services |
| 06 | [Identity, Access & Security](06_Identity_Access_Security.md) | Architecture & services |
| 07 | [Cost Management](07_Cost_Management.md) | Management & governance |
| 08 | [Governance & Compliance](08_Governance_and_Compliance.md) | Management & governance |
| 09 | [Monitoring & Management Tools](09_Monitoring_and_Management_Tools.md) | Management & governance |
| 10 | [Practice Questions by Domain](10_Practice_Questions_by_Domain.md) | All — practice |
| 11 | [Most Asked & Tricky Questions](11_Most_Asked_and_Tricky_Exam_Questions.md) | All — the traps |
| 12 | [Final Mock Exam](12_Final_Mock_Exam.md) | All — timed simulation |
| 13 | [Exam Dump: Practice Set](13_Exam_Dump_Practice_Set.md) | All — 30 extra exam-style Q&A |

**Suggested study plan (roughly 2 weeks, ~1 hour/day):**

1. **Days 1–2:** File 01 (cloud concepts) — the foundation everything else builds on.
2. **Days 3–7:** Files 02–06, one per day — this is the bulk of the exam.
3. **Days 8–9:** Files 07–09 — cost, governance, tools.
4. **Day 10:** File 10 — practice questions by domain, review anything you got wrong by re-reading that topic's note.
5. **Day 11:** File 11 — the tricky/commonly-confused pairs; these are where most points are lost.
6. **Day 12:** File 12 — the full timed mock exam under real conditions.
7. **Days 13–14:** Re-read only your weak areas; retake the mock exam sections you scored lowest on.

---

## How each note is structured

Every topic file (01–09) follows the same shape:

1. **What it is** — plain-language definition with a real-world analogy.
2. **The details the exam actually tests** — the specific facts, comparisons, and numbers Microsoft asks about.
3. **Exam Tip callouts** — flagged inline wherever a concept is a known source of wrong answers.
4. **Quick Review** — a bullet-point summary at the end of each file, good for same-day re-reading.

---

## Exam-day mechanics and strategy

- **Time budget:** ~85 minutes for ~50 questions ≈ under 2 minutes per question on average — comfortable at this level if you don't get stuck. If a question is taking too long, mark it for review and move on; you can return to flagged questions before submitting.
- **Read the question twice.** Fundamentals questions are often won or lost on a single word — "which is **not** an example of...", "which service provides **the fastest** retrieval", "which model requires **no** infrastructure management." Skimming causes most wrong answers, not lack of knowledge.
- **Eliminate obviously wrong options first.** Most 4-option questions have 1–2 answers you can rule out immediately, turning a guess into a 50/50.
- **Watch for "best"/"most cost-effective"/"least effort" questions** — these often have more than one *technically correct* option, but only one *best-fit* one. Re-read the scenario's actual constraint (cost? uptime? least management? compliance?) before choosing.
- **Case-study-style question sets** (a short scenario followed by several questions) let you re-read the scenario for each question — do so; don't rely on memory of it from three questions ago.
- **You cannot skip and come back within a "case study" segment once submitted** on some exam versions, but standalone questions can generally be flagged and revisited — use the review screen at the end.
- **Don't panic over vendor-specific numbers** (exact GB limits, exact SLA percentages) — the exam tests concepts and relationships far more than memorized figures, though a handful of well-known numbers (SLA tiers, region-pair counts, redundancy copy counts) are worth knowing cold — they're covered explicitly in this course.
- **Guess rather than leave blank** — there is no penalty for a wrong answer, so an educated (or even random) guess beats an empty answer.

---

## What "detail" means for this exam vs. the rest of this repo

The main [data engineering course](../../README.md) in this repo goes Basic → Advanced → Pro because real engineering work needs internals knowledge. AZ-900 does **not** test internals — it tests recognition and comparison ("what is X," "X vs Y," "which service fits scenario Z"). This course is written at the right altitude for that: thorough on every fact the exam can ask, without engineering-depth tangents the exam will never touch. If you want the *engineering* depth behind any Azure service mentioned here (storage, networking, Databricks, Data Factory), the main repo's folders are cross-linked throughout.

---

## Further Learning — Docs & Videos

**Official Microsoft resources**
- AZ-900 exam page (register, skills outline): https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/
- Official free learning path (Microsoft Learn): https://learn.microsoft.com/en-us/training/courses/az-900t00
- Exam skills measured (study guide PDF): https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-900
- Microsoft Learn practice assessment (free official mock): https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Full AZ-900 course (freeCodeCamp): https://www.youtube.com/results?search_query=az-900+full+course+freecodecamp
- AZ-900 exam cram / crash course: https://www.youtube.com/results?search_query=az-900+exam+cram+john+savill
- John Savill's Azure Fundamentals playlist: https://www.youtube.com/results?search_query=john+savill+az-900+study+cram

---

Start here: **[01 — Cloud Concepts](01_Cloud_Concepts.md)**.
