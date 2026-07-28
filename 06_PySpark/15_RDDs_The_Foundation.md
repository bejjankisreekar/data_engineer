# 15 — RDDs: The Foundation

> Prev: [Performance & Best Practices](14_Performance_and_Best_Practices.md) · Series home: [Learning Path](00_PySpark_Learning_Path.md)

Every file so far used the **DataFrame API** — and deliberately so; it's what you write in 2026. This file goes one level deeper: the **RDD (Resilient Distributed Dataset)**, the original data structure Spark was built around, and the thing DataFrames actually compile down to. Understanding RDDs turns "Spark is fast because it's in-memory" into a mechanical, provable fact instead of a slogan.

---

## Level 1 — What is an RDD?

An **RDD** is Spark's most basic data structure: an **immutable, distributed collection of objects**, split into partitions across the cluster, that Spark can recompute if a piece is lost.

Unpack the name — it explains the whole design:

| Letter | Meaning | Why it matters |
|---|---|---|
| **R**esilient | Can rebuild itself after a failure | Spark doesn't replicate data for safety; it remembers *how to recreate* it |
| **D**istributed | Split into partitions across machines | The unit of [parallelism](Spark_Processing.md) |
| **D**ataset | A collection of *any* Python/Java/Scala objects | Not limited to rows/columns — could be strings, tuples, custom classes |

Analogy: a DataFrame is a spreadsheet torn into chunks ([file 02](02_DataFrame_Basics.md)) — rows and named, typed columns. An RDD is more primitive: a **bag of Python objects torn into chunks**, with no column names, no types Spark understands, no optimizer looking inside. If a DataFrame is a filing cabinet with labeled folders, an RDD is a stack of boxes — Spark knows how to split and ship the boxes, but has no idea what's written on the papers inside.

### Your first RDD

```python
nums = spark.sparkContext.parallelize([1, 2, 3, 4, 5])   # RDDs come from sparkContext, not spark
nums.collect()          # [1, 2, 3, 4, 5]   — action: brings data to the driver

lines = spark.sparkContext.textFile("path/to/file.txt")   # one RDD element per line of text
lines.count()                                              # action
```

Same **lazy transformation vs action** split as DataFrames ([reminder](01_Getting_Started_SparkSession.md)) — `parallelize`/`textFile`/`map`/`filter` describe; `collect`/`count`/`take` execute.

### Creating RDDs — the three ways

```python
rdd1 = spark.sparkContext.parallelize([1, 2, 3])              # from a Python collection
rdd2 = spark.sparkContext.textFile("path/file.txt")           # from a file — one line per element
rdd3 = df.rdd                                                  # from an existing DataFrame — each element becomes a Row
```

---

## Level 1 — Transformations (build the plan)

```python
nums = spark.sparkContext.parallelize([1, 2, 3, 4, 5, 6])

nums.map(lambda x: x * 2)                    # [2,4,6,8,10,12] — one-to-one
nums.filter(lambda x: x % 2 == 0)            # [2,4,6] — keep matching elements
nums.flatMap(lambda x: [x, x*10])            # [1,10,2,20,3,30,...] — one-to-MANY, then flattened
nums.distinct()                              # unique elements
nums.sample(withReplacement=False, fraction=0.5)

a = spark.sparkContext.parallelize([1, 2, 3])
b = spark.sparkContext.parallelize([2, 3, 4])
a.union(b)                                   # [1,2,3,2,3,4] — keeps duplicates, unlike DataFrame union? (no — same: keeps dupes)
a.intersection(b)                            # [2, 3]
a.subtract(b)                                # [1]
```

**`flatMap`** is the one beginners always pause on: `map` gives exactly one output per input; `flatMap` gives *zero or more*, then flattens the results into a single-level RDD. It's the RDD ancestor of DataFrame's [`explode`](09_Complex_Types_and_JSON.md).

### The classic word count (the "hello world" of big data)

