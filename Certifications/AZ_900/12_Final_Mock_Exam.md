# 12 — Final Mock Exam

> Prev: [Most Asked & Tricky Questions](11_Most_Asked_and_Tricky_Exam_Questions.md) · Series home: [Overview](00_AZ900_Study_Guide_Overview.md)

## Instructions — read before starting

This is a **50-question, timed, closed-book simulation** of the real exam. Conditions to replicate:

- **Set a timer for 75 minutes** (slightly tighter than the real 85, to build margin).
- No notes, no searching, no going back to the topic files.
- Answer every question — there's no penalty for a wrong guess, so never leave one blank.
- Mark your answers on paper or in a separate document first; **do not scroll to the Answer Key section until you've finished all 50**, or you'll defeat the purpose of the test.
- Domain weighting is reflected in the section sizes below, matching the real exam's published breakdown (25–30% / 35–40% / 30–35%).

When you're done, jump to **Answer Key & Explanations** at the bottom, grade yourself, and read the **Scoring Guide** to interpret your result.

---

## Section A — Cloud Concepts (14 questions)

**A1.** A startup wants to avoid any upfront investment in physical servers and instead pay only for compute as it grows. Which financial model does this represent?
A. CapEx B. OpEx C. Fixed-cost licensing D. Depreciation-based accounting

**A2.** Which term best describes a cloud system's ability to remain operational and accessible even when a component fails?
A. Elasticity B. High availability C. Agility D. Economies of scale

**A3.** A company automatically adds 10 more application instances during a traffic spike, then automatically removes them an hour later when traffic normalizes. This is an example of:
A. Vertical scaling B. Fault tolerance C. Elasticity D. Disaster recovery

**A4.** Which of the following is an example of Software as a Service (SaaS)?
A. Azure Virtual Machines B. Azure Kubernetes Service C. Microsoft 365 D. Azure Virtual Network

**A5.** A company wants to deploy a database without managing the underlying OS, patching, or backups, but still wants full control over the schema and data. Which service model fits best?
A. IaaS B. PaaS C. SaaS D. On-premises

**A6.** Which cloud deployment model uses infrastructure dedicated entirely to a single organization, whether hosted on-premises or by a third party?
A. Public cloud B. Private cloud C. Hybrid cloud D. Multi-cloud

**A7.** An organization keeps sensitive financial records on its own on-premises servers but bursts analytics workloads into Azure during quarter-end. Which deployment model is this?
A. Public cloud B. Private cloud C. Hybrid cloud D. Multi-cloud

**A8.** Which of the following best defines "economies of scale" in the context of cloud computing?
A. Prices increase as more customers use the service B. Large-scale cloud provider operations lower the per-unit cost of resources compared to individual companies self-hosting C. Every customer pays an identical flat fee D. Scaling a VM up always doubles its cost

**A9.** Resizing a database from 4 vCores to 2 vCores because load has decreased is an example of:
A. Scaling in B. Scaling down C. Elasticity only D. Disaster recovery

**A10.** Which of these is NOT one of Azure's three core cloud service models?
A. IaaS B. PaaS C. SaaS D. DBaaS

**A11.** A company needs to run a small piece of code only when a new file is uploaded, and wants to pay nothing when no files are being uploaded. Which concept does this best describe?
A. Reserved capacity B. Serverless computing C. Virtual Machine Scale Sets D. Hybrid cloud

**A12.** Which statement about the consumption-based pricing model is FALSE?
A. You pay only for what you use B. There is no need to predict capacity years in advance C. It always requires a multi-year contract D. It shifts spending from CapEx toward OpEx

**A13.** A company wants to use Azure for new application development while also using Google Cloud for its data analytics platform, with no on-premises component at all. This is:
A. Hybrid cloud B. Multi-cloud C. Private cloud D. Community cloud

**A14.** Which benefit of the cloud specifically refers to the speed at which a business can develop, test, and deploy new solutions?
A. Reliability B. Agility C. Fault tolerance D. Economies of scale

---

## Section B — Azure Architecture and Services (19 questions)

**B1.** Which Azure construct serves as both a billing boundary and an access-control boundary?
A. Resource group B. Management group C. Subscription D. Tenant

**B2.** A single resource can belong to how many resource groups at once?
A. Unlimited B. Exactly one C. Up to three D. Zero — resource groups are optional

**B3.** Which is deployed to allow governance policies to be applied consistently across multiple subscriptions at once?
A. Resource group B. Management group C. Availability Zone D. Resource lock

