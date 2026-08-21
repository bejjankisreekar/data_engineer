# Clusters & Compute

## What is it?

A **cluster** in Databricks is the group of virtual machines that actually runs your Spark code. Nothing executes without compute attached: a notebook or job hands work to a cluster, the cluster's **driver** plans it and the **workers** (executors) do it in parallel ([Spark architecture recap](../03_Programming/PySpark/Spark_Architecture.md)).

Choosing and sizing compute correctly is where Databricks cost and performance are won or lost — this is the most practical note in the module.

In one line: **a cluster = one driver VM + N worker VMs running a Databricks Runtime, that you rent while your code runs.**

---

## Analogy: hiring crew for a job

A **driver** is the site foreman — it doesn't lift bricks, it reads the plan, splits the work into tasks, and hands them out. The **workers** are the labourers who do the lifting in parallel. A small repair needs one foreman and two labourers; building a tower needs a big crew. **Autoscaling** is hiring extra labourers when the work piles up and letting them go when it's quiet. **Auto-termination** is sending everyone home (and stopping the clock) when there's no work at all — so you're not paying a crew to stand around.

---

## The cluster types (the key decision)

| Type | When it runs | Use for | Cost |
|---|---|---|---|
| **All-purpose (interactive)** | You start it; stays up until idle-terminate | Development, exploration, ad-hoc analysis, shared teamwork | Higher (often idle) |
| **Job cluster** | Created for a job run, **destroyed when done** | Scheduled/production jobs | Lower (no idle time) |
| **SQL warehouse** | Serves Databricks SQL / BI queries | Dashboards, SQL analysts, BI tools | Depends on size/serverless |
| **Instance pool** | Warm idle VMs shared by clusters | Cutting cluster **startup** time | Small idle cost, big time saving |

**The #1 cost mistake:** running a scheduled job on an always-on all-purpose cluster. **Rule: interactive clusters for humans, job clusters for jobs.**

---

## Anatomy of a cluster

```
        ┌─────────────┐
        │   DRIVER    │  ← plans work, holds results, runs the notebook
        └──────┬──────┘
     ┌─────────┼─────────┐
 ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
 │Worker│  │Worker│  │Worker│  ← executors run tasks in parallel
 └──────┘  └──────┘  └──────┘
   (autoscale: 2 → 8 workers as load grows)
```

Configuration knobs you'll actually touch:
- **Databricks Runtime (DBR)** — Spark + library version (pick an LTS for production; Photon for SQL speed).
- **Worker & driver VM type** — memory-optimized, compute-optimized, or general.
- **Min/max workers** — the autoscaling range.
- **Auto-termination** — minutes of idle before shutdown (set it low!).
- **Access mode** — single-user vs shared (matters for Unity Catalog).
- **Spot/on-demand** — spot VMs are cheaper but can be reclaimed.

---

## Advantages

- **Elastic** — autoscale up for big jobs, down when idle; no fixed cluster to maintain.
- **Cost control** — auto-termination and job clusters mean you pay only while working.
- **Fast starts** — instance pools keep warm VMs ready.
- **Photon** — big speedups for SQL/DataFrame workloads with no code change.
- **Isolation** — each job cluster is fresh, avoiding "noisy neighbour" and dependency clashes.

## Disadvantages

- **Startup latency** — a cold cluster takes minutes to launch (pools mitigate).
- **Cost sprawl** — idle interactive clusters and oversized VMs waste money quietly.
- **Tuning skill needed** — wrong VM type or worker count = slow *and* expensive.
- **Spot reclaim** — cheap spot workers can vanish mid-job, causing retries.

---

## Azure Usage

- **DBUs (Databricks Units)** — Databricks bills DBUs *plus* the underlying Azure VM cost. Cost ≈ (DBU rate × cluster DBUs) + Azure VM hours.
- **Cluster policies** — platform teams restrict VM types, autoscale limits, tags, and auto-termination so a big workspace doesn't overspend.
- **Tags** — attach cost-center tags to clusters for chargeback in Azure Cost Management.
- **Serverless** — Databricks-managed compute (SQL warehouses, and increasingly jobs/DLT) that starts in seconds with no VM management.

---

## Real World Example

A team's nightly ETL ran on the same all-purpose cluster they used for development — left running 24/7 "so it's ready in the morning." The cluster cost as much idle as it did working. Two changes fixed it: the nightly pipeline moved to a **job cluster** (created at 2 a.m., destroyed by 2:40 a.m.), and the dev cluster got a **20-minute auto-termination**. Monthly compute spend dropped by more than half with zero change to the actual pipeline logic — and the pipeline even ran faster on a right-sized, isolated job cluster.

---

## Right-sizing: memory vs compute vs storage optimized

