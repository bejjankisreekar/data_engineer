# SQL Data Types

## Why data types matter

Every column in a table must be given a **data type** when it's created — a rule about what kind of value it's allowed to hold. This is what stops someone from typing "banana" into a Salary column, or a date into a Name column.

Analogy: think of a paper form with labeled boxes — one box says "Date of Birth" and is clearly meant for a date, another says "Age" and is meant for a whole number. A data type is that label, enforced automatically by the database instead of left to whoever's filling out the form.

---

## Common Data Types

| Category | Type (T-SQL / general SQL) | Holds | Example |
|---|---|---|---|
| Whole numbers | `INT` | Whole numbers, no decimals | `60000` |
| Decimal numbers | `DECIMAL(p,s)` / `FLOAT` | Numbers with decimal places | `1999.50` |
| Short text | `VARCHAR(n)` | Text up to a set maximum length | `'John'` |
| Long text | `TEXT` | Very large amounts of text | An entire article |
| Date only | `DATE` | Calendar date | `2026-07-17` |
| Date and time | `DATETIME` | Date plus a time of day | `2026-07-17 14:30:00` |
| True/False | `BIT` (T-SQL) / `BOOLEAN` | Yes/no, true/false | `1` or `0` |
| Money | `MONEY` / `DECIMAL(19,4)` | Currency values | `5000.00` |

`VARCHAR(50)` means "text, up to 50 characters." If you try to store a 51-character name, the database rejects it — the same way a paper form's name box would run out of physical space.

---

## Why not just store everything as text?

You technically could store `"60000"` as text instead of a number — but then the database can no longer do numeric operations correctly. Sorting `"9"`, `"10"`, `"2"` as text gives you `"10", "2", "9"` (comparing character by character), while sorting them as numbers correctly gives `2, 9, 10`. Choosing the right data type isn't just bookkeeping — it changes how the data behaves.

---

## Data Types in Practice

```sql
CREATE TABLE Employee (
    EmployeeID INT,
    Name VARCHAR(50),
    HireDate DATE,
    Salary DECIMAL(10,2)
);
```

This table definition — using `CREATE`, covered in [SQL_DDL.md](SQL_DDL.md) — locks in the shape of every future row: `EmployeeID` must be a whole number, `Name` up to 50 characters of text, `HireDate` a calendar date, and `Salary` a decimal number with up to 2 digits after the point.

---

## Azure Usage

Azure SQL Database and Azure Synapse Analytics both use T-SQL data types (`INT`, `VARCHAR`, `DATETIME2`, `DECIMAL`, and so on). When designing a table for a data warehouse, picking the smallest data type that safely fits the data (e.g. `INT` instead of a larger type, if values will never exceed a few million) reduces storage cost and speeds up queries across billions of rows.

---

## Real World Example

A hospital's patient records table stores `DateOfBirth` as a `DATE`, not text, specifically so the database can calculate a patient's current age automatically and correctly sort patients by birthday — something that would require constant manual correction if birthdates were just free-form text typed in however each staff member preferred.
