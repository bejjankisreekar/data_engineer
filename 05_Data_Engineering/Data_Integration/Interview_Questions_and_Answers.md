# Data Integration — Interview Questions & Answers

Tagged: 🔥 very common · ⭐ common · 💡 deeper.

---

## Fundamentals
**Q1. 🔥 What is data integration? How is it different from ETL?**
Combining data from many sources into a unified, consistent view. ETL/ELT is *one technique* within it; integration also covers replication, CDC, virtualization, streaming, and API/app integration.

**Q2. 🔥 ETL vs ELT?**
ETL transforms before load (external engine); ELT loads raw then transforms in the target using its compute. Modern lakehouse = ELT.

**Q3. ⭐ Batch vs streaming integration — when each?**
Batch = scheduled bulk (most analytics/reporting). Streaming = continuous low-latency (real-time dashboards, alerting, fraud). Most platforms are hybrid.

**Q4. ⭐ What is data virtualization/federation?**
Querying multiple sources **without moving/copying** data (e.g., Synapse serverless external tables over the lake). Good for ad-hoc access and avoiding copies.

**Q5. 💡 What are data silos and why do they matter?**
Isolated source systems with their own formats/"truth." Integration unifies them so cross-system questions (total revenue per customer) can be answered consistently.

## Patterns
**Q6. 🔥 Full vs incremental load?**
Full reloads everything (simple, costly). Incremental loads only changes via a **watermark** or **CDC** — standard at scale. Incremental must be **idempotent**.

**Q7. 🔥 How do you make a load idempotent?**
MERGE on the business key, or overwrite the target **partition** for the run window. Ensures re-runs don't duplicate.

**Q8. 🔥 What is a metadata-driven pipeline?**
One generic pipeline driven by a **control table** (source, target, load type, watermark). A loop iterates config rows. New table = one config row, not a new pipeline — scales to hundreds of tables.

**Q9. ⭐ How do you handle schema drift?**
Land raw with schema evolution (Auto Loader `_rescued_data` / Delta `mergeSchema`); don't hard-map volatile sources; alert on new/changed columns.

**Q10. 💡 Delivery semantics — at-least-once vs exactly-once?**
At-least-once may duplicate → pair with an **idempotent** sink. Exactly-once = checkpoint + idempotent sink (Structured Streaming + Delta MERGE). Ordering guaranteed only within a partition/key.

## CDC
**Q11. 🔥 What is CDC and why use it over a watermark?**
Captures row-level inserts/updates/**deletes** from the source change log, near real-time. Beats a watermark because it **captures deletes** and doesn't scan the whole table.

**Q12. ⭐ Log-based vs trigger-based vs query-based CDC?**
Log-based reads the transaction log (lowest overhead, all changes + order — preferred). Trigger-based writes to a shadow table (adds write load). Query/timestamp polls a modified column (misses deletes).

**Q13. ⭐ How do you apply CDC changes to Delta?**
`MERGE` handling D/U/I; dedupe to the **latest change per key** for out-of-order events; use DLT `APPLY CHANGES` for SCD2.

**Q14. 💡 What is Delta Change Data Feed (CDF)?**
A Delta feature exposing row-level changes *out of* a Delta table (`table_changes(...)`) so downstream jobs propagate only changes (e.g., Silver → Gold) without full re-scans.

## Azure services
**Q15. 🔥 ADF vs Databricks vs Synapse for integration?**
ADF = orchestration + ingestion (connectors, on-prem via SHIR). Databricks = heavy Spark transformation, streaming, ML. Synapse = MPP warehouse + serverless lake query + its own pipelines.

**Q16. 🔥 Event Hubs vs Service Bus vs Event Grid?**
Event Hubs = high-throughput event **streaming**. Service Bus = enterprise **messaging** (queues/topics, ordering, transactions). Event Grid = reactive **event routing**.

**Q17. ⭐ How do you integrate an on-prem source?**
ADF **Self-Hosted Integration Runtime** (2+ nodes for HA), secrets in Key Vault, incremental watermark/CDC.

**Q18. ⭐ When would you use Logic Apps vs ADF?**
Logic Apps for **SaaS app/workflow** integration (connectors, approvals, webhooks); ADF for **data** ingestion/orchestration at scale.

**Q19. 💡 When would you use Azure Functions in integration?**
Lightweight, event-driven glue — call a REST API on a timer, react to a blob, small transforms — not heavy data processing (use Spark).

## Scenario
**Q20. 🔥 "Sync 500 tables from on-prem SQL to the lake, low maintenance, capture deletes."**
Metadata-driven framework + **CDC** (SQL CDC/Debezium) → Event Hub/files → **MERGE** into Delta; SHIR for connectivity; Key Vault secrets; idempotent, monitored, alerting.

## Common interview mistakes
- Treating integration as only "ADF ETL."
- Full loads at scale; non-idempotent appends.
- Watermark when deletes matter (use CDC).
- Confusing Event Hubs / Service Bus / Event Grid.

## Related Topics
[ETL vs ELT](../ETL_ELT/01_ETL_vs_ELT.md) · [Azure Data Factory](../ETL_ELT/02_Azure_Data_Factory.md) · [Data Modeling](../../02_Databases/Data_Modeling/00_Data_Modeling_Learning_Path.md) · [Data Storage](../../04_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)
