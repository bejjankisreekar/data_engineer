# SQL Keys and Joins

## Why this file exists

[SQL_Database.md](SQL_Database.md) showed one table (Employee). In real systems, data is split across *many* tables, and you need a way to connect them back together. That connection relies on **keys** and **joins**.

Analogy: imagine a filing cabinet with one drawer for Customers and a separate drawer for Orders. Instead of re-writing a customer's full name and address on every single order form, each order form just references a Customer ID. To see a customer's full order history, you match the ID on the order form to the ID in the customer drawer. That matching is exactly what a join does.

---

## Primary Key

A **primary key** is the column that uniquely identifies each row in a table. No two rows can have the same value, and it can never be empty.

Customer Table

| CustomerID (primary key) | Name | City |
|---|---|---|
| 1 | Meera | Hyderabad |
| 2 | Raj | Pune |

`CustomerID` is the primary key — it's how every other table will refer to "this exact customer."

---

## Foreign Key

A **foreign key** is a column in one table that points to the primary key of another table.

Order Table

| OrderID | CustomerID (foreign key) | Amount |
|---|---|---|
| 501 | 1 | 2000 |
| 502 | 1 | 1500 |
| 503 | 2 | 3000 |

`CustomerID` in the Order table isn't the order's own identity — it's a pointer back to the Customer table. This is how the database knows order 501 belongs to Meera without repeating her name and city on every row.

---

## Why not just repeat the data everywhere?

Without keys, every order row would need to repeat the customer's name, city, and every other detail. That causes two problems:

- **Wasted space** — the same customer details copied hundreds of times.
- **Inconsistency** — if Meera moves to a new city, you'd have to find and update every single order row. Miss one, and now your data disagrees with itself.

Splitting data into separate tables connected by keys, and storing each fact only once, is called **normalization**.

---

## Joins

A **join** combines rows from two tables using a shared key — usually the primary key of one table matched against the foreign key of another.

```sql
SELECT
    Order.OrderID,
    Customer.Name,
    Order.Amount
FROM Order
JOIN Customer
    ON Order.CustomerID = Customer.CustomerID;
```

Result

| OrderID | Name | Amount |
|---|---|---|
| 501 | Meera | 2000 |
| 502 | Meera | 1500 |
| 503 | Raj | 3000 |

The query reunites data that normalization intentionally kept apart.

---

## Common Join Types

| Join Type | Returns |
|---|---|
| INNER JOIN | Only rows that match in both tables |
| LEFT JOIN | All rows from the left table, plus matches from the right (unmatched right side is blank) |
| RIGHT JOIN | All rows from the right table, plus matches from the left |
| FULL JOIN | All rows from both tables, matched where possible |

Example: a LEFT JOIN from Customer to Order would still show a customer who has never placed an order — with blank order details — because "all customers" is the priority, not "only customers with orders."

---

## Real World Example

An insurance company keeps:

- A **Policyholders** table (one row per person)
- A **Claims** table (one row per claim, referencing a Policyholder via a foreign key)

A claims officer never re-types a policyholder's full details onto every claim. They just reference the Policyholder ID, and a join pulls the full policyholder details back in whenever a report is generated. This is the same pattern behind almost every business system: banking, healthcare, retail, and HR.
