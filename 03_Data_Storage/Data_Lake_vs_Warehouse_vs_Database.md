# Data Lake vs Data Warehouse vs Database

## Why compare all three?

By now you've met the [SQL Database](../01_SQL/SQL_Database.md) and the [SQL Warehouse](../01_SQL/SQL_Warehouse.md). This note adds a third storage pattern — the **Data Lake** — and lines up all three side by side, because beginners often mix them up. They solve different problems and are frequently used *together* in the same company.

---

## Analogy: a retail business

Think of a supermarket chain:

- **Database** = the checkout till at each store. It records "this customer bought these items right now," and needs to be instantly accurate and fast, one transaction at a time.
- **Data Lake** = the loading dock behind the supermarket. Every delivery — boxes, crates, pallets, in whatever packaging the supplier used — gets dropped off here as-is, unsorted, before anyone decides what to do with it.
- **Data Warehouse** = the neatly organized store shelves. Everything has been unpacked, cleaned, labeled, and arranged so a shopper (or in data terms, a business analyst) can quickly find exactly what they need.

---

## What is a Data Lake?

A Data Lake is large-scale storage that holds data in its **original, raw form** — structured, semi-structured, or unstructured — before anyone has cleaned or organized it.

Examples of what lands in a data lake:

- Raw [CSV](../02_File_formats/CSV.md) exports from an old system
- [JSON](../02_File_formats/JSON.md) files from an API
- Photos, PDFs, videos
- [Parquet](../02_File_formats/Parquet.md) files converted from streaming data

Nothing needs to be cleaned or structured before it's allowed into a data lake — that's the point. Store first, decide what to do with it later.

---

## Side-by-Side

| | Database | Data Lake | Data Warehouse |
|---|---|---|---|
| Data type | Structured only | Any (raw, unstructured, structured) | Structured only |
| Data state | Current, live | Raw, unprocessed | Cleaned, organized |
| Optimized for | Fast transactions (OLTP) | Cheap, flexible storage at scale | Fast analytics (OLAP) |
| Typical user | Application, end customer | Data engineer | Business analyst |
| Example question it answers | "What's in this customer's cart right now?" | "Do we even have last year's server logs saved somewhere?" | "What were total sales by region last year?" |

---

## How they connect

```
Applications (SQL Databases)
        ↓
Data Lake (raw storage, everything dumped in as-is)
        ↓
Cleaning / Transformation (ETL or ELT)
        ↓
Data Warehouse (organized, ready for analysis)
        ↓
Power BI / Reports
```

Raw data usually lands in the lake first — cheaply and without needing a plan — and only the data worth analyzing gets cleaned and moved into the warehouse.

---

## Azure Equivalents

| Concept | Azure Service |
|---|---|
| Database | Azure SQL Database |
| Data Lake | Azure Data Lake Storage (see [Azure_Data_Lake_Storage.md](Azure_Data_Lake_Storage.md)) |
| Data Warehouse | Azure Synapse Analytics / Microsoft Fabric Warehouse |

---

## Real World Example

A hospital's patient-monitoring devices constantly stream raw sensor readings into a **data lake** — heart rate, oxygen level, timestamps, in whatever format the devices produce. Overnight, a pipeline cleans and aggregates that raw data — flagging abnormal readings, calculating daily averages — and loads the results into a **data warehouse** for doctors and administrators to review in dashboards. Meanwhile, the hospital's patient records **database** keeps handling day-to-day tasks: registering a new patient, booking an appointment, updating a chart, all in real time.
