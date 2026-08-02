# Project Setup & Prerequisites

## What this note is

Before building any pipeline you need an environment and a clean repo layout. This note gets you a **working, free-tier Azure + Databricks + Git setup** and a **project structure** that looks professional on GitHub. Do this once; all three projects reuse it.

Analogy: this is *mise en place* — a cook sets out every ingredient and tool before turning on the stove. Set up the account, storage, compute, secrets, and repo now, so each project is "just cooking," not "where's the pan?"

---

## The accounts & tools you need (all free to start)

| Thing | What for | Cost |
|---|---|---|
| **Azure free account** | ADLS, ADF, Key Vault, Azure SQL | $200 credit + always-free tiers |
| **Azure Databricks** (trial) or **Community Edition** | Spark compute, notebooks | Trial uses your credit; CE is free (limited) |
| **Power BI Desktop** | The BI/serving layer | Free (Windows app) |
| **Git + GitHub account** | Version control & portfolio | Free |
| **VS Code** | Editing code, ADF/dbt locally | Free |

> Don't have a card for the Azure account? **Databricks Community Edition + local PySpark** covers Projects 1 and 2 conceptually. But a real Azure setup is worth it — the *services* are what interviews ask about.

---

## Step 1 — Create the core Azure resources

Create one **Resource Group** (e.g., `rg-de-projects`) to hold everything, so cleanup is one click. Inside it:

1. **Storage account** with **hierarchical namespace enabled** → this makes it **ADLS Gen2**, not plain Blob. Create containers: `bronze`, `silver`, `gold`, and `raw-landing`.
2. **Azure Databricks workspace** (Standard/Trial).
3. **Azure Key Vault** — to store secrets (never hardcode keys).
4. *(Project 3)* **Azure Data Factory** and an **Azure SQL Database** (Basic tier).

```bash
# Azure CLI equivalent (optional — the portal works too)
az group create -n rg-de-projects -l eastus
az storage account create -n stdeprojects001 -g rg-de-projects \
  --sku Standard_LRS --hns true          # --hns true = ADLS Gen2
```

See [ADLS](../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md) for what the hierarchical namespace buys you.

---

## Step 2 — Connect Databricks to ADLS securely

**Never** paste a storage key into a notebook. The professional pattern:

1. Create a **Microsoft Entra service principal** (app registration) and grant it the **Storage Blob Data Contributor** role on the storage account.
2. Store its secret in **Key Vault**.
3. In Databricks, read it via a **secret scope** (backed by Key Vault) and use **OAuth** to mount/access the lake. On Unity Catalog workspaces, use an **external location + storage credential** instead of mounts.

```python
# Databricks — access ADLS via a secret (no keys in code)
service_credential = dbutils.secrets.get(scope="de-kv", key="sp-secret")
spark.conf.set("fs.azure.account.auth.type.stdeprojects001.dfs.core.windows.net", "OAuth")
# ... OAuth provider config referencing the service principal ...
df = spark.read.parquet("abfss://bronze@stdeprojects001.dfs.core.windows.net/…")
```

This "secret scope + service principal" pattern is itself an interview answer — see [Governance & Security](../05_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md).

---

## Step 3 — Structure the GitHub repo

A recruiter opens your repo README first. Make the layout obvious:

```
my-azure-de-project/
├── README.md                 # architecture diagram + how to run + results
├── data/                     # sample/seed data (small only!)
├── notebooks/
│   ├── 01_bronze_ingest.py
│   ├── 02_silver_clean.py
│   └── 03_gold_model.py
├── src/                      # reusable .py modules (transformations, utils)
├── conf/                     # configs, schema definitions
├── adf/                      # exported ADF pipeline JSON (Project 3)
├── tests/                    # pytest / chispa tests
├── .github/workflows/        # CI (lint + tests)
└── .gitignore                # never commit secrets, .env, data dumps
```

- **`.gitignore` first** — add `*.env`, secrets, and large data before your first commit. Committing a storage key to GitHub is a real, career-embarrassing mistake.
- Commit in **logical steps** with clear messages ([Git workflow](../07_DevOps/Git_GitHub/02_Core_Workflow_Add_Commit_Status_Log.md)).

---

## Step 4 — Pick your data

Good project data is **realistic, joinable, and has a time dimension** (so you can show incremental loads and SCDs):

| Dataset | Why it's good |
|---|---|
| **NYC Taxi trips** | Huge, real, time-series, classic — great for batch + performance stories |
| **Retail/e-commerce (Kaggle Olist, Online Retail)** | Multiple tables → star schema, SCDs, joins |
| **Public APIs (weather, GitHub, stocks)** | Shows API ingestion + incremental pulls |
| **Synthetic events (your own generator)** | Perfect for the streaming project |

Pick one **multi-table retail-style** set for Project 1 (best for modeling) and a **streamable** source for Project 2.

---

## Cleanup discipline (do this every session)

- **Terminate clusters** (or set auto-termination to 10–20 min) — idle compute is the #1 surprise bill.
- **Pause/delete** Azure SQL and ADF when not in use.
- When a project is done, **delete the whole resource group** — one command removes everything.

```bash
az group delete -n rg-de-projects --yes --no-wait
```

This is genuine FinOps behavior, covered in [Cost & Performance](../16_Cost_and_Performance/00_Cost_and_Performance_Learning_Path.md).

---

## Checklist before you start Project 1

- [ ] Resource group + ADLS Gen2 with bronze/silver/gold containers
- [ ] Databricks workspace + a small cluster (auto-terminate on)
- [ ] Key Vault + secret scope wired into Databricks (no keys in code)
- [ ] GitHub repo created with the structure above and a `.gitignore`
- [ ] A dataset downloaded and understood (know the columns and grain)

Next: **[02 — Project 1: Batch Medallion Pipeline](02_Project_1_Batch_Medallion_Pipeline.md)**.

## Further Learning — Docs & Videos
- Databricks secret scopes: https://learn.microsoft.com/azure/databricks/security/secrets/
- Connect Databricks to ADLS: https://learn.microsoft.com/azure/databricks/connect/storage/azure-storage
- Video — Databricks + ADLS setup: https://www.youtube.com/results?search_query=databricks+adls+gen2+service+principal+setup
