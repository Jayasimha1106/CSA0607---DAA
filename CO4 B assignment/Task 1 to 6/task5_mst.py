"""
CO4 Assignment 4B - Task 5: Three greedy engineers, one network  (Kruskal, Prim, Boruvka)

All three rest on the CUT PROPERTY: for any cut of the vertices, a lightest edge crossing the cut is
safe (some MST contains it).  They differ in WHICH cut they look at:
  Kruskal : globally lightest edge that does not close a cycle   (forest of many growing trees, needs DSU)
  Prim    : lightest edge leaving the ONE growing tree           (single tree, needs priority queue / key[])
  Boruvka : lightest edge leaving EACH component, all at once    (parallel rounds, needs component labels)
Edges carry an id; ties are broken by (weight, id) so every algorithm works with a strict total order.
"""

import heapq
import random
from itertools import combinations

VERTICES = list("ABCDEFGH")

# (u, v, weight)  - unique-weight version
BASE_EDGES = [
    ("A", "B", 4), ("A", "C", 2), ("B", "C", 6), ("B", "D", 3), ("C", "D", 8), ("C", "E", 5), ("D", "E", 7),
    ("D", "F", 9), ("E", "F", 1), ("E", "G", 10), ("F", "G", 11), ("F", "H", 12), ("G", "H", 13),
]
# Modified version: weights changed so that several different MSTs have the same total cost
TIE_EDGES = [
    ("A", "B", 4), ("A", "C", 2), ("B", "C", 4), ("B", "D", 3), ("C", "D", 8), ("C", "E", 5), ("D", "E", 5),
    ("D", "F", 9), ("E", "F", 1), ("E", "G", 10), ("F", "G", 10), ("F", "H", 12), ("G", "H", 12),
]


class DisjointSet:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
        self.find_calls = 0

    def find(self, x):
        self.find_calls += 1
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]       # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.rank[ra] += self.rank[ra] == self.rank[rb]
        return True


def edge_key(index, edge, reverse_ties=False):
    return (edge[2], -index if reverse_ties else index)


# ----------------------------------------------------------------------------- Kruskal
def kruskal(vertices, edges, reverse_ties=False, trace=None):
    ordered = sorted(range(len(edges)), key=lambda i: edge_key(i, edges[i], reverse_ties))
    dsu, chosen, total = DisjointSet(vertices), [], 0
    for i in ordered:
        u, v, w = edges[i]
        if dsu.union(u, v):
            chosen.append(i)
            total += w
            if trace is not None:
                trace.append(f"  ACCEPT {u}-{v} ({w})  joins two different trees   forest edges={len(chosen)}")
        elif trace is not None:
            trace.append(f"  reject {u}-{v} ({w})  endpoints already connected (would close a cycle)")
        if len(chosen) == len(vertices) - 1:
            break
    return chosen, total, {"find_calls": dsu.find_calls, "edges_examined": ordered.index(i) + 1}


# ----------------------------------------------------------------------------- Prim
def prim(vertices, edges, start, reverse_ties=False, trace=None):
    adjacency = {v: [] for v in vertices}
    for i, (u, v, w) in enumerate(edges):
        adjacency[u].append((v, i))
        adjacency[v].append((u, i))
    in_tree, chosen, total = {start}, [], 0
    heap = [(edge_key(i, edges[i], reverse_ties), i, v) for v, i in adjacency[start]]
    heapq.heapify(heap)
    pushes, pops = len(heap), 0
    while heap and len(in_tree) < len(vertices):
        key, i, v = heapq.heappop(heap)
        pops += 1
        if v in in_tree:
            if trace is not None:
                trace.append(f"  skip   {edges[i][0]}-{edges[i][1]} ({edges[i][2]})  both ends already in the tree (stale heap entry)")
            continue
        in_tree.add(v)
        chosen.append(i)
        total += edges[i][2]
        if trace is not None:
            trace.append(f"  ADD    {edges[i][0]}-{edges[i][1]} ({edges[i][2]})  lightest edge leaving tree {sorted(in_tree - {v})} -> adds {v}")
        for nb, j in adjacency[v]:
            if nb not in in_tree:
                heapq.heappush(heap, (edge_key(j, edges[j], reverse_ties), j, nb))
                pushes += 1
    return chosen, total, {"heap_pushes": pushes, "heap_pops": pops}


