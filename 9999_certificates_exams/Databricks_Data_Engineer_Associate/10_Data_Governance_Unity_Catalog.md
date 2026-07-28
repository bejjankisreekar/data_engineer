# 10 — Data Governance: Unity Catalog

*Domain: Data Governance (9%) — smallest domain, easiest to max out.*

---

## What it is

**Unity Catalog (UC)** is Databricks' **centralized governance layer** for data and AI. It provides a **single place** to manage access control, auditing, lineage, and data discovery across **all** workspaces in an account. One permission model, one namespace, applied consistently to tables, views, files (volumes), ML models, and functions.

**Analogy:** Without UC, each workspace is a separate building with its own locks and guest lists. Unity Catalog is a single security office for the whole campus — one badge system, one visitor log, one directory.

> **Exam Tip:** Unity Catalog centralizes governance **across workspaces** at the **account level** (not per-workspace). It gives you unified access control, auditing, data lineage, and search/discovery over data and AI assets.

---

## The three-level namespace

Unity Catalog uses a **three-level** naming hierarchy to reference data: **`catalog.schema.table`**.

```
catalog.schema.table
   │       │      └── table / view / volume / function / model
   │       └── schema (a.k.a. database) — a grouping of tables
   └── catalog — the top-level container (e.g., per environment or team)
```

```sql
SELECT * FROM main.sales.transactions;   -- catalog=main, schema=sales, table=transactions
USE CATALOG main;
USE SCHEMA sales;
```

> **Exam Tip:** UC introduces a **three-level namespace `catalog.schema.table`** — one more level than the legacy Hive metastore's two-level `schema.table` (a.k.a. `database.table`). The **catalog** is the new top layer. Knowing "three-part name = Unity Catalog" is a frequent question.

---

## The object hierarchy

From top to bottom:

```
Metastore  (one per region, attached to the account)
  └── Catalog        (top-level container of schemas)
        └── Schema / Database   (container of tables, views, volumes, functions)
              ├── Table          (managed or external)
              ├── View
              ├── Volume         (governed non-tabular files)
              ├── Function       (UDF)
              └── Model          (registered ML model)
```

- **Metastore** — the top-level container of metadata for a region; one metastore is attached to workspaces in that region. (Distinct from the legacy per-workspace Hive metastore.)
- **Catalog** — first part of the namespace; groups schemas (often one catalog per environment: `dev`, `prod`).
- **Schema (database)** — groups tables/views/volumes/functions.
- **Volume** — governs access to **non-tabular data** (files, images, unstructured) — the UC-native replacement for DBFS mounts.

> **Exam Tip:** Know the order: **Metastore → Catalog → Schema → Table/View/Volume/Function**. **Volumes** govern **files/unstructured data**; tables/views govern tabular data. The **metastore** sits above catalogs (one per region).

---

## Managing access — GRANT / REVOKE

Unity Catalog uses SQL-standard **`GRANT`/`REVOKE`** privileges on securable objects:

```sql
GRANT SELECT ON TABLE main.sales.transactions TO `analysts`;
GRANT USAGE ON SCHEMA main.sales TO `analysts`;
GRANT USE CATALOG ON CATALOG main TO `analysts`;
REVOKE SELECT ON TABLE main.sales.transactions FROM `analysts`;
SHOW GRANTS ON TABLE main.sales.transactions;
```

