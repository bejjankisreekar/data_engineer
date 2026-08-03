# Practical SQL Query Interview Questions (55 Solved with Explanations)

The **query-writing** problems actually asked in data engineering / analyst interviews (Microsoft, Accenture, TCS, Infosys, Deloitte, product companies). Each has: the **question**, the **answer** (query), and a **clear explanation** of *why* it works. Standard SQL (T-SQL / ANSI); dialect notes at the end. Difficulty: 🟢 Easy · 🟡 Medium · 🔴 Hard.

> Assumed tables:
> `Employee(id, name, salary, dept_id, manager_id, hire_date)` ·
> `Department(dept_id, dept_name)` ·
> `Orders(order_id, customer_id, order_date, amount)` ·
> `Customers(customer_id, name, city)` ·
> `Logins(user_id, login_date)`

---

## A. Salary, Ranking & Top-N

### 1. 🟡 Find the second highest salary
```sql
SELECT MAX(salary) AS second_highest
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);
```
**Explanation:** The subquery finds the top salary. The outer query then finds the **max of everything below it** — which is the 2nd highest. Simple, but only returns one value and doesn't generalize to "Nth". The robust, general version uses ranking:
```sql
SELECT DISTINCT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM Employee
) t WHERE rnk = 2;
```
`DENSE_RANK` assigns 1 to the highest salary, 2 to the next distinct salary, etc. Picking `rnk = 2` gives the 2nd highest and correctly handles **ties** (two people on the top salary still leave the next distinct value as #2).

### 2. 🟡 Find the Nth highest salary (e.g., 3rd)
```sql
SELECT DISTINCT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rnk FROM Employee
) t WHERE rnk = 3;
```
**Explanation:** Same idea as Q1 generalized — `DENSE_RANK` ranks distinct salaries high→low; filter `rnk = N`. Use `DENSE_RANK` (not `ROW_NUMBER`) so tied salaries count as one rank; use `DISTINCT` so ties don't return duplicate rows.

### 3. 🔴 Top 3 earners in each department
```sql
SELECT * FROM (
  SELECT e.*, DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) rnk
  FROM Employee e
) t WHERE rnk <= 3;
```
**Explanation:** `PARTITION BY dept_id` restarts the ranking **within each department**, so every department gets its own 1,2,3… ranking by salary. Filtering `rnk <= 3` keeps the top 3 per department. This "partition + rank + filter" is the single most reused interview pattern.

### 4. 🟡 Highest-paid employee per department
```sql
SELECT * FROM (
  SELECT e.*, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) rn
  FROM Employee e
) t WHERE rn = 1;
```
**Explanation:** `ROW_NUMBER` gives a unique 1,2,3… per department ordered by salary descending, so `rn = 1` is the top earner. `ROW_NUMBER` (not RANK) guarantees exactly **one** row per department even if two people tie on salary.

### 5. 🟢 Employees earning more than the company average
```sql
SELECT * FROM Employee WHERE salary > (SELECT AVG(salary) FROM Employee);
```
**Explanation:** The scalar subquery computes one number — the overall average — and the outer query keeps rows above it. The subquery runs once (non-correlated), so it's efficient.

### 6. 🟡 Employees earning more than their department average
```sql
SELECT * FROM (
  SELECT e.*, AVG(salary) OVER (PARTITION BY dept_id) avg_sal FROM Employee e
) t WHERE salary > avg_sal;
```
**Explanation:** The window `AVG(salary) OVER (PARTITION BY dept_id)` attaches **each department's average** to every row *without collapsing rows* (unlike GROUP BY). Then we simply compare each salary to its own department's average. This avoids a separate GROUP BY + join.

### 7. 🟡 Top 10% earners
```sql
SELECT * FROM (
  SELECT e.*, NTILE(10) OVER (ORDER BY salary DESC) bucket FROM Employee e
) t WHERE bucket = 1;
```
**Explanation:** `NTILE(10)` splits all rows into 10 equal buckets by salary descending; bucket 1 is the top tenth. Great for percentiles/quantiles without manual math.

### 8. 🟡 Rank employees by salary (show the three ranking functions)
```sql
SELECT name, salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) row_num,
  RANK()       OVER (ORDER BY salary DESC) rnk,
  DENSE_RANK() OVER (ORDER BY salary DESC) dense_rnk
FROM Employee;
```
**Explanation:** For salaries 100,100,90: `ROW_NUMBER`=1,2,3 (always unique), `RANK`=1,1,3 (ties share a rank, then a **gap**), `DENSE_RANK`=1,1,2 (ties share, **no gap**). Knowing which to use is a guaranteed follow-up.

---

## B. Duplicates

### 9. 🟡 Find duplicate emails
```sql
SELECT email, COUNT(*) FROM Employee GROUP BY email HAVING COUNT(*) > 1;
```
**Explanation:** GROUP BY collapses rows per email; `COUNT(*)` counts rows in each group; `HAVING COUNT(*) > 1` keeps only emails appearing more than once. `HAVING` filters **groups** (WHERE can't, because the count doesn't exist until after grouping).

### 10. 🔴 Delete duplicates, keep one (lowest id)
```sql
WITH cte AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) rn FROM Employee
)
DELETE FROM cte WHERE rn > 1;
```
**Explanation:** Within each email group, `ROW_NUMBER` numbers the rows by id; the first (`rn = 1`) is the keeper, so we delete everything with `rn > 1`. Deleting through the CTE deletes the underlying base-table rows. Changing the `ORDER BY` decides *which* copy you keep.

### 11. 🟡 Count total vs distinct
```sql
SELECT COUNT(*) total, COUNT(DISTINCT email) distinct_emails FROM Employee;
```
**Explanation:** `COUNT(*)` counts all rows (including duplicates and NULLs); `COUNT(DISTINCT email)` counts unique non-NULL emails. The gap between them reveals how many duplicate/blank emails exist.

### 12. 🟡 Find rows duplicated across multiple columns
```sql
SELECT name, dept_id, COUNT(*) FROM Employee
GROUP BY name, dept_id HAVING COUNT(*) > 1;
```
**Explanation:** Grouping by the **combination** of columns treats a duplicate as "same name AND same dept". `HAVING COUNT(*) > 1` flags combos that repeat. Extend the GROUP BY list to define "duplicate" more strictly.

---

## C. Joins & Missing Records

### 13. 🟢 Customers who never placed an order
```sql
SELECT c.* FROM Customers c
LEFT JOIN Orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```
**Explanation:** A LEFT JOIN keeps all customers; non-matching customers get NULLs on the Orders side. Filtering `o.order_id IS NULL` keeps exactly those with **no matching order** — the "anti-join" pattern. (You must test a column that's NOT NULL when a match exists, like the PK.)

### 14. 🟡 Records in A not in B (three ways)
```sql
-- 1) LEFT JOIN / IS NULL (anti-join)
SELECT a.* FROM A a LEFT JOIN B b ON a.id=b.id WHERE b.id IS NULL;
-- 2) NOT EXISTS (usually fastest, NULL-safe)
SELECT a.* FROM A a WHERE NOT EXISTS (SELECT 1 FROM B b WHERE b.id=a.id);
-- 3) EXCEPT (set difference, also de-dupes)
SELECT id FROM A EXCEPT SELECT id FROM B;
```
**Explanation:** All return rows in A with no counterpart in B. `NOT EXISTS` short-circuits on the first match and is **NULL-safe**; `NOT IN` (a common wrong answer) returns *no rows* if B contains any NULL, because `x <> NULL` is unknown. Prefer `NOT EXISTS`.

### 15. 🟢 Departments with no employees
```sql
SELECT d.* FROM Department d
LEFT JOIN Employee e ON d.dept_id=e.dept_id WHERE e.id IS NULL;
```
**Explanation:** Same anti-join as Q13 from the department side — keep all departments, then keep only those where no employee matched (`e.id IS NULL`).

### 16. 🟡 Employee with their manager's name (self join)
```sql
SELECT e.name AS employee, m.name AS manager
FROM Employee e LEFT JOIN Employee m ON e.manager_id = m.id;
```
**Explanation:** The Employee table is joined **to itself** — one alias (`e`) as the worker, another (`m`) as the manager, linked by `e.manager_id = m.id`. LEFT JOIN keeps top-level employees whose `manager_id` is NULL (they show a NULL manager).

### 17. 🟡 Employees earning more than their manager
```sql
SELECT e.name FROM Employee e
JOIN Employee m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```
**Explanation:** Self join pairs each employee with their manager row; the WHERE compares the two salaries on the **same joined row**. INNER JOIN here (not LEFT) because employees with no manager can't out-earn one.

### 18. 🔴 Count of direct reports per manager (including zero)
```sql
SELECT m.name AS manager, COUNT(e.id) AS reports
FROM Employee m LEFT JOIN Employee e ON e.manager_id = m.id
GROUP BY m.name;
```
**Explanation:** LEFT JOIN keeps every potential manager even if nobody reports to them; `COUNT(e.id)` counts **non-NULL** report ids, so managers with no reports correctly show 0 (whereas `COUNT(*)` would wrongly show 1).

---

## D. Aggregation & GROUP BY

### 19. 🟢 Headcount, total & average salary per department
```sql
SELECT dept_id, COUNT(*) headcount, SUM(salary) total, AVG(salary) avg_sal
FROM Employee GROUP BY dept_id;
```
**Explanation:** GROUP BY collapses employees into one row per department; the aggregates summarize each group. Every non-aggregated column in SELECT must appear in GROUP BY.

### 20. 🟡 Departments with more than 5 employees
```sql
SELECT dept_id, COUNT(*) FROM Employee GROUP BY dept_id HAVING COUNT(*) > 5;
```
**Explanation:** `WHERE` filters rows *before* grouping; `HAVING` filters *after*, on aggregate results. Since the count only exists after grouping, "more than 5 employees" must be a HAVING condition.

### 21. 🟡 Department with the highest total salary
```sql
SELECT TOP 1 dept_id, SUM(salary) total   -- MySQL/Postgres: LIMIT 1
FROM Employee GROUP BY dept_id ORDER BY total DESC;
```
**Explanation:** Aggregate per department, order descending by the total, take the top row. For ties (two departments with the same top total) use `WITH TIES` or a `RANK()` version instead.

### 22. 🟡 Bucket employees into salary bands
```sql
SELECT band, COUNT(*) FROM (
  SELECT CASE WHEN salary < 50000 THEN 'Low'
              WHEN salary < 100000 THEN 'Mid' ELSE 'High' END AS band
  FROM Employee
) t GROUP BY band;
```
**Explanation:** The `CASE` derives a category per row; grouping by that derived column counts how many fall in each band. Wrapping it in a subquery lets us GROUP BY the alias cleanly across dialects.

### 23. 🟢 Min/max/avg order amount per customer
```sql
SELECT customer_id, MIN(amount), MAX(amount), AVG(amount)
FROM Orders GROUP BY customer_id;
```
**Explanation:** One row per customer with their spending range and average — straightforward per-group aggregation.

---

## E. Window Functions

### 24. 🟡 Running (cumulative) total of orders per customer
```sql
SELECT customer_id, order_date, amount,
  SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) running_total
FROM Orders;
```
**Explanation:** The window sums amounts from the first row up to the **current** row, ordered by date, and restarts per customer. The frame (`UNBOUNDED PRECEDING … CURRENT ROW`) is what makes it *cumulative* rather than a grand total.

### 25. 🟡 Month-over-month revenue change
```sql
SELECT month, revenue,
  revenue - LAG(revenue) OVER (ORDER BY month) AS mom_change
FROM MonthlyRevenue;
```
**Explanation:** `LAG(revenue)` pulls the **previous month's** value onto the current row; subtracting gives the change. `LEAD` would look forward instead. The first row's LAG is NULL (no prior month).

### 26. 🟡 Latest order per customer
```sql
SELECT * FROM (
  SELECT o.*, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) rn
  FROM Orders o
) t WHERE rn = 1;
```
**Explanation:** Order each customer's orders newest-first, number them, keep `rn = 1`. This "dedupe to latest per key" is used constantly in CDC/Silver-layer logic (keep the most recent record per business key).

### 27. 🔴 3-day moving average of daily sales
```sql
SELECT sale_date, daily_total,
  AVG(daily_total) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) mov_avg
FROM DailySales;
```
**Explanation:** The frame `2 PRECEDING … CURRENT ROW` = a sliding 3-row window (today + 2 prior days). Averaging over it smooths spikes. Widen the frame for longer moving averages.

### 28. 🟡 First and last order date per customer
```sql
SELECT DISTINCT customer_id,
  FIRST_VALUE(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) first_order,
  LAST_VALUE(order_date)  OVER (PARTITION BY customer_id ORDER BY order_date
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) last_order
FROM Orders;
```
**Explanation:** `FIRST_VALUE`/`LAST_VALUE` return boundary values of the window. **Trap:** by default the frame ends at the current row, so `LAST_VALUE` would return the current row's date — you must widen the frame to the whole partition (`UNBOUNDED FOLLOWING`) to get the true last value.

### 29. 🟡 Each employee's share of department salary
```sql
SELECT name, salary,
  salary * 100.0 / SUM(salary) OVER (PARTITION BY dept_id) AS pct_of_dept
FROM Employee;
```
**Explanation:** `SUM(salary) OVER (PARTITION BY dept_id)` gives the department total on every row; dividing salary by it yields each person's percentage. `* 100.0` forces decimal division (avoids integer truncation).

---

## F. Date & Time

### 30. 🟢 Orders in the last 30 days
```sql
SELECT * FROM Orders WHERE order_date >= DATEADD(DAY, -30, GETDATE());
-- Postgres: WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
```
**Explanation:** Compute the cutoff date once and keep rows on/after it. Writing it as `order_date >= cutoff` (not a function on `order_date`) keeps the predicate **SARGable** so an index on `order_date` can be used.

### 31. 🟡 Orders per month
```sql
SELECT FORMAT(order_date,'yyyy-MM') ym, COUNT(*), SUM(amount)
FROM Orders GROUP BY FORMAT(order_date,'yyyy-MM') ORDER BY ym;
```
**Explanation:** Formatting the date to `yyyy-MM` buckets every order into its calendar month; grouping by that string aggregates per month. (For big tables, grouping on a computed date column can prevent index use — acceptable for reporting.)

### 32. 🟡 Employees hired this year
```sql
-- SARGable version:
SELECT * FROM Employee
WHERE hire_date >= DATEFROMPARTS(YEAR(GETDATE()),1,1);
```
**Explanation:** `WHERE YEAR(hire_date) = YEAR(GETDATE())` works but wraps the column in a function → **no index seek** (full scan). Rewriting as `hire_date >= Jan-1-this-year` is SARGable and index-friendly — a classic senior distinction.

### 33. 🔴 Customers who ordered in 3+ consecutive months
```sql
WITH m AS (
  SELECT DISTINCT customer_id, DATEFROMPARTS(YEAR(order_date),MONTH(order_date),1) mth
  FROM Orders
),
r AS (
  SELECT customer_id, mth,
    DATEADD(MONTH, -ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY mth), mth) grp
  FROM m
)
SELECT DISTINCT customer_id FROM r GROUP BY customer_id, grp HAVING COUNT(*) >= 3;
```
**Explanation:** This is **gaps-and-islands**. For a consecutive run of months, `month − row_number` stays **constant** (both increase by 1 each step), so that constant becomes a group id per streak. Counting rows per streak and keeping `>= 3` finds runs of 3+ consecutive months.

### 34. 🟡 Days between consecutive orders per customer
```sql
SELECT customer_id, order_date,
  DATEDIFF(DAY, LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date), order_date) days_gap
FROM Orders;
```
**Explanation:** `LAG(order_date)` gives the previous order's date for the same customer; `DATEDIFF` measures the gap. Useful for churn/frequency analysis. First order per customer shows NULL (no previous).

---

## G. Gaps & Islands / Streaks

### 35. 🔴 Longest streak of consecutive login days per user
```sql
WITH r AS (
  SELECT user_id, login_date,
    DATEADD(DAY, -ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date), login_date) grp
  FROM (SELECT DISTINCT user_id, login_date FROM Logins) x
)
SELECT user_id, MAX(streak) longest FROM (
  SELECT user_id, grp, COUNT(*) streak FROM r GROUP BY user_id, grp
) s GROUP BY user_id;
```
**Explanation:** Same trick as Q33 but on days: `date − row_number` is constant within a consecutive run, forming a streak id. Count rows per streak, then take the max streak per user. De-dupe logins first so multiple logins on one day don't break the math.

### 36. 🔴 Find missing sequence numbers
```sql
SELECT id + 1 AS missing_from
FROM Seq s
WHERE NOT EXISTS (SELECT 1 FROM Seq n WHERE n.id = s.id + 1)
  AND id < (SELECT MAX(id) FROM Seq);
```
**Explanation:** For each id, if `id + 1` doesn't exist in the table, there's a gap starting after it. Excluding the max id avoids flagging the natural end of the sequence.

---

## H. Self-Join & Comparison

### 37. 🟡 Pairs of employees in the same department
```sql
SELECT a.name, b.name, a.dept_id
FROM Employee a JOIN Employee b
  ON a.dept_id = b.dept_id AND a.id < b.id;
```
**Explanation:** Self-join on department produces all same-dept combinations. The condition `a.id < b.id` removes self-pairs (a with itself) and mirror duplicates (A-B vs B-A), leaving each unordered pair once.

### 38. 🟡 Values appearing in 3 consecutive rows (LeetCode "Consecutive Numbers")
```sql
SELECT DISTINCT l1.num
FROM Logs l1 JOIN Logs l2 ON l1.id = l2.id-1 AND l1.num=l2.num
             JOIN Logs l3 ON l1.id = l3.id-2 AND l1.num=l3.num;
```
**Explanation:** Join the table to itself three times on consecutive ids (`id`, `id+1`, `id+2`) requiring the same `num` each time. A row survives only if the same value repeats across three consecutive ids.

---

## I. Conditional Aggregation / Pivot

### 39. 🟡 Count orders by status in one row (pivot with CASE)
```sql
SELECT customer_id,
  SUM(CASE WHEN status='shipped' THEN 1 ELSE 0 END) shipped,
  SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) pending
FROM Orders GROUP BY customer_id;
```
**Explanation:** Each `CASE` outputs 1 only for the matching status, so summing it counts that status. This "conditional aggregation" pivots rows into columns without a PIVOT operator (works in every dialect, including Spark SQL).

### 40. 🟡 Pivot monthly sales into columns
```sql
SELECT product,
  SUM(CASE WHEN MONTH(sale_date)=1 THEN amount END) Jan,
  SUM(CASE WHEN MONTH(sale_date)=2 THEN amount END) Feb
FROM Sales GROUP BY product;
```
**Explanation:** Same conditional-aggregation trick, summing `amount` only for the target month into each column. `ELSE` omitted → NULLs for non-matching months, which SUM ignores.

### 41. 🟡 Percentage of shipped orders per customer
```sql
SELECT customer_id,
  100.0 * SUM(CASE WHEN status='shipped' THEN 1 ELSE 0 END) / COUNT(*) pct_shipped
FROM Orders GROUP BY customer_id;
```
**Explanation:** Numerator counts shipped orders (conditional sum), denominator counts all orders; `100.0 *` forces decimal division. A rate = conditional count ÷ total count.

---

## J. NULL Handling

### 42. 🟢 Replace NULL salary with 0
```sql
SELECT name, COALESCE(salary, 0) salary FROM Employee;
```
**Explanation:** `COALESCE` returns the first non-NULL argument, so NULL salaries become 0. It's ANSI-standard and accepts many arguments (unlike `ISNULL`).

### 43. 🟡 Employees with no manager
```sql
SELECT * FROM Employee WHERE manager_id IS NULL;
```
**Explanation:** NULL means "unknown/absent", so you must test with `IS NULL` — `= NULL` never matches because any comparison to NULL evaluates to *unknown*.

### 44. 🟡 COALESCE vs ISNULL vs NULLIF
```sql
SELECT COALESCE(nick, name, 'unknown') AS display_name,  -- first non-null (ANSI, N args)
       ISNULL(nick, 'n/a')             AS tsql_only,       -- T-SQL, exactly 2 args
       NULLIF(a, b)                     AS null_if_equal    -- NULL if a=b
FROM Employee;
```
**Explanation:** `COALESCE` = portable, multi-argument default. `ISNULL` = T-SQL only, two arguments. `NULLIF(a,b)` returns NULL when a=b — handy to avoid divide-by-zero: `x / NULLIF(y,0)`.

---

## K. String Manipulation

### 45. 🟡 Extract the domain from an email
```sql
SELECT email, SUBSTRING(email, CHARINDEX('@', email)+1, LEN(email)) domain FROM Users;
```
**Explanation:** `CHARINDEX('@', email)` finds the @ position; `SUBSTRING` from one char after it to the end returns everything after @ (the domain). Overshooting the length is safe — SUBSTRING just stops at the end.

### 46. 🟡 Clean and capitalize a name
```sql
SELECT TRIM(name),
       UPPER(LEFT(name,1)) + LOWER(SUBSTRING(name,2,LEN(name))) AS proper
FROM Employee;
```
**Explanation:** `TRIM` removes stray spaces; capitalize the first letter and lowercase the rest to normalize casing. String cleaning like this is bread-and-butter Silver-layer work.

### 47. 🟡 Names starting with 'A' or containing 'son'
```sql
SELECT * FROM Employee WHERE name LIKE 'A%' OR name LIKE '%son%';
```
**Explanation:** `%` matches any sequence of characters. `'A%'` = starts with A; `'%son%'` = contains "son". Note a leading `%` prevents index use (scan) — fine for ad-hoc, costly at scale.

---

## L. Advanced

### 48. 🔴 Median salary
```sql
SELECT DISTINCT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) OVER () median FROM Employee;
```
**Explanation:** `PERCENTILE_CONT(0.5)` returns the value at the 50th percentile (the median), interpolating between the two middle values for even counts. `WITHIN GROUP (ORDER BY salary)` defines the ordered set it works on.

### 49. 🔴 Mode (most frequent salary)
```sql
SELECT TOP 1 salary FROM Employee GROUP BY salary ORDER BY COUNT(*) DESC;
```
**Explanation:** Count how often each salary occurs, order by that count descending, take the top — the most common value. Use `WITH TIES` if multiple salaries share the top frequency.

### 50. 🔴 Percentile rank / cumulative distribution
```sql
SELECT name, salary,
  CUME_DIST()    OVER (ORDER BY salary) cume,
  PERCENT_RANK() OVER (ORDER BY salary) pr
FROM Employee;
```
**Explanation:** `CUME_DIST` = fraction of rows with a value ≤ the current one; `PERCENT_RANK` = relative rank in [0,1]. Both describe where each salary sits in the distribution — useful for "top X%" logic.

### 51. 🟡 Second highest salary per department
```sql
SELECT * FROM (
  SELECT e.*, DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) rnk
  FROM Employee e
) t WHERE rnk = 2;
```
**Explanation:** Combines Q2 (Nth highest) with Q3 (per group): partition by department, rank salaries descending, keep rank 2. `DENSE_RANK` so ties on the top salary still leave a genuine "second" value.

### 52. 🟡 Total spend > 10000 customers
```sql
SELECT customer_id, SUM(amount) total FROM Orders
GROUP BY customer_id HAVING SUM(amount) > 10000;
```
**Explanation:** Aggregate spend per customer; `HAVING` filters on the aggregate (WHERE can't reference `SUM`). Returns high-value customers.

### 53. 🟡 Top customer by revenue each year
```sql
SELECT * FROM (
  SELECT YEAR(order_date) yr, customer_id, SUM(amount) rev,
    RANK() OVER (PARTITION BY YEAR(order_date) ORDER BY SUM(amount) DESC) rnk
  FROM Orders GROUP BY YEAR(order_date), customer_id
) t WHERE rnk = 1;
```
**Explanation:** First aggregate revenue per customer per year (GROUP BY), then rank within each year (`PARTITION BY year`) and keep the top. Note you can use `SUM(amount)` **inside** the window's ORDER BY because windows run *after* GROUP BY.

### 54. 🔴 Flag employees with duplicate salaries
```sql
SELECT name, salary,
  CASE WHEN COUNT(*) OVER (PARTITION BY salary) > 1 THEN 'dup' ELSE 'unique' END salary_flag
FROM Employee;
```
**Explanation:** `COUNT(*) OVER (PARTITION BY salary)` counts how many people share each salary, attached to every row without collapsing. If more than one, flag it — a window-based way to label duplicates while keeping all rows.

### 55. 🟡 Second highest without TOP/LIMIT/OFFSET
```sql
SELECT MAX(salary) FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);
```
**Explanation:** A pure-aggregate solution when the interviewer bans `TOP`/`LIMIT`/window functions: the highest salary strictly below the overall maximum is the second highest. Elegant, but doesn't generalize to Nth (that needs ranking).

---

## Dialect cheat notes
| Task | T-SQL (Azure SQL/Synapse) | MySQL / Postgres / Spark SQL |
|---|---|---|
| Limit rows | `SELECT TOP n` | `LIMIT n` |
| Date add | `DATEADD(DAY,-30,GETDATE())` | `CURRENT_DATE - INTERVAL '30 days'` |
| Null default | `ISNULL(x,0)` | `COALESCE(x,0)` (works everywhere) |
| String concat | `a + b` | `CONCAT(a,b)` / `a \|\| b` |
| Current date | `GETDATE()` | `CURRENT_DATE` / `now()` |
| First non-null | `COALESCE` (portable) | `COALESCE` |

---

## Top patterns to memorize (the 80/20)
- ✔ **Nth highest / top-N per group** → `DENSE_RANK`/`ROW_NUMBER` + `PARTITION BY` + filter
- ✔ **Deduplicate / latest per key** → `ROW_NUMBER() = 1`
- ✔ **Missing records** → LEFT JOIN + `IS NULL`, or `NOT EXISTS` (never `NOT IN` with NULLs)
- ✔ **Running total / moving avg** → `SUM/AVG OVER (ORDER BY ... ROWS ...)`
- ✔ **Prev/next comparison** → `LAG`/`LEAD`
- ✔ **Consecutive streaks** → gaps-and-islands (`date − ROW_NUMBER = group id`)
- ✔ **Pivot** → conditional `SUM(CASE WHEN ...)`
- ✔ **Group filter** → `HAVING`
- ✔ **Self join** → employee/manager, pairs (`a.id < b.id`)
- ✔ **SARGable predicates** → never wrap the filtered column in a function

> Practice live on **LeetCode (Top SQL 50)**, **HackerRank SQL**, and **StrataScratch** — interviewers pull heavily from them.

---

# 🔗 LeetCode SQL Problems (with problem numbers)

The questions above map directly to real LeetCode problems. Solve these on LeetCode to practice live. URL pattern: `https://leetcode.com/problems/<name>/`.

## Direct LeetCode equivalents of the questions in this file
| This file Q# | LeetCode # | Problem name | Difficulty |
|---|---|---|---|
| Q1, Q55 | **176** | Second Highest Salary | 🟡 Medium |
| Q2 | **177** | Nth Highest Salary | 🟡 Medium |
| Q8 | **178** | Rank Scores | 🟡 Medium |
| Q3, Q51 | **185** | Department Top Three Salaries | 🔴 Hard |
| Q4 | **184** | Department Highest Salary | 🟡 Medium |
| Q9 | **182** | Duplicate Emails | 🟢 Easy |
| Q10 | **196** | Delete Duplicate Emails | 🟢 Easy |
| Q13 | **183** | Customers Who Never Order | 🟢 Easy |
| Q16, Q17 | **181** | Employees Earning More Than Their Managers | 🟢 Easy |
| Q18 | **570 / 1731** | Managers with ≥5 Reports / Number of Employees Reporting | 🟡/🟢 |
| Q30, Q34 | **197** | Rising Temperature | 🟢 Easy |
| Q33, Q35 | **1321 / 603** | Restaurant Growth / Consecutive Available Seats | 🟡 |
| Q38 | **180** | Consecutive Numbers | 🟡 Medium |
| Q39, Q40 | **1179** | Reformat Department Table (pivot) | 🟢 Easy |
| Q42, Q44 | **1683 / 1327** | Invalid Tweets / List Products in a Period | 🟢 Easy |
| Q45, Q46 | **1667** | Fix Names in a Table | 🟢 Easy |
| Q47 | **1527** | Patients With a Condition | 🟢 Easy |
| Q54, Q55 | **627** | Swap Salary | 🟢 Easy |
| Q26 (latest per key) | **1070 / 550** | Product Sales Analysis III / Game Play Analysis IV | 🟡 |
| Q22 (bucketing) | **1907** | Count Salary Categories | 🟡 Medium |
| Q37 (self-join pairs) | **1050** | Actors and Directors Who Cooperated ≥3 Times | 🟢 Easy |

## LeetCode "SQL 50" study plan — must-solve (in order, with numbers)
> The official free study plan: https://leetcode.com/studyplan/top-sql-50/

**Select & basics**
- **1757** Recyclable and Low Fat Products 🟢
- **584** Find Customer Referee 🟢
- **595** Big Countries 🟢
- **1148** Article Views I 🟢
- **1683** Invalid Tweets 🟢

**Joins**
- **1378** Replace Employee ID With The Unique Identifier 🟢
- **1068** Product Sales Analysis I 🟢
- **1581** Customer Who Visited but Did Not Make Any Transactions 🟢
- **197** Rising Temperature 🟢
- **1661** Average Time of Process per Machine 🟢
- **577** Employee Bonus 🟢
- **1280** Students and Examinations 🟢
- **570** Managers with at Least 5 Direct Reports 🟡
- **1934** Confirmation Rate 🟡

**Aggregate functions**
- **620** Not Boring Movies 🟢
- **1075** Project Employees I 🟢
- **1633** Percentage of Users Attended a Contest 🟢
- **1211** Queries Quality and Percentage 🟢
- **1193** Monthly Transactions I 🟡
- **1174** Immediate Food Delivery II 🟡
- **550** Game Play Analysis IV 🟡

**Sorting & grouping**
- **2356** Number of Unique Subjects Taught by Each Teacher 🟢
- **1141** User Activity for the Past 30 Days I 🟢
- **1070** Product Sales Analysis III 🟡
- **596** Classes More Than 5 Students 🟢
- **1729** Find Followers Count 🟢
- **619** Biggest Single Number 🟢
- **1045** Customers Who Bought All Products 🟡

**Advanced select & joins**
- **1731** The Number of Employees Which Report to Each Employee 🟢
- **1789** Primary Department for Each Employee 🟢
- **610** Triangle Judgement 🟢
- **1164** Product Price at a Given Date 🟡
- **1204** Last Person to Fit in the Bus 🟡
- **1907** Count Salary Categories 🟡

**Subqueries**
- **1978** Employees Whose Manager Left the Company 🟢
- **626** Exchange Seats 🟡
- **1341** Movie Rating 🟡
- **1321** Restaurant Growth 🟡
- **602** Friend Requests II: Who Has the Most Friends 🟡
- **585** Investments in 2016 🟡
- **185** Department Top Three Salaries 🔴

**String functions & regex**
- **1667** Fix Names in a Table 🟢
- **1527** Patients With a Condition 🟢
- **196** Delete Duplicate Emails 🟢
- **176** Second Highest Salary 🟡
- **1484** Group Sold Products By The Date 🟢
- **1327** List the Products Ordered in a Period 🟢
- **1517** Find Users With Valid E-Mails 🟢

## Classic must-solve beyond the 50 (frequently asked)
- **176** Second Highest Salary 🟡
- **177** Nth Highest Salary 🟡
- **178** Rank Scores 🟡
- **180** Consecutive Numbers 🟡
- **181** Employees Earning More Than Their Managers 🟢
- **182** Duplicate Emails 🟢
- **183** Customers Who Never Order 🟢
- **184** Department Highest Salary 🟡
- **185** Department Top Three Salaries 🔴
- **196** Delete Duplicate Emails 🟢
- **197** Rising Temperature 🟢
- **262** Trips and Users 🔴
- **569** Median Employee Salary 🔴
- **570** Managers with at Least 5 Direct Reports 🟡
- **571** Find Median Given Frequency of Numbers 🔴
- **574** Winning Candidate 🟡
- **578** Get Highest Answer Rate Question 🟡
- **601** Human Traffic of Stadium 🔴
- **602** Friend Requests II 🟡
- **608** Tree Node 🟡
- **612** Shortest Distance in a Plane 🟡
- **614** Second Degree Follower 🟡
- **626** Exchange Seats 🟡
- **627** Swap Salary 🟢
- **1194** Tournament Winners 🔴
- **1225** Report Contiguous Dates 🔴

**How to practice:** do the **SQL 50** first (covers 90% of interview patterns), then the classic Hard ones (185, 262, 601, 569/571 median, 1225 gaps-and-islands). Time yourself — most interviews give 15–20 min per query.
