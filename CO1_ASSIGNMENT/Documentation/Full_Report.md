# Task 1: Algorithm Design (5 marks)

Input: array of n student records, unique Registration Number as key. Goal: find the record with key K.

| | Strategy | Style | Design technique | Preprocessing |
|---|---|---|---|---|
| A | Linear search | Iterative | Brute force | None |
| B | Binary search | Recursive | Decrease and conquer | Merge sort by key |
| C | Hash table with chaining | Iterative | Space-time trade-off | Build table from n records |

The three are different ideas: A inspects every record, B discards half of a sorted range per step, C computes where the key must be.

## A: Linear search (iterative)
**Idea:** scan records one by one until a match or the end.
```
LinearSearch(R[0..n-1], K)
  for i <- 0 to n-1 do
      if R[i].key = K then return i
  return -1
```
**Why chosen:** baseline; no preprocessing, works on unordered data, best for tiny or one-off lookups.

## B: Binary search (recursive)
**Idea:** compare K with the middle key of a sorted range; recurse into the half that can contain K.
```
Sort(R) by key                      // preprocessing (merge sort)
BinarySearch(R, K, low, high)
  if low > high then return -1      // base case
  mid <- floor((low + high) / 2)
  if R[mid].key = K then return mid
  else if K < R[mid].key then return BinarySearch(R, K, low, mid-1)
  else return BinarySearch(R, K, mid+1, high)
```
**Why chosen:** exploits ordering to shrink the search space geometrically; supports range queries.

## C: Hash table with separate chaining (iterative)
**Idea:** h(K) = K mod m (m prime near n) maps a key to a bucket; only that short chain is searched.
```
BuildTable(R[0..n-1], m)            // preprocessing
  for each bucket b: b <- empty list
  for i <- 0 to n-1 do insert R[i] at T[h(R[i].key)]

HashSearch(T, K)
  for each p in T[h(K)] do
      if p.key = K then return p
  return null
```
**Why chosen:** a fundamentally different idea (address computation); promises constant average search time, which matters at high request rates.

Code: [`../Task_8_Implementation_Testing/Source_Code/search_algorithms.py`](../Task_8_Implementation_Testing/Source_Code/search_algorithms.py)

# Task 2: Basic Operation (2 marks)

| Algorithm | Basic operation | Where | Why appropriate | Growth of its count with n |
|---|---|---|---|---|
| A Linear | Key comparison `R[i].key = K` | Loop body | Executed every iteration; index increment is proportional to it | Up to n (linear) |
| B Binary | Key comparison `R[mid].key` with K (three-way, counted as one) | Each recursive call | One per call; calls are the only repeated work | +1 each time n doubles |
| B preprocessing | Key comparison in merge step | Merge | Dominates sorting time | About n log2 n |
| C Hash | Key comparison `p.key = K` while walking the chain (hash computation is O(1), counted separately) | While loop | Chain walking is the only variable-length work | Depends on load factor alpha = n/m, not directly on n |

The comparison is the right unit: it is the most frequent operation, hardware independent, and exactly what the loop or recursion repeats. The code counts it directly (`comps += 1`).

# Task 3: Time-Complexity Derivation (6 marks)

Input size n = number of records.

## A: Linear search
- Worst case (last or absent): C(n) = sum_{i=0}^{n-1} 1 = n.
- Key at position i (1-based): C = i.
- Average, successful, each position equally likely: C_avg = (1/n)(1+2+...+n) = (n+1)/2.
- With probability p of being present: C_avg = p(n+1)/2 + n(1-p).
- Preprocessing 0. q searches: q n worst case.

## B: Binary search
After k comparisons at most n/2^k records remain; the search ends when n/2^k < 1, i.e. k > log2 n.
Worst case: C(n) = floor(log2 n) + 1. Check: n = 1,000 -> 10; 10,000 -> 14; 100,000 -> 17; 1,000,000 -> 20.
Average (successful) is about log2 n - 1.
Preprocessing: merge sort T(n) = 2T(n/2) + n -> Theta(n log n) (about 2 x 10^7 comparisons at n = 10^6).
Total for q searches: n log n + q log n.

