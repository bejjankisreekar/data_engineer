# Azure Blob Storage

## What is it?

Azure Blob Storage is Microsoft's general-purpose cloud storage for files. "Blob" stands for **B**inary **L**arge **OB**ject — Azure's word for "a file," whether that's a spreadsheet, a photo, a video, or a data export.

Analogy: think of Blob Storage as an enormous, endlessly expandable cloud filing cabinet. You can drop in any kind of file, give it a name, organize it into "containers" (similar to folders), and retrieve it from anywhere with an internet connection.

---

## Why not just use a regular hard drive or file server?

- **Scale** — a single storage account can hold from a few kilobytes to petabytes of data, without you needing to buy or manage physical hard drives.
- **Durability** — Azure automatically keeps multiple copies of your data across different hardware (and optionally different regions), so a single disk failure doesn't lose anything.
- **Accessibility** — files can be reached over the internet from anywhere, by any authorized application or person, without setting up your own servers.
- **Pay-as-you-go** — you pay for the storage and access you actually use, rather than buying fixed hardware capacity upfront.

---

## Key Building Blocks

| Term | What it means |
|---|---|
| Storage Account | The top-level container for all your storage in Azure — like the filing cabinet itself |
| Container | A grouping inside the storage account, similar to a folder |
| Blob | An individual file inside a container |

---

## Access Tiers

Not all stored data is accessed equally often. Azure offers different pricing tiers based on how "warm" the data needs to be:

| Tier | Best For | Analogy |
|---|---|---|
| Hot | Data accessed frequently | Papers on your desk |
| Cool | Data accessed occasionally (weeks/months) | Papers in a nearby drawer |
| Archive | Data rarely accessed, kept for compliance/history | Boxes in long-term storage, slower to retrieve |

Choosing the right tier is mostly a cost decision: cheaper tiers cost less to store but cost more (and take longer) to retrieve.

---

## Used In

- Backing up files and application data
- Serving images/videos for websites
- Storing exports, logs, and archives
- As the underlying storage layer for [Azure Data Lake Storage](03_Azure_Data_Lake_Storage.md)

---

## Azure Usage

Blob Storage is the foundation many other Azure data services are built on top of. Azure Data Factory, Databricks, and Synapse can all read from and write to Blob Storage directly.

---

## Real World Example

An insurance company scans and uploads every paper claim form as a PDF into Blob Storage. Recent claims (still being processed) sit in the Hot tier for quick access. Once a claim is settled and closed, it's moved to the Archive tier, since regulations require it to be kept for years but it's very unlikely anyone will need to open it again soon.

---
---

# Part 2 — Advanced

## Redundancy options — how many copies, and where

Every write is automatically replicated; *you* choose the blast radius it survives:

| Option | Copies | Survives | Rough cost |
|---|---|---|---|
| **LRS** | 3 in one datacenter | Disk/rack failure | baseline |
| **ZRS** | 3 across availability zones | Datacenter/zone loss | ~1.25× |
| **GRS / GZRS** | +3 async-copied to the paired region | Regional disaster | ~2× |
| **RA-GRS/RA-GZRS** | + read access to the secondary | Region loss, with read continuity | ~2× |

Pro notes: geo-replication is **asynchronous** — regional failover can lose the last minutes of writes (RPO > 0, [replication trade-offs](../00_Fundamentals/04_Master_Slave_Architecture.md)); failover is something you *initiate and rehearse*, not magic. Data platforms commonly run ZRS + rebuildable-from-source pipelines instead of paying GRS for derived data — **classify what's truly irreplaceable** and protect that.

## Blob types & the object-storage contract

- **Block blobs** (files, up to ~190 TB) — your world; **append blobs** (log-style appends); **page blobs** (VM disks, random writes).
- The contract that shapes everything: objects are **immutable-per-write** — no in-place edits, no appends to block blobs, "rename" = copy+delete. This is *why* [Parquet files are immutable](../02_File_formats/05_Parquet.md) and why table formats do versioned-file commits rather than updates ([Delta](../07_PySpark/Why_Spark_Why_Databricks.md)).
- Consistency is **strong** (read-after-write) — modern object stores fixed the eventual-consistency traps of early S3 ([CAP note](../00_Fundamentals/03_Distributed_Computing.md)).
- Throughput scales with *parallelism across blobs/prefixes*, not per-connection speed — the design reason engines write many files at once.

## Access control done properly

Ranked from best to last-resort:

