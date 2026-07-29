# Data Lake — Interview Questions

## Overview
A data lake stores raw data of any type at low cost in object storage (ADLS Gen2), the landing zone of the platform. Interviews test lake vs warehouse, zones, the "data swamp" risk, and governance.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is a data lake? | 🟢 | ★★★★★ |
| 2 | Data lake vs data warehouse? | 🟢 | ★★★★★ |
| 3 | Zones (raw/curated) / medallion? | 🟡 | ★★★★★ |
| 4 | Schema-on-read vs schema-on-write? | 🟡 | ★★★★☆ |
| 5 | What is a "data swamp"? How to avoid? | 🟡 | ★★★★☆ |
| 6 | File formats & partitioning in the lake? | 🟡 | ★★★★☆ |
| 7 | Governance & security in a lake? | 🔴 | ★★★★☆ |
| 8 | Data lake vs lakehouse? | 🟡 | ★★★★☆ |

## Key Answers
- **Q1:** Centralized store for **all data types** (structured/semi/unstructured) at scale and low cost, in open formats — no schema required on write. On Azure = **ADLS Gen2**.
- **Q4:** **Schema-on-read** (lake) = apply schema when you query (flexible). **Schema-on-write** (warehouse) = enforce on load (reliable). Lakehouse adds schema enforcement on the lake via Delta.
- **Q5:** A **data swamp** = ungoverned lake nobody can trust/find data in. Avoid with **zones, naming standards, cataloging (Purview), governance (Unity Catalog), and Delta for reliability**.
- **Q8:** Lake = cheap raw storage without ACID/governance guarantees; **lakehouse** adds warehouse reliability (Delta) on top.

## Scenario Questions
- **"Organize a new lake."** Zones: raw/Bronze → Silver → Gold; partition by date; consistent naming; Parquet/Delta; catalog + RBAC.
- **"The lake became unusable."** Data swamp → introduce governance, cataloging, Delta tables, ownership.
- **"Secure the lake."** RBAC + ACLs + Managed Identity + private endpoints (see ADLS Gen2 notes).

## Quick Revision
- ✔ Data lake = all data types, low cost, open formats, **schema-on-read**
- ✔ Warehouse = structured, schema-on-write, curated
- ✔ Zones: **Bronze/Silver/Gold**; partition by date
- ✔ Avoid **data swamp** with governance + catalog + Delta
- ✔ Lakehouse = lake + warehouse reliability (Delta)
- ✔ Azure lake = **ADLS Gen2**

## Common Mistakes
- Treating the lake as a dumping ground (swamp).
- No zones/naming/governance.
- Confusing lake vs lakehouse.

## Senior-Level
Seniors design a governed, zoned lake on ADLS Gen2 with Delta reliability, cataloging (Purview/Unity Catalog), security (RBAC/ACL/private endpoints), and lifecycle/cost management — evolving lake → lakehouse.

## Related Topics
ADLS Gen2, Lakehouse, Delta Lake, Data Warehousing, ETL vs ELT
