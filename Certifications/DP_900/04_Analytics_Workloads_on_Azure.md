# 04 — Analytics Workloads on Azure

*Domain: Analytics workloads on Azure (25–30%)*

---

## What it is

This domain is about turning raw data into **insight** — the modern data-warehouse/analytics architecture and the Azure services that implement each stage: **ingest → store → process → model → visualize**. It's the largest, most service-heavy domain, and it maps directly onto the platforms this repo covers in depth.

---

## Modern data warehouse / analytics architecture

```
Sources ─► INGEST ─► STORE ─► PROCESS/TRANSFORM ─► MODEL/SERVE ─► VISUALIZE
           (ADF /    (ADLS    (Synapse Spark /     (Synapse SQL /  (Power BI)
            pipelines) Gen2)    Databricks)          Fabric WH)
```

Every analytics solution is some version of this flow. Know which Azure service plays each role.

---

## The core Azure analytics services

| Service | Role | Repo deep-dive |
|---|---|---|
| **Azure Data Factory (ADF)** | Cloud **ingestion & orchestration** (ETL/ELT pipelines, low-code) | [ADF](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) |
| **Azure Data Lake Storage Gen2** | Scalable **storage** for raw/curated analytics data | [ADLS](../../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md) |
| **Azure Synapse Analytics** | Unified **warehouse + Spark + pipelines** platform | [Synapse](../../10_Synapse_and_Fabric/01_Azure_Synapse_Analytics.md) |
| **Azure Databricks** | Apache **Spark** big-data processing & ML (lakehouse) | [Databricks](../../08_Databricks/01_What_is_Databricks.md) |
| **Microsoft Fabric** | All-in-one **SaaS analytics** on OneLake (Synapse's successor) | [Fabric](../../10_Synapse_and_Fabric/03_Microsoft_Fabric.md) |
| **Power BI** | **Visualization** — reports & dashboards | this note |

> **Exam Tip:** Map the keyword to the service — *pipelines / move & orchestrate data* → **Data Factory**; *big-data Spark processing* → **Databricks**; *data warehouse / SQL analytics* → **Synapse**; *unified SaaS analytics + OneLake* → **Fabric**; *dashboards / visuals* → **Power BI**; *store huge analytics data* → **ADLS Gen2**.

---

## ETL vs ELT

- **ETL** — Extract → **Transform** → Load (transform *before* loading; classic warehouse).
- **ELT** — Extract → Load → **Transform** (load raw first, transform in the target; modern lake/lakehouse).

Full note: [ETL vs ELT](../../06_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md).

> **Exam Tip:** ELT loads raw data first and transforms it *inside* the destination (data lake/warehouse) — the modern big-data pattern. ETL transforms *before* loading.

---

## Batch vs stream processing (analytics context)

- **Batch** — scheduled processing of collected data (ADF, Synapse/Databricks Spark jobs).
- **Stream / real-time** — continuous processing (**Event Hubs/IoT Hub** → **Stream Analytics** or Spark) for live dashboards and alerts. See [Streaming](../../09_Streaming/00_Streaming_Learning_Path.md).

---

## Power BI essentials

Power BI is Microsoft's **data-visualization** and business-intelligence tool. Know the pieces:

| Component | What it is |
|---|---|
| **Power BI Desktop** | Windows authoring app — build models, transform data (Power Query), create reports |
| **Power BI Service** | Cloud SaaS — publish, share, and view reports/dashboards |
| **Power BI Mobile** | Mobile apps for viewing |
| **Report** | Multi-page, interactive visuals over one dataset |
| **Dashboard** | Single-page canvas pinning visuals from one or more reports (Service only) |
| **Dataset / Semantic model** | The data + relationships + measures a report is built on |

**The workflow:** connect to data → transform (Power Query) → model (relationships, DAX measures) → visualize (Desktop) → publish → share (Service).

> **Exam Tip:** **Report** = multi-page, built in Desktop, over one dataset. **Dashboard** = single-page, in the Service, pins visuals possibly from *many* reports. Authoring happens in **Desktop**; sharing/consuming in the **Service**.

> **Exam Tip:** In Fabric, Power BI can use **Direct Lake** to read Delta from OneLake directly — import-speed *and* live freshness ([Fabric](../../10_Synapse_and_Fabric/03_Microsoft_Fabric.md)).

---

## Types of data analytics

A commonly tested "ladder" of analytics maturity:

| Type | Answers | Example |
|---|---|---|
| **Descriptive** | What happened? | Last month's sales report |
| **Diagnostic** | Why did it happen? | Why sales dropped in region X |
| **Predictive** | What will happen? | Forecast next quarter's demand |
| **Prescriptive** | What should we do? | Recommend the optimal price |
| **Cognitive** | Apply AI/reasoning | Sentiment from support tickets |

> **Exam Tip:** Descriptive = past, Diagnostic = why, Predictive = future, Prescriptive = recommended action. Order them lowest→highest maturity.

---

## Quick Review

- Analytics flow: **ingest (ADF) → store (ADLS) → process (Synapse/Databricks Spark) → serve (Synapse/Fabric WH) → visualize (Power BI)**.
- **ADF** = orchestration/ETL; **Databricks** = Spark; **Synapse** = warehouse+Spark; **Fabric** = SaaS analytics on OneLake; **Power BI** = visuals.
- **ETL** transforms before load; **ELT** loads raw then transforms in the target.
- Power BI: **Desktop** authors, **Service** shares; **Report** = multi-page over one dataset, **Dashboard** = single-page pinning many.
- Analytics types: **Descriptive → Diagnostic → Predictive → Prescriptive → Cognitive**.
- Real-time analytics: **Event Hubs → Stream Analytics**.

---

## Further Learning — Docs & Videos

- Explore analytics workloads on Azure (Learn): https://learn.microsoft.com/en-us/training/paths/azure-data-fundamentals-explore-data-warehouse-analytics/
- Power BI overview: https://learn.microsoft.com/en-us/power-bi/fundamentals/power-bi-overview
- Video search: https://www.youtube.com/results?search_query=dp-900+analytics+workloads+power+bi

---

Next: **[05 — Practice Questions by Domain](05_Practice_Questions_by_Domain.md)**.