## C: Hash table
Assume simple uniform hashing; expected chain length = alpha = n/m.
- Unsuccessful search: alpha comparisons expected.
- Successful search: 1 + alpha/2 - alpha/(2n), about 1 + alpha/2.
- With m about n, alpha is about 1, so search is Theta(1 + alpha) = Theta(1).
- Worst case (all keys in one bucket): n.
- Preprocessing: n head-insertions at O(1) plus allocating m buckets: Theta(n).
- Total for q searches: n + q(1 + alpha).

## Overall
| Algorithm | Preprocessing | Per search (worst) | q searches in total |
|---|---|---|---|
| A | 0 | n | q n |
| B | n log n | log n | n log n + q log n |
| C | n | n (rare); expected 1 + alpha | n + q(1 + alpha) |

Break-even of B vs A (average linear cost n/2): n log2 n + q log2 n < q n/2 when q > about 2 log2 n, roughly 40 searches at n = 10^6 (comparison count). Measured wall-clock break-even is larger; see Task 10.

# Task 4: Best, Average and Worst Case (4 marks)

## A: Linear search
- **Best:** key is the first record -> 1 comparison; the loop exits immediately.
- **Average:** key equally likely anywhere -> (n+1)/2 comparisons (half the array scanned).
- **Worst:** key is last or absent -> n comparisons. Absent keys are the costliest because nothing stops the scan early.

## B: Binary search
- **Best:** key is the middle element of the initial range -> 1 comparison.
- **Average:** most elements lie deep in the implicit decision tree (half are at the deepest level) -> about log2 n - 1.
- **Worst:** key at a leaf or absent -> floor(log2 n) + 1. Average and worst differ by about one comparison, so behaviour is very predictable.

## C: Hash table
- **Best:** bucket holds only the target (or is empty for an absent key) -> 1 or 0 comparisons.
- **Average:** chain length alpha -> about 1 + alpha/2 comparisons, provided the hash spreads keys evenly (prime m near n).
- **Worst:** every key collides into one bucket -> single chain of n -> n comparisons. This arises from a poor hash function or adversarial keys, not typical data.

# Task 5: Asymptotic Analysis (3 marks)

| Algorithm | Best | Average | Worst | Tight bound |
|---|---|---|---|---|
| A search | Omega(1) | Theta(n) | O(n) | worst case is Theta(n) |
| B search | Omega(1) | Theta(log n) | O(log n) | average and worst both Theta(log n) |
| B preprocessing | | | | Theta(n log n) |
| C search | Omega(1) | Theta(1) | O(n) | average is Theta(1) |
| C build | | | | Theta(n) |

Growth order: 1 < log n < n < n log n.

From n = 1,000 to 1,000,000 (1000x more data):
- Linear: worst-case work grows 1000x (10^3 -> 10^6 comparisons).
- Binary: 10 -> 20 comparisons (only doubles).
- Hash: stays at about 1 to 2 comparisons.

For the university: linear search degrades visibly as the database grows; binary and hash searches stay effectively instant. What grows is preprocessing (sort about 10^4 -> 2 x 10^7 comparisons; hash build 10^3 -> 10^6 insertions), but it is paid once, not per search.

# Task 6: Recurrence Relation (3 marks)

For recursive binary search:
- **Original problem size:** n (elements between low and high).
- **Subproblem size:** n/2 (one half after discarding the middle).
- **Number of recursive calls:** one (only one half is searched).
- **Work outside the call:** computing mid and one comparison, constant c.
- **Base case:** empty range (low > high) or one element, constant c1.

**T(n) = T(n/2) + c for n > 1, T(1) = c1**

Derived from the algorithm: a = 1 call on size n/b with b = 2, constant extra work. It is not merge sort's recurrence, because the other half is never explored.

# Task 7: Solving the Recurrence (4 marks)

T(n) = T(n/2) + c, T(1) = c1. Assume n = 2^k so n/2 is always an integer.

## Method 1: Iteration (backward substitution)
- T(n) = T(n/2) + c
- = T(n/4) + 2c
- = T(n/8) + 3c
- = ... = T(n/2^i) + i c

Base case when n/2^i = 1, i.e. i = log2 n:

