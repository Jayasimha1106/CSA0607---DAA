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
