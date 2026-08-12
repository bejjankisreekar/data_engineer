# Lakehouse, Delta Lake & Delta Table — Interview Questions & Answers

Covers the three notes in this folder: [Delta Lake](01_Delta_Lake.md), [Delta Table](02_Delta_Table.md), and [Lakehouse Architecture](03_Lakehouse_Architecture.md). Questions are tagged **[Theory]** or **[Scenario]** and marked ⭐ when they're very frequently asked.

---

## Delta Lake — the storage layer

**1. ⭐ [Theory] What is Delta Lake?**
An open-source storage layer that adds ACID transactions, updates/deletes/merge, time travel, and schema enforcement to a data lake. It works by wrapping ordinary Parquet files with a transaction log (`_delta_log`) that records which files make up the table at each version. In short: **Parquet files + a transaction log that makes them behave like a database table.**

**2. ⭐ [Theory] Delta Lake vs plain Parquet — what's the difference?**
Parquet is a *file* format; Delta is a *table* format built on top of Parquet. Parquet alone has no transactions, no `UPDATE`/`DELETE` (you rewrite files by hand), and no history. Delta adds all of that via its log, while the data itself is still open Parquet.

**3. [Theory] How does Delta achieve ACID transactions on object storage that has no locks?**
Optimistic concurrency control. A writer reads the current version N, does its work, then tries to commit the next log file `N+1.json`. Object stores guarantee only one process can create a given filename, so only one writer wins that commit; others detect the conflict, re-read, and retry. This yields serializable isolation without a lock server.

**4. [Scenario] Parquet is immutable, so how does an `UPDATE` actually work in Delta?**
Delta doesn't edit files in place. It writes *new* Parquet files containing the updated rows, then commits a transaction that `remove`s the old files and `add`s the new ones. The old files remain on disk (tombstoned), which is exactly what enables time travel. (Modern Delta can instead write a *deletion vector* — a bitmap marking changed rows — and defer the rewrite.)

**5. ⭐ [Theory] What is time travel and how is it possible?**
Reading a table as it existed at a past version or timestamp (`VERSION AS OF 8`, `TIMESTAMP AS OF '...'`). It's possible because updates/deletes tombstone old files rather than deleting them, and the log records the exact set of files valid at each version. Uses: reproducing a report, auditing, debugging "what changed", and rolling back a bad load with `RESTORE`.

**6. [Scenario] A junior sets `VACUUM` to a 1-hour retention to save storage. What breaks?**
`VACUUM` physically deletes tombstoned files older than the retention window. Shrinking it to an hour destroys the ability to time-travel to older versions and can corrupt any in-flight readers or streaming jobs still referencing those files. The 7-day default exists for that safety margin — don't shorten it casually.

**7. [Theory] What is schema enforcement vs schema evolution?**
Enforcement (default) rejects a write whose columns/types don't match the table — a guardrail against silent corruption. Evolution (opt-in, via `mergeSchema` or `ALTER TABLE ADD COLUMN`) lets the schema grow *on purpose*; new columns backfill as NULL for old rows.

**8. [Theory] What are checkpoints in the Delta log?**
To avoid replaying thousands of JSON commit files, Delta writes a Parquet *checkpoint* summarizing the whole table state every 10 commits. A reader loads the latest checkpoint plus the few JSON files after it, instead of the entire history.

---

## Delta Table — using the table

**9. ⭐ [Theory] Managed vs external (unmanaged) Delta table — what's the difference?**
For a **managed** table the metastore owns the storage location, and `DROP TABLE` deletes *both* the metadata and the underlying files. For an **external** table you specify the `LOCATION`, and `DROP TABLE` removes only the metadata — the files stay. Use external when other engines share the files or you need the data to outlive the table definition.

**10. [Scenario] Someone runs `DROP TABLE` expecting the data files to survive, but they're gone. Why?**
It was a *managed* table — dropping it deletes the files too. This is the #1 accidental data-loss cause with Delta. `DESCRIBE DETAIL` shows the `location`; if the table must be droppable without losing data, make it external.

**11. ⭐ [Theory] What is `MERGE` and why is it the killer feature?**
`MERGE` performs insert-or-update (upsert) plus delete in one atomic operation: `WHEN MATCHED THEN UPDATE`, `WHEN NOT MATCHED THEN INSERT`. It's the backbone of CDC apply and SCD Type 2, letting you fold a mixed feed of new and changed rows into a table without pre-splitting them.