**B4.** What is the maximum nesting depth for management groups, not counting the root management group?
A. 3 levels B. 6 levels C. 10 levels D. Unlimited

**B5.** Which Azure service is the underlying deployment and management layer behind the Azure Portal, CLI, and PowerShell?
A. Azure Resource Manager B. Azure Active Directory C. Azure Monitor D. Azure Advisor

**B6.** A company needs their VM-based application to survive the failure of an entire datacenter within a region, without deploying to a different region. What should they use?
A. A single VM with Premium SSD B. Virtual Machines distributed across multiple Availability Zones C. LRS storage redundancy D. Azure Front Door

**B7.** Which compute service is best suited for a team that wants to migrate an existing legacy application requiring full control of the Windows Server OS?
A. Azure Functions B. Azure Virtual Machines C. Azure Container Instances D. Azure App Service

**B8.** Which feature of Azure App Service allows a new version of an application to be tested in a separate environment and then swapped into production with minimal downtime?
A. Deployment slots B. VM Scale Sets C. Availability Zones D. Resource locks

**B9.** Which service provides a managed Kubernetes control plane, letting you focus on your worker nodes and containerized workloads rather than managing the Kubernetes master infrastructure?
A. Azure Container Instances B. Azure Kubernetes Service C. Azure App Service D. Azure Virtual Machines

**B10.** Which networking service connects two Azure Virtual Networks so resources communicate as if on the same network, using Microsoft's backbone rather than the public internet?
A. VPN Gateway B. VNet Peering C. ExpressRoute D. Azure Firewall

**B11.** A global retailer needs to route users to whichever Azure region currently has the healthiest and lowest-latency deployment of their application, based on DNS. Which service fits?
A. Azure Load Balancer B. Application Gateway C. Azure Traffic Manager D. Network Security Group

**B12.** Which Azure Storage service would you choose to store millions of unstructured product images for a website?
A. Table Storage B. Queue Storage C. Blob Storage D. Disk Storage

**B13.** Which storage redundancy option provides the LOWEST cost while still protecting against a single disk or server failure?
A. LRS B. GRS C. RA-GRS D. GZRS

**B14.** Data in the Archive access tier can be accessed:
A. Instantly, with no delay B. Only after a rehydration process that can take hours C. Only by Microsoft support D. Only if stored using GRS

**B15.** Which tool is used to migrate a very large volume of data (hundreds of terabytes) to Azure when network bandwidth is severely limited?
A. AzCopy B. Azure Storage Explorer C. Azure Data Box D. Azure Migrate

**B16.** What is the correct relationship between authentication and authorization?
A. Authorization always occurs first B. They occur simultaneously and cannot be separated C. Authentication verifies identity and must succeed before authorization determines access D. Authorization replaces the need for authentication

**B17.** Which built-in RBAC role grants full access to manage resources, including the ability to grant access to other users?
A. Reader B. Contributor C. Owner D. User Access Administrator

**B18.** Which security model is based on the principles "verify explicitly," "use least privilege access," and "assume breach"?
A. Defense in depth B. Zero Trust C. Shared responsibility model D. Role-Based Access Control

**B19.** Which Azure service is a SIEM/SOAR platform used to detect and respond to active security threats across an environment?
A. Microsoft Defender for Cloud B. Microsoft Sentinel C. Azure Key Vault D. Azure Policy

---

## Section C — Azure Management and Governance (17 questions)

**C1.** Which tool compares the cost of an organization's existing on-premises infrastructure against the projected cost of running the same workload in Azure?
A. Pricing Calculator B. TCO Calculator C. Cost Management + Billing D. Azure Advisor

**C2.** Outbound data transfer (egress) from Azure is generally:
A. Always free B. Charged, unlike most inbound data transfer which is generally free C. Only charged on weekends D. Not something Azure ever measures

**C3.** Which pricing option requires a 1- or 3-year commitment in exchange for a significant discount, best suited to steady, predictable workloads?
A. Pay-as-you-go B. Spot Instances C. Reserved Instances D. Azure Hybrid Benefit

**C4.** Which Azure Hybrid Benefit specifically allows you to reduce cost by reusing something you already own?
A. Existing Azure credits B. Existing on-premises Windows Server/SQL Server licenses with Software Assurance C. Existing AWS reserved instances D. Existing third-party support contracts

**C5.** A company wants to prevent modification AND deletion of a critical resource, while still allowing it to be read. Which lock type should they apply?
A. CanNotDelete B. ReadOnly C. Contributor D. Deny Policy

