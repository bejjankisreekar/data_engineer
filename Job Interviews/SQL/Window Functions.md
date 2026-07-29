# SQL — Window Functions

## Overview
Window functions compute across a set of rows **related to the current row** without collapsing them (unlike GROUP BY). Essential for ranking, running totals, dedup, and time-series — a guaranteed interview topic.

---

## Anatomy
```sql
FUNCTION() OVER (PARTITION BY col ORDER BY col [ROWS/RANGE frame])
```
- **PARTITION BY** = reset the window per group (optional).
- **ORDER BY** = order within the window.
- **Frame** = which rows are included (running vs whole partition).

---

## The functions (know each)
| Category | Functions |
|---|---|
| Ranking | `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE(n)` |
| Offset | `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE` |
| Aggregate | `SUM`, `AVG`, `COUNT`, `MIN`, `MAX` OVER(...) |

**ROW_NUMBER vs RANK vs DENSE_RANK:** unique / gaps after ties / no gaps.

---

## Common patterns (memorize)
```sql
-- Top-N per group (latest order per customer)
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) rn
  FROM orders
) t WHERE rn = 1;

-- Running total
SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date
                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

-- Month-over-month change
LAG(revenue) OVER (PARTITION BY product ORDER BY month) AS prev_revenue

-- Percentile buckets
NTILE(4) OVER (ORDER BY score) AS quartile
```

---

## GROUP BY vs window
| | GROUP BY | Window |
|---|---|---|
| Rows | Collapses to one per group | **Keeps all rows** |
| Use | Aggregate summary | Per-row calc referencing the group |

---

## Scenario Questions
**S1. "Latest record per key (dedup)."** `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) = 1`.
**S2. "Running/cumulative total."** `SUM(...) OVER (ORDER BY ...)` with a frame.
**S3. "Compare each row to the previous."** `LAG(...)`.
**S4. "3rd highest salary per department."** `DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) = 3`.

---

## Quick Revision
- ✔ Window keeps all rows; GROUP BY collapses
- ✔ ROW_NUMBER (unique) · RANK (gaps) · DENSE_RANK (no gaps) · NTILE (buckets)
- ✔ Dedup = ROW_NUMBER = 1
- ✔ LAG/LEAD = compare to prev/next row
- ✔ Running total = `SUM() OVER (ORDER BY ...)`
- ✔ `LAST_VALUE` needs explicit frame or it returns current row

## Common Interview Mistakes
- Using GROUP BY when you need per-row context.
- `LAST_VALUE` without a proper frame (returns wrong value).
- Confusing RANK and DENSE_RANK.

## Senior-Level Discussion
Seniors note that window functions are the SQL twin of PySpark `Window` — same dedup/ranking patterns move directly into Spark. They're mindful of frame clauses and of sort cost on large partitions.

## Related Topics
[SQL Interview Questions](SQL%20Interview%20Questions.md) · [Query Optimization](Query%20Optimization.md) · [PySpark Partitioning](../PySpark/Partitioning.md)
