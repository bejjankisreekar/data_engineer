# IaaS vs PaaS vs SaaS — Cloud Service Models

[Deployment models](01_Public_Private_Hybrid_Cloud.md) answered *whose computers*. Service models answer a different question: **how much of the stack do you manage vs the provider?**

---

## Analogy: pizza 🍕

| Model | Pizza version | You do | Provider does |
|---|---|---|---|
| **On-premises** | Cook at home | Everything: kitchen, ingredients, cooking, dishes | Nothing |
| **IaaS** | Rented kitchen | Bring ingredients, cook, serve | Kitchen, oven, gas |
| **PaaS** | Pizza delivered | Set the table, choose toppings | Makes and delivers the pizza |
| **SaaS** | Eat at a restaurant | Just show up and eat | Everything |

---

## The stack — who manages what

```
                     On-prem    IaaS      PaaS      SaaS
Application           YOU       YOU       YOU      provider
Data                  YOU       YOU       YOU      you (content)
Runtime / middleware  YOU       YOU     provider   provider
Operating system      YOU       YOU     provider   provider
Virtual machine       YOU     provider  provider   provider
Physical servers      YOU     provider  provider   provider
Networking / building YOU     provider  provider   provider
```

The further right, the less you manage — and the less you can customize.

---

## IaaS — Infrastructure as a Service

You rent **raw building blocks**: virtual machines, disks, networks. You install and manage everything from the OS upward.

- **Azure examples:** Virtual Machines, Virtual Network, managed disks
- **Use when:** you need full control, or you're lifting-and-shifting an existing server to the cloud unchanged
- **Trade-off:** most flexibility, most maintenance (patching, scaling, backups are on you)

## PaaS — Platform as a Service

You rent a **ready platform** and bring only your code/data/configuration. No OS patching, no server management; scaling is a slider or automatic.

- **Azure examples:** Azure SQL Database, [Azure Data Factory](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md), Azure Databricks, Synapse, App Service, [ADLS](../../05_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md)
- **Use when:** you want to build things without babysitting servers — **this is where data engineers live**
- **Trade-off:** less control over the underlying environment

## SaaS — Software as a Service

You rent a **finished application** through a browser. Nothing to build or manage — just use it.

- **Examples:** Outlook/Microsoft 365, Power BI service, Salesforce, Gmail
- **Use when:** the software already exists and you just need to *use* it
- **Trade-off:** least control — you configure, you don't build

---

## Data engineering lens

| Task | Service | Model |
|---|---|---|
| "I installed SQL Server on an Azure VM myself" | Azure VM | IaaS |
| "I use Azure SQL Database; Microsoft patches it" | Azure SQL DB | PaaS |
| "My pipelines run in Data Factory" | ADF | PaaS |
| "My Spark clusters are managed by Databricks" | Azure Databricks | PaaS (with SaaS-like workspace) |
| "Analysts view dashboards in Power BI service" | Power BI | SaaS |

A typical Azure data platform is **almost entirely PaaS** — that's the sweet spot: you focus on pipelines and data, Microsoft runs the machinery. (It's also the Databricks pitch in [Why_Spark_Why_Databricks.md](../../08_Databricks/02_Why_Spark_Why_Databricks.md): Spark-on-IaaS-you-manage vs Spark-as-a-platform.)

---

## Quick memory hook

- **IaaS** — "**I** manage it" (infrastructure rented, everything above is yours)
- **PaaS** — "**P**latform ready, bring your code/data"
- **SaaS** — "**S**imply use the software"

---
---

# Part 2 — Advanced

## The shared responsibility model (the security version of the stack)

"The cloud is secure" is half a sentence. Security **of** the cloud is the provider's job; security **in** the cloud is yours — and the split moves with the service model:

| Responsibility | IaaS | PaaS | SaaS |
|---|---|---|---|
| Physical datacenter, hypervisor | Provider | Provider | Provider |
| OS patching, runtime hardening | **You** | Provider | Provider |
| Network controls (firewalls, private endpoints) | **You** | **Shared** | Provider |
| Identity & access management | **You** | **You** | **You** |
| Data classification, encryption choices | **You** | **You** | **You** |
| Client devices, user behavior | **You** | **You** | **You** |

The last three rows never leave you. Most real cloud breaches are misconfigured *customer* responsibilities (public storage containers, over-broad access keys) — not provider failures.

## Serverless / FaaS — the level beyond PaaS

**Serverless** pushes abstraction further: you don't even provision a platform instance — code/queries run on demand and you pay per execution.

- **FaaS:** Azure Functions — event-driven snippets ("when a file lands in the lake, trigger the pipeline").
- **Serverless analytics:** Synapse serverless SQL pools (pay per TB scanned), Databricks Serverless SQL (instant warehouses).
- Trade-offs: zero idle cost and instant scale vs cold starts, execution time limits, and less environment control.

