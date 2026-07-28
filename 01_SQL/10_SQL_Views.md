# SQL Views

## What is a view?

A view is a **saved query** that behaves like a table. It doesn't store any data of its own — every time you query a view, the database re-runs the underlying query behind the scenes and hands you the result as if it were a real table.

Analogy: think of a view as a labeled, saved search folder in an email inbox. The folder doesn't physically hold a separate copy of your emails — it just always shows "every unread email from my manager," recalculated fresh every time you open it. The view is the saved definition of that search, not a copy of the underlying emails.

---

## Creating a View

```sql
CREATE VIEW ITEmployees AS
SELECT EmployeeID, Name, Salary
FROM Employee
WHERE Department = 'IT';
```

Now, instead of retyping that filter every time:

```sql
SELECT * FROM ITEmployees;
```

This runs the saved query and returns only IT employees — exactly as if `ITEmployees` were a real, physical table.

---

## Why use a view?

- **Simplicity** — hide a complicated query (with several [joins](07_SQL_Keys_and_Joins.md) and calculations) behind a simple, reusable name
- **Security** — give someone access to a view that only shows certain columns or rows (e.g. hide the Salary column), without giving them access to the full underlying table
- **Consistency** — if ten different reports all need "active customers," a single view definition ensures they all use exactly the same definition of "active," instead of ten slightly different copies of similar logic

---

## A View Combining Multiple Tables

```sql
CREATE VIEW OrderSummary AS
SELECT
    Customer.Name,
    Orders.OrderID,
    Orders.Amount
FROM Orders
JOIN Customer ON Orders.CustomerID = Customer.CustomerID;
```

Anyone querying `OrderSummary` gets clean, joined results without needing to know or write the underlying join logic themselves.

---

## Views Are Not Copies

Because a view re-runs its underlying query every time, it always reflects the *current* data in the real tables — there's no risk of a view showing stale, out-of-date information. The trade-off is that a view built on a slow, complex query is exactly as slow every time it's queried, since that work isn't saved between uses.

(For very large or frequently repeated queries where this recalculation cost matters, some databases support a "materialized" or "indexed" view, which *does* store a physical copy of the result and refreshes it periodically — a more advanced variation on the same idea.)

---

## Azure Usage

