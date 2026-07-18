# Azure Data Factory (ADF)

## What is it?

Azure Data Factory is Azure's tool for building, scheduling, and monitoring data pipelines — largely through a visual, drag-and-drop interface rather than writing code from scratch.

Analogy: if moving and transforming data is an assembly line, Data Factory is the control room where you design the assembly line's layout, set it running on a schedule, and watch a dashboard to confirm every station did its job.

---

## Core Building Blocks

| Term | What it means |
|---|---|
| Pipeline | The overall workflow — a sequence of steps (activities) that run in order |
| Activity | A single step inside a pipeline, e.g. "copy this file" or "run this transformation" |
| Dataset | A pointer to a specific piece of data an activity reads or writes (a table, a file, a folder) |
| Linked Service | The connection details for a data source or destination (like a saved login for a database or storage account) |
| Trigger | What starts a pipeline running — a schedule (every night at 2am), or an event (a new file arrives) |

---

## A Simple Example Pipeline

```
Trigger: every night at 2 AM
   ↓
Activity 1: Copy sales data from an on-premises SQL Database
   ↓
Activity 2: Copy the data into Azure Data Lake Storage (raw layer)
   ↓
Activity 3: Run a transformation (e.g. via Databricks) to clean the data
   ↓
Activity 4: Load the cleaned result into Azure Synapse Analytics
```

This is a textbook [ETL/ELT](ETL_vs_ELT.md) pipeline, built entirely by connecting boxes on a canvas rather than writing custom scripts for every step.

---

## Why not just write a script?

You could write a custom program to move and transform data instead. Data Factory earns its place by handling the parts every pipeline eventually needs, without you building them yourself:

- **Scheduling** — run automatically every night, every hour, or the moment a file lands
- **Monitoring** — a dashboard showing which runs succeeded, failed, or are still running
- **Retry logic** — automatically retry a step that failed due to a temporary network issue
- **Connectors** — pre-built connections to hundreds of data sources (SQL Server, Salesforce, SAP, Amazon S3, and more), so you don't write custom connection code for each one

---

## Copy Activity vs Mapping Data Flow

- **Copy Activity** — moves data from A to B with little or no transformation. Fast, simple, the workhorse of most pipelines.
- **Mapping Data Flow** — a visual way to define actual transformation logic (filtering rows, joining tables, aggregating values) without writing Spark code directly; ADF runs it on a Spark cluster behind the scenes.

---

## Azure Usage

Data Factory typically sits at the center of an Azure data platform, connecting:

- Source systems (on-premises databases, SaaS apps, APIs)
- [Azure Data Lake Storage](../03_Data_Storage/Azure_Data_Lake_Storage.md) (raw storage)
- Azure Databricks (heavy transformation)
- Azure Synapse Analytics (final, query-ready warehouse)

---

## Real World Example

A logistics company has package-tracking data sitting in an old on-premises database that only their internal warehouse staff can query. Every night, a Data Factory pipeline copies that day's tracking data into Azure Data Lake Storage, triggers a Databricks job to calculate on-time delivery rates, and loads the result into Synapse — so that by the time the operations team arrives in the morning, a Power BI dashboard already shows yesterday's performance, without anyone manually running a single query.
