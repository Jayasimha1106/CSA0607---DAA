# CO2 Debugging and Optimisation – SentinelOps SOC Alert-Triage Module (CSA06)

```
CO2_Debugging_Optimisation/
├── Pseudocode/         Pseudocode.md – corrected and optimised algorithms
├── Source_Code/        original.py, corrected.py, optimised.py, demo.py,
│                       test_harness.py, debug_steps.py, run_experiments.py
├── Report/             Word report (defects, debugging, optimisation, analysis)
├── Supporting_Files/   test datasets, execution logs, CSV results, graphs, output captures
└── README.md
```

Run from this folder (Python 3.8+; matplotlib only for graphs):

```
python Source_Code/demo.py original|corrected|optimised   # run (from inside Source_Code)
python Source_Code/test_harness.py
python Source_Code/debug_steps.py
python Source_Code/run_experiments.py
```
`demo.py` imports its sibling modules, so run it as `cd Source_Code && python demo.py corrected`.
