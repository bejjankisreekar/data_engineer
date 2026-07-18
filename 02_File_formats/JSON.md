# JSON (JavaScript Object Notation)

## What is JSON?

JSON stores data as key-value pairs — a label ("key") paired with its value, like a name tag paired with the name written on it (`"Name": "John"`).

Analogy: think of a form with labeled boxes, except some boxes can contain an entire smaller form nested inside them (an "address" box that itself contains "city" and "country" boxes). [CSV](CSV.md) can only handle a single flat grid — JSON can handle that nesting.

Example

```json
{
  "EmployeeID":101,
  "Name":"John",
  "Department":"IT",
  "Salary":60000
}
```

Multiple records

```json
[
  {
    "EmployeeID":101,
    "Name":"John"
  },
  {
    "EmployeeID":102,
    "Name":"Alice"
  }
]
```

---

## Advantages

- Flexible
- Supports nested objects
- Supports arrays
- Widely used in APIs

---

## Example

Customer

```json
{
"name":"John",
"address":{
"city":"New York",
"country":"USA"
}
}
```

CSV cannot store nested structures like this.

---

## Used In

- REST APIs
- Configuration files
- Event data
- IoT
- Web applications

---

## Azure Usage

ADF

Databricks

Synapse

Event Hub

Cosmos DB

---

## Where JSON Fits

JSON is the standard shape for data moving between web applications and APIs, but it's rarely the format used for long-term analytical storage — see [File Format Comparison](File_Format_Comparison.md) for what it's typically converted into ([Parquet](Parquet.md), usually) before large-scale analysis.