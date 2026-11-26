"""Task B1 - Instrumented backtracking graph colouring (CO5).

Two vertex-selection strategies:
  "input"  : Version 1 - vertices in the order 0,1,...,n-1
  "dsatur" : Version 2 - dynamic 'most-constrained-first' (saturation degree,
             ties broken by uncoloured-neighbour degree, then lowest index)
"""


def build_adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def colour_graph(n, edges, m, strategy="input", trace=False, names=None):
    adj = build_adj(n, edges)
    colour = [0] * n                       # 0 = uncoloured, 1..m = colours
    stats = dict(nodes=0, candidates=0, rejected=0, backtracks=0, max_depth=0)
    log = []
    nm = (lambda v: names[v]) if names else (lambda v: str(v))

    def select_vertex():
        uncol = [v for v in range(n) if colour[v] == 0]
        if strategy == "input":
            return uncol[0]
        def key(v):
            sat = len({colour[u] for u in adj[v] if colour[u]})
            deg = sum(1 for u in adj[v] if colour[u] == 0)
            return (-sat, -deg, v)
        return min(uncol, key=key)

    def feasible(v, c):
        return all(colour[u] != c for u in adj[v])

    def solve(depth):
        stats["nodes"] += 1                                # node visited
        stats["max_depth"] = max(stats["max_depth"], depth)
        if depth == n:                                     # goal: all coloured
            return True
        v = select_vertex()                                # choose
        for c in range(1, m + 1):                          # candidates
            stats["candidates"] += 1
            if not feasible(v, c):                         # check
                stats["rejected"] += 1
                if trace:
                    log.append("  " * depth + f"try {nm(v)}={c}: REJECT (a neighbour already has {c})")
                continue
            colour[v] = c                                  # assign
            if trace:
                log.append("  " * depth + f"try {nm(v)}={c}: ACCEPT -> explore")
            if solve(depth + 1):                           # explore
                return True
            colour[v] = 0                                  # undo
            stats["backtracks"] += 1
            if trace:
                log.append("  " * depth + f"BACKTRACK: undo {nm(v)}={c}")
        if trace:
            log.append("  " * depth + f"dead end at {nm(v)} (no colour left) -> return FAILURE")
        return False

    ok = solve(0)
    res = dict(stats)
    res["colourable"] = ok
    res["colouring"] = colour[:] if ok else None
    res["trace"] = log
    return res


def valid_colouring(n, edges, m, colouring):
    return (colouring is not None and len(colouring) == n and
            all(1 <= c <= m for c in colouring) and
            all(colouring[u] != colouring[v] for u, v in edges))