**T(n) = c1 + c log2 n = Theta(log n)**

## Method 2: Master Theorem (verification)
Form T(n) = aT(n/b) + f(n) with a = 1, b = 2, f(n) = c = Theta(1). n^(log_b a) = n^0 = 1. f(n) = Theta(n^0), so **Case 2** applies: T(n) = Theta(n^0 log n) = Theta(log n). Applicable because a >= 1, b > 1 and f is positive.

## Method 3: Induction check
Claim T(n) <= c log2 n + c1. Base T(1) = c1 holds. Step: T(n) = T(n/2) + c <= c log2(n/2) + c1 + c = c log2 n + c1. Holds.

## Interpretation
Doubling the database adds only a constant amount of work (one more comparison). Recursion depth is log2 n, so about 20 stack frames at 10^6 records.

# Task 8: Implementation and Testing (4 marks)

Source code is in `Source_Code/`:

| File | Purpose |
|---|---|
| `search_algorithms.py` | Linear search, recursive binary search + merge sort, hash table with chaining; all count comparisons |
| `test_correctness.py` | Edge-case and randomized correctness tests |
| `run_benchmark.py` | Benchmark at n = 1,000 / 10,000 / 100,000 / 1,000,000; writes `Task_9_Experimental_Performance/results.csv` |
| `make_graphs.py` | Generates graphs and tables into `Report/Tables_and_Graphs/` |

## Test cases
empty database; single record (present / absent); first element (linear best); last element (linear worst); middle element (binary best); absent key below and above range; random present key; randomized agreement of all three algorithms with Python set membership for n = 1, 2, 3, 10, 100, 1000. In the benchmark every query is also checked against set membership for all three algorithms.

Result: `ALL TESTS PASSED` (see `Report/Output_Screenshots/test_output.txt`).

## Procedure (reproducible)
- Same dataset per size: unique 8-digit registration numbers, `random.Random(42)`.
- Same 200 queries for all algorithms: 100 present (random) + 100 absent; `random.Random(7)`.
- Time with `time.perf_counter()`; preprocessing (sort, hash build) timed separately and included in the total-cost analysis.
- Python 3.12 on one machine, no other heavy programs running.

## Run
```
cd Task_8_Implementation_Testing/Source_Code
python test_correctness.py
python run_benchmark.py
python make_graphs.py     # needs matplotlib
```

# Task 9: Experimental Performance (3 marks)

Raw data: [`results.csv`](results.csv). Graphs: `../Report/Tables_and_Graphs/`. 200 mixed queries per size (50% present, 50% absent).

**Average comparisons per search**

| n | Linear avg comps | Binary avg comps | Hash avg comps | Load factor |
|---|---|---|---|---|
| 1,000 | 723.0 | 9.54 | 1.245 | 0.9911 |
| 10,000 | 7,672.5 | 13.06 | 1.250 | 0.9993 |
| 100,000 | 73,661.8 | 16.32 | 1.220 | 1.0000 |
| 1,000,000 | 723,410.5 | 19.40 | 1.305 | 1.0000 |

**Execution time**

| n | Linear (s/search) | Binary (s/search) | Hash (s/search) | Sort (s) | Hash build (s) |
|---|---|---|---|---|---|
| 1,000 | 2.012e-05 | 9.679e-07 | 1.171e-07 | 0.0010 | 0.0001 |
| 10,000 | 2.370e-04 | 1.347e-06 | 1.349e-07 | 0.0136 | 0.0037 |
| 100,000 | 2.358e-03 | 2.020e-06 | 2.415e-07 | 0.1865 | 0.0234 |
| 1,000,000 | 2.374e-02 | 3.035e-06 | 6.223e-07 | 2.3808 | 0.8569 |

Merge-sort comparisons: 8,730 / 120,370 / 1,535,851 / 18,674,298.

**Graphs:** `graph1_comparisons.png`, `graph2_search_time.png`, `graph3_preprocessing.png`, `graph4_total_cost_n1M.png`.

![comparisons](../Report/Tables_and_Graphs/graph1_comparisons.png)
![search time](../Report/Tables_and_Graphs/graph2_search_time.png)
![preprocessing](../Report/Tables_and_Graphs/graph3_preprocessing.png)
![total cost](../Report/Tables_and_Graphs/graph4_total_cost_n1M.png)

