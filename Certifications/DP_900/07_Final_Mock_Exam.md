# 07 — Final Mock Exam

30 questions across all four domains. Give yourself ~35 minutes, no notes. Answers with brief explanations at the bottom — don't peek until you've finished.

---

1. Which type of data has a flexible schema with tags or keys, such as JSON?
   A) Structured B) Semi-structured C) Unstructured D) Relational

2. A system that records thousands of small customer purchases per second is:
   A) OLAP B) A data warehouse C) OLTP D) A data lake

3. Which role designs and builds data pipelines?
   A) Data Analyst B) DBA C) Data Engineer D) Developer

4. Which format is columnar and best for analytics?
   A) CSV B) JSON C) Parquet D) XML

5. Which is a characteristic of streaming data?
   A) Processed on a nightly schedule B) Bounded dataset C) Processed continuously as it arrives D) Always stored as CSV

6. Which SQL category does `SELECT` belong to?
   A) DDL B) DML C) DQL D) DCL

7. Which service offers the least management overhead for a new relational cloud database?
   A) SQL Server on VM B) Azure SQL Managed Instance C) Azure SQL Database D) Azure Cosmos DB

8. You must migrate an on-prem SQL Server using SQL Agent jobs with minimal code change. Choose:
   A) Azure SQL Database B) Azure SQL Managed Instance C) Cosmos DB D) Azure Database for MySQL

9. Which purchasing/compute option auto-pauses when idle to save cost?
   A) Provisioned B) Elastic pool C) Serverless D) DTU

10. `CREATE TABLE` is which SQL category?
    A) DDL B) DML C) DQL D) DCL

11. Which Azure Storage service holds messages for decoupling app components?
    A) Blob B) File C) Table D) Queue

12. What does ADLS Gen2 add over standard Blob Storage?
    A) SQL query engine B) Hierarchical namespace C) Global replication D) Graph API

13. Which Cosmos DB API is best for graph data?
    A) NoSQL/Core B) MongoDB C) Gremlin D) Table

14. For data accessed roughly once a year at lowest storage cost:
    A) Hot B) Cool C) Cold D) Archive

15. Which is a key benefit of Cosmos DB?
    A) OS-level access B) Global distribution with low latency C) Free unlimited storage D) Columnar analytics engine

16. Which NoSQL store type uses nodes and edges?
    A) Key-value B) Document C) Column-family D) Graph

17. Which service orchestrates ETL/ELT pipelines with a low-code interface?
    A) Power BI B) Azure Data Factory C) Cosmos DB D) Azure SQL Database

18. ELT differs from ETL because it:
    A) Never transforms data B) Transforms before loading C) Loads raw data first, then transforms D) Only works on streaming

19. Which service is Apache Spark-based for big-data processing and ML?
    A) Azure Databricks B) Power BI C) Azure SQL Database D) Event Hubs

20. Microsoft's unified SaaS analytics platform built on OneLake is:
    A) Synapse B) Databricks C) Microsoft Fabric D) HDInsight

21. In Power BI, where do you primarily author reports?
    A) Power BI Service B) Power BI Desktop C) Power BI Mobile D) Excel

22. A single-page canvas that pins visuals from multiple reports is a:
    A) Report B) Dataset C) Dashboard D) Workspace

23. "What will next quarter's sales be?" is which analytics type?
    A) Descriptive B) Diagnostic C) Predictive D) Prescriptive

24. Which two services fit real-time ingest + processing? (choose the pair)
    A) ADF + Power BI B) Event Hubs + Stream Analytics C) Blob + Cosmos DB D) Synapse + Power BI

25. Which storage is optimized for large-scale analytics data lakes?
    A) Azure Files B) Table Storage C) ADLS Gen2 D) Queue Storage

26. Normalization primarily aims to:
    A) Speed up all queries B) Reduce data redundancy C) Add columns D) Encrypt data

27. A primary key:
    A) Links to another table B) Uniquely identifies each row C) Speeds up all joins D) Stores JSON

28. Which is unstructured data?
    A) A relational table B) A JSON document C) A video file D) A CSV with a header

29. Which Power BI mode reads Delta directly from OneLake for speed and freshness?
    A) Import B) DirectQuery C) Direct Lake D) Live

30. Which analytics type recommends the best action to take?
    A) Descriptive B) Diagnostic C) Predictive D) Prescriptive

---

## Answer key

| # | Ans | Why |
|---|---|---|
| 1 | B | JSON with tags/keys = semi-structured. |
| 2 | C | High-volume small transactions = OLTP. |
| 3 | C | Data engineer builds pipelines. |
| 4 | C | Parquet is columnar/analytics. |
| 5 | C | Streaming = continuous as data arrives. |
| 6 | C | `SELECT` = DQL. |
| 7 | C | Azure SQL Database = fully managed, least admin. |
| 8 | B | Managed Instance = high-compat migration. |
| 9 | C | Serverless auto-pauses when idle. |
| 10 | A | `CREATE TABLE` = DDL. |
| 11 | D | Queue Storage = messaging/decoupling. |
| 12 | B | Hierarchical namespace for analytics. |
| 13 | C | Gremlin = graph API. |
| 14 | D | Archive = cheapest, rarely accessed. |
| 15 | B | Global distribution, low latency. |
| 16 | D | Graph = nodes + edges. |
| 17 | B | Azure Data Factory orchestrates pipelines. |
| 18 | C | ELT loads raw first, transforms in target. |
| 19 | A | Databricks = Spark. |
| 20 | C | Fabric = SaaS on OneLake. |
| 21 | B | Authoring in Power BI Desktop. |
| 22 | C | Dashboard pins from many reports. |
| 23 | C | Predictive = future forecast. |
| 24 | B | Event Hubs ingest + Stream Analytics process. |
| 25 | C | ADLS Gen2 for analytics lakes. |
| 26 | B | Normalization reduces redundancy. |
| 27 | B | Primary key uniquely identifies rows. |
| 28 | C | Video = unstructured. |
| 29 | C | Direct Lake reads OneLake Delta directly. |
| 30 | D | Prescriptive = recommended action. |

**Scoring:** 21/30 ≈ 700/1000 (passing zone). Aim for 26+ before booking. Re-read any domain where you miss more than one.

---

You've finished the DP-900 track. For the associate-level next step, see **[DP-700 — Fabric Data Engineer](../DP_700_Fabric_Data_Engineer/00_DP700_Study_Guide_Overview.md)**.