Views are commonly used in Azure SQL Database and Azure Synapse Analytics to give business analysts and Power BI reports a simplified, stable "front door" into a complex warehouse schema — hiding the underlying [star schema's](13_SQL_Warehouse.md) many joined tables behind a single, business-friendly view name like `SalesSummary`.

---

## Real World Example

A hospital's IT team creates a view called `ActivePatients` that joins the Patients table with the Admissions table and filters out discharged patients. Doctors and nurses querying `ActivePatients` never need to know or write that underlying join and filter logic themselves — and if the hospital's definition of "active" ever changes, updating the one view definition fixes every report built on top of it at once.

---
---

# Part 2 — Advanced

## How views execute: inlining

A view is not pre-run and cached — the optimizer **inlines** its definition into your query and optimizes the whole thing together:

```sql
SELECT * FROM ITEmployees WHERE Salary > 60000;
-- optimizer actually plans:
SELECT EmployeeID, Name, Salary FROM Employee
WHERE Department = 'IT' AND Salary > 60000;   -- your filter merged in!
```

Consequences worth internalizing: filtering a view *can* use the base table's indexes (predicates push through), views add **zero performance overhead by themselves** — but **views stacked on views** compound into query text the optimizer struggles with. A five-layer view lasagna where each layer joins "just one more table" is the most common cause of mysteriously slow reports in mature warehouses. Flatten or materialize when nesting exceeds ~2 levels.

## Materialized / indexed views — trading freshness for speed

When the underlying query is expensive and asked constantly, store the result:

| Engine | Feature | Refresh model |
|---|---|---|
| SQL Server | **Indexed view** | Maintained *synchronously* with every base-table write (adds write cost!) |
| PostgreSQL | `MATERIALIZED VIEW` | Manual/scheduled `REFRESH` |
| Snowflake/BigQuery | Materialized views | Auto-refresh, engine picks them transparently |
| Databricks | **Materialized views** (DLT-backed) | Managed incremental refresh |

The design question is always: *how stale is acceptable?* Dashboards tolerating 15-minute lag → materialize; regulatory "as-of-now" queries → don't. A materialized view is conceptually just a **precomputed aggregate table with a maintenance contract** — see also [OLAP summary tables](../00_Fundamentals/02_OLAP_Storage.md).

## Updatable views & guard rails

A simple single-table view is writable — `UPDATE ITEmployees SET ...` modifies `Employee`. Two sharp edges:

- You can update a row *out of* the view (set Department='HR' — it vanishes from ITEmployees but the write succeeded). `WITH CHECK OPTION` forbids writes that would escape the view's WHERE — the correct setting for security-scoped views.
- Multi-table/aggregated views are not (sensibly) updatable — treat views as read interfaces and route writes through the base tables or procedures.

## Views as security surfaces

The classic pattern: revoke SELECT on the base table entirely, grant it on views that expose only permitted columns/rows ([DCL](12_SQL_DCL_TCL.md)):

```sql
CREATE VIEW hr.EmployeeDirectory AS
SELECT EmployeeID, Name, Department          -- no Salary column
FROM dbo.Employee WHERE is_deleted = 0;
GRANT SELECT ON hr.EmployeeDirectory TO analyst_role;
```

Modern engines add **row-level security** (policy functions filtering per user) and **dynamic data masking** — but the humble column-hiding view remains the most portable access-control tool in SQL.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Views as the API of the warehouse

The strongest architectural use of views: a **semantic/contract layer** between physical tables and consumers. Physical star schema tables stay engineering territory; analysts and BI touch only `mart.*` views. Benefits pros exploit:

- **Refactoring freedom** — repartition, split, or rename base tables; the view keeps the old contract alive (expand–contract pattern, [04_SQL_DDL.md](04_SQL_DDL.md)).
- **One definition of truth** — "active customer," "net revenue" defined once; ten dashboards can't drift apart.
- **Soft-delete hygiene** — `WHERE is_deleted = 0` lives in the view, never forgotten in a report ([soft deletes](05_SQL_DML.md)).

In Databricks this pattern is first-class: gold-layer **views in Unity Catalog** over silver Delta tables, with grants at the view level.

## SELECT * inside a view — the schema-drift bomb

`CREATE VIEW v AS SELECT * FROM t` captures the column list *at creation time* in some engines (SQL Server): add a column to `t` and the view doesn't show it; drop one and the view breaks at query time with a binding error. Rules seniors enforce in review:

- **Explicit column lists in every view definition.**
- `WITH SCHEMABINDING` (SQL Server) where you want the engine to *prevent* base-table changes that would break the view — required for indexed views anyway.
- After base-table DDL, refresh dependent view metadata (`sp_refreshview`) or, better, recreate views from source control — views belong in [migrations](04_SQL_DDL.md) like every other schema object.

## Views vs CTEs vs tables — the placement decision

| Logic used by | Belongs in |
|---|---|
| One query | [CTE](09_SQL_Subqueries.md) |
| Several queries, always fresh, cheap enough | View |
| Several queries, expensive, staleness OK | Materialized view / scheduled summary table |
| Cross-team contract with SLAs | Physical table built by pipeline (dbt model, Delta table) |

The dbt world blurs this deliberately: every model is *written* as a SELECT, and a config flag decides view vs table vs incremental — the decision above, made declarative.

## Field-tested gotchas

- A view referencing a dropped/renamed column fails at **query time**, not deploy time — dependency-check before dropping anything (`sys.dm_sql_referencing_entities`, Unity Catalog lineage).
- `ORDER BY` inside a view is ignored (or requires TOP hacks) — ordering belongs to the consuming query.
- Nested views can hide **repeated scans** of the same base table; flattening often halves the I/O.
- Granting on a view while the underlying schema changes owners can break **ownership chaining** (suddenly everyone needs base-table rights) — keep view + tables in the same schema/owner or use explicit grants.

## Interview-grade Q&A

- *Do views make queries faster?* No — they're inlined text. Materialized/indexed views do, at a freshness or write cost.
- *How do you expose data to analysts without giving table access?* Column-limited, row-filtered views (+ CHECK OPTION), grants on views only.
- *View vs materialized view?* Live query each time vs stored result needing refresh — choose by staleness tolerance and query cost.
- *Why did the view break after an ALTER TABLE?* Stale binding (SELECT * capture or dropped column) — explicit columns, schemabinding, and views-in-source-control prevent it.

---

## Further Learning — Docs & Videos

**Documentation**
- SQL views (W3Schools): https://www.w3schools.com/sql/sql_view.asp
- CREATE VIEW / materialized views (PostgreSQL): https://www.postgresql.org/docs/current/sql-createview.html

**Videos**
- SQL views explained: https://www.youtube.com/results?search_query=sql+views+explained+materialized+view
