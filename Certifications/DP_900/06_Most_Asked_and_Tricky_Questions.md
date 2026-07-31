# 06 — Most Asked & Tricky Questions

The comparison pairs and confusions that decide most DP-900 wrong answers. Learn to tell each pair apart instantly.

---

## The confusable pairs

**1. OLTP vs OLAP**
OLTP = transactions, current data, many small writes, normalized, row-based (the app's database). OLAP = analytics, historical data, big aggregating reads, denormalized, columnar (the warehouse).

**2. Structured vs semi-structured vs unstructured**
Structured = fixed schema tables. Semi-structured = JSON/XML (self-describing, flexible). Unstructured = images/video/audio/free text. *A JSON document is semi-structured, not unstructured.*

**3. ETL vs ELT**
ETL transforms **before** loading (classic warehouse). ELT loads raw **then** transforms in the destination (modern lake/lakehouse).

**4. Batch vs streaming**
Batch = bounded data, scheduled. Streaming = unbounded data, continuous, real-time.

**5. Azure SQL Database vs SQL Managed Instance vs SQL Server on VM**
Azure SQL Database = fully managed, cloud-native, least admin. Managed Instance = high SQL Server compatibility for migrations (PaaS). SQL Server on VM = full control, OS access (IaaS).

**6. Blob Storage vs ADLS Gen2**
Both store objects; **ADLS Gen2 adds a hierarchical namespace** for analytics. Blob = general object storage.

**7. Blob tiers: Hot vs Cool vs Cold vs Archive**
Hot = frequent access, highest storage cost/lowest access cost. Cool/Cold = infrequent. Archive = rarely accessed, cheapest storage, retrieval latency.

**8. Cosmos DB APIs**
NoSQL/Core (document, default), MongoDB (Mongo apps), Cassandra (column-family), Gremlin (graph), Table (key-value). Pick by existing data model/app.

**9. Power BI Report vs Dashboard**
Report = multi-page, Desktop-authored, one dataset. Dashboard = single-page, Service-only, pins visuals from possibly many reports.

**10. Power BI Desktop vs Service**
Desktop = author (model + build). Service = publish, share, consume, and build dashboards.

**11. Synapse vs Databricks vs Fabric**
Synapse = unified warehouse+Spark platform. Databricks = best Spark/lakehouse. Fabric = SaaS successor to Synapse on OneLake with Power BI built in.

**12. Data roles**
DBA = manage/secure databases. Data Engineer = build pipelines/storage. Data Analyst = build reports/visuals.

---

## Keyword → answer cheat sheet

| Scenario keyword | Answer |
|---|---|
| Move/orchestrate data, low-code pipelines | **Azure Data Factory** |
| Big-data Spark processing / ML | **Azure Databricks** |
| Data warehouse / SQL analytics | **Azure Synapse Analytics** |
| Unified SaaS analytics, OneLake | **Microsoft Fabric** |
| Dashboards & reports | **Power BI** |
| Massive analytics storage | **ADLS Gen2** |
| Global, low-latency NoSQL | **Cosmos DB** |
| Graph data | **Cosmos DB Gremlin API** |
| Fully-managed relational, least admin | **Azure SQL Database** |
| Migrate on-prem SQL Server, high compatibility | **SQL Managed Instance** |
| Need OS access to SQL Server | **SQL Server on VM** |
| Rarely accessed, cheapest storage | **Archive** blob tier |
| Real-time ingest | **Event Hubs / IoT Hub** |
| Real-time processing | **Stream Analytics** |
| Cheap intermittent DB, pay-when-used | **Serverless Azure SQL Database** |

---

## Tricky yes/no traps

- "ADLS Gen2 is a NoSQL database." → **No** — it's file/object storage with a hierarchical namespace.
- "A dashboard can combine visuals from multiple reports." → **Yes** (a report cannot span multiple datasets, but a dashboard can pin from many reports).
- "ELT transforms data before loading it." → **No** — that's ETL; ELT loads first.
- "Cosmos DB guarantees single-digit-millisecond latency." → **Yes** (with SLAs).
- "Archive tier data is available for immediate read." → **No** — it must be rehydrated (retrieval latency).
- "Azure SQL Database gives you OS-level access." → **No** — that's SQL Server on a VM (IaaS).

---

Next: **[07 — Final Mock Exam](07_Final_Mock_Exam.md)**.
