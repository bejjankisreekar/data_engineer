# Cost & Performance — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Cost fundamentals

**Q1. 🔥 Why is cost a data engineer's responsibility?**
Cloud meters every choice as money — cluster size, data scanned, idle time — so engineering decisions directly drive the bill. "It works" isn't done; "works, fast, cheap" is.

**Q2. 🔥 What usually dominates a data platform's cost, and what are the top levers?**
**Compute** (size × time). Top levers: right-size compute, auto-terminate idle, and scan less data / finish faster.

**Q3. ⭐ Name the universal cost levers.**
Right-size compute, turn off idle compute, scan less data, avoid recompute (incremental), pick the right compute type, co-locate data and compute.

**Q4. ⭐ How do you get cost visibility and control in Azure?**
Azure Cost Management (analysis by tag/resource), resource **tagging** for attribution, and **budgets with alerts**; enforce with cluster policies/quotas.

**Q5. 💡 What's the trade-off in cost optimization?**
Cost vs performance vs reliability/freshness — right-size per workload SLA rather than blindly minimizing (too-small clusters miss SLAs; spot can be reclaimed).

---

## Databricks / Spark cost

**Q6. 🔥 What is a DBU?**
A Databricks Unit — a normalized per-second processing charge on top of the underlying Azure VM cost.

**Q7. 🔥 What's the most common Databricks cost mistake?**
Running scheduled jobs on an always-on all-purpose cluster instead of an auto-terminating **job cluster**.

**Q8. ⭐ Job cluster vs all-purpose cluster (cost view)?**
Job clusters are ephemeral, per-run, auto-terminated — cheapest for scheduled work. All-purpose stays up for interactive dev and wastes money if idle.

**Q9. ⭐ When do you use spot instances?**
Workers on fault-tolerant batch jobs (big discount, tolerate reclaim); keep the driver on-demand; avoid for latency-critical/short-SLA work.

**Q10. 💡 Does Photon always save money?**
No — it has a higher DBU rate. It saves money only when it speeds the job up more than proportionally; benchmark it (often a win for scan/aggregation-heavy work).

**Q11. ⭐ How do you right-size a cluster?**
Match to data/job size and read the Spark UI: idle executors → too big; heavy spill/GC → too small. Use autoscaling with sensible min/max.

---

## Storage & query cost

**Q12. 🔥 What drives query cost more — storing or scanning data?**
Scanning. How much data a query reads (compute time, or per-TB billing on serverless) usually dwarfs storage cost.

**Q13. 🔥 How do you make queries scan less data?**
Partition pruning (partition by filtered, sensible-cardinality columns like date), Delta file skipping + `ZORDER`, and columnar formats (Parquet/Delta) for column pruning.

**Q14. 🔥 What's the danger of over-partitioning?**
High-cardinality partition columns create millions of tiny files — slower and costlier. Partition only by columns you filter on with reasonable cardinality.

**Q15. 🔥 What is the small-file problem and how do you fix it?**
Too many tiny files cost more to open than to read (and per-operation charges). Fix with `OPTIMIZE`/compaction (target ~128 MB–1 GB) and `VACUUM` old files.

**Q16. ⭐ How do ADLS access tiers reduce cost?**
Lifecycle policies auto-move rarely-read data to Cool/Cold/Archive — cheaper storage for the long tail you must keep but seldom read.

**Q17. 💡 How is Synapse Serverless SQL billed, and how do you optimize it?**
Per **TB of data processed** — minimize scanned data via partitioning, pruning, and columnar formats. Layout literally becomes a line-item cost.

**Q18. 💡 How do you cut Synapse Dedicated SQL pool cost?**
Pause it when idle (it bills for provisioned DWUs while on) and scale DWUs to the workload.

**Q19. 💡 How is Cosmos DB cost controlled?**
RUs (Request Units): good partition keys, prefer point reads, right-size/autoscale throughput, and TTL to shed cold data.

---

## Performance

**Q20. 🔥 What is a shuffle and why is it expensive?**
Redistributing data across the network so related rows co-locate (join/groupBy/distinct/orderBy). Costly (network+disk+serialization); minimize by filtering early and broadcasting.

**Q21. 🔥 What is data skew and how do you fix it?**
Uneven data across partitions so one task dominates; fix with AQE, salting the hot key, broadcasting the small side, or filtering junk (null) keys.

**Q22. 🔥 When and how do you use a broadcast join?**
Joining a big table to a small one — broadcast the small side to avoid shuffling the big table (`broadcast(df)`); Spark auto-broadcasts under a threshold.

**Q23. ⭐ When should you cache a DataFrame?**
When it's expensive to compute and reused multiple times — not indiscriminately (over-caching wastes memory and can hurt).

**Q24. 🔥 How do you debug a slow Spark job?**
Open the **Spark UI**, find the slow stage, and diagnose skew (one long task), shuffle (big shuffle read/write), spill (memory pressure), or small files.

**Q25. 💡 How does performance tuning relate to cost?**
Directly — less data scanned and less shuffle mean shorter runtime, which means lower compute cost. They're the same optimization.

---

## Scenario

**Q26. 🔥 "Your nightly Databricks job's cost tripled and it now runs 3 hours. Diagnose it."**
Check the Spark UI for a new bottleneck: **skew** (a key grew lopsided → one long task), **small files** (streaming/over-partitioning → compact with `OPTIMIZE`), a **full rebuild** that should be incremental, or **shuffle** blowup from a changed query. On the cost side, confirm it's on a **job cluster** with autoscaling/spot and isn't over-provisioned. Usually it's data-growth-induced skew or small files — fix the layout, and both runtime and cost drop together.

**Q27. 💡 "Design a cost-efficient nightly pipeline with a 6 AM freshness SLA."**
Job cluster with auto-termination and autoscaling; spot workers + on-demand driver (SLA has slack overnight); incremental loads (MERGE/Auto Loader), not full rebuilds; partition by date + `OPTIMIZE`/`ZORDER` so queries prune; columnar Delta; tag + cluster policy for governance; a freshness alert so a missed SLA is caught. Right-size to hit 6 AM comfortably, not to be fastest possible.

---

## Further Learning
- Back to the [Learning Path](00_Cost_and_Performance_Learning_Path.md)
- Related: [PySpark Performance](../03_Programming/PySpark/14_Performance_and_Best_Practices.md) · [Databricks Clusters](../08_Databricks/02_Clusters_and_Compute.md) · [Storage](../05_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)