Common privileges: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`, `CREATE TABLE`, `CREATE SCHEMA`, `ALL PRIVILEGES`.

> **Exam Tip:** To let a user query a table, they generally need a **chain of privileges**: `USE CATALOG` on the catalog **and** `USE SCHEMA` on the schema **and** `SELECT` on the table. Granting `SELECT` alone isn't enough if they can't "use" the parent catalog/schema. Privileges also **inherit downward** — a grant on a catalog/schema applies to objects within it.

### Principals: users, groups, service principals

- Grant to **users**, **groups** (recommended — manage access by group), or **service principals** (for automation/jobs).
- **Best practice:** assign privileges to **groups**, not individual users, for manageability.

---

## Ownership

- Every UC object has an **owner** (a user or group). The owner can grant/revoke privileges on it and drop it.
- Ownership can be transferred with `ALTER ... OWNER TO`.

> **Exam Tip:** The **owner** of an object controls its permissions. Best practice is to make a **group** the owner so access management doesn't depend on one person.

---

## Lineage, auditing, discovery

- **Data lineage** — UC automatically captures **column- and table-level lineage** (which tables/columns feed which), shown in Catalog Explorer. Helps impact analysis and compliance.
- **Audit logs** — UC records who accessed what and when.
- **Search & discovery** — Catalog Explorer lets users browse, search, tag, and document data assets.

> **Exam Tip:** Unity Catalog provides **automated data lineage** (table and column level) with **no extra code** — captured for queries run on UC-enabled compute. It also provides centralized **auditing** and **data discovery/search**.

---

## Managed vs external tables under UC

- **Managed tables** — UC manages both metadata and the underlying storage (in the metastore's managed storage location); dropping deletes the data.
- **External tables** — data lives at an **external location** you define; dropping removes only metadata. UC governs access via **Storage Credentials** and **External Locations**.
  - **Storage Credential** — an object representing a cloud credential (e.g., an IAM role/managed identity) UC uses to access storage.
  - **External Location** — a path + a storage credential, governing access to a specific cloud storage location.

> **Exam Tip:** Under UC, access to external cloud storage is governed through **Storage Credentials** (the auth) + **External Locations** (the path). This replaces ad-hoc DBFS mounts and instance profiles for governed access.

---

## Dynamic views for fine-grained security

You can restrict rows/columns using **dynamic views** with functions like `current_user()`, `is_account_group_member()`:

```sql
CREATE VIEW sales_secure AS
SELECT
  id,
  CASE WHEN is_account_group_member('managers') THEN salary ELSE 'REDACTED' END AS salary
FROM main.hr.employees
WHERE is_account_group_member('managers') OR region = current_user();
```

> **Exam Tip:** **Dynamic views** implement **column masking and row-level security** using `current_user()` / `is_account_group_member()` — show or hide data based on who's querying.

---

## Quick Review

- **Unity Catalog** = centralized, **account-level** governance across all workspaces: access control, lineage, audit, discovery.
- **Three-level namespace `catalog.schema.table`** (vs legacy two-level Hive `schema.table`) — three parts = UC.
- Hierarchy: **Metastore → Catalog → Schema → Table/View/Volume/Function**. **Volumes** govern **files/unstructured** data.
- Access via **`GRANT`/`REVOKE`**; querying a table needs **USE CATALOG + USE SCHEMA + SELECT**; privileges **inherit downward**.
- Grant to **groups** (best practice), users, or service principals. Every object has an **owner**.
- **Automated table + column lineage**, auditing, and search — no extra code.
- External storage governed via **Storage Credentials + External Locations**; **dynamic views** do row/column-level security.

---

## Further Learning — Docs & Videos

**Official documentation**
- Unity Catalog overview: https://docs.databricks.com/en/data-governance/unity-catalog/index.html
- UC object model: https://docs.databricks.com/en/data-governance/unity-catalog/index.html#object-model
- Manage privileges (GRANT): https://docs.databricks.com/en/data-governance/unity-catalog/manage-privileges/index.html
- Data lineage: https://docs.databricks.com/en/data-governance/unity-catalog/data-lineage.html
- Volumes: https://docs.databricks.com/en/connect/unity-catalog/volumes.html
- Dynamic views (row/column security): https://docs.databricks.com/en/data-governance/unity-catalog/create-views.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Unity Catalog explained: https://www.youtube.com/results?search_query=databricks+unity+catalog+tutorial
- Three-level namespace & GRANT: https://www.youtube.com/results?search_query=databricks+unity+catalog+catalog+schema+table+grant
- Lineage & governance: https://www.youtube.com/results?search_query=databricks+unity+catalog+data+lineage

---

Next: **[11 — Practice Questions by Domain](11_Practice_Questions_by_Domain.md)**.
