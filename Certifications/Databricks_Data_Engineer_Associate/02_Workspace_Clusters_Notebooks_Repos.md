# 02 — Workspace, Clusters, Notebooks & Repos

*Domain: Databricks Lakehouse Platform (24%)*

---

## Clusters

A **cluster** is a set of computation resources (a **driver** node + one or more **worker** nodes) running the Databricks Runtime. Your notebook/job attaches to a cluster to run code.

### Cluster types

| Type | Purpose | Behavior |
|---|---|---|
| **All-Purpose cluster** | Interactive development — notebooks, ad-hoc analysis, collaboration | Created manually; can be shared by multiple users; can be restarted; stays until terminated. |
| **Job cluster** | Running an automated job/workflow | Created automatically when the job starts, **terminated automatically when the job finishes**. Cheaper and isolated. |

> **Exam Tip:** Use **all-purpose clusters** for interactive/development work and **job clusters** for scheduled production jobs. Job clusters are recommended for production because they spin up fresh, run the job, and tear down — lower cost and no state leakage. Running scheduled jobs on all-purpose clusters costs more.

### Driver vs Workers

- **Driver node** — runs the main program, maintains cluster state, distributes tasks, collects results. `display()`/`collect()` results come back to the driver. There is exactly **one** driver.
- **Worker (executor) nodes** — run the actual distributed tasks in parallel. More workers = more parallelism.

### Cluster modes / access modes (Unity Catalog era)

- **Single-user (assigned) access mode** — one named user; supports Python, SQL, Scala, R; full Unity Catalog features for that user.
- **Shared access mode** — multiple users share the cluster with process isolation; supports Python and SQL (Scala limited); Unity Catalog enforced.
- **No-isolation shared** — legacy, not UC-secured.

### Cluster lifecycle & cost controls

- **Auto-termination** — cluster shuts down after N minutes of inactivity to save cost. Strongly recommended for all-purpose clusters.
- **Autoscaling** — automatically adds/removes workers between a min and max based on load.
- **Restart / Terminate / Delete** — restart keeps config and clears state; terminate stops compute but **keeps the config** so you can restart; delete removes the config entirely.

> **Exam Tip:** **Terminating a cluster does not delete it** — the configuration is retained and you can restart it later. Only *delete* removes it. Restarting a cluster clears cached data and installed session state.

---

## Databricks Runtime (DBR)

You choose a **DBR version** when creating a cluster. Key variants:

- **Standard DBR** — Spark + Delta + optimizations.
- **DBR ML** — adds popular ML libraries (TensorFlow, PyTorch, scikit-learn, XGBoost) and GPU support.
- **Photon** — vectorized engine toggle for faster SQL/DataFrame workloads.
- **LTS (Long-Term Support)** versions — supported longer; preferred for production stability.

---

## Notebooks

A **notebook** is an interactive document of runnable cells attached to a cluster.

- **Multi-language** — the notebook has a default language, but any cell can switch using **magic commands**:
  - `%python`, `%sql`, `%scala`, `%r` — run that cell in the named language.
  - `%md` — Markdown (documentation).
  - `%sh` — shell command on the driver node.
  - `%fs` — file system commands (e.g., `%fs ls /`).
  - `%run ./other_notebook` — **run another notebook inline**, sharing its variables/functions into the current one.
- **`dbutils`** — Databricks utilities available in notebooks:
  - `dbutils.fs` — file system operations (`ls`, `cp`, `mkdirs`, `rm`).
  - `dbutils.widgets` — create parameters/inputs for the notebook (used to parameterize jobs).
  - `dbutils.secrets` — retrieve secrets from a secret scope (never hardcode credentials).
  - `dbutils.notebook.run("path", timeout, args)` — run another notebook **as a separate job** and get a return value (vs `%run` which runs inline).

> **Exam Tip:** **`%run` vs `dbutils.notebook.run()`** is a classic distinction. `%run` executes another notebook **in the same context** — its variables and functions become available in the caller. `dbutils.notebook.run()` executes it in a **new, separate execution** and returns only a string value; variables are **not** shared. Use `%run` to import shared functions/config; use `dbutils.notebook.run()` to orchestrate/parameterize independent notebooks.

- **Collaboration** — real-time co-editing, comments, and version history are built in.
- **Results & display** — `display(df)` renders a DataFrame as an interactive table/chart in the notebook.

---

## Databricks Repos / Git folders

**Repos** (now "Git folders") integrate Git version control directly into the workspace.

- Clone a remote repo (GitHub, GitLab, Bitbucket, Azure DevOps) into your workspace.
- Perform **commit, push, pull, branch, and merge** from the Databricks UI.
- Enables **CI/CD** — production code lives in Git; jobs run notebooks from a specific branch/commit.

> **Exam Tip:** Repos support standard Git operations (clone, commit, push, pull, branch) and are the recommended way to manage code versioning and promote code between environments (dev → staging → prod). The Workspace's built-in notebook revision history is **not** a substitute for Git.

---

## DBFS and storage abstractions

- **DBFS (Databricks File System)** — a distributed file system abstraction mounted over cloud object storage. Paths look like `/dbfs/...` or `dbfs:/...`. The `/FileStore` area holds uploaded files.
- With **Unity Catalog**, prefer **Volumes** (governed storage locations) and managed tables over raw DBFS mounts. DBFS root and mounts are legacy patterns.

> **Exam Tip:** Uploaded data lands under `dbfs:/FileStore/`. `dbutils.fs.ls("/")` and `%fs ls /` list DBFS. Under Unity Catalog, non-tabular files are governed through **Volumes**.

---

## Quick Review

- **All-purpose cluster** = interactive/dev, shared, manual, persists. **Job cluster** = auto-created and **auto-terminated** with the job; cheaper for production.
- **Driver** (one, coordinates, receives results) + **workers** (parallel task execution).
- **Auto-termination** saves cost on idle; **autoscaling** adjusts worker count. **Terminate keeps config** (restartable); **delete** removes it.
- **DBR** variants: Standard, **ML** (adds ML libs), **Photon** (faster SQL), **LTS** (production).
- Magic commands: `%python %sql %scala %r %md %sh %fs %run`. `dbutils` = `fs`, `widgets`, `secrets`, `notebook.run`.
- **`%run`** = inline, shares variables; **`dbutils.notebook.run()`** = separate execution, returns a string only.
- **Repos / Git folders** = built-in Git (clone/commit/push/pull/branch) for version control and CI/CD.

---

## Further Learning — Docs & Videos

**Official documentation**
- Compute / clusters: https://docs.databricks.com/en/compute/index.html
- Cluster configuration: https://docs.databricks.com/en/compute/configure.html
- Databricks Runtime releases: https://docs.databricks.com/en/release-notes/runtime/index.html
- Notebooks: https://docs.databricks.com/en/notebooks/index.html
- `dbutils` reference: https://docs.databricks.com/en/dev-tools/databricks-utils.html
- Git folders (Repos): https://docs.databricks.com/en/repos/index.html

**Videos**
- Databricks official YouTube channel: https://www.youtube.com/@Databricks
- Clusters explained: https://www.youtube.com/results?search_query=databricks+cluster+all+purpose+vs+job+cluster
- Notebooks & magic commands: https://www.youtube.com/results?search_query=databricks+notebook+magic+commands+dbutils
- Databricks Repos / Git integration: https://www.youtube.com/results?search_query=databricks+repos+git+integration

---

Next: **[03 — Delta Lake Fundamentals](03_Delta_Lake_Fundamentals.md)**.
