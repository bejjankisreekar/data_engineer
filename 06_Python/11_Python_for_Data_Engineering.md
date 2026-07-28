# 11 — Python for Data Engineering

This closing file connects everything you've learned to the actual job — and to **module 07 (PySpark)**, where the same ideas scale to big data. It's a bridge, not a deep dive: a taste of pandas plus the mental model that carries into Spark.

---

## Where Python fits in a data pipeline

A data engineer's core loop is **Extract → Transform → Load**, on a schedule, reliably. Python is the glue for all of it:

| Stage | What Python does | Tools |
|---|---|---|
| **Extract** | Call APIs, read files, query databases | `requests`, `os`, DB drivers, cloud SDKs |
| **Transform** | Clean, reshape, join, aggregate data | `pandas` (small data), **PySpark** (big data) |
| **Load** | Write to a warehouse/lake/table | connectors, Spark writers |
| **Orchestrate** | Schedule, retry, alert, order tasks | Airflow, Databricks Jobs |

Everything in files 01–10 shows up here: variables, strings (paths), lists/dicts (records & config), loops/conditionals (per-file logic and data-quality rules), functions (pipeline steps), files & exceptions (I/O and robustness), modules & venvs (dependencies).

---

## pandas — the single-machine data workhorse

**pandas** is the most popular Python library for working with tabular data on **one machine**. Its main object is the **DataFrame** — a table with named columns, much like a spreadsheet or SQL table. Learning it now makes PySpark's DataFrame feel familiar.

```python
import pandas as pd

# Read a CSV into a DataFrame
df = pd.read_csv("orders.csv")

df.head()                     # first 5 rows
df.shape                      # (rows, columns)
df.columns                    # column names
df.info()                     # types and non-null counts

# Select and filter
df["amount"]                          # one column
df[["id", "amount"]]                  # several columns
df[df["amount"] > 100]                # rows where amount > 100

# Create / transform a column
df["amount_with_tax"] = df["amount"] * 1.18

# Group and aggregate (like SQL GROUP BY)
df.groupby("country")["amount"].sum()

# Handle missing values
df["amount"].fillna(0)                # replace NaN with 0
df.dropna(subset=["id"])              # drop rows missing an id

# Write out
df.to_parquet("orders_clean.parquet")
```

Notice how this mirrors SQL (module 01): select, filter (`WHERE`), `groupby` (`GROUP BY`), and file formats (module 02: CSV in, Parquet out).

---

## pandas vs PySpark — when to use which

| | pandas | PySpark |
|---|---|---|
| Runs on | **One machine**, in memory | A **cluster**, distributed |
| Data size | Up to a few GB (fits in RAM) | GBs to PBs (bigger than memory) |
| API feel | DataFrame with columns | DataFrame with columns (very similar!) |
| Best for | Small/medium data, quick analysis, prototypes | Big data, production pipelines, lakehouse |

> **Rule of thumb:** If the data fits comfortably in memory on one machine, pandas is simpler. When it's too big — or you're building a production pipeline on Databricks/Spark — you move to **PySpark**. The good news: the DataFrame concepts transfer almost directly.

The key conceptual jump you'll make in module 07 is **lazy, distributed execution** — Spark spreads the same select/filter/groupby work across many machines and only runs it when you ask for a result. But the *shape* of the code (columns, filters, group-bys) is what you just saw in pandas.

---

## A tiny end-to-end example (everything together)

```python
import pandas as pd

def run_pipeline(input_path, output_path):
    try:
        df = pd.read_csv(input_path)                 # extract
    except FileNotFoundError:
        print(f"Missing input: {input_path}")
        return 0

    df = df.dropna(subset=["id"])                    # transform: drop bad rows
    df["email"] = df["email"].str.strip().str.lower()
    df = df[df["amount"] > 0]                         # data-quality rule

    df.to_parquet(output_path)                       # load
    return len(df)

if __name__ == "__main__":
    rows = run_pipeline("orders.csv", "orders_clean.parquet")
    print(f"Loaded {rows} clean rows")
```

This 15-line script uses: functions, arguments, `try/except`, files, strings, conditionals, and a DataFrame — the whole module, working as one small pipeline.

---

## Where to go next

- **Module 07 — PySpark:** the distributed version of everything here. Your Python fluency lets you focus on *big-data concepts* (partitions, shuffles, lazy evaluation) instead of syntax.
- **Module 09 — Git & GitHub:** version-control your pipeline code and ship it with CI/CD.
- **The Databricks certification track** (`9999_certificates_exams/`): applies Python + Spark + Delta on the lakehouse.

---

## Why it matters for data engineering

This is the job, in miniature. A data engineer who knows Python can read almost any data tool's API, automate any repetitive data task, build robust ingestion and transformation, and step up to distributed processing with Spark without relearning how to program. Files 01–10 gave you the language; this file showed you the shape of the work it powers.

---

## Further Learning — Docs & Videos

**Documentation**
- pandas — Getting started: https://pandas.pydata.org/docs/getting_started/index.html
- pandas 10-minute intro: https://pandas.pydata.org/docs/user_guide/10min.html
- From pandas to PySpark: https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html
- Python for data engineering (overview): https://www.databricks.com/glossary/pyspark

**Videos**
- pandas full tutorial for beginners: https://www.youtube.com/results?search_query=pandas+tutorial+for+beginners
- pandas vs PySpark for data engineering: https://www.youtube.com/results?search_query=pandas+vs+pyspark+data+engineering

Next: test yourself with the **[Interview Questions & Answers](Interview_Questions_and_Answers.md)**.
