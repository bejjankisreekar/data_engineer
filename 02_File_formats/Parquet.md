# Parquet

## What is Parquet?

Parquet is a columnar storage file format developed for Big Data.

Unlike CSV, data is stored column by column instead of row by row.

Analogy: imagine a library that, instead of shelving books individually, keeps a separate index card box for every single fact — one box just for "titles," one just for "authors," one just for "publish years." If someone only wants a list of publish years, they can flip through one box instead of pulling every book off every shelf. That's the advantage columnar storage gives over row storage.

---

## Row Storage

CSV

```
101 John IT 60000
102 Alice HR 50000
103 David IT 65000
```

---

## Column Storage

EmployeeID

```
101
102
103
```

Name

```
John
Alice
David
```

Department

```
IT
HR
IT
```

Salary

```
60000
50000
65000
```

---

## Why is this faster?

Suppose you only need Salary.

CSV

Reads entire file.

Parquet

Reads only Salary column.

Huge performance improvement.

---

## Advantages

- Highly compressed — repeated values (like a Department column full of "IT," "IT," "HR") squeeze down efficiently, since similar values are stored next to each other (see [Glossary](../GLOSSARY.md#storage-and-files))
- Very fast
- Schema included — the file itself records what columns exist and their types, so no separate documentation is needed to read it
- Column pruning — a query only reads the specific columns it asks for, ignoring the rest of the table entirely
- Predicate pushdown — if a query filters for `Salary > 60000`, Parquet can skip entire chunks of data upfront, without reading each individual row and checking it one by one, because it keeps track of the minimum/maximum value stored in each chunk
- Great for analytics

For a side-by-side against the other row/columnar formats in this folder, see [File Format Comparison](File_Format_Comparison.md).

---

## Used In

Databricks

Spark

Azure Synapse

Data Lakes

Delta Lake

Machine Learning

---

## Azure Usage

Most Azure Data Engineering projects store data in Parquet format.