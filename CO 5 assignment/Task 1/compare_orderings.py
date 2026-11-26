"""Task B1.3 / B1.4 - Version 1 (input order) vs Version 2 (DSATUR-style) on identical graphs."""
import random
from graph_colouring import colour_graph, valid_colouring
from test_graph_colouring import complete, cycle, WHEEL5, PETERSEN

def hidden_clique(path_len=8):
    # path 0..path_len-1, then K4 on the last four vertices (disconnected from the path)
    e = [(i, i + 1) for i in range(path_len - 1)]
    k = list(range(path_len, path_len + 4))
    e += [(a, b) for i, a in enumerate(k) for b in k[i + 1:]]
    return path_len + 4, e

GROTZSCH = [(0,1),(0,4),(1,2),(2,3),(3,4)] + [(5+i, (i+1) % 5) for i in range(5)] + \
           [(5+i, (i-1) % 5) for i in range(5)] + [(10, 5+i) for i in range(5)]

def random_graph(n, p, seed):
    rnd = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if rnd.random() < p]

GRAPHS = [
    ("G1 Wheel W5, m=3", 6, WHEEL5, 3),
    ("G2 Hidden K4 behind path(8), m=3", *hidden_clique(8), 3),
    ("G3 Groetzsch graph (11v), m=3", 11, GROTZSCH, 3),
    ("G4 Random G(14,0.35) seed 1, m=4", 14, random_graph(14, 0.35, 1), 4),
    ("G5 Random G(14,0.35) seed 2, m=3", 14, random_graph(14, 0.35, 2), 3),
    ("G6 Random G(16,0.30) seed 3, m=3", 16, random_graph(16, 0.30, 3), 3),
]

if __name__ == "__main__":
    print(f"{'Graph':36}{'Ans':6}| {'Measure':22}{'Version 1':>12}{'Version 2':>12}{'Reduction':>11}")
    for name, n, e, m in GRAPHS:
        r1 = colour_graph(n, e, m, "input"); r2 = colour_graph(n, e, m, "dsatur")
        assert r1["colourable"] == r2["colourable"]
        for key, label in (("nodes","Search nodes"),("candidates","Candidate assignments"),
                           ("rejected","Rejected branches"),("backtracks","Backtracks")):
            a, b = r1[key], r2[key]
            red = f"{100*(a-b)/a:.1f}%" if a else "-"
            print(f"{name if key=='nodes' else '':36}{str(r1['colourable']) if key=='nodes' else '':6}| {label:22}{a:>12}{b:>12}{red:>11}")
        print("-" * 100)
