# 04 — Slowly Changing Dimensions (SCD)

## What is an SCD?

A **Slowly Changing Dimension** is a dimension whose attributes **change over time** — a customer moves city, a product changes category. The question is: when the source value changes, do you **overwrite** it, **keep history**, or something in between? SCD "types" are the standard answers.

**Analogy:** A customer moves from Hyderabad to Bangalore. Do you erase "Hyderabad" (Type 1), or keep the old record and add a new one so past orders still show "Hyderabad" (Type 2)? That choice is the SCD type.

---

## The SCD types (Type 2 is the one that matters most)

| Type | Behavior | History? | Use |
|---|---|---|---|
| **Type 0** | Never changes (retain original) | Original only | Immutable attributes (birth date) |
| **Type 1** | **Overwrite** the old value | None | When history doesn't matter |
| **Type 2** | **Add a new row** per change (+ effective dates / current flag) | **Full** | The common one — auditability, point-in-time reporting |
| **Type 3** | Add a **"previous value" column** | Limited (1 prior) | Track just the last change |
| **Type 4** | Move history to a **separate history table** | Full (elsewhere) | Fast current dim + separate history |
| **Type 6** | Hybrid **1 + 2 + 3** | Full + current attribute | Both current and historical views |

> **Interview tip:** If asked "how do you keep history of dimension changes?" the answer is **SCD Type 2** — new row per change with `start_date`, `end_date`, and `is_current`, using **surrogate keys**.

---

## SCD Type 2 in detail

Each version of a business entity is a **separate row** with its own **surrogate key**:

| product_sk | product_nk | category | start_date | end_date | is_current |
|---|---|---|---|---|---|
| 101 | P-1 | Snacks | 2024-01-01 | 2025-06-30 | false |
| 205 | P-1 | Healthy Snacks | 2025-07-01 | 9999-12-31 | true |

- Facts reference the **surrogate key** valid at the time of the event, so historical facts keep their historical context.
- `is_current = true` gives the latest version; date ranges enable **point-in-time** queries.

### Implementing SCD2 with Delta MERGE
```sql
-- Step 1: close changed current rows
MERGE INTO gold.dim_product t
USING staging s ON t.product_nk = s.product_nk AND t.is_current = true
WHEN MATCHED AND (t.category <> s.category) THEN
  UPDATE SET t.is_current = false, t.end_date = current_date();

-- Step 2: insert new versions for changed + brand-new keys
INSERT INTO gold.dim_product
SELECT next_sk(), s.product_nk, s.category, current_date(), DATE'9999-12-31', true
FROM staging s
LEFT JOIN gold.dim_product t
  ON t.product_nk = s.product_nk AND t.is_current = true
WHERE t.product_nk IS NULL OR t.category <> s.category;
```
> Databricks **Delta Live Tables `APPLY CHANGES ... STORED AS SCD TYPE 2`** automates this pattern.

---

## Related concepts
- **Rapidly Changing Dimension (RCD):** an attribute changes so often that SCD2 explodes row counts → split it into a **mini-dimension** (bucketed ranges) referenced by the fact.
- **Late-arriving dimension:** a fact arrives before its dimension row exists → insert a **placeholder/inferred member** now, update attributes when the dimension arrives.
- **Late-arriving fact:** an old fact arrives now → look up the dimension version that was current **at the fact's event date** (not today's).

---

## Pro / Interview notes
- **SCD2 requires surrogate keys** — the natural key repeats across versions, so it can't be the PK.
- Track changes only on **meaningful attributes**; overwriting trivial ones (Type 1) avoids row explosion.
- **Common mistakes:** using the natural key as PK (can't version), forgetting the current-flag/date maintenance, or updating facts to the *current* dim version (breaks history).
- MERGE performance: **partition-prune** the target on the join key so you don't rewrite the whole dimension.

---

## Quick Review
- ✔ SCD = dimension attributes that change over time
- ✔ **Type 1** overwrite (no history) · **Type 2** new row + dates/flag (full history) · **Type 3** prior-value column
- ✔ **Type 2 is the default** for auditable point-in-time reporting; needs **surrogate keys**
- ✔ Implement with **Delta MERGE** (close old row, insert new version) or DLT `APPLY CHANGES ... SCD TYPE 2`
- ✔ Handle **late-arriving** dimensions (inferred members) and facts (historical dim version)
- ✔ RCD → mini-dimension to avoid row explosion

## Further Learning — Docs & Videos
- SCD types (Kimball): https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2-dimension/
- DLT APPLY CHANGES (SCD2): https://docs.databricks.com/en/delta-live-tables/cdc.html
- Video — SCD Type 1/2/3 explained: https://www.youtube.com/results?search_query=slowly+changing+dimension+type+1+2+3+explained

Next: **[05 — Data Vault & Modern Modeling](05_Data_Vault_and_Modern_Modeling.md)**.
