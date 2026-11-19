# Task 1: Algorithm Design (5 marks)

Input: array of n student records, unique Registration Number as key. Goal: find the record with key K.

| | Strategy | Style | Design technique | Preprocessing |
|---|---|---|---|---|
| A | Linear search | Iterative | Brute force | None |
| B | Binary search | Recursive | Decrease and conquer | Merge sort by key |
| C | Hash table with chaining | Iterative | Space-time trade-off | Build table from n records |

The three are different ideas: A inspects every record, B discards half of a sorted range per step, C computes where the key must be.

## A: Linear search (iterative)
**Idea:** scan records one by one until a match or the end.
```
LinearSearch(R[0..n-1], K)
  for i <- 0 to n-1 do
      if R[i].key = K then return i
  return -1
```
**Why chosen:** baseline; no preprocessing, works on unordered data, best for tiny or one-off lookups.

## B: Binary search (recursive)
**Idea:** compare K with the middle key of a sorted range; recurse into the half that can contain K.
```
Sort(R) by key                      // preprocessing (merge sort)
BinarySearch(R, K, low, high)
  if low > high then return -1      // base case
  mid <- floor((low + high) / 2)
  if R[mid].key = K then return mid
  else if K < R[mid].key then return BinarySearch(R, K, low, mid-1)
  else return BinarySearch(R, K, mid+1, high)
```
**Why chosen:** exploits ordering to shrink the search space geometrically; supports range queries.

## C: Hash table with separate chaining (iterative)
**Idea:** h(K) = K mod m (m prime near n) maps a key to a bucket; only that short chain is searched.
```
BuildTable(R[0..n-1], m)            // preprocessing
  for each bucket b: b <- empty list
  for i <- 0 to n-1 do insert R[i] at T[h(R[i].key)]

HashSearch(T, K)
  for each p in T[h(K)] do
      if p.key = K then return p
  return null
```
**Why chosen:** a fundamentally different idea (address computation); promises constant average search time, which matters at high request rates.

Code: [`../Task_8_Implementation_Testing/Source_Code/search_algorithms.py`](../Task_8_Implementation_Testing/Source_Code/search_algorithms.py)
