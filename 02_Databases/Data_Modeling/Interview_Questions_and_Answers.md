# Data Modeling — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module.

---

## Fundamentals

**Q1. 🔥 What are the three levels of a data model?**
**Conceptual** (entities + relationships, business view), **Logical** (attributes, keys, rules — DB-agnostic), **Physical** (tables, data types, indexes, partitions for a specific engine).

**Q2. 🔥 Primary key vs foreign key vs surrogate key?**
PK uniquely identifies a row; FK references another table's PK (enforces a relationship); **surrogate key** = system-generated meaningless integer PK, stable and decoupled from the source (used for warehouse dimensions to enable SCD2).

**Q3. ⭐ Natural key vs surrogate key — which for a warehouse dimension and why?**
**Surrogate key.** A natural (business) key repeats across historical versions of the same entity, so it can't be the PK in an SCD2 dimension; the surrogate gives each version a unique, stable PK.

**Q4. ⭐ How do you model a many-to-many relationship?**
With a **junction/bridge table** holding the two foreign keys (e.g., `student_course(student_id, course_id)`) — relational models can't store M:N directly.

**Q5. 💡 Cardinality types?**
1:1, 1:N, M:N. M:N requires a bridge table.

---

## Normalization

**Q6. 🔥 What is normalization and why do it?**
Organizing tables to remove redundancy so each fact is stored once, preventing insert/update/delete anomalies.

**Q7. 🔥 Explain 1NF, 2NF, 3NF.**
1NF = atomic values + PK (no repeating groups). 2NF = 1NF + no partial dependency on part of a composite key. 3NF = 2NF + no transitive dependency (non-key columns depend only on the key). Mantra: *the key, the whole key, nothing but the key.*

**Q8. ⭐ When do you denormalize?**
For **read-heavy analytics/BI** — star-schema dimensions and Gold tables denormalize to reduce joins and speed queries, accepting redundancy (managed by rebuilding from governed sources).

**Q9. ⭐ Normalize vs denormalize — where in the medallion architecture?**
Normalize source/Silver (integrity); **denormalize Gold** (star/OBT) for query speed.

---

## Dimensional modeling

**Q10. 🔥 Star vs snowflake schema?**
Star = denormalized dimensions (fewer joins, faster, BI-preferred). Snowflake = normalized dimensions (less redundancy, more joins, slower).

**Q11. 🔥 Fact vs dimension table?**
Fact = numeric measures + FKs (tall, fast-growing). Dimension = descriptive attributes (short, wide, slowly changing).

**Q12. 🔥 What is grain? Why define it first?**
The grain is what one fact row represents. Define it first because every dimension and measure must be true at that grain; mixed grain breaks aggregations.

**Q13. ⭐ Kimball's 4-step dimensional design?**
1) pick the business process, 2) declare the grain, 3) choose dimensions, 4) choose facts/measures.

**Q14. ⭐ Types of fact tables?**
Transaction (one event), periodic snapshot (state at intervals), accumulating snapshot (one process across milestones), factless (event with no measure).

**Q15. 💡 Conformed dimension?**
A dimension shared across facts/marts with identical meaning (one dim_date/dim_customer) → consistent cross-mart reporting. A key senior signal.

**Q16. ⭐ Additive vs semi-additive vs non-additive measures?**
Additive = sum across all dims (sales). Semi-additive = sum across some but not time (balance, inventory). Non-additive = never sum (ratios, %). Store components, compute ratios at query time.

**Q17. 💡 Degenerate & junk dimensions?**
Degenerate = a key with no attributes kept in the fact (invoice number). Junk = several low-cardinality flags bundled into one small dimension.

---

## SCD

**Q18. 🔥 Explain SCD Types 1, 2, 3.**
Type 1 = overwrite (no history); Type 2 = new row per change with start/end dates + current flag (full history); Type 3 = add a "previous value" column (limited history).

**Q19. 🔥 How do you implement SCD2 in Delta/Spark?**
`MERGE`: match the current row on the natural key; if a tracked attribute changed, close it (`is_current=false`, set `end_date`) and insert a new versioned row with a new surrogate key. Or DLT `APPLY CHANGES ... STORED AS SCD TYPE 2`.

**Q20. ⭐ Why do you need surrogate keys for SCD2?**
Because one natural key maps to multiple historical rows; each needs a unique PK, and facts reference the version valid at event time.

**Q21. 💡 Late-arriving dimension — how do you handle it?**
Insert an inferred/placeholder dimension member (with a surrogate key) so the fact can load now; update its attributes when the real dimension arrives.

**Q22. 💡 Rapidly changing dimension?**
Split the volatile attributes into a **mini-dimension** (bucketed ranges) referenced by the fact, to avoid SCD2 row explosion.

---

## Modern / Data Vault

**Q23. ⭐ Kimball vs Inmon vs Data Vault?**
Kimball = bottom-up conformed dimensional marts (fast to value, BI-friendly). Inmon = top-down normalized enterprise warehouse then marts (governance-first). Data Vault = hubs/links/satellites integration layer (auditable, agile) with star marts on top.

**Q24. 💡 Data Vault components?**
**Hubs** (business keys), **Links** (relationships), **Satellites** (attributes + history). Insert-only, timestamped, parallel-loadable — used for the integration layer, not BI serving.

**Q25. ⭐ When would you use One Big Table (OBT) instead of a star schema?**
When a column-store engine (Delta/Snowflake) makes join-free wide tables faster — for specific reports, ML feature tables, or when join cost dominates. Trade redundancy for zero joins.

**Q26. 🔥 How does modeling map to the lakehouse layers?**
Bronze = raw (no modeling), Silver = cleaned/normalized (or Data Vault), **Gold = dimensional star schema and/or OBT** for serving.

---

## Common interview mistakes
- Copying the OLTP schema straight into the warehouse (join-heavy, slow).
- Natural key as PK in an SCD2 dimension.
- Not defining grain → mixed-grain facts.
- Summing non-additive measures.
- Using Data Vault as the serving layer (too many joins).

## Related Topics
[SQL](../SQL/07_SQL_Keys_and_Joins.md) · [Data Warehousing](../Data_Warehousing/01_Data_Warehouse_Fundamentals.md) · [Data Integration](../../06_Data_Engineering/Data_Integration/01_Data_Integration_Fundamentals.md) · [Delta Lake / Lakehouse](../../05_Storage_and_Formats/Data_Storage/01_Data_Lake_vs_Warehouse_vs_Database.md)
