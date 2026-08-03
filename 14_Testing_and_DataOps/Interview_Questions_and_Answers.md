# Testing & DataOps — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Testing pipelines

**Q1. 🔥 How do you unit-test a PySpark pipeline?**
Extract transformations into pure `DataFrame -> DataFrame` functions, then test them with `pytest` + `chispa` on tiny in-memory DataFrames using arrange/act/assert. `chispa.assert_df_equality` compares schema + rows.

**Q2. 🔥 Why separate transformation logic from I/O?**
So the logic is testable without cloud/files (and reusable/cleaner). Mixing read/transform/write in one function makes it untestable.

**Q3. ⭐ What is the test pyramid for data engineering?**
Many fast **unit** tests (one transform, tiny data), fewer **integration** tests (steps together, real Spark/Delta), a few **end-to-end** tests (whole pipeline on sample data).

**Q4. ⭐ What should you unit-test in a pipeline?**
Business rules, dedupe/filter logic, join correctness, and edge cases (nulls, empty input, duplicate keys, boundaries) — not Spark/Delta itself or trivial passthroughs.

**Q5. 💡 Difference between testing code and testing data?**
Unit tests verify transformation **logic** on fixed inputs; data-quality tests verify the **actual values** flowing through (nulls, ranges, duplicates, volume, freshness). You need both.

---

## Data quality testing

**Q6. 🔥 What is Great Expectations?**
A Python framework for defining **expectations** (not-null, in-range, in-set, row-count) and validating pandas/Spark DataFrames against them, producing reports and gating pipelines.

**Q7. ⭐ Name the data quality dimensions.**
Completeness, uniqueness, validity, consistency, accuracy, timeliness.

**Q8. 🔥 What are the possible responses to a failed data quality check?**
**Warn** (log/alert, continue), **drop/quarantine** (route bad rows aside, continue with good), or **fail/block** (stop before bad data propagates) — chosen per check by severity.

**Q9. ⭐ Where should data quality gates live?**
At layer boundaries — especially **Bronze→Silver** (structure/completeness, the trust boundary) and **Silver→Gold** (business rules/aggregate sanity).

**Q10. 💡 dbt tests vs Great Expectations vs DLT expectations?**
dbt tests for SQL/warehouse models; Great Expectations for framework-agnostic Python/Spark validation; DLT expectations for declarative gates inside Databricks pipelines.

---

## Data contracts

**Q11. 🔥 What is a data contract?**
An explicit, enforced, versioned agreement between data producers and consumers covering schema, semantics, quality, and SLAs — effectively an "API for data."

**Q12. 🔥 What problem do data contracts solve?**
Silent upstream changes — renamed/dropped columns, changed units (dollars→cents) — that break consumers even though the consumer's own code is correct.

**Q13. ⭐ What's in a data contract?**
Schema (names/types/nullability), semantics, quality guarantees, SLA, versioning/change policy, and ownership.

**Q14. ⭐ How are contracts enforced?**
Schema validation on ingest (reject/quarantine), CI checks that block breaking producer changes, and schema registries for streaming topics.

**Q15. 💡 Breaking vs non-breaking schema change?**
Adding optional fields or widening types is backward-compatible; renaming/removing fields or changing type/meaning is breaking — needs a version bump and consumer notice.

**Q16. 💡 How do contracts relate to quality tests and observability?**
Layered defense: contracts **prevent** bad interfaces (shift-left), quality tests **catch** bad values, observability **detects** anything that slips through.

---

## DataOps & CI/CD

**Q17. 🔥 What is DataOps?**
DevOps applied to data — version control, automated testing, CI/CD, environment isolation, and monitoring — so teams ship pipeline changes fast and safely.

**Q18. 🔥 How is CI/CD for data different from app code?**
You test **both** the code (unit tests) and the **data** (quality checks / `dbt build` on a test dataset), because both can break independently.

**Q19. ⭐ What runs in a data CI pipeline?**
Lint/format, unit tests, a pipeline/`dbt build` run against a small test dataset, and data-quality checks — all gating merge and deploy.

**Q20. 🔥 Why separate dev/test/prod environments?**
To build and test without touching production data; the same parameterized code (dbt targets, ADF ARM params, env catalogs) runs against each environment.

**Q21. ⭐ How do you deploy data pipelines across environments?**
As code — Databricks Asset Bundles/Repos, dbt targets, ADF ARM templates, Terraform for infra — promoted through release pipelines, not manual UI clicks.

**Q22. 💡 How does DataOps reduce risk?**
Automated tests + isolated environments + deploy-from-Git verify a change before it can hit production, directly answering "what will this break?"

---

## Scenario

**Q23. 🔥 "A source team changed a column and broke your pipeline overnight. How do you prevent this recurring?"**
Short term: schema validation on ingest to fail-fast/quarantine and alert. Long term: a **data contract** with the producer (schema + change policy) enforced by CI on their side so breaking changes can't ship silently, plus **freshness/volume/schema observability** to detect anything that slips through. Add a unit/data test that encodes the expectation.

**Q24. 💡 "You need to refactor a core transformation used by 20 downstream tables. How do you do it safely?"**
Work on a branch; extract the logic into a tested pure function; add/expand unit tests capturing current correct behavior; run CI (`dbt build`/pipeline + tests) on a test dataset; use dbt's `+` selectors or lineage to see the full downstream blast radius; deploy to test env first, validate outputs (audit-helper/row-count diffs), then promote to prod with monitoring watching.

---

## Further Learning
- Back to the [Learning Path](00_Testing_and_DataOps_Learning_Path.md)
- Related: [Data Quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md) · [CI/CD](../07_DevOps/Git_GitHub/09_Production_Best_Practices_and_CICD.md) · [dbt](../13_dbt/00_dbt_Learning_Path.md) · [Monitoring](../12_Monitoring_and_Observability/00_Monitoring_Learning_Path.md)
