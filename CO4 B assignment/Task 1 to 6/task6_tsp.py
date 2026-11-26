r"""
CO4 Assignment 4B - Task 6: Last-mile delivery route optimisation (TSP by Dynamic Programming, Held-Karp)

Model
-----
Location 0 is the distribution hub.  Delivery locations are 1..n.  cost[i][j] = travel cost i -> j.
A subset S of delivery locations is stored as a bit mask (bit k-1 set  <=>  location k is in S).

    DP[S][j] (j in S) = minimum cost of a path that STARTS at the hub, visits EXACTLY the locations in S
                         (each once) and ENDS at location j.
    Base      : DP[{j}][j] = cost[0][j]
    Recurrence: DP[S][j] = min over i in S\{j} of  DP[S\{j}][i] + cost[i][j]
    Answer    : min over j of  DP[ALL][j] + cost[j][0]        (return to the hub)
    parent[S][j] = the i that achieved the minimum  -> route reconstruction.
States: n * 2^(n-1) (valid (S, j) pairs).  Time O(n^2 2^n).  Space O(n 2^n).
"""

import itertools
import math
import random
import time
import tracemalloc

INF = float("inf")


def held_karp(cost):
    """cost is an (n+1)x(n+1) matrix, index 0 = hub.  Returns (best_cost, route, stats)."""
    size = len(cost)
    if size == 0 or any(len(row) != size for row in cost):
        raise ValueError("cost matrix must be square and non-empty")
    n = size - 1
    if n == 0:
        return 0, [0, 0], {"states": 0, "transitions": 0, "table_entries": 0}
    full = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]               # dp[mask][j-1]
    parent = [[-1] * n for _ in range(1 << n)]
    states = transitions = 0

    for j in range(1, n + 1):                              # base states: hub -> j
        dp[1 << (j - 1)][j - 1] = cost[0][j]
        states += 1
        transitions += 1

    for mask in range(1, full + 1):
        if mask & (mask - 1) == 0:                         # singletons are base states
            continue
        for j in range(1, n + 1):
            bit = 1 << (j - 1)
            if not mask & bit:
                continue
            previous = mask ^ bit
            best, best_i = INF, -1
            for i in range(1, n + 1):
                if previous >> (i - 1) & 1:
                    transitions += 1
                    candidate = dp[previous][i - 1] + cost[i][j]
                    if candidate < best:
                        best, best_i = candidate, i
            dp[mask][j - 1], parent[mask][j - 1] = best, best_i
            states += 1

    best_total, last = INF, -1
    for j in range(1, n + 1):                              # close the tour back to the hub
        total = dp[full][j - 1] + cost[j][0]
        if total < best_total:
            best_total, last = total, j
    route, mask, j = [], full, last
    while j != -1:
        route.append(j)
        i = parent[mask][j - 1]
        mask ^= 1 << (j - 1)
        j = i
    route = [0] + route[::-1] + [0]
    return best_total, route, {"states": states, "transitions": transitions, "table_entries": (1 << n) * n}


def brute_force_tsp(cost):
    """Independent reference: enumerate every permutation of the delivery locations."""
    n = len(cost) - 1
    best, best_route, count = INF, None, 0
    for perm in itertools.permutations(range(1, n + 1)):
        count += 1
        path = (0,) + perm + (0,)
        total = sum(cost[a][b] for a, b in zip(path, path[1:]))
        if total < best:
            best, best_route = total, path
    return best, list(best_route), count


def route_cost(cost, route):
    return sum(cost[a][b] for a, b in zip(route, route[1:]))


def matrix_from_points(points):
    return [[round(math.dist(p, q)) for q in points] for p in points]


def show_matrix(labels, cost):
    print("      " + "".join(f"{x:>5}" for x in labels))
    for lab, row in zip(labels, cost):
        print(f"{lab:>5} " + "".join(f"{x:>5}" for x in row))


