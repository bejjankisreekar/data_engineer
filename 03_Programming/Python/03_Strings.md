# 03 — Strings

## What is a string?

A **string** (`str`) is text — a sequence of characters. You write it in single or double quotes (they're equivalent).

```python
a = "hello"
b = 'world'
path = "/data/raw/orders.csv"
```

For multi-line text, use triple quotes:

```python
sql = """
SELECT * FROM orders
WHERE amount > 100
"""
```

---

## Strings are sequences — indexing and slicing

Each character has a position (**index**) starting at **0**. Negative indexes count from the end.

```python
s = "python"
s[0]     # 'p'   first character
s[-1]    # 'n'   last character
s[1:4]   # 'yth' slice: from index 1 up to (not including) 4
s[:3]    # 'pyt' from start to index 3
s[3:]    # 'hon' from index 3 to end
len(s)   # 6     length
```

> **Gotcha:** Indexing starts at 0, and a slice `[start:end]` **excludes** `end`. `s[1:4]` gives characters 1, 2, 3 — not 4.

---

## Common string methods

Methods are functions attached to a value; call them with a dot. Strings are **immutable**, so methods return a *new* string rather than changing the original.

```python
name = "  Data Engineer  "

name.strip()          # "Data Engineer"  — remove surrounding whitespace
name.lower()          # "  data engineer  "
name.upper()          # "  DATA ENGINEER  "
name.replace("Data", "Cloud")   # "  Cloud Engineer  "
"a,b,c".split(",")    # ['a', 'b', 'c'] — string → list
"-".join(["2024","01","15"])    # "2024-01-15" — list → string
"orders.csv".endswith(".csv")   # True
"orders.csv".startswith("ord")  # True
"HELLO".isupper()               # True
"file.txt".find("txt")          # 5  (index where it starts, -1 if absent)
```

> **Gotcha:** Because strings are immutable, `name.strip()` does **not** change `name` — you must reassign: `name = name.strip()`.

---

## f-strings — the modern way to build text

An **f-string** (formatted string) lets you drop variables and expressions directly inside `{ }`. Prefix the string with `f`.

```python
table = "orders"
rows = 1500
msg = f"Loaded {rows} rows into {table}"
# "Loaded 1500 rows into orders"

price = 19.999
f"Total: ${price:.2f}"     # "Total: $20.00"  — :.2f formats to 2 decimals
f"{rows:,}"                # "1,500"  — thousands separator
```

f-strings are the preferred formatting style — readable and fast. (Older code uses `.format()` or `%` formatting; you'll see them but shouldn't need to write them.)

---

## Escape characters

Some characters need a backslash:

```python
"line1\nline2"   # \n = newline
"col1\tcol2"     # \t = tab
"He said \"hi\"" # \" = literal quote
r"C:\data\raw"   # r-prefix = raw string, backslashes stay literal (great for Windows paths)
```

> **Tip:** Use **raw strings** (`r"..."`) for Windows file paths and regular expressions so `\` isn't misread as an escape.

---

## Why it matters for data engineering

Strings are everywhere in pipelines: file paths, table names, column names, JSON payloads, SQL built dynamically, log messages, and any text column in your data. `split`/`join` convert between delimited text and lists (the heart of parsing CSV lines). `strip`/`lower`/`replace` are your daily data-cleaning verbs. f-strings build the log lines and dynamic queries you'll write constantly.

---

## Further Learning — Docs & Videos

**Documentation**
- Text sequence type (str) — all methods: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
- f-strings (formatted string literals): https://docs.python.org/3/reference/lexical_analysis.html#f-strings
- String formatting guide (Real Python): https://realpython.com/python-f-strings/

**Videos**
- Python strings & methods explained: https://www.youtube.com/results?search_query=python+strings+methods+explained
- Python f-strings tutorial: https://www.youtube.com/results?search_query=python+f+strings+tutorial

Next: **[04 — Lists, Tuples & Sets](04_Lists_Tuples_Sets.md)**.
