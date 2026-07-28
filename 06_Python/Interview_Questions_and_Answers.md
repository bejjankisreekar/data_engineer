# 06. Python — Interview Questions & Answers

Test yourself across the whole module. Cover the answer, commit to a response, then check. Tagged by how often each shows up: 🔥 = very common, ⭐ = common, 💡 = deeper/less frequent.

---

## Fundamentals & data types

**Q1. 🔥 Is Python compiled or interpreted? Statically or dynamically typed?**
Interpreted (run line by line, no separate compile step) and dynamically typed (you don't declare types; a variable can even be reassigned to a different type).

**Q2. 🔥 What's the difference between `==` and `=`?**
`=` assigns a value to a variable. `==` compares two values and returns `True`/`False`. Using `=` where you meant `==` is a syntax error in an `if`.

**Q3. ⭐ What does `None` represent, and how does it relate to databases?**
`None` is Python's "no value" / missing. It maps to SQL `NULL` and to missing values in datasets — you handle it constantly during cleaning.

**Q4. ⭐ What's the difference between `/`, `//`, and `%`?**
`/` is true division (always returns a float). `//` is floor division (integer result, drops remainder). `%` is modulo (the remainder). E.g. `10/3=3.33`, `10//3=3`, `10%3=1`.

**Q5. 💡 Why does `int("3.9")` fail but `int(3.9)` work?**
`int()` on a float truncates → `3`. But `int("3.9")` tries to parse a decimal *string* as an integer and raises `ValueError`. Do `int(float("3.9"))`.

---

## Strings

**Q6. 🔥 What is an f-string and why is it preferred?**
A formatted string literal prefixed with `f`, letting you embed variables/expressions in `{ }`: `f"Loaded {n} rows"`. Preferred for readability and speed over `.format()` and `%`.

**Q7. ⭐ Strings are immutable — what does that mean in practice?**
You can't change a string in place; methods like `.strip()` return a *new* string. You must reassign: `name = name.strip()`. Forgetting to reassign is a classic bug.

**Q8. ⭐ How do you convert a delimited string to a list and back?**
`"a,b,c".split(",")` → `['a','b','c']`; `",".join(['a','b','c'])` → `"a,b,c"`. This is the essence of parsing/writing CSV lines.

---

## Collections

**Q9. 🔥 List vs tuple vs set — the differences?**
List: ordered, mutable, allows duplicates `[ ]`. Tuple: ordered, **immutable**, allows duplicates `( )`. Set: **unordered, unique** values `{ }`. Choose by whether you need order, mutability, and uniqueness.

**Q10. 🔥 How do you deduplicate a list?**
`list(set(my_list))` — converting to a set drops duplicates. (Order isn't guaranteed; use `dict.fromkeys(my_list)` to dedupe while preserving order.)

**Q11. 🔥 What's a dictionary and why is it central to data work?**
A key→value mapping `{ }`. It's the in-memory form of a JSON object, so every API/JSON ingestion navigates dicts: `record["user"]["id"]`.

**Q12. ⭐ `d["key"]` vs `d.get("key")` — when to use each?**
`d["key"]` raises `KeyError` if absent (use when you're sure it exists). `d.get("key")` returns `None` (or a supplied default) if absent — safer for messy data.

**Q13. 💡 Why does `{}` create a dict, not a set? How do you make an empty set?**
`{}` is historically the empty dict. Use `set()` for an empty set.

---

## Control flow & functions

**Q14. 🔥 What are Python's "falsy" values?**
`False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything else is truthy. `if not items:` is the idiomatic "is it empty/missing?" check.

**Q15. ⭐ `for` vs `while` — when to use which?**
`for` iterates a known collection or a fixed range (can't loop forever). `while` runs until a condition becomes false — use it when the number of iterations isn't known (e.g., retry until success). Prefer `for` when possible.

**Q16. 🔥 What does a function return if there's no `return` statement?**
`None`.

**Q17. ⭐ What are `*args` and `**kwargs`?**
`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict. Used when a function accepts a variable number of inputs.

**Q18. 💡 What's the mutable-default-argument gotcha?**
`def f(items=[])` creates the list once and shares it across all calls, causing state to leak between calls. Use `def f(items=None): items = items or []`.

**Q19. ⭐ What is a lambda and when would you use one?**
A one-line anonymous function, e.g. `lambda x: x*x`. Use it for short throwaway logic passed to functions like `sort(key=...)`, `filter`, or Spark expressions. For anything longer, use a named `def`.

---

## Comprehensions

**Q20. 🔥 Rewrite this loop as a comprehension: build a list of squares of 0–4.**
`[n*n for n in range(5)]`. With a filter: `[n for n in nums if n % 2 == 0]`.

**Q21. ⭐ When should you NOT use a comprehension?**
When it becomes hard to read (multiple nested `for`/`if` clauses). Readability wins — expand it back to a loop.

---

## Files & exceptions

**Q22. 🔥 Why use `with open(...)` instead of `open(...)`?**
`with` automatically closes the file when the block ends, even if an error occurs — preventing resource leaks.

**Q23. ⭐ Difference between file modes `"w"` and `"a"`?**
`"w"` creates/overwrites (erases existing content); `"a"` appends to the end, preserving existing content.

**Q24. 🔥 How does `try/except` make a pipeline robust?**
It catches errors (bad row, missing file, flaky API) so the job can log the problem, route the bad record to a reject area, and continue — instead of crashing the whole run. Catch specific exceptions, not a bare `except:`.

**Q25. ⭐ `json.load` vs `json.loads`?**
`json.load(f)` reads from a **file** object; `json.loads(s)` parses a **string** (the `s` = string). Same for `dump`/`dumps`.

**Q26. 💡 Name three common exceptions and their causes.**
`ValueError` (right type, bad value — `int("abc")`), `KeyError` (missing dict key), `FileNotFoundError` (bad path). Also `TypeError`, `IndexError`, `ZeroDivisionError`.

---

## Modules, environments & DE application

**Q27. 🔥 What is a virtual environment and why does it matter?**
An isolated per-project Python setup so each project's package versions don't clash. It makes pipelines reproducible across laptop, CI, and production. Created with `python -m venv .venv`.

**Q28. ⭐ What is `requirements.txt` and how is it used?**
A file pinning a project's package versions. `pip freeze > requirements.txt` snapshots them; `pip install -r requirements.txt` recreates the environment elsewhere.

**Q29. ⭐ How should secrets (passwords, tokens) be handled in Python code?**
Read them from environment variables (`os.environ.get("TOKEN")`) or a secret manager — never hard-code them in the script.

**Q30. 🔥 pandas vs PySpark — when do you use each?**
pandas runs on one machine in memory (good for data that fits in RAM, quick analysis). PySpark runs distributed on a cluster (for big data and production pipelines). The DataFrame concepts are similar, so pandas is a natural stepping stone to PySpark.

**Q31. 💡 What does `if __name__ == "__main__":` do?**
Code under it runs only when the file is executed directly, not when it's imported as a module — letting a file serve both as a runnable script and an importable library.

**Q32. ⭐ Map three Python structures to their data-engineering roles.**
Lists → batches of rows/files to process. Dicts → JSON records and config. Sets → deduplication and fast membership checks.

---

## Further Learning — Docs & Videos

**Documentation**
- Official Python tutorial (all topics): https://docs.python.org/3/tutorial/index.html
- Python glossary: https://docs.python.org/3/glossary.html
- Real Python tutorials: https://realpython.com/

**Videos**
- Python interview questions & answers: https://www.youtube.com/results?search_query=python+interview+questions+and+answers
- Python for data engineering interview: https://www.youtube.com/results?search_query=python+data+engineering+interview+questions

Back to the module map: **[00 — Python Learning Path](00_Python_Learning_Path.md)**.
