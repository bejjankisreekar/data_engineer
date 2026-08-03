# Databricks & Spark Cost Optimization

## Where the Databricks bill comes from

A Databricks bill has **two stacked layers**:
1. **Cloud VM cost** — the Azure virtual machines in your cluster (paid to Azure).
2. **DBUs (Databricks Units)** — Databricks' own usage charge, a normalized measure of processing per second, varying by workload tier and cluster type.

So **cost ≈ (VM price + DBU rate) × cluster size × runtime**. Every optimization below shrinks one of those factors. This builds on [Clusters & Compute](../08_Databricks/02_Clusters_and_Compute.md).

---

## Lever 1 — Use the right cluster type

| Cluster | Cost behavior | Use for |
|---|---|---|
| **Job cluster** | Spun up per job, **auto-terminated** after | **Scheduled production jobs** — cheapest, isolated |
| **All-purpose (interactive)** | Stays up while you work; costly if idle | Dev/exploration only |
| **Serverless** | Pay per use, instant start, no idle | Bursty/ad-hoc SQL & jobs; no cluster management |
| **SQL Warehouse** | For BI/SQL; can auto-stop | Serving Power BI / dbt |

**The single biggest Databricks waste:** running scheduled jobs on an always-on all-purpose cluster. Move them to **job clusters**. ([Workflows](../12_Orchestration/03_Databricks_Workflows.md))

---

## Lever 2 — Auto-terminate and autoscale

- **Auto-termination** — set interactive clusters to shut down after 10–20 min idle. This alone eliminates the classic "left the cluster on over the weekend" bill.
- **Autoscaling** — let the cluster grow/shrink worker count with load, so you don't pay for a fixed large cluster during light phases. Set a sensible **min/max**; a too-high max can still surprise you.

---

## Lever 3 — Spot / low-priority instances

**Spot instances** (Azure Spot VMs) use spare capacity at up to ~70–90% discount — but Azure can **reclaim** them with little notice.

- ✅ Great for **workers** on fault-tolerant batch jobs (Spark re-runs lost tasks).
- ⚠️ Keep the **driver** on-demand (losing it kills the job).
- ❌ Avoid for latency-critical or short-SLA jobs that can't tolerate interruption.

A common cost win: spot workers + on-demand driver on nightly batch. This ties to [reliability](../13_Monitoring_and_Observability/03_Pipeline_Reliability.md) — spot is a cost/reliability trade.

---

## Lever 4 — Photon

**Photon** is Databricks' vectorized C++ execution engine. It speeds up many SQL/DataFrame workloads substantially. It carries a higher DBU rate, but if it makes a job finish **more than proportionally faster**, the **total cost drops** (shorter runtime beats higher rate). Benchmark it — for scan/aggregation-heavy jobs it's often a net win.

---

## Lever 5 — Right-size, don't over-provision

- Match cluster size to the **data volume and job**, not "big to be safe." A 2 GB job doesn't need 20 nodes.
- Fewer, larger nodes vs many small — depends on the workload; test.
- Watch the **Spark UI**: if most executors are idle, you over-provisioned; if there's heavy spill/GC, you under-provisioned. ([Performance](04_Performance_Optimization.md))

---

## Lever 6 — Scan and shuffle less (cost = work)

Every performance optimization in [file 04](04_Performance_Optimization.md) is *also* a cost optimization, because less work = less compute-time:

- **Partition pruning / file skipping** so queries read only relevant data.
- **Avoid wide shuffles** and skew that make jobs drag.
- **Incremental processing** (MERGE, Auto Loader) instead of full rebuilds.
- **`OPTIMIZE`/compaction** so you don't scan millions of tiny files.

---

## Lever 7 — Don't recompute; cache and reuse

- Persist expensive intermediate results instead of recomputing them across notebooks.
- Use **incremental** pipelines so each run processes only new data ([dbt incremental](../14_dbt/02_Models_and_Refs.md), [Structured Streaming](../03_Programming/PySpark/13_Structured_Streaming.md)).
- Materialize a shared Gold table once rather than every dashboard recomputing it.

---

## A cost-optimization checklist for a Databricks job

- [ ] Runs on a **job cluster** (not all-purpose), with **auto-termination**
- [ ] **Autoscaling** with sensible min/max
- [ ] **Spot workers** + on-demand driver (if SLA tolerates)
- [ ] **Photon** benchmarked and enabled if it's a net win
- [ ] Right-sized to the data (checked in Spark UI, no idle army / no heavy spill)
- [ ] **Incremental**, not full rebuild; tables `OPTIMIZE`d
- [ ] Tagged for cost attribution; covered by a **cluster policy**

---

## Interview-grade Q&A

- *What's a DBU?* A Databricks Unit — a normalized per-second measure of processing that Databricks charges on top of the underlying VM cost.
- *Biggest Databricks cost mistake?* Running scheduled jobs on an always-on all-purpose cluster instead of an auto-terminating **job cluster**.
- *When do you use spot instances?* For workers on fault-tolerant batch jobs (big discount, tolerate reclaim); keep the driver on-demand; avoid for latency-critical work.
- *Does Photon always save money?* No — it has a higher DBU rate; it saves money when it speeds the job up more than proportionally. Benchmark it.
- *How does performance tuning relate to cost?* Directly — less data scanned and less shuffle means shorter runtime, which means lower compute cost. Same problem.
- *How do you right-size a cluster?* Match to data/job size and inspect the Spark UI — idle executors mean too big; heavy spill/GC means too small.

---

## Further Learning — Docs & Videos
- Databricks cost optimization: https://learn.microsoft.com/azure/databricks/lakehouse-architecture/cost-optimization/
- Cluster configuration best practices: https://learn.microsoft.com/azure/databricks/compute/cluster-config-best-practices
- Photon: https://learn.microsoft.com/azure/databricks/compute/photon
- Video — Databricks cost optimization: https://www.youtube.com/results?search_query=databricks+cost+optimization+best+practices
