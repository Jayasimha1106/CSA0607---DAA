"""Task B2 - Same size, very different search.  n = 16 vertices, m = 3 colours.

Graph A: sparse, easily 3-colourable (path of 16 vertices).
Graph B: path of 12 vertices followed by a disconnected K4 (vertices 12..15).
         K4 needs 4 colours, so B is NOT 3-colourable, but the contradiction
         lives in the LAST four vertices of the input order.
"""
from graph_colouring import colour_graph

N, M = 16, 3
GRAPH_A = [(i, i + 1) for i in range(15)]
GRAPH_B = [(i, i + 1) for i in range(11)] + [(a, b) for a in range(12, 16) for b in range(a + 1, 16)]

def run(label, edges):
    out = {}
    for strat, tag in (("input", "V1 input-order"), ("dsatur", "V2 DSATUR")):
        r = colour_graph(N, edges, M, strat)
        out[tag] = r
        print(f"{label} | {tag:15} | colourable={str(r['colourable']):5} nodes={r['nodes']:>6} "
              f"candidates={r['candidates']:>6} rejected={r['rejected']:>6} "
              f"backtracks={r['backtracks']:>6} max_depth={r['max_depth']}")
    return out

if __name__ == "__main__":
    print(f"n={N}, m={M}; |E(A)|={len(GRAPH_A)}, |E(B)|={len(GRAPH_B)}")
    print("PREDICTION: B needs far more search than A (contradiction hidden at end of input order;")
    print("            earlier path vertices have ~3*2^11 consistent colourings, each re-explored).")
    a = run("Graph A", GRAPH_A)
    b = run("Graph B", GRAPH_B)
    ra, rb = a["V1 input-order"], b["V1 input-order"]
    print(f"\nV1 ratio B/A: nodes x{rb['nodes']/ra['nodes']:.1f}, backtracks x{rb['backtracks']/max(ra['backtracks'],1):.1f}, "
          f"rejected x{rb['rejected']/max(ra['rejected'],1):.1f}")
    # scaling of the hard family: path length L followed by K4
    print("\nScaling of hard family (V1): path length -> nodes")
    for L in range(4, 17, 2):
        e = [(i, i + 1) for i in range(L - 1)] + [(a, b) for a in range(L, L + 4) for b in range(a + 1, L + 4)]
        r = colour_graph(L + 4, e, 3, "input")
        print(f"  n={L+4:>2}  nodes={r['nodes']:>8}  backtracks={r['backtracks']:>8}")
