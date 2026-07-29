# 01 — Cloud Concepts

> Domain: **Describe cloud concepts** (25–30% of the exam) · Prev: [Overview](00_AZ900_Study_Guide_Overview.md) · Next: [Azure Architecture Fundamentals](02_Azure_Architecture_Fundamentals.md)

---

## What is cloud computing?

**Cloud computing** is the delivery of computing services — servers, storage, databases, networking, software — over the internet ("the cloud"), from a provider who owns and runs the physical hardware, billed for what you actually use.

Analogy: owning a car (buy it, maintain it, insure it, it depreciates, it sits idle 95% of the time) vs. using a taxi/ride-share (pay only when you ride, someone else maintains and insures the vehicle, you scale from one ride to ten instantly). On-premises IT is the car; cloud computing is the ride-share.

---

## The core benefits of cloud computing (know these cold)

| Benefit | What it means | Exam phrasing to recognize |
|---|---|---|
| **High availability** | The system stays up and reachable, minimizing downtime | "ensures a service remains operational" |
| **Scalability** | The ability to increase/decrease resources to match demand | "handle more load by adding resources" |
| **Elasticity** | Automatically scaling resources up *and back down* as demand changes | "automatically scales in and out" — the *automatic* + *both directions* part is what separates this from plain scalability |
| **Agility** | Quickly develop, test, and deploy — spin up resources in minutes, not weeks | "deploy resources rapidly" |
| **Fault tolerance** | The system keeps working even if a component fails | "continues operating despite a failure" |
| **Disaster recovery (DR)** | The ability to restore business function after a major outage/disaster | "recover after a regional outage" |
| **Reliability** | The system consistently performs as expected over time | broader umbrella term covering the above |

**Exam Tip:** *Scalability* vs *elasticity* is a classic confusion. Scalability = the *capability* to scale (could be manual). Elasticity = scaling that happens *automatically* in response to real-time demand, in both directions. If a question mentions "automatically" and "scales back down when demand drops," the answer is elasticity, not scalability alone.

**Exam Tip:** *Vertical scaling* (scale up/down — bigger/smaller VM) vs *horizontal scaling* (scale out/in — more/fewer VM instances). "Scale up" and "scale out" are not interchangeable on this exam — out = horizontal = more instances; up = vertical = bigger instance.

---

## CapEx vs OpEx — the financial model shift

| | CapEx (Capital Expenditure) | OpEx (Operating Expenditure) |
|---|---|---|
| Model | Buy physical infrastructure upfront | Pay for what you use, as you use it |
| Payment | Large upfront cost | Ongoing, predictable operating cost |
| Example | Buying servers for a datacenter | Paying a monthly Azure bill |
| Ownership | You own the hardware (it depreciates) | You own nothing physical |
| Traditional IT | ✅ CapEx-heavy | |
| Cloud computing | | ✅ OpEx-based — the **consumption-based model** |

**Exam Tip:** The exam will describe a scenario and ask whether it represents CapEx or OpEx. "Company buys 50 servers outright" = CapEx. "Company pays monthly for Azure VMs it can cancel any time" = OpEx / consumption-based model. This distinction is one of the most reliably tested facts on the whole exam.

### The consumption-based model

You pay only for the resources you consume, for as long as you consume them — no upfront hardware purchase, no long-term contractual commitment required (though *optional* commitment — Reserved Instances — can lower the price further; see [Cost Management](07_Cost_Management.md)). This is *the* defining economic feature of cloud computing.

### Economies of scale

Because cloud providers operate at massive scale (millions of servers across the world), their per-unit cost of compute/storage/networking is lower than what any single company could achieve running its own datacenter — and providers pass some of that savings on through lower prices.

---

## Cloud service types: IaaS, PaaS, SaaS

The three service models describe **how much of the stack you manage vs. the provider manages**.

Analogy — pizza: **On-premises** = you cook everything from scratch at home (buy the kitchen, ingredients, cook it yourself). **IaaS** = a rented kitchen — you bring your own ingredients and cook, but the oven/gas/space is provided. **PaaS** = pizza delivered to your table — you choose toppings, someone else makes and delivers it. **SaaS** = eating at a restaurant — you just show up and eat.

| Layer managed by YOU | On-prem | IaaS | PaaS | SaaS |
|---|---|---|---|---|
| Applications | ✅ | ✅ | ✅ | Provider |
| Data | ✅ | ✅ | ✅ | You (content only) |
| Runtime | ✅ | ✅ | Provider | Provider |
| Middleware | ✅ | ✅ | Provider | Provider |
| Operating system | ✅ | ✅ | Provider | Provider |
| Virtualization | ✅ | Provider | Provider | Provider |
| Servers (hardware) | ✅ | Provider | Provider | Provider |
| Storage & Networking | ✅ | Provider | Provider | Provider |

