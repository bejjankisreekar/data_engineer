# Data Quality — Interview Questions & Answers

Tagged: 🔥 very common · ⭐ common · 💡 deeper.

---

**Q1. 🔥 What are the dimensions of data quality?**
Accuracy, completeness, consistency, validity, uniqueness, timeliness, integrity — each with a concrete check (e.g., completeness → null checks; uniqueness → dedupe).

**Q2. 🔥 Where do you enforce data quality in a pipeline?**
At **each medallion hop** (shift-left): schema/row-count at Bronze, null/range/dupe/referential at Silver, business rules/reconciliation at Gold. Catch issues as early as possible.

**Q3. 🔥 How do you handle bad records without failing the whole load?**
Route them to a **quarantine/reject** table with the reason, keep the pipeline running, alert, and reprocess later. Fail only on critical, unrecoverable violations.

**Q4. ⭐ What are DLT expectations?**
Declarative data-quality rules in Delta Live Tables: `EXPECT` (keep + track), `ON VIOLATION DROP ROW` (drop bad rows, continue), `ON VIOLATION FAIL UPDATE` (halt pipeline).

**Q5. ⭐ How do Delta CHECK constraints help?**
`ALTER TABLE ... ADD CONSTRAINT c CHECK (...)` makes Delta **reject** writes that violate the rule — enforcing quality at the table level.

**Q6. ⭐ What is Great Expectations?**
An open-source framework for defining, running, and documenting data-quality **expectation suites**, producing validation results and data docs.

**Q7. 🔥 How do you check for duplicates and dedupe?**
`ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) = 1` (SQL) or `dropDuplicates([...])` (PySpark) — keep the latest/valid record per key.

**Q8. 💡 What is data observability?**
Continuous monitoring of **freshness, volume, schema, and distribution** with anomaly alerting (e.g., row count dropped 90%, a column went 50% null) — the "monitoring" of data quality.

**Q9. ⭐ How does schema enforcement help quality?**
Delta rejects writes whose schema doesn't match by default (bad/extra columns); `mergeSchema` opts into evolution; Auto Loader's `_rescued_data` captures unexpected fields instead of dropping them.

**Q10. 🔥 How do you ensure data hasn't been duplicated on a rerun?**
Make loads **idempotent** — MERGE on the business key or overwrite the target partition — so retries don't create duplicates.

**Q11. ⭐ How do you validate freshness/timeliness?**
Check max event/load timestamp against an SLA (e.g., `max(event_time) > now() - 2h`); alert if stale; monitor via observability.

**Q12. 💡 How do you wire quality into CI/CD?**
Run data-quality tests (expectations/Great Expectations) as **deployment gates** — block promotion to prod if critical checks fail; run on sample data in Test.

## Scenario
**Q13. 🔥 "Bad data reached a Gold report and broke it. How do you prevent recurrence?"**
Add quality **gates at Silver** (expectations), **quarantine** bad rows, add **reconciliation** checks at Gold, enable **observability/alerting**, and **RESTORE** the affected Delta table to a good version while backfilling after the fix.

**Q14. ⭐ "A daily feed's row count suddenly halved."**
Observability alert on volume anomaly → investigate the source/extract; quarantine/hold the load; don't overwrite good Gold data until validated.

## Common interview mistakes
- Validating only at the end of the pipeline.
- Failing the whole load on any bad row (no quarantine).
- Silently dropping bad data with no metric/alert.
- No freshness/volume monitoring.
- Non-idempotent loads causing duplicates.

## Related Topics
[Data Governance](../Data_Governance/01_Data_Governance_and_Security.md) · [ETL vs ELT](../ETL_ELT/01_ETL_vs_ELT.md) · [Data Integration](../Data_Integration/02_Integration_Patterns.md)
