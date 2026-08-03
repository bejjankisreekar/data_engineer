# Power BI for Engineers — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Focused on what a **data engineer** (not a BI analyst) is asked.

---

## Fundamentals

**Q1. 🔥 What's the difference between a semantic model and a report?**
The **semantic model** (dataset) is the data + relationships + measures; the **report** is the visuals built on it. Engineers own/influence the model and the Gold layer beneath it.

**Q2. 🔥 Where should heavy transformation happen — Power Query or upstream?**
**Upstream** in the pipeline (Spark/dbt/Gold). Power Query is for light last-mile shaping; pushing real ETL into the report is an anti-pattern that makes refreshes slow and logic un-shareable.

**Q3. ⭐ What is Power BI refresh and why does an engineer care?**
For Import models it reloads data on a schedule — effectively a data job that must be **orchestrated after the Gold load** and **monitored** (a failed refresh = stale dashboards).

**Q4. ⭐ Desktop vs Service vs Gateway?**
Desktop builds models/reports; the Service publishes/shares/schedules refresh and manages access; a Gateway bridges the Service to on-prem/private sources.

---

## Modeling

**Q5. 🔥 Why is star schema recommended for Power BI?**
Its VertiPaq engine is optimized for it — a central fact with surrounding dimensions gives fast, unambiguous filtering. Flat or snowflake models are slower and harder to work with.

**Q6. 🔥 How does your Gold-layer design affect BI performance?**
Directly — a clean star schema with surrogate keys and a date dimension makes reports fast; a flat or normalized Gold makes them slow and error-prone. BI performance is largely decided upstream.

**Q7. ⭐ Cardinality and filter direction — what's the norm?**
One-to-many relationships with single-direction filtering (dimension filters fact). Bidirectional filtering causes ambiguity and performance issues — avoid by default.

**Q8. ⭐ Why does an engineer provide a dedicated Date dimension?**
Time intelligence (YTD, YoY, same-period-last-year) requires a proper Date table marked in the model.

**Q9. 💡 What makes a semantic model fast?**
Star schema, narrow tables (drop unused columns), integer surrogate keys, correct types, single-direction relationships, and aggregates pre-computed in Gold — mostly upstream decisions.

---

## Storage modes

**Q10. 🔥 Import vs DirectQuery?**
**Import** copies data into in-memory VertiPaq (fastest queries, needs scheduled refresh, size limits). **DirectQuery** sends queries live to the source (always current, handles huge data, slower + loads the source).

**Q11. 🔥 What is Direct Lake?**
A **Fabric** mode that reads Delta/Parquet directly from OneLake into memory — Import-like speed with live data, no import or query translation and no refresh job. Ideal for lakehouse serving.

**Q12. ⭐ When would you choose DirectQuery, and what then becomes your concern?**
When data is too big to import or must be real-time. Then the **source's** performance and cost matter, because every visual queries it live — so partition/prune/optimize the source.

**Q13. 💡 What is a composite model?**
A mix of Import and DirectQuery tables in one model — flexibility (e.g., import small dims, DirectQuery a huge fact) at the cost of complexity.

---

## DAX (engineer's subset)

**Q14. 🔥 Measure vs calculated column?**
A **measure** computes at query time responding to filter context (aggregations like Total Sales); a **calculated column** computes per row at refresh and is stored. Prefer measures for aggregations; prefer computing per-row attributes in **Gold**.

**Q15. ⭐ What is filter context?**
The filters (slicers, rows/columns, visual) under which a measure evaluates — why the same measure shows different numbers in different visuals.

**Q16. ⭐ What does CALCULATE do?**
Modifies a measure's filter context (e.g., force `country = "US"`) — the key DAX function.

**Q17. 💡 As an engineer, where should calculations live?**
Push reusable/heavy/shared logic to **Gold** (single-sourced, consistent for all consumers); use DAX measures only for dynamic, filter-responsive aggregations.

---

## Serving & governance

**Q18. 🔥 How does data get from the lakehouse to Power BI?**
Connect Power BI to the Gold layer via the platform connector — Databricks SQL Warehouse, Fabric OneLake (Direct Lake), or Synapse — in Import, DirectQuery, or Direct Lake mode.

**Q19. ⭐ How do you ensure dashboards don't show half-loaded data?**
Trigger the Power BI refresh only **after** the Gold load succeeds (orchestrated via ADF/Databricks/Fabric or the Power BI API), and monitor refresh failures.

**Q20. ⭐ What makes a good Gold-to-BI handoff?**
Star-schema Gold with surrogate keys and a date dimension, pre-computed aggregates, narrow well-sized (`OPTIMIZE`d) Delta tables, and a reliable, monitored refresh.

**Q21. 💡 What is Row-Level Security (RLS)?**
Semantic-model rules that filter data per user (e.g., a regional manager sees only their region) — a governance control engineers help define.

---

## Scenario

**Q22. 🔥 "Your finance dashboard is slow. As the engineer, what do you check?"**
Model: is Gold a **star schema** or a bloated flat/snowflake table? Are there unused high-cardinality columns? Bidirectional relationships? Storage mode: is it DirectQuery hitting an unoptimized source (fix with partitioning/`OPTIMIZE`), or an oversized Import model (trim columns, pre-aggregate in Gold)? Are heavy calculations done in DAX that should be pre-computed in Gold? Usually the fix is **upstream** — reshape Gold into a clean star and pre-aggregate — not in the report.

**Q23. 💡 "Design the serving layer for a Fabric lakehouse."**
Land clean **star-schema Delta Gold** tables in the Fabric Lakehouse (surrogate keys, date dimension, pre-computed measures, `OPTIMIZE`d files); build a semantic model on them in **Direct Lake** mode for Import-speed live serving with no refresh job; add RLS for per-user filtering; certify the dataset so analysts build on the governed model; monitor for freshness.

---

## Further Learning
- Back to the [Learning Path](00_Power_BI_Learning_Path.md)
- Related: [Dimensional Modeling](../02_Databases/Data_Modeling/03_Dimensional_Modeling.md) · [Synapse & Fabric](../10_Synapse_and_Fabric/00_Learning_Path.md) · [Cost & Performance](../16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md)
