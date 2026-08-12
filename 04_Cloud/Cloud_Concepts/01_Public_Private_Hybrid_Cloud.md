# Public, Private & Hybrid Cloud

## First: what is "the cloud"?

The cloud is **someone else's computers, rented over the internet, paid for by usage**. Instead of buying servers, racking them in your own building, and maintaining them, you rent compute/storage/services from a provider and give them back when done.

The **deployment models** — public, private, hybrid — answer one question: **whose computers are they, and who else uses them?**

---

## Analogy: where do you live?

- **Public cloud = an apartment building.** You rent a flat; the builder owns and maintains the building; thousands of other tenants live in the same building (securely separated). Cheap, instant, zero maintenance for you.
- **Private cloud = your own house.** Built for you alone, fully under your control — and fully your cost and your maintenance.
- **Hybrid cloud = a house + a rented office.** You keep some things at home (private) and use rented space for the rest (public), with a road connecting the two.

---

## Public cloud

Infrastructure owned and operated by a provider — **Azure, AWS, Google Cloud** — and shared by many customers ("multi-tenant"), with each customer's environment isolated.

**Strengths**
- **Pay-as-you-go** — no upfront hardware cost (OpEx instead of CapEx)
- **Elastic** — scale from 1 to 1,000 machines in minutes, scale back down after
- **Global** — data centers worldwide
- **No maintenance** — provider handles hardware, power, cooling, physical security
- Huge catalog of ready services (databases, [data lakes](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md), Databricks, AI)

**Weaknesses**
- Less control over the underlying infrastructure
- Some industries/regulations restrict where data may live
- Costs can run away if unmanaged (idle clusters!)

---

## Private cloud

Cloud-style infrastructure (self-service, virtualized, automated) used by **one organization only** — either in its own data center or hosted dedicated by a provider.

**Strengths**
- Maximum **control** and customization
- Easier to satisfy strict **regulatory/data-residency** rules (banks, defense, government)
- Predictable performance — no noisy neighbors

**Weaknesses**
- Huge **upfront cost** (CapEx) and ongoing ops staff
- You buy for *peak* load, so hardware sits idle most of the time
- Scaling means purchasing and installing hardware — weeks, not minutes

---

## Hybrid cloud

**Private + public connected together**, letting data and applications move between them.

Typical patterns:
- Keep **sensitive data on-prem** (compliance), run **analytics burst workloads in public cloud**
- Gradual **migration**: legacy systems stay on-prem while new work goes to Azure
- **Burst to cloud**: normal load runs privately; seasonal spikes overflow into public cloud

Azure's hybrid tooling: Azure Arc, ExpressRoute (private network link), Azure Stack.

> Related term: **multi-cloud** = using two or more *public* clouds (e.g. Azure + AWS). Not the same as hybrid.

---

## Comparison table

| | Public | Private | Hybrid |
|---|---|---|---|
| Owned by | Provider (Azure/AWS/GCP) | Your organization | Both |
| Tenancy | Shared (isolated) | You alone | Mixed |
| Cost model | OpEx, pay-per-use | CapEx + ops staff | Both |
| Scale speed | Minutes | Weeks (buy hardware) | Depends on side |
| Control | Lower | Full | Split |
| Best for | Most workloads, startups→enterprises | Strict compliance, steady predictable load | Regulated orgs modernizing gradually |

---

## Why data engineers care

Modern data platforms are overwhelmingly **public cloud**: ADLS, [Databricks](../../08_Databricks/02_Why_Spark_Why_Databricks.md), Data Factory, Synapse are all public-cloud services. But large enterprises (banks, healthcare, insurance) are often **hybrid** — expect pipelines that pull from on-prem SQL Servers (via self-hosted integration runtimes) into the cloud lake.

Next: *how much of the stack you rent* — [02_SaaS_PaaS_IaaS.md](02_SaaS_PaaS_IaaS.md).

---
---

# Part 2 — Advanced

## Inside a public cloud: regions, zones, and what "3 nines" means

```
Geography (e.g. India)
└── Region (Central India — a metro area with 1+ datacenter campuses)
    └── Availability Zones (3 physically separate campuses: own power/cooling/network)
        └── Datacenters → racks → servers → VMs (your stuff)
```

- **Zonal deployment** — spread replicas across AZs; a building fire is a non-event. Azure's zone-redundant services (ZRS storage, zone-redundant SQL) do this for you.
- **Regional pairs** — Azure pairs regions (Central India ↔ South India) for geo-replication and sequenced platform updates.
- **SLA math** — 99.9% ("three nines") allows ~8.7 hours down/year; 99.99% allows ~52 minutes. Composite systems multiply: two chained 99.9% services ≈ 99.8%. Pros compute the *pipeline's* SLA, not each service's.

## The bill nobody reads: data transfer economics

| Movement | Cost |
|---|---|
| **Ingress** (into the cloud) | Free (they *want* your data — data gravity) |
| Within an AZ | Free |
| Cross-AZ / cross-region | Paid per GB |
| **Egress** (out to internet / another cloud) | The expensive one |