**12. [Scenario] Your nightly `MERGE` gets slower every week. Diagnose and fix.**
As the table grows, `MERGE` rewrites more files. Fixes: constrain the match to recently-touched partitions (`AND t.order_date >= current_date - 7`), partition or liquid-cluster the merge/join key, enable deletion vectors (merge-on-read so matched files aren't fully rewritten), and check for skew on the join key. A MERGE that rewrites the whole table nightly is a design bug.

**13. [Theory] What do `OPTIMIZE` and `VACUUM` do?**
`OPTIMIZE` compacts many small files into fewer large ones (fixing the small-file problem from streaming/frequent MERGE), and `OPTIMIZE ... ZORDER BY (col)` co-locates related data so queries skip more files. `VACUUM` physically deletes tombstoned files older than the retention window to reclaim storage.

**14. [Scenario] Why shouldn't you partition a Delta table by `customer_id`?**
It's high cardinality — you'd create millions of tiny partitions and files, wrecking scan performance and metadata handling. Partition on low-cardinality, commonly-filtered columns (dates), or better, use liquid clustering, which adapts and avoids the over-partitioning trap.

**15. [Theory] What is Change Data Feed (CDF)?**
A table property (`delta.enableChangeDataFeed = true`) that makes a Delta table emit its own row-level inserts/updates/deletes. Downstream jobs read only the changes (`table_changes('t', version)`) instead of rescanning the whole table — the basis of efficient incremental medallion pipelines.

**16. [Scenario] A bad feed doubled today's rows in a Delta table. Recovery?**
`RESTORE TABLE t VERSION AS OF <last_good_version>` (or `TIMESTAMP AS OF`). Because old file versions are tombstoned, not deleted, the restore is near-instant — no backup restore or downtime needed (assuming `VACUUM` hasn't already purged that version).

---

## Lakehouse — the architecture

**17. ⭐ [Theory] What is a lakehouse?**
An architecture that combines data-lake storage economics with data-warehouse guarantees in one system: cheap open lake storage + a transactional table format (Delta) + a SQL engine and catalog on top. Result: one copy of data serves BI, streaming, engineering, and ML — warehouse behavior at lake cost.

**18. ⭐ [Theory] What problem does the lakehouse solve?**
The two-copy problem. The old world ran a lake *and* a warehouse with a pipeline forever copying lake → warehouse, producing duplicate data, sync lag, and "which number is right?" reconciliation. The lakehouse organizes data in place on the lake, so there's one source of truth and no copy pipeline.

**19. ⭐ [Theory] Explain the medallion architecture.**
Three refinement layers of Delta tables. **Bronze**: raw, append-only, exactly as ingested (+ metadata) — the replay source. **Silver**: cleaned, typed, deduplicated, conformed — the shared enterprise view. **Gold**: business-modeled aggregates and star schemas — report/ML-ready. Each boundary is a contract, not just a folder name.

**20. [Scenario] A team points Power BI at the Silver layer "temporarily." Why is that a problem?**
It breaks the Gold contract and puts permanent BI query load on engineering tables that weren't modeled or optimized for it. Gold exists as the contract boundary for BI; Silver is for engineers and scientists. "Temporary" pointers to Silver tend to become permanent.

**21. [Theory] What three pillars make a lakehouse possible?**
(1) An open table format (Delta) providing ACID/time travel/schema enforcement; (2) a performant query engine (Spark for engineering, a vectorized SQL engine like Photon for BI); (3) a governance catalog (Unity Catalog / Purview) for one permission model, lineage, and discovery. Miss one and it's just a lake with extra steps.

**22. [Scenario] When would you still recommend a classic warehouse over a lakehouse?**
When the org is SQL-only, has a mature BI estate, runs high-concurrency small queries, and has no ML/streaming pressure — the migration cost can exceed the duplication cost the lakehouse would remove. The lakehouse is the default for *new, mixed-workload* platforms, not a rip-and-replace mandate.

**23. ⭐ [Theory] Lake vs warehouse vs lakehouse in one line each.**
Lake = cheap open storage for everything raw, no transactions. Warehouse = governed, SQL-optimized store for BI, but rigid/often proprietary. Lakehouse = open lake storage that learned transactions, so one copy serves both.

**24. [Scenario] What turns a lakehouse into a "data swamp," and what prevents it?**
No contracts, no catalog, no owners, and no modeling — a table format alone isn't governance. Prevented by enforced Bronze/Silver/Gold contracts, a governance catalog (Unity Catalog/Purview), quality gates between layers, and real dimensional modeling in Gold. The storage merged; the discipline didn't.

**25. [Theory] Where does Delta / the lakehouse show up in Azure?**
Azure Databricks (Delta + Unity Catalog + Databricks SQL) is the primary lakehouse platform, storing Delta files on ADLS Gen2. Microsoft Fabric is the SaaS lakehouse where OneLake stores everything as Delta by default. Governance via Unity Catalog and Microsoft Purview; BI via Power BI over the SQL endpoint / Direct Lake.

---

## Related Notes

- [Delta Lake](01_Delta_Lake.md) · [Delta Table](02_Delta_Table.md) · [Lakehouse Architecture](03_Lakehouse_Architecture.md)
- [Data Lake vs Warehouse vs Database](../Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) · [Parquet](../File_Formats/05_Parquet.md)
- [12 — Delta Lake with PySpark](../../03_Programming/PySpark/12_Delta_Lake_with_PySpark.md) (hands-on code)
- Interview folders: [Delta Lake](../../Job%20Interviews/Delta%20Lake/Delta%20Lake%20Interview%20Questions.md) · [Lakehouse](../../Job%20Interviews/Lakehouse/Lakehouse%20Interview%20Questions.md)
