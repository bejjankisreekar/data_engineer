# dbt Snapshots, Seeds & Macros

## Snapshots — SCD Type 2, the dbt way

Source systems usually **overwrite** records — a customer's row just changes when they move city, losing the old value. **Snapshots** are dbt's built-in mechanism to **capture history** — implementing [Slowly Changing Dimension Type 2](../02_Databases/Data_Modeling/04_Slowly_Changing_Dimensions.md) automatically.

Analogy: a snapshot is a **security camera on a whiteboard** that someone keeps erasing and rewriting. The whiteboard (source) only ever shows the current value; the camera (snapshot) keeps a timestamped record of every version it ever showed.

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}
{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',                 -- or 'timestamp'
    check_cols=['city', 'email']      -- track changes to these
) }}
select * from {{ source('raw', 'customers') }}
{% endsnapshot %}
```

Run `dbt snapshot` on a schedule. dbt automatically maintains **`dbt_valid_from`** and **`dbt_valid_to`** columns: when a tracked column changes, it **closes the old row** (sets `valid_to`) and **inserts a new version**. That's SCD2 — the exact history-tracking you built by hand with a Delta `MERGE` in [Project 1](../11_Projects/02_Project_1_Batch_Medallion_Pipeline.md), here in a few lines of config.

**Two strategies:**
- **`timestamp`** — use a reliable `updated_at` column from the source (preferred when it exists).
- **`check`** — compare `check_cols` values run-to-run (when there's no trustworthy timestamp).

---

## Seeds — small static data as version-controlled tables

A **seed** is a small CSV in your repo that dbt loads into the warehouse as a table via `dbt seed`. Perfect for **static lookup/reference data** you want in version control:

```
seeds/country_codes.csv     →   loaded as a `country_codes` table
seeds/status_mappings.csv   →   used in models via {{ ref('status_mappings') }}
```

Use seeds for **small, rarely-changing** data (country codes, category mappings, holiday calendars) — **not** for loading real source data (that's the EL tool's job). Once seeded, reference it like any model with `ref()`.

---

## Macros — reusable SQL with Jinja (DRY)

dbt SQL is templated with **Jinja** (`{{ }}` / `{% %}`), which you've already seen in `ref()` and `config()`. **Macros** are reusable functions you write to eliminate copy-pasted SQL:

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    round( {{ column_name }} / 100.0, {{ precision }} )
{% endmacro %}
```

```sql
-- use it in any model
select
    order_id,
    {{ cents_to_dollars('amount_cents') }} as amount_usd
from {{ ref('stg_orders') }}
```

Fix the conversion logic once in the macro and every model updates — the DRY principle applied to SQL. Jinja also gives you `if/else`, `for` loops (e.g., pivot over a list of columns), and variables, turning static SQL into **dynamic, generated** SQL.

---

## Packages — don't reinvent the wheel

dbt has a package ecosystem (dbt Hub). Add them in `packages.yml` and `dbt deps`:

| Package | Gives you |
|---|---|
| **dbt-utils** | Battle-tested macros (surrogate keys, pivots, date spines, extra tests) |
| **dbt-expectations** | Great-Expectations-style data tests (ranges, row counts, distributions) |
| **codegen** | Auto-generate model/YAML boilerplate |
| **audit-helper** | Compare two model outputs (great for refactors) |

`dbt_utils.generate_surrogate_key(['a','b'])` alone saves writing hash logic in every dimension — the [surrogate key](../02_Databases/Data_Modeling/03_Dimensional_Modeling.md) pattern, packaged.

---

## Putting it together — the dbt command lifecycle

```bash
dbt deps          # install packages
dbt seed          # load reference CSVs
dbt snapshot      # capture SCD2 history
dbt run           # build models
dbt test          # run data tests
# or just:
dbt build         # seed + run + snapshot + test, all in DAG order
dbt docs generate # build docs + lineage
```

`dbt build` is what you schedule in production (via [orchestration](../12_Orchestration/00_Orchestration_Learning_Path.md) or dbt Cloud).

---

## Interview-grade Q&A

- *How does dbt implement SCD2?* **Snapshots** — `dbt snapshot` tracks changes (timestamp or check strategy) and maintains `dbt_valid_from`/`dbt_valid_to`, closing old rows and inserting new versions automatically.
- *timestamp vs check snapshot strategy?* `timestamp` uses a reliable source `updated_at`; `check` compares specified columns run-to-run when no trustworthy timestamp exists.
- *What are seeds for?* Loading **small, static** reference CSVs from the repo as tables — not for real source data.
- *What are macros?* Reusable Jinja-templated SQL functions that keep transformations DRY (write logic once, use everywhere).
- *Why use packages like dbt-utils?* Reusable, tested macros (surrogate keys, pivots, extra tests) so you don't rewrite common SQL patterns.
- *What does `dbt build` do?* Runs seeds, models, snapshots, and tests together in dependency order — the production command.

---

## Further Learning — Docs & Videos
- dbt snapshots (SCD2): https://docs.getdbt.com/docs/build/snapshots
- dbt seeds: https://docs.getdbt.com/docs/build/seeds
- Jinja & macros: https://docs.getdbt.com/docs/build/jinja-macros
- dbt packages hub: https://hub.getdbt.com/
- Video — dbt snapshots & macros: https://www.youtube.com/results?search_query=dbt+snapshots+macros+tutorial
