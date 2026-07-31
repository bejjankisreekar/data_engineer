# 11 — Practice Questions by Domain

Work through each domain's questions after reading its topic file(s). Answers with explanations follow each block. Cover the answer, commit to a choice, then check.

---

## Domain 1 — Databricks Lakehouse Platform

**Q1.** What does the Lakehouse architecture combine?
- A. Two separate systems: a data lake and a data warehouse kept in sync
- B. The low-cost open storage of a data lake with the reliability and performance of a data warehouse
- C. A NoSQL database with a relational database
- D. On-prem Hadoop with cloud object storage

**Q2.** In the classic Databricks deployment, where does the customer's source data reside?
- A. In the Databricks control plane
- B. In Databricks' cloud account
- C. In the customer's own cloud object storage account
- D. On the driver node's local disk

**Q3.** Which compute is used by Databricks SQL for BI/analyst queries?
- A. All-purpose cluster
- B. Job cluster
- C. SQL Warehouse
- D. Driver node

**Q4.** What does Photon provide?
- A. A new programming language
- B. A vectorized execution engine that speeds up SQL/DataFrame workloads without code changes
- C. A governance layer
- D. A streaming source

**Q5.** Which statement about the control plane is correct?
- A. It stores the customer's raw data
- B. It hosts backend services like the web UI, job scheduler, and cluster manager
- C. It runs inside the customer's VPC in serverless mode
- D. It is where Spark executors run

<details><summary>Answers 1–5</summary>

1. **B** — Lakehouse = cheap open lake storage + warehouse reliability/performance, enabled by Delta Lake.
2. **C** — Source data stays in the customer's cloud storage; Databricks reads it in place.
3. **C** — Databricks SQL runs on **SQL Warehouses**.
4. **B** — Photon is a vectorized engine; transparent to code, speeds up SQL/DataFrame work.
5. **B** — The control plane hosts backend services and metadata, not customer source data.
</details>

---

## Domain 1 — Clusters, Notebooks, Repos

**Q6.** You schedule a production job. Which cluster type is recommended and why?
- A. All-purpose cluster, because it stays running
- B. Job cluster, because it is created and terminated automatically with the job (lower cost, isolated)
- C. SQL Warehouse, because it's cheapest
- D. Single-node cluster, because production needs one machine

**Q7.** What is the difference between `%run` and `dbutils.notebook.run()`?
- A. They are identical
- B. `%run` executes the other notebook inline and shares its variables/functions; `dbutils.notebook.run()` runs it separately and returns only a string
- C. `%run` returns a DataFrame; `dbutils.notebook.run()` returns nothing
- D. `dbutils.notebook.run()` shares variables; `%run` does not

**Q8.** You **terminate** an all-purpose cluster. What happens?
- A. Its configuration is deleted permanently
- B. Compute stops but the configuration is retained; you can restart it
- C. All tables it created are dropped
- D. Nothing; it keeps running

**Q9.** Which magic command runs another language in a single notebook cell?
- A. `%md`
- B. `%sql`
- C. `%fs`
- D. `%sh`

<details><summary>Answers 6–9</summary>

6. **B** — Job clusters auto-create/terminate with the job → cheaper, isolated, fresh state.
7. **B** — `%run` = inline, shares variables; `dbutils.notebook.run()` = separate execution, returns a string only.
8. **B** — Terminate keeps the config (restartable); only *delete* removes it.
9. **B** — `%sql` runs SQL in that cell (`%md` is Markdown, `%fs` file system, `%sh` shell). Any of `%python/%sql/%scala/%r` switch language.
</details>

---

## Domain 1 — Delta Lake

**Q10.** You run `DROP TABLE t`. The underlying data files are still in storage afterward. What kind of table was `t`?
- A. Managed
- B. External
- C. Temporary
- D. Global temp view

**Q11.** Which command performs an atomic upsert (insert new + update existing) in one transaction?
- A. `INSERT INTO`
- B. `INSERT OVERWRITE`
- C. `MERGE INTO`
- D. `UNION ALL`

**Q12.** What two things physically make up a Delta table?
- A. CSV files + a manifest
- B. Parquet data files + a `_delta_log` transaction log
- C. ORC files + a Hive metastore entry
- D. JSON files + an index

**Q13.** After running `VACUUM t` with default settings, what is true?
- A. Time travel works infinitely into the past
- B. Data files unreferenced and older than 7 days are deleted, limiting time travel to that window
- C. The table is dropped
- D. Small files are compacted

**Q14.** Which command improves query performance by compacting many small files into fewer large ones?
- A. `VACUUM`
- B. `OPTIMIZE`
- C. `ZORDER`
- D. `ANALYZE`

**Q15.** By default, when you write a DataFrame with a different schema to an existing Delta table, what happens?
- A. New columns are silently added
- B. The write fails due to schema enforcement unless you enable `mergeSchema`
- C. The table is dropped and recreated
- D. Only matching columns are written, extras ignored silently

