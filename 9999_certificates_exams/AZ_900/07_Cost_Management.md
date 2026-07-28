# 07 — Cost Management

> Domain: **Describe Azure management and governance** · Prev: [Identity, Access & Security](06_Identity_Access_Security.md) · Next: [Governance & Compliance](08_Governance_and_Compliance.md)

---

## Factors that affect Azure costs

| Factor | How it affects cost |
|---|---|
| **Resource type & size** | Bigger VM, more storage, higher-tier service = more cost |
| **Consumption/usage** | Pay-as-you-go — the more you use, the more you pay |
| **Region** | Prices vary by region due to local infrastructure/operating costs |
| **Bandwidth (data transfer)** | **Inbound** data transfer is typically free; **outbound** (egress) data transfer, especially across regions, is charged |

**Exam Tip:** Data transfer *into* Azure is generally free; data transfer *out* of Azure (or between regions) is where cost accrues. A question about minimizing cost when moving large data around often hinges on keeping traffic within a region or minimizing egress.

---

## Pricing tools

| Tool | Purpose |
|---|---|
| **Pricing Calculator** | Estimates the cost of **specific Azure services** you plan to configure — pick services, sizes, regions, and see an estimated monthly bill *before* you deploy anything |
| **Total Cost of Ownership (TCO) Calculator** | Compares the cost of running your **current on-premises infrastructure** against running the equivalent workload in Azure — used to build the business case for migrating to the cloud |

**Exam Tip:** These two are a classic confusion pair. **Pricing Calculator** = "what will *this specific new Azure setup* cost?" **TCO Calculator** = "what am I *already* spending on-prem, and how does that compare to Azure?" If the scenario mentions comparing on-prem costs to cloud costs, it's TCO Calculator; if it's about estimating a new Azure deployment, it's Pricing Calculator.

---

## Azure Cost Management + Billing

The built-in tool for **monitoring, allocating, and optimizing** cloud spend after resources are already running:

- View current and historical spend, broken down by subscription, resource group, service, or **tag**.
- Set **budgets** and get alerts when spending approaches or exceeds a threshold.
- Export billing data for reporting.
- Available to everyone with a subscription (not a separate purchase).

## Tags

**Tags** are key-value pairs attached to resources (e.g. `Department: Finance`, `Environment: Production`) used to organize resources for **cost reporting, automation, and governance** — letting you answer "how much did the Finance department spend this month?" even when their resources are spread across multiple resource groups.

## Azure Advisor — cost recommendations

**Azure Advisor** is a free tool that analyzes your resource configuration and usage, then gives personalized recommendations across five categories: **Cost, Reliability, Security, Operational Excellence, and Performance**. In the cost category specifically, it flags things like idle/underutilized VMs that could be resized or shut down, and unused reserved capacity.

---

## Ways to save money: Pricing models

| Model | How it works | Savings vs. Pay-as-you-go |
|---|---|---|
| **Pay-as-you-go** | Standard consumption pricing, no commitment | Baseline (0%) |
| **Reserved Instances** | Commit to using a resource (e.g. a VM size) for **1 or 3 years**, paid upfront or monthly | Up to ~70% cheaper, in exchange for a commitment |
| **Spot Instances/VMs** | Use Azure's **spare, unused capacity** at a steep discount; Azure can **evict/reclaim** the VM with little notice when it needs the capacity back | Up to ~90% cheaper, but not reliable for critical/long-running workloads |
| **Azure Hybrid Benefit** | Use existing on-premises **Windows Server/SQL Server licenses** (with Software Assurance) to reduce the cost of the equivalent Azure resource | Significant savings if you already own eligible licenses |

**Exam Tip:** Reserved Instances = commitment for predictable/steady workloads (cheaper, but you're locked in). Spot Instances = cheapest, but **can be evicted at any time** — never for anything that must stay running or is business-critical; a classic fit is batch processing or fault-tolerant workloads that can pause and resume.

---

## Quick Review

- Cost drivers: resource type/size, consumption, **region**, and **outbound** data transfer (inbound is generally free).
- **Pricing Calculator** = estimate a new Azure deployment. **TCO Calculator** = compare current on-prem cost to Azure.
- **Cost Management + Billing** = monitor/allocate/optimize spend after deployment; supports budgets and alerts.
- **Tags** = key-value metadata for cost reporting and organization.
- **Azure Advisor** = free recommendations across Cost, Reliability, Security, Operational Excellence, Performance.
- **Reserved Instances** = commit 1–3 years for up to ~70% savings. **Spot VMs** = spare capacity, up to ~90% savings, can be evicted anytime. **Azure Hybrid Benefit** = reuse existing on-prem licenses.

---

## Further Learning — Docs & Videos

**Official documentation**
- Azure Cost Management + Billing: https://learn.microsoft.com/en-us/azure/cost-management-billing/cost-management-billing-overview
- Pricing Calculator: https://azure.microsoft.com/en-us/pricing/calculator/
- Total Cost of Ownership (TCO) Calculator: https://azure.microsoft.com/en-us/pricing/tco/calculator/
- Azure Advisor: https://learn.microsoft.com/en-us/azure/advisor/advisor-overview
- Reservations, Spot VMs, Hybrid Benefit: https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/save-compute-costs-reservations

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Azure cost management explained: https://www.youtube.com/results?search_query=azure+cost+management+pricing+calculator+tco+az-900
- Reserved Instances vs Spot vs Hybrid Benefit: https://www.youtube.com/results?search_query=azure+reserved+instances+spot+vm+hybrid+benefit

---

Next: [08 — Governance & Compliance](08_Governance_and_Compliance.md)
