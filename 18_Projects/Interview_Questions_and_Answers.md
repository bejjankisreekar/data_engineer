# Projects — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers all three projects ([reading order](00_Projects_Learning_Path.md)).

This file is different from the other Q&A files. The others test *topics*; this one tests **your project**. The moment a project is on your résumé, interviewers stop asking definitions and start asking "why did you do it that way?" — and vague answers here undo a strong technical interview. Rehearse these out loud.

Projects: [1 — Batch Medallion](02_Project_1_Batch_Medallion_Pipeline.md) · [2 — Streaming](03_Project_2_Streaming_Pipeline.md) · [3 — ADF Orchestrated ELT](04_Project_3_ADF_Orchestrated_ELT.md) · [Portfolio presentation](05_Portfolio_and_GitHub_Presentation.md)

---

## The walkthrough (how every project conversation opens)

**Q1. 🔥 "Walk me through a project you've built."**
Use a fixed 4-beat structure, ~2 minutes: **(1) Scenario/business problem** → **(2) architecture in one breath** (source → Bronze → Silver → Gold → Power BI) → **(3) one interesting problem you solved** (SCD2, dedupe, late data) → **(4) the outcome** (a dashboard someone uses, a load time, a cost). Then stop and let them dig. Don't narrate every file you wrote.

**Q2. 🔥 "Why did you choose this architecture?"**
Because the requirements demanded it, not because it's fashionable. Medallion because raw must be replayable (Bronze), business rules need one enforcement point (Silver), and BI needs a stable star schema (Gold). Say what you'd do differently at 100× the volume — that shows judgment rather than tutorial-following.

**Q3. 🔥 "What was the hardest problem you hit?"**
Pick a *real* one and tell it as a story: symptom → how you diagnosed it → the fix → what you'd do differently. Strong candidates: duplicate rows on pipeline re-run, day-2 schema drift, small-file explosion, a skewed join, or state growth in streaming. The diagnosis step is what interviewers actually score.

**Q4. ⭐ "What would you do differently if you rebuilt it?"**
Have a genuine answer ready — e.g. add data quality gates and quarantine from day one, use Auto Loader instead of a directory listing, make the pipeline metadata-driven earlier, or add CI tests on transformation logic. "Nothing" reads as no reflection.

**Q5. ⭐ "How do I know you actually built it?"**
Because you can show the repo, the README diagram, and the commit history — and answer follow-ups about failure modes. Be able to open the code and explain any function you wrote ([portfolio presentation](05_Portfolio_and_GitHub_Presentation.md)).

---

## Project 1 — Batch medallion pipeline

**Q6. 🔥 Why three layers? Isn't Bronze wasteful?**
Bronze is your **replay source and audit trail**. When a Silver business rule turns out wrong, you rebuild from Bronze instead of re-pulling from a source system that may no longer hold that history. Storage is cheap; re-extraction and lost history are not ([medallion](../05_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md)).

**Q7. 🔥 "How did you handle a customer changing their address?"**
**SCD2** with Delta `MERGE`: match the current row on the natural key; if a tracked attribute changed, close the old row (`valid_to`, `is_current = false`) and insert a new version with a new surrogate key. That preserves "what was true when the order was placed" ([SCD](../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md)).

**Q8. 🔥 "How do you make a re-run safe (idempotent)?"**
Bronze is append-only and reprocessable; Silver/Gold use **`MERGE` on the business key**, never blind `append`, plus a dedupe window for repeated events. Re-running the same day's file produces the same result rather than doubling revenue.

**Q9. 🔥 "Day 2's file arrives with an extra column. What happens?"**
Bronze accepts it via Delta **schema evolution** (`mergeSchema`) so ingestion doesn't fail; Silver **validates explicitly** against the expected schema, so a surprise column is a decision, not a silent change flowing into reports.

**Q10. ⭐ "Where do you put data quality checks and what happens to bad rows?"**
At the **Bronze → Silver boundary** — the contract point. Bad rows go to a **quarantine table** with a reason code rather than being dropped or failing the whole load, and volume/null-rate anomalies raise an alert ([data quality](../06_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md)).

**Q11. ⭐ "Your job got slow after a few weeks. Why?"**
Almost always the **small-file problem** — many daily loads and MERGEs produce thousands of tiny files, wrecking scan performance. Fix: scheduled `OPTIMIZE` (with Z-order or liquid clustering), sensible partitioning, and *not* over-partitioning (millions of tiny partitions is the opposite failure).

**Q12. ⭐ "A join between orders and customers was slow. What did you check?"**
Sizes first — **broadcast** the small dimension to avoid a shuffle. Then check for **skew** (one key dominating) and fix with salting/AQE, and confirm you're not shuffling more columns than needed ([performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)).

