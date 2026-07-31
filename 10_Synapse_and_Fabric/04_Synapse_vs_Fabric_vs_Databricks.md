# Synapse vs Fabric vs Databricks

## Why this note exists

"Which platform would you choose, and why?" is one of the most common **senior** Azure Data Engineer interview questions — and a real decision teams make. The three platforms overlap heavily, and the wrong answer ("Databricks, it's the best") without reasoning is a red flag. This note is the **decision framework**: what each is best at, and how to pick.

These aren't strictly competitors — many real architectures use **two** (e.g. Databricks for engineering + Power BI/Fabric for BI). The skill is matching platform strengths to the org's actual constraints.

---

## The one-paragraph summary

- **[Azure Synapse Analytics](01_Azure_Synapse_Analytics.md)** — mature, PaaS, strong **MPP SQL warehouse**; still everywhere, but **superseded by Fabric** for new builds.
- **[Microsoft Fabric](03_Microsoft_Fabric.md)** — **SaaS**, unified, **Power BI-native**, one Delta lake (OneLake); simplest for Microsoft-centric orgs; newer/maturing.
- **[Databricks](../08_Databricks/01_What_is_Databricks.md)** — best-in-class **Spark/lakehouse**, data engineering + ML, **open and multi-cloud**; the power/control choice.

---

## Side-by-side

| | Synapse | Fabric | Databricks |
|---|---|---|---|
| Delivery model | PaaS (provision pools) | **SaaS** (no infra) | PaaS (managed clusters) |
| Best at | MPP SQL warehouse | Unified analytics + **Power BI** | **Spark / lakehouse / ML** |
| Storage | ADLS (Parquet/Delta) | **OneLake** (Delta-native) | ADLS (Delta) |
| Spark quality | Good | Good | **Best** (Photon, DLT, UC) |
| SQL warehouse | **Strong** (dedicated MPP) | Strong (Warehouse item) | Databricks SQL (good) |
| BI integration | Power BI (connected) | **Power BI built-in (Direct Lake)** | Power BI (connected) |
| Openness / portability | Azure | Microsoft SaaS (open Delta) | **Open, multi-cloud** |
| ML / data science | Basic | Growing | **Strong** (MLflow) |
| Ops burden | Medium (pause pools) | **Lowest** (SaaS) | Medium (clusters) |
| Maturity | **Mature** | Newer | **Mature** |
| Lifecycle | Legacy-forward | **Where MS is investing** | Actively leading |

---

## Decision framework — pick by the deciding factor

| If the deciding factor is… | Lean toward |
|---|---|
| Best-in-class **Spark, data engineering, or ML** | **Databricks** |
| **Multi-cloud** or avoiding Microsoft lock-in | **Databricks** |
| **Power BI-heavy** org, want minimal platform ops | **Fabric** |
| **SaaS simplicity**, one bill, no infrastructure team | **Fabric** |
| A **green-field** Microsoft-native analytics platform | **Fabric** (over Synapse) |
| An **existing** MPP SQL warehouse / mature Synapse estate | **Synapse** (optimize; plan Fabric path) |
| High-concurrency **T-SQL BI warehouse**, SQL-first team | **Synapse** dedicated *or* **Fabric** Warehouse |
| Heavy **streaming + ML + lakehouse** at scale | **Databricks** (+ maybe Fabric/Power BI for BI) |

---

## Common real-world combinations

Platforms coexist more often than they compete:

- **Databricks + Power BI** — engineers build the lakehouse (Delta) in Databricks; analysts consume gold tables in Power BI. The most common enterprise pairing.
- **Databricks + Fabric** — Databricks for engineering/ML; Fabric/OneLake (via shortcuts to the same Delta) for the Power BI serving layer.
- **Synapse → Fabric migration** — existing Synapse estate, gradually moving workloads to Fabric as it matures.
- **Synapse + Databricks** — Synapse dedicated pool as the SQL warehouse, Databricks for Spark engineering (a very common "before Fabric" pattern).

Because all three center on **open Delta**, data can be shared between them without lock-in at the storage layer — which is exactly why mixed architectures work.

---

## Real World Example

A retailer interviewing a data engineer asks: *"We're Microsoft-heavy, Power BI is everywhere, we have a small platform team, but our data scientists need serious ML. What would you build?"* A strong answer: **Fabric as the core** — OneLake for one Delta copy, Data Factory for ingestion, Warehouse for the SQL marts, and **Direct Lake** Power BI for fast, always-fresh dashboards with almost no ops. **But** for the ML workload, add **Databricks** pointing at the *same* Delta data (via shortcuts/OneLake), because Databricks leads on Spark and MLflow. Skip standing up **Synapse** new — it's the platform Fabric replaces. The reasoning (ops constraints + Power BI gravity → Fabric; ML depth → Databricks; open Delta lets them share one copy) is what the interviewer is actually testing.

---
---

# Part 2 — Advanced

