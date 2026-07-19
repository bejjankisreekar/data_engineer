# 08 — Governance & Compliance

> Domain: **Describe Azure management and governance** · Prev: [Cost Management](07_Cost_Management.md) · Next: [Monitoring & Management Tools](09_Monitoring_and_Management_Tools.md)

---

## Azure Policy

**Azure Policy** creates, assigns, and enforces **rules about what resources are allowed to look like or do** — it's about *configuration compliance*, not user permissions.

- A **policy definition** describes a rule (e.g. "only allow VM sizes from an approved list," "require a `CostCenter` tag on every resource," "only allow deployments to specific regions").
- Policies are assigned at a scope (management group, subscription, resource group) and can have different **effects**: `Deny` (block the non-compliant action), `Audit` (allow it but flag it as non-compliant in reports), `Append` (add a setting automatically, like a missing tag), `Disabled`.
- A **policy initiative** (or "policy set") is a group of related policy definitions bundled together and assigned as one unit — e.g. a whole set of policies for regulatory compliance.
- Azure Policy gives you a **compliance dashboard** showing which resources violate which policies.

## Resource Locks

A **lock** prevents accidental modification or deletion of a resource, resource group, or subscription, regardless of a user's RBAC permissions.

| Lock type | Prevents |
|---|---|
| **CanNotDelete (Delete lock)** | Deletion — the resource can still be read and modified |
| **ReadOnly** | Both modification **and** deletion — the resource can only be read |

Locks apply **regardless of RBAC role** — even an Owner cannot delete a locked resource without first removing the lock. Locks inherit downward from the scope they're applied at (a lock on a resource group protects everything in it).

---

## RBAC vs Azure Policy — the single most tested comparison on the exam

| | RBAC | Azure Policy |
|---|---|---|
| Controls | **Who** can perform **what actions** | **What** resources/configurations are **allowed to exist** |
| Question it answers | "Can this user start/stop/delete this VM?" | "Is this VM the right size, region, and does it have the right tags?" |
| Example | Grant "Contributor" on a resource group | Deny creation of any storage account without HTTPS-only traffic enabled |
| Applies to | Users, groups, service principals | Resources (regardless of who created them) |

**Exam Tip:** If a question is about **permissions/access** ("can Bob create a VM?"), it's RBAC. If it's about **resource configuration/compliance** ("must every storage account use encryption?"), it's Azure Policy. A user can have full RBAC permission to create a resource and still be **blocked by Azure Policy** if the resource doesn't meet the required configuration — the two systems are independent and both apply simultaneously.

**Exam Tip:** Resource Locks are a *third*, separate mechanism from both — locks aren't about permissions (RBAC) or configuration rules (Policy); they're a simple on/off switch preventing delete/modify regardless of anything else.

---

## Azure Blueprints (Blueprints / newer "Template Specs" naming aside — know the concept)

**Azure Blueprints** package together a repeatable set of governance artifacts — **ARM templates, RBAC role assignments, Azure Policy assignments, and resource groups** — so an entire compliant environment can be deployed consistently and repeatably, rather than manually recreating governance setup for every new subscription/project.

Analogy: Azure Policy is a single rule; a Blueprint is a whole starter-kit of resources + rules + permissions bundled together and stamped out consistently.

---

## Microsoft Purview

A unified **data governance** service that helps organizations **discover, classify, and manage** data across their estate (Azure, other clouds, on-premises) — building a map of where sensitive data lives, tracking data lineage, and applying consistent classification/labeling for compliance.

---

## Compliance offerings and trust resources

| Resource | Purpose |
|---|---|
| **Microsoft Trust Center** | Central information hub on Microsoft's security, privacy, and compliance practices |
| **Service Trust Portal** | Provides access to audit reports, compliance guides, and trust documentation (e.g. ISO, SOC, GDPR-related materials) |
| **Compliance offerings** | Azure maintains certifications against a large number of global, regional, and industry-specific standards (ISO 27001, GDPR, HIPAA, FedRAMP, etc.) that customers can rely on for their own compliance obligations |

---

## Quick Review

- **Azure Policy** = enforces rules about resource *configuration/compliance* (effects: Deny, Audit, Append). A **policy initiative** groups multiple policies.
- **Resource Locks**: **CanNotDelete** blocks deletion only; **ReadOnly** blocks modification and deletion. Locks override RBAC — even an Owner is blocked.
- **RBAC vs Policy**: RBAC = who can do what (identity/permissions); Policy = what configurations are allowed (resource compliance). Independent systems, both apply at once.
- **Azure Blueprints** = a repeatable package of ARM templates + RBAC + Policy + resource groups, for consistently deploying a compliant environment.
- **Microsoft Purview** = data governance — discover, classify, and track lineage of data across the estate.
- **Trust Center** / **Service Trust Portal** = where to find Microsoft's compliance certifications and audit reports.

Next: [09 — Monitoring & Management Tools](09_Monitoring_and_Management_Tools.md)
