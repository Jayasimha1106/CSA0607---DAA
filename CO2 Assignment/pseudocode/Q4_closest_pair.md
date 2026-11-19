# Q4 – Pseudocode: Brute-Force Closest Pair
```
ClosestPair(D[0..n-1]):  best = infinity; pairs = 0
  for i = 0 to n-2:
      for j = i+1 to n-1:                 # j > i  => each unordered pair exactly once, no (i,i), no (j,i)
          pairs++
          d2 = (xi-xj)^2 + (yi-yj)^2      # squared distance: sqrt is monotone so comparison is unchanged
          if d2 < best: best = d2; pair = (i, j)
  return sqrt(best), pair, pairs
```
Pair count: sum_{i=0}^{n-2} (n-1-i) = n(n-1)/2 = C(n,2).
