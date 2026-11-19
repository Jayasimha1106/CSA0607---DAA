# Task 8: Implementation and Testing (4 marks)

Source code is in `Source_Code/`:

| File | Purpose |
|---|---|
| `search_algorithms.py` | Linear search, recursive binary search + merge sort, hash table with chaining; all count comparisons |
| `test_correctness.py` | Edge-case and randomized correctness tests |
| `run_benchmark.py` | Benchmark at n = 1,000 / 10,000 / 100,000 / 1,000,000; writes `Task_9_Experimental_Performance/results.csv` |
| `make_graphs.py` | Generates graphs and tables into `Report/Tables_and_Graphs/` |

## Test cases
empty database; single record (present / absent); first element (linear best); last element (linear worst); middle element (binary best); absent key below and above range; random present key; randomized agreement of all three algorithms with Python set membership for n = 1, 2, 3, 10, 100, 1000. In the benchmark every query is also checked against set membership for all three algorithms.

Result: `ALL TESTS PASSED` (see `Report/Output_Screenshots/test_output.txt`).

## Procedure (reproducible)
- Same dataset per size: unique 8-digit registration numbers, `random.Random(42)`.
- Same 200 queries for all algorithms: 100 present (random) + 100 absent; `random.Random(7)`.
- Time with `time.perf_counter()`; preprocessing (sort, hash build) timed separately and included in the total-cost analysis.
- Python 3.12 on one machine, no other heavy programs running.

## Run
```
cd Task_8_Implementation_Testing/Source_Code
python test_correctness.py
python run_benchmark.py
python make_graphs.py     # needs matplotlib
```
