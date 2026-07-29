# Data Warehouse Fundamentals

## What is a Data Warehouse?

A **Data Warehouse** is a central repository that collects, integrates, and stores data from many different source systems, structured specifically to support business analysis and reporting — not day-to-day transactions.

This note covers the warehouse as an **architecture** — its layers, the methodologies used to design one, and how it fits alongside other systems. For the SQL-level view (star schema, `SUM`/`GROUP BY` reporting queries, SCD Type 2) see [SQL Warehouse](../SQL/13_SQL_Warehouse.md); for the storage-pattern theory underneath it (columnar storage, OLAP internals) see [OLAP Storage](../../01_Foundations/Fundamentals/02_OLAP_Storage.md).

---

## The classic definition

Bill Inmon, widely credited as "the father of data warehousing," defined a data warehouse by four properties — still the cleanest way to describe one:

| Property | Meaning |
|---|---|
| **Subject-oriented** | Organized around business subjects (Customer, Product, Sales) — not around the applications that happen to produce the data |
| **Integrated** | Data from many inconsistent source systems is reconciled into one consistent format (one definition of "customer," one currency, one set of codes) |
| **Time-variant** | Every record is tied to a point in time; the warehouse holds *history*, not just the current state |
| **Non-volatile** | Once loaded, data isn't modified or deleted in normal operation — new facts are appended, not overwritten |

Analogy: imagine three regional offices each keeping their own paper ledgers, in their own formats, using their own product codes. A data warehouse is the head office's master ledger — every regional ledger's entries are translated into one consistent format, stamped with a date, and filed permanently. Nobody erases an old entry to "correct" it; a correction is a new entry.

---

## Where data comes from

```
ERP → CRM → HRMS → Sales System → Website Logs → APIs
                    │
                    ▼
              Data Warehouse
```

A warehouse doesn't generate its own data — it's filled by pipelines pulling from operational ([OLTP](../../01_Foundations/Fundamentals/01_OLTP_Storage.md)) systems and external sources. See [ETL vs ELT](../../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) and [Data Pipelines](../../05_Data_Engineering/ETL_ELT/03_Data_Pipelines.md) for how that loading actually happens.

---

## The layers of a warehouse system

```
Source Systems  →  Staging Area  →  (ODS)  →  Data Warehouse  →  Data Marts  →  BI / Reports
```

- **Staging area** — a temporary landing zone holding raw, as-extracted data, exactly as it arrived from the source. Nothing here is cleaned or modeled yet; it exists purely so a failed transformation can be re-run without re-extracting from the source system.
- **Operational Data Store (ODS)** — an optional layer sitting between source systems and the warehouse, holding *current, lightly integrated, near-real-time* operational data (not deeply historical or dimensionally modeled). Used when operational reporting needs data fresher than the warehouse's normal load cycle, without hitting production OLTP systems directly.
- **Data Warehouse** — the integrated, historical, subject-oriented store described above.
- **Data Marts** — smaller, department-focused subsets of the warehouse (its own topic: [Data Mart](02_Data_Mart.md)).

---

## Real World Example

A hospital network's data warehouse integrates patient records from five hospitals, each running a different Electronic Health Record system with different patient ID formats and different diagnosis code versions. The warehouse's job is to resolve all of that into one consistent "Patient" and "Diagnosis" definition, and to keep every historical admission on record — even for a patient who has since moved hospitals or whose diagnosis was later revised — so a "total admissions by diagnosis, last 5 years" report is possible at all.

---

## Azure Usage

**Azure Synapse Analytics** and **Microsoft Fabric Warehouse** are Microsoft's modern data warehouse products — both are SQL-based, MPP (massively parallel processing) engines built for exactly this subject-oriented, integrated, historical workload. See [SQL Warehouse](../SQL/13_SQL_Warehouse.md) for MPP distribution details (HASH/ROUND_ROBIN/REPLICATE).

---
---

# Part 2 — Advanced

## Warehouse architecture tiers

| Tier | Shape | Trade-off |
|---|---|---|
| **Single-tier** | Source systems feed directly into one warehouse layer, minimal separation | Simple, but source changes ripple straight into reporting; rarely used in practice |
| **Two-tier** | Staging + warehouse, no separate mart layer | Common in smaller estates |
| **Three-tier** | Staging → warehouse → data marts, each layer serving a distinct purpose | The standard enterprise pattern — separates raw landing, integrated history, and department-facing consumption |

The three-tier shape maps directly onto the [medallion architecture](../../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) used in modern lakehouses (staging ≈ bronze, warehouse ≈ silver, marts ≈ gold) — the *names* changed with the technology, but the layering logic that Inmon described in the 1990s is the same reasoning that produced bronze/silver/gold decades later.

## Two competing methodologies: Inmon vs Kimball

The two classic, opposed approaches to *building* a warehouse:

