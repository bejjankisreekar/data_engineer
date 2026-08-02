# Monitoring Fundamentals

## What is monitoring?

Monitoring is **continuously watching your systems and data so you learn about problems from your tools, not from an angry stakeholder.** It's collecting signals, defining what "healthy" means, and getting **alerted** when reality diverges.

Analogy: monitoring is the **dashboard and warning lights in a car**. You don't stare at the engine; you glance at the speed, fuel, and temperature, and a red light tells you *before* the engine seizes. A pipeline without monitoring is a car with the dashboard covered — you only learn there's a problem when you're stranded on the highway (the CEO's dashboard is blank).

---

## The three pillars of observability signals

| Signal | What it is | Example in data |
|---|---|---|
| **Metrics** | Numbers over time | Rows processed, job duration, RU/DBU used, error count |
| **Logs** | Timestamped event records | "Task X failed: connection timeout" |
| **Traces** | The path of a request across steps | A record's journey Bronze→Silver→Gold |

Metrics tell you **something is wrong** (duration doubled); logs tell you **what** ("out of memory"); traces tell you **where** (the Silver join stage). Together they turn "it's broken" into "here's exactly why."

---

## SLA, SLO, SLI — the reliability vocabulary

| Term | Meaning | Data example |
|---|---|---|
| **SLI** (Indicator) | The measurement | "% of days the sales table is ready by 6 AM" |
| **SLO** (Objective) | Your internal target | "99% of days ready by 6 AM" |
| **SLA** (Agreement) | The promise to stakeholders (often with consequences) | "Data available by 7 AM on business days" |

For data engineers the headline SLA is usually **freshness/timeliness** ("data is ready by X") and **completeness** ("all expected data arrived"). Framing your work in SLIs/SLOs signals senior maturity in interviews.

---

## What to actually monitor in a data platform

**Operational (did it run?)**
- Job/pipeline success & failure, duration and trend (a job creeping from 20→90 min is a warning)
- Retries and their frequency
- Cluster/compute health and cost ([Cost](../16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md))
- Queue depth / lag for streaming ([Streaming](../09_Streaming/01_Streaming_Fundamentals.md))

**Data (is it right?)** — covered in [Data Observability](04_Data_Observability.md)
- Freshness (is today's data here?)
- Volume (row counts within expected range?)
- Schema (did columns/types change?)
- Quality (nulls, duplicates, out-of-range) ([Data Quality](../05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md))

---

## Good alerting (the hard part)

Alerts are only useful if people trust them. The failure mode is **alert fatigue** — so many noisy alerts that everyone ignores them, including the real one.

Principles:
- **Alert on symptoms users feel** (the dashboard is stale), not every internal wobble.
- **Actionable** — every alert should tell the responder what to check/do.
- **Right severity** — page a human only for things that need a human *now*; route the rest to a channel/ticket.
- **Tunable thresholds** — "row count dropped >30% vs the 7-day average," not a brittle fixed number.
- **Deduplicate & group** — one incident shouldn't fire fifty alerts.

A good alert answers: *what broke, how bad, and what do I do?*

---

## The on-call mindset

Real data teams rotate **on-call**. What matters:
- **Runbooks** — documented "if X alert fires, do Y" so any engineer can respond.
- **Blameless post-mortems** — after an incident, fix the *system* (add a check, a retry, an alert), not the person.
- **MTTD / MTTR** — Mean Time To **Detect** and to **Resolve**; observability lowers both.

You don't need to run on-call to answer *"how would you know if your pipeline broke overnight, and what would you do?"* — that question is asking for this mindset.

---

## Interview-grade Q&A

- *Monitoring vs observability?* Monitoring watches known metrics/alerts ("is the known thing broken?"); observability lets you diagnose unforeseen problems, especially bad-but-green data.
- *The three signal types?* Metrics (numbers over time), logs (event records), traces (path across steps).
- *SLA vs SLO vs SLI?* SLI = the measurement, SLO = your internal target, SLA = the external promise (often with penalties).
- *What's the most dangerous kind of failure?* A job that **succeeds but produces wrong/stale data** — invisible to basic monitoring, caught only by data observability.
- *How do you avoid alert fatigue?* Alert on user-visible symptoms, make alerts actionable with the right severity, use trend-based thresholds, and dedupe.
- *How would you know a pipeline broke overnight?* Failure alerts + freshness/volume checks with notifications, plus a dashboard of run history and SLAs.

---

## Further Learning — Docs & Videos
- SRE: SLIs, SLOs, SLAs: https://sre.google/sre-book/service-level-objectives/
- Azure Monitor alerts: https://learn.microsoft.com/azure/azure-monitor/alerts/alerts-overview
- Video — monitoring & alerting concepts: https://www.youtube.com/results?search_query=monitoring+alerting+sli+slo+sla+explained