def main():
    names = ["Hub", "A", "B", "C", "D", "E", "F"]
    points = [(0, 0), (4, 7), (9, 2), (12, 8), (6, 12), (14, 3), (2, 3)]
    cost = matrix_from_points(points)

    print("=" * 100)
    print("TASK 6.3  ROUTE OPTIMISATION ENGINE  (hub + 6 delivery locations)")
    print("Coordinates:", dict(zip(names, points)))
    print("Cost matrix (rounded Euclidean distance):")
    show_matrix(names, cost)
    best, route, stats = held_karp(cost)
    print("\nOptimal route :", " -> ".join(names[k] for k in route))
    print("Visit order   :", ", ".join(names[k] for k in route[1:-1]), "(then return to Hub)")
    legs = [f"{names[a]}->{names[b]}={cost[a][b]}" for a, b in zip(route, route[1:])]
    print("Leg costs     :", ", ".join(legs))
    print(f"Minimum Travel Cost = {best}   (re-computed from route = {route_cost(cost, route)})")
    print("DP statistics :", stats)

    print("\n" + "=" * 100)
    print("TASK 6.4  VALIDATION - hub + 4 delivery locations")
    small = [row[:5] for row in cost[:5]]
    show_matrix(names[:5], small)
    ref_cost, ref_route, perms = brute_force_tsp(small)
    dp_cost, dp_route, _ = held_karp(small)
    print(f"Exhaustive enumeration: {perms} permutations, best = {ref_cost}, route = {' -> '.join(names[k] for k in ref_route)}")
    print(f"Dynamic programming   : best = {dp_cost}, route = {' -> '.join(names[k] for k in dp_route)}")
    all_costs = sorted(route_cost(small, (0,) + p + (0,)) for p in itertools.permutations(range(1, 5)))
    print("All 24 tour costs sorted:", all_costs)
    print("Costs match:", ref_cost == dp_cost)
    rng, mismatches = random.Random(3), 0
    for _ in range(300):
        k = rng.randint(1, 8)
        m = [[0 if a == b else rng.randint(1, 50) for b in range(k + 1)] for a in range(k + 1)]   # asymmetric
        mismatches += held_karp(m)[0] != brute_force_tsp(m)[0]
    print(f"Randomised regression (300 asymmetric matrices, 1..8 locations): mismatches = {mismatches}")
    print("Boundary tests: 1 location ->", held_karp([[0, 7], [9, 0]])[:2], "| 0 locations ->", held_karp([[0]])[:2])
    try:
        held_karp([[0, 1], [1]])
    except ValueError as err:
        print("Malformed matrix rejected:", err)

    print("\n" + "=" * 100)
    print("TASK 6.5  STATE-SPACE GROWTH")
    print(f"{'n':>3}{'2^n subsets':>13}{'DP states':>12}{'n*2^(n-1)':>12}{'transitions':>13}{'table entries':>15}"
          f"{'time (s)':>10}{'peak mem (MB)':>15}{'states ratio':>14}")
    rng = random.Random(1)
    previous_states = None
    for n in range(4, 18):
        pts = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n + 1)]
        m = matrix_from_points(pts)
        t0 = time.perf_counter()
        _, _, st = held_karp(m)
        elapsed = time.perf_counter() - t0
        tracemalloc.start()
        held_karp(m)
        peak = tracemalloc.get_traced_memory()[1] / 1e6
        tracemalloc.stop()
        ratio = "" if previous_states is None else f"x{st['states'] / previous_states:.2f}"
        print(f"{n:>3}{2 ** n:>13}{st['states']:>12}{n * 2 ** (n - 1):>12}{st['transitions']:>13}{st['table_entries']:>15}"
              f"{elapsed:>10.3f}{peak:>15.1f}{ratio:>14}")
        previous_states = st["states"]
    print("\nExtrapolation (not executed): states = n*2^(n-1), table entries = n*2^n")
    for n in (20, 25, 30, 200):
        digits = n * math.log10(2)
        print(f"  n={n:>3}: 2^n ~ 10^{digits:.1f}; table entries ~ {n} x 10^{digits:.1f}"
              + (f" ~ {n * 2 ** n * 8 / 1e9:,.1f} GB at 8 bytes/entry" if n <= 30 else ""))


if __name__ == "__main__":
    main()
