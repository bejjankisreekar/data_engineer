# Python (for Data Engineers) — Interview Questions & Answers

## Overview
Python interviews for DE focus on data-handling fluency: data types, comprehensions, functions, file/JSON handling, error handling, pandas basics, and clean pipeline code. See the repo's `03_Programming/Python` module for depth.

Difficulty: 🟢 Easy · 🟡 Medium · 🔴 Hard · Confidence: ★.

---

## Interview Questions & Answers

### 🟢 Q1. List vs tuple vs set vs dict? ★★★★★
**List** = ordered, mutable, allows duplicates `[ ]`. **Tuple** = ordered, immutable `( )`. **Set** = unordered, unique values `{ }`. **Dict** = key→value pairs `{k:v}` (JSON-like). Choose by order/mutability/uniqueness needs.

### 🟡 Q2. Mutable vs immutable types? ★★★★☆
**Immutable** (can't change in place): int, float, str, tuple, frozenset, bool. **Mutable**: list, dict, set. Immutability matters for dict keys (must be immutable) and for avoiding accidental shared-state bugs.

### 🟢 Q3. List comprehension example? ★★★★★
`[n*n for n in range(5)]` → squares; with filter `[n for n in nums if n%2==0]`. Concise "transform each item, optionally filter" — the Pythonic replacement for a build-a-list loop.

### 🟡 Q4. *args vs **kwargs? ★★★☆☆
`*args` collects extra **positional** args into a tuple; `**kwargs` collects extra **keyword** args into a dict. Used when a function takes a variable number of inputs.

### 🟢 Q5. How do you read/parse JSON? ★★★★☆
`json.load(f)` from a file, `json.loads(s)` from a string → returns dicts/lists. `json.dump`/`json.dumps` to serialize back. Remember: the `s` variants work on **strings**.

### 🟡 Q6. try/except/finally — error handling? ★★★★☆
`try` runs risky code; `except <Error>` catches specific failures; `else` runs if no error; `finally` always runs (cleanup). Catch **specific** exceptions, not a bare `except:` that hides bugs. Core to robust pipelines.

### 🟡 Q7. Shallow vs deep copy? ★★★☆☆
`copy.copy()` = shallow (nested objects still shared references); `copy.deepcopy()` = fully independent clone. Matters when mutating nested structures — a shallow copy can change the original.

### 🔴 Q8. Generators vs lists (yield)? ★★★☆☆
A generator (`yield`) produces items **lazily**, one at a time, holding only the current item in memory — ideal for streaming large files/datasets. A list materializes everything at once (memory-heavy). Generators are single-pass.

### 🔴 Q9. Decorators — what/why? ★★☆☆☆
A decorator wraps a function to add behavior (logging, timing, retry, auth) without changing its code, using `@decorator` syntax. Common in frameworks (Flask routes, Airflow tasks, PySpark `@udf`).

### 🟡 Q10. pandas: read csv, filter, groupby? ★★★★☆
`df = pd.read_csv("f.csv")`; filter `df[df.amount>100]`; aggregate `df.groupby("city")["amount"].sum()`. pandas DataFrame ≈ an in-memory SQL table; mirrors SQL SELECT/WHERE/GROUP BY.

### 🟡 Q11. pandas vs PySpark — when? ★★★★☆
**pandas** = single machine, in-memory (data fits in RAM, quick analysis/prototypes). **PySpark** = distributed across a cluster (big data, production pipelines). DataFrame concepts transfer, so pandas is a stepping stone.

### 🟡 Q12. How do you handle secrets/config? ★★★★☆
Read from **environment variables** (`os.environ.get`) or a secret manager / Key Vault — never hard-code. Keep config in files/env, not in source. In Databricks use secret scopes.

### 🟢 Q13. Deduplicate a list? ★★★★☆
`list(set(items))` (order not preserved) or `list(dict.fromkeys(items))` (preserves order). Sets give O(1) membership and instant dedup.

### 🟢 Q14. Count word/element frequency? ★★★★☆
`from collections import Counter; Counter(text.split())` → a dict of counts, with `.most_common(n)`. The idiomatic way to count.

### 🔴 Q15. Why avoid mutable default arguments? ★★☆☆☆
`def f(x=[])` creates the list **once** and shares it across all calls, so state leaks between calls (a classic bug). Use `def f(x=None): x = x or []`.

### 🟡 Q16. `is` vs `==`? ★★★☆☆
`==` compares **values**; `is` compares **identity** (same object in memory). Use `is` only for `None`/singletons (`if x is None`), `==` for value equality.

### 🟡 Q17. What is a context manager (`with`)? ★★★☆☆
An object that sets up and tears down a resource automatically (`__enter__`/`__exit__`). `with open(...) as f:` guarantees the file closes even on error — used for files, DB connections, locks.

### 🟡 Q18. enumerate / zip? ★★★☆☆
`enumerate(items)` yields `(index, value)` pairs; `zip(a, b)` pairs elements of two iterables. Cleaner than manual index tracking.

### 🔴 Q19. List vs generator comprehension? ★★☆☆☆
`[x for x in it]` builds a full list in memory; `(x for x in it)` is a lazy **generator** — same syntax, parentheses, memory-efficient for large/streamed data.

### 🟡 Q20. How do you make code reusable/testable? ★★★★☆
Wrap logic in **functions** with clear inputs/outputs, avoid global state, add error handling + logging, structure into modules, pin deps in `requirements.txt`, and write `pytest` unit tests.

---

## Scenario Questions
**🔴 S1. "Process a 50 GB file on a laptop." ★★★★☆** → stream with a **generator** / chunked pandas (`chunksize=...`), never `f.read()` all; or move to Spark.
**🟡 S2. "Clean a messy CSV before loading." ★★★★☆** → pandas: `str.strip().str.lower()`, `dropna`, dtype cast, `drop_duplicates`, `to_parquet`.
**🟡 S3. "Reusable parameterized pipeline step." ★★★☆☆** → a `def run(table, date)` with try/except + logging + return status.
**🔴 S4. "Call an API and handle failures." ★★★☆☆** → `requests` with timeout + retry/backoff, `try/except`, log errors, idempotent write.

---

## Code Examples
```python
from collections import Counter
list(dict.fromkeys(items))            # dedupe, keep order
Counter(text.lower().split())         # word frequency
def read_lines(path):                 # memory-safe streaming
    with open(path) as f:
        for line in f: yield line.strip()
import os; token = os.environ.get("TOKEN")   # secret from env
[{"id": r["id"], "sku": i["sku"]} for r in data for i in r["items"]]  # flatten JSON
```

---

## Quick Revision
- ✔ list/tuple/set/dict; mutable vs immutable
- ✔ Comprehensions (list/dict/set) + generator `(...)` for laziness
- ✔ Generators (`yield`) = memory-efficient streaming
- ✔ pandas small data, PySpark big data
- ✔ Secrets from **env vars / Key Vault**, never hard-coded
- ✔ Dedupe: `dict.fromkeys`; count: `Counter`; `is` only for None
- ✔ `with` = auto resource cleanup; avoid mutable defaults

## Common Interview Mistakes
- Mutable default arguments.
- Loading huge files fully into memory.
- Hard-coding credentials.
- `is` vs `==` confusion.
- Loops where vectorized/Spark ops fit.

## Senior-Level Discussion
Seniors write clean, testable, parameterized pipeline code with logging and error handling, prefer vectorized/Spark ops over Python loops, stream large data with generators, manage deps via venv/requirements, and know when Python glue vs Spark compute is right.

## Follow-up Questions
- "Why generators for ETL?" → constant memory over huge inputs.
- "How do you unit-test a transform?" → pure functions + `pytest`/`chispa` on small samples.

## Related Topics
PySpark, Coding Questions, Azure Functions, Data Validation
