# Power BI (for Data Engineers) — Interview Questions

## Overview
Power BI is the serving/BI layer. A DE isn't expected to be a full BI dev, but must know connectivity modes, star-schema modeling, DAX basics, refresh, and how Power BI consumes the Gold layer / Synapse.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | Import vs DirectQuery vs Live Connection? | 🔴 | ★★★★★ |
| 2 | Why a star schema for Power BI models? | 🟡 | ★★★★★ |
| 3 | DAX vs Power Query (M)? | 🟡 | ★★★★☆ |
| 4 | Scheduled refresh & data gateway? | 🟡 | ★★★★☆ |
| 5 | How does Power BI connect to Synapse/Databricks? | 🟡 | ★★★★☆ |
| 6 | Row-Level Security (RLS)? | 🔴 | ★★★☆☆ |
| 7 | Aggregations / composite models? | 🔴 | ★★★☆☆ |
| 8 | Performance tuning a slow report? | 🔴 | ★★★★☆ |

## Key Answers
- **Q1 (key):** **Import** = data cached in Power BI (fast, needs refresh, size limits). **DirectQuery** = queries the source live (fresh, no import, slower, pushes load to source). **Live Connection** = to a semantic model/AAS. Choose by freshness vs performance vs data size.
- **Q2:** Star schema (fact + denormalized dimensions) makes DAX simpler and faster and matches the model Power BI's engine (VertiPaq) optimizes for — so serve **Gold star-schema** tables.
- **Q5:** Connect to **Synapse/Databricks SQL** via native connectors; use DirectQuery for large/fresh data, Import for smaller curated marts.
- **Q8:** Reduce model size, star schema, avoid heavy DAX/bidirectional filters, pre-aggregate in the Gold layer, use aggregations, Import over DirectQuery where feasible.

## Scenario Questions
- **"Reports must show near-real-time data on a huge table."** DirectQuery to Synapse/Databricks SQL (or composite with aggregations).
- **"Report is slow."** Push aggregation to Gold, star-schema the model, trim columns, Import mode.
- **"Users should only see their region's data."** **Row-Level Security** roles.

## Quick Revision
- ✔ **Import** (fast/cached) vs **DirectQuery** (live/slower) vs **Live**
- ✔ Serve **star-schema Gold** tables; VertiPaq loves star
- ✔ **Power Query (M)** = transform on load; **DAX** = measures/calc
- ✔ Refresh via **scheduled refresh + gateway** (for on-prem/VNet)
- ✔ **RLS** for per-user data security
- ✔ Tune: pre-aggregate + star + trim + Import

## Common Mistakes
- Snowflaked/normalized models (slow DAX).
- DirectQuery on unoptimized sources (slow reports).
- Doing transformations in Power BI that belong in the Gold layer.

## Senior-Level
Seniors design the **Gold semantic layer** as star schema so BI is fast, pick connectivity mode by freshness/size, implement RLS, and push heavy transforms upstream — treating Power BI as a thin serving layer over the lakehouse/warehouse.

## Related Topics
Data Warehousing, Azure Synapse, Delta Lake, Lakehouse
