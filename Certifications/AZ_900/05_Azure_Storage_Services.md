# 05 — Azure Storage Services

> Domain: **Describe Azure architecture and services** · Prev: [Networking Services](04_Azure_Networking_Services.md) · Next: [Identity, Access & Security](06_Identity_Access_Security.md)

For the full engineering-depth version of this topic (internals, ACLs, performance), see the main repo's [Azure Blob Storage](../../04_Storage_and_Formats/Data_Storage/02_Azure_Blob_Storage.md) and [Azure Data Lake Storage](../../04_Storage_and_Formats/Data_Storage/03_Azure_Data_Lake_Storage.md) notes. This file covers exactly what AZ-900 tests.

---

## The storage account

Every Azure storage service sits inside a **storage account** — the top-level container that provides a unique namespace and holds all your data services (Blob, File, Table, Queue, Disk).

---

## The storage services (know what each holds)

| Service | Stores | Structure | Typical use |
|---|---|---|---|
| **Blob Storage** | Unstructured object data — any file type | Flat namespace (container → blob), or hierarchical with ADLS Gen2 | Images, video, backups, logs, big data analytics files |
| **Disk Storage** | Managed disks for Azure VMs | Behaves like a physical hard disk attached to a VM | VM operating system and data disks |
| **File Storage (Azure Files)** | Fully managed **file shares** | Standard SMB/NFS protocol, mountable like a network drive | Lift-and-shift apps expecting a traditional file share, shared config files |
| **Table Storage** | NoSQL key-value data | Simple schema-less tables | Structured, non-relational data at massive scale, low cost |
| **Queue Storage** | Messages for asynchronous communication | FIFO-ish message queue between application components | Decoupling application components, work queues |

**Exam Tip:** "A company wants to lift-and-shift a legacy app that reads/writes to a network file share" → **Azure Files**, not Blob Storage (Blob is object storage, not a mountable SMB share). "Store millions of unstructured images cheaply" → **Blob Storage**. These two are the most common storage-selection scenario questions.

### Blob access tiers

Blob Storage offers **access tiers** trading storage cost against access cost/latency:

| Tier | Best for | Storage cost | Access cost |
|---|---|---|---|
| **Hot** | Frequently accessed data | Highest | Lowest |
| **Cool** | Infrequently accessed data (accessed less than once a month), kept for at least 30 days | Lower | Higher |
| **Archive** | Rarely accessed data, kept for at least 180 days, offline | Lowest | Highest (and slow — hours to rehydrate before it's readable) |

**Exam Tip:** Archive tier data is **not immediately readable** — it must be "rehydrated" first, which can take hours. A question describing "data that must be instantly available at all times" rules out Archive.

---

## Redundancy (replication) options — how many copies, and where

Azure automatically replicates your data for durability. The options trade cost against how big a disaster they protect against:

| Option | Full name | Copies | Protects against |
|---|---|---|---|
| **LRS** | Locally Redundant Storage | 3 copies within **one datacenter** | Hardware failure (disk/server) |
| **ZRS** | Zone-Redundant Storage | 3 copies across **different Availability Zones** in one region | Datacenter/zone-level failure |
| **GRS** | Geo-Redundant Storage | LRS in primary region + async-copied to a **secondary paired region** | Regional disaster (data not immediately readable in the secondary unless failover occurs) |
| **RA-GRS** | Read-Access Geo-Redundant Storage | Same as GRS, **plus read access** to the secondary region's copy at any time | Regional disaster, with read continuity even before failover |
| **GZRS** | Geo-Zone-Redundant Storage | ZRS in primary region + async-copied to secondary region | Zone failure *and* regional disaster combined |
| **RA-GZRS** | Read-Access Geo-Zone-Redundant Storage | GZRS + read access to the secondary | The highest level of durability and read availability offered |

**Exam Tip:** This table is asked about constantly, often as "which redundancy option provides read access to a secondary region" (**RA-GRS** or **RA-GZRS** — the "RA" prefix is the tell) or "which is the cheapest option that survives a single datacenter failure" (**LRS**). Know that geo-replication is **asynchronous** — a regional failure can still lose the last few seconds/minutes of writes before the secondary catches up.

---

## Data migration and transfer tools

| Tool | Purpose |
|---|---|
| **AzCopy** | Command-line tool for fast, scriptable upload/download/copy of data to/from Azure Storage |
| **Azure Storage Explorer** | Free GUI application for browsing and managing Azure Storage data |
| **Azure Migrate** | A hub of tools to assess and migrate on-premises servers/databases/apps to Azure |
| **Azure Data Box** | A **physical appliance** Microsoft ships to you, into which you copy large volumes of data offline, then ship it back to Azure — used when the amount of data is too large to transfer efficiently over a network connection |

**Exam Tip:** "Company has 200 TB of data and limited network bandwidth — how do they move it to Azure?" → **Azure Data Box** (physical shipping beats a slow network transfer for very large one-time migrations).

---

## Quick Review

- Storage account = top-level container for Blob/Disk/File/Table/Queue storage.
- **Blob** = unstructured objects. **Disk** = VM disks. **Files** = mountable SMB/NFS shares (lift-and-shift). **Table** = NoSQL key-value. **Queue** = async messaging between components.
- Blob tiers: **Hot** (frequent access, most expensive to store), **Cool** (infrequent, 30-day minimum), **Archive** (rare, 180-day minimum, offline, hours to rehydrate).
- Redundancy: **LRS** (one datacenter) → **ZRS** (zones in one region) → **GRS** (+ paired region, async) → **RA-GRS** (+ readable secondary) → **GZRS**/**RA-GZRS** (zones + region combined).
- **AzCopy** (CLI), **Storage Explorer** (GUI), **Azure Migrate** (assess & migrate), **Data Box** (physical offline transfer for huge datasets).

---

## Further Learning — Docs & Videos

**Official documentation**
- Azure Storage account overview: https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview
- Blob storage & access tiers (Hot/Cool/Archive): https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview
- Storage redundancy (LRS/ZRS/GRS/GZRS): https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy
- Data migration options (AzCopy, Data Box, Migrate): https://learn.microsoft.com/en-us/azure/storage/common/storage-choose-data-transfer-solution

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- Azure storage services explained: https://www.youtube.com/results?search_query=azure+storage+blob+file+queue+table+az-900
- Blob access tiers & redundancy: https://www.youtube.com/results?search_query=azure+storage+redundancy+lrs+zrs+grs+access+tiers

---

Next: [06 — Identity, Access & Security](06_Identity_Access_Security.md)
