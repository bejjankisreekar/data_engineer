# 13 — Exam Dump: Practice Set

> **What this is:** 30 extra **exam-style** practice questions with answers and one-line explanations — a "dump"-style rapid drill on top of [10 — Practice Questions](10_Practice_Questions_by_Domain.md), [11 — Most Asked & Tricky](11_Most_Asked_and_Tricky_Exam_Questions.md), and the [12 — Final Mock Exam](12_Final_Mock_Exam.md).
>
> **These are original questions written to the exam's style and objectives — not real/leaked exam items.** Memorizing leaked questions violates Microsoft's exam NDA and won't build understanding. Answer each before revealing.

---

## Domain 1 — Cloud Concepts (~25–30%)

**1.** Replacing up-front server purchases with a monthly cloud bill is a shift from:
<details><summary>Answer</summary>**CapEx → OpEx** — capital expenditure (buy assets) becomes operational expenditure (pay as you consume).</details>

**2.** Automatically adding resources at peak and removing them afterward is called:
<details><summary>Answer</summary>**Elasticity** — scale out/in to match demand. (Scalability is the ability to grow; elasticity is doing it dynamically.)</details>

**3.** In the **IaaS** model, who is responsible for patching the guest operating system?
<details><summary>Answer</summary>The **customer**. Microsoft manages the physical host; you manage OS and up.</details>

**4.** Microsoft 365 and Dynamics 365 are examples of which service model?
<details><summary>Answer</summary>**SaaS** — finished software; the provider manages everything.</details>

**5.** An organization keeps sensitive workloads on-premises but bursts to Azure for peak capacity. This is:
<details><summary>Answer</summary>**Hybrid cloud** — a mix of private (on-prem) and public (Azure).</details>

**6.** Which responsibility **always** remains the customer's, regardless of service model?
<details><summary>Answer</summary>**Data, identities, and accounts** (data classification & accountability). These never transfer to the provider.</details>

**7.** "Pay only for the resources you use" describes which pricing approach?
<details><summary>Answer</summary>**Consumption-based pricing** — no upfront cost, billed by usage.</details>

**8.** The ability of a system to remain operational during a component failure is:
<details><summary>Answer</summary>**High availability**. (Disaster recovery is about *recovering* after a major outage.)</details>

**9.** Which model gives you the **most control** over the underlying operating system and runtime?
<details><summary>Answer</summary>**IaaS** — you manage OS, runtime, and apps; only hardware is abstracted.</details>

**10.** A workload that runs entirely on infrastructure owned and operated by your own company is a:
<details><summary>Answer</summary>**Private cloud**.</details>

---

## Domain 2 — Azure Architecture & Services (~35–40%)

**11.** Two or more physically separate datacenters within a single Azure region are called:
<details><summary>Answer</summary>**Availability Zones** — protect against a datacenter-level failure inside a region.</details>

**12.** A pair of regions 300+ miles apart used for platform-managed replication and staged updates is a:
<details><summary>Answer</summary>**Region pair**.</details>

**13.** The logical container that holds related Azure resources sharing a lifecycle is a:
<details><summary>Answer</summary>**Resource group** — resources live in exactly one; deleting the group deletes them all.</details>

**14.** Which service is the **serverless, event-driven compute** option billed per execution?
<details><summary>Answer</summary>**Azure Functions**.</details>

**15.** You want managed Kubernetes for container orchestration. Which service?
<details><summary>Answer</summary>**Azure Kubernetes Service (AKS)**. (ACI is for simple single containers without orchestration.)</details>

**16.** A dedicated, private, high-throughput connection from on-premises to Azure that does **not** traverse the public internet is:
<details><summary>Answer</summary>**ExpressRoute**. (A VPN Gateway connects over the encrypted public internet.)</details>

**17.** Which Blob **access tier** is cheapest to store but has the highest access cost and latency?
<details><summary>Answer</summary>**Archive** tier — for rarely accessed data (must be rehydrated to read).</details>

**18.** Which redundancy option copies data to a **second region**?
<details><summary>Answer</summary>**GRS / RA-GRS** (Geo-Redundant). LRS and ZRS stay within one region.</details>

**19.** Which is the fully managed, globally distributed **NoSQL** database in Azure?
<details><summary>Answer</summary>**Azure Cosmos DB**.</details>

**20.** Which tool lets you provision resources repeatably using declarative JSON/Bicep templates?
<details><summary>Answer</summary>**Azure Resource Manager (ARM)** templates / **Bicep**.</details>

**21.** You need a private network boundary in Azure to isolate and connect your VMs. You create a:
<details><summary>Answer</summary>**Virtual Network (VNet)**.</details>

**22.** Which compute option is best for hosting a web app **without managing the underlying OS**?
<details><summary>Answer</summary>**Azure App Service** (PaaS).</details>

---

## Domain 3 — Management & Governance (~30–35%)

**23.** Which tool estimates the cost of a **planned** Azure deployment before you build it?
<details><summary>Answer</summary>The **Pricing Calculator**. (The TCO Calculator compares on-prem vs Azure.)</details>

**24.** Which free service gives personalized recommendations across cost, security, reliability, and performance?
<details><summary>Answer</summary>**Azure Advisor**.</details>

**25.** Which service enforces organizational rules, e.g. "only allow resources in West Europe"?
<details><summary>Answer</summary>**Azure Policy**. (RBAC controls *who* can act; Policy controls *what* is allowed.)</details>

**26.** You must prevent anyone from accidentally deleting a critical resource. Apply a:
<details><summary>Answer</summary>**Resource lock** (CanNotDelete or ReadOnly).</details>

**27.** Which grants a user the "Reader" role on a specific resource group?
<details><summary>Answer</summary>**Azure RBAC (Role-Based Access Control)**.</details>

**28.** Requiring a second verification factor at sign-in is:
<details><summary>Answer</summary>**Multi-Factor Authentication (MFA)** — part of Microsoft Entra ID.</details>

**29.** Which service provides a unified security posture and threat protection across Azure resources?
<details><summary>Answer</summary>**Microsoft Defender for Cloud**. (Microsoft Sentinel is the cloud-native SIEM/SOAR.)</details>

**30.** Where do you check whether an **Azure service outage** is affecting your resources right now?
<details><summary>Answer</summary>**Azure Service Health** (in the portal). Advisor is for recommendations; Monitor is for your own metrics/logs.</details>

---

## Score guide

| Score | Readiness |
|---|---|
| 27–30 | Exam-ready — book it |
| 22–26 | Close — review the domains you missed |
| < 22 | Re-study the [study guide](00_AZ900_Study_Guide_Overview.md) before the real exam |

Next: revisit the [Final Mock Exam](12_Final_Mock_Exam.md) under timed conditions.
