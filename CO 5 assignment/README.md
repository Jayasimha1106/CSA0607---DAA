# CO5 Assignment 5 – Search, Complexity and Approximation Engineering
Course: CSA06 Design and Analysis of Algorithms | Student: Jaya Venkata Simha

## Structure
```
CO5_Assignment_5/
├── Source_Code/
│   ├── Task_B1_Graph_Colouring/        graph_colouring.py, test_graph_colouring.py, compare_orderings.py
│   ├── Task_B2_Adversarial_Search/     adversarial_search.py (+ copy of graph_colouring.py)
│   ├── Task_B3_Exact_vs_Approximation/ set_cover.py, run_experiments.py
│   └── Task_B4_Bin_Packing/            bin_packing.py
├── Report/
│   ├── CO5_Assignment_5_Report.docx / .pdf   (Part A pseudocode + Part B evidence, all 9 tasks)
│   └── *_output.txt                          (raw program output used in the report)
└── README.md
```
## Requirements
Python 3.8+ (standard library only). No installation needed.

## How to run
```
cd Source_Code/Task_B1_Graph_Colouring        && python3 test_graph_colouring.py && python3 compare_orderings.py
cd Source_Code/Task_B2_Adversarial_Search     && python3 adversarial_search.py
cd Source_Code/Task_B3_Exact_vs_Approximation && python3 run_experiments.py
cd Source_Code/Task_B4_Bin_Packing            && python3 bin_packing.py
```
All random inputs use fixed seeds, so results are reproducible (B4 timings vary by machine).

## Instrumentation (B1/B2)
nodes visited, candidate assignments, branches rejected by the feasibility test, backtracks (undo operations), maximum depth, final colouring.
