# Task 2: Basic Operation (2 marks)

| Algorithm | Basic operation | Where | Why appropriate | Growth of its count with n |
|---|---|---|---|---|
| A Linear | Key comparison `R[i].key = K` | Loop body | Executed every iteration; index increment is proportional to it | Up to n (linear) |
| B Binary | Key comparison `R[mid].key` with K (three-way, counted as one) | Each recursive call | One per call; calls are the only repeated work | +1 each time n doubles |
| B preprocessing | Key comparison in merge step | Merge | Dominates sorting time | About n log2 n |
| C Hash | Key comparison `p.key = K` while walking the chain (hash computation is O(1), counted separately) | While loop | Chain walking is the only variable-length work | Depends on load factor alpha = n/m, not directly on n |

The comparison is the right unit: it is the most frequent operation, hardware independent, and exactly what the loop or recursion repeats. The code counts it directly (`comps += 1`).