**C6.** Which of these correctly distinguishes Azure Policy from RBAC?
A. Azure Policy governs identity and permissions; RBAC governs resource configuration B. RBAC governs what actions a user can perform; Azure Policy governs what configurations resources are allowed to have C. They are interchangeable terms for the same governance feature D. Azure Policy only applies at the subscription level

**C7.** What does a "policy initiative" represent in Azure Policy?
A. A single, standalone policy rule B. A group of related policy definitions bundled together and assigned as one unit C. A resource lock applied to multiple subscriptions D. A budget alert threshold

**C8.** Which Azure feature packages ARM templates, RBAC role assignments, and Policy assignments to allow consistent, repeatable deployment of a compliant environment?
A. Azure Blueprints B. Azure Advisor C. Microsoft Purview D. Log Analytics

**C9.** Which service is used specifically to discover, classify, and track lineage of sensitive data across an organization's data estate for governance purposes?
A. Azure Monitor B. Microsoft Purview C. Azure Policy D. Cost Management + Billing

**C10.** Which tool provides a public, non-personalized dashboard showing the health of Azure services globally, for all customers?
A. Azure Service Health B. Azure Status C. Azure Advisor D. Azure Monitor

**C11.** Which tool would tell a specific customer that an ongoing Azure incident is currently affecting THEIR deployed resources?
A. Azure Status B. Azure Service Health C. Microsoft Trust Center D. Service Trust Portal

**C12.** Azure Advisor provides personalized recommendations across which five categories?
A. Compute, Storage, Networking, Identity, Cost B. Cost, Reliability, Security, Operational Excellence, Performance C. IaaS, PaaS, SaaS, FaaS, DBaaS D. CapEx, OpEx, TCO, ROI, SLA

**C13.** Which of the following best describes the relationship between Bicep and ARM templates?
A. Bicep is unrelated to ARM and deploys independently B. Bicep is a more concise language that compiles into an ARM template (JSON) before deployment C. ARM templates are being replaced entirely and no longer function D. Bicep only works with PowerShell, never Azure CLI

**C14.** What key property do both ARM templates and Bicep share, which allows the same template to be redeployed safely to reach the same end state?
A. They are imperative B. They are declarative C. They require a GUI D. They can only be used once

**C15.** Which browser-based tool provides a pre-authenticated command-line shell (Bash or PowerShell) with no local installation required?
A. Azure CLI B. Azure Cloud Shell C. Azure PowerShell D. Azure Mobile App

**C16.** A company wants to track and report Azure spend by project, even though each project's resources are scattered across several resource groups. What is the best mechanism?
A. Resource locks B. Tags C. Region selection D. Availability Zones

**C17.** Which tool would you use to browse and manage the contents of a storage account through a graphical desktop application?
A. AzCopy B. Azure Data Box C. Azure Storage Explorer D. Azure Migrate

---

## Answer Key & Explanations

### Section A
1. **B** — Consumption-based, pay-as-you-go = OpEx, the defining shift cloud computing enables.
2. **B** — High availability = staying operational/accessible despite failures.
3. **C** — Automatic scaling in both directions based on demand = elasticity, not just scalability.
4. **C** — Microsoft 365 is finished software you use directly = SaaS. The other three are IaaS/PaaS building blocks.
5. **B** — Full control of schema/data but no OS/patching/backup management = PaaS (e.g. Azure SQL Database).
6. **B** — Dedicated to one organization, on-prem or hosted = private cloud by definition.
7. **C** — On-prem + public cloud connected = hybrid, regardless of which workload runs where.
8. **B** — Economies of scale = provider's massive scale lowers per-unit cost versus self-hosting.
9. **B** — Reducing a single instance's size is vertical scaling ("scale down"); scaling in/out would mean changing instance *count*.
10. **D** — "DBaaS" is not one of the three core Azure service models tested (IaaS/PaaS/SaaS).
11. **B** — Event-triggered code, pay only when it runs = serverless (Azure Functions).
12. **C** — FALSE statement to find: consumption-based pricing specifically does NOT require a multi-year contract — that's what Reserved Instances add optionally.
13. **B** — Two public clouds (Azure + GCP), no on-prem component = multi-cloud, not hybrid.
14. **B** — Agility = speed of developing, testing, and deploying.

