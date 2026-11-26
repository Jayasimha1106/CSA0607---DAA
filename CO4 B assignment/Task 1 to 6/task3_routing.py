"""
CO4 Assignment 4B - Task 3: Routing engine under changing network conditions
Dijkstra -> Bellman-Ford (negative edge, negative cycle) -> Floyd + Warshall (all pairs)

Network: 8 locations A..H, directed weighted edges (13 edges).
"""

import heapq

INF = float("inf")
VERTICES = list("ABCDEFGH")

# (from, to, weight)  ---- Stage A : every weight is non-negative
NORMAL_EDGES = [
    ("A", "B", 4), ("A", "C", 5), ("C", "B", 2), ("B", "D", 3), ("C", "D", 6),
    ("D", "E", 2), ("D", "F", 6), ("E", "F", 1), ("E", "G", 5), ("F", "G", 2),
    ("F", "H", 7), ("G", "H", 3), ("C", "E", 8),
]


def with_changes(edges, replace=None, add=None):
    """Return a modified copy of an edge list (replace maps (u,v) -> new weight)."""
    replace = replace or {}
    result = [(u, v, replace.get((u, v), w)) for u, v, w in edges]
    return result + list(add or [])


def build_adjacency(vertices, edges):
    adjacency = {v: [] for v in vertices}
    for u, v, w in edges:
        adjacency[u].append((v, w))
    return adjacency


# ----------------------------------------------------------------------------- shortest paths
def dijkstra(vertices, edges, source):
    """Textbook Dijkstra: a vertex is FINAL once it is extracted; it is never revisited."""
    adjacency = build_adjacency(vertices, edges)
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[source] = 0
    finalised, order = set(), []
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in finalised:
            continue
        finalised.add(u)
        order.append((u, d))
        for v, w in adjacency[u]:
            if v not in finalised and d + w < dist[v]:
                dist[v] = d + w
                pred[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, pred, order


def bellman_ford(vertices, edges, source):
    """Returns (dist, pred, negative_cycle_or_None, passes_used)."""
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[source] = 0
    passes_used = 0
    for _ in range(len(vertices) - 1):
        changed = False
        passes_used += 1
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed = True
        if not changed:                                   # early exit: already converged
            break
    # |V|-th pass: if ANY edge can still be relaxed, a reachable negative cycle exists
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            pred[v] = u
            return dist, pred, extract_cycle(pred, v, len(vertices)), passes_used
    return dist, pred, None, passes_used


def extract_cycle(pred, start, vertex_count):
    """Walk |V| predecessor links to be sure we are INSIDE the cycle, then collect it."""
    node = start
    for _ in range(vertex_count):
        node = pred[node]
    cycle, cur = [node], pred[node]
    while cur != node:
        cycle.append(cur)
        cur = pred[cur]
    cycle.reverse()
    return cycle + [cycle[0]]


def reconstruct_path(pred, source, target):
    path, node = [], target
    while node is not None:
        path.append(node)
        node = pred[node]
    path.reverse()
    return path if path and path[0] == source else []


def floyd_warshall_distance(vertices, edges):
    index = {v: k for k, v in enumerate(vertices)}
    n = len(vertices)
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[None] * n for _ in range(n)]
    for u, v, w in edges:
        if w < dist[index[u]][index[v]]:
            dist[index[u]][index[v]] = w
            nxt[index[u]][index[v]] = index[v]
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    negative_cycle = any(dist[i][i] < 0 for i in range(n))
    return dist, nxt, negative_cycle


def warshall_reachability(vertices, edges):
    index = {v: k for k, v in enumerate(vertices)}
    n = len(vertices)
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v, _ in edges:
        reach[index[u]][index[v]] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    reach[i][j] = reach[i][j] or reach[k][j]
    return reach


# ----------------------------------------------------------------------------- presentation
def print_edges(edges):
    print("Edges:", ", ".join(f"{u}->{v}({w})" for u, v, w in edges), f"   |V|={len(VERTICES)} |E|={len(edges)}")


def print_distance_table(vertices, dist, pred, source):
    print(f"{'Vertex':<8}{'Distance':>9}  {'Predecessor':<12}Path")
    for v in vertices:
        d = "inf" if dist[v] == INF else dist[v]
        path = " -> ".join(reconstruct_path(pred, source, v)) if dist[v] != INF else "unreachable"
        print(f"{v:<8}{d!s:>9}  {str(pred[v]):<12}{path}")


def print_matrix(vertices, matrix, cell):
    print("      " + "".join(f"{v:>5}" for v in vertices))
    for v, row in zip(vertices, matrix):
        print(f"{v:>4}  " + "".join(f"{cell(x):>5}" for x in row))


def fmt_dist(x):
    return "inf" if x == INF else str(x)


def path_from_next(vertices, nxt, i, j):
    if nxt[i][j] is None:
        return [] if i != j else [vertices[i]]
    path = [vertices[i]]
    while i != j:
        i = nxt[i][j]
        path.append(vertices[i])
    return path


