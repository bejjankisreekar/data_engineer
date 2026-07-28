# 09 — Files & Exceptions

Two essential, practical skills: reading/writing files, and handling errors gracefully so a pipeline doesn't crash on the first bad record.

---

## Part A — Reading and writing files

### The `with open(...)` pattern

Always open files using `with`. It guarantees the file is **closed** automatically, even if an error happens midway.

```python
# Write text to a file
with open("output.txt", "w") as f:
    f.write("line 1\n")
    f.write("line 2\n")

# Read the whole file
with open("output.txt", "r") as f:
    content = f.read()

# Read line by line (memory-friendly for big files)
with open("output.txt", "r") as f:
    for line in f:
        print(line.strip())
```

### File modes

| Mode | Meaning |
|---|---|
| `"r"` | Read (default); errors if the file doesn't exist |
| `"w"` | Write; **creates or overwrites** (truncates existing content) |
| `"a"` | Append; adds to the end, keeps existing content |
| `"r+"` | Read and write |

> **Gotcha:** `"w"` **erases** the file's existing contents on open. Use `"a"` to add without destroying what's there.

### Reading CSV and JSON with the standard library

```python
import csv
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)          # each row becomes a dict keyed by header
    for row in reader:
        print(row["name"], row["amount"])

import json
with open("config.json") as f:
    config = json.load(f)               # JSON file → Python dict
value = config["source_path"]

json_str = json.dumps({"a": 1})         # Python dict → JSON string
data = json.loads('{"a": 1}')           # JSON string → Python dict
```

> **Tip:** `json.load`/`dump` work with **files**; `json.loads`/`dumps` (with the `s`) work with **strings**. Remember: `s` = string.

---

## Part B — Exceptions (error handling)

An **exception** is an error that interrupts normal execution. Unhandled, it crashes the program. `try`/`except` lets you catch it and respond.

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    result = None
    print("Cannot divide by zero — set result to None")
```

### try / except / else / finally

```python
try:
    f = open("data.csv")           # code that might fail
    data = f.read()
except FileNotFoundError:
    print("File is missing")       # runs only if that error occurred
except Exception as e:
    print(f"Some other error: {e}") # catch-all; e holds the error details
else:
    print("Succeeded")             # runs only if NO exception
finally:
    print("Always runs (cleanup)") # runs no matter what
```

### Common built-in exceptions

| Exception | Typical cause |
|---|---|
| `ValueError` | `int("abc")` — right type, wrong value |
| `TypeError` | `"a" + 5` — wrong type |
| `KeyError` | `d["missing"]` — key not in dict |
| `IndexError` | `lst[99]` — index out of range |
| `FileNotFoundError` | Opening a path that doesn't exist |
| `ZeroDivisionError` | Dividing by zero |

### Raising your own errors

```python
def load(path):
    if not path.endswith(".csv"):
        raise ValueError(f"Expected a .csv file, got: {path}")
```

> **Gotcha:** Avoid a bare `except:` that swallows *everything* silently — it hides real bugs. Catch the **specific** exceptions you expect, and log the rest.

---

## Why it matters for data engineering

This file is where "toy scripts" become "production pipelines":

- **File I/O** is the literal job — read source files, write outputs, load configs. `csv` and `json` handling here is what you do before (and alongside) heavier tools like pandas and Spark.
- **Exception handling** is what makes a pipeline **robust**. Real data is dirty: a malformed row, a missing file, a flaky API. Good pipelines catch these, route bad records to a reject/quarantine area, log the problem, and keep going — instead of crashing the whole nightly job on record #4,000,001.
- `try/except` around network/IO calls, plus **retries**, is the backbone of reliable ingestion. `finally` guarantees cleanup (closing connections, releasing locks).

---

## Further Learning — Docs & Videos

**Documentation**
- Reading and writing files: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
- Errors and exceptions: https://docs.python.org/3/tutorial/errors.html
- csv module: https://docs.python.org/3/library/csv.html
- json module: https://docs.python.org/3/library/json.html

**Videos**
- Python file handling (open, read, write): https://www.youtube.com/results?search_query=python+file+handling+open+read+write
- Python try except error handling: https://www.youtube.com/results?search_query=python+try+except+error+handling+tutorial

Next: **[10 — Modules & Virtual Environments](10_Modules_and_Virtual_Environments.md)**.
