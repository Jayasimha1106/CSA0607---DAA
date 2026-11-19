# Q6 – Pseudocode: Exhaustive Search for the Airlift (0/1 selection)
Representation: a candidate = n-bit mask; bit i = 1 means package i is loaded.  Total candidates = 2^n.
```
ExhaustiveAirlift(pkg[0..n-1], limit):
  bestValue = -1; bestMask = 0; candidates = 0; feasible = 0
  for mask = 0 to 2^n - 1:                         # GENERATE every subset
      candidates++
      w = 0; v = 0
      for i = 0 to n-1:
          if bit i of mask is 1: w += pkg[i].weight; v += pkg[i].value
      if w <= limit:                               # FEASIBILITY check
          feasible++
          if v > bestValue: bestValue = v; bestMask = mask      # EVALUATE + RETAIN best
  return decode(bestMask), bestValue

Recursive variant (used for timing): Go(i, w, v, mask):
  if i == n: check feasibility, update best, return
  Go(i+1, w, v, mask)                              # exclude package i
  Go(i+1, w+wt[i], v+val[i], mask | 1<<i)          # include package i
```