These numbers come from one run on the machine used to prepare this repository; rerun `run_benchmark.py` on your own machine and update the tables, since absolute times vary by hardware.

# Task 10: Theory vs Experiment (4 marks)

Data: `../Task_9_Experimental_Performance/results.csv`.

## 1. Comparison counts agree with theory
- **Linear:** with half the queries present and half absent, theory gives 0.5(n+1)/2 + 0.5n, about 0.75n. Measured: 723 (n=1,000) and 723,410 (n=1,000,000) against predictions of about 750 and 750,000. Counts grow about 10x per 10x of n.
- **Binary:** theory is about log2 n (9.97, 13.3, 16.6, 19.9). Measured 9.54, 13.06, 16.32, 19.40. The increase per 10x of n is 3.52, 3.26, 3.08, close to log2 10 = 3.32. Measured values are slightly below log2 n because absent searches and some successful searches stop slightly early.
- **Hash:** theory is 0.5(alpha) + 0.5(1 + alpha/2), about 1.25 at alpha = 1. Measured 1.22 to 1.31, flat across all sizes.
- **Merge sort:** theory n log2 n = 9,966 / 132,877 / 1,660,964 / 19,931,569. Measured 8,730 / 120,370 / 1,535,851 / 18,674,298, i.e. slightly below because merge sort needs about n log2 n - 1.25n comparisons.

## 2. Timing: mostly consistent, with some deviations
- **Linear time** grows 11.8x, 10.0x, 10.1x per 10x of n, matching Theta(n).
- **Binary search time** rises from 0.97 microseconds to 3.04 microseconds (3.1x) while comparison count only doubles (2.03x). Likely cause: for large arrays the probes fall outside CPU cache, so each comparison costs more (memory latency), and each recursive call adds Python call overhead.
- **Hash search time** rises from 0.117 to 0.622 microseconds (5.3x) although comparisons stay flat. Likely cause: random bucket access in a 1M-bucket table of separate Python lists causes cache misses, which the O(1) model ignores.
- **Sort time** grows 2,381x for 1000x more data; n log n predicts about 2,000x. Consistent.
- **Hash build** grows about 6,200x for 1000x more data, worse than the linear prediction. Likely cause: creating 10^6 separate list objects stresses memory allocation and cache. Asymptotically it is still Theta(n) in operations, but constant factors rise with size.

## 3. Which scales better
Hash search is flattest, then binary, then linear. At n = 10^6, per search: linear 23.7 ms, binary 3.0 microseconds (about 7,800x faster), hash 0.62 microseconds (about 38,000x faster than linear, about 4.9x faster than binary).

## 4. Preprocessing and break-even
Break-even against linear search at n = 10^6 (measured times): sort + binary pays off after about 100 searches (theory from comparison counts: about 40); hash after about 36 searches. The measured sort break-even is higher because Python merge sort has a large constant factor (list slicing and appends) that comparison counts do not capture.

## 5. Reasons for differences (summary)
Interpreter overhead, CPU cache and memory effects at large n, memory allocation costs in building 10^6 Python lists, timer resolution at small n (times near 1e-7 s), and single-run measurement noise. Counting comparisons verifies the algorithms' growth; wall-clock time adds hardware effects.

# Task 11: Final Design Recommendation (4 marks)

**Recommended (general case, before the Day-4 constraints): binary search on a sorted array.**

- **Why over linear search:** measured 3.0 microseconds vs 23.7 ms per search at n = 10^6 (about 7,800x faster); only 19.4 comparisons vs 723,410. Sorting (2.38 s) is recovered after about 100 searches.
- **Why over hashing at this stage:** the update rate was unknown. Binary search has a deterministic O(log n) worst case with no collision risk, minimal memory (just the array), and supports ordered operations such as range queries on registration numbers (for example, a whole batch). Hash search is faster in raw time (0.62 microseconds) and cheaper to build (0.86 s), so this choice trades some speed for predictability and ordered access.
- **Theoretical efficiency:** preprocessing Theta(n log n), search Theta(log n).
- **Experimental performance:** comparisons 9.5 / 13.1 / 16.3 / 19.4 for n = 10^3 to 10^6, matching log2 n; time per search only 3.1x higher for 1000x more data.
- **Preprocessing cost:** 2.38 s at n = 10^6 (18.7 million comparisons).
- **Trade-offs and limitations:** inserting into a sorted array costs O(n); frequent updates need a balanced tree or a merge strategy. Recursion uses O(log n) stack (about 20 frames at 10^6).
- **Scalability:** a 1000x larger database only doubles the comparisons, so it remains practical as the database grows.

