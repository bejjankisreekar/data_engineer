# 13 — Final Mock Exam

**45 questions · 90-minute limit · pass mark 70% (32/45).**

Simulate real conditions: no notes, one sitting, ~2 min/question. Write down your answers, then score against the **Answer Key** at the bottom. Anything you miss → re-read that domain's file.

---

### Section A — Lakehouse Platform (Q1–Q11)

**1.** The Lakehouse architecture is primarily enabled by which technology?
A. Apache Hive  B. Delta Lake  C. HDFS  D. Parquet alone

**2.** In the classic deployment model, the compute (data) plane runs in:
A. Databricks' cloud account  B. The customer's cloud account  C. The control plane  D. On-premises

**3.** Which is created automatically and terminated when a scheduled job completes?
A. All-purpose cluster  B. SQL Warehouse  C. Job cluster  D. Serverless SQL

**4.** Photon primarily provides:
A. Governance  B. A vectorized engine that speeds SQL/DataFrame workloads  C. A new language  D. A streaming source

**5.** To share helper functions defined in another notebook into your current notebook, use:
A. `dbutils.notebook.run()`  B. `%run`  C. `%sh`  D. `import`

**6.** You terminate (not delete) a cluster. The configuration is:
A. Deleted permanently  B. Retained; the cluster can be restarted  C. Converted to a job cluster  D. Archived to storage

**7.** Databricks SQL dashboards and analyst queries run on:
A. All-purpose clusters  B. Job clusters  C. SQL Warehouses  D. The driver node

**8.** Which supports standard Git operations (commit/push/pull/branch) inside the workspace?
A. DBFS  B. Repos / Git folders  C. Notebook revision history  D. Unity Catalog

**9.** The Databricks control plane hosts:
A. Customer raw data  B. Backend services (UI, job scheduler, cluster manager) and metadata  C. Spark executors  D. External tables

**10.** Which `dbutils` module retrieves credentials without hardcoding them?
A. `dbutils.fs`  B. `dbutils.widgets`  C. `dbutils.secrets`  D. `dbutils.notebook`

**11.** Uploaded files via the UI land under which path by default?
A. `/mnt/`  B. `dbfs:/FileStore/`  C. `/tmp/`  D. `/user/hive/`

---

### Section B — ELT with Spark SQL & Python (Q12–Q24)

**12.** Which correctly queries a JSON file directly?
A. `SELECT * FROM read('/f.json')`  B. `SELECT * FROM json.\`/f.json\``  C. `OPEN json '/f.json'`  D. `LOAD '/f.json'`

**13.** A table created with `USING CSV OPTIONS(header="true") LOCATION '/data'` is:
A. A managed Delta table  B. A non-Delta external table reading files live  C. A temp view  D. A materialized view

**14.** Which survives a cluster restart?
A. Temp view  B. Global temp view  C. A regular view (`CREATE VIEW`)  D. A CTE

**15.** `payload` is a JSON **string** column. Extract nested `user.id` with:
A. `payload.user.id`  B. `payload:user.id`  C. `payload->user->id`  D. `explode(payload)`

**16.** Which turns each array element into its own row?
A. `transform`  B. `explode`  C. `filter`  D. `flatten`

**17.** `UNION ALL` differs from `UNION` because it:
A. Removes duplicates  B. Keeps duplicates  C. Sorts results  D. Requires same schema only

**18.** Which is an **action** in PySpark?
A. `withColumn`  B. `select`  C. `count`  D. `filter`

**19.** The default DataFrame save mode when the target already exists is:
A. append  B. overwrite  C. errorifexists  D. ignore

**20.** `df.withColumn("c", col("a")+1)` returns:
A. The same df, mutated  B. A new DataFrame  C. A list of rows  D. None

**21.** Why prefer built-in functions over Python UDFs?
A. UDFs can't return null  B. UDFs are slower and opaque to the optimizer  C. UDFs only work in SQL  D. No difference

**22.** To query a DataFrame with `spark.sql(...)`, first:
A. `df.save()`  B. `df.createOrReplaceTempView("v")`  C. `df.cache()`  D. `df.collect()`

**23.** Which counts only non-null values of `email`?
A. `count(*)`  B. `count(email)`  C. `count(1)`  D. `sum(email)`

**24.** A persisted, reusable, governed SQL function is created with:
A. `CREATE UDF`  B. `CREATE FUNCTION ... RETURNS ... RETURN ...`  C. `DEFINE FUNCTION`  D. `@udf`

---

### Section C — Incremental Data Processing (Q25–Q35)

**25.** What gives a Structured Streaming query exactly-once fault tolerance?
A. Output mode  B. Checkpoint location  C. Trigger  D. Watermark

**26.** Which trigger processes all available new data then stops?
A. `processingTime="5 minutes"`  B. `availableNow=True`  C. default  D. `continuous=True`

**27.** For a streaming aggregation showing full running totals, use output mode:
A. append  B. update  C. complete  D. overwrite

**28.** Auto Loader uses which format string?
A. `autoloader`  B. `cloudFiles`  C. `stream`  D. `delta`

**29.** Auto Loader's advantage over a manual read loop is that it:
A. Is written in Scala  B. Tracks processed files and ingests only new ones at scale  C. Requires no storage  D. Skips schema inference

