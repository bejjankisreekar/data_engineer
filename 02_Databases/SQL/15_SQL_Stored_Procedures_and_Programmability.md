# SQL Stored Procedures and Programmability

## Why this file exists

So far, SQL has been things you *send* to a database: [DDL](04_SQL_DDL.md) defines structures, [DML](05_SQL_DML.md) changes rows, [DQL](06_SQL_DQL.md) reads them. This file covers the fourth category — logic that **lives inside the database and is saved under a name**.

Analogy: everything so far has been typing commands at a counter. Programmability is handing the clerk a **written procedure** they keep in a drawer — "when I say *run the daily load*, do these eleven steps in this order, and if step 6 fails, undo everything." The steps live with the clerk, not in your head.

---

## The whole family, at a glance

Six programmable objects. People confuse them constantly, and the confusion always comes down to three questions: how is it called, can it change data, and what does it give back?

| Object | Called how | Can modify data? | Returns | Usable inside a `SELECT`? |
|---|---|---|---|---|
| **[View](10_SQL_Views.md)** | Like a table, in `FROM` | No (mostly) | A table | Yes |
| **Stored procedure** | `EXEC` / `CALL`, as its own statement | **Yes** | 0…n result sets, output params, return code | **No** |
| **Scalar UDF** | Inline: `SELECT dbo.fn(x)` | No | One single value | Yes |
| **Inline table-valued function** | In `FROM`, with arguments | No | A table | Yes |
| **Multi-statement TVF** | In `FROM`, with arguments | No | A table | Yes |
| **Trigger** | **Never called** — DML fires it automatically | **Yes** | Nothing | No |

> The one that trips people up: a stored procedure **cannot** be used inside a query. You can't `SELECT * FROM my_proc()`. If you need the result in a query, you wanted a *function* or a *view*. That single constraint drives most of the design choices below.

---

## 1. Stored procedures

A saved, parameterized program. The unit of work data pipelines actually call.

### The basic shape

```sql
CREATE PROCEDURE sales.usp_GetOrdersByCustomer
    @CustomerID INT
AS
BEGIN
    SET NOCOUNT ON;                  -- suppress "(3 rows affected)" chatter

    SELECT OrderID, Amount, Status
    FROM sales.Orders
    WHERE CustomerID = @CustomerID;
END;
```

```sql
EXEC sales.usp_GetOrdersByCustomer @CustomerID = 1;
```

| OrderID | Amount | Status |
|---|---|---|
| 501 | 2000 | Shipped |
| 502 | 1500 | Pending |

`SET NOCOUNT ON` is near-universal in production procedures: the row-count messages are extra network round-trips that some client drivers mistake for result sets.

### Parameters — input, default, and output

```sql
CREATE PROCEDURE sales.usp_LoadDailySales
    @LoadDate    DATE,                     -- required
    @Overwrite   BIT = 1,                  -- optional, defaults to 1
    @RowsLoaded  INT = NULL OUTPUT         -- hands a value BACK to the caller
AS
BEGIN
    SET NOCOUNT ON;

    IF @Overwrite = 1
        DELETE FROM sales.FactSales WHERE SaleDate = @LoadDate;

    INSERT INTO sales.FactSales (SaleDate, CustomerKey, Amount)
    SELECT s.SaleDate, c.CustomerKey, s.Amount
    FROM staging.Sales s
    JOIN dim.Customer c ON c.CustomerID = s.CustomerID
    WHERE s.SaleDate = @LoadDate;

    SET @RowsLoaded = @@ROWCOUNT;          -- rows the last statement touched
    RETURN 0;                              -- 0 = success, by convention
END;
```

```sql
DECLARE @loaded INT, @status INT;
EXEC @status = sales.usp_LoadDailySales
        @LoadDate   = '2026-08-21',
        @RowsLoaded = @loaded OUTPUT;

SELECT @status AS return_code, @loaded AS rows_loaded;
```

| return_code | rows_loaded |
|---|---|
| 0 | 1284 |

