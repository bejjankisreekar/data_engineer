# SQL DCL and TCL (Access Control and Transactions)

## Two categories, one file

[What_is_SQL.md](What_is_SQL.md) introduced five command categories. This file covers the last two — DCL (who's allowed to do what) and TCL (how a group of changes is saved or undone) — because both are about *controlling* SQL's behavior rather than directly working with structure or data.

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