1. **Entra ID + RBAC roles** (`Storage Blob Data Reader/Contributor`) granted to **managed identities** of ADF/Databricks — no secrets to leak ([identity as perimeter](../03_Cloud/02_SaaS_PaaS_IaaS.md)).
2. **User-delegation SAS** — time-boxed, scoped links backed by Entra (external sharing).
3. Account SAS/keys — legacy; rotate, vault, and plan their retirement. **Disable public blob access at the account level** on day one — "public container" remains the most common cloud data-breach headline.

Plus network posture: private endpoints + default-deny firewall on any account holding real data ([cloud network posture](../03_Cloud/01_Public_Private_Hybrid_Cloud.md)).

---

# Part 3 — Pro Level (what 10+ year engineers know)

## Lifecycle management — the tiering you automate, not remember

Policy, not people, moves data between tiers:

```json
{ "rules": [{ "name": "age-out-raw", "type": "Lifecycle",
  "definition": { "filters": { "prefixMatch": ["raw/"] },
    "actions": { "baseBlob": {
      "tierToCool":    { "daysAfterModificationGreaterThan": 30 },
      "tierToArchive": { "daysAfterModificationGreaterThan": 180 },
      "delete":        { "daysAfterModificationGreaterThan": 2555 } } } } }] }
```

The traps: **Cool/Archive have per-GB *read* and early-deletion charges** — a "cost-saving" archive of data someone then scans monthly costs more than Hot; Archive rehydration takes **hours** (and rehydration fees) — never archive anything a pipeline might need on demand. Model access patterns before tiering; measure with storage analytics after.

## Versioning, soft delete, immutability — the "oops" ladder

- **Soft delete** (blob + container): a recycle bin with retention — the first thing to enable everywhere.
- **Blob versioning**: every overwrite keeps the prior version — protects against bad pipeline overwrites, but on churn-heavy paths (streaming checkpoints, Delta logs) version bloat quietly multiplies storage cost; scope it deliberately.
- **Immutability policies (WORM)**: time-locked or legal-hold — regulatory-grade "nobody, including admins, can delete," the tool for audit/compliance zones.
- None of these replace **cross-account backup** for the truly critical: an attacker or script with enough permission can still purge; separation of accounts/subscriptions is the last line.

## Operating storage for data platforms

- **Naming/layout is an API**: `container/domain/dataset/year=2026/month=07/...` — consistent, partition-friendly, ACL-plannable ([ADLS specifics](03_Azure_Data_Lake_Storage.md)). Renaming a petabyte later is a project.
- **Cost telemetry**: per-container inventory reports + cost tags; the classic surprise is transaction (per-operation) costs from millions of tiny writes, not GB — another push against [small files](../07_PySpark/Spark_Processing.md).
- **Egress awareness**: cross-region reads from your "cheap" storage add per-GB fees ([data transfer economics](../03_Cloud/01_Public_Private_Hybrid_Cloud.md)) — keep compute in the storage region.
- Monitor: availability metric, throttling (503s → too many requests per partition), capacity trends per container.

## Field-tested gotchas

- Overwriting a blob while a reader streams it can fail mid-read — readers of mutable paths need retry + ETag checks; better: write-new-then-swap-reference patterns (what table formats formalize).
- SAS tokens in notebook cells/URLs end up in git history — treat any pasted SAS as leaked; user-delegation SAS + short expiry limits the damage.
- Account-level throughput limits exist (tens of Gbps) — a Spark job with 2,000 tasks hammering one account can throttle; scale-out across accounts is a real pattern at extreme scale.
- Deleting millions of blobs is itself a slow, billable operation — lifecycle-policy deletes beat client-side delete loops.

## Interview-grade Q&A

- *LRS vs ZRS vs GRS — how do you choose?* Blast radius vs cost, per data class: rebuildable derived data → LRS/ZRS; irreplaceable sources → ZRS+GRS with rehearsed failover.
- *Why can't you edit a file in place in object storage?* Immutable object contract — the foundation table formats build versioned commits on.
- *How should a Databricks job authenticate to storage?* Managed identity/service principal with scoped RBAC — never account keys in code.
- *Archive tier looks 10× cheaper — why be careful?* Retrieval latency (hours), rehydration + read charges, early-deletion fees — cheap to hold, expensive to touch.

---

## Further Learning — Docs & Videos

**Documentation**
- Azure Blob Storage overview: https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction
- Blob access tiers: https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview
- Storage redundancy: https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy

**Videos**
- Azure Blob Storage tutorial: https://www.youtube.com/results?search_query=azure+blob+storage+tutorial
