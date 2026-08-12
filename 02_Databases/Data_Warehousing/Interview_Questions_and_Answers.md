# Data Warehousing — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module: [Fundamentals](01_Data_Warehouse_Fundamentals.md) · [Data Mart](02_Data_Mart.md) · [Data Mesh](03_Data_Mesh.md) · [Data Fabric](04_Data_Fabric_and_Architecture_Comparison.md).

> 🗺️ Confused about warehouse vs lake vs lakehouse? See the [Storage Paradigms Map](../../05_Storage_and_Formats/00_Storage_Paradigms_Map.md).

---

## Warehouse fundamentals

**Q1. 🔥 What is a data warehouse?**
A central repository that collects, integrates, and stores data from many source systems, structured specifically for business analysis and reporting — not for day-to-day transactions.

**Q2. 🔥 What are the four defining properties of a data warehouse?**
Inmon's definition: **subject-oriented** (organized around Customer/Product/Sales, not source apps), **integrated** (inconsistent sources reconciled to one format), **time-variant** (every record tied to a point in time; holds history), **non-volatile** (loaded data isn't updated/deleted in normal operation — facts are appended).

**Q3. 🔥 Data warehouse vs database (OLTP)?**
OLTP runs the live business — many small, fast, concurrent transactions on current data. A warehouse serves analytics — few large scan-heavy queries over integrated history. Different workload, different physical design ([OLTP](../../01_Foundations/Fundamentals/01_OLTP_Storage.md) vs [OLAP](../../01_Foundations/Fundamentals/02_OLAP_Storage.md)).

**Q4. ⭐ Why not just run reports directly on the production database?**
Analytical scans compete with transactional workload (locking, cache eviction, latency spikes), the OLTP schema is normalized for writes not reads, and it holds only *current* state — no history. Offload instead via extracts/CDC.

**Q5. ⭐ What does "non-volatile" mean in practice — never any updates?**
It means the warehouse isn't edited operationally like an OLTP table. History is *added*, not overwritten — corrections come as new versions (e.g. SCD2 rows) so prior reported numbers stay reproducible.

**Q6. 💡 Why is "time-variant" the property teams implement half-way?**
Teams build SCD Type 2 on customer dimensions but forget it on product dimensions, silently losing "what did this product cost when it was sold" accuracy. Time-variance must be decided **per dimension**, deliberately.

---

## Layers & architecture

**Q7. 🔥 Walk through the layers of a warehouse system.**
`Source Systems → Staging → (ODS) → Data Warehouse → Data Marts → BI/Reports`. Staging lands raw as-extracted data; the warehouse holds integrated history; marts are department-scoped subsets.

**Q8. 🔥 What is the staging area for, and what breaks without it?**
A temporary landing zone holding raw data exactly as it arrived. Without it you lose the only safe place to **re-run a failed transformation without re-extracting from the source** — the same raw-retention discipline as Bronze in the [medallion architecture](../../05_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md).

**Q9. ⭐ What is an ODS, and why not just query it instead of building a warehouse?**
An **Operational Data Store** holds current, lightly integrated, near-real-time operational data — used for fresh operational reporting without hitting production OLTP. It lacks deep history and dimensional modeling, so it *complements* a warehouse rather than replacing one.

**Q10. ⭐ Single-tier vs two-tier vs three-tier architecture?**
Single-tier = sources feed one layer directly (source changes ripple into reporting; rare). Two-tier = staging + warehouse, no mart layer (smaller estates). **Three-tier** = staging → warehouse → marts, the standard enterprise pattern separating landing, integrated history, and consumption.

**Q11. 💡 What quietly turns an ODS into a second warehouse?**
No retention/archival policy. Nobody decides to keep history — it just accumulates because deleting feels risky. Decide ODS retention explicitly up front.

---

## Inmon vs Kimball

**Q12. 🔥 Inmon vs Kimball, in one line?**
**Inmon** = top-down: build one normalized (3NF) enterprise warehouse first, derive dependent marts from it. **Kimball** = bottom-up: build dimensional star-schema marts first, kept comparable through **conformed dimensions**.

**Q13. 🔥 What are conformed dimensions and why do they matter?**
Dimensions shared across marts/facts with identical meaning (one `dim_date`, one `dim_customer`). They're the "bus" that lets independently built marts be combined and compared — the thing that keeps Kimball's bottom-up approach from drifting.

**Q14. ⭐ Which methodology would you choose in a design review?**
Small team, fast-moving, BI-first → **Kimball** dimensional bus (ship a star schema per subject area; invest in conformed dimensions from day one). Large enterprise, many consumers, consistency non-negotiable → **Inmon** central integration layer first. Most 2020s teams → **hybrid**: one governed Silver/integration layer (Inmon discipline) + star-schema Gold marts (Kimball speed).

**Q15. 💡 What's the "we'll conform the dimensions later" trap?**
It never happens under deadline pressure. Conformed dimensions are dramatically cheaper to design *before* the second mart exists than to retrofit across five marts that have already diverged.

---

## Data marts

**Q16. 🔥 What is a data mart, and why not let everyone query the warehouse?**
A department-scoped subset of the warehouse, built for **performance, simplicity, and access control** that one shared enterprise schema doesn't provide. Almost always a denormalized [star schema](../SQL/13_SQL_Warehouse.md).

**Q17. 🔥 Dependent vs independent vs hybrid marts?**
**Dependent** — sourced from the already-integrated central warehouse (consistent; needs the warehouse first — Inmon). **Independent** — pulled straight from source systems (fast to build; every mart reinvents integration logic → metric drift). **Hybrid** — a mix, needing deliberate governance.

