# ORC (Optimized Row Columnar)

## What is ORC?

ORC is a columnar file format, in the same family as [Parquet](Parquet.md) — data is stored column by column instead of row by row, and the schema is stored inside the file. ORC was created in the Hadoop/Hive ecosystem, while Parquet grew up around Spark; today the two formats solve the same problem in very similar ways.

---

## Column Storage, Refresher

EmployeeID column

```
101
102
103
```

Salary column

```
60000
50000
65000
```

Just like Parquet, if a query only needs the Salary column, ORC only has to read that column's data — not the entire table.

---

## What makes ORC distinct

- **Built-in indexes** — ORC stores lightweight statistics (min/max values, row counts) for chunks of each column, so a query can skip entire sections of a file that can't possibly contain a match. Think of it like a book's index telling you a topic definitely isn't on pages 50–90, so you never open those pages.
- **Strong compression** — ORC typically compresses slightly better than Parquet on similar data, at the cost of a bit more CPU time to read/write.
- **Deep Hive integration** — ORC was designed specifically to work well with Apache Hive, a SQL-like query engine for Hadoop.

---

## Advantages

- Highly compressed
- Fast for analytical queries (column pruning, like Parquet)
- Built-in indexing skips irrelevant data automatically
- Good for very large, append-heavy datasets

---

## Disadvantages

- Less universally supported outside the Hadoop/Hive ecosystem than Parquet
- Smaller community and tooling support in the Azure/Spark/Databricks world compared to Parquet
- Not human-readable

---

## Used In

- Apache Hive
- Hadoop-based data lakes
- Legacy big-data platforms migrating toward Azure

---

## Azure Usage

- Azure Synapse and Databricks can both read ORC files, mainly to support data migrated from existing Hadoop/Hive systems
- New Azure projects typically choose Parquet by default; ORC mainly shows up when importing from an existing on-premises Hadoop estate

---

## ORC vs Parquet, in one line

Both are columnar and serve the same purpose. Parquet has become the default choice in most new Azure/Spark/Databricks projects, while ORC is more common if your data already comes from a Hive/Hadoop system. See [File_Format_Comparison.md](File_Format_Comparison.md) for a full side-by-side.