Consequences: replicate compute *to* the data, keep chatty services in one region, and know that "multi-cloud data platform" often really means "pay egress twice." This asymmetry is deliberate lock-in — factor it into architecture choices, not just contracts.

## Hybrid connectivity, concretely

- **Site-to-site VPN** — encrypted tunnel over the public internet. Cheap, ~1 Gbps class, internet-weather-dependent.
- **Azure ExpressRoute** — a private physical circuit from your datacenter into Azure's edge. Predictable latency, up to 100 Gbps, required by most regulated enterprises.
- **Azure Arc** — projects on-prem/other-cloud servers and Kubernetes into Azure's control plane so one governance/policy layer covers both.
- **Self-hosted Integration Runtime** — the data engineer's daily hybrid tool: a small agent installed *inside* the private network that lets [Data Factory](../../06_Data_Engineering/ETL_ELT/02_Azure_Data_Factory.md) reach on-prem SQL Servers without opening inbound firewall holes (it dials *out*).

## Compliance & data residency (why private/hybrid persists)

- **GDPR/RBI/HIPAA-style rules** constrain *where data may physically live* and who may access it. Public clouds answer with region pinning, customer-managed keys (CMK), confidential computing (encrypted-in-use enclaves), and sovereign clouds.
- The subtler issue is **jurisdiction** (e.g. CLOUD Act debates) — which is why some governments and banks keep a private/sovereign layer even when technical objections are solved.

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Landing zones — how enterprises actually adopt public cloud

Nobody serious clicks "Create Resource" ad hoc. Enterprises deploy a **landing zone**: a pre-built scaffold of management groups, subscriptions (prod/non-prod separated), hub-and-spoke networking, Azure Policy guardrails ("no public IPs on storage"), centralized logging, and IaC (Terraform/Bicep) pipelines. Data platforms live inside a **data landing zone** spoke with private endpoints to storage. If you join a mature org, this structure — not the portal — is your reality.

## Network posture for data platforms (the part DEs are quizzed on)

Default-deny is the modern stance:

- Storage accounts and warehouses get **private endpoints** (a NIC inside your VNet) — no public internet exposure; DNS resolves the service to a private IP.
- Compute (Databricks with **VNet injection / secure cluster connectivity**) runs in your network with no public IPs.
- Result: "the data lake" is unreachable from the internet even with a leaked key — defense in depth beyond passwords.

## FinOps — cost as an engineering discipline

The cloud's elasticity cuts both ways; mature teams treat cost like a performance metric:

- **Commitment discounts** — reservations/savings plans (~30–60% off) for steady load; **spot VMs** (~60–90% off, evictable) for retryable batch — perfect for Spark workers, never for the driver.
- **Auto-terminate everything** — an idle interactive cluster is the classic 5-figure surprise.
- **Tag-and-showback** — every resource tagged by team/project; monthly cost per pipeline is a KPI.
- Architecture beats discounts: one poorly partitioned table scanned daily can out-cost the entire reservation savings.

## Multi-cloud: the honest take

- **Accidental multi-cloud** (acquisitions, team preferences) is the norm; **strategic multi-cloud** ("avoid lock-in by abstracting everything") usually costs more than the lock-in it avoids — you forfeit each cloud's best services and pay egress forever.
- What pros actually do: pick a primary cloud, keep **data in open formats** (Parquet/Delta/Iceberg) so *data* is portable even if plumbing isn't, and accept managed-service lock-in where it buys velocity.

## Field-tested gotchas

- "Hybrid" latency kills chatty pipelines: a lookup-per-row against an on-prem DB over VPN turns a 5-minute job into 5 hours. Batch or replicate instead.
- Cross-region DR that's never rehearsed is fiction — schedule failover drills like backups restores: **untested = nonexistent**.
- Region choice is semi-permanent: moving petabytes later costs egress + weeks. Choose with data residency + service availability + AZ support in mind on day one.

## Interview-grade Q&A

- *Region vs availability zone?* Region = metro-area group of datacenters; AZ = independent facility within it. AZs give HA; paired regions give DR.
- *Why is hybrid still common?* Compliance/residency, latency to on-prem systems, migration inertia, and sunk datacenter cost.
- *How does ADF reach an on-prem database securely?* Self-hosted Integration Runtime making outbound connections — no inbound firewall rules.
- *Biggest cloud cost levers for a data platform?* Turn off idle compute, right-size/partition data to scan less, commitment pricing, spot for stateless batch.

---

## Further Learning — Docs & Videos

**Documentation**
- Cloud deployment models (Azure): https://learn.microsoft.com/en-us/training/modules/describe-cloud-service-types/
- Public vs private vs hybrid cloud (IBM): https://www.ibm.com/topics/hybrid-cloud
- What is hybrid cloud? (AWS): https://aws.amazon.com/what-is/hybrid-cloud/

**Videos**
- Public vs private vs hybrid cloud explained: https://www.youtube.com/results?search_query=public+vs+private+vs+hybrid+cloud+explained
