# Task 4: Best, Average and Worst Case (4 marks)

## A: Linear search
- **Best:** key is the first record -> 1 comparison; the loop exits immediately.
- **Average:** key equally likely anywhere -> (n+1)/2 comparisons (half the array scanned).
- **Worst:** key is last or absent -> n comparisons. Absent keys are the costliest because nothing stops the scan early.

## B: Binary search
- **Best:** key is the middle element of the initial range -> 1 comparison.
- **Average:** most elements lie deep in the implicit decision tree (half are at the deepest level) -> about log2 n - 1.
- **Worst:** key at a leaf or absent -> floor(log2 n) + 1. Average and worst differ by about one comparison, so behaviour is very predictable.

## C: Hash table
- **Best:** bucket holds only the target (or is empty for an absent key) -> 1 or 0 comparisons.
- **Average:** chain length alpha -> about 1 + alpha/2 comparisons, provided the hash spreads keys evenly (prime m near n).
- **Worst:** every key collides into one bucket -> single chain of n -> n comparisons. This arises from a poor hash function or adversarial keys, not typical data.
