# Q2 – Pseudocode: Sequential Search experiments
```
SequentialSearch(L[0..n-1], key):  comps = 0
  for i = 0 to n-1:
      comps++
      if L[i].ToolID == key: return i, comps     # successful
  return -1, comps                               # unsuccessful: exactly n comparisons

Experiment(sizes):
  for n in sizes:
      L = n random records (ToolID, TechID, IssueTime, Bay)
      best      = comps(search L[0])             # position 1
      middle    = comps(search L[n/2])
      worst     = comps(search L[n-1])
      average   = mean comps over 1000 random existing keys
      miss      = comps(search a key not in L)
      time      = mean wall time of 20 unsuccessful searches
Decision model:  sequential cost/day = Q * n/2     index (hash) cost/day = Q * 1 + U (updates)
```