Three distinct ways a procedure gives something back, and they are **not** interchangeable:

| Mechanism | Carries | Use for |
|---|---|---|
| Result set (`SELECT`) | Rows and columns | The actual data |
| `OUTPUT` parameter | One scalar per parameter | Counts, IDs, computed flags |
| `RETURN n` | A single integer | Status only — 0 success, non-zero failure. **Never** use it to return data |

### The idempotent load pattern

The single most valuable procedure shape in data engineering — safe to re-run, which is exactly what an orchestrator with a retry policy needs ([idempotency](../../06_Data_Engineering/ETL_ELT/03_Data_Pipelines.md)):

```text
   delete this partition   ->   re-insert this partition   ->   commit
   ------------------------------------------------------------------
   run it once   -> correct
   run it twice  -> correct (identical result, no duplicates)
   run it after a half-failed run -> correct (the delete cleans up)
```

Contrast a naive `INSERT`-only procedure: run it twice and every row is duplicated. The delete-then-insert (or `MERGE`) shape is what makes a retry safe.

**Use stored procedures when:**

- **Set-based load logic belongs next to the data** — the work happens in the database instead of pulling millions of rows across the network into an application.
- **You want to grant an action, not a table.** `GRANT EXECUTE` on the procedure and *no* permission on the underlying tables: the caller can run precisely that operation and nothing else ([DCL](12_SQL_DCL_TCL.md)).
- **A pipeline needs to call one named thing.** [ADF's](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) Stored Procedure activity is the standard way to trigger transformation logic in Azure SQL or a Synapse dedicated pool.

---

## 2. Error handling — `TRY…CATCH` and transactions

A procedure without error handling can leave your table **half-loaded**. This is the difference between a failed run and a corrupted table.

### What goes wrong without it

```text
   BEGIN TRAN
     DELETE old partition      -- succeeds, 1200 rows gone
     INSERT new partition      -- FAILS on row 700 (bad data type)
   ... no CATCH, no ROLLBACK

   Result: the delete happened, the insert didn't.
           The partition is now EMPTY, and the job reported failure.
           Someone's dashboard shows zero revenue for that day.
```

### The pattern that fixes it

```sql
CREATE PROCEDURE sales.usp_LoadDailySales_Safe
    @LoadDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;          -- any runtime error aborts the whole transaction

    BEGIN TRY
        BEGIN TRANSACTION;

            DELETE FROM sales.FactSales WHERE SaleDate = @LoadDate;

            INSERT INTO sales.FactSales (SaleDate, CustomerKey, Amount)
            SELECT s.SaleDate, c.CustomerKey, s.Amount
            FROM staging.Sales s
            JOIN dim.Customer c ON c.CustomerID = s.CustomerID
            WHERE s.SaleDate = @LoadDate;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0            -- a transaction is still open or doomed
            ROLLBACK TRANSACTION;

        INSERT INTO ops.LoadErrors (ProcName, LoadDate, ErrNum, ErrMsg, ErrLine, LoggedAt)
        VALUES (ERROR_PROCEDURE(), @LoadDate, ERROR_NUMBER(),
                ERROR_MESSAGE(), ERROR_LINE(), SYSUTCDATETIME());

        THROW;    -- re-raise so the CALLER (ADF, Airflow) sees a failure too
    END CATCH;
END;
```

Now the same failure leaves the table **exactly as it was** — the delete is rolled back with the insert.

**The pieces:**

| Element | Why it's there |
|---|---|
| `SET XACT_ABORT ON` | Without it, some errors abort only the *statement* and quietly continue the transaction |
| `XACT_STATE()` | Returns `1` (committable), `-1` (doomed, must roll back), `0` (none). Safer than `@@TRANCOUNT` alone |
| Log **before** `THROW` | After re-raising, execution stops — log first or lose the diagnostic |
| Bare `THROW` | Re-raises the original error with its number and line intact. `RAISERROR` (older) loses that fidelity |

> **`THROW` is not optional.** A `CATCH` that swallows the error makes the procedure return success while having done nothing. The orchestrator marks the run green, and nobody finds out until a report is wrong. Log it, then re-raise.
>
> `TRY…CATCH` does **not** catch everything: compile errors, syntax errors, and severity-20+ failures bypass it entirely.

---

## 3. User-defined functions — three kinds, one performance cliff

All three are "functions," and their performance differs by orders of magnitude.

### Scalar UDF — one value in, one value out

```sql
CREATE FUNCTION dbo.fn_FiscalYear (@d DATE)
RETURNS INT
AS
BEGIN
    RETURN CASE WHEN MONTH(@d) >= 4 THEN YEAR(@d) + 1 ELSE YEAR(@d) END;
END;

SELECT OrderID, dbo.fn_FiscalYear(OrderDate) AS fiscal_year FROM sales.Orders;
```

Convenient, and **the classic performance killer**:

```text
   SELECT ... dbo.fn_FiscalYear(OrderDate) ... FROM Orders    -- 10,000,000 rows

   Historically the engine executes the function body
   ONCE PER ROW  ->  10,000,000 separate invocations
   and (pre-2019) the whole query loses parallelism.

   The identical CASE expression written inline: one set-based pass.
```

SQL Server 2019+ can *inline* simple scalar UDFs automatically, which removes much of the pain — but only when the function qualifies, and you generally won't notice when it silently stops qualifying. The safe habit stands: **prefer an inline expression or an inline TVF in any hot query path.**

### Inline table-valued function — a parameterized view

```sql
CREATE FUNCTION sales.tvf_OrdersForCustomer (@CustomerID INT)
RETURNS TABLE
AS
RETURN (
    SELECT OrderID, Amount, Status
    FROM sales.Orders
    WHERE CustomerID = @CustomerID
);

SELECT * FROM sales.tvf_OrdersForCustomer(1);
```

Note: a **single `RETURN (SELECT …)`** with no `BEGIN`/`END`. That's what makes it *inline* — the optimizer expands the body into the calling query and plans them together, exactly like a view. **This is the good one.** If you want a view that takes an argument, this is it.

### Multi-statement TVF — procedural, and quietly slow

```sql
CREATE FUNCTION sales.mstvf_OrderSummary (@CustomerID INT)
RETURNS @result TABLE (OrderID INT, Amount DECIMAL(10,2))   -- declares a table
AS
BEGIN
    INSERT INTO @result SELECT OrderID, Amount
    FROM sales.Orders WHERE CustomerID = @CustomerID;
    RETURN;
END;
```

The body is procedural, so the optimizer **can't see inside it**. It guesses the row count (historically a flat 1 or 100), and a wrong estimate picks the wrong join strategy for everything downstream.

### The ranking to remember

| Rank | Form | Why |
|---|---|---|
| 🥇 | Inline expression / `CASE` | No function overhead at all |
| 🥈 | **Inline TVF** | Optimizer expands and plans it with the query |
| 🥉 | Multi-statement TVF | Opaque to the optimizer, bad estimates |
| ⚠️ | Scalar UDF in a `SELECT`/`WHERE` over many rows | Per-row execution, parallelism loss |

> Same lesson in Spark: built-in functions → `pandas_udf` → plain Python UDF, in that order. A Python UDF leaves the JVM and blinds [Catalyst](../../03_Programming/PySpark/Spark_Processing.md), exactly as a scalar UDF blinds the SQL optimizer.

---

## 4. Triggers — code that runs whether you asked or not

A trigger is a block of code attached to a table that fires **automatically** on `INSERT`, `UPDATE`, or `DELETE`. You never call it. That's its power and its danger.

### `inserted` and `deleted` — the pseudo-tables

Inside a trigger you get two virtual tables holding the affected rows:

```text
   Statement        `inserted` holds        `deleted` holds
   -----------------------------------------------------------
   INSERT           the new rows            (empty)
   DELETE           (empty)                 the removed rows
   UPDATE           the NEW versions        the OLD versions
                    ^ both populated -- join them to see what changed
```

### Example — an audit trail

```sql
CREATE TRIGGER sales.trg_Orders_AuditStatus
ON sales.Orders
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT UPDATE(Status) RETURN;      -- skip if this column wasn't touched

    INSERT INTO sales.Orders_Audit (OrderID, OldStatus, NewStatus, ChangedAt, ChangedBy)
    SELECT d.OrderID, d.Status, i.Status, SYSUTCDATETIME(), SUSER_SNAME()
    FROM inserted i
    JOIN deleted  d ON d.OrderID = i.OrderID
    WHERE ISNULL(i.Status,'') <> ISNULL(d.Status,'');   -- only real changes
END;
```

```sql
UPDATE sales.Orders SET Status = 'Shipped' WHERE OrderID IN (501, 502);
SELECT * FROM sales.Orders_Audit;
```

| AuditID | OrderID | OldStatus | NewStatus | ChangedAt | ChangedBy |
|---|---|---|---|---|---|
| 1 | 501 | Pending | Shipped | 2026-08-21 09:14:02 | svc_etl |
| 2 | 502 | Pending | Shipped | 2026-08-21 09:14:02 | svc_etl |

### The gotcha that causes real outages

**A trigger fires ONCE PER STATEMENT, not once per row.**

```sql
-- BROKEN: assumes exactly one row was affected
CREATE TRIGGER trg_Bad ON sales.Orders AFTER UPDATE AS
BEGIN
    DECLARE @id INT = (SELECT OrderID FROM inserted);   -- ERROR if 2+ rows
    UPDATE sales.Summary SET LastOrder = @id;           -- or silently wrong
END;
```

Update 5,000 rows in one statement and `inserted` holds 5,000 rows. A scalar assignment either errors or arbitrarily picks one. **Triggers must be written set-based**, joining `inserted`/`deleted` as tables — like the audit example above. This bug is invisible in testing (developers test one row at a time) and detonates on the first bulk load.

### `AFTER` vs `INSTEAD OF`

| Type | Runs | Typical use |
|---|---|---|
| `AFTER` (default) | After the DML, inside the same transaction | Auditing, denormalized counters, enforcing rules constraints can't express |
| `INSTEAD OF` | *Replaces* the DML entirely | Making a multi-table [view](10_SQL_Views.md) updatable; routing writes elsewhere |

**Use triggers when:** you need something to happen *no matter which application writes* — audit trails and integrity rules that must not depend on every client remembering.

**Avoid them when:** the logic could live in the pipeline. Triggers are **invisible** — a slow `UPDATE` with no obvious cause is very often a trigger nobody remembered, and a trigger firing row-heavy logic can make a bulk load 100× slower. They also cascade: a trigger's writes fire *other* triggers.

> In warehouses and lakehouses, triggers are largely **absent by design** (Synapse dedicated pools don't support them; Delta has no equivalent). The lakehouse answer to "capture what changed" is [Change Data Feed / CDC](../../06_Data_Engineering/Data_Integration/03_Change_Data_Capture.md), not trigger code.

---

## 5. Temp tables vs table variables vs CTEs vs views

Four ways to hold an intermediate result. Picking wrong is a common cause of "the procedure got slow."

| | `#temp` table | `@table` variable | CTE | [View](10_SQL_Views.md) |
|---|---|---|---|---|
| Lives in | tempdb, session-scoped | Memory/tempdb, batch-scoped | Nowhere — inlined into the query | Catalog, permanent definition |
| Has statistics? | **Yes** | **No** (SQL Server 2019+ improves estimates) | N/A — part of the outer plan | N/A |
| Can be indexed? | Yes, any index | Primary key/unique only | No | Only if indexed/materialized |
| Survives a `ROLLBACK`? | No — rolls back with the transaction | **Yes** — unaffected by rollback | N/A | N/A |
| Referenced more than once? | Cheap — computed once | Cheap | **Re-evaluated each time** | Re-evaluated each time |
| Best for | Large intermediates, multi-use, needs indexing | Small row counts (hundreds), and rollback-surviving logs | Readability, one-time use, recursion | A named, reusable query contract |

**The decision in practice:**

- **CTE** — default choice for readability and for making a [window function](14_SQL_Window_Functions.md) filterable. But referencing the same CTE three times means computing it three times.
- **`#temp` table** — when the intermediate is large, used more than once, or needs an index. Statistics let the optimizer plan the *next* step properly, which is usually the whole reason a temp table beats a CTE.
- **`@table` variable** — small sets, or when you need the rows to **survive a rollback** (the standard trick for logging inside a transaction that may be undone).
- **View** — when the definition is reused across *different* queries by *different* people.

```sql
-- Rollback-surviving log: the classic @table variable use
DECLARE @log TABLE (Msg NVARCHAR(200), LoggedAt DATETIME2);

BEGIN TRY
    BEGIN TRAN;
        INSERT INTO @log VALUES ('starting load', SYSUTCDATETIME());
        -- ... work that fails ...
    COMMIT TRAN;
END TRY
BEGIN CATCH
    ROLLBACK TRAN;                        -- table variable contents SURVIVE this
    INSERT INTO ops.Log SELECT * FROM @log;
END CATCH;
```

---

## 6. Cursors — and why you almost always rewrite them

A **cursor** walks a result set one row at a time, the way a `for` loop walks a list. SQL is a *set-based* language, and a cursor opts out of that.

```sql
-- The cursor way: RBAR -- "Row By Agonizing Row"
DECLARE @OrderID INT, @Amount DECIMAL(10,2);

DECLARE order_cur CURSOR FOR
    SELECT OrderID, Amount FROM sales.Orders WHERE Status = 'Pending';

OPEN order_cur;
FETCH NEXT FROM order_cur INTO @OrderID, @Amount;

WHILE @@FETCH_STATUS = 0
BEGIN
    UPDATE sales.Orders
    SET Discount = CASE WHEN @Amount > 1000 THEN 0.10 ELSE 0.05 END
    WHERE OrderID = @OrderID;

    FETCH NEXT FROM order_cur INTO @OrderID, @Amount;
END;

CLOSE order_cur;
DEALLOCATE order_cur;
```

```sql
-- The set-based way: one statement, one pass, one transaction
UPDATE sales.Orders
SET Discount = CASE WHEN Amount > 1000 THEN 0.10 ELSE 0.05 END
WHERE Status = 'Pending';
```

```text
   100,000 pending orders

   Cursor:      100,000 round trips, 100,000 UPDATE statements,
                100,000 log writes           -> minutes
   Set-based:   1 statement, 1 optimized plan -> under a second
```

Identical result. The set-based version is typically **100–1000×** faster, and it's shorter.

**The legitimate uses** (rare, and they share a shape — the work genuinely isn't set-based):

- Calling a **stored procedure per row** that can't be rewritten (e.g. sending one message per order to a queue).
- **Administrative loops over objects** — "rebuild the index on every table matching a pattern."
- Batched deletes that must be chunked to avoid lock escalation (a `WHILE` loop over `DELETE TOP (10000)` — a loop, but *not* per row).

> When you see a cursor in inherited code, the first question is always "what set-based statement replaces this?" The answer is usually `UPDATE … FROM`, `MERGE`, or a [window function](14_SQL_Window_Functions.md).

---

## 7. Dynamic SQL — building queries as strings

Sometimes the table or column name isn't known until runtime. That's what dynamic SQL is for — and it's where SQL injection lives.

```sql
-- DANGEROUS: string concatenation
DECLARE @sql NVARCHAR(MAX);
SET @sql = 'SELECT * FROM sales.Orders WHERE Status = ''' + @Status + '''';
EXEC(@sql);
```

```text
   If @Status = "x'; DROP TABLE sales.Orders; --"

   the executed string becomes:
      SELECT * FROM sales.Orders WHERE Status = 'x'; DROP TABLE sales.Orders; --'
                                                    ^^^^^^^^^^^^^^^^^^^^^^^^
                                                    a second statement, now running
```

```sql
-- SAFE: sp_executesql with real parameters
DECLARE @sql NVARCHAR(MAX) = N'SELECT * FROM sales.Orders WHERE Status = @p_status';

EXEC sp_executesql @sql,
     N'@p_status VARCHAR(20)',      -- parameter declaration
     @p_status = @Status;           -- value passed separately, never parsed as SQL
```

The value travels **beside** the query text instead of being pasted into it, so it can never be read as code. Parameterizing also lets the engine cache and reuse one plan instead of compiling a new one per distinct string.

> **Identifiers can't be parameterized.** A table or column *name* must be concatenated — so validate it against `sys.tables`/`sys.columns` first, or wrap it in `QUOTENAME(@TableName)`. Never concatenate a raw user-supplied identifier.

**Where data engineers legitimately need it:** metadata-driven pipelines. One procedure that loads *any* table listed in a control table beats fifty near-identical procedures — the same instinct behind [ADF's parameterized pipelines](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md).

---

## 8. Control flow — the procedural bits

```sql
DECLARE @RowCount INT, @Threshold INT = 1000;      -- declare with a default

SELECT @RowCount = COUNT(*) FROM staging.Sales;    -- assign from a query

IF @RowCount = 0
BEGIN
    THROW 50001, 'Staging is empty - upstream extract likely failed.', 1;
END
ELSE IF @RowCount < @Threshold
BEGIN
    INSERT INTO ops.Warnings (Msg) VALUES ('Row count suspiciously low');
END;

-- Batched delete: a loop, but each pass is still set-based
WHILE 1 = 1
BEGIN
    DELETE TOP (10000) FROM sales.FactSales WHERE SaleDate < '2020-01-01';
    IF @@ROWCOUNT = 0 BREAK;
END;
```

That batched-delete loop is worth keeping: deleting 50 million rows in one statement escalates to a table lock and blocks everything. Ten thousand at a time keeps locks short and the transaction log manageable.

---

## 9. The data engineering angle

**Where procedures fit in an Azure pipeline:**

```text
   ADF pipeline
      |
      +-- Copy activity            -> land raw data into staging
      +-- Stored Procedure activity -> EXEC usp_LoadDailySales @LoadDate
      |                                (transformation runs INSIDE the database)
      +-- on failure                -> the proc's THROW surfaces here, pipeline fails
```

The pipeline orchestrates; the procedure does the work next to the data. Millions of rows never cross the network.

**Procedures vs dbt:** both run SQL transformations in the warehouse. [dbt](../../13_dbt/) expresses them as **`SELECT` models** with version control, tests, lineage, and dependency resolution built in; procedures are imperative and give you `MERGE`, loops, and error handling. Modern teams default to dbt for transformation and keep procedures for genuinely procedural work. The deciding factor is usually not power but **discipline**: dbt makes version control and testing the default, whereas procedures only get them if you build that yourself.

**Version control is the real risk.** A procedure edited directly in SSMS exists in exactly one place, with no history and no review. Definitions belong in `.sql` files in git, deployed through [CI/CD](../../14_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md) like any other code.

**Platform support:**

| Platform | Procedures | Triggers | Notes |
|---|---|---|---|
| Azure SQL / SQL Server | Full T-SQL | Yes | The full toolkit described here |
| Synapse **dedicated** pool | Yes | **No** | No triggers, no cursors on some versions; `CREATE PROC` supported |
| Synapse **serverless** | Limited | No | Query-over-files engine, not a programmability host |
| PostgreSQL | `CREATE PROCEDURE` (11+), `plpgsql` functions | Yes | Functions long predate procedures here |
| MySQL | Yes, with `DELIMITER` | Yes | |
| Databricks / Spark SQL | SQL UDFs; no classic stored procedures | **No** | Use notebooks, [DLT](../../08_Databricks/08_Delta_Live_Tables.md), or Workflows instead |
| Microsoft Fabric warehouse | `CREATE PROC` supported | No | |

---

## Field-tested gotchas

- **A trigger fires per statement, not per row.** Any trigger that assigns `inserted` to a scalar variable is broken for multi-row DML — and passes single-row testing.
- **`CATCH` without `THROW` reports success.** The pipeline turns green having done nothing.
- **`RETURN` is for status, not data.** It carries one integer. Someone always tries to return a row count through it and then wonders why large counts break.
- **Scalar UDFs in `WHERE` clauses also kill index seeks** — `WHERE dbo.fn_Year(OrderDate) = 2026` is non-[sargable](06_SQL_DQL.md) for exactly the same reason `WHERE YEAR(OrderDate) = 2026` is.
- **Table variables survive `ROLLBACK`.** Useful for logging, surprising when you assumed the data was undone with everything else.
- **Nested triggers and recursion.** A trigger that writes to a table with its own trigger cascades. `RECURSIVE_TRIGGERS` off by default doesn't stop *indirect* recursion.
- **Dynamic SQL with concatenated identifiers** is injectable even when the *values* are parameterized. `QUOTENAME()` or validate against system catalogs.
- **`SET NOCOUNT OFF` (the default)** sends a row-count message per statement — measurable overhead in loops, and some ORMs misread them as result sets.
- **Procedures cache a plan based on the first parameter values they see** (parameter sniffing). A proc that's fast for one customer and catastrophically slow for another is the classic symptom; `OPTION (RECOMPILE)` or local variable copies are the usual mitigations.

---

## Interview-grade Q&A

- *Stored procedure vs function?* A procedure can modify data, is called with `EXEC` as its own statement, and can return multiple result sets; a function cannot modify data, is used inline inside a query, and returns one value or one table. You cannot `SELECT` from a procedure.
- *Which UDF type would you use and why?* Inline table-valued — the optimizer expands it into the calling query. Avoid scalar UDFs in hot paths (per-row execution, parallelism loss) and multi-statement TVFs (opaque to the optimizer, bad row estimates).
- *How do you make a stored procedure safe to re-run?* Make it idempotent: delete-then-insert (or `MERGE`) scoped to the partition being loaded, wrapped in an explicit transaction with `TRY…CATCH` and `THROW`.
- *What's wrong with this trigger?* If it treats `inserted` as a single row, it's broken for multi-row DML. Triggers fire once per statement — write them set-based.
- *When would you use a cursor?* Almost never. Only when the work is genuinely per row (calling a proc per record) or is administrative looping. Otherwise rewrite as `UPDATE … FROM`, `MERGE`, or a window function.
- *Temp table or table variable?* Temp table for large intermediates, multiple references, or when you need indexes and statistics. Table variable for small sets, or when the rows must survive a rollback.
- *How do you prevent SQL injection in dynamic SQL?* `sp_executesql` with declared parameters, so values are never parsed as code. Identifiers can't be parameterized — validate them or use `QUOTENAME()`.
- *Why might a procedure be fast for one input and slow for another?* Parameter sniffing — the cached plan was compiled for the first set of parameter values and suits a different data distribution.
- *Procedures or dbt for warehouse transformations?* dbt for declarative `SELECT`-based models where version control, testing, and lineage come free; procedures for genuinely imperative work. The real argument is engineering discipline, not capability.

---

## Further Learning — Docs & Videos

**Documentation**
- CREATE PROCEDURE (T-SQL): https://learn.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql
- TRY…CATCH error handling: https://learn.microsoft.com/en-us/sql/t-sql/language-elements/try-catch-transact-sql
- Scalar UDF inlining: https://learn.microsoft.com/en-us/sql/relational-databases/user-defined-functions/scalar-udf-inlining
- PostgreSQL PL/pgSQL: https://www.postgresql.org/docs/current/plpgsql.html

**Videos**
- SQL stored procedures explained: https://www.youtube.com/results?search_query=sql+stored+procedures+explained
- SQL triggers explained: https://www.youtube.com/results?search_query=sql+triggers+explained
- Why cursors are slow (set-based vs RBAR): https://www.youtube.com/results?search_query=sql+cursor+vs+set+based
