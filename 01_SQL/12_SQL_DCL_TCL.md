# SQL DCL and TCL (Access Control and Transactions)

## Two categories, one file

[01_What_is_SQL.md](01_What_is_SQL.md) introduced five command categories. This file covers the last two — DCL (who's allowed to do what) and TCL (how a group of changes is saved or undone) — because both are about *controlling* SQL's behavior rather than directly working with structure or data.

---

## DCL — Data Control Language

DCL commands manage **permissions**: who is allowed to read, change, or manage a table.

Analogy: DCL is the sign-in sheet and key list for the filing cabinet — deciding which staff members are allowed to open which drawers, and what they're allowed to do once they're in (just look, or also edit and remove).

### GRANT — giving permission

```sql
GRANT SELECT ON Employee TO ReportingTeam;
```

Allows the `ReportingTeam` user/role to run `SELECT` queries against the Employee table — but not to `INSERT`, `UPDATE`, or `DELETE` unless separately granted.

```sql
GRANT SELECT, INSERT, UPDATE ON Employee TO HRTeam;
```

### REVOKE — taking permission away

```sql
REVOKE INSERT ON Employee FROM HRTeam;
```

Removes a previously granted permission. `HRTeam` can still `SELECT` and `UPDATE`, but can no longer `INSERT` new rows.

### Why this matters

Not everyone who needs to *read* company data should be able to *change* it. A finance analyst building a report typically only needs `SELECT` access — granting them `DELETE` access "just in case" is an unnecessary risk, the same way a security guard checking IDs at a door doesn't also need a key to the safe inside.

---

## TCL — Transaction Control Language

A **transaction** is a group of one or more DML statements treated as a single, all-or-nothing unit (this ties directly to the ACID guarantees in the [Glossary](../GLOSSARY.md#databases-and-transactions)). TCL commands manage when that group of changes becomes permanent, or gets undone.

### COMMIT — making changes permanent

```sql
BEGIN TRANSACTION;

UPDATE Account SET Balance = Balance - 500 WHERE AccountID = 1;
UPDATE Account SET Balance = Balance + 500 WHERE AccountID = 2;

COMMIT;
```

Both `UPDATE` statements together represent "transfer 500 from Account 1 to Account 2." `COMMIT` saves both changes permanently, together. If the system crashed between the two `UPDATE` statements and before `COMMIT`, neither change would be saved — money can never leave one account without arriving in the other.

### ROLLBACK — undoing changes

```sql
BEGIN TRANSACTION;

UPDATE Account SET Balance = Balance - 500 WHERE AccountID = 1;
-- something looks wrong here

ROLLBACK;
```

`ROLLBACK` undoes every change made since the transaction began, as if none of it had happened. This is the safety net that makes it possible to test a risky-looking set of changes and back out cleanly if something's off — as long as `COMMIT` hasn't already been run.

### SAVEPOINT — a partial undo point

```sql
BEGIN TRANSACTION;

UPDATE Account SET Balance = Balance - 500 WHERE AccountID = 1;
SAVEPOINT AfterWithdrawal;

UPDATE Account SET Balance = Balance + 500 WHERE AccountID = 2;
-- problem found here

ROLLBACK TO AfterWithdrawal;
-- only the second UPDATE is undone; the first still stands

COMMIT;
```

A `SAVEPOINT` marks a checkpoint partway through a transaction, so you can undo *part* of the work without throwing away all of it.

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both support standard DCL and TCL. In practice, most day-to-day pipeline and report authors rarely write `GRANT`/`REVOKE` themselves — permissions are more often managed centrally by a database administrator, sometimes through Azure's role-based access control (RBAC) layered on top of SQL-level permissions. TCL, on the other hand, shows up constantly in application code: nearly every multi-step update (like a bank transfer) is wrapped in an explicit transaction.

---

## Real World Example

A bank's transfer feature wraps the "subtract from Account A, add to Account B" pair of updates inside a single transaction. If a network failure interrupts the process after the first update but before `COMMIT`, the entire transaction rolls back automatically, and the money never appears to vanish. Separately, the bank's DCL rules ensure a customer-facing app can `INSERT` new transactions but can never `DROP` the Account table itself.

---
---

# Part 2 — Advanced

## DCL done properly: roles, least privilege, and layers

Granting to individual users doesn't scale past ten people. The professional structure:

```sql
CREATE ROLE reporting_reader;
GRANT SELECT ON SCHEMA::mart TO reporting_reader;   -- grant at schema level, not per table
ALTER ROLE reporting_reader ADD MEMBER [aad_group_Analysts];  -- membership via AD group
```

Principles that survive audits:

- **Least privilege** — start from nothing; add narrowly. No human gets `db_owner` "temporarily."
- **Roles ↔ job functions, groups ↔ people** — joiners/leavers are handled in Entra ID, not in SQL.
- **Schema-level grants** — new tables in `mart` are automatically covered; per-table grant sprawl is unauditable.
- **`DENY` (T-SQL) trumps GRANT** — useful for carve-outs ("everything except Salary"), dangerous when forgotten.
- Finer tools when columns/rows matter: column-limited [views](10_SQL_Views.md), **Row-Level Security** policies, **Dynamic Data Masking** — and in the lakehouse, Unity Catalog's `GRANT SELECT ON catalog.schema.table` plus row filters/column masks: same DCL concepts, new engine.

## Isolation levels — what your transaction sees of others

TCL guarantees *your* changes commit atomically; **isolation levels** decide how much of *other* concurrent transactions you observe ([anomaly table](../00_Fundamentals/01_OLTP_Storage.md)):

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- typical default
```

- The pragmatic modern choice in SQL Server: **Read Committed Snapshot (RCSI)** — readers get a version-based snapshot, so readers and writers stop blocking each other (Azure SQL DB has it on by default).
- `NOLOCK` hint = read uncommitted: can read rows that are later rolled back, *and* can skip/double-read rows during page splits. In a financial report this is a career-limiting hint — use snapshot isolation instead.
- Higher isolation (Repeatable Read/Serializable) buys correctness with locks/aborts; reserve for genuinely invariant-critical sections (inventory decrement, ledger close).

## Transactions in practice: keep them short and handle the exits

```sql
BEGIN TRY
    BEGIN TRANSACTION;
    UPDATE Account SET Balance = Balance - 500 WHERE AccountID = 1;
    UPDATE Account SET Balance = Balance + 500 WHERE AccountID = 2;
    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;    -- never swallow — the caller must know it failed
END CATCH;
```

The cardinal sins: user interaction inside an open transaction, network calls inside a transaction, and the **forgotten open transaction** — one uncommitted session can block a table (and hold the [transaction log](02_SQL_Database.md)) for hours. Monitoring open long transactions is standard ops hygiene.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Deadlocks — anatomy and the standard defenses

Transaction A locks row 1 then wants row 2; B locks row 2 then wants row 1 → the engine kills one (error 1205, "deadlock victim"). Professional defenses, in order:

1. **Touch tables/rows in a consistent order** across all code paths (alphabetical, by key ascending — pick one, enforce it).
2. Keep transactions short and indexed (lock fewer rows for less time — [unindexed FKs](11_SQL_Indexes.md) are deadlock factories).
3. RCSI/snapshot isolation removes reader-writer deadlocks entirely.
4. **Retry logic** for the survivors: deadlocks are transient by definition; a 1205 should trigger an automatic retry with backoff, not a page to on-call.

## Transactions in the lakehouse — same ACID, different mechanics

Delta Lake gives ACID per table via an [optimistic-concurrency transaction log](../06_PySpark/Why_Spark_Why_Databricks.md): writers prepare files, then attempt to commit a new log version; a conflicting concurrent commit fails one writer (`ConcurrentAppendException`) who must retry. Key differences from a database engine:

- **No multi-table transactions** — you cannot atomically commit across two Delta tables; design so each table's write is independently idempotent ([idempotent DML](05_SQL_DML.md)).
- **No locks** — long "transactions" don't block anyone; conflicts surface at commit time instead.
- Isolation ≈ snapshot: readers always see the last committed version (time travel is reading *older* snapshots).

Distributed transactions across systems (DB + queue + lake) are avoided rather than solved: the **outbox pattern**, idempotent consumers, and sagas replaced two-phase commit in modern architecture — worth knowing by name for design interviews.

## Auditing & compliance — DCL's grown-up sibling

Who *can* access is DCL; who *did* access is auditing. Enterprise reality: SQL Audit / Purview / Unity Catalog audit logs shipped to a SIEM, periodic **access reviews** ("does this leaver's group still have PII read?"), and separation of duties (the person granting rights isn't the person using them). GDPR/SOX turn these from best practices into legal requirements — data engineers get pulled into "prove who could see this column" conversations regularly.

## Field-tested gotchas

- `GRANT ... WITH GRANT OPTION` lets the grantee re-grant — permission trees sprout in the dark; avoid, and audit for it.
- Revoking a role's permission doesn't kill **active sessions** using it — force reconnection for immediate effect.
- In migrations, DDL is transactional in Postgres (rollback-able!) but only partially in MySQL/Oracle — a failed half-migration behaves totally differently per engine ([migrations](04_SQL_DDL.md)).
- `SAVEPOINT`s don't release locks — "partial rollback" keeps everything acquired since BEGIN locked until the final COMMIT/ROLLBACK.
- Service accounts with `db_owner` because "the pipeline needed it once" are the #1 finding in real security reviews — pipelines need exactly INSERT/UPDATE/DELETE/SELECT on their targets, nothing more.

## Interview-grade Q&A

- *How do you structure permissions for a 200-person analytics org?* AD-group-backed roles, schema-level grants on curated schemas, views/RLS for row-column limits, zero direct user grants, quarterly access review.
- *A report shows a row that "never existed" — how?* Dirty read via NOLOCK/read-uncommitted caught a later-rolled-back insert; move to RCSI.
- *Deadlock strategy?* Consistent access order + short indexed transactions + snapshot isolation + automatic retry on 1205.
- *Do Delta tables have transactions?* Yes — single-table ACID via optimistic commits on the transaction log; cross-table atomicity must be designed, not assumed.

---

## Further Learning — Docs & Videos

**Documentation**
- GRANT/REVOKE (PostgreSQL): https://www.postgresql.org/docs/current/sql-grant.html
- Transactions COMMIT/ROLLBACK (PostgreSQL): https://www.postgresql.org/docs/current/tutorial-transactions.html

**Videos**
- SQL DCL & TCL (GRANT, COMMIT, ROLLBACK): https://www.youtube.com/results?search_query=sql+dcl+tcl+grant+revoke+commit+rollback
