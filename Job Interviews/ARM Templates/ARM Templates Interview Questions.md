# ARM Templates (& Bicep) — Interview Questions & Answers

## Overview
ARM templates are Azure's native JSON IaC; **Bicep** is the cleaner DSL that compiles to ARM. In DE, ARM is central to **ADF CI/CD** (publish generates ARM) and to provisioning Azure resources.

Difficulty: 🟢 · 🟡 · 🔴 · Confidence: ★.

---

## Interview Questions & Answers

### 🟢 Q1. What is an ARM template? ★★★★☆
A JSON file declaring Azure resources (and their properties/dependencies) that Azure Resource Manager deploys **declaratively** — you describe the desired state, ARM makes it so, in the right dependency order.

### 🟡 Q2. ARM vs Bicep? ★★★★☆
**Bicep** is a concise, readable DSL that **transpiles to ARM JSON** — Azure-native, far less verbose, better tooling. Prefer Bicep for new work; you'll still see ARM JSON (e.g., ADF publish output).

### 🟡 Q3. Parameters vs variables vs outputs? ★★★★☆
**Parameters** = inputs supplied at deploy time (per-environment values). **Variables** = computed/reused values inside the template. **Outputs** = values returned after deployment (e.g., a resource id for another template).

### 🔴 Q4. How does ADF use ARM templates for CI/CD? ★★★★★
ADF **Publish** generates an ARM template + parameters file into the `adf_publish` branch. The release pipeline deploys it to Test/Prod, **overriding ARM parameters** (linked-service endpoints, Key Vault URLs) per environment. This is the standard ADF promotion mechanism.

### 🔴 Q5. Incremental vs complete deployment mode? ★★★★☆
**Incremental** (default) adds/updates resources in the template, leaving others untouched. **Complete** **deletes** resources in the resource group that aren't in the template. Use **incremental** in shared RGs to avoid accidental deletions.

### 🟡 Q6. How do you parameterize per environment? ★★★★★
Keep environment-specific values (names, endpoints, SKUs, Key Vault URIs) as **parameters**, supplied via per-env **parameter files** or pipeline variables at deploy time. Never hard-code env values.

### 🟡 Q7. Linked/nested templates? ★★★☆☆
**Linked** templates reference other template files (modular, reusable); **nested** embed sub-templates inline. Both break a big deployment into manageable, reusable pieces (Bicep uses `module` for this).

### 🟡 Q8. ARM vs Terraform? ★★★☆☆
**ARM/Bicep** = Azure-native, no external state (state lives in Azure), tight Azure integration. **Terraform** = multi-cloud, explicit state file, huge module ecosystem. Choose by Azure-only vs multi-cloud and team preference.

### 🟡 Q9. How do you handle secrets in ARM? ★★★★☆
Reference **Key Vault** secrets in parameters (a `reference` to a KV secret id) so plaintext never appears in the template or parameter file. Combine with managed identities for resource access.

### 🟡 Q10. What is idempotency in ARM? ★★★☆☆
Re-deploying the same template produces the same result (no duplicates); ARM reconciles to the declared state. Safe to re-run.

### 🟡 Q11. dependsOn — what is it? ★★★☆☆
Declares an explicit deployment **dependency/order** between resources (e.g., a database after its server). Bicep often infers dependencies automatically from references.

### 🟡 Q12. What-if / validation? ★★★☆☆
`az deployment group what-if` previews changes before deploying (like Terraform `plan`); template **validation** checks syntax/schema before an actual deploy.

---

## Scenario Questions
**🔴 S1. "Promote ADF to prod with different endpoints." ★★★★★** → override ARM template parameters per stage in the release pipeline.
**🔴 S2. "A complete-mode deploy deleted a resource." ★★★★☆** → switch to **incremental** mode in shared resource groups.
**🟡 S3. "Avoid secrets in the template." ★★★★☆** → **Key Vault reference** in parameters.
**🟡 S4. "Preview infra changes before applying." ★★★☆☆** → `what-if` deployment.

---

## Code Example (Bicep)
```bicep
param location string = resourceGroup().location
param lakeName string
resource lake 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: lakeName
  location: location
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
  properties: { isHnsEnabled: true }   // ADLS Gen2
}
output lakeId string = lake.id
```

---

## Quick Revision
- ✔ ARM = native JSON IaC; **Bicep** = cleaner DSL → ARM
- ✔ Parameters (inputs) · variables (computed) · outputs (returns)
- ✔ ADF CI/CD = **publish → ARM → deploy with per-env params**
- ✔ **Incremental** (safe) vs **Complete** (deletes extras) mode
- ✔ Secrets via **Key Vault reference**; idempotent deploys
- ✔ `dependsOn` for order; `what-if` to preview

## Common Interview Mistakes
- Complete mode in shared RGs (deletes resources).
- Plaintext secrets in templates/parameter files.
- Not parameterizing environment values.

## Senior-Level Discussion
Seniors prefer Bicep, parameterize all env-specific values, reference Key Vault, use incremental mode safely, modularize with linked templates/modules, and integrate ARM deploys into DevOps releases — knowing when Terraform fits better (multi-cloud).

## Follow-up Questions
- "Why incremental mode by default?" → avoids deleting resources not in the template.
- "How is ARM state handled vs Terraform?" → ARM keeps state in Azure; no separate state file.

## Related Topics
Terraform, CI-CD, Azure DevOps, Azure Data Factory
