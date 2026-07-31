# 08 — Final Mock Exam

30 questions across all three domains. Give yourself ~45 minutes, no notes. Answers with brief explanations at the bottom.

---

1. Which Fabric item supports full T-SQL `INSERT`/`UPDATE`/`DELETE`?
   A) Lakehouse SQL analytics endpoint B) Warehouse C) Eventhouse D) Dataflow Gen2

2. You need to reference files in an Amazon S3 bucket inside OneLake without copying them. Use a:
   A) Copy activity B) Mirroring C) Shortcut D) Dataflow Gen2

3. Which feature gives a near-real-time replica of an Azure SQL Database in OneLake with no ETL?
   A) Shortcut B) Mirroring C) Eventstream D) Copy activity

4. A user should build items but not manage access. Which workspace role?
   A) Admin B) Member C) Contributor D) Viewer

5. Which promotes content across Dev → Test → Prod?
   A) Git integration B) Deployment pipelines C) Monitoring hub D) Data Activator

6. Restrict each analyst to their own department's rows. Which security?
   A) CLS B) OLS C) RLS D) V-Order

7. Which masks a credit-card column's value for unauthorized users while keeping the data stored?
   A) RLS B) Dynamic Data Masking C) OLS D) Sensitivity label

8. OneLake stores data primarily in which open format?
   A) CSV B) Avro C) Delta/Parquet D) ORC

9. For low-code data transformation during ingest, use:
   A) Copy activity B) Dataflow Gen2 C) Notebook D) Shortcut

10. Move very large volumes efficiently with minimal transformation:
    A) Dataflow Gen2 B) Copy activity C) Eventstream D) KQL

11. No-code ingestion and routing of streaming events:
    A) Eventhouse B) Eventstream C) Notebook D) Warehouse

12. Store and query real-time telemetry with KQL:
    A) Lakehouse B) Warehouse C) Eventhouse D) Dataflow

13. Apply inserts and updates to a Delta table atomically:
    A) OVERWRITE B) MERGE C) TRUNCATE D) COPY INTO

14. Keep full history of dimension changes:
    A) SCD 1 B) SCD 2 C) SCD 3 D) No SCD

15. Load only rows changed since the last run:
    A) Full load B) Incremental load C) Overwrite D) Snapshot

16. Complex, large-scale programmatic transforms belong in:
    A) Dataflow Gen2 B) A Spark notebook C) Power BI D) A shortcut

17. See run status/history of all pipelines and notebooks in one place:
    A) Capacity Metrics app B) Monitoring hub C) Spark UI D) Lineage view

18. A table written by streaming has millions of tiny files and slow reads. Fix:
    A) VACUUM B) OPTIMIZE C) DROP D) Full reload

19. Warehouse queries slowed after a big load. First action:
    A) Add partitions B) Update statistics C) VACUUM D) Restart capacity

20. Tenant workloads are throttled. The bottleneck is:
    A) Spark pool size B) Network C) Capacity (F SKU) D) OneLake storage

21. Which optimization speeds Direct Lake / Power BI reads at write time?
    A) VACUUM B) V-Order C) Broadcast join D) Caching

22. Make a pipeline resilient to a transient error:
    A) Ignore failures B) Configure retries/timeouts/on-failure C) Increase DWU D) Use a shortcut

23. Trigger an alert when an eventstream metric crosses a threshold:
    A) Monitoring hub B) Data Activator C) Capacity Metrics app D) Git

24. Which is read-only T-SQL over a Lakehouse's tables?
    A) Warehouse B) SQL analytics endpoint C) Eventhouse D) Semantic model

25. Aggregating a stream requires:
    A) A window B) A shortcut C) VACUUM D) A full load

26. Version-control Fabric items with branches and PRs:
    A) Deployment pipelines B) Git integration C) Data Activator D) Endorsement

27. Signal that a semantic model is official and trusted:
    A) Sensitivity label B) Endorsement (Certified) C) RLS D) Shortcut

28. VACUUM's purpose is to:
    A) Compact small files B) Remove old tombstoned files to reclaim storage C) Speed BI reads D) Update statistics

29. Which packages runtime version + libraries for reproducible notebooks?
    A) Capacity B) Spark environment C) Deployment rule D) Shortcut

30. "Only keep current dimension values, no history" is:
    A) SCD 1 B) SCD 2 C) SCD 3 D) SCD 4

---

## Answer key

| # | Ans | Why |
|---|---|---|
| 1 | B | Warehouse = full T-SQL DML; Lakehouse SQL endpoint is read-only. |
| 2 | C | Shortcut references external files in place. |
| 3 | B | Mirroring = live operational-DB replica. |
| 4 | C | Contributor builds items, no access mgmt. |
| 5 | B | Deployment pipelines promote across stages. |
| 6 | C | RLS restricts rows. |
| 7 | B | DDM masks values, data still stored. |
| 8 | C | OneLake is Delta/Parquet-native. |
| 9 | B | Dataflow Gen2 = low-code transform. |
| 10 | B | Copy activity = efficient movement. |
| 11 | B | Eventstream = no-code streaming ingest/route. |
| 12 | C | Eventhouse/KQL stores+queries real-time data. |
| 13 | B | MERGE = atomic upsert. |
| 14 | B | SCD 2 keeps full history. |
| 15 | B | Incremental load via watermark/CDC. |
| 16 | B | Spark notebook for complex transforms. |
| 17 | B | Monitoring hub shows all runs. |
| 18 | B | OPTIMIZE compacts small files. |
| 19 | B | Update statistics fixes plans. |
| 20 | C | Throttling = capacity (F SKU) overloaded. |
| 21 | B | V-Order speeds Direct Lake/BI reads. |
| 22 | B | Retries/timeouts/on-failure = resilience. |
| 23 | B | Data Activator triggers alerts. |
| 24 | B | SQL analytics endpoint = read-only T-SQL. |
| 25 | A | Streams aggregate over windows. |
| 26 | B | Git integration = version control. |
| 27 | B | Endorsement (Certified) signals trust. |
| 28 | B | VACUUM reclaims storage (tombstones). |
| 29 | B | Spark environment packages runtime+libs. |
| 30 | A | SCD 1 overwrites, no history. |

**Scoring:** 21/30 ≈ 700/1000 (passing zone). Aim for 26+ before booking. Re-read any domain where you miss more than one.

---

You've finished the DP-700 track. Combined with hands-on Fabric practice, you're prepared for the exam. For the broader path, see the **[ROADMAP](../../ROADMAP.md)**.
