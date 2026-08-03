# Project 1 — Batch Medallion Pipeline (runnable)

A **working** implementation of the [Project 1 walkthrough](../02_Project_1_Batch_Medallion_Pipeline.md): raw daily CSV files → **Bronze → Silver → Gold** Delta tables → a **star schema** with a **Slowly Changing Dimension (SCD2)**. It runs **locally on your laptop** with PySpark + Delta — no Azure account needed — and maps 1:1 onto Databricks.

> Reading the walkthrough teaches the ideas; running this proves you can build them. This is the difference the [ROADMAP](../../ROADMAP.md) keeps insisting on.

---

## What it demonstrates

| Concept | Where |
|---|---|
| **[Medallion architecture](../../04_Storage_and_Formats/Lakehouse/04_Medallion_Architecture.md)** (Bronze/Silver/Gold) | `src/bronze.py`, `silver.py`, `gold.py` |
| **Explicit schemas** (never `inferSchema`) | `config.py` |
| **Ingestion metadata** + append-only Bronze | `src/bronze.py` |
| **Quarantine** bad rows instead of dropping | `src/silver.py` (a negative-amount row on day 2) |
| **Dedupe** on re-sent rows | `src/silver.py` (a duplicated order line on day 2) |
| **Star schema** (fact + dimensions, surrogate keys) | `src/gold.py` |
| **SCD Type 2** via Delta `MERGE` | `src/gold.py` (`build_dim_customer`) |
| **Idempotent rebuilds** | Silver/Gold overwrite from full history each run |
| **Unit tests** for a data CI pipeline | `tests/test_silver.py` |

The two sample batches are designed to trigger the interesting cases: on **2026-08-03**, customer **C001 (Alice)** moves **Seattle → Denver** (SCD2), one order line is **duplicated** (dedupe), and one has a **negative amount** (quarantine).

---

## Prerequisites

- **Python 3.9–3.11**
- **Java 8, 11, or 17** on your PATH (Spark runs on a JVM). Check with `java -version`. If missing, install a JDK (e.g. Temurin) and ensure `JAVA_HOME` is set.

## Setup & run

```bash
cd 11_Projects/project_1_batch_medallion
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run_pipeline.py --show                      # runs both batches, prints Gold
pytest -q                                          # runs the unit tests
```

The first run downloads the Delta jars (a one-time delay). Output Delta tables land under `./lake/` (gitignored). Re-running is safe — the pipeline is idempotent.

---

## Expected result (the part that proves it works)

**`dim_customer` — Alice has two rows (SCD2 history kept):**

| customer_id | city | region | valid_from | valid_to | is_current |
|---|---|---|---|---|---|
| C001 | Seattle | WEST | 2026-08-02 | 2026-08-03 | false |
| C001 | Denver | CENTRAL | 2026-08-03 | *(null)* | true |
| C002 | Austin | SOUTH | 2026-08-02 | *(null)* | true |
| C004 | Boston | EAST | 2026-08-03 | *(null)* | true |

**`fact_sales`** — Alice's **day-1** orders join to her **Seattle** row; her **day-2** order joins to the **Denver** row (the fact is SCD2-aware, matching on the version valid at `order_date`).

**Quarantine** — the negative-amount line `O2003` is routed to `lake/silver/_quarantine/orders`, not silently dropped; the duplicated `O2002` line collapses to one row in Silver.

---

## Layout

```
project_1_batch_medallion/
├── config.py            # paths + explicit schemas (swap paths for abfss:// on Azure)
├── run_pipeline.py      # orchestrates Bronze→Silver→Gold for each batch
├── requirements.txt
├── src/
│   ├── common.py        # Delta-configured local SparkSession
│   ├── bronze.py        # land raw + ingest metadata (append-only)
│   ├── silver.py        # standardize, quarantine, dedupe (idempotent)
│   └── gold.py          # dim_date, dim_product (SCD1), dim_customer (SCD2), fact_sales
├── tests/test_silver.py # pytest/chispa-style unit tests
└── data/raw/<date>/     # sample daily CSV drops (orders, customers, products)
```

---

## How this maps to Azure / Databricks

| Local here | On Azure |
|---|---|
| `data/raw/<date>/*.csv` | ADLS Gen2 `raw-landing` container (see [ADLS](../../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)) |
| `./lake/bronze,silver,gold` | ADLS containers `bronze/silver/gold` |
| local `SparkSession` (`src/common.py`) | a Databricks cluster ([Clusters](../../08_Databricks/02_Clusters_and_Compute.md)) — delete `common.py`, use the provided `spark` |
| `run_pipeline.py` | a Databricks **Job / Workflow** ([Workflows](../../12_Orchestration/03_Databricks_Workflows.md)) or an ADF-triggered notebook |
| the `.py` stage files | Databricks notebooks or a **Delta Live Tables** pipeline ([DLT](../../08_Databricks/05_Delta_Live_Tables.md)) |
| `pytest` in a shell | the same tests in **CI** ([CI/CD for ADF & Databricks](../../15_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md)) |

Serve the Gold tables to Power BI as described in [Power BI for Engineers](../../17_Power_BI_for_Engineers/00_Power_BI_Learning_Path.md).

---

## Definition of done (matches the walkthrough)

- [x] Bronze/Silver/Gold Delta tables exist and rebuild from raw
- [x] Customer dimension implements SCD2 with a working `MERGE`
- [x] Bad rows are quarantined, not silently dropped
- [x] Duplicate rows are deduped on the business key
- [x] Unit tests cover the Silver transforms
- [ ] Point Power BI at Gold and build the finance dashboard *(your turn — great portfolio finish)*

Next in the walkthrough: **[Project 2 — Streaming Pipeline](../03_Project_2_Streaming_Pipeline.md)**.
