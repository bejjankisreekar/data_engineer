# 06 — Identity, Access & Security

> Domain: **Describe Azure architecture and services** · Prev: [Storage Services](05_Azure_Storage_Services.md) · Next: [Cost Management](07_Cost_Management.md)

This is one of the densest topics on the exam — expect several questions purely on identity and security concepts.

---

## Microsoft Entra ID (formerly Azure Active Directory)

**Microsoft Entra ID** is Azure's cloud-based **identity and access management** service — it's how users sign in and how applications/services authenticate. Every Azure subscription trusts exactly one Entra ID tenant.

**Exam Tip:** Entra ID is **not** the same as traditional on-premises Active Directory Domain Services (AD DS). AD DS uses domains/OUs and is designed for on-prem networked devices; Entra ID is a cloud identity service built around users, groups, and app registrations, accessed over HTTP/REST — no domain controllers involved. Entra ID does *not* replace AD DS for on-prem device/group policy management, though **Entra Connect** can sync identities between the two in hybrid setups.

---

## Authentication vs. Authorization (a guaranteed exam question)

| | Authentication (AuthN) | Authorization (AuthZ) |
|---|---|---|
| Question it answers | **"Who are you?"** | **"What are you allowed to do?"** |
| Proves | Your identity | Your permissions |
| Example | Signing in with username + password + MFA code | Being granted "Reader" access to a resource group |
| Happens | First | After authentication succeeds |

**Exam Tip:** If a question describes proving *who you are* (password, MFA, biometrics), it's authentication. If it describes *what you can access or do* (roles, permissions), it's authorization. These two words are swapped in wrong-answer options constantly.

---

## Multi-Factor Authentication (MFA)

Requires **two or more** independent verification methods to sign in — typically something you know (password) plus something you have (a phone/authenticator app code) or something you are (biometrics). MFA dramatically reduces the risk of compromised accounts even if a password is stolen.

## Conditional Access

A Microsoft Entra feature that enforces access rules based on **signals/conditions** — e.g. "require MFA if signing in from outside the corporate network," "block sign-in from specific countries," "require a compliant device." It's *if-this-then-that* logic layered on top of authentication.

## Single Sign-On (SSO)

Lets a user sign in **once** and gain access to multiple applications without re-authenticating for each one — reduces password fatigue and the number of credentials floating around.

---

## Role-Based Access Control (RBAC)

**RBAC** controls **who can do what to which Azure resources** by assigning **roles** to users/groups/service principals at a specific **scope** (management group, subscription, resource group, or individual resource).

### Built-in roles you must know

| Role | Can do |
|---|---|
| **Owner** | Full access, including managing access for others (assigning roles) |
| **Contributor** | Full access to manage resources, but **cannot** grant access to others |
| **Reader** | View resources only — no changes |
| **User Access Administrator** | Manage user access to Azure resources, but not the resources themselves |

RBAC assignments **inherit downward**: a role granted at the subscription level applies to every resource group and resource beneath it, unless a more specific assignment overrides it at a lower scope.

**Exam Tip:** RBAC controls *actions on resources* (can they start/stop/delete a VM). It is a completely different mechanism from **Azure Policy**, which controls *what configurations resources are allowed to have* (e.g. "only allow VMs of a certain size," "require a specific tag"). This RBAC-vs-Policy distinction is one of the single most tested comparisons on the entire exam — see [08 — Governance & Compliance](08_Governance_and_Compliance.md) for the full comparison table.

---

## Zero Trust model

A security philosophy summarized as **"never trust, always verify."** Instead of assuming anything inside a corporate network is safe, Zero Trust verifies every request explicitly, regardless of where it originates, using the principle of **least privilege access** (grant only the minimum access needed) and assuming breach (design as if an attacker is already inside).

The three guiding principles Microsoft states for Zero Trust:

1. **Verify explicitly** — always authenticate and authorize based on all available signals.
2. **Use least privilege access** — limit access with just-in-time and just-enough-access.
3. **Assume breach** — minimize blast radius, verify end-to-end encryption, use analytics to detect threats.

## Defense in depth

A **layered security strategy** — if one layer is breached, subsequent layers still protect the resource. The classic Microsoft diagram, from outside in:

```
Physical security → Identity & access → Perimeter → Network → Compute → Application → Data
```

Each layer adds a barrier: physical datacenter security, identity/MFA, perimeter (DDoS protection, firewalls), network segmentation (NSGs, VNets), compute hardening (VM patching, endpoint protection), application security (secure coding, WAF), and finally data (encryption, access control) at the core — the actual asset being protected.

**Exam Tip:** Defense in depth's whole point is *no single layer is trusted alone*. A question describing "multiple layers of security controls so that if one fails, others still protect the resource" is describing defense in depth.

---

## Key security services and tools

| Service | What it does |
|---|---|
| **Microsoft Defender for Cloud** | A Cloud Security Posture Management (CSPM) tool — continuously assesses your Azure resources, gives a **Secure Score**, and recommends fixes for vulnerabilities |
| **Microsoft Sentinel** | A cloud-native **SIEM/SOAR** (Security Information and Event Management / Security Orchestration, Automation and Response) — collects security data across your environment, detects threats, and can automate responses |
| **Azure Key Vault** | Securely stores and manages **secrets, encryption keys, and certificates**, so applications never hardcode sensitive values |
| **Azure Firewall** | A managed, cloud-based network security service protecting VNet resources at the network/application layer |
| **DDoS Protection** | Protects Azure resources against Distributed Denial of Service attacks (Basic tier is free and automatic; Standard tier offers more advanced mitigation) |

**Exam Tip:** Defender for Cloud gives you a **Secure Score** and recommendations (posture management); Sentinel is for **detecting and responding to active threats** (SIEM). These are frequently confused — Defender = "how secure am I and what should I fix," Sentinel = "what's actually happening/attacking me right now, and how do I respond."

---

## Quick Review

- **Entra ID** = Azure's cloud identity service; not the same as on-prem Active Directory Domain Services.
- **Authentication** = proving who you are. **Authorization** = what you're allowed to do. Auth happens first, then authZ.
- **MFA** = 2+ verification factors. **Conditional Access** = if-this-then-that access rules. **SSO** = sign in once, access many apps.
- **RBAC** = role assignments (Owner/Contributor/Reader/User Access Administrator) at a scope, controlling actions on resources. RBAC ≠ Azure Policy.
- **Zero Trust** = never trust, always verify; least privilege; assume breach.
- **Defense in depth** = layered security (physical → identity → perimeter → network → compute → application → data).
- **Defender for Cloud** = posture/secure score. **Sentinel** = SIEM/SOAR, active threat detection and response. **Key Vault** = secrets/keys/certificates storage.

---

## Further Learning — Docs & Videos

**Official documentation**
- Microsoft Entra ID (formerly Azure AD): https://learn.microsoft.com/en-us/entra/fundamentals/whatis
- Authentication vs authorization: https://learn.microsoft.com/en-us/entra/identity-platform/authentication-vs-authorization
- Azure RBAC overview: https://learn.microsoft.com/en-us/azure/role-based-access-control/overview
- Zero Trust model: https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-overview
- Defender for Cloud / Sentinel / Key Vault: https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Identity, MFA, Conditional Access, SSO: https://www.youtube.com/results?search_query=azure+entra+id+mfa+conditional+access+sso+az-900
- RBAC vs Azure Policy explained: https://www.youtube.com/results?search_query=azure+rbac+vs+policy+explained

---

Next: [07 — Cost Management](07_Cost_Management.md)
