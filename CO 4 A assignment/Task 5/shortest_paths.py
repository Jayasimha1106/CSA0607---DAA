"""Task 5 - Dijkstra, Bellman-Ford and Floyd-Warshall on the same graph."""
import heapq

INF = float("inf")
V = ["A", "B", "C", "D", "E"]
E = [("A", "B", 4), ("A", "C", 7), ("B", "C", 2), ("B", "D", 6),
     ("C", "D", 1), ("D", "E", 3), ("C", "E", 8)]


def fmt(x):
    return "INF" if x == INF else str(x)


def dijkstra(V, E, src, trace=False):
    adj = {v: [] for v in V}
    for u, v, w in E:
        adj[u].append((v, w))
    dist = {v: INF for v in V}; pred = {v: None for v in V}
    dist[src] = 0
    done, pq = set(), [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        if trace:
            print(f"  EXTRACT {u} (dist={d}) -> finalised")
        for v, w in adj[u]:
            if v in done:
                continue
            if dist[u] + w < dist[v]:
                if trace:
                    print(f"    relax {u}->{v} (w={w}): {fmt(dist[v])} -> {dist[u] + w}, pred[{v}]={u}")
                dist[v] = dist[u] + w; pred[v] = u
                heapq.heappush(pq, (dist[v], v))
            elif trace:
                print(f"    relax {u}->{v} (w={w}): {dist[u] + w} >= {fmt(dist[v])}, no change")
    return dist, pred


def bellman_ford(V, E, src, trace=False):
    dist = {v: INF for v in V}; pred = {v: None for v in V}
    dist[src] = 0
    for k in range(1, len(V)):
        changed = False
        for u, v, w in E:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; pred[v] = u; changed = True
        if trace:
            print(f"  pass {k}: " + ", ".join(f"{v}={fmt(dist[v])}" for v in V))
        if not changed:
            break
    neg_cycle = any(dist[u] != INF and dist[u] + w < dist[v] for u, v, w in E)
    return dist, pred, neg_cycle


def show(D, V, title):
    print(f"  {title}")
    print("        " + "".join(f"{v:>5}" for v in V))
    for i, v in enumerate(V):
        print(f"      {v} " + "".join(f"{fmt(x):>5}" for x in D[i]))


def floyd(V, E, trace=False):
    n = len(V); idx = {v: i for i, v in enumerate(V)}
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in E:
        D[idx[u]][idx[v]] = min(D[idx[u]][idx[v]], w)
    if trace:
        show(D, V, "D(0): direct edges only")
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] != INF and D[k][j] != INF and D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
        if trace:
            show(D, V, f"D({k+1}): intermediates allowed = {{{', '.join(V[:k+1])}}}")
    return D


def path(pred, t):
    p = []
    while t is not None:
        p.append(t); t = pred[t]
    return "->".join(reversed(p))


if __name__ == "__main__":
    print("=== Task 5.1 Dijkstra from A ===")
    d, p = dijkstra(V, E, "A", trace=True)
    for v in V:
        print(f"  dist[{v}]={fmt(d[v])}  pred={p[v]}  path={path(p, v)}")
    assert d == {"A": 0, "B": 4, "C": 6, "D": 7, "E": 10}

    print("\n=== Task 5.2 Bellman-Ford from A (same graph) ===")
    d2, p2, nc = bellman_ford(V, E, "A", trace=True)
    print("  negative cycle reachable:", nc); assert d2 == d and not nc

    print("\n  -- Negative edge where Dijkstra fails: A->B 2, A->C 3, C->B -2 --")
    V2, E2 = ["A", "B", "C"], [("A", "B", 2), ("A", "C", 3), ("C", "B", -2)]
    dd, _ = dijkstra(V2, E2, "A"); bb, _, nc = bellman_ford(V2, E2, "A")
    print("  Dijkstra    dist[B] =", dd["B"], "(WRONG)")
    print("  Bellman-Ford dist[B] =", bb["B"], "(correct), negative cycle:", nc)
    assert dd["B"] == 2 and bb["B"] == 1
    print("\n  -- Negative cycle: A->B 1, B->C -2, C->B 1 (cycle B->C->B weight -1) --")
    _, _, nc = bellman_ford(["A", "B", "C"], [("A", "B", 1), ("B", "C", -2), ("C", "B", 1)], "A")
    print("  negative cycle detected:", nc); assert nc

    print("\n=== Task 5.3 Floyd-Warshall (all pairs) ===")
    D = floyd(V, E, trace=True)
    for i, u in enumerate(V):
        assert all(D[i][j] == dijkstra(V, E, u)[0][v] for j, v in enumerate(V))
    print("\n  Floyd result equals Dijkstra run from every source.")
    print("\nAll Task 5 tests passed.")
