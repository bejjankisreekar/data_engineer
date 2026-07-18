# SQL Warehouse (Data Warehouse)

## What is a SQL Warehouse?

A SQL Warehouse stores huge amounts of historical business data for reporting and analytics.

Analogy: if a [SQL Database](SQL_Database.md) is a shop's cash register — recording each individual sale the instant it happens — a warehouse is the head office's year-end report, pulling together every till receipt from every store to answer big-picture questions like "which region sold the most this quarter?"

Unlike a SQL Database, data is rarely updated.

Instead, it is continuously loaded from different systems.

Example sources:

- ERP
- CRM
- HRMS
- Sales System
- Website Logs
- APIs

All data is combined into one place.

---

## Why use a Warehouse?

To answer business questions like:

- Total sales this year
- Best selling products
- Monthly revenue
- Customer growth
- Profit trends

---

## Example

Imagine Amazon.

Orders Table

10 million rows

Customers Table

2 million rows

Products Table

500,000 rows

The warehouse combines all of them for analysis.

---

## Typical Workflow

Applications
        ↓
SQL Databases
        ↓
ETL / ELT
        ↓
SQL Warehouse
        ↓
Power BI
        ↓
Reports

---

## Characteristics

- Read-heavy
- Historical data
- Optimized for analytics — this pattern is called OLAP (Online Analytical Processing), covered in the [Glossary](../GLOSSARY.md#databases-and-transactions)
- Large datasets
- Star schema — one central "facts" table (e.g. Sales) surrounded by smaller lookup tables (e.g. Products, Customers, Dates), connected the same way described in [Keys and Joins](SQL_Keys_and_Joins.md)
- Snowflake schema — like a star schema, but the lookup tables are broken down further into their own sub-tables

---

## Azure SQL Warehouse

Modern equivalent:

Azure Synapse Analytics

or

Microsoft Fabric Warehouse

---

## Advantages

- Very fast reporting
- Handles billions of rows
- Excellent for BI
- Historical analysis
- Business intelligence

---

## Example Query

Total sales per month

```sql
SELECT
Month,
SUM(SalesAmount)
FROM Sales
GROUP BY Month;
```

---

## Where does this data come from?

A warehouse doesn't collect its own data — it's filled by pipelines that pull data in from elsewhere. See [ETL vs ELT](../04_ETL_ELT/ETL_vs_ELT.md) for the two common ways this data-loading happens, and [Data Lake vs Warehouse vs Database](../03_Data_Storage/Data_Lake_vs_Warehouse_vs_Database.md) for how a warehouse fits alongside raw storage.

## SQL Database vs Warehouse

| SQL Database | SQL Warehouse |
|--------------|---------------|
|OLTP|OLAP|
|Current data|Historical data|
|Many updates|Few updates|
|Small to medium|Very large|
|Applications|Analytics|
|Fast transactions|Fast reporting|

---

## Real World Example

Hospital

Database

- New patient
- Doctor appointment
- Billing

Warehouse

- Total patients this year
- Disease trends
- Revenue analysis
- Insurance claims