```python
text = spark.sparkContext.parallelize([
    "the quick brown fox", "the fox jumps", "the dog sleeps"])

word_counts = (text
    .flatMap(lambda line: line.split(" "))     # → one element per WORD, not per line
    .map(lambda word: (word, 1))               # → ("the", 1), ("quick", 1), ...
    .reduceByKey(lambda a, b: a + b))          # → combine by key: ("the", 3), ("fox", 2), ...

word_counts.collect()
# [('the', 3), ('quick', 1), ('brown', 1), ('fox', 2), ('jumps', 1), ('dog', 1), ('sleeps', 1)]
```

This exact three-line shape is literally what [MapReduce](../00_Fundamentals/05_Hadoop_Architecture.md) automated, and it's why Spark's RDD API has "map" and "reduce" baked into its vocabulary — RDDs were Spark's answer to MapReduce, kept in memory instead of round-tripping to disk every stage.

---

## Level 1 — Actions (run the plan)

```python
nums = spark.sparkContext.parallelize([5, 3, 8, 1, 9])

nums.collect()          # ALL elements to the driver — same OOM danger as df.collect() (file 02)
nums.count()             # 5
nums.first()             # 5 (the first element)
nums.take(3)              # [5, 3, 8] — first 3, safe on big data
nums.reduce(lambda a, b: a + b)      # 26 — combine all elements pairwise into one value
nums.max(), nums.min(), nums.mean(), nums.sum()
nums.foreach(lambda x: print(x))     # run a function per element — for side effects, not return values
nums.saveAsTextFile("path/out/")     # write to storage — one part-file per partition, like df.write
```

Nothing above runs until called — exactly the [lazy evaluation](Spark_Processing.md) rule you already know from DataFrames, because DataFrames are built on this same engine.

---

## Level 2 — Pair RDDs: key-value operations

When RDD elements are `(key, value)` tuples, a whole extra set of operations unlocks — this is where RDDs feel most like a distributed dictionary:

```python
pairs = spark.sparkContext.parallelize([("IT", 60000), ("HR", 50000), ("IT", 65000), ("Fin", 55000)])

pairs.reduceByKey(lambda a, b: a + b)     # [("IT", 125000), ("HR", 50000), ("Fin", 55000)] — sum per key
pairs.groupByKey().mapValues(list)        # [("IT", [60000, 65000]), ...] — group, see warning below
pairs.mapValues(lambda v: v * 1.1)        # transform only the value, keep the key
pairs.keys()                              # ["IT", "HR", "IT", "Fin"]
pairs.values()                            # [60000, 50000, 65000, 55000]
pairs.sortByKey()                         # sorted by key
pairs.countByKey()                        # {'IT': 2, 'HR': 1, 'Fin': 1} — returns a Python dict, not an RDD!

depts = spark.sparkContext.parallelize([("IT", "Technology"), ("HR", "People")])
pairs.join(depts)          # [("IT", (60000, "Technology")), ("IT", (65000, "Technology")), ...]
pairs.leftOuterJoin(depts)  # keeps unmatched left keys, value becomes None
```

### `reduceByKey` vs `groupByKey` — the interview question

Both group by key, but they execute completely differently, and the difference is the #1 RDD performance lesson:

```python
# groupByKey: ships EVERY value across the network, THEN combines
pairs.groupByKey().mapValues(sum)          # all 60000, 65000 travel to one node, summed there

# reduceByKey: combines LOCALLY on each partition first, THEN ships only the partial sums
pairs.reduceByKey(lambda a, b: a + b)      # each node pre-sums its own IT values, tiny result travels
```

This is the exact same **map-side pre-aggregation** that makes DataFrame `groupBy().sum()` cheap ([shuffle mechanics](Spark_Processing.md)) — except with RDDs, *you* must choose the efficient operation; the DataFrame API's optimizer makes this choice for you automatically. That difference alone is most of why the DataFrame API replaced hand-written RDD code for everyday work.

---