### Section B
1. **C** — Subscription = billing boundary + access-control boundary.
2. **B** — A resource belongs to exactly one resource group.
3. **B** — Management groups apply governance across multiple subscriptions at once.
4. **B** — Six levels of nesting below the root management group.
5. **A** — Azure Resource Manager (ARM) underlies every management tool.
6. **B** — Spreading VMs across Availability Zones protects against a whole-datacenter failure within one region.
7. **B** — Full OS control for a legacy Windows Server app = Virtual Machines (IaaS).
8. **A** — Deployment slots let you stage and then swap a new version into production.
9. **B** — AKS = managed Kubernetes control plane.
10. **B** — VNet Peering connects VNets over Microsoft's backbone network, not the public internet.
11. **C** — DNS-based routing to the healthiest/lowest-latency region = Azure Traffic Manager.
12. **C** — Unstructured object data at scale (images) = Blob Storage.
13. **A** — LRS is the cheapest redundancy tier and still protects against a single disk/server failure within one datacenter.
14. **B** — Archive tier requires rehydration, which can take hours — not instant.
15. **C** — Azure Data Box is for large offline data transfers when bandwidth is limited.
16. **C** — Authentication (identity) must succeed before authorization (permissions) is evaluated.
17. **C** — Owner = full resource management + ability to grant access to others. Contributor cannot grant access.
18. **B** — "Verify explicitly, least privilege, assume breach" are Microsoft's three Zero Trust principles verbatim.
19. **B** — Microsoft Sentinel is the SIEM/SOAR for active threat detection and response.

### Section C
1. **B** — TCO Calculator compares existing on-prem cost to the Azure equivalent.
2. **B** — Outbound (egress) data transfer is charged; inbound is generally free.
3. **C** — Reserved Instances require a 1- or 3-year commitment for a discount, suited to steady workloads.
4. **B** — Azure Hybrid Benefit reuses existing on-prem Windows Server/SQL Server licenses (with Software Assurance).
5. **B** — ReadOnly blocks both modification and deletion; CanNotDelete only blocks deletion.
6. **B** — RBAC = user permissions/actions; Azure Policy = allowed resource configurations.
7. **B** — A policy initiative bundles multiple related policy definitions into one assignable unit.
8. **A** — Azure Blueprints package templates + RBAC + Policy for repeatable compliant environment deployment.
9. **B** — Microsoft Purview handles data discovery, classification, and lineage.
10. **B** — Azure Status is the public, non-personalized global health dashboard.
11. **B** — Azure Service Health is the personalized incident view scoped to your own resources.
12. **B** — Cost, Reliability, Security, Operational Excellence, Performance — Azure Advisor's five categories.
13. **B** — Bicep compiles down to an ARM template (JSON) before deployment.
14. **B** — Both are declarative — they describe desired end state, making redeployment idempotent/safe.
15. **B** — Azure Cloud Shell is the pre-authenticated, browser-based shell requiring no local install.
16. **B** — Tags let you report cost/usage across resources regardless of which resource group holds them.
17. **C** — Azure Storage Explorer is the GUI application for browsing/managing storage account contents.

---

## Scoring Guide

Count your correct answers out of 50.

| Score | Interpretation |
|---|---|
| **45–50** | Exam-ready. Review only the specific questions you missed. |
| **38–44** | Close — re-read the notes files behind your missed questions, then retake this mock exam in 2–3 days. |
| **28–37** | Solid foundation, but gaps remain. Revisit [11 — Most Asked & Tricky Questions](11_Most_Asked_and_Tricky_Exam_Questions.md) fully, then redo file 10's domain practice before retaking this exam. |
| **Below 28** | Go back through files 01–09 in full before attempting another mock — don't sit the real exam yet. |

The real exam's 700/1000 scaled passing score does **not** map 1:1 to "70% of questions" (some questions carry more weight, and a few are unscored pilot questions) — but scoring consistently **38+/50 (76%)** on fresh mock questions is a reasonable readiness signal in practice, since it builds in margin for the scaled scoring and for the mild unfamiliarity of real exam phrasing versus practice questions.

**If you passed this mock comfortably:** book the real exam. Confidence decays if you over-study past the point of diminishing returns — once you're reliably scoring well on fresh questions across all three domains, you're ready.

**Good luck.**

---

## Further Learning — Docs & Videos

**Official resources — final prep & booking**
- Book the AZ-900 exam (Pearson VUE via Microsoft): https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/
- Free official practice assessment (take right before booking): https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment
- Online proctored exam — what to expect: https://learn.microsoft.com/en-us/credentials/certifications/online-exams
- Exam sandbox (try the exam interface): https://aka.ms/examdemo

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- AZ-900 full practice exam (timed): https://www.youtube.com/results?search_query=az-900+full+practice+exam+timed
- AZ-900 last-minute revision / exam cram: https://www.youtube.com/results?search_query=az-900+last+minute+revision+exam+cram
