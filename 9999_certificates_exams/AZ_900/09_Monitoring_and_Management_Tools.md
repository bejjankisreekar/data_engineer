# 09 — Monitoring & Management Tools

> Domain: **Describe Azure management and governance** · Prev: [Governance & Compliance](08_Governance_and_Compliance.md) · Next: [Practice Questions by Domain](10_Practice_Questions_by_Domain.md)

---

## Ways to interact with and manage Azure

| Tool | What it is | Best for |
|---|---|---|
| **Azure Portal** | Web-based graphical user interface (GUI) | Visual management, exploring services, one-off tasks, beginners |
| **Azure Cloud Shell** | Browser-based command-line shell (choose **Bash** or **PowerShell**), pre-authenticated, no local install needed | Quick scripting/CLI work from any browser, including mobile |
| **Azure CLI** | Cross-platform command-line tool (installed locally), command syntax similar to Bash | Scripting and automation, especially for those comfortable with Bash-style commands, cross-platform (Windows/Linux/Mac) |
| **Azure PowerShell** | Command-line tool using PowerShell **cmdlets** (installed locally or in Cloud Shell) | Scripting and automation, especially for teams already using PowerShell/Windows admin backgrounds |
| **Azure Mobile App** | iOS/Android app | Monitoring resources, checking status, running basic tasks, and receiving alerts on the go |
| **REST API / SDKs** | Programmatic access to Azure Resource Manager | Building custom applications/automation that manage Azure resources directly |

**Exam Tip:** All of these tools ultimately route through **Azure Resource Manager (ARM)** ([covered in file 02](02_Azure_Architecture_Fundamentals.md)) — that's *why* RBAC, tags, and policy apply consistently no matter which tool you use.

---

## Infrastructure as Code: ARM Templates vs. Bicep

| | ARM Templates | Bicep |
|---|---|---|
| Format | JSON | A newer, simpler domain-specific language (DSL) |
| Readability | Verbose | Much more concise and readable |
| Relationship | The underlying format ARM actually deploys | **Compiles down to** an ARM template (JSON) before deployment |
| Both are | **Declarative** — describe the desired end state; Azure figures out how to get there | Same |

**Exam Tip:** Both ARM templates and Bicep are **declarative** (describe *what* you want, not *how* to build it step by step) — this is the key concept the exam tests, more than Bicep-specific syntax. Declarative deployment means the same template can be safely redeployed repeatedly (idempotent) to converge on the same desired state.

---

## Monitoring and health tools (a commonly confused trio)

| Tool | What it tells you | Scope |
|---|---|---|
| **Azure Service Health** | Personalized info about **service issues, planned maintenance, and health advisories** that affect *your specific resources and regions* | Your subscription/resources |
| **Azure Status** | A public, global dashboard of the **current health of all Azure services across all regions** — not personalized | Global, all customers |
| **Azure Advisor** | Personalized **best-practice recommendations** across Cost, Reliability, Security, Operational Excellence, and Performance | Your subscription/resources |
| **Azure Monitor** | Collects, analyzes, and acts on **telemetry** (metrics and logs) from your applications and infrastructure; supports **alerts** and dashboards | Your subscription/resources |
| **Log Analytics** | The query/analysis workspace within Azure Monitor for exploring **log data** using the Kusto Query Language (KQL) | Your subscription/resources |

**Exam Tip:** This is the trio most commonly mixed up:
- **Azure Status** = "is Azure broken right now, globally, for everyone?" (public, not personalized)
- **Azure Service Health** = "is Azure broken right now, specifically affecting *my* resources?" (personalized)
- **Azure Advisor** = "how could *my* resources be configured better?" (recommendations, not incidents)

If a question mentions an outage affecting your specific deployed resources → Service Health. A global outage dashboard with no personalization → Azure Status. Proactive recommendations to improve cost/security/performance → Advisor. Custom metrics, logs, and alerting on your own telemetry → Azure Monitor.

---

## Quick Review

- **Portal** = GUI. **Cloud Shell** = browser-based CLI (Bash or PowerShell), no install. **Azure CLI** / **Azure PowerShell** = locally installed command-line tools. **Mobile App** = monitoring/alerts on the go. All route through ARM.
- **ARM templates** (JSON) and **Bicep** (concise DSL that compiles to ARM JSON) are both **declarative** infrastructure-as-code — describe the end state, not the steps.
- **Azure Status** = public global health dashboard. **Service Health** = personalized health/incidents for your resources. **Advisor** = personalized best-practice recommendations. **Azure Monitor** = telemetry/metrics/logs/alerts on your resources. **Log Analytics** = the KQL query workspace inside Azure Monitor.

You've now covered every topic file. Next: **[10 — Practice Questions by Domain](10_Practice_Questions_by_Domain.md)** to test yourself.
