# Document Databases

## What is a document database?

A document database stores data as **self-contained documents** — usually **JSON** (or its binary form, **BSON**) — where each document holds all the related information about one thing, including nested objects and lists.

Analogy: think of a **manila folder for each customer**. Inside one folder you keep their name, all their addresses, their list of past orders, their preferences — everything about that customer in *one place*. You don't keep addresses in a separate cabinet and orders in a third room. Grab the folder and you have the whole picture. A document database is a giant, instantly-searchable set of these folders.

Examples: **MongoDB**, **Azure Cosmos DB** (NoSQL/Mongo APIs), **Couchbase**, **Amazon DocumentDB**, **Firestore**.

---

## Example

One customer as a single document:

```json
{
  "_id": "cust_1001",
  "name": "Asha Rao",
  "email": "asha@example.com",
  "addresses": [
    { "type": "home", "city": "Bengaluru", "pin": "560001" },
    { "type": "work", "city": "Bengaluru", "pin": "560100" }
  ],
  "preferences": { "newsletter": true, "theme": "dark" },
  "orders": [
    { "orderId": "o-88", "total": 1299, "items": 3, "date": "2026-01-14" }
  ]
}
```

In a relational database this would be **four tables** (customers, addresses, preferences, orders) joined together. Here it's **one document** you read in a single hit. Documents in the same **collection** don't all need identical fields — the next customer might have no `orders` array yet, or an extra `loyaltyTier` field.

Querying can reach *inside* documents (unlike key-value):

```javascript
// MongoDB-style
db.customers.find({ "addresses.city": "Bengaluru" })
db.customers.find({ "preferences.newsletter": true })
db.customers.updateOne(
  { _id: "cust_1001" },
  { $push: { orders: { orderId: "o-89", total: 499, items: 1 } } }
)
```

---

## Why document databases are popular

- **Maps to application objects** — a JSON document *is* basically the object your code already uses; no "object-relational mismatch," no shredding into tables and re-joining.
- **Flexible schema** — add a field to new documents without a migration; different documents can differ.
- **Fast reads for whole objects** — one lookup returns the complete entity, no joins.
- **Natural fit for web/mobile APIs**, catalogs, user profiles, content management, and event/telemetry data.

---

## Embedding vs Referencing — the central modeling choice

Because there are no joins, you decide how related data is stored:

| Approach | What it means | Use when |
|---|---|---|
| **Embed** | Nest related data *inside* the parent document (orders inside customer) | Data is read together, owned by the parent, and bounded in size |
| **Reference** | Store just an ID pointing to another document (like a foreign key) | Data is large, shared across parents, or grows unbounded |

Rule of thumb: **"data that is queried together should be stored together."** Embed the addresses (small, always read with the customer). Reference the products in an order by ID if the full product catalog is huge and shared. Getting this balance right is the heart of [NoSQL data modeling](07_NoSQL_Data_Modeling.md).

---

## Azure Usage

**Azure Cosmos DB** is Azure's managed document database, offered through the **NoSQL (SQL) API** and a **MongoDB API** (so existing Mongo apps run nearly unchanged). Data engineers frequently ingest Cosmos DB documents into a lakehouse via the **Change Feed** or **Azure Synapse Link** (analytical store), then **flatten** the nested JSON into tabular Silver/Gold tables. See [08_Azure_Cosmos_DB.md](08_Azure_Cosmos_DB.md).

---

## Real World Example

A retailer's product catalog lives in **MongoDB/Cosmos DB** because products are wildly inconsistent: a T-shirt has size and color; a laptop has RAM, CPU, and ports; a book has an author and ISBN. In a relational database you'd fight this with sparse columns or an ugly key-value attributes table. As documents, each product simply carries the fields it needs. The app reads a product page with **one document fetch** — title, specs, images, and reviews summary all in one object.

---

## Collections, documents, and the (soft) schema

A **document** is one JSON/BSON object; a **collection** is a group of documents (loosely the equivalent of a table). Collections are schema-flexible by default, but production systems add guardrails: MongoDB supports **JSON Schema validators** that reject documents missing required fields or with wrong types. The lesson from [What is NoSQL](01_What_is_NoSQL.md) applies — "flexible" should not mean "anything goes." Teams that skip validation end up with the same field as a string in half the documents and an object in the other half, and every consumer pays for it.

