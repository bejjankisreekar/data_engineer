# Unity Catalog

## What is it?

**Unity Catalog (UC)** is Databricks' centralized **governance layer** — one place to manage *who can access what data, across all workspaces*, plus lineage, discovery, and auditing. Before UC, each workspace had its own Hive metastore and permissions were scattered and inconsistent; UC gives an entire organization **one catalog, one permission model, one source of truth** for data governance.

In one line: **Unity Catalog = a single, org-wide access-control + metadata + lineage layer over all your Databricks data.**

---

## Analogy: a library's central catalog and membership desk

Imagine a university with many library buildings. Before UC, each building had its *own* card catalog and its *own* rules about who could borrow what — a book restricted in one building was freely lent in another, and no one could say who had read it. **Unity Catalog is a single central catalog + membership system** for *all* buildings: one search to find any book (discovery), one membership card that works everywhere (identity), one rulebook for who may read each shelf (access control), and a log of every checkout (audit + lineage).

---

## The three-level namespace

This is the defining UC concept and a guaranteed interview question. Every table/view has a **three-part name**:

```
catalog . schema . table
   │         │        │
   │         │        └── the table or view
   │         └── a grouping of tables (a "database")
   └── top-level container, often per environment or domain

e.g.   prod.sales.orders      dev.sales.orders      finance.gl.transactions
```

- **Metastore** — the top of the hierarchy, one per region, attached to workspaces.
- **Catalog** — first level; commonly split by environment (`dev`/`prod`) or business domain.
- **Schema** (database) — groups related tables.
- **Table / View / Volume / Function** — the objects themselves.

Legacy Hive was two-level (`schema.table`); UC adds the **catalog** level, which is what enables clean dev/prod and domain separation.

---

## What UC governs

| Object | Governed by UC |
|---|---|
| **Tables & views** | Managed and external Delta tables |
| **Volumes** | Non-tabular files (models, images, exports) |
| **Functions** | Registered UDFs |
| **Models** | MLflow models |
| **External locations & storage credentials** | Governed access to ADLS paths (replaces mounts) |

Permissions use familiar SQL: `GRANT SELECT ON TABLE prod.sales.orders TO group_analysts;`

---

## Advantages

- **One permission model** — govern all workspaces from one place, with SQL `GRANT`/`REVOKE` ([DCL recap](../02_Databases/SQL/12_SQL_DCL_TCL.md)).
- **Fine-grained access** — down to table, column (masking), and row (filters).
- **Automatic lineage** — table- and column-level lineage captured as jobs run.
- **Discovery & search** — a searchable catalog of all data assets.
- **Audit** — every access logged for compliance.
- **Identity federation** — users/groups from **Microsoft Entra ID** synced in, not managed per-workspace.
- **Open sharing** — **Delta Sharing** to share data across orgs without copying.

## Disadvantages

- **Migration effort** — moving off the legacy Hive metastore and mounts takes planning.
- **Setup complexity** — metastore, storage credentials, external locations, and identity sync are a learning curve.
- **Access-mode constraints** — some older cluster/library patterns need shared/single-user access modes to work with UC.

---

## Azure Usage

- **Identity** — UC users and groups come from **Microsoft Entra ID** (SCIM sync), so access aligns with corporate identity.
- **Storage** — UC governs data in **ADLS Gen2** via *storage credentials* (a managed identity) + *external locations* (a governed path). This **replaces DBFS mounts**, which are being deprecated.
- **Purview** — UC lineage/metadata integrates with **Microsoft Purview** for enterprise-wide cataloging beyond Databricks ([governance](../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)).

---

## Real World Example

A bank runs a dev and a prod Databricks workspace and must prove to auditors exactly who can see customer PII. With Unity Catalog: PII columns in `prod.customers.accounts` are **masked** for the analyst group and visible only to a compliance group; **row filters** restrict each regional team to its own region's rows; **column-level lineage** shows auditors that the `risk_score` in a Gold table derives from specific Silver columns; and every query is **logged**. When a new analyst joins, adding them to the right **Entra ID group** grants exactly the right access across both workspaces — no per-workspace fiddling, one governed model.

---

## Managed vs external tables under UC

UC sharpens the [managed vs external](../05_Storage_and_Formats/Lakehouse/02_Delta_Table.md) distinction:
- **Managed tables** live in UC-managed storage; UC owns the full lifecycle (and `DROP` deletes the data).
- **External tables** point at an **external location** (a governed ADLS path via a storage credential); `DROP` removes only metadata.

