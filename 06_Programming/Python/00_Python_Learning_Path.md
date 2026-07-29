# 06. Python — Learning Path

Python is the primary programming language of data engineering. SQL (module 01) lets you *query* data; Python lets you *move, transform, automate, and orchestrate* it — and it's the language you'll write PySpark in (module 07). This module takes you from "never written code" to "comfortable enough to read and write the Python a data engineer uses every day."

**No coding background required.** Every file explains new terms the first time they appear and leads with a plain-language idea before the code.

---

## Why Python for data engineering?

- **It's the lingua franca of data.** PySpark, pandas, Airflow, dbt's Python models, most cloud SDKs (Azure, AWS, GCP), and nearly every data tool have a Python API.
- **It's readable.** Python reads almost like English, which matters when pipelines are maintained by teams.
- **It glues everything together.** A data engineer's job is often "get data from A, reshape it, land it in B, on a schedule, reliably" — Python is the glue for exactly that.
- **It's the on-ramp to PySpark.** The DataFrame code you'll write in module 07 *is* Python. Learn the language here so Spark is about *distributed data*, not about *syntax*.

---

## Reading order

| # | File | What you'll learn |
|---|---|---|
| 00 | [Python Learning Path](00_Python_Learning_Path.md) | This map |
| 01 | [Getting Started](01_Getting_Started.md) | What Python is, installing it, running code, the REPL |
| 02 | [Variables & Data Types](02_Variables_and_Data_Types.md) | Storing values; int, float, str, bool, None; dynamic typing |
| 03 | [Strings](03_Strings.md) | Text: slicing, methods, f-strings, formatting |
| 04 | [Lists, Tuples & Sets](04_Lists_Tuples_Sets.md) | The three ordered/unordered collections |
| 05 | [Dictionaries](05_Dictionaries.md) | Key-value data — the workhorse structure |
| 06 | [Conditionals & Loops](06_Conditionals_and_Loops.md) | Decisions and repetition |
| 07 | [Functions](07_Functions.md) | Reusable blocks; arguments, return, scope, lambda |
| 08 | [Comprehensions](08_Comprehensions.md) | Concise list/dict/set building |
| 09 | [Files & Exceptions](09_Files_and_Exceptions.md) | Reading/writing files; handling errors |
| 10 | [Modules & Virtual Environments](10_Modules_and_Virtual_Environments.md) | import, pip, venv, project layout |
| 11 | [Python for Data Engineering](11_Python_for_Data_Engineering.md) | pandas intro and the bridge to PySpark |
| — | [Interview Questions & Answers](Interview_Questions_and_Answers.md) | Test yourself across the module |

**Suggested pace:** one file per day. Type every example yourself — reading code is not the same as writing it. By file 11 you'll have exactly the Python foundation module 07 (PySpark) assumes.

---

## How each note is structured

1. **What is it?** — plain-language definition, usually with a real-world comparison.
2. **Examples** — small, concrete, runnable snippets.
3. **Why it matters for data engineering** — where the concept shows up in real pipelines.
4. **Gotchas** — the mistakes beginners actually make.
5. **Further Learning — Docs & Videos** — official docs and video links to go deeper.

---

## Further Learning — Docs & Videos

**Documentation**
- Official Python tutorial: https://docs.python.org/3/tutorial/index.html
- Python for beginners (python.org): https://www.python.org/about/gettingstarted/
- Real Python (high-quality tutorials): https://realpython.com/

**Videos**
- Python full course for beginners: https://www.youtube.com/results?search_query=python+full+course+for+beginners+freecodecamp
- Python for data engineering: https://www.youtube.com/results?search_query=python+for+data+engineering+tutorial

Start here: **[01 — Getting Started](01_Getting_Started.md)**.
