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

## Common interview mistakes
- Account keys/SAS instead of Managed Identity.
- Secrets in code/notebooks.
- Public network access (no private endpoints).
- Per-user grants instead of groups.
- Confusing RBAC (identity permissions) with Azure Policy (resource compliance).

## Related Topics
[Data Quality](../Data_Quality/01_Data_Quality_Fundamentals.md) · [ADLS Gen2 security](../../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md) · [Databricks Unity Catalog](../../Certifications/Databricks_Data_Engineer_Associate/10_Data_Governance_Unity_Catalog.md)
