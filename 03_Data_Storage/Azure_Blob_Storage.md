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
- As the underlying storage layer for [Azure Data Lake Storage](Azure_Data_Lake_Storage.md)

---

## Azure Usage

Blob Storage is the foundation many other Azure data services are built on top of. Azure Data Factory, Databricks, and Synapse can all read from and write to Blob Storage directly.

---

## Real World Example

An insurance company scans and uploads every paper claim form as a PDF into Blob Storage. Recent claims (still being processed) sit in the Hot tier for quick access. Once a claim is settled and closed, it's moved to the Archive tier, since regulations require it to be kept for years but it's very unlikely anyone will need to open it again soon.