| | Inmon (top-down / CIF) | Kimball (bottom-up / dimensional bus) |
|---|---|---|
| Starting point | Build one normalized, enterprise-wide warehouse first | Build individual dimensional data marts first, conformed to share dimensions |
| Data marts | *Dependent* — extracted from the central warehouse afterward | The warehouse effectively *is* the union of well-designed marts |
| Design style | Highly normalized (3NF) at the core | Denormalized star schemas throughout ([star schema detail](../SQL/13_SQL_Warehouse.md)) |
| Time to first value | Slower — the enterprise model must be designed first | Faster — one department's mart can ship in weeks |
| Consistency risk | Low — one central model | Higher — marts can drift unless dimensions are deliberately *conformed* (shared Date/Customer/Product dimensions reused across every mart) |

Inmon's approach is called the **Corporate Information Factory (CIF)** — a fully normalized enterprise data warehouse at the center, with dependent data marts drawn from it. Kimball's is the **dimensional bus architecture** — a shared set of "conformed dimensions" acts as the bus that every subject-area mart plugs into, so they can be combined and compared even though no single normalized model was built first.

## Why most real projects end up hybrid

In practice, few organizations follow either methodology purely: teams often build Kimball-style star schemas (for speed and BI-friendliness) while still maintaining Inmon-style discipline around a single integrated staging/ODS layer (for consistency) — getting the fast time-to-value of dimensional modeling without the "spreadmart" drift that pure independent marts risk (see [Data Mart](02_Data_Mart.md) for that failure mode in detail).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## The cloud didn't change the theory — it changed the storage engine

Everything Inmon and Kimball described (staging, integration, conformed dimensions, marts) is exactly what a modern [lakehouse](../../01_Foundations/Fundamentals/06_Big_Data_Evolution_Timeline.md) still does — the only genuine change is *where* the data physically lives and what engine reads it. A Delta/Iceberg gold layer exposed as views is functionally a Kimball-style dimensional mart; a silver layer with conformed keys is functionally an ODS/integration layer. Anyone who's designed a warehouse the "old way" can transfer that judgment directly onto a modern stack — the vocabulary shifted, the discipline didn't.

## Choosing Inmon vs Kimball vs hybrid in a real design review

- **Small team, fast-moving business, BI is the main consumer** → Kimball-style dimensional bus. Ship a star schema per subject area quickly; invest in conformed dimensions from day one so marts stay comparable.
- **Large enterprise, many downstream consumers (BI, ML, regulatory reporting), consistency is non-negotiable** → Inmon-style central integration layer first, marts derived from it — slower to first report, but avoids the multi-year "which number is right" tax of drifted independent marts.
- **Most 2020s teams** → a lakehouse medallion architecture that borrows Inmon's discipline (one governed silver layer, conformed keys) and Kimball's speed (star-schema gold marts built fast on top of it).

## Field-tested gotchas

- **Skipping the staging layer** to "save a step" removes your only safe place to re-run a broken transformation without re-hitting the source system — see the [raw retention discipline](../../05_Data_Engineering/ETL_ELT/01_ETL_vs_ELT.md) this maps to.
- **An ODS built without a retention/archival policy quietly becomes a second warehouse** — nobody decided that, it just accumulated history because deleting felt risky. Decide ODS retention explicitly.
- **"We'll conform the dimensions later"** never happens under deadline pressure — conformed dimensions (shared Date, Customer, Product keys across every mart) are dramatically cheaper to design *before* the second mart exists than to retrofit across five marts that have already diverged.
- Time-variance is often only partially implemented — teams build SCD Type 2 on customer dimensions but forget it on product dimensions, silently losing "what did this product cost when it was sold" accuracy.

## Interview-grade Q&A

- *What are the four defining properties of a data warehouse?* Subject-oriented, integrated, time-variant, non-volatile (Inmon's definition).
- *Inmon vs Kimball, in one line?* Top-down normalized-core-first vs bottom-up dimensional-marts-first, reconciled through conformed dimensions.
- *What is an ODS, and why not just query it instead of building a warehouse?* A lightly integrated, current-state operational layer — it lacks the deep history and dimensional modeling a warehouse provides, so it complements rather than replaces one.
- *How does the medallion architecture relate to classic warehouse theory?* It's the same staging → integration → consumption layering Inmon described, implemented on lake storage instead of a relational engine.

Next: the department-facing consumption layer → [Data Mart](02_Data_Mart.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Data warehousing (Azure Architecture Center): https://learn.microsoft.com/en-us/azure/architecture/data-guide/relational-data/data-warehousing
- What is a data warehouse? (Databricks): https://www.databricks.com/glossary/data-warehouse
- Star vs snowflake schema: https://www.databricks.com/glossary/star-schema
- Kimball dimensional modeling: https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/

**Videos**
- Data warehouse concepts & dimensional modeling: https://www.youtube.com/results?search_query=data+warehouse+dimensional+modeling+star+snowflake+schema
- Fact vs dimension tables: https://www.youtube.com/results?search_query=fact+table+vs+dimension+table+explained
