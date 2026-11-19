# Q7 – Pseudocode: Order-and-Prune Closest Pair (redesign of Q4)
```
ClosestPairPrune(D[0..n-1]):
  ax = axis (x or y) with the larger coordinate spread          # preprocessing 1: O(n)
  S  = D sorted by coordinate ax                                 # preprocessing 2: O(n log n), O(n) memory
  best = infinity; calcs = 0
  for i = 0 to n-2:
      for j = i+1 to n-1:
          gap = S[j].ax - S[i].ax                                # >= 0 because S is sorted
          if gap^2 >= best: break                                # PRUNE: all later points are at least `gap` away
          calcs++
          d2 = squared distance(S[i], S[j])
          if d2 < best: best = d2
  return sqrt(best), calcs
```
Invariant that makes pruning safe: distance(S[i],S[k]) >= |S[k].ax - S[i].ax| >= gap >= sqrt(best) for every k >= j,
so no skipped pair can beat the current best.
