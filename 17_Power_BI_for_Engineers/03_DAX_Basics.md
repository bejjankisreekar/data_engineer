# DAX Basics (for Engineers)

## What is DAX, and how much do you need?

**DAX (Data Analysis Expressions)** is the formula language of Power BI (and Analysis Services / Fabric semantic models). As an **engineer**, you don't need to be a DAX wizard — you need enough to **create the core measures your Gold layer implies, verify numbers are correct, and understand why an analyst's total is wrong.** This note is that pragmatic subset.

Analogy: DAX is to Power BI what SQL is to a database — the language that turns stored data into answers. You already think in [SQL](../02_Databases/SQL/01_What_is_SQL.md); DAX is a cousin with one big twist (context, below).

---

## The one distinction that trips everyone: measures vs calculated columns

| | **Calculated column** | **Measure** |
|---|---|---|
| Computed | Row-by-row, **at refresh**, stored in the table | On the fly, **at query time**, per visual |
| Cost | Uses memory (materialized) | Uses CPU when viewed |
| Example | `full_name = [first] & " " & [last]` | `Total Sales = SUM(fact[amount])` |
| Use for | A per-row attribute you filter/group by | An aggregation that responds to slicers |

**Rule:** if it aggregates and should react to filters (revenue, count, average), it's a **measure**. If it's a per-row value you slice by, it *could* be a calculated column — but **better: compute it upstream in Gold** and import it, saving memory. Engineers lean on Gold, not calculated columns.

---

## Context — why DAX feels different from SQL

DAX measures are evaluated inside a **context** — the filters currently applied by the visual (the row's month, the selected region, the slicer). `SUM(fact[amount])` returns *total* sales in a card, but *this month's* sales in a monthly bar chart — **the same measure, different context.** Two kinds:

- **Filter context** — the filters from slicers, rows/columns, and the visual.
- **Row context** — iterating row-by-row (in calculated columns and iterator functions like `SUMX`).

`CALCULATE` is the function that **modifies** filter context — the most important and most confusing DAX function. This context model is *the* conceptual leap; you don't need mastery, but know it exists so wrong totals make sense.

---

## The essential functions

```dax
Total Sales   = SUM(fact_sales[amount])
Order Count   = COUNTROWS(fact_sales)
Avg Order     = DIVIDE([Total Sales], [Order Count])          -- DIVIDE handles /0
Distinct Cust = DISTINCTCOUNT(fact_sales[customer_key])

-- CALCULATE: change the filter context
Sales US      = CALCULATE([Total Sales], dim_region[country] = "US")

-- Time intelligence (needs a marked Date dimension)
Sales YTD     = TOTALYTD([Total Sales], dim_date[date])
Sales LY      = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(dim_date[date]))
YoY %         = DIVIDE([Total Sales] - [Sales LY], [Sales LY])

-- Iterator: row-by-row then aggregate
Revenue       = SUMX(fact_sales, fact_sales[qty] * fact_sales[price])
```

Notes engineers care about:
- **`DIVIDE`** over `/` — returns blank instead of erroring on divide-by-zero.
- **Time intelligence** (`TOTALYTD`, `SAMEPERIODLASTYEAR`) **requires a proper Date dimension** marked in the model ([star schema](02_Semantic_Model_and_Star_Schema.md)) — a modeling job you own.
- **`SUMX`** and other `X` iterators compute per row then aggregate — powerful but heavier; often better pre-computed in Gold.

---

## The engineer's principle: push logic to Gold when you can

Every calculation can live in one of three places; prefer the leftmost that fits:

```
Gold layer (Spark/dbt)  →  Semantic model (calculated column)  →  Measure (DAX)
   cheapest to serve,          materialized, uses memory,           flexible, per-query
   shared by all consumers     report-specific                       report-specific
```

- **Reusable, heavy, or shared** logic (revenue definitions, cleaned attributes) → compute in **Gold** so every consumer gets it consistently.
- **Dynamic, filter-responsive** aggregations → **measures** (they *must* be DAX to react to slicers).

This division keeps the semantic model light and the business logic **single-sourced** — a governance win ([data quality/consistency](../05_Data_Engineering/Data_Quality/01_Data_Quality_Fundamentals.md)).

---

## Interview-grade Q&A

- *Measure vs calculated column?* A measure computes at query time responding to filter context (aggregations like Total Sales); a calculated column computes per row at refresh and is stored (per-row attributes). Prefer measures for aggregations and Gold for per-row attributes.
- *What is filter context?* The set of filters (slicers, rows/columns, visual) under which a measure evaluates — why the same measure shows different values in different visuals.
- *What does CALCULATE do?* Modifies the filter context of a measure (e.g., force country = "US"). The key DAX function.
- *Why use DIVIDE instead of /?* It safely returns blank on divide-by-zero instead of erroring.
- *What does time intelligence require?* A dedicated Date dimension marked as the model's date table.
- *As an engineer, where should calculations live?* Push reusable/heavy/shared logic to Gold; use DAX measures only for dynamic, filter-responsive aggregations.

---

## Further Learning — Docs & Videos
- DAX overview: https://learn.microsoft.com/dax/
- Measures vs calculated columns: https://learn.microsoft.com/power-bi/transform-model/desktop-measures
- CALCULATE & context: https://learn.microsoft.com/dax/calculate-function-dax
- Video — DAX for beginners: https://www.youtube.com/results?search_query=dax+basics+power+bi+measures