## Level 2 — Persistence: cache and persist

```python
big = spark.sparkContext.textFile("huge_file.txt").map(parse_line)

big.cache()             # shorthand for persist(MEMORY_AND_DISK)
big.count()              # first action MATERIALIZES the cache
big.filter(...).count()  # reuses cached data — doesn't re-read/re-parse from scratch

from pyspark import StorageLevel
big.persist(StorageLevel.MEMORY_ONLY)          # fastest, lost if it doesn't fit (recomputed via lineage)
big.persist(StorageLevel.MEMORY_AND_DISK)      # spills to disk instead of dropping (the safe default)
big.persist(StorageLevel.DISK_ONLY)            # for datasets that never fit in RAM
big.unpersist()                                 # free it up when done
```

Identical concept to DataFrame `.cache()` ([Spark_Processing.md](Spark_Processing.md)) — because DataFrame caching *is* this, one layer under the hood.

---

## Level 3 — Pro corner

### How "resilient" actually works: lineage

An RDD never stores a backup copy of your data for safety. Instead, it remembers its **lineage** — the exact chain of transformations that produced it (`textFile → map → filter → reduceByKey`). If a partition is lost when an executor dies, Spark **recomputes just that partition** by replaying its slice of the lineage graph — not the whole dataset, not a restore-from-backup.

```python
rdd = spark.sparkContext.textFile("data.txt").map(parse).filter(is_valid)
rdd.toDebugString()      # prints the lineage graph — every stage this RDD depends on
```

This is the mechanical reason Spark needs no replication layer of its own the way [HDFS](../00_Fundamentals/05_Hadoop_Architecture.md) does — fault tolerance is *recomputation from a recipe*, not *duplication of the dish*. It's cheap until the lineage chain gets very long (hundreds of chained transformations before any action) — at which point recovery itself gets expensive, which is exactly why `checkpoint()` exists: it writes the RDD to reliable storage and **truncates the lineage**, so recovery never has to replay more than one step.

```python
spark.sparkContext.setCheckpointDir("path/checkpoints/")
long_chain_rdd.checkpoint()     # next action also saves it; lineage is cut here
```

### Narrow vs wide dependencies — where shuffles are born

- **Narrow dependency**: each output partition depends on exactly one input partition (`map`, `filter`, `flatMap`). No network movement — [Spark_Processing.md](Spark_Processing.md) calls this a *narrow transformation* and the term originates exactly here.
- **Wide dependency**: an output partition needs data from *many* input partitions (`reduceByKey`, `groupByKey`, `join`, `sortByKey`) → a **shuffle**. This is the RDD-level definition of the same shuffle boundary that ends a [Spark stage](Spark_Architecture.md).

```python
rdd.map(...).filter(...)          # one stage — all narrow, pipelined together on each partition
rdd.map(...).reduceByKey(...)     # TWO stages — the shuffle boundary splits them
```

`toDebugString()` shows this too — indentation levels correspond to stage boundaries.

### Partitioning control

```python
rdd.getNumPartitions()
rdd.repartition(8)                          # full shuffle to redistribute into 8 partitions
rdd.coalesce(2)                             # merge down, no shuffle if reducing count
pairs.partitionBy(8, lambda k: hash(k) % 8) # CUSTOM partitioner — keeps related keys co-located
```

A custom partitioner is real power unavailable at the DataFrame level: if you know `join`s and `reduceByKey`s will repeatedly hit the same keys, partitioning once by that key and reusing the partitioned RDD avoids re-shuffling on every operation — an advanced technique for hand-tuned pipelines.

### Shared variables — broadcast and accumulators

```python
# Broadcast: ship a read-only value to every executor ONCE, instead of once per task/closure
lookup = {"IT": "Technology", "HR": "People"}
bc = spark.sparkContext.broadcast(lookup)
pairs.map(lambda kv: (bc.value.get(kv[0], "Unknown"), kv[1])).collect()

# Accumulator: a write-only counter executors can add to, read only on the driver
bad_rows = spark.sparkContext.accumulator(0)
def validate(line):
    global bad_rows
    if not is_valid(line):
        bad_rows.add(1)
    return line
rdd.foreach(validate)
print(bad_rows.value)     # only trustworthy AFTER an action has fully run
```

