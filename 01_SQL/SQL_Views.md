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

- **Simplicity** — hide a complicated query (with several [joins](SQL_Keys_and_Joins.md) and calculations) behind a simple, reusable name
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

Views are commonly used in Azure SQL Database and Azure Synapse Analytics to give business analysts and Power BI reports a simplified, stable "front door" into a complex warehouse schema — hiding the underlying [star schema's](SQL_Warehouse.md) many joined tables behind a single, business-friendly view name like `SalesSummary`.

---

## Real World Example

A hospital's IT team creates a view called `ActivePatients` that joins the Patients table with the Admissions table and filters out discharged patients. Doctors and nurses querying `ActivePatients` never need to know or write that underlying join and filter logic themselves — and if the hospital's definition of "active" ever changes, updating the one view definition fixes every report built on top of it at once.
