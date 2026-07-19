# 11 — Most Asked & Tricky Exam Questions

> Prev: [Practice Questions by Domain](10_Practice_Questions_by_Domain.md) · Next: [Final Mock Exam](12_Final_Mock_Exam.md)

This file is different from file 10 on purpose: instead of a broad question bank, it isolates the **specific comparisons and traps that candidates consistently report seeing on the real exam** — the pairs of terms that sound similar, the "which is NOT" phrasing, and the small number of hard facts worth memorizing exactly. If you only have one hour left before your exam, spend it here.

---

## The 15 comparison pairs that decide most wrong answers

### 1. RBAC vs Azure Policy

| | RBAC | Azure Policy |
|---|---|---|
| Controls | Who can do what (permissions) | What configurations are allowed (compliance) |
| Scope of the question | "Can Bob delete this VM?" | "Is this VM allowed to be this size / in this region?" |

**Trap:** A user can have full RBAC rights to create a resource and still be *blocked by Policy* if the configuration violates a rule. The two are independent and both apply simultaneously — full notes: [08](08_Governance_and_Compliance.md).

### 2. Resource Lock vs RBAC vs Policy

A **lock** (CanNotDelete / ReadOnly) overrides *everything* — even an Owner cannot bypass a lock without removing it first. It's not a permission system or a compliance system; it's a blunt on/off switch on an action.

### 3. Availability Zone vs Region vs Region Pair

Scope, smallest to largest: **Availability Zone** (datacenter within a region, min. 3 per supporting region) → **Region** (geographic area) → **Region Pair** (two regions ≥300 miles apart, matched for DR and staged updates). Full notes: [02](02_Azure_Architecture_Fundamentals.md).

### 4. LRS vs ZRS vs GRS vs RA-GRS vs GZRS vs RA-GZRS

Memorize the "RA" prefix rule: **any option starting with RA has read access to the secondary region.** Otherwise: L = one datacenter, Z = zones in one region, G = geo (a second paired region), GZ = zones + geo combined. Full table: [05](05_Azure_Storage_Services.md).

### 5. VPN Gateway vs ExpressRoute

**VPN Gateway = encrypted, but still over the public internet. ExpressRoute = private, never touches the public internet.** If the question says "does not use the public internet" or "guaranteed bandwidth," the answer is ExpressRoute.

### 6. Load Balancer vs Application Gateway vs Traffic Manager vs Front Door

- **Load Balancer** = Layer 4, one region, no web-awareness.
- **Application Gateway** = Layer 7, one region, HTTP-aware, has a **WAF**.
- **Traffic Manager** = DNS-level, routes across **multiple regions**, doesn't see the actual traffic.
- **Front Door** = Layer 7, **global**, combines routing + edge acceleration + WAF.

**Trap:** "WAF" in the question → Application Gateway or Front Door, never Load Balancer or Traffic Manager. "Multiple regions" → Traffic Manager or Front Door, never plain Load Balancer.

### 7. IaaS vs PaaS vs SaaS classification

The exam will name a real Azure service and ask you to classify it. Memorize these anchors:

| Definitely IaaS | Definitely PaaS | Definitely SaaS |
|---|---|---|
| Virtual Machines | App Service | Microsoft 365 |
| Virtual Network | Azure SQL Database | Power BI service (not Power BI Desktop) |
| Managed Disks | Azure Functions (serverless) | Dynamics 365 |

### 8. CapEx vs OpEx

**Buy hardware upfront = CapEx. Pay as you go = OpEx.** Cloud computing is fundamentally an OpEx model. A scenario mentioning "no upfront cost," "cancel anytime," "pay only for what's used" = OpEx/consumption-based.

### 9. Scalability vs Elasticity

**Scalability** = the *capability* to add/remove resources (can be manual). **Elasticity** = *automatic* scaling, in *both* directions, in response to real-time demand. If the question says "automatically" and mentions scaling back down, it's elasticity.

### 10. Vertical (scale up/down) vs Horizontal (scale out/in) scaling

**Up/down = resize one instance** (vertical). **Out/in = add/remove instances** (horizontal). VM Scale Sets are the classic horizontal-scaling example.

### 11. Authentication vs Authorization

**Authentication = "who are you" (proving identity).** **Authorization = "what can you do" (permissions).** AuthN always happens before AuthZ.

### 12. Azure Status vs Azure Service Health vs Azure Advisor

- **Azure Status** = public, global, not personalized ("is Azure down for everyone?").
- **Service Health** = personalized to *your* resources ("is Azure down for *me*?").
- **Advisor** = personalized *recommendations*, not incidents ("how could I do this better?").

### 13. Pricing Calculator vs TCO Calculator

**Pricing Calculator** = estimate a *new* Azure deployment's cost. **TCO Calculator** = compare *existing on-premises* spend against running the same workload in Azure. If the scenario mentions "current on-premises costs," it's TCO.

