# Apache Airflow

## What is Airflow?

Apache Airflow is the **open-source, code-first orchestrator** that became the industry standard for scheduling data workflows. You define pipelines as **Python code** (DAGs), and Airflow schedules them, runs the tasks in dependency order, retries failures, and gives you a rich UI to monitor everything.

Analogy: where [ADF](02_ADF_Orchestration.md) is a low-code control tower you configure with a GUI, Airflow is a **programmable control tower** — you *write* the flight plan in Python, so you get the full power (and responsibility) of code: version control, testing, loops, dynamic generation, any Python library.

Even in Azure shops, Airflow appears constantly (via **Azure Managed Airflow** in ADF, **Astronomer**, or self-hosted) and is a heavy résumé/interview keyword — worth knowing even if your day job is ADF/Databricks.

---

## The core concepts

| Concept | What it is |
|---|---|
| **DAG** | The pipeline — a Python file defining tasks and their dependencies |
| **Task** | One unit of work (an operator instance) |
| **Operator** | A template for a task: `PythonOperator`, `BashOperator`, `DatabricksSubmitRunOperator`, `SparkSubmitOperator`, etc. |
| **Sensor** | A special operator that **waits** for a condition (file exists, partition ready) |
| **Scheduler** | The process that decides what runs when |
| **Executor** | How/where tasks run (Local, Celery, Kubernetes) |
| **XCom** | Small data passed *between* tasks ("cross-communication") |
| **Hook** | A reusable connection to an external system (DBs, cloud) |

---

## A minimal DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract(): ...
def transform(): ...
def load(): ...

with DAG(
    dag_id="daily_sales_etl",
    schedule="0 2 * * *",              # cron: 2 AM daily
    start_date=datetime(2026, 1, 1),
    catchup=False,                      # don't backfill history on first deploy
    default_args={"retries": 2},
) as dag:

    e = PythonOperator(task_id="extract",   python_callable=extract)
    t = PythonOperator(task_id="transform", python_callable=transform)
    l = PythonOperator(task_id="load",      python_callable=load)

    e >> t >> l                          # dependencies: e then t then l
```

The `>>` operator draws the DAG edges. Because it's Python, you can build tasks in a **loop** (one per table from a config list) — Airflow's version of ADF's metadata-driven ForEach.

---

## Scheduling & backfill

- `schedule` takes a **cron** string or a preset (`@daily`, `@hourly`).
- Airflow runs on **data intervals**: a `@daily` DAG for 2026-08-01 runs *after* that day completes, with the interval available as `logical_date` — enabling clean, idempotent per-interval processing.
- **`catchup`** — if `True`, deploying a DAG with a past `start_date` **backfills** every missed interval; set `False` to avoid an accidental flood. Backfill is a headline Airflow feature.

This interval model is *why* Airflow tasks should be **idempotent** ([Fundamentals](01_Orchestration_Fundamentals.md)) — a backfill reruns many intervals.

---

## Operators you'll actually use in a data role

- **`PythonOperator` / `@task` (TaskFlow API)** — run Python.
- **`BashOperator`** — run a shell command.
- **`DatabricksSubmitRunOperator` / `DatabricksRunNowOperator`** — trigger a Databricks job (the common Azure bridge).
- **`SparkSubmitOperator`** — submit a Spark job.
- **`SQLExecuteQueryOperator`** — run SQL against a warehouse.
- **Sensors** (`FileSensor`, `ExternalTaskSensor`) — wait for a file or another DAG.
- **Provider packages** — Azure, AWS, GCP, dbt, Snowflake operators/hooks.

The pattern in most modern stacks: **Airflow orchestrates; the heavy compute runs elsewhere** (Databricks, Spark, warehouse). Airflow triggers and waits — it doesn't crunch big data itself.

---

## Airflow vs ADF vs Databricks Workflows

| | Airflow | ADF | Databricks Workflows |
|---|---|---|---|
| **Style** | Code (Python) | Low-code GUI + JSON | Config in workspace |
| **Best for** | Complex, cross-system DAGs | Azure-native ingest | Databricks-centric transforms |
| **Backfill** | First-class (`catchup`) | Tumbling-window trigger | Limited |
| **Ecosystem** | Huge (any system) | Azure connectors | Databricks/DLT/dbt |
| **Ops burden** | You run it (or use managed) | Fully managed | Fully managed |

Airflow wins when workflows are **complex, dynamic, code-first, and span many systems**; managed services win when you want less ops overhead on a single platform.

---

## Interview-grade Q&A

- *What is Airflow and why popular?* Open-source, Python-defined DAG orchestrator — flexible, version-controllable, huge ecosystem; the de facto standard.
- *What is a DAG in Airflow?* A Python file defining tasks and dependencies (`a >> b`), scheduled and run in order.
- *Operator vs sensor?* An operator does work; a sensor waits for a condition (file/partition/other DAG) before downstream tasks run.
- *What does `catchup` do?* Controls backfilling of missed intervals when a DAG deploys with a past start date.
- *What is XCom?* A mechanism to pass small values between tasks — not for large data.
- *Does Airflow process the data?* Usually no — it orchestrates and triggers external compute (Databricks/Spark/warehouse); tasks should be idempotent.
- *Airflow vs ADF?* Code-first, cross-system, backfill-strong vs low-code, Azure-native, fully managed.

---

## Further Learning — Docs & Videos
- Airflow core concepts: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/
- TaskFlow API tutorial: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html
- Azure Managed Airflow (in ADF): https://learn.microsoft.com/azure/data-factory/concept-managed-airflow
- Video — Airflow crash course: https://www.youtube.com/results?search_query=apache+airflow+crash+course
