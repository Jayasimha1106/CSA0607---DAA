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
