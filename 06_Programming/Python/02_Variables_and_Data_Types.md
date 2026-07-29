# 02 — Variables & Data Types

## What is a variable?

A **variable** is a name that points to a value. You "assign" a value to a name with `=`, then reuse the name.

**Analogy:** A variable is a labeled box. You put a value in the box and write a label on it; later you refer to the box by its label, not by remembering the value.

```python
city = "Hyderabad"
population = 10_000_000     # underscores are allowed for readability
is_metro = True
```

- The name is on the **left**, the value on the **right**.
- `=` means "assign," **not** "equals" (equality is `==`, covered in file 06).

---

## Python is dynamically typed

You never declare a type. Python infers it from the value, and a variable can even be reassigned to a different type.

```python
x = 5        # x is an int
x = "five"   # now x is a str — perfectly legal
```

Check a value's type with `type()`:

```python
type(5)        # <class 'int'>
type(3.14)     # <class 'float'>
type("hi")     # <class 'str'>
type(True)     # <class 'bool'>
```

---

## The core built-in data types

| Type | Name | Example | Used for |
|---|---|---|---|
| `int` | Integer | `42`, `-7`, `1_000` | Whole numbers (counts, IDs) |
| `float` | Floating point | `3.14`, `-0.5`, `2.0` | Decimal numbers (money, measurements) |
| `str` | String | `"hello"`, `'a'` | Text (names, file paths, JSON) |
| `bool` | Boolean | `True`, `False` | Yes/no, flags, conditions |
| `None` | NoneType | `None` | "No value" / missing / not set |

```python
count = 100          # int
price = 19.99        # float
name = "invoice"     # str
active = False       # bool
middle_name = None   # None — deliberately empty
```

> **Note:** `True` and `False` are capitalized in Python. `None` is capitalized too. `true`/`null` (from JSON/other languages) will raise a `NameError`.

---

## Converting between types (casting)

Data arrives as text constantly (CSV files, form inputs, API responses). You convert with the type's name:

```python
int("42")       # 42   (str → int)
float("3.14")   # 3.14 (str → float)
str(42)         # "42" (int → str)
int(3.9)        # 3    (float → int, truncates — does NOT round)
bool(0)         # False; bool(1) and any non-empty value → True
```

> **Gotcha:** `int("3.9")` raises an error — you can't parse a decimal string straight to int. Do `int(float("3.9"))` → `3`.

---

## Basic arithmetic

```python
10 + 3    # 13  addition
10 - 3    # 7   subtraction
10 * 3    # 30  multiplication
10 / 3    # 3.333...  division — ALWAYS returns a float
10 // 3   # 3   floor division — drops the remainder
10 % 3    # 1   modulo — the remainder
10 ** 3   # 1000  exponent (10 to the power 3)
```

> **Gotcha:** `/` always gives a float, even `10 / 2` → `5.0`. Use `//` when you want an integer result.

---

## Why it matters for data engineering

Type handling *is* half of data cleaning. Raw source data is almost always strings — you cast `"2024-01-15"` to a date, `"19.99"` to a float, `"true"` to a bool. Mismatched types cause the most common pipeline bugs (adding a number to a string, or a column that's text when it should be numeric). Knowing `int`, `float`, `str`, `bool`, `None` and how to convert between them is the foundation of every transformation.

`None` maps directly to **NULL** in databases and **missing values** in datasets — you'll handle it constantly.

---

## Further Learning — Docs & Videos

**Documentation**
- Built-in types: https://docs.python.org/3/library/stdtypes.html
- Numbers tutorial: https://docs.python.org/3/tutorial/introduction.html#numbers
- Built-in functions (int, float, str, bool): https://docs.python.org/3/library/functions.html

**Videos**
- Python variables & data types explained: https://www.youtube.com/results?search_query=python+variables+and+data+types+explained
- Type casting in Python: https://www.youtube.com/results?search_query=python+type+casting+int+float+str

Next: **[03 — Strings](03_Strings.md)**.
