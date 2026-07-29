# 06 — Conditionals & Loops

This file is about **control flow** — making decisions (conditionals) and repeating work (loops). Together they turn a straight list of statements into logic.

---

## Comparisons and booleans

Conditions evaluate to `True` or `False`.

```python
5 == 5      # True   equal to (note: two equals signs)
5 != 3      # True   not equal
5 > 3       # True   greater than
5 <= 5      # True   less than or equal
"a" == "A"  # False  strings are case-sensitive
```

Combine conditions with `and`, `or`, `not`:

```python
age = 25
age > 18 and age < 65     # True — both must hold
age < 13 or age > 60      # False — either can hold
not (age > 18)            # False
```

> **Gotcha:** `=` assigns; `==` compares. `if x = 5:` is a syntax error — you want `if x == 5:`.

---

## if / elif / else

```python
amount = 150

if amount > 1000:
    tier = "gold"
elif amount > 100:          # checked only if the first was False
    tier = "silver"
else:
    tier = "bronze"

print(tier)                 # "silver"
```

- The colon `:` and the **indentation** define each block (see file 01).
- `elif` = "else if"; you can have as many as you like. `else` is optional.

### Truthiness

Python treats many values as `True`/`False` in a condition without an explicit comparison:

```python
items = []
if items:               # empty list is "falsy" → this block is skipped
    print("has items")

name = ""
if not name:            # empty string is falsy → runs
    print("name is missing")
```

Falsy values: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything else is truthy. This is the idiomatic way to check "is this empty/missing?"

---

## for loops — repeat over a collection

A **for loop** runs a block once per item in a collection.

```python
files = ["a.csv", "b.csv", "c.csv"]

for f in files:
    print(f"Processing {f}")
```

### `range()` — loop a fixed number of times

```python
for i in range(3):        # 0, 1, 2  (stops before 3)
    print(i)

for i in range(1, 6):     # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8  (step of 2)
    print(i)
```

### `enumerate()` and looping a dict

```python
for index, f in enumerate(files):     # get position AND value
    print(index, f)                   # 0 a.csv / 1 b.csv / 2 c.csv

for key, value in {"a": 1, "b": 2}.items():
    print(key, value)
```

---

## while loops — repeat until a condition is false

```python
attempts = 0
while attempts < 3:
    print(f"Attempt {attempts}")
    attempts += 1          # MUST change the condition, or it loops forever
```

Use `while` when you don't know the number of iterations up front (e.g., "retry until it succeeds").

> **Gotcha:** Forgetting to update the condition (`attempts += 1`) creates an **infinite loop**. `for` loops can't do this because they iterate a finite collection — prefer `for` when you can.

---

## break and continue

```python
for n in range(10):
    if n == 5:
        break        # exit the loop entirely
    if n % 2 == 0:
        continue     # skip to the next iteration
    print(n)         # prints 1, 3
```

---

## Why it matters for data engineering

Control flow is the logic of every pipeline:

- **Loops** process batches: "for each file in the landing folder, load it"; "for each table in the config, run the extract."
- **Conditionals** implement business rules and data quality: "if the row is missing an id, send it to the reject table"; "if the file is empty, skip it."
- **Truthiness** is how you check for missing/empty data cleanly.
- **`break`/`continue`** handle early exits and skipping bad records.

In PySpark you'll often replace explicit row-by-row loops with DataFrame operations (which are faster and distributed), but you'll still use Python loops to orchestrate *tables, files, dates, and partitions* — the higher-level units of work.

---

## Further Learning — Docs & Videos

**Documentation**
- if statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements
- for statements & range: https://docs.python.org/3/tutorial/controlflow.html#for-statements
- Truth value testing: https://docs.python.org/3/library/stdtypes.html#truth-value-testing

**Videos**
- Python if/elif/else explained: https://www.youtube.com/results?search_query=python+if+elif+else+explained
- Python for and while loops: https://www.youtube.com/results?search_query=python+for+loop+while+loop+tutorial

Next: **[07 — Functions](07_Functions.md)**.
