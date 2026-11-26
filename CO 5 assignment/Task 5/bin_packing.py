"""Task B4 - Bin packing: First Fit Decreasing (FFD) heuristic + small exact solver.

Placement rule (FFD): sort workloads by demand, largest first; place each into the
FIRST (lowest-numbered) open server whose remaining capacity >= demand; else open a new server.
"""
import random, time
from math import ceil


def first_fit_decreasing(demands, C):
    order = sorted(range(len(demands)), key=lambda i: -demands[i])
    bins, remaining, checks = [], [], 0          # bins hold workload indices
    for i in order:
        d = demands[i]
        assert 0 < d <= C, "demand must be in (0, C]"
        placed = False
        for b in range(len(bins)):
            checks += 1
            if remaining[b] >= d:
                bins[b].append(i); remaining[b] -= d; placed = True; break
        if not placed:
            bins.append([i]); remaining.append(C - d)
    return bins, remaining, checks


def exact_bins(demands, C):
    """Backtracking exact solver (small n): returns the minimum number of bins."""
    items = sorted(demands, reverse=True)
    best = [len(items)]
    loads = []
    def rec(k):
        if len(loads) >= best[0]:
            return
        if k == len(items):
            best[0] = len(loads); return
        seen = set()
        for b in range(len(loads)):
            if loads[b] + items[k] <= C and loads[b] not in seen:
                seen.add(loads[b]); loads[b] += items[k]; rec(k + 1); loads[b] -= items[k]
        loads.append(items[k]); rec(k + 1); loads.pop()
    rec(0)
    return best[0]


def show(demands, C, label):
    bins, rem, checks = first_fit_decreasing(demands, C)
    print(f"--- {label}: {len(demands)} workloads, capacity C={C} ---")
    print(f"Servers used: {len(bins)}   (lower bound ceil(sum/C) = {ceil(sum(demands)/C)}, fit-checks = {checks})")
    for s, (b, r) in enumerate(zip(bins, rem), 1):
        print(f"  Server {s}: workloads {[ (i+1, demands[i]) for i in b]}  load={C-r}  remaining={r}")
    return len(bins)


if __name__ == "__main__":
    C = 100
    rnd = random.Random(42)
    demo = [rnd.randint(10, 70) for _ in range(12)]
    print("B4.1 demo input (workload demands):", demo)
    show(demo, C, "B4.1 demo")

    print("\nB4.2 Challenge input (C=10): demands [4,4,3,3,3,3]")
    ch = [4, 4, 3, 3, 3, 3]
    n = show(ch, 10, "B4.2 challenge")
    print("Exact optimum:", exact_bins(ch, 10), "servers  (4+3+3 | 4+3+3)")

    print("\nB4.2 random small instances: FFD vs exact (C=100, 10 items in 20..60, 200 trials)")
    worse = 0; r2 = random.Random(1)
    for _ in range(200):
        d = [r2.randint(20, 60) for _ in range(10)]
        if len(first_fit_decreasing(d, 100)[0]) > exact_bins(d, 100): worse += 1
    print(f"FFD strictly worse than optimum in {worse}/200 trials")

    print("\nB4.3 Scale test (C=100, demands uniform 1..100)")
    print(f"{'Workloads':>10}{'Servers':>9}{'LowerBound':>12}{'Ratio':>8}{'FitChecks':>12}{'Seconds':>9}")
    for N in (1000, 2000, 5000, 10000, 20000):
        d = [rnd.randint(1, 100) for _ in range(N)]
        t = time.perf_counter(); bins, rem, chk = first_fit_decreasing(d, 100); dt = time.perf_counter() - t
        lb = ceil(sum(d) / 100)
        print(f"{N:>10}{len(bins):>9}{lb:>12}{len(bins)/lb:>8.3f}{chk:>12}{dt:>9.3f}")
