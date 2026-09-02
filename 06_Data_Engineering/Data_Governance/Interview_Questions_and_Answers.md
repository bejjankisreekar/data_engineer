# Data Governance & Security — Interview Questions & Answers

Tagged: 🔥 very common · ⭐ common · 💡 deeper.

---

**Q1. 🔥 What is data governance?**
Policies, roles, and controls ensuring data is secure, compliant, discoverable, high-quality, and understood — covering cataloging, access/security, lineage, classification/privacy, quality, ownership, and auditing.

**Q2. 🔥 Authentication vs authorization?**
authN = proving who you are (Entra ID, Managed Identity). authZ = what you're allowed to do (RBAC/ACL/GRANT). authN happens first.

**Q3. 🔥 How do you secure an Azure data platform?**
Managed Identity + RBAC (least privilege), Key Vault for secrets, private endpoints + firewall, encryption (TDE/CMK, TLS), fine-grained control (Unity Catalog/RLS/masking), and auditing to Log Analytics + Defender.

**Q4. 🔥 How does Databricks/ADF access storage securely?**
**Managed Identity + RBAC** (`Storage Blob Data Contributor`) or a service principal with a **Key Vault-backed secret scope** — never account keys/SAS.

**Q5. ⭐ RBAC vs ACLs on ADLS — and evaluation order?**
RBAC = coarse (container/account); ACLs = fine (file/folder POSIX rwx). **RBAC is evaluated first**; ACLs apply to principals without a data-plane RBAC role. Grant to groups.

**Q6. 🔥 What is data lineage and why does it matter?**
The record of where data came from and how it flows (source → transform → target). Used for impact analysis, debugging, and compliance. Purview and Unity Catalog capture it **automatically**.

**Q7. ⭐ Purview vs Unity Catalog?**
Purview = estate-wide catalog, classification (PII), and lineage across many sources. Unity Catalog = Databricks-scoped access control + lineage. Complementary.

**Q8. ⭐ How do you implement row/column-level security?**
**Dynamic views** using `current_user()`/`is_account_group_member()` (Unity Catalog), or Row-Level Security + dynamic data masking in Azure SQL/Synapse.

**Q9. 🔥 How do you handle GDPR "right to be forgotten"?**
`DELETE FROM t WHERE user_id=...` in Delta, then **VACUUM** to physically remove files (respect retention); ensure no copies linger in other zones; audit the deletion.

**Q10. ⭐ How do you classify and protect PII?**
Purview scans and **classifies** (SSN, credit card, etc.); apply masking/anonymization for non-privileged users; restrict via RBAC/dynamic views; encrypt sensitive columns (Always Encrypted).

**Q11. ⭐ Where do secrets go?**
**Azure Key Vault**, referenced via secret scopes / linked services / variable groups — never in code, notebooks, or YAML. Rotate regularly.

**Q12. 💡 What is Azure Policy's role in governance?**
Enforces resource **configuration/compliance** rules (e.g., "storage must use private endpoints", "deny public IPs") — distinct from RBAC (which controls identity permissions).

**Q13. 💡 What is a data steward/owner?**
An accountable person per data domain responsible for its quality, definitions, and access decisions — the human side of governance.

**Q14. ⭐ Encryption at rest vs in transit vs Always Encrypted?**
At rest = TDE (default, server can decrypt); in transit = TLS; **Always Encrypted** = client-side encryption so data is hidden even from DBAs/the server.

## Scenario
**Q15. 🔥 "Auditor asks: prove least-privilege access and trace a PII column's origin."**
Show RBAC/UC grants to groups (least privilege), Purview **classification** of the PII column, and Purview/UC **lineage** tracing source → Gold; plus audit logs in Log Analytics.

## Identity (Microsoft Entra ID)

**Q16. 🔥 Managed identity vs service principal?**
A managed identity **is** a service principal whose credentials Azure creates and rotates for you — available only to Azure resources, with no secret you ever handle. A plain service principal needs a client secret or certificate you manage yourself, which is what you use from outside Azure (GitHub Actions, on-prem jobs). Prefer **managed identity** whenever the caller is an Azure resource.

**Q17. 🔥 I'm Owner on the storage account but get `403 AuthorizationPermissionMismatch` reading a file. Why?**
Owner/Contributor are **control-plane** roles — they let you manage the account, not read blobs with your own identity. Data access needs a **data-plane** role such as `Storage Blob Data Reader`/`Contributor`. This is the single most common ADLS access mistake.

**Q18. ⭐ System-assigned vs user-assigned managed identity?**
System-assigned is created and destroyed with one resource (redeploy it and every role assignment must be redone). User-assigned is a standalone Azure resource shared by many services and surviving redeployment — the right choice for CI/CD-deployed resources and fleets.

**Q19. ⭐ How do you authenticate CI/CD to Azure without storing a secret?**
**Workload identity federation** — GitHub Actions/GitLab/Kubernetes present their own OIDC token, which Entra exchanges for an access token via a federated credential on the app registration. No secret exists to leak, expire, or rotate.

**Q20. 💡 What are Conditional Access and PIM, and how can they break a pipeline?**
Conditional Access evaluates signals (user, app, device, location, risk) at sign-in and can require MFA or block. PIM gives just-in-time, time-boxed, approval-gated activation of privileged roles instead of standing admin. The classic failure is a tenant-wide "require MFA" policy that catches an unattended service principal — service principals can't do MFA, so the pipeline dies. Scope CA to users; govern workload identities with Entra Workload ID policies.

Full treatment: **[Microsoft Entra ID](03_Microsoft_Entra_ID.md)**.

## Common interview mistakes
- Account keys/SAS instead of Managed Identity.
- Secrets in code/notebooks.
- Public network access (no private endpoints).
- Per-user grants instead of groups.
- Confusing RBAC (identity permissions) with Azure Policy (resource compliance).
- Assuming Contributor grants data access — control-plane roles don't read blobs.
- Long-lived client secrets with no rotation plan, where a managed identity would do.

## Related Topics
[Microsoft Entra ID](03_Microsoft_Entra_ID.md) · [Network Security](02_Network_Security_and_Private_Connectivity.md) · [Data Quality](../Data_Quality/01_Data_Quality_Fundamentals.md) · [ADLS Gen2 security](../../05_Storage_and_Formats/Data_Lakes_and_Storage/03_Azure_Data_Lake_Storage.md) · [Databricks Unity Catalog](../../Certifications/Databricks_Data_Engineer_Associate/10_Data_Governance_Unity_Catalog.md)
