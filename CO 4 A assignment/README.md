# CO4 Assignment 4A – Algorithmic Design through Pseudocode

**Course:** CSA06 Design and Analysis of Algorithms (SIMATS Engineering)
**Outcome:** CO4 – Dynamic Programming and Greedy strategies

The full report (problem analysis, pseudocode, manual traces, calculations, test cases, results,
execution output and source listings) is in `Report/`.

| Task | Topic | Strategy | Program | Verified result |
|------|-------|----------|---------|-----------------|
| 1 | LoadVehicle review (fractional knapsack) | Greedy by value/weight | `Source_Code/Task_1/fractional_knapsack.py` | A(10,60) B(20,100) C(30,120), cap 50 → 240 |
| 2 | Job sequencing with deadlines | Greedy, highest profit, latest free slot | `Source_Code/Task_2/job_sequencing.py` | C, A, D → 180; with B=90: B, A, D → 210 |
| 3 | 0/1 knapsack | DP table `DP[i][w]` + reconstruction | `Source_Code/Task_3/knapsack_dp.py` | W=7 → 45 (items Q, R) |
| 4 | WordBreak forensics | DP debugging | `Source_Code/Task_4/word_break.py` | `abcd` / `{bcd}` exposes missing `DP[j]` test |
| 5 | Dijkstra, Bellman-Ford, Floyd | Greedy / relaxation / DP | `Source_Code/Task_5/shortest_paths.py` | From A: B=4, C=6, D=7, E=10 |
| 6 | Energy-aware scheduling (Design Challenge) | DP – weighted interval scheduling | `Source_Code/Task_6/energy_scheduling.py` | J2, J5, J7, J8 → 200 |

## Run
Python 3, standard library only:

```bash
cd Source_Code/Task_1 && python3 fractional_knapsack.py
```

Each task folder also contains `output.txt` (captured run) and `screenshots/` (output images).
Every program checks itself with assertions and randomised tests against brute-force/reference solutions.

## Structure
```
CO4_Assignment_4A/
├── Source_Code/Task_1 … Task_6/
├── Report/CO4_Assignment_4A_Report.pdf (+ .docx)
└── README.md
```