- **Memory-optimized** — wide joins, big shuffles, caching, skew ([joins](../03_Programming/PySpark/07_Joins.md)). Most ETL lives here.
- **Compute-optimized** — CPU-bound work, lots of narrow transformations, streaming.
- **Storage-optimized** — very large shuffles/caching that spill to local disk.

Start from the workload, not a default. A shuffle-heavy job on compute-optimized VMs will spill and crawl; a CPU-bound job on memory-optimized VMs wastes RAM you paid for.

## Autoscaling — what it can and can't do

Autoscaling adds/removes *workers* based on pending tasks. It helps bursty and unpredictable loads. It does **not** fix a badly written job (a giant shuffle or skew doesn't get faster with more small workers if one task is the bottleneck), and it can thrash on very short jobs. For steady, predictable batch jobs, a fixed size is often cheaper and more predictable than autoscaling.

## Photon

Photon is a native (C++) vectorized execution engine that replaces parts of the JVM Spark engine for SQL and DataFrame operations. It can dramatically speed up scans, filters, joins, and aggregations — and because it costs more DBUs per hour but finishes faster, the *total* cost often drops. It doesn't accelerate arbitrary Python UDFs ([why UDFs are slow](../03_Programming/PySpark/10_UDFs_and_Pandas_Integration.md)).

## SQL warehouses vs clusters

**Databricks SQL warehouses** are compute tuned for BI/SQL: high concurrency, fast startup (serverless), and result caching, feeding dashboards and tools like Power BI. Use a SQL warehouse for the *serving* layer and all-purpose/job clusters for *engineering* — pointing Power BI at a general-purpose cluster is the wrong tool.

---

## Reading the Spark UI is the real tuning skill

Right-sizing isn't guesswork — the **Spark UI** shows it. Look for: tasks spilling to disk (need more memory or better partitioning), one task far slower than the rest ([skew](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)), a huge shuffle read (a join that should be broadcast), and long GC pauses (driver/executor under-provisioned). The pro sizes a cluster by running once and reading the UI, not by copying someone's config.

## Job clusters + pools is the production default

The mature pattern: scheduled jobs run on **job clusters** drawn from an **instance pool**. Pools keep a few warm VMs so job clusters start in seconds instead of minutes, while job clusters guarantee no idle spend after the run. This gives near-interactive startup at batch-cluster cost — the best of both.

## Spot instances with a safety net

Spot (preemptible) workers cut cost sharply but can be reclaimed. The field pattern: **driver on-demand, workers on spot with on-demand fallback**, so a reclaim degrades speed instead of killing the job. Never put the driver on spot — losing it kills the whole run.

## Field-tested gotchas

- **Interactive cluster for scheduled jobs** — the classic money leak; use job clusters.
- **Auto-termination disabled** "for convenience" — an idle cluster all weekend is pure waste.
- **Autoscaling a 30-second job** — scaling overhead exceeds the work; fix the code or fix the size.
- **Driver on spot** — one reclaim and the job dies.
- **Oversized cluster to "make it fast"** — often the job is skewed or shuffle-bound; more workers won't help, and you now overpay.
- **Ignoring the Spark UI** — tuning by vibes instead of evidence.

## Interview-grade Q&A

- *All-purpose vs job cluster?* All-purpose is interactive and stays up for humans (dev, ad-hoc, shared); a job cluster is created for a single job run and destroyed after — cheaper for scheduled work.
- *How do you cut Databricks compute cost?* Job clusters for jobs, aggressive auto-termination, right-sized VM types, instance pools for startup, spot workers with on-demand fallback, cluster policies to enforce it.
- *What is Photon and when does it help?* A vectorized C++ engine that speeds up SQL/DataFrame workloads; it doesn't accelerate Python UDFs.
- *What does autoscaling not fix?* A skewed or badly-written job — more small workers won't speed up a single bottleneck task.
- *When do you use a SQL warehouse instead of a cluster?* For BI/SQL serving (dashboards, high concurrency, Power BI), not for Spark engineering work.

---

## Related Notes

- **Prev:** [What is Databricks?](01_What_is_Databricks.md) · **Next:** [Notebooks, Repos & Jobs](04_Notebooks_Repos_and_Jobs.md)
- **Spark internals:** [Spark Architecture](../03_Programming/PySpark/Spark_Architecture.md) · [Performance & Best Practices](../03_Programming/PySpark/14_Performance_and_Best_Practices.md)
- **Interview:** [Databricks Performance Optimization](../Job%20Interviews/Azure%20Databricks/Performance%20Optimization.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Compute (clusters): https://learn.microsoft.com/en-us/azure/databricks/compute/
- Cluster configuration best practices: https://learn.microsoft.com/en-us/azure/databricks/compute/cluster-config-best-practices

**Videos**
- Databricks clusters explained: https://www.youtube.com/results?search_query=databricks+clusters+explained
- Databricks cost optimization: https://www.youtube.com/results?search_query=databricks+cost+optimization
