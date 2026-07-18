# SQL DQL (Data Query Language)

## What is DQL?

DQL is the part of SQL used purely to **read** data, without changing anything. It has exactly one command: `SELECT`. Given how often it's used, `SELECT` arguably deserves its own category more than any other keyword in SQL.

---

## The Basic Shape

```sql
SELECT column1, column2
FROM TableName
WHERE condition
ORDER BY column1;
```

Read as a sentence: "get these columns, from this table, only for rows matching this condition, sorted by this column."

---

## SELECT — choosing columns

```sql
-- Every column
SELECT * FROM Employee;

-- Specific columns only
SELECT Name, Salary FROM Employee;
```

Using `*` is convenient while exploring data, but naming specific columns is better practice in real pipelines and reports — it's clearer what's being retrieved, and it keeps working correctly even if someone adds a new column to the table later.

---

## WHERE — filtering rows

```sql
SELECT * FROM Employee
WHERE Department = 'IT';
```

Common comparison operators:

| Operator | Meaning |
|---|---|
| `=` | Equal to |
| `!=` or `<>` | Not equal to |
| `>` , `<` | Greater than, less than |
| `>=` , `<=` | Greater than or equal to, less than or equal to |

Combine conditions with `AND` / `OR`:

```sql
SELECT * FROM Employee
WHERE Department = 'IT' AND Salary > 60000;
```

---

## Handy Filtering Keywords

```sql
-- Matches any of a list of values
SELECT * FROM Employee
WHERE Department IN ('IT', 'HR');

-- Matches a range (inclusive)
SELECT * FROM Employee
WHERE Salary BETWEEN 50000 AND 65000;

-- Pattern matching: % means "any characters"
SELECT * FROM Employee
WHERE Name LIKE 'J%';   -- names starting with J

-- Checking for missing values
SELECT * FROM Employee
WHERE PhoneNumber IS NULL;
```

**A note on NULL**: `NULL` means "no value recorded" — it isn't the same as zero or an empty string. You can never test for it with `= NULL`; you must use `IS NULL` or `IS NOT NULL`. This trips up almost everyone the first time they hit it.

---

## DISTINCT — removing duplicates

```sql
SELECT DISTINCT Department
FROM Employee;
```

Returns each department name once, even if hundreds of employees share it — useful for quickly seeing "what values actually exist in this column."

---

## ORDER BY — sorting results

```sql
SELECT Name, Salary
FROM Employee
ORDER BY Salary DESC;
```

`ASC` (ascending, smallest/earliest first) is the default; `DESC` reverses it (largest/latest first).

---

## Putting it together

```sql
SELECT Name, Department, Salary
FROM Employee
WHERE Department IN ('IT', 'Finance')
  AND Salary > 55000
ORDER BY Salary DESC;
```

"Show me the name, department, and salary of every IT or Finance employee earning more than 55000, sorted highest salary first."

---

## Azure Usage

`SELECT` queries are how analysts and Power BI reports actually pull data out of Azure SQL Database or Azure Synapse Analytics — DQL is the command category end users interact with the most, even if they never touch DDL or DML directly.

---

## Real World Example

A store manager wants to know: "Which products priced over 500, in the Electronics category, are we running low on?" That entire business question translates directly into one `SELECT` statement with a `WHERE` clause combining several conditions, sorted by remaining stock — no other SQL command category is needed just to answer a question.