### 14. Reserved Instances vs Spot Instances vs Pay-as-you-go

**Reserved** = commit 1–3 years, up to ~70% off, for steady/predictable workloads. **Spot** = up to ~90% off, uses spare capacity, **can be evicted anytime** — never for critical/always-on workloads. **Pay-as-you-go** = full price, no commitment, maximum flexibility.

### 15. Hybrid cloud vs Multi-cloud

**Hybrid** = public **+** private, connected. **Multi-cloud** = two or more **public** providers (e.g. Azure + AWS). "Multiple clouds" alone doesn't imply private infrastructure — don't default to "hybrid" just because two systems are mentioned.

---

## Frequently reported real-exam question themes

These aren't verbatim exam questions (which would violate Microsoft's NDA), but they represent the *shape* of question repeatedly reported by candidates as appearing on the real exam — practice recognizing this shape:

- **"A company needs X while minimizing Y — which service/option?"** (a scenario with a specific constraint — cost, management overhead, uptime, compliance — and you must match the constraint to the right service, not just recognize the service exists).
- **"Which of the following is an example of [IaaS/PaaS/SaaS/deployment model]?"** — direct classification of a named, real Azure service.
- **"Which of the following is NOT true about [X]?"** — read every option carefully; three will be true facts and one false one, and skimming causes you to pick a true statement by mistake.
- **Drag-and-drop / matching** — matching a list of terms (e.g. Region, Availability Zone, Resource Group) to their correct definitions, or ordering the management hierarchy correctly.
- **"Which tool would you use to..."** — a task description mapped to the *one* correct tool among several plausible-sounding distractors (this is where the comparison pairs above come from).
- **Yes/No or True/False statement sets** within a single scenario ("For each statement, select Yes if true, No if false") — these often test 2–3 closely related facts about the *same* scenario, so getting the scenario's core fact right early carries through the whole set.

---

## Numbers worth knowing cold

| Fact | Value |
|---|---|
| Minimum Availability Zones in a region that supports them | 3 |
| Typical minimum distance between paired regions | 300 miles |
| Maximum management group nesting depth (below the root) | 6 levels |
| Minimum retention before moving to Cool tier is cost-effective | ~30 days |
| Minimum retention before moving to Archive tier is cost-effective | ~180 days |
| AZ-900 passing score | 700 / 1000 |
| AZ-900 exam duration | 85 minutes |
| Commonly cited SLA: single VM on Premium SSD (no redundancy) | 99.9% |
| Commonly cited SLA: VMs in an Availability Set | 99.95% |
| Commonly cited SLA: VMs across 2+ Availability Zones | 99.99% |

**Exam Tip on SLA figures:** you're very unlikely to need an exact SLA percentage memorized to the decimal — but you *are* likely to be asked to **rank** configurations by expected availability (single VM < Availability Set < Availability Zones), and the *pattern* — more redundancy/spread = higher guaranteed uptime — is the actual tested concept.

---

## Rapid-Fire True/False Round

- T/F: Deleting a resource group only deletes the resource group itself, not the resources inside it. — **False.** Everything inside is deleted too.
- T/F: ExpressRoute traffic travels over the public internet. — **False.** That's VPN Gateway; ExpressRoute is private.
- T/F: A Spot VM is guaranteed to keep running until you manually stop it. — **False.** Azure can evict it with little notice.
- T/F: Elasticity means resources scale automatically in both directions. — **True.**
- T/F: RBAC and Azure Policy are the same feature. — **False.** RBAC = permissions; Policy = configuration compliance.
- T/F: Azure Functions is an example of serverless computing. — **True.**
- T/F: A management group can contain other management groups. — **True**, up to 6 levels deep below the root.
- T/F: Archive tier data can be read instantly with no delay. — **False.** It must be rehydrated first, which can take hours.
- T/F: Multi-cloud always includes an on-premises component. — **False.** Multi-cloud means 2+ public clouds; on-prem involvement would make it hybrid as well, but isn't required for the multi-cloud label itself.
- T/F: A CanNotDelete lock can still be bypassed by a user with the Owner role. — **False.** Locks override RBAC entirely.
- T/F: ZRS replicates data to a different Azure region. — **False.** ZRS stays within one region, across zones; GRS is the one that replicates to a different region.
- T/F: The TCO Calculator is used to estimate the cost of a brand-new Azure deployment. — **False.** That's the Pricing Calculator; TCO compares existing on-prem cost to Azure.
- T/F: Azure Advisor and Azure Service Health are the same tool. — **False.** Advisor gives recommendations; Service Health reports personalized incidents.
- T/F: Authentication happens before authorization. — **True.**
- T/F: A Reserved Instance requires a 1- or 3-year commitment. — **True.**

---

Next: put it all together under real time pressure — **[12 — Final Mock Exam](12_Final_Mock_Exam.md)**.
