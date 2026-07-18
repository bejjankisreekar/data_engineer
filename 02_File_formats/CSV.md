# CSV (Comma Separated Values)

## What is CSV?

CSV is a plain text file where each row is separated by a new line and columns are separated by commas.

Analogy: it's exactly what you'd get if you took a spreadsheet and stripped away all the formatting — no colors, no formulas, no cell merging — leaving just the raw values separated by commas. That simplicity is exactly why almost every tool on earth can open a CSV file.

Example:

```csv
EmployeeID,Name,Department,Salary
101,John,IT,60000
102,Alice,HR,50000
103,David,Finance,55000
```

---

## Advantages

- Easy to read
- Human readable
- Supported everywhere
- Small learning curve

---

## Disadvantages

- No compression
- No schema
- No nested data
- Large file size

---

## Used In

- Excel exports
- Data sharing
- Small datasets
- Import/Export

---

## Azure Usage

ADF

Databricks

Synapse

Power BI

All can read CSV files.

---

## Where CSV Fits

CSV is usually where a data journey *starts* (a raw export from an old system) rather than where it stays. See [File Format Comparison](File_Format_Comparison.md) for how CSV compares to [JSON](JSON.md), [Avro](Avro.md), [ORC](ORC.md), and [Parquet](Parquet.md), and when it's worth converting away from it.