## Indexes make document queries fast

Without an index, querying by a field means scanning every document — fine for 1,000 docs, fatal for 50 million. Document databases let you **index fields inside documents**, including nested paths and array elements (`addresses.city`). The trade-off is the classic one from [SQL indexes](../SQL/11_SQL_Indexes.md): indexes speed reads but slow writes and cost storage. In document DBs you index specifically to support your **known query patterns** — you don't index everything.

## Atomicity is per-document (mostly)

A write to a **single document is atomic** — updating a customer and pushing a new order into their embedded array happens all-or-nothing. This is a big reason embedding is powerful: things that must change together live in one document and update atomically. Historically, updates spanning *multiple* documents were **not** transactional (BASE). Modern engines (MongoDB 4.0+, Cosmos DB within a partition) added **multi-document transactions**, but they're more limited and costly than relational ACID — so you still design to keep a transaction inside one document/partition where possible. See [06_CAP_Theorem_and_Consistency.md](06_CAP_Theorem_and_Consistency.md).

## The aggregation pipeline

Document databases can do more than fetch-by-id. MongoDB's **aggregation pipeline** chains stages (`$match` → `$group` → `$sort` → `$project`) much like SQL's `WHERE`/`GROUP BY`/`SELECT`, letting you compute analytics inside the database. It's powerful, but heavy analytical crunching is usually better pushed to a lakehouse/warehouse — the document DB stays the fast operational serving layer.

---

## The unbounded array anti-pattern

The most common document-modeling mistake: **embedding an array that grows forever**. Putting *every* order inside the customer document works with 5 orders and explodes at 50,000 — documents have size limits (MongoDB 16 MB), rewrites get expensive, and reads drag in data you don't need. The fix is the **subset / bucket pattern**: embed the *recent* few (e.g., last 5 orders for the profile page) and store the full history as separate referenced documents. Ask of every embedded array: *can this grow without bound?* If yes, don't embed it all.

## Schema versioning without migrations

Because you can't cheaply `ALTER` a billion documents, teams use a **`schemaVersion` field** on each document and handle multiple versions in code, migrating lazily as documents are touched. This is a genuine architectural pattern — the flexibility that lets you evolve without downtime also means **old and new shapes coexist**, and your read logic must tolerate both. Data engineers ingesting these collections must handle every version present.

## The dual-write / consistency trap

A frequent production bug: the app writes to the document DB *and* to a search index or cache, but one write succeeds and the other fails, leaving them inconsistent. The robust pattern is **Change Data Capture** off the document DB's change stream (MongoDB Change Streams, Cosmos DB Change Feed) as the single source of truth that fans out to other systems — rather than the app writing to two places and hoping both succeed. This is exactly how you'll wire document DBs into pipelines in [09_NoSQL_in_Data_Engineering.md](09_NoSQL_in_Data_Engineering.md).

## Interview-grade Q&A

- *What is a document database and how does it differ from key-value?* Stores queryable JSON/BSON documents; unlike key-value, you can query and index fields *inside* the value.
- *Embedding vs referencing — how do you choose?* Embed data read together, owned by the parent, and bounded in size; reference data that's large, shared, or unbounded.
- *What's the unbounded array anti-pattern?* Embedding an ever-growing list in one document; fix with the subset/bucket pattern (embed recent, reference the rest).
- *Is a document write atomic?* A single-document write is atomic; multi-document transactions exist in modern engines but are more limited than relational ACID.
- *How do you keep a "flexible" collection from becoming a swamp?* Schema validators, a `schemaVersion` field, and disciplined access-pattern-driven modeling.

---

## Further Learning — Docs & Videos

**Documentation**
- MongoDB data modeling: https://www.mongodb.com/docs/manual/data-modeling/
- MongoDB schema design patterns: https://www.mongodb.com/developer/products/mongodb/mongodb-schema-design-best-practices/
- Cosmos DB for NoSQL: https://learn.microsoft.com/azure/cosmos-db/nosql/

**Videos**
- MongoDB explained: https://www.youtube.com/results?search_query=mongodb+explained+for+beginners
- Embedding vs referencing in document databases: https://www.youtube.com/results?search_query=mongodb+embedding+vs+referencing