<details><summary>Answers 10–15</summary>

10. **B** — Dropping an **external** table removes only metadata; data files remain.
11. **C** — `MERGE INTO` = atomic upsert/CDC.
12. **B** — Parquet data + `_delta_log`.
13. **B** — VACUUM removes unreferenced files older than the retention period (default **7 days**), which limits time travel to that window.
14. **B** — `OPTIMIZE` compacts small files; `ZORDER` co-locates for filtering.
15. **B** — Schema enforcement fails the write; enable `mergeSchema` to evolve.
</details>

---

## Domain 2 — ELT with Spark SQL

**Q16.** How do you quickly query a self-describing JSON file directly without creating a table?
- A. `SELECT * FROM json.\`/path/to/file.json\``
- B. `LOAD json '/path'`
- C. `IMPORT '/path'`
- D. `OPEN json '/path'`

**Q17.** You create a table with `USING CSV ... OPTIONS (header="true") LOCATION '/path'`. Which is true?
- A. It is a managed Delta table
- B. It is a non-Delta external table that reads the CSV files directly
- C. It copies the CSV into Delta format
- D. It fails because CSV isn't supported

**Q18.** Which object stores a query definition (not data) and survives a cluster restart?
- A. Temp view
- B. Global temp view
- C. View (`CREATE VIEW`)
- D. CTE

**Q19.** You have a column `raw` containing JSON strings. Which operator navigates into it?
- A. Dot: `raw.field`
- B. Colon: `raw:field`
- C. Arrow: `raw->field`
- D. Bracket only: `raw[field]`

**Q20.** Which function turns each element of an array column into its own row?
- A. `flatten`
- B. `explode`
- C. `transform`
- D. `collect_list`

**Q21.** `UNION` vs `UNION ALL`?
- A. Both keep duplicates
- B. `UNION` removes duplicates; `UNION ALL` keeps them
- C. `UNION ALL` removes duplicates; `UNION` keeps them
- D. They are identical

<details><summary>Answers 16–21</summary>

