# Microsoft Purview — Interview Questions

## Overview
Microsoft Purview (formerly Azure Purview) is the unified **data governance** service: catalog, discovery, classification, lineage, and sensitivity labeling across the estate. In DE interviews it's the "how do you govern/catalog/track lineage" answer.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Purview? What problems does it solve? | 🟢 | ★★★★★ |
| 2 | Data Map vs Data Catalog? | 🟡 | ★★★★☆ |
| 3 | How does scanning & classification work? | 🟡 | ★★★★☆ |
| 4 | Data lineage — how is it captured? | 🔴 | ★★★★☆ |
| 5 | Sensitivity labels / PII classification? | 🟡 | ★★★★☆ |
| 6 | Purview vs Unity Catalog? | 🔴 | ★★★☆☆ |
| 7 | Business glossary? | 🟢 | ★★★☆☆ |
| 8 | How does it integrate with ADF/Synapse? | 🟡 | ★★★☆☆ |

## Key Answers
- **Q1:** Centralized governance — **discover, classify, catalog, and track lineage** of data across ADLS, SQL, Synapse, Power BI, and on-prem/multi-cloud. Answers "what data do we have, where, who owns it, is it sensitive, where did it come from."
- **Q3:** Purview **scans** registered sources on a schedule, extracts metadata, and applies **classifications** (built-in/custom rules for PII like SSN, credit card).
- **Q4:** Lineage is captured from **ADF/Synapse pipeline runs** and other connectors, showing source→transform→sink flow for impact analysis and compliance.
- **Q6:** **Unity Catalog** governs Databricks data (access control + lineage within the lakehouse); **Purview** is broader estate-wide cataloging/classification. They complement each other.

## Scenario Questions
- **"Auditor asks where a PII column originated."** Purview **lineage** + classification traces source→Gold.
- **"Find all datasets containing credit-card data."** Classification search in the catalog.
- **"Give analysts a searchable catalog with owners/glossary."** Purview Data Catalog + business glossary.

## Quick Revision
- ✔ Purview = estate-wide **catalog + classification + lineage + labels**
- ✔ **Data Map** (metadata graph) + **Data Catalog** (search/browse)
- ✔ **Scans** discover & **classify** (PII rules)
- ✔ **Lineage** from ADF/Synapse for impact/compliance
- ✔ Complements **Unity Catalog** (Databricks-scoped)

## Common Mistakes
- Confusing Purview (broad catalog) with Unity Catalog (Databricks governance).
- Thinking Purview enforces access (it's mainly discovery/governance/cataloging).

## Senior-Level
Seniors position Purview for enterprise cataloging, lineage, and PII classification across sources, integrate lineage from ADF/Synapse, and pair it with Unity Catalog for lakehouse access control — supporting GDPR/compliance and data discovery.

## Related Topics
Azure Databricks (Unity Catalog), Azure Data Factory, ADLS Gen2, Data Warehousing
