# Data Observability

## What is data observability?

Data observability is monitoring the **health of the data itself**, not just the pipelines that move it. A job can finish "successfully" while the data it produced is **stale, half-missing, or subtly wrong**. Data observability is the practice — and the tools — that catch those silent problems.

Analogy: operational monitoring checks that the **water pipes** are running (pressure's fine, no leaks). Data observability checks that the **water is safe to drink** (not contaminated, not brown, actually flowing). A green pipe carrying bad water is exactly the failure basic monitoring can't see — and it's the one that erodes trust in the whole data platform.

---

## Why it's the frontier of data engineering

The most damaging incidents are **"data downtime"** — periods when data is wrong, missing, or stale — because:
- The pipeline **reported success**, so nobody was alerted.
- A dashboard showed **plausible-but-wrong** numbers, and someone made a decision on them.
- By the time it's noticed (often by an executive), trust is already damaged and the root cause is buried days back.

Preventing data downtime is increasingly a named responsibility in senior DE roles.

---

## The five pillars of data observability

| Pillar | The question | Example failure it catches |
|---|---|---|
| **Freshness** | Is the data up to date? | Sales table stuck on yesterday — upstream feed silently stopped |
| **Volume** | Is the amount of data as expected? | Row count dropped 60% — a source file was truncated |
| **Schema** | Did the structure change? | A source renamed/dropped a column — downstream joins now null |
| **Quality / Distribution** | Are the *values* sane? | Nulls spiked, a currency field flipped units, IDs duplicated |
| **Lineage** | Where did it come from / what's affected? | Trace a bad Gold number back to the exact source and job |

Memorize these five — "what would you monitor about the *data*?" is a direct interview question, and this table is the answer.

---

## Implementing checks (you can start with plain code)

You don't need a fancy tool to begin. Assertions in the pipeline cover a lot:

```python
# Freshness
latest = spark.read.format("delta").load(gold).agg(max("event_date")).collect()[0][0]
assert latest == expected_date, f"STALE: latest={latest}, expected={expected_date}"

# Volume — compare to a rolling baseline, not a fixed number
today = df.count()
baseline = read_avg_count_last_7_days()
assert today > baseline * 0.5, f"VOLUME DROP: {today} vs baseline {baseline}"

# Schema — detect drift
assert set(df.columns) == expected_columns, f"SCHEMA CHANGED: {set(df.columns) ^ expected_columns}"

# Quality
null_rate = df.filter(col("customer_id").isNull()).count() / today
assert null_rate < 0.01, f"NULL SPIKE in customer_id: {null_rate:.1%}"
```

Failing (or better, **alerting**) on these turns silent corruption into a visible, actionable signal. Pair with [Data Quality](../05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) expectations and quarantine.

---

## Tools that formalize it

| Tool | Niche |
|---|---|
| **Great Expectations / Soda** | Declarative data quality/expectation tests in pipelines ([Testing](../15_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)) |
| **dbt tests** | Built-in `not_null`, `unique`, `relationships`, custom tests ([dbt](../14_dbt/03_Tests_and_Documentation.md)) |
| **Delta Live Tables expectations** | `@dlt.expect` quality gates inside the pipeline ([DLT](../08_Databricks/05_Delta_Live_Tables.md)) |
| **Monte Carlo / Bigeye / Anomalo** | ML-based anomaly detection across all five pillars, automatically |
| **Microsoft Purview** | Lineage + cataloging across Azure ([Governance](../05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)) |

Start with code/dbt/DLT checks; graduate to a dedicated platform when scale and criticality justify it.

---

## Lineage — the "what's affected?" pillar

**Lineage** maps how data flows: source → Bronze → Silver → Gold → dashboard. It answers two priceless questions during an incident:
- **Upstream (root cause):** "This Gold number is wrong — which source and job produced it?"
- **Downstream (blast radius):** "This source is broken — which tables and dashboards are affected, and who do I warn?"

**Unity Catalog** (Databricks) and **Purview** (Azure) capture lineage automatically. In interviews, lineage is the answer to *"a metric is wrong — how do you find the cause and the impact?"*

---

## Interview-grade Q&A

- *What is data observability, and how does it differ from pipeline monitoring?* It monitors the **health of the data** (freshness, volume, schema, quality, lineage), catching "green job, bad data" cases that operational monitoring misses.
- *Name the five pillars.* Freshness, volume, schema, quality/distribution, lineage.
- *What is "data downtime"?* Periods when data is missing, stale, or wrong — often invisible because the job succeeded.
- *How would you detect a source that silently stopped?* A **freshness** check/alert on the latest partition timestamp vs an SLA.
- *How do you catch a volume anomaly?* Compare today's row count to a rolling baseline and alert on a large deviation, not a fixed threshold.
- *A Gold metric is wrong — how do you find the cause and blast radius?* **Lineage** (Unity Catalog/Purview) to trace upstream to the source/job and downstream to affected tables/dashboards.
- *Which tools?* dbt tests, Great Expectations/Soda, DLT expectations for checks; Monte Carlo/Bigeye for automated anomaly detection; Purview/Unity Catalog for lineage.

---

## Further Learning — Docs & Videos
- The five pillars of data observability (Monte Carlo): https://www.montecarlodata.com/blog-what-is-data-observability/
- Great Expectations: https://docs.greatexpectations.io/docs/
- Unity Catalog lineage: https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/data-lineage
- Video — data observability & data downtime: https://www.youtube.com/results?search_query=data+observability+five+pillars