External locations + storage credentials are how UC governs *raw file paths* without insecure mounts — the storage credential (a managed identity) holds the access, and grants on the external location control who can use it.

## Fine-grained access: masking & row filters

- **Column masking** — a function that redacts a column for unauthorized users (`***-**-1234` for SSN).
- **Row filters** — a function that limits which rows a principal sees (region-based, tenant-based).

Both are defined once and enforced everywhere the table is queried — governance that travels with the data, not bolted onto each report.

## Lineage — automatic and column-level

As jobs run, UC records which tables/columns feed which — table *and* column level. This answers "if I change this Bronze column, what breaks downstream?" and "where did this Gold number come from?" without manual documentation. It's a core reason to adopt UC beyond access control.

## Delta Sharing

An open protocol to share live Delta tables with other orgs/tools **without copying** — the recipient reads your data directly (even from non-Databricks engines). It turns data sharing from "export a copy and hope it's current" into "grant read on a live table."

---

## UC is what makes "one copy, many engines" governable

The [lakehouse promise](../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) is one copy of data read by many engines — but without a single governance layer that's a security nightmare. Unity Catalog is the piece that makes it *safe*: one permission model spanning engineering (Spark), BI (SQL warehouses), and ML, tied to corporate identity. When evaluating a lakehouse, the pro asks "whose catalog governs it?" — UC is Databricks' answer, and it's the difference between a governed platform and a swamp.

## Catalog design is an org-design decision

How you carve up catalogs/schemas encodes your operating model: **environment-based** (`dev`/`test`/`prod` catalogs) suits central platform teams; **domain-based** (`sales`, `finance`, `marketing` catalogs) suits a [data mesh](../02_Databases/Data_Warehousing/03_Data_Mesh.md) with domain ownership. Many orgs combine both (`prod_sales`, `dev_sales`). Getting this taxonomy right early avoids painful renames later — it's a governance-architecture choice, not an afterthought.

## Migration off Hive metastore

Real orgs adopt UC incrementally: stand up the metastore, create catalogs, migrate external locations off mounts, then move tables schema by schema, running old and new in parallel until access and lineage are trusted. Big-bang migrations of a live analytics estate fail; the consulting playbook is workload-by-workload with reconciliation.

## Field-tested gotchas

- **Still using DBFS mounts** — deprecated and ungoverned; migrate to external locations + storage credentials.
- **Over-granting** — `GRANT ... TO account users` defeats the point; grant to Entra ID groups by role.
- **Two-level thinking** — forgetting the catalog level and colliding `dev`/`prod` tables; use the full three-part name.
- **Ignoring lineage** — UC captures it for free; teams that don't use it keep documenting dependencies by hand.
- **Access-mode surprises** — a legacy cluster in "no isolation" mode can't use UC features; use shared/single-user access modes.

## Interview-grade Q&A

- *What is Unity Catalog?* Databricks' centralized governance layer — one org-wide model for access control, metadata, lineage, discovery, and audit across all workspaces.
- *Explain the three-level namespace.* `catalog.schema.table` — UC adds the catalog level above the legacy Hive `schema.table`, enabling clean dev/prod and domain separation, all under a regional metastore.
- *How does UC do fine-grained security?* SQL `GRANT`/`REVOKE` at table level, plus column masking and row filters defined once and enforced on every query; identity from Entra ID groups.
- *How does UC govern raw file paths?* Storage credentials (a managed identity) + external locations over ADLS, replacing insecure DBFS mounts.
- *Why does UC matter for the lakehouse?* It provides the single governance model that lets one copy of data be safely read by Spark, SQL, and ML — answering "whose catalog governs it?"

---

## Related Notes

- **Prev:** [Notebooks, Repos & Jobs](04_Notebooks_Repos_and_Jobs.md) · **Next:** [Delta Live Tables](08_Delta_Live_Tables.md)
- **Governance:** [Data Governance & Security](../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) · **Access SQL:** [SQL DCL & TCL](../02_Databases/SQL/12_SQL_DCL_TCL.md)
- **Cert:** [Data Governance & Unity Catalog](../Certifications/Databricks_Data_Engineer_Associate/10_Data_Governance_Unity_Catalog.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Unity Catalog: https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/
- Manage privileges in UC: https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/manage-privileges/

**Videos**
- Unity Catalog explained: https://www.youtube.com/results?search_query=databricks+unity+catalog+explained
- Unity Catalog three-level namespace: https://www.youtube.com/results?search_query=unity+catalog+three+level+namespace
