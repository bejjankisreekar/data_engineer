# 04 — Azure Networking Services

> Domain: **Describe Azure architecture and services** · Prev: [Compute Services](03_Azure_Compute_Services.md) · Next: [Azure Storage Services](05_Azure_Storage_Services.md)

---

## Virtual Network (VNet)

An **Azure Virtual Network (VNet)** is your own private, isolated network inside Azure — the cloud version of a network in your own datacenter. Resources inside a VNet (VMs, etc.) can communicate securely with each other, the internet, and on-premises networks.

- A VNet is divided into **subnets** — smaller segments used to organize and isolate groups of resources (e.g. a "web" subnet, a "database" subnet).
- **VNet Peering** connects two VNets so resources in each can communicate as if they were on the same network — traffic stays on Microsoft's backbone network, never touching the public internet.

## Connecting to Azure from outside: VPN Gateway vs ExpressRoute

Both connect an on-premises network to Azure, but very differently:

| | VPN Gateway | ExpressRoute |
|---|---|---|
| Connection type | Encrypted tunnel **over the public internet** | **Private, dedicated connection** — never touches the public internet |
| Setup | Fast to set up | Requires a connectivity provider, slower to provision |
| Bandwidth/reliability | Variable (internet-dependent) | Consistent, high bandwidth, predictable latency (up to 100 Gbps) |
| Cost | Lower | Higher |
| Typical use | Smaller workloads, dev/test, quick setup | Mission-critical, high-throughput, regulated/enterprise workloads |

**Exam Tip:** This comparison is one of the most frequently tested pairs in the whole exam. The single word to remember: ExpressRoute = **private**, does **not** traverse the public internet. VPN Gateway = encrypted, but still travels **over** the public internet.

## Load balancing traffic: four different services (commonly confused)

| Service | OSI Layer | What it does | Use when |
|---|---|---|---|
| **Azure Load Balancer** | Layer 4 (transport — TCP/UDP) | Distributes traffic across VMs/resources within a region based on IP and port | High-performance, low-latency load balancing of non-HTTP or simple traffic |
| **Application Gateway** | Layer 7 (application — HTTP/HTTPS) | Load balances *web* traffic, can route based on URL path, includes a built-in **Web Application Firewall (WAF)** | Web application traffic needing content-based routing or WAF protection |
| **Azure Traffic Manager** | DNS-level | Routes traffic across **different Azure regions** based on DNS, before the request even reaches Azure | Global load balancing / directing users to the nearest or healthiest region |
| **Azure Front Door** | Layer 7, global | Global entry point for web apps combining CDN-like edge routing, load balancing, and WAF | Global-scale web applications needing both performance and security at the edge |

**Exam Tip:** Load Balancer = regional, Layer 4. Application Gateway = regional, Layer 7 (web-aware, has WAF). Traffic Manager = global, DNS-based routing (doesn't see the actual traffic, just directs). Front Door = global, Layer 7, combines routing + acceleration + WAF. Questions naming "WAF" point to Application Gateway or Front Door; questions naming "across multiple regions" point to Traffic Manager or Front Door, not Load Balancer.

## Azure DNS

A hosting service for **DNS domains**, managed using the same tools, APIs, and billing as other Azure resources — translates domain names to IP addresses.

## Content Delivery Network (CDN)

A distributed network of servers ("edge nodes" or "points of presence") that **caches content close to users geographically**, reducing latency for static content (images, video, scripts) by serving it from a nearby location instead of the origin server every time.

## Network Security Group (NSG)

A basic **firewall** for a VNet or subnet — a set of allow/deny rules based on source/destination IP, port, and protocol, controlling inbound and outbound traffic. This is Azure's most fundamental network-level access control, distinct from identity-based access control (RBAC — see [06](06_Identity_Access_Security.md)).

---

## Quick Review

- **VNet** = your private network in Azure, divided into subnets. **VNet Peering** connects two VNets over Microsoft's backbone (never the public internet).
- **VPN Gateway** = encrypted connection over the public internet. **ExpressRoute** = private dedicated connection that never touches the public internet — higher cost, higher reliability.
- **Load Balancer** = Layer 4, regional. **Application Gateway** = Layer 7, regional, web-aware, has WAF. **Traffic Manager** = DNS-based, global. **Front Door** = Layer 7, global, routing + acceleration + WAF.
- **Azure DNS** hosts DNS domains. **CDN** caches static content at edge locations close to users.
- **NSG** = basic allow/deny firewall rules at the network level.

---

## Further Learning — Docs & Videos

**Official documentation**
- Azure Virtual Network (VNet): https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview
- VNet peering: https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview
- VPN Gateway vs ExpressRoute: https://learn.microsoft.com/en-us/azure/expressroute/expressroute-introduction
- Load balancing options (LB / App Gateway / Front Door / Traffic Manager): https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview
- Network Security Groups (NSG): https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Azure networking fundamentals: https://www.youtube.com/results?search_query=azure+networking+fundamentals+vnet+az-900
- Load Balancer vs App Gateway vs Front Door vs Traffic Manager: https://www.youtube.com/results?search_query=azure+load+balancer+vs+application+gateway+vs+front+door+vs+traffic+manager

---

Next: [05 — Azure Storage Services](05_Azure_Storage_Services.md)