**Q13. ⭐ "Why a star schema in Gold instead of one big table?"**
Star gives BI tools conformed dimensions, consistent metric definitions, and efficient slicing; OBT is a valid choice for a specific wide report or an ML feature table. The point is choosing per consumer, not dogma ([dimensional modeling](../02_Databases/Data_Modeling/03_Dimensional_Modeling.md)).

**Q14. 💡 "Numbers changed after a re-run. How would you debug that?"**
`DESCRIBE HISTORY` on the Gold table to see what operation ran, then **time-travel** to compare versions (`VERSION AS OF`) and identify which load introduced the difference — then fix the root cause (a blind `append`, or a non-idempotent transform) rather than patching the output.

---

## Project 2 — Streaming pipeline

**Q15. 🔥 "Batch or streaming — how do you decide?"**
By the **freshness requirement of the decision**, not by preference. Streaming when action must happen in seconds-to-minutes (fraud, live ops, alerting); otherwise batch is cheaper, simpler, easier to test and backfill. "We streamed because it's modern" is a red flag.

**Q16. 🔥 "How do you get exactly-once?"**
**Checkpointing** (Spark tracks source offsets and progress) plus an **idempotent Delta sink** — so a restart resumes from the last committed offset instead of reprocessing or double-writing. End-to-end it's effectively exactly-once, built on an at-least-once source plus idempotent writes.

