# 03 — Azure Compute Services

> Domain: **Describe Azure architecture and services** · Prev: [Architecture Fundamentals](02_Azure_Architecture_Fundamentals.md) · Next: [Azure Networking Services](04_Azure_Networking_Services.md)

**Compute** is anything that runs your workload — code, applications, containers. This file covers Azure's compute options and, critically, *when to pick which one* — a favorite exam question shape.

---

## Azure Virtual Machines (VMs)

An **IaaS** offering: a full virtual computer running in Azure — you choose the OS (Windows/Linux), size (CPU/RAM/disk), and you're responsible for OS patching, runtime, and everything above it.

- Use when: you need full control over the OS/environment, are migrating an existing on-prem server ("lift and shift"), or need software that requires specific OS-level configuration.
- **Virtual Machine Scale Sets (VMSS)** — a group of **identical, load-balanced VMs** that can automatically scale out (add instances) or in (remove instances) based on demand or a schedule. This is the mechanism behind horizontal scaling for VM-based workloads.

## Azure App Service

A **PaaS** offering for hosting web apps, REST APIs, and mobile app backends. You deploy your code; Azure manages the OS, runtime, and patching underneath.

- Supports multiple languages/frameworks (.NET, Java, Node.js, Python, PHP, and containers).
- **Deployment slots** let you stage a new version (e.g. in a "staging" slot) and swap it into production with near-zero downtime, with an easy rollback by swapping back.
- Built-in autoscaling, load balancing, and continuous deployment integration.
- Use when: you're building a web application and don't want to manage servers/OS/patching yourself.

## Azure Container Instances (ACI)

The **fastest and simplest way to run a single container** in Azure with no orchestration, no VM to manage, and per-second billing. Good for short-lived, isolated tasks (a batch job, a simple API) where you don't need the scale/complexity of Kubernetes.

## Azure Kubernetes Service (AKS)

A **managed Kubernetes** service — Azure operates the Kubernetes control plane (the "brain" that schedules and manages containers) for you; you manage your worker nodes and container workloads. Use when you need to orchestrate **many containers at scale** with features like self-healing, rolling updates, and service discovery — ACI is for one container; AKS is for a whole fleet.

## Azure Functions

A **serverless**, event-driven compute service — you write a single function that runs in response to a trigger (an HTTP request, a timer, a new file, a queue message), and Azure handles all scaling and infrastructure. On the **Consumption plan**, you pay only for actual execution time and number of executions — nothing while idle.

- Use when: you have small, event-driven pieces of logic ("glue code") rather than a full always-on application.

## Azure Virtual Desktop

A desktop and app virtualization service running in the cloud — lets users remotely access a full Windows desktop and applications from any device. Relevant mostly as a named service to recognize on the exam, not a deep topic.

---

## Choosing the right compute option (the core exam skill for this section)

| Need | Best fit | Why |
|---|---|---|
| Full control of OS, lift-and-shift a legacy server | **Virtual Machine** | Only option giving OS-level control |
| Host a web app/API without managing servers | **App Service** | PaaS — deploy code, Azure handles the rest |
| Run one container quickly, briefly | **Container Instances (ACI)** | Fastest single-container startup, no orchestration overhead |
| Run many containers with orchestration, scaling, self-healing | **AKS** | Full Kubernetes container orchestration |
| Run small event-triggered code with zero idle cost | **Azure Functions** | True serverless, consumption billing |
| Auto-scale a fleet of identical VMs | **VM Scale Sets** | Horizontal scaling for VM-based workloads |

**Exam Tip:** Scenario questions in this domain almost always describe a *constraint* ("least management overhead," "pay only when code runs," "need full OS access," "quickly run a single container for a batch job") and expect you to match it to the service designed for exactly that constraint. Memorize the "why" column above, not just the names — the exam tests the reasoning, not just recall.

**Exam Tip:** Azure Functions and App Service are both PaaS, but only Functions is described as **serverless** on this exam — the distinguishing feature is per-execution billing with true scale-to-zero, versus App Service which (outside of its own consumption-style plans) is generally always-on.

---

## Quick Review

- **VM** = IaaS, full OS control, you patch and manage it. **VM Scale Sets** = auto-scaling groups of identical VMs.
- **App Service** = PaaS for web apps/APIs; deployment slots enable safe staged rollouts.
- **ACI** = fastest way to run a single container, no orchestration.
- **AKS** = managed Kubernetes for orchestrating many containers at scale.
- **Azure Functions** = serverless, event-triggered, pay-per-execution, scales to zero.
- Compute choice comes down to: how much control do you need vs. how little management overhead do you want?

---

## Further Learning — Docs & Videos

**Official documentation**
- Azure compute services overview: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree
- Azure Virtual Machines: https://learn.microsoft.com/en-us/azure/virtual-machines/overview
- Azure App Service: https://learn.microsoft.com/en-us/azure/app-service/overview
- Azure Functions (serverless): https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview
- Containers — ACI & AKS: https://learn.microsoft.com/en-us/azure/aks/what-is-aks

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Azure compute options explained: https://www.youtube.com/results?search_query=azure+compute+services+vm+app+service+functions+aks
- VMs vs Containers vs Serverless: https://www.youtube.com/results?search_query=azure+vm+vs+containers+vs+serverless

---

Next: [04 — Azure Networking Services](04_Azure_Networking_Services.md)