# Task 12: Day-4 Design Challenge (8 marks)

**Changed requirement:** 50,000 searches per hour on 1,000,000 records; new records added once per day.

Numbers below use the measured data (`../Report/Tables_and_Graphs/day4_numbers.md`).

## A. Impact Analysis (2 marks)
- **What changed:** search volume is now large and specified; updates are rare and batched.
- **Assumptions affected:** earlier we judged the cost of one search. Now the cost is searches per day x cost per search: 50,000/hour is 13.9 per second, or 1.2 million per day if sustained for 24 hours.
- **Why search frequency matters:** a one-off cost (preprocessing) is divided across 1.2 million searches, so its per-search share is negligible, while any per-search cost is multiplied 1.2 million times.
- **Why rare updates matter:** the main weakness of sorted arrays and static hash tables is costly insertion. With one batch per day, the structure can be rebuilt or merged overnight.

## B. Evaluation of the Original Design (2 marks)
- **Under load:** binary search takes about 3.0 microseconds per search, so 13.9 searches/s uses about 0.004% of one core. The original design **remains acceptable**.
- **Preprocessing acceptable?** Sorting takes 2.38 s once per day, against 1.2 million searches (about 2 microseconds amortized per search). Merging a sorted batch of k new records is O(n + k), cheaper than a full re-sort.
- **Better alternative?** Linear search is not viable: 23.7 ms per search x 13.9/s is about 33% of one core permanently, and 28,494 s (7.9 hours) of CPU per day. The hash table is faster still: 0.62 microseconds per search, and builds in 0.86 s versus 2.38 s for sorting.

## C. Adaptation or Redesign (2 marks)
**Decision: MODIFY.** Keep the preprocessing-based architecture but upgrade the index and the update strategy.
- **Revised strategy:** primary index is a hash table (division hashing, prime m near n, chaining), rebuilt in a nightly batch (or extended by O(k) inserts for k new records). The sorted array with binary search is retained as a fallback and for range queries.
- **What changed:** from sort + binary (n log n, then log n) to hash build + hash search (n, then about 1).
- **Complexity effect:** per-search cost Theta(log n) -> expected Theta(1); preprocessing Theta(n log n) -> Theta(n). Measured daily CPU for 1.2M searches: binary 3.64 s (+2.38 s sort) vs hash 0.75 s (+0.86 s build).

## D. Evidence-Based Defence (2 marks)

| Factor (n = 10^6) | Linear | Sort + binary | Hash |
|---|---|---|---|
| Preprocessing (measured) | 0 | 2.38 s | 0.86 s |
| Search time (measured) | 23.7 ms | 3.0 microseconds | 0.62 microseconds |
| Avg comparisons (measured) | 723,410 | 19.4 | 1.31 |
| Daily search CPU for 1.2M searches | 28,494 s | 3.64 s | 0.75 s |
| CPU load at 13.9 req/s | 33% of a core | 0.004% | 0.0009% |
| Break-even vs linear | n/a | about 100 searches | about 36 searches |
| Worst case | n | log n | n (very unlikely) |

The decision follows from: (1) search volume is high enough that any one-off preprocessing becomes negligible; (2) daily updates make rebuilding cheap; (3) hashing has the lowest measured search time and preprocessing cost.

**Honest trade-off:** at 14 requests per second even the original binary-search design is more than fast enough, so hashing gives headroom and lower CPU use rather than rescuing a failing design. Hash tables use more memory, provide no ordered traversal and depend on a good hash function; hence the sorted array is kept for range queries. Only the linear design genuinely fails the new requirement.