| Model | You manage | Azure examples |
|---|---|---|
| **IaaS** (Infrastructure as a Service) | OS upward — most control, most responsibility | Azure Virtual Machines, Virtual Network, managed disks |
| **PaaS** (Platform as a Service) | Just your app/code/data — provider handles OS/runtime | Azure App Service, Azure SQL Database, Azure Functions |
| **SaaS** (Software as a Service) | Just your usage/config/data — nothing to build | Microsoft 365, Power BI service, Outlook, Dynamics 365 |

**Exam Tip:** You will absolutely be asked to classify a named service as IaaS/PaaS/SaaS. Memorize the examples above cold: **VM = IaaS**, **App Service / Azure SQL Database / Azure Functions = PaaS**, **Microsoft 365 / Power BI service = SaaS**. Azure Functions specifically is often called out as **serverless**, a special case of PaaS where you don't manage or think about servers at all — see below.

### Serverless computing

**Serverless** doesn't mean "no servers" — it means *you never provision, manage, or think about servers*. Code runs on demand, scales automatically, and you're billed only for actual execution time (down to the millisecond in some services), not for idle capacity. **Azure Functions** is the flagship example. Serverless is a further-abstracted subset of PaaS.

---

## Cloud deployment models

| Model | Description | When to use |
|---|---|---|
| **Public cloud** | Infrastructure owned and run by the cloud provider, shared (multi-tenant) among customers | Most workloads — lowest cost, no maintenance, elastic scale |
| **Private cloud** | Infrastructure dedicated to a single organization, either on-premises or hosted privately | Strict regulatory/compliance needs, full control required |
| **Hybrid cloud** | A combination of public and private, with connectivity between them | Gradual migration, data residency needs, "burst to cloud" for peak load |
| **Multi-cloud** | Using **two or more public cloud providers** (e.g. Azure + AWS) together | Avoiding vendor lock-in, using best-of-breed services from each, or inherited from mergers/acquisitions |

**Exam Tip:** *Hybrid* = public + private *connected*. *Multi-cloud* = two or more *public* clouds. These are commonly swapped in wrong-answer options — don't confuse "multiple clouds" (multi-cloud) with "cloud + on-prem" (hybrid).

More detail on this exact topic, including Azure's specific hybrid tools (Azure Arc, ExpressRoute, Azure Stack), lives in the main repo's [Public, Private & Hybrid Cloud](../../03_Cloud/Cloud_Concepts/01_Public_Private_Hybrid_Cloud.md) note if you want engineering-level depth beyond what AZ-900 requires.

---

## Quick Review

- Cloud computing = renting compute/storage/networking from a provider, billed by consumption.
- Key benefits: high availability, scalability (manual capability), elasticity (automatic, both directions), agility, fault tolerance, disaster recovery, reliability.
- Vertical scaling = bigger/smaller (scale up/down). Horizontal scaling = more/fewer instances (scale out/in).
- CapEx = buy upfront (traditional IT). OpEx = pay-as-you-go (cloud). Cloud is fundamentally an OpEx, consumption-based model.
- IaaS/PaaS/SaaS = how much of the stack you manage. VM = IaaS. App Service/Azure SQL DB/Functions = PaaS. Microsoft 365 = SaaS.
- Serverless = a PaaS subset where you never manage or provision servers at all; billed per execution.
- Public = shared provider infrastructure. Private = dedicated to one org. Hybrid = public + private connected. Multi-cloud = 2+ public providers.

---

## Further Learning — Docs & Videos

**Official documentation**
- Describe cloud computing (MS Learn module): https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/
- Benefits of cloud computing: https://learn.microsoft.com/en-us/training/modules/describe-benefits-use-cloud-services/
- Cloud service types (IaaS/PaaS/SaaS): https://learn.microsoft.com/en-us/training/modules/describe-cloud-service-types/
- Cloud deployment models: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Cloud concepts (IaaS vs PaaS vs SaaS): https://www.youtube.com/results?search_query=iaas+paas+saas+explained+azure
- CapEx vs OpEx / scaling explained: https://www.youtube.com/results?search_query=az-900+cloud+concepts+capex+opex+scaling

---

Next: [02 — Azure Architecture Fundamentals](02_Azure_Architecture_Fundamentals.md)
