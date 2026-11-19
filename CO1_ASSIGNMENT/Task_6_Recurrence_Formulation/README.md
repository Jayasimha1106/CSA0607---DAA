# Task 6: Recurrence Relation (3 marks)

For recursive binary search:
- **Original problem size:** n (elements between low and high).
- **Subproblem size:** n/2 (one half after discarding the middle).
- **Number of recursive calls:** one (only one half is searched).
- **Work outside the call:** computing mid and one comparison, constant c.
- **Base case:** empty range (low > high) or one element, constant c1.

**T(n) = T(n/2) + c for n > 1, T(1) = c1**

Derived from the algorithm: a = 1 call on size n/b with b = 2, constant extra work. It is not merge sort's recurrence, because the other half is never explored.