## Why "just use Databricks" is the wrong interview answer

Databricks is excellent, but answering every scenario with it ignores the constraints interviewers embed: a tiny team that can't run clusters, an org that lives in Power BI, a mandate to minimize ops, an existing Synapse investment, or a budget shape. The senior signal is **naming the deciding constraint** and choosing accordingly — sometimes that's Fabric's SaaS simplicity or Synapse's existing estate, not Databricks' raw power. Match tool to context, don't recite a favorite.

## The open-Delta thread that ties them together

All three read/write **open Delta on object storage**. This is why they interoperate and why "one copy, many engines" ([lakehouse](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md)) spans platforms: Databricks can write Delta that Fabric reads via a shortcut; Synapse serverless can query Delta that Databricks produced. The strategic evaluation question stays constant across all three: *does it read/write open formats in storage I control, and whose catalog governs it?*

## Lifecycle awareness is a senior differentiator

Knowing *where each platform sits in its lifecycle* matters as much as features: Synapse is mature but **legacy-forward** (Microsoft's roadmap points to Fabric); Fabric is **ascending but maturing**; Databricks is **mature and actively leading**. Recommending a new-build on Synapse dedicated pools in 2025+ signals being a version behind. Factor roadmap direction, not just today's feature grid.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Total cost of ownership beats feature checklists

The platform with the longest feature list rarely wins the real decision — **TCO and team fit do**. Databricks' power is wasted (and its cluster ops a burden) on a five-person Power BI shop that Fabric's SaaS would serve for less total effort. Conversely, forcing a heavy-ML, multi-cloud enterprise onto Fabric to "keep it simple" caps them below what Databricks delivers. Price the *people and ops*, the *duplication avoided*, and the *lock-in*, not just the per-unit compute — the same discipline as the [lake/warehouse/lakehouse TCO](../04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) analysis.

## Migration reality: move workloads, not everything

Synapse→Fabric (or anything→anything) succeeds workload-by-workload with parallel-run and reconciliation, never big-bang. Move new pipelines to the target first, keep BI marts last, and retire the old platform only once trust transfers — the same [migration playbook](../04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) that governs every platform change. Because all three share open Delta, migrations are often "re-point the engine at the same data," which is a genuine advantage to plan around.

## Field-tested gotchas

- **Answering every scenario "Databricks"** — ignores ops/BI/team constraints interviewers plant; name the deciding factor.
- **New-build on Synapse dedicated pools in 2025+** — usually the wrong lifecycle call; weigh Fabric/Databricks.
- **Assuming Fabric matches Databricks Spark/ML** — it doesn't yet; don't over-promise.
- **Ignoring that they share open Delta** — leads to unnecessary copies and missed mixed-architecture options.
- **Feature-grid decisions** — real choices hinge on TCO, team skills, ops appetite, and roadmap direction.

## Interview-grade Q&A

- *Synapse vs Fabric vs Databricks — one line each?* Synapse: mature MPP SQL warehouse platform (being superseded by Fabric). Fabric: SaaS, unified, Power BI-native on OneLake. Databricks: best-in-class open Spark/lakehouse/ML.
- *An org is Power BI-heavy with a small team — which platform?* Fabric — SaaS simplicity, built-in Power BI with Direct Lake, one lake, minimal ops.
- *A team needs top-tier Spark and ML across clouds — which?* Databricks — best Spark (Photon), MLflow, open and multi-cloud.
- *Would you build new on Synapse today?* Generally no for green-field — Fabric is its successor; keep/optimize existing Synapse estates and plan a Fabric path.
- *Why do these platforms coexist rather than replace each other?* They all use open Delta, so a common pattern is Databricks for engineering/ML + Fabric/Power BI for BI, sharing one copy of data.
- *What actually decides the choice?* TCO, team skills, ops appetite, BI gravity, openness/multi-cloud needs, and platform lifecycle — not the raw feature list.

---

## Related Notes

- **Prev:** [Microsoft Fabric](03_Microsoft_Fabric.md) · **Module start:** [Learning Path](00_Learning_Path.md)
- **The platforms:** [Synapse](01_Azure_Synapse_Analytics.md) · [Fabric](03_Microsoft_Fabric.md) · [Databricks](../08_Databricks/01_What_is_Databricks.md)
- **Foundations:** [Lakehouse Architecture](../04_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Data Lake vs Warehouse vs Database](../04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) · [Data Fabric & Architecture Comparison](../02_Databases/Data_Warehousing/04_Data_Fabric_and_Architecture_Comparison.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Fabric vs Synapse (Microsoft guidance): https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview
- Databricks vs Fabric positioning: https://www.databricks.com/product/comparison

**Videos**
- Fabric vs Synapse vs Databricks: https://www.youtube.com/results?search_query=fabric+vs+synapse+vs+databricks
- Microsoft Fabric vs Databricks: https://www.youtube.com/results?search_query=microsoft+fabric+vs+databricks
