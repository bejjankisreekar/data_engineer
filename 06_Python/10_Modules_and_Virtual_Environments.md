# 10 — Modules, Packages & Virtual Environments

This file covers how Python code is **organized and reused** (modules/packages), how you install other people's code (`pip`), and how you keep each project's dependencies isolated (virtual environments) — the everyday plumbing of real projects.

---

## Modules — reusing code with `import`

A **module** is just a `.py` file. Importing it makes its functions and variables available in yours.

```python
import math
math.sqrt(16)          # 4.0
math.pi                # 3.14159...

# Import specific names
from datetime import datetime
datetime.now()

# Import with an alias (very common in data work)
import pandas as pd
import pyspark.sql.functions as F
```

### The standard library

Python ships with a large **standard library** — no installation needed. The ones a data engineer touches most:

| Module | Use |
|---|---|
| `os` / `pathlib` | File paths, directories, environment variables |
| `datetime` | Dates and times |
| `json` / `csv` | Parse and write JSON/CSV |
| `re` | Regular expressions (pattern matching in text) |
| `logging` | Structured logs (better than `print` in production) |
| `sys` | Interpreter/runtime info, command-line args |

```python
import os
path = os.path.join("data", "raw", "orders.csv")   # OS-correct path joining
token = os.environ.get("API_TOKEN")                 # read an env var (for secrets)
```

> **Tip:** Read secrets (passwords, tokens) from **environment variables** with `os.environ`, never hard-code them in the script.

---

## Your own modules

Split code across files and import between them:

```
project/
├── main.py
└── helpers.py
```

```python
# helpers.py
def clean(name):
    return name.strip().lower()

# main.py
from helpers import clean
clean("  Ada  ")     # "ada"
```

### The `if __name__ == "__main__":` guard

Code under this guard runs only when the file is executed **directly**, not when it's imported. It keeps a file usable both as a script and as an importable module.

```python
def main():
    print("running the pipeline")

if __name__ == "__main__":
    main()
```

---

## Installing third-party packages with `pip`

**pip** is Python's package installer. It fetches packages from **PyPI** (the Python Package Index).

```
pip install pandas
pip install pyspark
pip install requests
pip list                 # show installed packages
pip freeze > requirements.txt   # snapshot exact versions for reproducibility
pip install -r requirements.txt # install everything a project needs
```

A `requirements.txt` file pins the packages/versions your project depends on — commit it so teammates and production get the same environment.

---

## Virtual environments — isolate each project

Different projects need different package versions. A **virtual environment** is an isolated Python setup per project, so installing pandas 2.0 for project A doesn't break project B that needs pandas 1.5.

```
python -m venv .venv          # create an environment in a .venv folder

# Activate it:
#   Windows:  .venv\Scripts\activate
#   Mac/Linux: source .venv/bin/activate

pip install pandas            # now installs INTO this env only
deactivate                    # leave the environment
```

**Analogy:** A virtual environment is a separate toolbox per project. Without it, every project shares one global toolbox and their tools clash. With it, each project carries exactly the tools (and versions) it needs.

> **Gotcha:** Always activate the venv *before* `pip install`. Installing into the global Python is the classic cause of "it works on my machine but nowhere else." Also add `.venv/` to `.gitignore` — you commit `requirements.txt`, not the installed packages.

---

## Why it matters for data engineering

- **Imports** are how you use the entire data ecosystem: `pandas`, `pyspark`, cloud SDKs (`azure-storage-blob`, `boto3`), `requests` for APIs, `airflow` for orchestration.
- **The standard library** (`os`, `datetime`, `json`, `logging`) handles paths, timestamps, config, and logging in every pipeline.
- **`requirements.txt` + virtual environments** make pipelines **reproducible** — the same code + same pinned dependencies runs identically on your laptop, in CI, and in production. This reproducibility is a core data-engineering discipline (and it ties into the CI/CD material in module 09, Git & GitHub).
- Databricks and Spark clusters manage libraries the same way conceptually — you declare dependencies so every executor has them.

---

## Further Learning — Docs & Videos

**Documentation**
- Modules: https://docs.python.org/3/tutorial/modules.html
- The Python standard library: https://docs.python.org/3/library/index.html
- Installing packages (pip): https://packaging.python.org/en/latest/tutorials/installing-packages/
- venv — virtual environments: https://docs.python.org/3/library/venv.html

**Videos**
- Python modules and imports: https://www.youtube.com/results?search_query=python+modules+and+imports+explained
- pip and virtual environments (venv): https://www.youtube.com/results?search_query=python+venv+pip+virtual+environment+tutorial

Next: **[11 — Python for Data Engineering](11_Python_for_Data_Engineering.md)**.
