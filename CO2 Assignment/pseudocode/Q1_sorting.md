# Q1 – Pseudocode: Selection, Bubble, Insertion Sort (with counters)

## Selection Sort
```
SelectionSort(A[0..n-1]):  comps = 0; swaps = 0
  for i = 0 to n-2:
      min = i
      for j = i+1 to n-1:
          comps++
          if A[j] < A[min]: min = j        # find smallest of the unsorted part
      if min != i: swap(A[i], A[min]); swaps++
  return A, comps, swaps
```
## Bubble Sort (with early-exit flag)
```
BubbleSort(A[0..n-1]):  comps = 0; swaps = 0
  for i = 0 to n-2:
      swapped = false
      for j = 0 to n-2-i:
          comps++
          if A[j] > A[j+1]: swap(A[j], A[j+1]); swaps++; swapped = true
      if swapped == false: break           # a full pass with no swap => already sorted
  return A, comps, swaps
```
## Insertion Sort
```
InsertionSort(A[0..n-1]):  comps = 0; moves = 0
  for i = 1 to n-1:
      v = A[i]; j = i-1
      while j >= 0:
          comps++
          if A[j] > v: A[j+1] = A[j]; moves++; j--
          else: break                      # correct slot found
      A[j+1] = v
  return A, comps, moves
```
## Experiment procedure
```
for each dataset D in {random, sorted, reverse, 95%-sorted+new batch, 95%-scattered, all-equal, min-at-end}:
    for each algorithm S in {Selection, Bubble, Insertion}:
        run S on a COPY of D; verify output == sorted(D); record comps, swaps/moves, time
```
