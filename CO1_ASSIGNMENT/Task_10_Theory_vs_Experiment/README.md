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
