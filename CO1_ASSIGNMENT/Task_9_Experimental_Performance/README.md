# Task 9: Experimental Performance (3 marks)

Raw data: [`results.csv`](results.csv). Graphs: `../Report/Tables_and_Graphs/`. 200 mixed queries per size (50% present, 50% absent).

**Average comparisons per search**

| n | Linear avg comps | Binary avg comps | Hash avg comps | Load factor |
|---|---|---|---|---|
| 1,000 | 723.0 | 9.54 | 1.245 | 0.9911 |
| 10,000 | 7,672.5 | 13.06 | 1.250 | 0.9993 |
| 100,000 | 73,661.8 | 16.32 | 1.220 | 1.0000 |
| 1,000,000 | 723,410.5 | 19.40 | 1.305 | 1.0000 |

**Execution time**

| n | Linear (s/search) | Binary (s/search) | Hash (s/search) | Sort (s) | Hash build (s) |
|---|---|---|---|---|---|
| 1,000 | 2.012e-05 | 9.679e-07 | 1.171e-07 | 0.0010 | 0.0001 |
| 10,000 | 2.370e-04 | 1.347e-06 | 1.349e-07 | 0.0136 | 0.0037 |
| 100,000 | 2.358e-03 | 2.020e-06 | 2.415e-07 | 0.1865 | 0.0234 |
| 1,000,000 | 2.374e-02 | 3.035e-06 | 6.223e-07 | 2.3808 | 0.8569 |

Merge-sort comparisons: 8,730 / 120,370 / 1,535,851 / 18,674,298.

**Graphs:** `graph1_comparisons.png`, `graph2_search_time.png`, `graph3_preprocessing.png`, `graph4_total_cost_n1M.png`.

![comparisons](../Report/Tables_and_Graphs/graph1_comparisons.png)
![search time](../Report/Tables_and_Graphs/graph2_search_time.png)
![preprocessing](../Report/Tables_and_Graphs/graph3_preprocessing.png)
![total cost](../Report/Tables_and_Graphs/graph4_total_cost_n1M.png)

These numbers come from one run on the machine used to prepare this repository; rerun `run_benchmark.py` on your own machine and update the tables, since absolute times vary by hardware.
