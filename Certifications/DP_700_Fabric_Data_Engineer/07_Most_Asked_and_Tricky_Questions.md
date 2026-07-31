# 07 — Most Asked & Tricky Questions

The comparison pairs and confusions that decide most DP-700 wrong answers. Learn to tell each pair apart instantly.

---

## The confusable pairs

**1. Lakehouse vs Warehouse**
Lakehouse = Spark + SQL, files + Delta tables, **written by Spark/notebooks** (SQL endpoint is read-only). Warehouse = full read/write **T-SQL** (INSERT/UPDATE/DELETE/MERGE). Both store Delta in OneLake.

**2. Shortcut vs Mirroring**
Shortcut = *reference* files in ADLS/S3/GCS/other workspace, no copy. Mirroring = *live replica* of an operational database (Azure SQL, Cosmos, Snowflake) into OneLake as Delta.

**3. Copy activity vs Dataflow Gen2**
Copy = move data efficiently at scale, minimal transform. Dataflow Gen2 = low-code Power Query *transformation* during ingest.

**4. Data pipeline vs Dataflow Gen2**
Pipeline = orchestration (DAG of activities, scheduling, dependencies). Dataflow Gen2 = the actual low-code data transformation. A pipeline can *run* a dataflow.

**5. Git integration vs Deployment pipelines**
Git = version control & collaboration (branches, PRs, source of truth). Deployment pipelines = promote content across Dev/Test/Prod stages with rules.

**6. RLS vs CLS vs OLS vs DDM**
RLS = restrict rows. CLS = restrict columns. OLS = hide whole objects. DDM = *mask* column values (data still present, hidden in output).

**7. Eventstream vs Eventhouse**
Eventstream = no-code streaming *ingest & routing*. Eventhouse/KQL DB = *store & analyze* real-time data with KQL.

**8. Full vs incremental load**
Full = reload everything (small dims, first load). Incremental = only new/changed rows via watermark/CDC (large sources).

**9. SCD 1 vs SCD 2**
SCD 1 = overwrite, no history. SCD 2 = new row per change, full history (`is_current`, start/end dates) via `MERGE`.

**10. MERGE vs overwrite**
MERGE = upsert (insert+update+delete atomically), preserves history and concurrent writes. Overwrite = replace everything, loses history.

**11. OPTIMIZE vs VACUUM**
OPTIMIZE = compact small files for read speed. VACUUM = delete old tombstoned files to reclaim storage (can break time travel if retention too short).

**12. V-Order**
A Fabric write-time Parquet optimization for fast reads (esp. Direct Lake/Power BI). Not the same as OPTIMIZE (compaction) — they complement each other.

**13. Workspace roles**
Admin (all + access mgmt) > Member (edit + add lower) > Contributor (build, no access mgmt) > Viewer (read only).

**14. Monitoring hub vs Capacity Metrics app**
Monitoring hub = run history/status of items. Capacity Metrics app = CU consumption/throttling.

---

## Keyword → answer cheat sheet

| Scenario keyword | Answer |
|---|---|
| Reference external files, no copy | **Shortcut** |
| Live replica of operational DB, no ETL | **Mirroring** |
| Move lots of data, low-code | **Copy activity** |
| Low-code transform on ingest | **Dataflow Gen2** |
| Complex/large programmatic transform | **Notebook (Spark)** |
| Full T-SQL read/write warehouse | **Warehouse** |
| No-code streaming ingest/route | **Eventstream** |
| Store/query real-time with KQL | **Eventhouse / KQL DB** |
| Upsert new + changed rows | **MERGE** |
| Keep full dimension history | **SCD Type 2** |
| Only changed rows since last run | **Incremental load (watermark/CDC)** |
| Promote Dev→Test→Prod | **Deployment pipelines** |
| Version control items | **Git integration** |
| Restrict rows per user | **RLS** |
| Mask a sensitive column's values | **DDM** |
| See all run history | **Monitoring hub** |
| Diagnose throttling / CU usage | **Capacity Metrics app** |
| Compact small files | **OPTIMIZE** |
| Fast Direct Lake / BI reads | **V-Order** |
| Alert when a metric crosses a threshold | **Data Activator** |

---

## Tricky traps

- "The SQL analytics endpoint of a Lakehouse lets you INSERT/UPDATE data." → **No** — it's **read-only** T-SQL; use a **Warehouse** for T-SQL writes.
- "A shortcut copies the data into OneLake." → **No** — it *references* it in place.
- "Use a full load to capture only changed rows." → **No** — that's **incremental**.
- "VACUUM makes queries faster by compacting files." → **No** — that's **OPTIMIZE**; VACUUM reclaims storage.
- "Deployment pipelines version-control your code." → **No** — that's **Git**; deployment pipelines *promote* between stages.
- "DDM removes the column from the table." → **No** — it **masks** the displayed value; data is still stored (CLS removes access).
- "Throttling is fixed by adding Spark workers." → **No** — throttling is a **capacity (F SKU)** limit; scale/stagger the capacity.
- "Eventhouse ingests streams with no code." → **No** — **Eventstream** does the no-code ingest/route; Eventhouse stores/analyzes with KQL.

---

Next: **[08 — Final Mock Exam](08_Final_Mock_Exam.md)**.