**Q18. ⭐ What is a "spreadmart" and how do you prevent it?**
Dozens of departmental marts (or spreadsheets treated as marts) that each independently — and *differently* — defined the same metric, so two executives bring two numbers for "net revenue." Prevented by conformed dimensions and a governed shared semantic layer, **not** by banning marts outright.

**Q19. ⭐ How does a data mart look different in a lakehouse?**
Often not a separate physical database at all — a **domain-scoped set of Gold-layer views** over the same Delta tables, with catalog grants (e.g. Unity Catalog) restricting each domain. The mart becomes a *lens*, not a duplicate copy.

**Q20. 💡 Why is schema similarity between two marts not proof of comparability?**
Both may have a `region` column while encoding genuinely different business rules underneath (different region-to-store mappings). Comparability comes from conformed definitions, not matching column names.

---

## Data mesh

**Q21. 🔥 What is data mesh in one sentence?**
A decentralized **organizational** model where business domains own and publish their own data as governed products, supported by a shared self-serve platform and federated governance — *not* a storage technology.

**Q22. 🔥 What are the four principles of data mesh?**
1) **Domain-oriented decentralized ownership**, 2) **data as a product** (schema contract, docs, freshness/quality SLA, owner), 3) **self-serve data infrastructure platform**, 4) **federated computational governance** (org-wide standards enforced by automated policy). Remove any one and it's chaos, not mesh.

**Q23. 🔥 Is data mesh a replacement for a warehouse, lake, or lakehouse?**
No — and this is the key distinction. Those are *technology* choices about how data is stored and queried; mesh is a decision about *who owns and is accountable for* data. They sit on different axes and combine freely — each domain commonly runs its own lakehouse.

**Q24. ⭐ When would you advise against data mesh?**
Small-to-mid organizations, a single product line, or anywhere the "platform team" and "governance council" would be the same three people in different hats. Without a genuine measured central-team bottleneck and domain engineering capacity, a centralized lakehouse with domain-scoped marts delivers the same benefit far cheaper.

**Q25. 💡 What are the most common failed mesh adoptions?**
"Mesh" as a rebrand for existing silos (no platform, no federated governance); exposing raw tables with no contract/SLA (moving the swamp closer to the source); no real self-serve (still filing tickets, so the bottleneck never moved); and under-investing in governance, which recreates independent-mart drift at larger scale. Also: cross-domain analytics still needs conformed keys — mesh decentralizes who maintains them, it doesn't remove the need.

---

## Data fabric & choosing between patterns

**Q26. 🔥 What's the difference between data fabric and data mesh?**
**Fabric** is a *technology* pattern — active metadata, automated integration, virtualization connecting distributed sources so data feels unified without a big-bang migration. **Mesh** is an *organizational* pattern — domain ownership, data as a product, federated governance. They complement rather than compete: fabric tooling is often what makes a mesh's federated governance achievable at scale.

**Q27. ⭐ Is Microsoft Fabric "a data fabric"?**
It's a **product** that embodies data-fabric *principles* (OneLake as a unifying storage/metadata layer across engines), but using it doesn't automatically mean the organization implemented the pattern — that still requires deliberate governance design. Don't conflate the two in an interview.

**Q28. 🔥 How do warehouse, lake, lakehouse, mesh, and fabric relate?**
Five patterns answering five *different* questions, not one question five ways: warehouse = integrated historical SQL storage; lake = cheap raw storage; lakehouse = warehouse guarantees at lake economics; mesh = who *owns* data organizationally; fabric = how to technically connect/govern already-scattered data. The first three are storage tech, mesh is ownership, fabric is integration — commonly combined.

**Q29. ⭐ When is data fabric the right call over consolidating into one lakehouse?**
When disparate systems (legacy on-prem, multiple clouds, SaaS) can't or shouldn't be migrated big-bang and federated discovery/governance is needed sooner than consolidation could deliver. Caveat: federated queries carry real latency/reliability cost — virtualization is a **bridge**, not always a permanent architecture.

**Q30. 💡 Did the cloud change warehouse theory?**
No — it changed the *storage engine*. Staging, integration, conformed dimensions, and marts are exactly what a lakehouse still does: a Delta Gold layer is functionally a Kimball mart; a Silver layer with conformed keys is functionally an ODS/integration layer. The vocabulary shifted, the discipline didn't.

---

## Common interview mistakes
- Saying data mesh **replaces** a warehouse/lakehouse — it's an ownership model, a different axis.
- Claiming "we use Microsoft Fabric" therefore "we have a data fabric architecture" — product ≠ pattern.
- Skipping the staging layer, then having no way to re-run a failed load without re-extracting.
- Treating independent marts as harmless — they're how spreadmarts and "which number is right?" meetings start.
- Describing Kimball without mentioning **conformed dimensions** (the whole mechanism that keeps it consistent).
- Presenting the five patterns as a ladder where "newer is better" instead of axis-based trade-offs.

## Related Topics
[Data Modeling](../Data_Modeling/03_Dimensional_Modeling.md) · [SQL Warehouse (star schema, SCD)](../SQL/13_SQL_Warehouse.md) · [Storage Paradigms Map](../../05_Storage_and_Formats/00_Storage_Paradigms_Map.md) · [Lakehouse Architecture](../../05_Storage_and_Formats/Lakehouse/03_Lakehouse_Architecture.md) · [Medallion Architecture](../../05_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md) · [Data Governance](../../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md)
