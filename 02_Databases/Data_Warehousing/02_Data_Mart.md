# Data Mart

## What is a Data Mart?

A **Data Mart** is a smaller, focused subset of a data warehouse, built around the needs of a single department, business function, or subject area — Sales, Finance, HR — rather than the whole enterprise.

Analogy: if the [data warehouse](01_Data_Warehouse_Fundamentals.md) is an entire supermarket carrying everything the whole company might ever need, a data mart is one aisle — the frozen foods aisle, stocked and organized specifically for shoppers who only care about frozen foods, pulled from the same overall supply chain as everything else in the store.

---

## Why not just query the warehouse directly?

- **Performance** — a mart holds a fraction of the warehouse's data, so departmental queries run faster without competing for resources with every other team's workload.
- **Simplicity** — a mart exposes only the tables, columns, and business logic relevant to one department, instead of the full enterprise schema an analyst would otherwise have to navigate.
- **Access control** — a mart is a natural security boundary: Finance's mart can hold salary and revenue data that HR's mart never exposes, without managing row/column-level permissions across one giant shared warehouse table.
- **Ownership** — a department can govern "their" mart's definitions (e.g. what counts as a "qualified lead") without needing sign-off from every other team using the central warehouse.

---

## Data Mart vs Data Warehouse

| | Data Warehouse | Data Mart |
|---|---|---|
| Scope | Entire organization | One department / subject area |
| Data volume | Very large | A focused subset |
| Users | Cross-functional analysts, enterprise BI | One department's analysts |
| Design | Often more normalized/integrated at the core | Almost always a denormalized [star schema](../SQL/13_SQL_Warehouse.md) |
| Built by | Central data/platform team | Central team (for dependent marts) or the department itself (independent marts) |

---

## Real World Example

A retail company's central data warehouse holds every fact about every store, product, employee, and financial transaction. The **Finance data mart** exposes only revenue, cost, and margin facts joined to Date/Store/Product dimensions — finance analysts never see HR salary data or inventory shrinkage details that live in the same warehouse but belong to other marts.

---

## Azure Usage

Data marts are typically implemented as a dedicated schema or database within Azure Synapse Analytics/Microsoft Fabric, or as a curated set of gold-layer Delta tables and views scoped to one domain in Databricks/Fabric — either way, the same underlying pattern: a governed, department-scoped slice of the larger warehouse/lakehouse.

---
---

# Part 2 — Advanced

## Three ways to build a data mart

| Type | Sourced from | Trade-off |
|---|---|---|
| **Dependent** | The central data warehouse | Consistent (inherits the warehouse's integration work), but requires the warehouse to exist first — the Inmon approach |
| **Independent** | Source systems directly, bypassing any central warehouse | Fast to build, but every mart reinvents its own integration logic and definitions — high risk of inconsistency |
| **Hybrid** | A mix — some facts from the warehouse, some extracted directly for speed | Balances speed and consistency, but needs deliberate governance to avoid drifting toward independent-mart problems |

**Dependent marts** are how Kimball's dimensional bus and Inmon's CIF both actually deliver data to end users — the mart is just a subject-area-scoped extract (or, in a lakehouse, a set of views) drawn from an already-integrated layer, sharing the same conformed dimensions as every other mart.

**Independent marts** skip the central integration step entirely — a department pulls straight from source systems and builds its own star schema. This is fast to stand up but is exactly how organizations end up with two departments each claiming a different "total revenue" number, because each mart quietly made its own decisions about currency conversion, return handling, or which orders count as "completed."

## Star schema per mart

Each mart is typically its own [star schema](../SQL/13_SQL_Warehouse.md) — a fact table (e.g. `Fact_Sales`) surrounded by the dimensions relevant to that subject area. The dimensional-bus discipline matters here specifically: if the Sales mart's `Dim_Date` and the Finance mart's `Dim_Date` are two separately built tables rather than the same **conformed dimension**, a report trying to compare sales trends against financial close dates will silently misalign.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Data mart sprawl — the "spreadmart" problem

**Spreadmarts** is the industry's half-joking name for the endpoint of unchecked independent-mart proliferation: dozens of departmental marts (or, worse, personal spreadsheets treated as marts), each with its own silently-different definition of common metrics like "active customer" or "net revenue." The organizational symptom is unmistakable: two executives arrive at the same meeting with two different numbers for the same metric, and nobody can say which is right without a lengthy reconciliation exercise.

The fix isn't banning data marts — dependent marts built on conformed dimensions from a governed integration layer are exactly what makes fast, department-specific analytics possible without central-team bottlenecks. The fix is banning *independent* marts as the default, and treating shared metric definitions as a governed artifact (a [semantic layer](../SQL/13_SQL_Warehouse.md)) rather than something each mart reinvents.

## Data marts in a lakehouse world

In a modern medallion architecture, "data mart" often isn't a separate physical database at all — it's a **domain-scoped set of gold-layer views** over the same underlying Delta/Iceberg tables everyone else reads, with grants (e.g. Unity Catalog permissions) restricting each domain's view to its own team. This gives every practical benefit of a classic dependent mart (focus, performance via [OLAP physical design](../../01_Foundations/Fundamentals/02_OLAP_Storage.md), access control) without physically copying data anywhere — the mart is a *lens*, not a duplicate.

## Field-tested gotchas

- An "independent mart built for speed during a deadline" almost never gets migrated to dependent status later — it becomes permanent technical and organizational debt the moment it ships a number an executive relies on.
- Marts that skip conformed dimensions can *look* identical in schema (both have a `region` column) while encoding genuinely different business rules underneath (different region-to-store mappings) — schema similarity is not proof of comparability.
- Granting broad warehouse access "because building a mart takes too long" defeats the access-control benefit marts exist to provide — the mart boundary is a governance decision, not just a performance optimization.
- A mart with no owner accountable for its metric definitions drifts the fastest — assign explicit ownership, the same discipline [data mesh](03_Data_Mesh.md) formalizes at a larger scale.

## Interview-grade Q&A

- *What is a data mart, and why not just let everyone query the warehouse?* A department-scoped subset of the warehouse, built for performance, simplicity, and access control that a single shared enterprise schema doesn't provide.
- *Dependent vs independent data marts?* Dependent marts are sourced from an already-integrated central warehouse (consistent, slower to start); independent marts pull directly from source systems (fast, but prone to metric drift).
- *What is a "spreadmart," and how do you prevent it?* Departmental data stores that have each independently — and differently — defined the same business metrics; prevented by conformed dimensions and a governed shared semantic layer, not by banning marts outright.
- *How does a data mart look different in a lakehouse vs a classic warehouse?* Often just a set of permissioned gold-layer views over shared Delta tables, rather than a physically separate copied database.

Next: the organizational answer to mart sprawl at enterprise scale → [Data Mesh](03_Data_Mesh.md)

---

## Further Learning — Docs & Videos

**Documentation**
- What is a data mart? (AWS): https://aws.amazon.com/what-is/data-mart/
- Data mart vs data warehouse (IBM): https://www.ibm.com/think/topics/data-mart

**Videos**
- Data mart vs data warehouse explained: https://www.youtube.com/results?search_query=data+mart+vs+data+warehouse+explained
