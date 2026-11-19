# Q3 – Pseudocode: Brute-Force String Matching
```
BruteForceMatch(T[0..n-1], P[0..m-1], findAll):  comps = 0; hits = []
  for i = 0 to n-m:                       # every alignment of pattern over text
      j = 0
      while j < m:
          comps++
          if T[i+j] != P[j]: break        # mismatch: abandon this alignment
          j++
      if j == m:
          hits.append(i)
          if not findAll: break
  return hits, comps
```
Test design: T1 best (first pattern char never occurs in text) ; T2 worst (T = A^n, P = A^(m-1)B) ;
T3 random text ; T4 match at index 0 ; T5 periodic text `ABAB…` vs `ABABABABAC`.
