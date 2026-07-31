# 02 — Relational Data on Azure

*Domain: Relational data on Azure (20–25%)*

---

## What it is

This domain covers **relational databases** — data in tables with fixed schemas, related by keys, queried with SQL — and the **Azure services** that host them. You need the core relational concepts (covered deeply in this repo's [SQL](../../02_Databases/SQL/01_What_is_SQL.md) module) plus which Azure service fits which scenario.

---

## Relational concepts (exam essentials)

- **Table** = rows × columns; each column has a **data type** ([SQL Data Types](../../02_Databases/SQL/03_SQL_Data_Types.md)).
- **Primary key** = unique row identifier; **foreign key** = reference to another table's PK ([Keys & Joins](../../02_Databases/SQL/07_SQL_Keys_and_Joins.md)).
- **Index** = structure that speeds lookups ([Indexes](../../02_Databases/SQL/11_SQL_Indexes.md)).
- **View** = a saved query used like a virtual table ([Views](../../02_Databases/SQL/10_SQL_Views.md)).
- **Normalization** = reduce redundancy by splitting data into related tables ([Normalization](../../02_Databases/Data_Modeling/02_Normalization_and_Denormalization.md)).

## SQL statement categories

| Category | Purpose | Examples |
|---|---|---|
| **DDL** | Define structure | `CREATE`, `ALTER`, `DROP` ([DDL](../../02_Databases/SQL/04_SQL_DDL.md)) |
| **DML** | Modify data | `INSERT`, `UPDATE`, `DELETE` ([DML](../../02_Databases/SQL/05_SQL_DML.md)) |
| **DQL** | Query data | `SELECT` ([DQL](../../02_Databases/SQL/06_SQL_DQL.md)) |
| **DCL** | Control access | `GRANT`, `REVOKE` ([DCL/TCL](../../02_Databases/SQL/12_SQL_DCL_TCL.md)) |

> **Exam Tip:** Know which verb belongs to which category — `SELECT` = DQL, `INSERT/UPDATE/DELETE` = DML, `CREATE/ALTER/DROP` = DDL, `GRANT/REVOKE` = DCL.

---

## Azure relational services

The core decision is **IaaS vs PaaS** ([IaaS/PaaS/SaaS](../../03_Cloud/Cloud_Concepts/02_SaaS_PaaS_IaaS.md)) — how much you manage vs Azure manages.

| Service | Model | What it is |
|---|---|---|
| **SQL Server on Azure VM** | **IaaS** | Full SQL Server you install/manage on a VM — most control, most work; for lift-and-shift needing OS access |
| **Azure SQL Managed Instance** | **PaaS** | Near-100% SQL Server compatibility, managed; best for migrating on-prem SQL Server with minimal changes |
| **Azure SQL Database** | **PaaS** | Fully managed single database / elastic pool; cloud-first, least admin; the default modern choice |
| **Azure Database for PostgreSQL / MySQL / MariaDB** | **PaaS** | Managed open-source database engines |

> **Exam Tip:** The IaaS→PaaS ladder for SQL Server: **SQL Server on VM** (you manage OS + SQL) → **SQL Managed Instance** (managed, high compatibility, for migrations) → **Azure SQL Database** (fully managed, cloud-native). More PaaS = less admin, less OS control.

> **Exam Tip:** Choosing between them — need OS-level access / a specific SQL feature / lift-and-shift with the VM → **SQL Server on VM**. Migrating on-prem SQL Server with instance-level features (SQL Agent, cross-DB queries) → **Managed Instance**. New cloud app, minimal management → **Azure SQL Database**. Using MySQL/PostgreSQL → the matching **Azure Database for …**.

---

## Deployment & management concepts

- **Provisioned vs serverless (Azure SQL Database)** — provisioned = fixed compute you pay for continuously; serverless = auto-scales and can auto-pause when idle (pay per use).
- **Elastic pool** — a shared pool of resources across many databases with variable usage.
- **DTU vs vCore** — two purchasing models (bundled DTU vs granular vCore).
- **Management tools** — Azure portal, **Azure Data Studio**, **SQL Server Management Studio (SSMS)**, Azure CLI/PowerShell.

> **Exam Tip:** If a scenario has unpredictable, intermittent usage and wants to save cost when idle, the answer is **serverless** (Azure SQL Database) or an **elastic pool** for many variable databases.

---

## Quick Review

- Relational = tables with fixed schemas related by **primary/foreign keys**, queried with **SQL**.
- SQL categories: **DDL** (structure), **DML** (change data), **DQL** (`SELECT`), **DCL** (permissions).
- IaaS→PaaS: **SQL Server on VM** → **SQL Managed Instance** → **Azure SQL Database** (least management).
- **Managed Instance** = high-compatibility migrations; **Azure SQL Database** = cloud-native, least admin.
- **Azure Database for PostgreSQL/MySQL/MariaDB** = managed open-source engines.
- **Serverless / elastic pool** = cost-efficient for intermittent or many-variable workloads.

---

## Further Learning — Docs & Videos

- Explore relational data on Azure (Learn): https://learn.microsoft.com/en-us/training/paths/azure-data-fundamentals-explore-relational-data/
- Azure SQL deployment options: https://learn.microsoft.com/en-us/azure/azure-sql/azure-sql-iaas-vs-paas-what-is-overview
- Video search: https://www.youtube.com/results?search_query=dp-900+relational+data+azure+sql

---

Next: **[03 — Non-Relational Data on Azure](03_Non_Relational_Data_on_Azure.md)**.
