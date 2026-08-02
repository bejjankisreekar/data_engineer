# Portfolio & GitHub Presentation

## Why this note exists

You built three real pipelines. If a recruiter can't understand them in **90 seconds** of skimming your GitHub, they didn't happen. This note turns your projects into a **portfolio that gets interviews** and **résumé bullets that survive follow-up questions**.

Analogy: the pipeline is the meal; this is the plating. The same food wins or loses depending on how it's presented.

---

## The project README is 80% of the impact

A hiring manager reads the **README**, not your code. Every project repo needs one with this exact skeleton:

```markdown
# NorthWind Retail — Azure Medallion Pipeline

One-line pitch: *Batch + streaming lakehouse that turns raw retail data into a
finance dashboard, built on ADLS, Databricks, Delta, and Power BI.*

## Architecture
![architecture](docs/architecture.png)   ← a real diagram, not words

## What it does
- Ingests daily order files + a live order stream
- Bronze → Silver → Gold medallion with SCD2 customer dimension
- Orchestrated nightly by Azure Data Factory, monitored with alerts
- Serves a Power BI sales dashboard

## Tech stack
ADLS Gen2 · Azure Data Factory · Databricks (PySpark) · Delta Lake ·
Event Hubs · Power BI · Key Vault · GitHub Actions (CI)

## How to run
1. ... (setup steps)
2. ...

## Results / screenshots
![dashboard](docs/dashboard.png)

## What I learned / hardest problem
Handling duplicate order events with an idempotent MERGE + watermark.
```

Non-negotiables: **an architecture diagram**, **screenshots of the result**, and a **"hardest problem"** section (interviewers jump straight to it).

---

## Make the repo itself look senior

| Signal | How |
|---|---|
| **Clean structure** | The layout from [01 — Setup](01_Project_Setup_and_Prerequisites.md) — `notebooks/`, `src/`, `tests/`, `conf/` |
| **No secrets committed** | `.gitignore` for `.env`/keys; if you ever leak one, rotate it and say so |
| **Real commit history** | Logical commits with clear messages, not one "final upload" ([Git](../07_DevOps/Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md)) |
| **Tests exist** | Even a few `chispa`/pytest tests signal maturity ([Testing](../15_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)) |
| **CI badge** | A GitHub Actions workflow that lints + tests → green badge in the README ([CI/CD](../07_DevOps/CICD/00_CICD_Learning_Path.md)) |
| **Reproducible** | Someone else could run it from the README |

---

## Résumé bullets that survive follow-ups

Weak: *"Built data pipelines using Azure."*
Strong (**action + tech + scale + result**):

- *"Built a medallion lakehouse (ADLS + Databricks + Delta) processing ~5M daily order rows, implementing SCD2 dimensions via Delta MERGE, cutting the finance report refresh from 3 hours to 15 minutes."*
- *"Designed a Structured Streaming pipeline on Event Hubs with checkpointing and watermarking for exactly-once, powering a live revenue dashboard at ~1-minute latency."*
- *"Orchestrated ingestion with a metadata-driven ADF pipeline (incremental watermark loads + failure alerting), replacing 12 per-table pipelines with one parameterized flow."*

Rule: **never write a bullet you can't defend for five follow-up questions.** If you didn't do it, don't claim it.

---

## The 2-minute project walkthrough (rehearse this)

Interviews almost always open with *"tell me about a project."* Structure your answer:

1. **Context (15s)** — the business problem ("finance needed a daily sales view; data came as nightly files + a live stream").
2. **Architecture (30s)** — the medallion diagram, naming the service at each hop.
3. **Your decisions (45s)** — one or two real choices: *why* Delta, *how* you did SCD2, *how* you made re-runs idempotent.
4. **A problem you hit (20s)** — duplicate events → watermark + MERGE.
5. **Result (10s)** — the dashboard, the time saved, what you'd improve next.

Practice it out loud until it's 2 minutes and natural. This single skill wins more offers than any additional certificate.

---

## Beyond the three projects (stretch)

Once the core three are solid, one differentiator each:

- **dbt** on top of Gold for tested, documented transformations ([dbt](../14_dbt/00_dbt_Learning_Path.md)).
- **CI/CD** deploying notebooks/ADF across dev→prod ([DataOps](../15_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)).
- **Cost writeup** — a short doc on how you sized clusters and cut spend ([Cost](../16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md)).
- **A system-design doc** — how you'd scale this to 100× data ([System Design](../18_System_Design/00_System_Design_Learning_Path.md)).

Depth on one project beats breadth across ten half-built ones.

---

## Portfolio checklist

- [ ] Each project repo has a README with diagram, screenshots, and a "hardest problem"
- [ ] No secrets in any repo; `.gitignore` in place
- [ ] Clean structure, real commit history, at least a few tests
- [ ] 3 defensible résumé bullets (action + tech + scale + result)
- [ ] A rehearsed 2-minute walkthrough for each project
- [ ] A pinned "best" repo on your GitHub profile

## Further Learning — Docs & Videos
- How to write a good README: https://www.makeareadme.com/
- Data engineering portfolio tips: https://www.youtube.com/results?search_query=data+engineering+portfolio+projects+github
- Résumé for data engineers: https://www.youtube.com/results?search_query=data+engineer+resume+projects+tips
