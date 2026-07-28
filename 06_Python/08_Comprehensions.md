# 08 — Comprehensions

## What is a comprehension?

A **comprehension** is a concise, one-line way to build a list, dictionary, or set from another collection. It replaces a multi-line loop that just builds up a result.

**The idea:** "give me a new collection made by doing X to each item, optionally keeping only the ones that match a condition."

---

## List comprehensions

Compare the loop version with the comprehension:

```python
# Loop version
squares = []
for n in range(5):
    squares.append(n * n)
# [0, 1, 4, 9, 16]

# Comprehension — same result, one line
squares = [n * n for n in range(5)]
```

Read it as: **`[ expression  for item in collection ]`**.

### With a condition (filter)

Add an `if` to keep only some items:

```python
nums = [1, 2, 3, 4, 5, 6]

evens = [n for n in nums if n % 2 == 0]      # [2, 4, 6]
labels = [f"id_{n}" for n in nums if n > 3]  # ['id_4', 'id_5', 'id_6']
```

Read it as: **`[ expression  for item in collection  if condition ]`**.

### A practical data example

```python
files = ["orders.csv", "readme.txt", "users.csv", "log.txt"]

csvs = [f for f in files if f.endswith(".csv")]     # ['orders.csv', 'users.csv']
cleaned = [name.strip().lower() for name in [" A ", " B "]]   # ['a', 'b']
```

---

## Dictionary comprehensions

Build a dict with `{key: value for ...}`:

```python
nums = [1, 2, 3]

squared = {n: n * n for n in nums}         # {1: 1, 2: 4, 3: 9}

# Invert a dict (swap keys and values)
codes = {"IN": "India", "US": "United States"}
names = {v: k for k, v in codes.items()}   # {'India': 'IN', 'United States': 'US'}
```

---

## Set comprehensions

Build a set (unique values) with `{expression for ...}`:

```python
words = ["a", "b", "a", "c", "b"]
unique_lengths = {len(w) for w in words}   # {1}
```

---

## Keep them readable

Comprehensions are loved for concise, simple transforms. But **don't over-nest**. If you find yourself writing two `for` clauses and two `if`s in one line, a normal loop is clearer:

```python
# Too much for one line — use a loop instead
result = [f(x) for row in data for x in row if x > 0 if f(x) is not None]
```

> **Rule of thumb:** if a stranger can't read it at a glance, expand it back into a loop.

---

## Why it matters for data engineering

Comprehensions are the idiomatic Python way to do the "for each record, transform / filter" work that fills pipelines:

- Build the **list of files** to process: `[f for f in os.listdir(path) if f.endswith(".parquet")]`.
- **Clean a batch** of values: `[v.strip().upper() for v in raw_values]`.
- **Reshape records**: `[{"id": r[0], "name": r[1]} for r in rows]`.
- Build **column lists** for Spark: `[col(c) for c in numeric_columns]`.

They're also conceptually the *single-machine* version of what a PySpark `select`/`filter` does across a cluster — same "transform each item, keep the ones that match" mental model, just distributed. Getting comfortable here makes DataFrame transformations feel familiar in module 07.

---

## Further Learning — Docs & Videos

**Documentation**
- List comprehensions: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
- Nested list comprehensions: https://docs.python.org/3/tutorial/datastructures.html#nested-list-comprehensions
- Comprehensions guide (Real Python): https://realpython.com/list-comprehension-python/

**Videos**
- Python list comprehensions explained: https://www.youtube.com/results?search_query=python+list+comprehension+explained
- Dict & set comprehensions: https://www.youtube.com/results?search_query=python+dictionary+comprehension+tutorial

Next: **[09 — Files & Exceptions](09_Files_and_Exceptions.md)**.