**30.** Which medallion layer holds raw, as-ingested data?
A. Bronze  B. Silver  C. Gold  D. Platinum

**31.** Cleaned, deduplicated, validated, and joined data belongs in:
A. Bronze  B. Silver  C. Gold  D. Raw

**32.** In DLT, reference another pipeline table with:
A. Its file path  B. `LIVE.table` / `dlt.read()`  C. `spark.table()` only  D. A REST call

**33.** A DLT expectation with `ON VIOLATION DROP ROW`:
A. Keeps bad rows and tracks them  B. Drops bad rows; pipeline continues  C. Fails the pipeline  D. Rewrites the table

**34.** A DLT `EXPECT` with no `ON VIOLATION` clause:
A. Drops bad rows  B. Keeps bad rows and records the violation in metrics  C. Fails the update  D. Ignores the constraint entirely

**35.** Which streaming caveat applies when reading a Delta table modified by UPDATE/DELETE?
A. Nothing changes  B. The stream may fail unless `ignoreChanges`/`ignoreDeletes` is set  C. Data is lost silently  D. It converts to batch

---

### Section D — Production Pipelines (Q36–Q42)

**36.** A multi-task Databricks Job with dependencies forms a:
A. Cluster  B. DAG of tasks  C. Notebook  D. View

**37.** To re-run only the failed and downstream tasks of a job run:
A. Recreate the job  B. Use Repair run  C. Restart the cluster  D. Clone the job

**38.** A scheduled notebook reads a Job-passed parameter with:
A. `spark.conf.get`  B. `dbutils.widgets.get("p")`  C. `input()`  D. `os.getenv`

**39.** Databricks Jobs natively support scheduling via:
A. Only manual runs  B. Cron schedules, file-arrival triggers, and continuous mode  C. Only external Airflow  D. Only the REST API

**40.** For a scheduled production pipeline, the recommended cluster is:
A. All-purpose (stays warm)  B. Job cluster (auto-created/terminated)  C. SQL Warehouse  D. Single-node all-purpose

**41.** To recover from transient task failures automatically, configure:
A. A longer timeout  B. Automatic retries  C. A bigger driver  D. Continuous mode

**42.** A DLT pipeline can be orchestrated as:
A. A task inside a Databricks Job  B. Only standalone  C. Only via Airflow  D. Only manually

---

### Section E — Data Governance (Q43–Q45)

**43.** Unity Catalog's namespace is:
A. `schema.table`  B. `catalog.schema.table`  C. `table`  D. `db.schema.table.column`

**44.** A user with `SELECT` on a table still can't query it. Most likely missing:
A. `MODIFY`  B. `USE CATALOG` + `USE SCHEMA`  C. Ownership  D. `CREATE TABLE`

**45.** Which UC object governs access to non-tabular files (e.g., images)?
A. Table  B. View  C. Volume  D. Function

---

## Answer Key

| Q | A | Q | A | Q | A | Q | A | Q | A |
|---|---|---|---|---|---|---|---|---|---|
| 1 | B | 10 | C | 19 | C | 28 | B | 37 | B |
| 2 | B | 11 | B | 20 | B | 29 | B | 38 | B |
| 3 | C | 12 | B | 21 | B | 30 | A | 39 | B |
| 4 | B | 13 | B | 22 | B | 31 | B | 40 | B |
| 5 | B | 14 | C | 23 | B | 32 | B | 41 | B |
| 6 | B | 15 | B | 24 | B | 33 | B | 42 | A |
| 7 | C | 16 | B | 25 | B | 34 | B | 43 | B |
| 8 | B | 17 | B | 26 | B | 35 | B | 44 | B |
| 9 | B | 18 | C | 27 | C | 36 | B | 45 | C |

---

## Scoring guide

- **41–45 (91%+):** Exam-ready. Do a final skim of file 12's rapid-fire table.
- **36–40 (80–89%):** Solid. Re-read the topic files for your missed questions.
- **32–35 (70–78%):** Passing but thin — reinforce weak domains before booking.
- **Below 32 (<70%):** Not ready yet. Re-study the domain(s) where you missed the most, redo file 11, then retake this mock.

## Domain-to-question map (for targeted review)

| Domain | Questions | Study file |
|---|---|---|
| Lakehouse Platform | 1–11 | [01](01_Lakehouse_Platform_Fundamentals.md)–[03](03_Delta_Lake_Fundamentals.md) |
| ELT (SQL & Python) | 12–24 | [04](04_ELT_with_Spark_SQL.md)–[05](05_ELT_with_PySpark_and_Python.md) |
| Incremental Processing | 25–35 | [06](06_Structured_Streaming.md)–[08](08_Delta_Live_Tables.md) |
| Production Pipelines | 36–42 | [09](09_Production_Pipelines_Jobs.md) |
| Data Governance | 43–45 | [10](10_Data_Governance_Unity_Catalog.md) |

---

**Good luck.** When you can score 90%+ on this mock and answer file 12's rapid-fire table from memory, you're ready to book the exam.

Back to **[00 — Study Guide Overview](00_Study_Guide_Overview.md)**.
