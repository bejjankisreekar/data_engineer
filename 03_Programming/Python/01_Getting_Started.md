# 01 — Getting Started with Python

## What is Python?

**Python** is a general-purpose programming language known for being readable and beginner-friendly. You write instructions in plain-ish text; the Python **interpreter** reads them top to bottom and carries them out.

**Analogy:** A recipe is a list of steps a cook follows in order. A Python program is a list of steps the interpreter follows in order. You write the recipe; Python does the cooking.

Python is **interpreted** (run line by line, no separate compile step) and **dynamically typed** (you don't declare that a variable is a number or text — Python figures it out). Both make it fast to write and easy to learn.

---

## Installing and running Python

You have three common ways to run Python code:

1. **The REPL (interactive shell)** — type `python` in a terminal and you get a `>>>` prompt where each line runs immediately. Great for experimenting.
   ```
   >>> 2 + 3
   5
   >>> print("hello")
   hello
   ```
2. **A script file** — save code in a file ending in `.py` and run it:
   ```
   python my_script.py
   ```
3. **A notebook** (Jupyter / Databricks / VS Code) — cells you run one at a time, mixing code, output, and notes. This is what you'll use most as a data engineer.

> **Note:** This course assumes **Python 3** (the current version). Python 2 is retired — ignore any tutorial using `print "x"` without parentheses; that's old Python 2 syntax.

---

## Your first program

```python
print("Hello, data engineering!")
```

- `print(...)` is a **built-in function** that displays text.
- The text in quotes is a **string** (covered in file 03).

Running it outputs:
```
Hello, data engineering!
```

---

## Comments

Anything after `#` on a line is a **comment** — ignored by Python, written for humans.

```python
# This calculates the total; Python ignores this line
total = 10 + 5   # inline comments work too
```

---

## Indentation matters (this is unusual)

Most languages use braces `{ }` to group code. **Python uses indentation** (spaces at the start of a line). Blocks that belong together must be indented the same amount (4 spaces is standard).

```python
if total > 10:
    print("big")       # indented → inside the if
    print("still big") # same block
print("done")          # not indented → runs always
```

> **Gotcha:** Mixing tabs and spaces, or inconsistent indentation, causes an `IndentationError`. Pick 4 spaces and stay consistent.

---

## Why it matters for data engineering

Every pipeline you build — an ingestion script, a transformation job, an Airflow DAG, a PySpark notebook — is Python code run by an interpreter. Understanding *how code runs* (top to bottom, indentation-defined blocks, scripts vs notebooks) is the base layer under everything else in this module.

---

## Further Learning — Docs & Videos

**Documentation**
- Python setup and usage: https://docs.python.org/3/using/index.html
- The Python tutorial — an informal intro: https://docs.python.org/3/tutorial/introduction.html
- Downloading Python: https://www.python.org/downloads/

**Videos**
- Install Python & run your first program: https://www.youtube.com/results?search_query=install+python+and+run+first+program
- Python REPL and scripts explained: https://www.youtube.com/results?search_query=python+repl+vs+script+explained

Next: **[02 — Variables & Data Types](02_Variables_and_Data_Types.md)**.
