# 04 — Lists, Tuples & Sets

These three types hold **collections** of values. Choosing the right one signals intent and prevents bugs.

| Type | Ordered? | Changeable (mutable)? | Duplicates? | Syntax |
|---|---|---|---|---|
| **List** | Yes | Yes | Yes | `[1, 2, 3]` |
| **Tuple** | Yes | **No** | Yes | `(1, 2, 3)` |
| **Set** | No | Yes | **No** | `{1, 2, 3}` |

---

## Lists — the everyday collection

A **list** is an ordered, changeable sequence. It's the container you'll reach for most.

```python
files = ["a.csv", "b.csv", "c.csv"]

files[0]              # "a.csv"   indexing (starts at 0)
files[-1]             # "c.csv"   last item
files[0:2]            # ["a.csv", "b.csv"]  slicing (like strings)
len(files)            # 3

files.append("d.csv")     # add to the end
files.insert(0, "z.csv")  # add at a position
files.remove("b.csv")     # remove by value
popped = files.pop()      # remove & return the last item
files.sort()              # sort in place
"a.csv" in files          # True — membership test
```

Lists can hold mixed types and nest:

```python
row = ["Ada", 36, True]
matrix = [[1, 2], [3, 4]]
matrix[1][0]     # 3
```

> **Gotcha:** `files.sort()` changes the list and returns `None`. Don't write `files = files.sort()` — that sets `files` to `None`. Either call `files.sort()` alone, or use `sorted(files)` which returns a new sorted list.

---

## Tuples — fixed, unchangeable sequences

A **tuple** is like a list but **immutable** — once created, you can't add, remove, or change items. Use it for data that shouldn't change: coordinates, a fixed record, function returns.

```python
point = (12.9, 77.5)      # latitude, longitude
point[0]                  # 12.9
# point[0] = 5            # ERROR — tuples can't be modified

# Unpacking — a very common Python idiom
lat, lon = point
```

Why bother when lists exist? Tuples are slightly faster, signal "this is fixed," and (unlike lists) can be used as dictionary keys or set members.

---

## Sets — unique, unordered values

A **set** holds only **unique** items and has no order. Perfect for deduplication and membership checks.

```python
ids = {1, 2, 2, 3, 3, 3}
ids                     # {1, 2, 3} — duplicates dropped automatically

ids.add(4)
ids.discard(1)
3 in ids                # True — very fast membership test

# Deduplicate a list instantly:
unique = list(set([1, 1, 2, 3, 3]))   # [1, 2, 3]
```

Sets support math-style operations:

```python
a = {1, 2, 3}
b = {2, 3, 4}
a & b     # {2, 3}     intersection (in both)
a | b     # {1,2,3,4}  union (in either)
a - b     # {1}        difference (in a, not b)
```

> **Gotcha:** `{}` creates an empty **dictionary**, not a set. For an empty set use `set()`.

---

## Why it matters for data engineering

- **Lists** model rows, batches of files, columns to process, records read from a source. Iterating a list is the core loop of most scripts.
- **Tuples** represent fixed records and are what many functions return (e.g., `(rows_loaded, errors)`). Unpacking makes that clean.
- **Sets** are the fast, idiomatic way to **deduplicate** and to check "have I already seen this key?" — both extremely common in ingestion and CDC logic.

These same ideas reappear in PySpark: a DataFrame is (conceptually) a collection of rows, and `dropDuplicates()` is the distributed cousin of `set()`.

---

## Further Learning — Docs & Videos

**Documentation**
- Lists tutorial: https://docs.python.org/3/tutorial/introduction.html#lists
- Data structures (lists, tuples, sets): https://docs.python.org/3/tutorial/datastructures.html
- Set types: https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset

**Videos**
- Python lists, tuples, sets explained: https://www.youtube.com/results?search_query=python+lists+tuples+sets+explained
- When to use list vs tuple vs set: https://www.youtube.com/results?search_query=python+list+vs+tuple+vs+set

Next: **[05 — Dictionaries](05_Dictionaries.md)**.