These are the RDD-level primitives behind DataFrame [broadcast joins](07_Joins.md) and [UDF closure shipping](10_UDFs_and_Pandas_Integration.md) — same mechanics, same warning: accumulators updated inside a transformation (not an action) can double-count under retries/speculative execution, because the transformation may run more than once. Never use an accumulator for anything that must be exactly correct — use it for approximate monitoring only.

### RDD vs DataFrame vs Dataset — the full picture

| | RDD | DataFrame | Dataset |
|---|---|---|---|
| Contents | Any JVM/Python object | Named, typed columns | Named, typed columns + compile-time types |
| Optimizer | **None** — your code runs as-is | Catalyst — rewrites your plan | Catalyst |
| Speed | Baseline | Fast (JVM-generated code) | Fast |
| Type safety | Full (Python is dynamic, but Scala RDDs are compile-checked) | Runtime only | Compile-time (Scala/Java only — **no Python Dataset**) |
| API level | Low (map/reduce, imperative-ish) | High (declarative, SQL-like) | High + typed |
| When to reach for it | Unstructured data, fine-grained control, legacy code | Everyday PySpark work | Scala/Java teams wanting types |

**Why the DataFrame API won for daily work**: Catalyst can see *what* a `filter`/`select`/`join` means and rewrite it (pushdown, reordering, broadcast decisions — [Catalyst internals](What_Is_Apache_Spark.md)); an RDD `.map(lambda x: ...)` is an opaque Python function the optimizer cannot look inside, so it runs exactly as literally written, in whatever order you wrote it, with no help. This is the RDD-level version of the exact same [UDF penalty](10_UDFs_and_Pandas_Integration.md) you already learned for DataFrames — it isn't a coincidence, a UDF *is* RDD-style opaque code smuggled into a DataFrame pipeline.

### When RDDs are still the right tool today

- Reading genuinely unstructured data with per-record custom logic that has no column shape at all (parsing exotic binary formats, custom scientific data).
- Fine-grained control over partitioning and physical execution that the DataFrame API doesn't expose (custom partitioners above).
- Legacy codebases (pre-2015 Spark code) you're maintaining or migrating.
- Occasionally, `df.rdd.mapPartitions(...)` as an escape hatch when even `pandas_udf`/`mapInPandas` ([file 10](10_UDFs_and_Pandas_Integration.md)) can't express something.

For everything else — which is nearly everything a data engineer does day to day — the DataFrame API ([file 02](02_DataFrame_Basics.md) onward) is strictly better: faster by default, more readable, and optimized automatically.

## Checkpoint

1. Write word count from scratch on `["spark is fast", "spark is fun"]`, and explain what `flatMap` did that `map` couldn't.
2. Why is `reduceByKey` almost always preferred over `groupByKey`? Trace what each ships across the network.
3. An executor dies mid-job. Walk through exactly how Spark recovers the lost partition, and name the concept that makes it possible.
4. You're maintaining an old RDD pipeline with a 200-step transformation chain that keeps failing on executor loss. What single technique would you reach for, and why?

Back to the series: [00 — Learning Path](00_PySpark_Learning_Path.md) · Deeper theory: [What_Is_Apache_Spark.md](What_Is_Apache_Spark.md), [Spark_Architecture.md](Spark_Architecture.md)

---

## Further Learning — Docs & Videos

**Documentation**
- RDD programming guide: https://spark.apache.org/docs/latest/rdd-programming-guide.html
- RDD API (PySpark): https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.RDD.html

**Videos**
- Spark RDDs explained (transformations and actions): https://www.youtube.com/results?search_query=spark+rdd+explained+transformations+actions