The full spectrum: `On-prem → IaaS → Containers/K8s → PaaS → Serverless → SaaS` — each step trades control for velocity.

## Identity is the new perimeter (the PaaS glue)

In a PaaS world there are no servers to firewall; **identity** does the isolating:

- **Managed Identity** — an Azure service gets its own Entra ID identity, so ADF can read the data lake with **no stored password at all**. Grant "this factory may read this container," done.
- **RBAC roles** (Storage Blob Data Reader, Contributor…) scoped to the narrowest resource possible.
- Pro habit: **secrets that don't exist can't leak** — prefer managed identities over connection strings, and Key Vault for the unavoidable rest.

## Picking a model: the decision in practice

- Existing app, must move unchanged, odd OS dependencies → **IaaS** (lift-and-shift), modernize later.
- Building new pipelines/apps → **PaaS** by default; drop to IaaS only for a concrete blocker (kernel modules, exotic licensing).
- Commodity capability (email, BI viewing, CRM) → **SaaS**; building it yourself is negative-value work.
- Spiky, event-shaped glue → **serverless**.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Total cost of ownership: the hidden column in the table

IaaS looks cheapest per hour and is usually the most expensive per year, because the missing line items are human: patching, backups, HA design, 3am pages. The honest comparison for "SQL Server on a VM vs Azure SQL Database":

| | VM (IaaS) | Azure SQL DB (PaaS) |
|---|---|---|
| VM/service cost | lower | higher |
| Patching, backups, HA engineering | **you build & staff it** | included |
| Failover tested? | only if you test it | provider's SLA |
| Realistic TCO | higher | lower for most workloads |

Pros justify PaaS with TCO and *time-to-value*, not sticker price — and justify the rare IaaS choice in writing.

## Lock-in: a gradient, not a boolean

Each step right increases switching cost. The mature stance is *managed* lock-in:

- Keep **data** in open formats (Parquet/Delta) on object storage — data is the heaviest thing to move ("data gravity").
- Keep **logic** in portable languages (SQL, PySpark, dbt) rather than proprietary GUIs where feasible.
- Accept lock-in freely where the alternative is running undifferentiated infrastructure yourself. Avoiding all lock-in is itself a costly architecture.

## Classifying the gray areas (favorite interview trap)

- **Databricks** — PaaS at heart (you bring code, they run Spark), with SaaS-like workspace UX, on IaaS VMs *in your subscription* you can see but shouldn't manage. Its serverless SKUs move it further right.
- **Kubernetes (AKS)** — "IaaS+" / CaaS: the control plane is managed, node pools and everything above are yours. Powerful; rarely worth it just for data pipelines when Databricks/ADF exist.
- **Power BI** — SaaS for consumers, but the *datasets/semantic models* inside are engineering artifacts you own: SaaS shell, PaaS-like responsibility within.
- The point pros make: the model describes a **responsibility boundary**, not a product category — always ask "what am I on the hook for?"

## Field-tested gotchas

- PaaS quotas/limits (DTUs, concurrent pipeline runs, function timeouts) replace hardware limits — read the limits page *before* the design review, not during the incident.
- Provider maintenance windows now happen *to* you — design retries; a transient failover is normal PaaS weather, not an outage.
- "Serverless" ≠ "costless": pay-per-TB-scanned engines make an unpartitioned `SELECT *` a billing event ([OLAP gotchas](../../01_Foundations/Fundamentals/02_OLAP_Storage.md)).
- SaaS data still needs your governance: exporting the CRM's data into the lake makes *you* its steward — classification and retention follow the data, not the vendor.

## Interview-grade Q&A

- *Where does the provider's security duty end?* At the layer you configure: they secure the infrastructure; you secure identities, network exposure, and data — in every model.
- *Why is Azure SQL DB "PaaS" if there's still a server name?* The "server" is a logical namespace; OS, patching, HA are Microsoft's. Responsibility, not terminology, defines the model.
- *When is IaaS the right answer in 2026?* Legacy/lift-and-shift, unsupported dependencies, specialized licensing/appliances — a shrinking but real list.
- *Managed identity vs connection string?* Managed identity: no secret to store, rotate, or leak; RBAC-scoped. Connection strings persist only where managed identity isn't supported.

---

## Further Learning — Docs & Videos

**Documentation**
- Cloud service types IaaS/PaaS/SaaS (Azure): https://learn.microsoft.com/en-us/training/modules/describe-cloud-service-types/
- IaaS vs PaaS vs SaaS (Red Hat): https://www.redhat.com/en/topics/cloud-computing/iaas-vs-paas-vs-saas
- Shared responsibility model: https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility

**Videos**
- IaaS vs PaaS vs SaaS explained: https://www.youtube.com/results?search_query=iaas+vs+paas+vs+saas+explained
- Shared responsibility model in cloud: https://www.youtube.com/results?search_query=cloud+shared+responsibility+model+explained
