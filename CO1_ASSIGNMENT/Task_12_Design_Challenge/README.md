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