16. **A** — `SELECT * FROM json.\`/path\`` queries files directly.
17. **B** — `USING CSV` + `LOCATION` = **non-Delta external table** reading files live (no ACID). Use CTAS to get a managed Delta copy.
18. **C** — A regular **view** persists in the metastore (temp/global-temp views don't survive; a CTE is one-query only).
19. **B** — Colon `:` for JSON-string columns; dot `.` for struct columns.
20. **B** — `explode` flattens an array into rows.
21. **B** — `UNION` dedups; `UNION ALL` keeps duplicates (and is faster).
</details>

---

## Domain 2 — ELT with PySpark

**Q22.** Which of these is an **action** (triggers execution)?
- A. `select`
- B. `filter`
- C. `withColumn`
- D. `count`

**Q23.** What does `df.withColumn("x2", col("x") * 2)` return?
- A. It mutates `df` in place
- B. A new DataFrame with the added column (df is immutable)
- C. A list of rows
- D. Nothing

**Q24.** What is the default save mode when writing a DataFrame to a new table/path?
- A. append
- B. overwrite
- C. errorifexists (fails if it already exists)
- D. ignore

**Q25.** Why prefer built-in Spark functions over Python UDFs?
- A. Python UDFs can't return strings
- B. Python UDFs are slower (JVM↔Python serialization) and opaque to the optimizer
- C. Built-in functions run only in SQL
- D. There is no difference

**Q26.** What does `collect()` do, and why be careful?
- A. Counts rows; it's always safe
- B. Brings **all** rows to the driver as a list; can OOM the driver on large data
- C. Writes the DataFrame to disk
- D. Registers a temp view

**Q27.** How do you make a DataFrame queryable via `spark.sql(...)`?
- A. `df.save()`
- B. `df.createOrReplaceTempView("v")`
- C. `df.toSQL()`
- D. `df.register()`

<details><summary>Answers 22–27</summary>

22. **D** — `count()` is an action; `select/filter/withColumn` are lazy transformations.
23. **B** — Returns a new DataFrame; DataFrames are immutable.
24. **C** — Default is `errorifexists` (fails if target exists).
25. **B** — UDFs serialize between JVM and Python and can't be optimized by Catalyst → slower.
26. **B** — `collect()` pulls everything to the driver; risky for big data.
27. **B** — `createOrReplaceTempView` bridges DataFrame → SQL.
</details>

---

## Domain 3 — Incremental Data Processing

**Q28.** What makes a Structured Streaming query fault-tolerant and exactly-once?
- A. The output mode
- B. The checkpoint location (tracks processed offsets so it resumes correctly)
- C. The trigger interval
- D. Autoscaling

**Q29.** Which trigger processes all currently available new data and then stops (ideal for scheduled incremental jobs)?
- A. `processingTime="1 hour"`
- B. `availableNow=True`
- C. default (no trigger)
- D. `continuous`

**Q30.** For a streaming aggregation that must show full running totals, which output mode is appropriate?
- A. append
- B. update
- C. complete
- D. overwrite

**Q31.** Which feature incrementally ingests new files from cloud storage, tracking which files were already processed?
- A. `spark.read.json` in a loop
- B. Auto Loader (`format("cloudFiles")`)
- C. `COPY INTO` only
- D. DBFS mount

**Q32.** In the medallion architecture, which layer holds cleaned, deduplicated, validated, and joined data?
- A. Bronze
- B. Silver
- C. Gold
- D. Platinum

**Q33.** In DLT, which expectation action **drops** rows that violate the constraint while letting the pipeline continue?
- A. `EXPECT` (no ON VIOLATION)
- B. `ON VIOLATION DROP ROW` / `expect_or_drop`
- C. `ON VIOLATION FAIL UPDATE` / `expect_or_fail`
- D. `IGNORE`

**Q34.** How do DLT tables reference each other to build the dependency graph?
- A. By file path
- B. With `LIVE.table_name` (SQL) or `dlt.read()/dlt.read_stream()` (Python)
- C. Through a config file
- D. They can't reference each other

<details><summary>Answers 28–34</summary>

28. **B** — The checkpoint location tracks offsets → fault tolerance + exactly-once.
29. **B** — `Trigger.AvailableNow` processes all new data then stops (best for scheduled incremental).
30. **C** — `complete` rewrites the full result table each trigger — needed for running totals.
31. **B** — Auto Loader with `cloudFiles` auto-tracks processed files.
32. **B** — Silver = cleaned/validated/deduped/joined. (Bronze = raw, Gold = business aggregates.)
33. **B** — `DROP ROW` removes bad rows, pipeline continues. Default keeps+tracks; `FAIL UPDATE` halts.
34. **B** — `LIVE.` / `dlt.read()` create dependencies.
</details>

---

## Domain 4 — Production Pipelines

**Q35.** A Databricks Job with multiple dependent tasks forms what?
- A. A single notebook
- B. A DAG of tasks (some sequential, some parallel)
- C. A cluster
- D. A view

**Q36.** After a job fails on its 3rd task, how do you re-run only the failed (and downstream) tasks?
- A. Recreate the job
- B. Use **Repair run**
- C. Delete and re-add each task
- D. Restart the cluster

**Q37.** How does a scheduled notebook read a parameter passed by the Job?
- A. `spark.conf.get`
- B. `dbutils.widgets.get("param")`
- C. `os.environ`
- D. `input()`

**Q38.** Which scheduling capabilities do Databricks Jobs natively support? (Select the best answer)
- A. Only manual runs
- B. Cron schedules, file-arrival triggers, and continuous mode
- C. Only external Airflow triggers
- D. Only API triggers

<details><summary>Answers 35–38</summary>

35. **B** — A multi-task job is a DAG.
36. **B** — **Repair run** re-executes only failed/downstream tasks.
37. **B** — `dbutils.widgets.get("param")`.
38. **B** — Jobs support cron, file-arrival triggers, and continuous mode natively.
</details>

---

## Domain 5 — Data Governance

**Q39.** Unity Catalog introduces a namespace with how many levels, and what are they?
- A. Two: `schema.table`
- B. Three: `catalog.schema.table`
- C. Four: `metastore.catalog.schema.table`
- D. One: `table`

**Q40.** A user has `SELECT` on a table but still can't query it. What's the most likely missing privilege?
- A. `MODIFY` on the table
- B. `USE CATALOG` on the catalog and `USE SCHEMA` on the schema
- C. Ownership of the metastore
- D. `CREATE TABLE`

**Q41.** Which Unity Catalog object governs access to **non-tabular files** (images, unstructured data)?
- A. Table
- B. View
- C. Volume
- D. Function

**Q42.** What governance capability does Unity Catalog provide automatically with no extra code?
- A. Data compression
- B. Table- and column-level data lineage
- C. Cluster autoscaling
- D. Cost optimization

**Q43.** Best practice: to whom should you grant privileges for manageability?
- A. Individual users
- B. Groups
- C. The metastore admin only
- D. Service principals only

<details><summary>Answers 39–43</summary>

39. **B** — `catalog.schema.table` (three levels) = Unity Catalog.
40. **B** — Needs the chain: `USE CATALOG` + `USE SCHEMA` + `SELECT`.
41. **C** — **Volumes** govern non-tabular/unstructured files.
42. **B** — UC captures table- and column-level lineage automatically.
43. **B** — Grant to **groups** for manageable access control.
</details>

---

Next: **[12 — Most Asked & Tricky Exam Questions](12_Most_Asked_and_Tricky_Exam_Questions.md)**.
