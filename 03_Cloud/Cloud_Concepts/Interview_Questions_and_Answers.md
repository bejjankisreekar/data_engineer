# 03_Cloud — Interview Questions & Answers

## How to use this file

This folder has two notes covering cloud deployment models and service models — foundational vocabulary for any cloud-based data engineering role. Questions mix THEORY (definitions, comparisons) with PRACTICAL/SCENARIO questions (classifying real services, designing a hybrid architecture, justifying a cost decision). Every answer explains why it's correct, not just what the answer is.

- **[Frequently Asked]** — core concepts almost every interview touches: public/private/hybrid, IaaS/PaaS/SaaS with real examples, the shared responsibility model.
- **[Senior/Experienced]** — deeper Pro-level material: landing zones, FinOps, network posture (private endpoints), TCO comparisons, the lock-in gradient.

---

## Table of Contents

1. [Public, Private & Hybrid Cloud](#1-public-private--hybrid-cloud)
2. [SaaS, PaaS, IaaS](#2-saas-paas-iaas)
3. [Rapid-Fire Round](#rapid-fire-round)

---

## 1. Public, Private & Hybrid Cloud

*(full notes: [01_Public_Private_Hybrid_Cloud.md](01_Public_Private_Hybrid_Cloud.md))*

#### Q1. What's the difference between public, private, and hybrid cloud? **[Frequently Asked]**
*Why interviewers ask this:* One of the most fundamental cloud interview questions, a near-guaranteed opener.
**Answer:** **Public cloud** is infrastructure owned and operated by a provider (Azure, AWS, GCP) and shared among many customers, with each customer's environment isolated — pay-as-you-go, elastic, no maintenance burden. **Private cloud** is cloud-style infrastructure dedicated to a single organization, either on their own premises or hosted privately — full control, but the organization bears the upfront cost and ongoing operations. **Hybrid cloud** connects private and public together, letting data and applications move between them — e.g. sensitive data stays on-prem for compliance while analytics bursts run in the public cloud. This is correct because it distinguishes the three by *who owns the infrastructure and who else shares it*, which is the actual question deployment models answer.

#### Q2. What's the difference between hybrid cloud and multi-cloud? **[Frequently Asked]**
*Why interviewers ask this:* A very commonly confused pair, and a classic "gotcha" wrong-answer trap.
**Answer:** **Hybrid cloud** specifically means public **+** private infrastructure connected together. **Multi-cloud** means using two or more **public** cloud providers together (e.g. Azure and AWS), with no private/on-prem component required for the label to apply. This is correct because it isolates the actual distinguishing factor (private infrastructure involvement) rather than treating "using multiple systems" as sufficient to call something hybrid — a company using only Azure and AWS together is multi-cloud, not hybrid.

#### Q3. Why do large regulated enterprises (banks, healthcare, government) still commonly run hybrid cloud rather than going fully public? **[Frequently Asked]**
*Why interviewers ask this:* Tests whether the candidate understands hybrid cloud's real, persistent business drivers rather than dismissing it as a legacy transitional state.
**Answer:** Four real reasons: **compliance/data residency** requirements (GDPR, RBI, HIPAA-style rules constraining where data may physically live and who may access it); **latency** to on-premises systems that can't be economically or safely moved; **migration inertia** — large legacy estates can't move overnight; and **sunk datacenter investment** that hasn't fully depreciated yet. This is correct because it names concrete, still-current business drivers rather than framing hybrid as purely a temporary stepping stone to "eventually fully public," which is not how most regulated enterprises actually operate.

#### Q4. What is a "landing zone," and why do mature enterprises use one instead of letting engineers create resources directly? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real enterprise cloud-adoption experience, a genuinely senior-level topic.
**Answer:** A landing zone is a pre-built scaffold for cloud adoption: management group hierarchy, subscriptions separated by environment (prod/non-prod), hub-and-spoke networking, Azure Policy guardrails (e.g. "no public IPs on storage"), centralized logging, and infrastructure-as-code (Terraform/Bicep) pipelines for deploying into it. Data platforms specifically live inside a "data landing zone" spoke with private endpoints to storage. This is correct because it describes governance and networking applied *before* any workload is deployed, which is precisely what prevents the ungoverned sprawl that results from engineers clicking "Create Resource" ad hoc in the portal — the reality in any organization mature enough to have this structure.

#### Q5. What network posture should a data platform (storage accounts, warehouses, Databricks) use for security, and why? **[Senior/Experienced]**
*Why interviewers ask this:* Tests concrete, actionable security knowledge beyond generic "use good security practices" answers.
**Answer:** Default-deny: storage accounts and warehouses should sit behind **private endpoints** (a network interface inside your own VNet, so DNS resolves the service to a private IP, never a public one); compute like Databricks should run with **VNet injection / secure cluster connectivity**, keeping it inside your network with no public IPs at all. The result is that the data lake is genuinely unreachable from the public internet even if a credential leaks — defense in depth beyond just password/key hygiene. This is correct because it names the specific mechanisms (private endpoints, VNet injection) that achieve network-level isolation, not just "restrict access," and explains why this matters even beyond credential security.

#### Q6. What is Azure ExpressRoute, and why would a regulated enterprise pay for it instead of a standard VPN Gateway connection? **[Senior/Experienced]**
*Why interviewers ask this:* Tests real hybrid-connectivity knowledge, common in cloud architecture interviews.
**Answer:** ExpressRoute is a private, dedicated physical circuit from an organization's datacenter directly into Azure's edge network — traffic never touches the public internet, unlike a site-to-site VPN, which is an encrypted tunnel that still travels *over* the public internet. ExpressRoute gives predictable latency and bandwidth up to 100 Gbps, which is why most regulated enterprises with strict reliability/compliance requirements require it despite the higher cost, while VPN Gateway remains cheap and fast to set up for smaller or less critical workloads. This is correct because it identifies the actual technical difference (private circuit vs. encrypted-but-public-internet tunnel) that drives the cost/reliability trade-off, not just "ExpressRoute is the enterprise option."

#### Q7. A pipeline doing a lookup-per-row against an on-premises database over a hybrid VPN connection turned a 5-minute job into 5 hours. What happened, and how would you fix it? **[Senior/Experienced]**
*Why interviewers ask this:* A realistic performance-debugging scenario testing understanding of hybrid latency in practice.
**Answer:** Every row-by-row lookup pays the full round-trip network latency of the hybrid connection, and that latency — while individually small — compounds catastrophically across millions of rows. Hybrid connections are simply not designed for chatty, per-row communication patterns. The fix is to **batch or replicate** instead: pull the on-prem data in bulk once (or replicate it into the cloud on a schedule), then perform lookups locally within the cloud environment rather than crossing the hybrid link per row. This is correct because it identifies the actual mechanism (per-row round-trip latency compounding at scale) rather than a vague "the network is slow," and gives the concrete architectural fix (batch/replicate vs. chatty per-row calls).

#### Q8. What are the biggest cloud cost levers for a data platform, in order of impact? **[Frequently Asked]**
*Why interviewers ask this:* A practical FinOps question, increasingly common as cloud spend scrutiny has grown.
**Answer:** In rough order: **turn off idle compute** (an idle interactive cluster or an always-on warehouse sized for peak load is the classic five-figure surprise); **right-size and partition data so queries scan less** (architecture beats discounts — one poorly partitioned table scanned daily can out-cost the entire reservation savings from the next lever); **commitment pricing** (reservations/savings plans, ~30–60% off for steady, predictable workloads); and **spot VMs** (~60–90% off spare capacity, for retryable/stateless batch work — never for anything stateful like a driver node). This is correct because it orders the levers by actual impact rather than listing them arbitrarily — architecture and idle-resource discipline typically dwarf pricing-model optimizations in real bills.

#### Q9. Why is "avoiding all vendor lock-in by going multi-cloud" often a worse strategy than it sounds? **[Senior/Experienced]**
*Why interviewers ask this:* A judgment question testing whether the candidate can push back on an appealing-sounding but often costly strategy — a common senior-level trap question.
**Answer:** Strategic multi-cloud (deliberately abstracting everything to run identically anywhere) usually costs *more* than the lock-in it avoids: it forfeits each cloud's best differentiated services in favor of a lowest-common-denominator subset, and cross-cloud data movement means paying **egress costs twice**. The mature stance most pros actually take is picking a primary cloud, keeping *data* in open formats (Parquet/Delta/Iceberg) so the data itself stays portable even if the surrounding plumbing doesn't, and accepting managed-service lock-in deliberately where it buys real engineering velocity. This is correct because it distinguishes *accidental* multi-cloud (a normal byproduct of acquisitions or team history, which is fine to accommodate) from *strategic* multi-cloud (a deliberate abstraction-everywhere policy, which usually isn't worth its cost) — a nuance that shows real architectural judgment.

---

## 2. SaaS, PaaS, IaaS

*(full notes: [02_SaaS_PaaS_IaaS.md](02_SaaS_PaaS_IaaS.md))*

#### Q10. What's the difference between IaaS, PaaS, and SaaS? **[Frequently Asked]**
*Why interviewers ask this:* One of the most universally asked cloud fundamentals questions.
**Answer:** The three service models describe **how much of the technology stack you manage versus the provider manages**. **IaaS** (Infrastructure as a Service) rents raw building blocks — VMs, disks, networks — and you manage everything from the OS upward (e.g. Azure Virtual Machines). **PaaS** (Platform as a Service) provides a ready platform where you bring only your code/data/configuration, with no OS patching or server management (e.g. Azure SQL Database, App Service, Azure Data Factory). **SaaS** (Software as a Service) is a finished application accessed directly, with nothing to build or manage at all (e.g. Microsoft 365, Power BI service). This is correct because it frames the distinction by *management responsibility*, not just a list of examples — which is what actually determines which model fits a given need.

#### Q11. Classify these as IaaS, PaaS, or SaaS: Azure Virtual Machines, Azure SQL Database, Microsoft 365. **[Frequently Asked]**
*Why interviewers ask this:* Tests the ability to apply the IaaS/PaaS/SaaS framework to real, named Azure services, which is how this concept is actually tested in practice.
**Answer:** **Azure Virtual Machines** = IaaS (you manage the OS, patching, and everything above it). **Azure SQL Database** = PaaS (you manage schema, data, and queries; Microsoft manages the OS, patching, and underlying engine). **Microsoft 365** = SaaS (a finished application you simply use). This is correct because each classification is justified by *what you're responsible for managing*, not the product's name or category alone — the same reasoning applies to classify any unfamiliar service correctly in an interview.

#### Q12. Why is Azure SQL Database considered PaaS when it still has a "server name" you configure, which sounds like infrastructure? **[Senior/Experienced]**
*Why interviewers ask this:* A favorite "gray area" trap question testing whether the candidate understands responsibility boundaries versus surface-level terminology.
**Answer:** The "server" in Azure SQL Database is a **logical namespace**, not a physical or virtual machine you provision, patch, or manage — the underlying OS, patching, and high availability are entirely Microsoft's responsibility. The service model is defined by *actual management responsibility*, not by whether a product's terminology happens to include a word like "server." This is correct because it resolves the apparent contradiction by pointing to the real test (who patches the OS, who handles failover) rather than terminology, which is exactly the kind of gray-area reasoning senior interviews are checking for.

#### Q13. Explain the shared responsibility model, and state which responsibilities never shift to the provider regardless of service model. **[Frequently Asked]**
*Why interviewers ask this:* A very commonly asked cloud security fundamentals question.
**Answer:** Security **of** the cloud (physical datacenter, hypervisor) is always the provider's responsibility; security **in** the cloud shifts progressively to the provider as you move from IaaS to PaaS to SaaS (OS patching and network controls become the provider's job at PaaS and beyond). But three responsibilities **never** shift away from the customer in any model: identity and access management, data classification and encryption choices, and client device/user behavior. This is correct because it names the specific rows that stay constant across all three models — which is also why most real cloud security breaches trace back to misconfigured *customer* responsibilities (public storage containers, over-broad access keys), not provider failures.

#### Q14. What is serverless computing, and how does it relate to PaaS? **[Frequently Asked]**
*Why interviewers ask this:* Tests understanding of serverless as a distinct point on the abstraction spectrum, not just a marketing term.
**Answer:** Serverless pushes abstraction one step further than typical PaaS — you don't even provision a platform instance; code or queries run purely on demand and you pay strictly per execution, with true scale-to-zero when idle. Azure Functions (FaaS) is the canonical example; Synapse serverless SQL pools (pay per TB scanned) extend the same idea to analytics. The full spectrum, in increasing abstraction: on-prem → IaaS → containers/Kubernetes → PaaS → serverless → SaaS. This is correct because it positions serverless precisely on the control/abstraction spectrum rather than treating it as an unrelated fourth category, and gives the specific billing property (per-execution, true scale-to-zero) that distinguishes it from ordinary PaaS.

#### Q15. How should a service like Azure Data Factory authenticate to a storage account in production, and why is that the correct choice? **[Frequently Asked]**
*Why interviewers ask this:* A practical security-hygiene question, extremely common across cloud interviews.
**Answer:** Via **Managed Identity** — the Azure service is given its own Entra ID identity, and access is granted through scoped RBAC roles (e.g. "Storage Blob Data Reader" on a specific container), with **no password or connection string stored anywhere**. This is correct because it removes an entire class of risk: a secret that doesn't exist can't leak, be rotated late, or be pasted into the wrong place — which is why "prefer managed identities over connection strings" is a standing rule rather than a situational recommendation.

#### Q16. Is Databricks IaaS, PaaS, or SaaS? **[Senior/Experienced]**
*Why interviewers ask this:* One of the most common "classify the gray area" trap questions — tests nuanced reasoning rather than a confident wrong answer.
**Answer:** Fundamentally PaaS — you bring code and Databricks runs Spark for you — but with a SaaS-like collaborative workspace experience (notebooks, dashboards) layered on top, running on IaaS-level VMs that exist *in your own Azure subscription*, visible to you but not meant to be managed directly. Its newer serverless SKUs move it further toward the PaaS/serverless end of the spectrum by removing even that VM visibility. This is correct because it doesn't force a single clean label onto a product that genuinely spans the spectrum — the senior-level answer is recognizing that the service model describes a *responsibility boundary*, and asking "what am I actually on the hook for here?" rather than insisting on one category.

#### Q17. When is choosing IaaS still the right call in a modern Azure data platform? **[Senior/Experienced]**
*Why interviewers ask this:* Tests whether the candidate defaults reflexively to PaaS everywhere or actually understands IaaS's remaining legitimate use cases.
**Answer:** IaaS remains correct for: lift-and-shift of an existing application that must move unchanged and has odd OS-level dependencies (kernel modules, legacy drivers); unsupported software dependencies that no managed PaaS offering accommodates; and specialized licensing or appliance requirements. Outside those concrete blockers, PaaS is the default for new work, because it removes patching, backup, and HA engineering the team would otherwise have to build and staff themselves. This is correct because it gives specific, checkable blockers rather than a vague "sometimes IaaS is needed" — a real design review should be able to name which blocker applies before choosing IaaS.

#### Q18. Why does IaaS often end up costing *more* over a year than the equivalent PaaS option, even though its hourly rate looks cheaper? **[Senior/Experienced]**
*Why interviewers ask this:* Tests total-cost-of-ownership thinking rather than sticker-price comparison, a genuinely senior distinction.
**Answer:** The IaaS hourly VM cost is lower, but it excludes the human cost of patching, backups, and high-availability engineering — all of which are included in a PaaS offering's price. A team running "SQL Server on a VM" must build and staff its own patching cadence, backup strategy, and failover testing (and a failover is only as good as the last time it was actually tested), whereas Azure SQL Database includes all of that under the provider's SLA. This is correct because it identifies the specific hidden line items (patching, backup, HA engineering, tested failover) that the sticker-price comparison omits — the honest total-cost-of-ownership argument for PaaS, not just "it's more convenient."

---

## Rapid-Fire Round

- Q: Public cloud — shared or dedicated infrastructure? — A: Shared (multi-tenant), provider-owned.
- Q: Private cloud — shared or dedicated? — A: Dedicated to one organization.
- Q: Hybrid cloud = public + what? — A: Private, connected together.
- Q: Multi-cloud = two or more of what kind of cloud? — A: Public cloud providers.
- Q: VPN Gateway or ExpressRoute — which never touches the public internet? — A: ExpressRoute.
- Q: What Azure networking construct makes a storage account unreachable from the public internet? — A: A private endpoint.
- Q: IaaS, PaaS, or SaaS — where do data engineers spend most of their time? — A: PaaS.
- Q: Azure Virtual Machines — IaaS, PaaS, or SaaS? — A: IaaS.
- Q: Microsoft 365 — IaaS, PaaS, or SaaS? — A: SaaS.
- Q: In the shared responsibility model, what three things are always the customer's job? — A: Identity/access management, data classification/encryption, client device/user behavior.
- Q: What billing property defines true serverless? — A: Pay per execution, with scale-to-zero when idle.
- Q: Managed identity or connection string — which has no secret to leak? — A: Managed identity.
- Q: What's the biggest single cloud cost lever for a data platform? — A: Turning off idle compute.
- Q: Spot VMs are appropriate for what kind of workload? — A: Retryable, stateless batch work — never a stateful driver/primary node.
- Q: What makes strategic (not accidental) multi-cloud often more expensive than the lock-in it avoids? — A: Forfeiting best-of-breed services per cloud, plus paying egress costs twice.

Back to the folder: [03_Cloud notes](.) · Related: [04_Data_Storage Interview Q&A](../../04_Storage_and_Formats/Data_Storage/Interview_Questions_and_Answers.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Cloud computing fundamentals (Azure): https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/
- Cloud models (IBM): https://www.ibm.com/topics/cloud-computing

**Videos**
- Cloud computing interview questions: https://www.youtube.com/results?search_query=cloud+computing+interview+questions+iaas+paas+saas
