# Monitoring & Observability — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Fundamentals

**Q1. 🔥 Monitoring vs observability?**
Monitoring watches **known** metrics and fires alerts ("is the known thing broken?"). Observability lets you diagnose **unforeseen** issues — especially data that's wrong despite a green job. You need both.

**Q2. 🔥 What are the three observability signals?**
**Metrics** (numbers over time), **logs** (event records), **traces** (a request's path across steps). Metrics say something's wrong, logs say what, traces say where.

**Q3. 🔥 SLA vs SLO vs SLI?**
**SLI** = the measurement (e.g., % of days data is on time). **SLO** = your internal target (99%). **SLA** = the external promise, often with consequences (data by 7 AM).

**Q4. 🔥 What's the most dangerous type of pipeline failure?**
One that **succeeds but produces stale/wrong/partial data** — invisible to basic monitoring, caught only by data observability (freshness/volume checks).

**Q5. ⭐ How do you avoid alert fatigue?**
Alert on user-visible symptoms, make each alert actionable with the right severity, use trend/baseline thresholds instead of brittle fixed ones, and dedupe/group alerts.

**Q6. 💡 What are MTTD and MTTR?**
Mean Time To **Detect** and Mean Time To **Resolve** an incident. Good observability lowers both.

---

## Azure Monitor & Log Analytics

**Q7. 🔥 How do you monitor Azure data pipelines?**
Enable **diagnostic settings** to send resource logs/metrics to a **Log Analytics workspace**, query with **KQL**, define **alert rules**, and notify via **action groups**; visualize in workbooks/dashboards.

**Q8. 🔥 What is KQL?**
Kusto Query Language — the pipe-based (`|`) query language for Log Analytics/Azure Monitor logs (`where`, `project`, `summarize`, `bin`, `render`).

**Q9. ⭐ Why might your ADF/Databricks logs not appear in Log Analytics?**
**Diagnostic settings weren't enabled** — nothing is routed by default; you must turn it on per resource.

**Q10. ⭐ Metric alert vs log alert?**
Metric alerts fire on numeric thresholds in near-real-time; **log (KQL) alerts** run a scheduled query and fire on its results — better for data checks like "0 rows loaded today."

**Q11. ⭐ What is an action group?**
The reusable definition of who/what is notified when an alert fires — email, SMS, Teams, webhook, Logic App, PagerDuty.

**Q12. 💡 How do you catch a "succeeded but empty" run in Azure?**
A scheduled **log alert** on a KQL query checking row counts/freshness of the target table — job status alone won't reveal it.

---

## Reliability

**Q13. 🔥 How do you make a pipeline safe to rerun?**
**Idempotency** — MERGE/upsert on a business key or partition overwrite (`replaceWhere`) keyed to the run, so retries and backfills never duplicate data.

**Q14. 🔥 A malformed record appears in a 10M-row batch — what do you do?**
**Quarantine** it: route bad rows to a side table, keep processing the good rows, and alert only if the bad-row ratio crosses a threshold. Never fail the whole batch on one row.

**Q15. ⭐ How do you handle transient failures?**
Retries with exponential backoff plus timeouts; escalate to an alert only after retries are exhausted; circuit-break a dependency that's clearly down.

**Q16. ⭐ Why keep a raw Bronze layer, from a reliability angle?**
It's a safety net — reprocess Silver/Gold from Bronze after a logic fix without re-hitting the source system.

**Q17. 💡 Prevention vs recovery — which should you optimize?**
Both, but since failure is inevitable, design for fast, safe **recovery**: rerun-from-failed-task, small idempotent units, deterministic per-run partitions.

**Q18. 💡 What are freshness and completeness SLAs?**
Freshness = data is current by a deadline; completeness = all expected inputs arrived. Both are alerted independently of job success to catch silent staleness/partial loads.

---

## Data Observability

**Q19. 🔥 What is data observability and why does it matter?**
Monitoring the **health of the data** (freshness, volume, schema, quality, lineage) to prevent **data downtime** — periods of missing/stale/wrong data that pipelines report as successful.

**Q20. 🔥 Name the five pillars of data observability.**
Freshness, volume, schema, quality/distribution, and lineage.

**Q21. ⭐ How would you detect a source that silently stopped feeding you?**
A **freshness** alert comparing the latest partition/timestamp against the SLA.

**Q22. ⭐ How do you catch a volume anomaly without false alarms?**
Compare today's row count to a **rolling baseline** (e.g., 7-day average) and alert on large deviation, rather than a fixed threshold.

**Q23. 🔥 A Gold metric is wrong — how do you find the cause and impact?**
**Lineage** (Unity Catalog/Purview): trace **upstream** to the source/job that produced it and **downstream** to the tables/dashboards affected (blast radius).

**Q24. 💡 What tools implement data observability?**
Code assertions, **dbt tests**, **Great Expectations/Soda**, **DLT expectations** for checks; **Monte Carlo/Bigeye/Anomalo** for automated anomaly detection; **Purview/Unity Catalog** for lineage.

**Q25. 💡 What is "data downtime"?**
Any period when data is missing, stale, erroneous, or otherwise untrustworthy — the core thing data observability exists to reduce.

---

## Scenario

**Q26. 🔥 "Your nightly pipeline shows all-green, but the CEO says the dashboard numbers look wrong. Walk me through it."**
Green means the *jobs* ran, not that the *data* is right. Check the data-observability signals: **freshness** (is the latest data actually today's?), **volume** (row count vs baseline — did a source truncate?), **schema** (did a column change, nulling a join?), **distribution/quality** (null spike, unit change, duplicates?). Use **lineage** to trace the suspect metric to its source and the exact job. Fix, add a **check/alert** so this class of failure can't be silent again, and run a blameless post-mortem.

**Q27. 💡 How would you design monitoring for a new critical pipeline from scratch?**
Operational: success/failure + duration-trend alerts, retries, and a failure→alert action group. Data: freshness + completeness SLAs, volume-vs-baseline, schema-drift, and key quality checks — as log/DLT/dbt alerts. Centralize logs in Log Analytics, build a health dashboard, write a runbook, and define the SLO/SLA with stakeholders.

---

## Further Learning
- Back to the [Learning Path](00_Monitoring_Learning_Path.md)
- Related: [Reliability](03_Pipeline_Reliability.md) · [Data Quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) · [Testing & DataOps](../15_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)
