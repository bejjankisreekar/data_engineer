# 07 — Functions

## What is a function?

A **function** is a named, reusable block of code. You define it once, then **call** it as many times as you like — optionally passing in values and getting a result back.

**Analogy:** A coffee machine is a function. You put in inputs (water, beans — the *arguments*), press start (the *call*), and get output (coffee — the *return value*). You don't rebuild the machine each morning; you reuse it.

```python
def greet(name):
    return f"Hello, {name}!"

greet("Ada")      # "Hello, Ada!"
greet("Sam")      # "Hello, Sam!"
```

- `def` starts the definition; `name` is a **parameter**.
- `return` sends a value back to the caller. Without `return`, a function returns `None`.

---

## Arguments and return values

```python
def add(a, b):
    return a + b

total = add(3, 5)      # total = 8
```

### Default arguments

Give a parameter a default so callers can omit it:

```python
def load(path, mode="append"):
    return f"Loading {path} in {mode} mode"

load("orders.csv")                 # "...in append mode"
load("orders.csv", "overwrite")    # "...in overwrite mode"
```

### Keyword arguments

Pass by name for clarity (order then doesn't matter):

```python
load(mode="overwrite", path="orders.csv")
```

### Returning multiple values

A function can return several values as a tuple; unpack them on the way out:

```python
def summarize(numbers):
    return len(numbers), sum(numbers)   # returns a tuple

count, total = summarize([10, 20, 30])  # count=3, total=60
```

---

## `*args` and `**kwargs` — flexible arguments

Sometimes you don't know how many arguments will be passed.

```python
def total(*args):            # *args collects extra positional args into a tuple
    return sum(args)

total(1, 2, 3, 4)            # 10

def configure(**kwargs):     # **kwargs collects named args into a dict
    return kwargs

configure(env="prod", retries=3)   # {'env': 'prod', 'retries': 3}
```

You'll see `*args, **kwargs` constantly in library code and decorators. For your own code, use them when a function genuinely needs a variable number of inputs.

---

## Scope — where variables live

Variables created **inside** a function are **local** — they don't exist outside it.

```python
def f():
    x = 10      # local to f
    return x

f()
# print(x)      # ERROR — x is not defined out here
```

A function *can read* variables defined outside (global), but assigning inside creates a new local one. Keep functions self-contained: take inputs as parameters, return outputs — avoid reaching for outside variables.

> **Gotcha (mutable default):** Never use a mutable default like `def f(items=[])`. That list is created once and shared across all calls, causing surprising bugs. Use `def f(items=None): items = items or []` instead.

---

## Lambda — tiny anonymous functions

A **lambda** is a one-line function without a name, handy for short operations passed to other functions:

```python
square = lambda x: x * x
square(5)                       # 25

# Common use: a sort key
people = [("Ada", 36), ("Sam", 29)]
people.sort(key=lambda p: p[1]) # sort by the second element (age)
```

Use lambdas for short, throwaway logic. For anything longer or reused, write a named `def`.

---

## Why it matters for data engineering

Functions are how you keep pipelines **DRY** (Don't Repeat Yourself), testable, and readable:

- Wrap each pipeline step in a function: `extract()`, `transform(df)`, `load(df, target)`.
- Parameterize with arguments so one function runs for many tables/dates/environments (`run(table, date)`).
- Return status so orchestration can react (`return rows_loaded, errors`).
- **PySpark UDFs** (module 07, file 10) are literally Python functions you register with Spark — everything here applies directly.
- Lambdas appear in `sort`, `filter`, `map`, and PySpark column expressions.

Well-factored functions are the difference between a 500-line unmaintainable script and a clean, testable pipeline.

---

## Further Learning — Docs & Videos

**Documentation**
- Defining functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- More on function arguments: https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions
- Lambda expressions: https://docs.python.org/3/reference/expressions.html#lambda

**Videos**
- Python functions explained: https://www.youtube.com/results?search_query=python+functions+explained+args+kwargs
- Python lambda functions: https://www.youtube.com/results?search_query=python+lambda+functions+tutorial

Next: **[08 — Comprehensions](08_Comprehensions.md)**.
