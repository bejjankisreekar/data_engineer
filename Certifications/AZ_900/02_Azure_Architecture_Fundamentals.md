# 02 — Azure Architecture Fundamentals

> Domain: **Describe Azure architecture and services** · Prev: [Cloud Concepts](01_Cloud_Concepts.md) · Next: [Azure Compute Services](03_Azure_Compute_Services.md)

This file covers the physical and organizational structure of Azure — the vocabulary every other Azure topic assumes you already know.

---

## The physical layer: Regions, Region Pairs, Availability Zones

### Region

A **region** is a geographic area containing one or more datacenters, networked together with low latency (e.g. "East US," "Central India," "West Europe"). When you deploy a resource, you choose the region it lives in.

- Not every service is available in every region.
- Some regions are restricted: **sovereign regions** (e.g. Azure Government, Azure China) serve specific compliance/legal needs and are operated separately.

### Region Pairs

Most Azure regions are paired with another region **at least 300 miles away** within the same geography (e.g. East US ↔ West US, North Europe ↔ West Europe). Region pairs exist for:

- **Sequential updates** — Microsoft rolls out platform updates to only one region in a pair at a time, so both are never updated simultaneously.
- **Disaster recovery priority** — if a region-wide outage occurs, the paired region is prioritized for recovery.
- **Data residency** — paired regions usually stay within the same geography/legal jurisdiction, keeping data recovery compliant with residency laws.

### Availability Zones

An **Availability Zone (AZ)** is a physically separate location *within* a region — its own datacenter(s) with independent power, cooling, and networking. A region that supports Availability Zones has **at least 3 separate zones**.

Deploying across zones protects against a datacenter-level failure (fire, power outage) without needing a whole different region. Not all regions support Availability Zones.

```
Geography (e.g. "United States")
 └─ Region (e.g. "East US")
     ├─ Availability Zone 1  (independent power/cooling/network)
     ├─ Availability Zone 2
     └─ Availability Zone 3
```

**Exam Tip:** Region = broad geographic area. Availability Zone = physically separate datacenter *within* a region, used for high availability. Region Pair = two regions matched for disaster recovery and staged updates. All three are commonly mixed up in wrong-answer choices — the key differentiator is *scope*: AZ (within a region) < Region < Region Pair (across two regions).

---

## The organizational hierarchy: Management Groups → Subscriptions → Resource Groups → Resources

Azure organizes everything you deploy into a nested hierarchy, from broadest governance scope down to individual resources:

```
Tenant (Microsoft Entra ID)
 └─ Management Group(s)          ← apply policy/access across many subscriptions
     └─ Subscription(s)           ← billing boundary + access-control boundary
         └─ Resource Group(s)     ← logical container for related resources
             └─ Resource(s)       ← the actual VM, storage account, database, etc.
```

### Resource

The most basic unit — a single instance of a service: one VM, one storage account, one virtual network.

### Resource Group

A **logical container** that holds related resources for a solution — e.g. all the resources for one application (its VM, its database, its storage account) grouped together.

- Every resource **must** belong to exactly one resource group.
- Resources within a group can be in *different regions* — a resource group itself is not tied to one region (though it has a "location" for storing its own metadata).
- **Deleting a resource group deletes everything inside it** — this is the single most tested fact about resource groups.
- Used for applying access control (RBAC) and cost tracking at the "application" level.

### Subscription

A **subscription** is a logical container tied to an Azure account that provides:

1. A **billing boundary** — costs are aggregated and invoiced per subscription.
2. An **access-control boundary** — Azure role assignments and policies can be scoped to a subscription.

Organizations commonly use multiple subscriptions to separate environments (dev vs. prod) or departments (finance vs. engineering), each with its own budget and access rules.

### Management Group

A **management group** sits *above* subscriptions, letting you apply governance (Azure Policy, RBAC) to **many subscriptions at once** instead of configuring each one individually. Management groups can be nested up to **6 levels deep**, plus the root management group at the top, which contains every subscription in the tenant by default.

**Exam Tip:** The ordering **Management Groups → Subscriptions → Resource Groups → Resources** (broadest to narrowest) is asked directly, and questions frequently test "what happens if you apply a policy at the management group level" — the answer is it cascades down to every subscription, resource group, and resource beneath it, unless overridden at a lower scope.

---

## Azure Resource Manager (ARM)

**Azure Resource Manager (ARM)** is the deployment and management layer for Azure — every action taken through the Azure Portal, Azure CLI, Azure PowerShell, or REST API goes *through* ARM, which then talks to the actual resource providers.

```
You (Portal / CLI / PowerShell / REST API / SDK)
        ↓
Azure Resource Manager (ARM)   ← single consistent layer for auth, RBAC, tagging, dependency handling
        ↓
Resource Providers (Microsoft.Compute, Microsoft.Storage, Microsoft.Sql, ...)
```

**Benefits of ARM (a favorite "what does ARM provide" exam question):**

- **Consistent management layer** — the same authentication, RBAC, and policy enforcement apply no matter which tool you used to make the request.
- **Declarative deployment via templates** — you describe the *desired end state* (in JSON, an "ARM template," or the more modern **Bicep** language) and ARM figures out how to get there, rather than scripting each step imperatively.
- **Dependency management** — ARM understands which resources depend on others and deploys/deletes them in the correct order.
- **Tagging** — apply metadata (key-value tags) to resources for organization, cost tracking, and automation, consistently across every resource type.
- **Idempotent, repeatable deployments** — the same template can be redeployed safely to reach the same end state.

More on ARM templates and Bicep: [09 — Monitoring & Management Tools](09_Monitoring_and_Management_Tools.md).

---

## Tenant

A **Microsoft Entra ID tenant** is a dedicated, isolated instance of Entra ID (Azure's identity service) representing one organization. One tenant can contain many subscriptions, but each subscription is associated with exactly one tenant. Identity and access management is covered fully in [06 — Identity, Access & Security](06_Identity_Access_Security.md).

---

## Quick Review

- **Region** = geographic area of datacenters. **Availability Zone** = physically separate datacenter(s) *within* a region (minimum 3 per supporting region), used for high availability. **Region Pair** = two regions ≥300 miles apart, matched for sequential updates and disaster recovery.
- Hierarchy, broadest to narrowest: **Management Group → Subscription → Resource Group → Resource.**
- A **resource** belongs to exactly one **resource group**; deleting the resource group deletes everything inside it.
- A **subscription** = billing boundary + access-control boundary.
- A **management group** applies governance across multiple subscriptions at once; up to 6 levels of nesting plus the root.
- **ARM** is the single consistent deployment/management layer behind every Azure tool (Portal, CLI, PowerShell); it enables declarative templates, dependency ordering, RBAC, and tagging.
- A **tenant** is one organization's dedicated Entra ID instance; it can contain multiple subscriptions.

---

## Further Learning — Docs & Videos

**Official documentation**
- Azure regions, availability zones, region pairs: https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview
- Management groups, subscriptions, resource groups, resources: https://learn.microsoft.com/en-us/azure/governance/management-groups/overview
- Azure Resource Manager (ARM) overview: https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview
- Core architectural components module: https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Regions & availability zones explained: https://www.youtube.com/results?search_query=azure+regions+availability+zones+explained
- Management group / subscription / resource group hierarchy: https://www.youtube.com/results?search_query=azure+management+group+subscription+resource+group+hierarchy

---

Next: [03 — Azure Compute Services](03_Azure_Compute_Services.md)