def prim_array(vertices, edges, start):
    """O(V^2) Prim with a key[] array and no heap - the natural choice for dense graphs."""
    weight = {}
    for u, v, w in edges:
        weight[(u, v)] = weight[(v, u)] = min(w, weight.get((u, v), w))
    key = {v: float("inf") for v in vertices}
    key[start] = 0
    done, total, scans, relax = set(), 0, 0, 0
    for _ in vertices:
        u = min((v for v in vertices if v not in done), key=lambda v: key[v])
        scans += len(vertices)
        done.add(u)
        total += key[u]
        for v in vertices:
            if v not in done and (u, v) in weight:
                relax += 1
                key[v] = min(key[v], weight[(u, v)])
    return total, {"vertex_scans": scans, "relaxations": relax}


# ----------------------------------------------------------------------------- Boruvka
def boruvka(vertices, edges, reverse_ties=False, trace=None):
    dsu, chosen, total, rounds, edge_scans = DisjointSet(vertices), [], 0, 0, 0
    components = len(vertices)
    while components > 1:
        rounds += 1
        cheapest = {}
        for i, (u, v, w) in enumerate(edges):              # every component looks for its lightest outgoing edge
            edge_scans += 1
            cu, cv = dsu.find(u), dsu.find(v)
            if cu == cv:
                continue
            for c in (cu, cv):
                if c not in cheapest or edge_key(i, edges[i], reverse_ties) < edge_key(cheapest[c], edges[cheapest[c]], reverse_ties):
                    cheapest[c] = i
        if trace is not None:
            trace.append(f" Round {rounds}: {components} components; lightest outgoing edge per component: " +
                         ", ".join(f"{c}:{edges[i][0]}-{edges[i][1]}({edges[i][2]})" for c, i in sorted(cheapest.items())))
        for i in sorted(set(cheapest.values()), key=lambda k: edge_key(k, edges[k], reverse_ties)):
            u, v, w = edges[i]
            if dsu.union(u, v):
                chosen.append(i)
                total += w
                components -= 1
                if trace is not None:
                    trace.append(f"   merge via {u}-{v} ({w})")
    return chosen, total, {"rounds": rounds, "edge_scans": edge_scans}


# ----------------------------------------------------------------------------- reference
def all_minimum_spanning_trees(vertices, edges):
    n, best, found = len(vertices), float("inf"), []
    for combo in combinations(range(len(edges)), n - 1):
        dsu = DisjointSet(vertices)
        if all(dsu.union(edges[i][0], edges[i][1]) for i in combo):
            cost = sum(edges[i][2] for i in combo)
            if cost < best:
                best, found = cost, []
            if cost == best:
                found.append(frozenset(combo))
    return best, found


def names(edges, chosen):
    return "{" + ", ".join(f"{edges[i][0]}{edges[i][1]}({edges[i][2]})" for i in sorted(chosen)) + "}"


def random_connected_graph(rng, n, m):
    vertices = list(range(n))
    weights = rng.sample(range(1, 10 * m), m)
    edges, present = [], set()
    for v in range(1, n):
        u = rng.randrange(v)
        edges.append((u, v, weights.pop()))
        present.add((u, v))
    while len(edges) < m:
        u, v = sorted(rng.sample(vertices, 2))
        if (u, v) not in present:
            present.add((u, v))
            edges.append((u, v, weights.pop()))
    return vertices, edges


