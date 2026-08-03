# 05 — Dictionaries

## What is a dictionary?

A **dictionary** (`dict`) stores data as **key → value** pairs. Instead of looking things up by position (like a list), you look them up by a meaningful key.

**Analogy:** A real dictionary maps a *word* (key) to its *definition* (value). A phone contact list maps a *name* (key) to a *number* (value). You don't ask for "the 5th contact" — you ask for "Ada's number."

```python
person = {
    "name": "Ada",
    "role": "Data Engineer",
    "years": 6
}

person["name"]      # "Ada" — look up by key
person["years"]     # 6
```

Dictionaries are one of the most important structures in Python — and the closest thing to a JSON object, which makes them central to data work.

---

## Creating, reading, updating, deleting

```python
d = {"a": 1, "b": 2}

d["c"] = 3          # add a new key
d["a"] = 100        # update an existing key
del d["b"]          # delete a key

"a" in d            # True — check if a key exists
len(d)              # number of pairs
```

### Safe lookups with `.get()`

Accessing a missing key with `d["missing"]` raises a `KeyError` and crashes. `.get()` returns `None` (or a default) instead:

```python
d.get("z")           # None — no crash
d.get("z", 0)        # 0 — supply a default
```

> **Gotcha:** Prefer `.get()` when a key might be absent (very common with messy source data). `d["z"]` should only be used when you're certain the key exists.

---

## Looping over dictionaries

```python
prices = {"apple": 30, "banana": 10, "cherry": 80}

for key in prices:                 # keys by default
    print(key)

for key, value in prices.items():  # keys AND values — the common pattern
    print(f"{key} costs {value}")

prices.keys()      # dict_keys(['apple', 'banana', 'cherry'])
prices.values()    # dict_values([30, 10, 80])
prices.items()     # pairs as (key, value) tuples
```

---

## Nested dictionaries (this is JSON)

Values can themselves be dicts or lists — which is exactly how JSON and API responses are shaped:

```python
order = {
    "id": 1001,
    "customer": {"name": "Ada", "city": "Hyderabad"},
    "items": [
        {"sku": "A1", "qty": 2},
        {"sku": "B7", "qty": 1}
    ]
}

order["customer"]["city"]     # "Hyderabad"
order["items"][0]["sku"]      # "A1"
order["items"][1]["qty"]      # 1
```

Reading `order["customer"]["city"]` — key inside a key — is exactly how you pull fields out of a JSON record.

---

## Why it matters for data engineering

Dictionaries are the **in-memory form of a JSON object**. When you read a JSON file or call a REST API, Python hands you back dicts and lists. Every ingestion script navigates them: `record["payload"]["user"]["id"]`. They're also how you:

- pass **configuration** around (`config["source_path"]`),
- build **row records** before writing them out,
- **count / group** things (`counts[key] = counts.get(key, 0) + 1`),
- map lookup tables (`country_code["IN"] → "India"`).

In PySpark, the `MapType` column and the JSON-parsing you'll do in module 07 are the distributed versions of exactly this. Master dicts and half of data wrangling clicks into place.

---

## Further Learning — Docs & Videos

**Documentation**
- Dictionaries tutorial: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
- Mapping type (dict) — all methods: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
- Working with JSON (json module): https://docs.python.org/3/library/json.html

**Videos**
- Python dictionaries explained: https://www.youtube.com/results?search_query=python+dictionaries+explained
- Python dict & JSON for data: https://www.youtube.com/results?search_query=python+dictionary+json+tutorial

Next: **[06 — Conditionals & Loops](06_Conditionals_and_Loops.md)**.
