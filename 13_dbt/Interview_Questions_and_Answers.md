# dbt — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Fundamentals

**Q1. 🔥 What is dbt and what problem does it solve?**
A SQL-based transformation framework that brings software engineering — dependency ordering, materialization, testing, docs, and lineage — to warehouse transformations, replacing fragile, untested, undocumented hand-run SQL scripts.

**Q2. 🔥 Where does dbt fit in ELT?**
It's the **T**. Data is already extracted and loaded (raw) into the warehouse; dbt transforms it **in place** using the warehouse's compute.

**Q3. 🔥 Does dbt have its own processing engine?**
No — it **compiles SQL and pushes it down** to the underlying platform (Databricks, Fabric, Synapse, Snowflake, BigQuery), which does the work.

**Q4. ⭐ dbt Core vs dbt Cloud?**
Core is the free, open-source CLI/engine. Cloud is a hosted layer adding a scheduler, web IDE, docs hosting, CI, and RBAC.

**Q5. ⭐ What is a dbt model?**
A single `.sql` file containing one `SELECT`; dbt wraps it in the right DDL and the filename becomes the resulting table/view.

**Q6. 💡 What is "analytics engineering"?**
Applying software practices — version control, modularity, testing, documentation — to analytics transformations; the discipline dbt popularized.

---

## Models, refs & materializations

**Q7. 🔥 What does `ref()` do, and why not hardcode table names?**
`ref()` declares a dependency (so dbt builds in the correct order) **and** resolves to the environment-correct fully-qualified name, giving free dev/prod portability. Hardcoding breaks across environments and hides dependencies.

**Q8. 🔥 `source()` vs `ref()`?**
`source()` references raw loaded tables (declared in a sources YAML); `ref()` references other dbt models.

**Q9. 🔥 Name the materializations and when to use each.**
**View** (default — cheap, always fresh), **table** (rebuilt each run — for expensive logic), **incremental** (only new/changed rows — for large fact tables), **ephemeral** (inlined as a CTE — reusable logic without its own object).

**Q10. ⭐ How does an incremental model work?**
First run builds everything; later runs use `is_incremental()` to filter to new rows and MERGE on the `unique_key`, avoiding full rebuilds.

**Q11. ⭐ What are staging / intermediate / marts?**
The standard dbt layering: `stg_` (clean per source), `int_` (business logic), `fct_`/`dim_` (final marts) — mirrors the medallion Bronze/Silver/Gold pattern.

**Q12. 💡 How does dbt determine build order?**
It compiles the `ref()`/`source()` graph into a **DAG** and runs models in dependency order.

**Q13. 💡 What do the `+` selectors do?** 
Graph selection: `model+` = the model and everything **downstream**; `+model` = the model and everything **upstream** — used to rebuild only what's affected.

---

## Tests & documentation

**Q14. 🔥 What testing does dbt provide out of the box?**
Generic tests declared in YAML — **`unique`, `not_null`, `relationships`, `accepted_values`** — plus custom **singular tests** (a SELECT that returns rows only on failure).

**Q15. ⭐ What is the `relationships` test?**
A referential-integrity check that every value in a column exists in a referenced model/column — enforcing FK-like integrity the warehouse doesn't.

**Q16. ⭐ How do you test an arbitrary business rule?**
A singular test: write a query that returns rows **only when the rule is violated**; the test fails if any rows come back.

**Q17. 🔥 How does dbt help with documentation and lineage?**
`dbt docs generate` builds a searchable docs website and an **auto-generated lineage DAG** from `ref()`/`source()` — always in sync with the code.

**Q18. 💡 What is `dbt source freshness`?**
A check that raw sources have loaded within warn/error thresholds — dbt's built-in **freshness** monitoring.

**Q19. 💡 How does dbt fit into CI/CD?**
Run `dbt build` (run + test) in the pipeline so a pull request that would break data quality **fails before merge**.

---

## Snapshots, seeds & macros

**Q20. 🔥 How does dbt implement SCD Type 2?**
**Snapshots**: `dbt snapshot` tracks changes (timestamp or check strategy) and maintains `dbt_valid_from`/`dbt_valid_to`, closing old rows and inserting new versions automatically.

**Q21. ⭐ timestamp vs check snapshot strategy?**
`timestamp` uses a reliable source `updated_at` column; `check` compares specified columns run-to-run when no trustworthy timestamp exists.

**Q22. ⭐ What are seeds for?**
Loading **small, static** reference CSVs from the repo as tables (country codes, mappings) — not for real source data.

**Q23. ⭐ What are macros?**
Reusable Jinja-templated SQL functions that keep transformations DRY — write logic once, use it across models.

**Q24. 💡 Why use packages like dbt-utils / dbt-expectations?**
Prebuilt, tested macros and tests (surrogate keys, pivots, date spines, range/row-count checks) so you don't rewrite common patterns.

**Q25. ⭐ What does `dbt build` do?**
Runs seeds, models, snapshots, and tests together in dependency order — the production one-command lifecycle.

---

## Azure & modern stack

**Q26. 🔥 What does dbt need to run, and how does it connect?**
A SQL compute engine, connected via an **adapter** (`dbt-databricks`, `dbt-fabric`, `dbt-snowflake`, …); dbt pushes compiled SQL down to it.

**Q27. 🔥 How does dbt work with Databricks?**
Via `dbt-databricks`, running models on a SQL Warehouse/cluster and materializing **Delta** tables (incrementals compile to `MERGE`), governed by Unity Catalog.

**Q28. 🔥 dbt vs PySpark — when each?**
dbt for SQL-based in-warehouse marts with testing/docs; PySpark for complex/custom/non-SQL or ML-scale processing. Commonly combined — Spark for ingestion/Bronze-Silver, dbt for Gold marts.

**Q29. ⭐ How do you schedule dbt?**
dbt Cloud's scheduler, or an orchestrator — Airflow, ADF, or a Databricks Workflows **dbt task**. dbt transforms; the orchestrator schedules.

**Q30. 💡 Where does dbt sit in the modern data stack?**
The transformation + testing + documentation layer between raw-loaded data and BI, orchestrated externally and governed by a catalog/observability layer.

---

## Scenario

**Q31. 💡 "Your Gold layer is untested SQL nobody documented. How does dbt help?"**
Reimplement the transforms as dbt models with `ref()` (auto ordering + lineage), add `unique`/`not_null`/`relationships` tests and source freshness, write model/column descriptions for auto-docs, use snapshots for any SCD2 dimensions, and run `dbt build` in CI so quality is enforced on every change — turning fragile scripts into a tested, documented, version-controlled data product.

---

## Further Learning
- Back to the [Learning Path](00_dbt_Learning_Path.md)
- Related: [ETL vs ELT](../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) · [Data Quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) · [Testing & DataOps](../14_Testing_and_DataOps/00_Testing_and_DataOps_Learning_Path.md)
