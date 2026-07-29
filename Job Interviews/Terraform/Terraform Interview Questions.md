# Terraform — Interview Questions & Answers

## Overview
Terraform is a declarative Infrastructure-as-Code tool to provision Azure resources (storage, Databricks, ADF, networking) reproducibly across environments. DE interviews test state, modules, and the plan/apply workflow.

Difficulty: 🟢 · 🟡 · 🔴 · Confidence: ★.

---

## Interview Questions & Answers

### 🟢 Q1. What is Terraform / IaC? Why use it? ★★★★★
**IaC** = defining infrastructure in code. **Terraform** is a declarative, cloud-agnostic IaC tool: you describe the desired state and it creates/updates resources to match. Benefits: reproducible, version-controlled, reviewable, no manual portal clicks.

### 🔴 Q2. What is the state file? Why remote state? ★★★★★
The **state file** (`terraform.tfstate`) maps your config to real resources and stores their current attributes. Keep it **remote** (Azure Storage backend) with **locking** so teams share one source of truth and concurrent applies don't corrupt it. **Never commit state to Git** (it can contain secrets).

### 🟢 Q3. plan vs apply vs destroy? ★★★★☆
`plan` = dry-run showing the change set. `apply` = execute the plan (create/update). `destroy` = tear down managed resources. Always review `plan` before `apply`.

### 🟡 Q4. Modules — what/why? ★★★★☆
**Modules** are reusable, parameterized bundles of resources (e.g., a "landing zone" module). They keep code DRY and consistent — call the same module with different variables per environment.

### 🟡 Q5. Managing multiple environments? ★★★★☆
Separate **workspaces** or per-env directories, each with its own **`tfvars`** and remote state, reusing shared modules. Vary only variables (names, sizes, endpoints) between Dev/Test/Prod.

### 🟡 Q6. Terraform vs ARM/Bicep? ★★★★☆
**Terraform** = multi-cloud, mature module ecosystem, explicit state. **ARM/Bicep** = Azure-native, no separate state file (state lives in Azure), tighter Azure integration. Choose Terraform for multi-cloud/standardization, Bicep for Azure-only teams.

### 🟡 Q7. How do you handle secrets? ★★★★★
Pull secrets from **Azure Key Vault** at runtime (data sources), mark variables `sensitive` (keeps them out of logs), and keep state **remote + encrypted**. Never hard-code secrets or commit state.

### 🔴 Q8. State locking — why? ★★★☆☆
Prevents two people/pipelines from applying at once and corrupting state. The Azure Storage backend uses **blob leases** for automatic locking.

### 🟡 Q9. Idempotency & drift detection? ★★★☆☆
Terraform is **idempotent** — re-applying an unchanged config does nothing. `terraform plan` detects **drift** (manual portal changes) by comparing real state to config; re-apply reconciles it.

### 🟡 Q10. Providers & backends? ★★★☆☆
A **provider** (e.g., `azurerm`, `databricks`) is the plugin that talks to an API. A **backend** defines where state lives (e.g., `azurerm` backend = Azure Storage). Both are declared in the config.

### 🟡 Q11. Variables, outputs, locals? ★★★☆☆
**Variables** = inputs (per-env via tfvars). **Outputs** = values exposed after apply (e.g., a resource id for another module). **Locals** = computed intermediate values to avoid repetition.

### 🔴 Q12. count vs for_each? ★★☆☆☆
Both create multiple resource instances. `count` uses an index (good for identical N copies); `for_each` iterates a map/set (stable keys, safer when adding/removing items — avoids index shifting).

### 🟡 Q13. terraform import — when? ★★☆☆☆
Brings an existing (manually created) resource under Terraform management by writing it into state, so you can manage it as code going forward.

---

## Scenario Questions
**🔴 S1. "Provision identical Dev/Test/Prod platforms." ★★★★★** → reusable **modules** + per-env `tfvars`; remote state per env with locking; CI/CD-driven plan/apply with approvals.
**🔴 S2. "Two engineers apply at once and corrupt state." ★★★★☆** → remote backend with **state locking** (blob lease) prevents it.
**🟡 S3. "Someone changed a resource in the portal." ★★★★☆** → `terraform plan` shows **drift**; re-apply to reconcile.
**🟡 S4. "Manage an existing resource with Terraform." ★★☆☆☆** → `terraform import` it into state, then add matching config.

---

## Code Example
```hcl
terraform {
  backend "azurerm" {                     # remote, locked state
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateacct"
    container_name       = "state"
    key                  = "prod.terraform.tfstate"
  }
}
resource "azurerm_storage_account" "lake" {
  name                     = var.lake_name
  resource_group_name      = var.rg
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true          # ADLS Gen2
}
```

---

## Quick Revision
- ✔ IaC = declarative, reproducible, version-controlled infra
- ✔ **Remote state + locking** (Azure Storage backend); never commit state
- ✔ plan (dry run) → apply → destroy
- ✔ **Modules** for reuse; `tfvars` per environment
- ✔ Secrets from **Key Vault**, mark `sensitive`
- ✔ `plan` detects **drift**; Terraform is idempotent
- ✔ `for_each` (stable keys) vs `count` (index)

## Common Interview Mistakes
- Committing/sharing state files (leaks secrets).
- Local state on a team project.
- Hard-coded secrets.
- `apply` without reviewing `plan`.
- `count` where `for_each` avoids index churn.

## Senior-Level Discussion
Seniors structure reusable modules, remote locked state per env, CI/CD-driven `plan`/`apply` with approvals, Key Vault secrets, drift management, and workspaces — and compare Terraform (multi-cloud) vs Bicep/ARM (Azure-native) by team context.

## Follow-up Questions
- "Why not commit state?" → contains resource attributes/secrets and causes conflicts.
- "How do you preview prod changes safely?" → `plan` in CI with approval before `apply`.

## Related Topics
ARM Templates, CI-CD, Azure DevOps, ADLS Gen2, Azure Databricks
