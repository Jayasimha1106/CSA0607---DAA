# Task 5: Asymptotic Analysis (3 marks)

| Algorithm | Best | Average | Worst | Tight bound |
|---|---|---|---|---|
| A search | Omega(1) | Theta(n) | O(n) | worst case is Theta(n) |
| B search | Omega(1) | Theta(log n) | O(log n) | average and worst both Theta(log n) |
| B preprocessing | | | | Theta(n log n) |
| C search | Omega(1) | Theta(1) | O(n) | average is Theta(1) |
| C build | | | | Theta(n) |

Growth order: 1 < log n < n < n log n.

From n = 1,000 to 1,000,000 (1000x more data):
- Linear: worst-case work grows 1000x (10^3 -> 10^6 comparisons).
- Binary: 10 -> 20 comparisons (only doubles).
- Hash: stays at about 1 to 2 comparisons.

For the university: linear search degrades visibly as the database grows; binary and hash searches stay effectively instant. What grows is preprocessing (sort about 10^4 -> 2 x 10^7 comparisons; hash build 10^3 -> 10^6 insertions), but it is paid once, not per search.