def main():
    print("=" * 100)
    print("TASK 5  BASE GRAPH (unique weights): 8 vertices, 13 edges")
    print("Edges:", ", ".join(f"{u}{v}({w})" for u, v, w in BASE_EDGES))
    for label, run in (("KRUSKAL", lambda t: kruskal(VERTICES, BASE_EDGES, trace=t)),
                       ("PRIM (start A)", lambda t: prim(VERTICES, BASE_EDGES, "A", trace=t)),
                       ("BORUVKA", lambda t: boruvka(VERTICES, BASE_EDGES, trace=t))):
        trace = []
        chosen, total, counters = run(trace)
        print(f"\n--- {label} construction trace ---")
        print("\n".join(trace))
        print(f"  Final MST edges: {names(BASE_EDGES, chosen)}   Total cost = {total}   counters={counters}")

    print("\n" + "=" * 100)
    print("STRESS TEST - modified weights create ties (BC 6->4, DE 7->5, FG 11->10, GH 13->12)")
    print("Edges:", ", ".join(f"{u}{v}({w})" for u, v, w in TIE_EDGES))
    best, all_msts = all_minimum_spanning_trees(VERTICES, TIE_EDGES)
    print(f"Exhaustive search over C(13,7)=1716 edge subsets: minimum cost = {best}, number of distinct MSTs = {len(all_msts)}")
    results = {}
    for label, fn in (
        ("Kruskal  ties by edge id (low first)", lambda: kruskal(VERTICES, TIE_EDGES)),
        ("Kruskal  ties by edge id (high first)", lambda: kruskal(VERTICES, TIE_EDGES, reverse_ties=True)),
        ("Prim     start A, low-id ties", lambda: prim(VERTICES, TIE_EDGES, "A")),
        ("Prim     start H, high-id ties", lambda: prim(VERTICES, TIE_EDGES, "H", reverse_ties=True)),
        ("Boruvka  low-id ties", lambda: boruvka(VERTICES, TIE_EDGES)),
        ("Boruvka  high-id ties", lambda: boruvka(VERTICES, TIE_EDGES, reverse_ties=True)),
    ):
        chosen, total, _ = fn()
        results[label] = frozenset(chosen)
        print(f"{label:<40} cost={total}  valid MST={frozenset(chosen) in all_msts}  edges={names(TIE_EDGES, chosen)}")
    distinct = len(set(results.values()))
    print(f"Distinct edge sets returned by the six runs: {distinct}; all costs equal {best}; all are genuine MSTs.")

    print("\n" + "=" * 100)
    print("DEPLOYMENT EVIDENCE - operation counters on random graphs (unique weights)")
    rng = random.Random(11)
    for label, n, m in (("A. Sparse  (n=2000, m=4000)", 2000, 4000), ("B. Dense   (n=300,  m=40000)", 300, 40000)):
        vertices, edges = random_connected_graph(rng, n, m)
        _, tk, ck = kruskal(vertices, edges)
        _, tp, cp = prim(vertices, edges, 0)
        _, tb, cb = boruvka(vertices, edges)
        print(f"{label}: costs equal = {tk == tp == tb} ({tk})")
        print(f"   Kruskal : sort of {m} edges (~{m * m.bit_length()} comparisons), edges examined before stopping = {ck['edges_examined']}, DSU finds = {ck['find_calls']}")
        print(f"   Prim(heap): heap pushes = {cp['heap_pushes']}, pops = {cp['heap_pops']}")
        print(f"   Boruvka : rounds = {cb['rounds']} (bound log2 n = {n.bit_length() - 1}), full edge scans = {cb['edge_scans']}")
        if n <= 300:
            tpa, cpa = prim_array(vertices, edges, 0)
            print(f"   Prim(array, no heap): vertex scans = {cpa['vertex_scans']}, relaxations = {cpa['relaxations']}, cost={tpa}")


if __name__ == "__main__":
    main()