**Q17. 🔥 "What is a watermark and why does it matter?"**
It declares how late an event may arrive and still be counted. It **bounds state** (so old windows are evicted and memory doesn't grow forever) and defines when a window is final. Set it to your real lateness SLA and **monitor dropped-event counts** — a too-tight watermark silently loses data.

**Q18. ⭐ "You deleted the checkpoint directory. What happens?"**
The stream loses its offset position and reprocesses from the configured starting point — duplicates or a full replay. Checkpoints are state, not scratch: never delete casually, and treat a schema/logic change that invalidates them as a deliberate migration.

**Q19. ⭐ "Duplicate events from the source — how do you handle them?"**
`dropDuplicates` on an event key **within the watermark window** (unbounded dedupe would grow state forever), plus an idempotent Delta `MERGE` so a replay can't double-count.

**Q20. ⭐ "Event Hubs vs Kafka — why did you pick one?"**
Event Hubs is a **managed** Azure service that speaks the Kafka protocol: same client code, no brokers to run. Self-managed Kafka earns its operational cost when you need its ecosystem (Connect, Streams), multi-cloud portability, or very long retention ([streaming](../09_Streaming/03_Apache_Kafka.md)).

**Q21. 💡 "Your streaming job cost more than the value it delivered. What went wrong?"**
Usually an always-on oversized cluster for a low-volume stream. Fixes: right-size or go single-node/serverless, lengthen the trigger interval, or use **Structured Streaming with `availableNow`** to run micro-batches on a schedule — streaming semantics (checkpoints, incremental state) at batch cost.

---

## Project 3 — ADF orchestrated ELT

**Q22. 🔥 "ADF vs Databricks — who does what?"**
ADF is the **control plane**: orchestration, movement, scheduling, dependencies, retries, alerting. Databricks is the **data plane**: transformation at scale. ADF triggers the notebook; it doesn't do the heavy compute itself.

**Q23. 🔥 "How do you do incremental loads instead of full reloads?"**
A **watermark column** (`modified_date`): Lookup the last loaded value → Copy only rows newer than it → update the watermark on success. When the source supports it, **CDC** is better still — log-based, catches deletes, no reliance on a reliable timestamp ([CDC](../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md)).

**Q24. 🔥 "What is a metadata-driven pipeline and why does it matter?"**
**One parameterized pipeline** looping (`ForEach`) over a config table listing tables, sources, and watermarks — instead of one pipeline per table. Adding a table becomes a config row, not a deployment. It's the difference between 3 pipelines and 300.

**Q25. ⭐ "Schedule trigger vs tumbling window trigger?"**
Schedule just fires on a clock. **Tumbling window** is stateful with fixed non-overlapping windows — it supports **dependencies and backfill**, so a missed day can be replayed for its exact window. Choose tumbling when correctness of each period matters.

**Q26. ⭐ "How are secrets handled?"**
Never in linked service definitions or notebooks — linked services **reference Azure Key Vault**, and Databricks reads them via secret scopes. Access is via managed identity/service principal with least privilege ([governance & security](../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)).

**Q27. ⭐ "A pipeline failed at 2 a.m. How do you find out and recover?"**
Failure path with an **alert activity** plus Azure Monitor alerting on the pipeline run, retries with backoff for transient faults, and idempotent activities so a rerun is safe. Then re-run the failed window (tumbling window makes this exact) ([monitoring](../12_Monitoring_and_Observability/03_Pipeline_Reliability.md)).

**Q28. 💡 "How do you promote a pipeline from dev to prod?"**
Git-integrated ADF with parameterized linked services per environment, deployed via ARM templates in a release pipeline with approvals — never hand-editing prod in the portal ([CI/CD for ADF & Databricks](../14_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md)).

---

## Cross-cutting follow-ups

**Q29. 🔥 "How would this change at 100× the data volume?"**
Name the specific pressure points: partitioning and file sizing, incremental-only processing (no full scans), Auto Loader for file discovery instead of directory listing, cluster sizing/autoscaling, and moving quality checks to sampled/aggregate checks. Showing you know *where* it breaks first is the answer.

**Q30. 🔥 "How did you test this?"**
Unit tests on transformation functions with small fixture DataFrames (pure functions, no cluster needed), schema/contract assertions between layers, row-count and null-rate checks after each load, and a smoke run on sample data in CI ([testing](../14_Testing_and_DataOps/01_Testing_Data_Pipelines.md)).

**Q31. ⭐ "How did you control cost while learning?"**
Auto-terminating clusters, smallest viable node sizes, free/trial tiers, deleting resource groups after each session, and small datasets — scale is proven by design decisions, not by burning credits ([cost](../15_Cost_and_Performance/01_Cost_Fundamentals_FinOps.md)).

**Q32. ⭐ "Who consumed the output, and how do you know it was right?"**
A Power BI dashboard over the Gold star schema, validated by reconciling totals against the source for a known period. Being able to say *how you proved correctness* matters more than the dashboard's looks.

**Q33. ⭐ "How is your code organized in the repo?"**
Transformation logic in tested `.py` modules; notebooks orchestrate and call them (thin notebooks). Config separate from code, secrets never committed, README with an architecture diagram and run instructions ([Git for DE](../07_DevOps/Git_GitHub/Interview_Questions_and_Answers.md)).

**Q34. 💡 "What monitoring would you add before calling this production-ready?"**
Freshness SLA per table, row-count/volume anomaly detection, failure alerting with an owner, run-duration trends to catch creeping degradation, and lineage so a broken Gold table traces back to its source ([observability](../12_Monitoring_and_Observability/04_Data_Observability.md)).

---

## Presenting it (résumé & portfolio follow-ups)

**Q35. 🔥 "Summarize this project in one résumé bullet."**
Action + tech + measurable outcome: *"Built an incremental medallion pipeline (ADF → Databricks → Delta) loading N tables nightly with SCD2 dimensions and quality gates, serving a Power BI sales dashboard."* Never claim numbers you can't defend.

**Q36. ⭐ "Is this a personal project or production work?"**
Say so plainly. A well-built personal project honestly labeled beats an inflated claim that collapses on the second follow-up — and interviewers ask follow-ups precisely to test this.

**Q37. ⭐ "Why should I care about a portfolio project with fake data?"**
Because the engineering decisions are real: idempotency, schema drift, SCD2, orchestration, failure handling, and cost. Frame it as "the data is synthetic; the failure modes and design trade-offs are the same ones production has."

**Q38. 💡 "What did you learn that you couldn't have learned from a tutorial?"**
The failure modes — duplicates on re-run, day-2 schema drift, small files, state growth, secrets management. Tutorials show the happy path; being able to narrate what broke and why is the entire differentiator.

---

## Common interview mistakes
- Narrating **every step** instead of the 4-beat structure, then getting cut off before the interesting part.
- Claiming numbers ("processed 10TB daily") you can't substantiate.
- Saying "streaming" when a batch job with a schedule is what was built — know which you have.
- No answer to "what broke?" — it signals a tutorial that was followed, not a pipeline that was built.
- Being unable to explain your **own** code when it's opened in front of you.
- Not mentioning idempotency/re-run safety, the single most common senior follow-up.

## Related Topics
[Medallion Architecture](../05_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md) · [Delta Table](../05_Storage_and_Formats/Lakehouse/02_Delta_Table.md) · [PySpark Performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md) · [SCD](../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) · [Orchestration](../11_Orchestration/01_Orchestration_Fundamentals.md) · [Streaming](../09_Streaming/01_Streaming_Fundamentals.md) · [System Design](../17_System_Design/02_Batch_Pipeline_Design.md) · [Testing & DataOps](../14_Testing_and_DataOps/01_Testing_Data_Pipelines.md)
