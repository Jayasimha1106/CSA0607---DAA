"""Task B1.1 / B1.4 - test suite and Version-1 vs Version-2 comparison."""
import unittest
from graph_colouring import colour_graph, valid_colouring

def complete(k): return [(i, j) for i in range(k) for j in range(i + 1, k)]
def cycle(k): return [(i, (i + 1) % k) for i in range(k)]
PETERSEN = [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),
            (5,7),(7,9),(9,6),(6,8),(8,5)]
WHEEL5 = cycle(5) + [(i, 5) for i in range(5)]

# (name, n, edges, m, expected_colourable, purpose)
TESTS = [
    ("T1 Even cycle C6, m=2",        6, cycle(6), 2, True,  "colourable, tight m (bipartite)"),
    ("T2 Petersen graph, m=3",      10, PETERSEN, 3, True,  "colourable, non-trivial structure"),
    ("T3 K4, m=3",                   4, complete(4), 3, False, "NOT colourable: clique larger than m"),
    ("T4 Odd cycle C5, m=2",         5, cycle(5), 2, False, "NOT colourable: odd cycle needs 3"),
    ("T5 Wheel W5, m=3",             6, WHEEL5, 3, False, "NOT colourable: chromatic number 4"),
    ("T6 Empty graph (n=0), m=3",    0, [], 3, True,  "boundary: no vertices"),
    ("T7 Single vertex, m=1",        1, [], 1, True,  "boundary: smallest non-empty graph"),
    ("T8 Single vertex, m=0",        1, [], 0, False, "boundary: no colours available"),
    ("T9 5 isolated vertices, m=1",  5, [], 1, True,  "boundary: no conflicts -> one colour suffices"),
    ("T10 K5, m=5",                  5, complete(5), 5, True,  "boundary: m equals chromatic number"),
    ("T11 K5, m=4",                  5, complete(5), 4, False, "boundary: m = chromatic number - 1"),
]

class TestColouring(unittest.TestCase):
    def test_all(self):
        for name, n, e, m, exp, _ in TESTS:
            for strat in ("input", "dsatur"):
                with self.subTest(name=name, strategy=strat):
                    r = colour_graph(n, e, m, strat)
                    self.assertEqual(r["colourable"], exp)
                    if exp:
                        self.assertTrue(valid_colouring(n, e, m, r["colouring"]))

def report():
    print(f"{'Test':30}{'Expect':7}{'Ver':4}{'Result':7}{'Nodes':>6}{'Cand':>6}{'Rej':>5}{'Back':>6}{'Depth':>6}  Colouring / status")
    for name, n, e, m, exp, purpose in TESTS:
        for strat, tag in (("input", "V1"), ("dsatur", "V2")):
            r = colour_graph(n, e, m, strat)
            ok = "PASS" if r["colourable"] == exp and (not exp or valid_colouring(n, e, m, r["colouring"])) else "FAIL"
            print(f"{name:30}{str(exp):7}{tag:4}{str(r['colourable']):7}{r['nodes']:>6}{r['candidates']:>6}"
                  f"{r['rejected']:>5}{r['backtracks']:>6}{r['max_depth']:>6}  {r['colouring']} [{ok}]")

if __name__ == "__main__":
    report()
    print()
    unittest.main(argv=["x"], exit=False, verbosity=1)
