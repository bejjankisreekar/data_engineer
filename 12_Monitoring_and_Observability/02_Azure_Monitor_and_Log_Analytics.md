# Azure Monitor & Log Analytics

## What is Azure Monitor?

Azure Monitor is Azure's **built-in, platform-wide monitoring service**. Nearly every Azure resource — ADF, Databricks, Storage, Azure SQL, Event Hubs — emits **metrics** and can send **logs** to it. **Log Analytics** is the store + query engine underneath, and **KQL** (Kusto Query Language) is how you ask it questions.

Analogy: Azure Monitor is the **central security office** of a large building. Every door, camera, and sensor (each Azure resource) reports to it; Log Analytics is the archive of all those recordings; KQL is how the guard searches the footage for "show me every failed entry at the east door last night."

---

## The pieces

| Piece | Role |
|---|---|
| **Metrics** | Numeric time-series, near-real-time (CPU, pipeline runs, throughput) |
| **Logs** | Rich, queryable event records sent to a **Log Analytics workspace** |
| **Diagnostic settings** | The switch that routes a resource's logs/metrics to Log Analytics (or Storage/Event Hubs) |
| **KQL** | The query language for logs |
| **Alerts** | Rules that fire actions when a metric/log condition is met |
| **Action groups** | Who/what gets notified (email, SMS, Teams, webhook, Logic App, PagerDuty) |
| **Workbooks / dashboards** | Visual monitoring views |

---

## Step 1 — Turn on diagnostics (nothing is logged by default)

For each resource (ADF, Databricks, Storage…), create a **diagnostic setting** that sends logs and metrics to your **Log Analytics workspace**. Without this, the rich logs simply aren't collected. This is the #1 practical gotcha: "why don't I see my ADF logs?" → diagnostics weren't enabled.

---

## Step 2 — Query with KQL

KQL reads like a pipeline of `|` operators — familiar if you know [SQL](../02_Databases/SQL/01_What_is_SQL.md) or PySpark chaining:

```kusto
// Failed ADF pipeline runs in the last 24h
ADFPipelineRun
| where Status == "Failed"
| where TimeGenerated > ago(24h)
| project TimeGenerated, PipelineName, Parameters, ErrorMessage
| order by TimeGenerated desc
```

```kusto
// Databricks job duration trend — spot a job slowly getting slower
DatabricksJobs
| where ActionName == "runSucceeded"
| summarize avg(DurationMs) by JobName, bin(TimeGenerated, 1d)
| render timechart
```

Core KQL verbs: `where` (filter), `project` (select), `summarize` (group/aggregate), `bin` (bucket time), `join`, `render` (chart). You don't need deep KQL for a DE role, but reading and writing basic queries is expected.

---

## Step 3 — Build alert rules

An alert = **a condition** + **an action group**:

- **Metric alert** — "ADF failed-run count > 0 in 5 min" or "cluster CPU > 90% for 15 min."
- **Log (KQL) alert** — run a KQL query on a schedule; fire if it returns rows (e.g., the failed-runs query above).
- **Action group** — email the team, post to Teams, trigger a Logic App/webhook, or page via PagerDuty.

```kusto
// Log alert: no rows loaded into the sales table today (a silent failure!)
sales_load_log_CL
| where TimeGenerated > startofday(now())
| summarize rows = sum(RowsLoaded_d)
| where rows == 0        // fires the alert when true
```

That last example catches the dangerous "green but empty" case that operational monitoring misses.

---

## Step 4 — Dashboards & workbooks

Assemble the key views into a **Workbook** or **Azure Dashboard**: pipeline success rate, job durations, cost trend, freshness of key tables. A single "data platform health" board that the team checks each morning is a strong, real deliverable.

---

## Service-specific monitoring (still feeds Azure Monitor)

- **ADF Monitor** — visual run history; rerun from failed activity; also exports to Log Analytics.
- **Databricks** — the Jobs UI, the Spark UI (stages/tasks/shuffle for [performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)), and cluster/audit logs to Log Analytics.
- **Cost** — **Azure Cost Management** + budgets/alerts ([Cost](../15_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md)).

The unifying idea: individual services have their own UIs, but you **centralize** into Azure Monitor so one place answers "is the platform healthy?"

---

## Interview-grade Q&A

- *How do you monitor Azure data pipelines?* Route resource logs/metrics via **diagnostic settings** to a **Log Analytics workspace**, query with **KQL**, and set **alert rules** with **action groups** for notifications; visualize in workbooks.
- *What is KQL?* Kusto Query Language — the pipe-based query language for Log Analytics/Azure Monitor logs.
- *Why don't you see logs by default?* Diagnostic settings must be enabled per resource to send logs to Log Analytics.
- *Metric alert vs log alert?* Metric alerts fire on numeric thresholds in near-real-time; log alerts run a KQL query on a schedule and fire on its result.
- *How do you catch a "succeeded but produced no data" run?* A scheduled **log alert** on a KQL query checking row counts/freshness — operational status alone won't catch it.
- *What's an action group?* The reusable definition of who/what gets notified when an alert fires.

---

## Further Learning — Docs & Videos
- Azure Monitor overview: https://learn.microsoft.com/azure/azure-monitor/overview
- KQL tutorial: https://learn.microsoft.com/azure/data-explorer/kusto/query/tutorials/learn-common-operators
- Monitor ADF with Azure Monitor: https://learn.microsoft.com/azure/data-factory/monitor-using-azure-monitor
- Video — KQL for beginners: https://www.youtube.com/results?search_query=kql+kusto+query+language+tutorial
