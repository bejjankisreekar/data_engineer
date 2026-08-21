# 🗺️ Storage Paradigms Map — Database → Warehouse → Data Lake → Lakehouse

**Start here if the words "database vs warehouse vs data lake vs lakehouse" blur together, or if you can't remember which folder a topic lives in.**

These four are the big "where does data live?" ideas in data engineering. They get mixed up constantly because they overlap — and in this repo they're taught in *learning order*, so they sit in different folders. This page is the single map that ties them together and tells you exactly where each one is.

---

## 👉 Which family does each one belong to? (read this first)

The simplest way to keep them straight — each paradigm belongs to **one of two families**, and that's exactly the folder it lives in:

| Paradigm | It is really a… | Family / Folder |
|---|---|---|
| 🗄️ **Database** | a **database** | 🟦 **Database** → `02_Databases` |
| 🏢 **Data Warehouse** | a **database** (a special one, built for analytics) | 🟦 **Database** → `02_Databases` |
| 🌊 **Data Lake** | **storage** | 🟩 **Storage** → `05_Storage_and_Formats` |
| 🏠 **Lakehouse** | **storage** (storage that gained a database's powers) | 🟩 **Storage** → `05_Storage_and_Formats` |

**In plain words:**
- **Data Warehouse is a *database* thing** → so it lives with the databases in `02_Databases`.
- **Data Lake and Lakehouse are *storage* things** → so they live with storage in `05_Storage_and_Formats`.
- A **Lakehouse = Data Lake (storage) + the powers of a Warehouse (database)** bolted on — which is why it's the odd one that blurs the two families. It's filed under **Storage** because underneath it's still just files in cheap storage.

---

## The 30-second picture

| # | Paradigm | One line | Everyday analogy |
|---|---|---|---|
| 1 | **Database (OLTP)** | Records live business transactions, one at a time, instantly | The **checkout till** — records each sale as it happens |
| 2 | **Data Warehouse** | Cleaned, organized data ready for reports & analytics | The **tidy store shelves** — unpacked, labeled, easy to shop |
| 3 | **Data Lake** | Cheap storage that holds *everything* raw, as-is | The **loading dock** — every delivery dumped in, unsorted |
| 4 | **Lakehouse** | A lake that learned the warehouse's tricks — one copy serves both | The **modern all-in-one building** — dock *and* shelves together |

> **The story in one breath:** raw data lands in the **lake**, gets cleaned into the **warehouse** for reports, while **databases** run the live app. The **lakehouse** is the modern move that merges the lake and warehouse into *one* system, so you don't keep two copies of everything.

---

## How they connect (the flow)

```
   Live app  ──▶  DATABASE (OLTP)        "what's in this cart right now?"
                      │
                      ▼  (raw data copied in)
                  DATA LAKE               "keep everything, decide later"
                      │
                      ▼  (clean / transform: ETL / ELT)
                  DATA WAREHOUSE          "total sales by region last year?"
                      │
                      ▼
                  Power BI / Reports

   ┌─────────────────────────────────────────────────────────┐
   │  LAKEHOUSE = Lake + Warehouse merged into ONE copy of    │
   │  data (via Delta) that serves BI, streaming, and ML.     │
   └─────────────────────────────────────────────────────────┘
```

---

## 📍 Where each topic lives in this repo

The content is spread across folders because you *learn* databases before lakehouses. Use this table to jump straight to any piece:

| Topic | Folder | Go to |
|---|---|---|
| **Database** (SQL, OLTP) | `02_Databases/SQL` | [What is a SQL Database](../02_Databases/SQL/02_SQL_Database.md) |
| **Data Warehouse** (fundamentals, marts, mesh) | `02_Databases/Data_Warehousing` | [Data Warehouse Fundamentals](../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md) |
| **Warehouse — SQL/modeling side** | `02_Databases/SQL` | [SQL Warehouse (star schema, SCD)](../02_Databases/SQL/13_SQL_Warehouse.md) |
| **Data Lake** (+ cloud storage) | `05_.../Data_Lakes_and_Storage` | [Azure Data Lake Storage](Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) |
| **All 3 compared** (Lake vs Warehouse vs DB) | `05_.../Data_Lakes_and_Storage` | ⭐ [Lake vs Warehouse vs Database](Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) |
| **Lakehouse** (Delta, medallion) | `05_.../Lakehouse` | ⭐ [Delta Lake vs Delta Table vs Lakehouse](Lakehouse/00_Delta_Lake_vs_Delta_Table_vs_Lakehouse.md) |
| **File formats** (Parquet, etc.) | `05_.../File_Formats` | [File Format Comparison](File_Formats/06_File_Format_Comparison.md) |

⭐ = the two deep-dive comparison notes — read these once and the whole picture clicks.

---

## Which deep-dive should I read?

- **"I mix up lake / warehouse / database"** → [Data Lake vs Warehouse vs Database](Data_Lakes_and_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md) *(covers the lakehouse too)*
- **"I mix up Delta Lake / Delta Table / Lakehouse"** → [Delta Lake vs Delta Table vs Lakehouse](Lakehouse/00_Delta_Lake_vs_Delta_Table_vs_Lakehouse.md)
- **"How is a warehouse actually built?"** → [Data Warehouse Fundamentals](../02_Databases/Data_Warehousing/01_Data_Warehouse_Fundamentals.md)
- **"How do I organize a lakehouse?"** → [Medallion Architecture (Bronze→Silver→Gold)](Lakehouse/04_Medallion_Architecture.md)

---

## In one line each (say this in an interview)

> **Database** = cheap-fast storage for *live* transactions (OLTP). **Warehouse** = governed, SQL-optimized store for *reports* (OLAP). **Data lake** = cheap open storage for *everything raw*. **Lakehouse** = a lake that gained ACID transactions (via Delta), so *one copy* of data serves BI, streaming, and ML — warehouse behavior at lake cost.