def main():
    source = "A"
    print("=" * 100)
    print("STAGE A - NORMAL ROUTING (Dijkstra, source A)")
    print_edges(NORMAL_EDGES)
    dist_a, pred_a, order_a = dijkstra(VERTICES, NORMAL_EDGES, source)
    print("Order in which vertices become finalised:", ", ".join(f"{v}({d})" for v, d in order_a))
    print_distance_table(VERTICES, dist_a, pred_a, source)

    print("\n" + "=" * 100)
    print("STAGE B - NEGATIVE EDGE  (C->B changes from +2 to -3)")
    neg_edges = with_changes(NORMAL_EDGES, replace={("C", "B"): -3})
    print_edges(neg_edges)
    print("PREDICTION (recorded before running):")
    print("  * Dijkstra will NOT remain valid. A->B (4) is cheaper than A->C (5) so B is finalised first with 4,")
    print("    but A->C->B = 5-3 = 2 is shorter. B is already final and is never corrected.")
    print("  * Decision affected: route to B (A->B instead of A->C->B) and every vertex reached through B (D,E,F,G,H);")
    print("    Dijkstra will over-estimate their distances.  Bellman-Ford should give B=2, D=5.")
    dist_d, pred_d, order_d = dijkstra(VERTICES, neg_edges, source)
    print("\nDijkstra on the modified graph (finalisation order):", ", ".join(f"{v}({d})" for v, d in order_d))
    print_distance_table(VERTICES, dist_d, pred_d, source)
    dist_b, pred_b, cycle, passes = bellman_ford(VERTICES, neg_edges, source)
    print(f"\nBellman-Ford on the modified graph (converged after {passes} passes, negative cycle = {cycle})")
    print_distance_table(VERTICES, dist_b, pred_b, source)
    print("\nComparison (Dijkstra vs Bellman-Ford):")
    print(f"{'Vertex':<8}{'Dijkstra':>9}{'BellmanFord':>13}{'Error':>8}")
    for v in VERTICES:
        err = dist_d[v] - dist_b[v]
        print(f"{v:<8}{dist_d[v]!s:>9}{dist_b[v]!s:>13}{err:>8}{'   <-- WRONG' if err else ''}")
    print("ACTUAL: prediction confirmed - Dijkstra reports B=4 via A->B, true shortest is A->C->B = 2; "
          "the error propagates to D,E,F,G,H.")

    print("\n" + "=" * 100)
    print("STAGE C - REACHABLE NEGATIVE-WEIGHT CYCLE  (add D->B = -4, giving cycle B->D->B = 3-4 = -1)")
    cyc_edges = with_changes(neg_edges, add=[("D", "B", -4)])
    print_edges(cyc_edges)
    dist_c, pred_c, cycle_c, passes_c = bellman_ford(VERTICES, cyc_edges, source)
    if cycle_c:
        weight = sum(w for a, b in zip(cycle_c, cycle_c[1:]) for u, v, w in cyc_edges if (u, v) == (a, b))
        print(f"NEGATIVE CYCLE DETECTED: {' -> '.join(cycle_c)}   total weight = {weight}")
        print("Shortest paths are undefined for every vertex reachable from the cycle; no distances are returned.")
        adjacency = build_adjacency(VERTICES, cyc_edges)
        seen, stack = set(cycle_c), list(set(cycle_c))
        while stack:
            for v, _ in adjacency[stack.pop()]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        print("Vertices with undefined shortest distance (reachable from the cycle):", sorted(seen))
    print("For contrast, the misleading answer a careless Dijkstra gives:",
          {v: d for v, d in dijkstra(VERTICES, cyc_edges, source)[0].items()})
    print("Failure-case test: negative cycle NOT reachable from the source must not be reported.")
    island_edges = NORMAL_EDGES + [("X", "Y", 2), ("Y", "X", -5)]
    _, _, island_cycle, _ = bellman_ford(VERTICES + ["X", "Y"], island_edges, source)
    print("  cycle X<->Y unreachable from A -> reported cycle =", island_cycle, "(expected None)")
    print("Edge-case test: source only, no edges ->", bellman_ford(["S"], [], "S")[:3])

    print("\n" + "=" * 100)
    print("STAGE D - ALL PAIRS (Floyd) and REACHABILITY (Warshall) on the Stage-B graph (negative edge, no negative cycle)")
    fl, nxt, has_cycle = floyd_warshall_distance(VERTICES, neg_edges)
    print("Floyd shortest-distance matrix (inf = unreachable):")
    print_matrix(VERTICES, fl, fmt_dist)
    print("Negative cycle found by Floyd (negative diagonal)?", has_cycle)
    i, j = VERTICES.index("A"), VERTICES.index("H")
    print("Route A -> H from Floyd next-hop table:", " -> ".join(path_from_next(VERTICES, nxt, i, j)), "cost", fl[i][j])
    wr = warshall_reachability(VERTICES, neg_edges)
    print("\nWarshall reachability matrix (1 = reachable):")
    print_matrix(VERTICES, wr, lambda x: "1" if x else "0")
    print("Reachability queries: A reaches H?", wr[0][7], "| H reaches A?", wr[7][0], "| C reaches B?", wr[2][1])
    _, _, cyc_found = floyd_warshall_distance(VERTICES, cyc_edges)
    print("Floyd on the Stage-C graph reports negative cycle (diagonal < 0):", cyc_found)


if __name__ == "__main__":
    main()
