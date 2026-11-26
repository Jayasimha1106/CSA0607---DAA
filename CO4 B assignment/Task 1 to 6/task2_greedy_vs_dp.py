"""
CO4 Assignment 4B - Task 2: Greedy vs Dynamic Programming (Knapsack)

Solution A : Fractional knapsack  - greedy by value/weight ratio (provably optimal for the FRACTIONAL problem).
Solution A': 0/1 "greedy intuition" - same ratio order, but items cannot be split (heuristic, NOT optimal).
Solution B : 0/1 knapsack         - dynamic programming over (item, capacity) with item reconstruction.

Work counters (not timing) are collected so the two strategies can be compared objectively.
"""

import random
from functools import cmp_to_key


# ----------------------------------------------------------------------------- Solution A
def fractional_greedy(items, capacity):
    """items: list of (id, weight, value).  Returns (total_value, picks, counters)."""
    comparisons = 0

    def by_ratio_desc(a, b):
        nonlocal comparisons
        comparisons += 1
        left, right = a[2] * b[1], b[2] * a[1]          # compare v_a/w_a with v_b/w_b without division
        return -1 if left > right else (1 if left < right else 0)

    order = sorted(items, key=cmp_to_key(by_ratio_desc))
    remaining, total, picks, scans = capacity, 0.0, [], 0
    for item_id, weight, value in order:
        scans += 1
        if remaining <= 0:
            break
        fraction = 1.0 if weight <= remaining else remaining / weight
        gained = value * fraction
        picks.append((item_id, fraction, weight * fraction, gained, value / weight))
        total += gained
        remaining -= weight * fraction
    return total, picks, {"comparisons": comparisons, "scans": scans, "memory_cells": len(items)}


# ----------------------------------------------------------------------------- Solution A' (0/1 greedy)
def greedy_01(items, capacity):
    """Ratio-ordered greedy for 0/1 knapsack: take an item whole if it still fits, otherwise skip it."""
    order = sorted(items, key=lambda it: it[2] / it[1], reverse=True)
    remaining, total, picks = capacity, 0, []
    for item_id, weight, value in order:
        if weight <= remaining:
            picks.append(item_id)
            total += value
            remaining -= weight
    return total, picks


# ----------------------------------------------------------------------------- Solution B
def knapsack_dp(items, capacity):
    """0/1 knapsack.  table[i][c] = best value using the first i items with capacity c."""
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    cell_updates = 0
    for i in range(1, n + 1):
        _, weight, value = items[i - 1]
        for c in range(capacity + 1):
            cell_updates += 1
            table[i][c] = table[i - 1][c]                                   # skip item i
            if weight <= c and table[i - 1][c - weight] + value > table[i][c]:
                table[i][c] = table[i - 1][c - weight] + value              # take item i
    chosen, c = [], capacity
    for i in range(n, 0, -1):                                               # trace back
        if table[i][c] != table[i - 1][c]:
            chosen.append(items[i - 1][0])
            c -= items[i - 1][1]
    chosen.reverse()
    return table[n][capacity], chosen, {"cell_updates": cell_updates, "memory_cells": (n + 1) * (capacity + 1)}


def brute_force_01(items, capacity):
    best = 0
    for mask in range(1 << len(items)):
        w = sum(items[k][1] for k in range(len(items)) if mask >> k & 1)
        v = sum(items[k][2] for k in range(len(items)) if mask >> k & 1)
        if w <= capacity:
            best = max(best, v)
    return best


# ----------------------------------------------------------------------------- presentation
def show_items(items, capacity):
    print(f"Capacity = {capacity}")
    print(f"{'Item':<6}{'Weight':>7}{'Value':>7}{'Value/Weight':>14}")
    for item_id, w, v in items:
        print(f"{item_id:<6}{w:>7}{v:>7}{v / w:>14.3f}")


def show_fractional(items, capacity):
    total, picks, ctr = fractional_greedy(items, capacity)
    print("Greedy decision sequence (descending value/weight):")
    for step, (item_id, frac, wt, gain, ratio) in enumerate(picks, 1):
        kind = "whole item" if frac == 1.0 else f"FRACTION {frac:.3f}"
        print(f"  step {step}: item {item_id} ratio={ratio:.3f} -> take {kind}, weight used={wt:.2f}, value gained={gain:.2f}")
    print(f"  Fractional greedy value = {total:.2f}   counters={ctr}")
    return total


def show_dp(items, capacity):
    best, chosen, ctr = knapsack_dp(items, capacity)
    print(f"  0/1 DP optimum = {best}, items = {chosen}, weight = {sum(w for i, w, v in items if i in chosen)}   counters={ctr}")
    return best


def random_instance(rng, n, max_w=20, max_v=50, fill=0.4):
    items = [(f"I{k + 1}", rng.randint(1, max_w), rng.randint(1, max_v)) for k in range(n)]
    return items, max(1, int(sum(w for _, w, _ in items) * fill))


def main():
    print("=" * 100)
    print("TASK 2.1  NORMAL CASES")
    normal_exact = [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]
    print("\nCase N1 - items exactly fill the knapsack")
    show_items(normal_exact, 60)
    f = show_fractional(normal_exact, 60)
    d = show_dp(normal_exact, 60)
    print(f"  fractional = {f:.2f}, 0/1 DP = {d}, 0/1 greedy = {greedy_01(normal_exact, 60)} -> all agree")

    print("\nCase N2 - capacity forces a split of the last item")
    show_items(normal_exact, 50)
    f = show_fractional(normal_exact, 50)
    d = show_dp(normal_exact, 50)
    print(f"  fractional = {f:.2f} (optimal for the FRACTIONAL problem) >= 0/1 DP = {d} (upper bound property)")

    print("\n" + "=" * 100)
    print("TASK 2.2  STUDENT-DESIGNED COUNTEREXAMPLE FOR 0/1 KNAPSACK")
    bad = [("X", 6, 30), ("Y", 5, 24), ("Z", 5, 24)]
    show_items(bad, 10)
    g_val, g_items = greedy_01(bad, 10)
    d_val, d_items, _ = knapsack_dp(bad, 10)
    print(f"  Ratio-greedy 0/1 : items={g_items} value={g_val}")
    print(f"  DP optimum       : items={d_items} value={d_val}")
    print(f"  GreedyResult != DPOptimum  ->  {g_val} != {d_val}  : {g_val != d_val}")
    print("  Greedy trace:")
    remaining = 10
    for item_id, w, v in sorted(bad, key=lambda it: it[2] / it[1], reverse=True):
        verdict = "TAKE" if w <= remaining else "skip (does not fit)"
        print(f"    item {item_id}: ratio {v / w:.2f}, weight {w}, remaining before = {remaining} -> {verdict}")
        if w <= remaining:
            remaining -= w
    print("  First harmful commitment: taking X (highest ratio 5.00). It uses 6 of 10 units, leaving 4,")
    print("  so neither Y nor Z (weight 5) fits.  The optimum {Y,Z} does not contain X at all.")
    print(f"  Fractional optimum for the same data = {fractional_greedy(bad, 10)[0]:.2f} (shows the 'lost' value is the unused 4 units)")

    print("\n" + "=" * 100)
    print("TASK 2.3  ENGINEERING COMPARISON (work counters, not time)")
    rng = random.Random(2024)
    print(f"{'n':>5}{'capacity':>10} | {'greedy compares':>16}{'greedy scans':>13}{'greedy mem':>11} | "
          f"{'DP cell updates':>16}{'DP mem cells':>14} | {'greedy01':>9}{'DP opt':>8}{'quality':>9}")
    for n, cap_scale in [(5, 10), (20, 100), (100, 1000), (300, 10000)]:
        items, _ = random_instance(rng, n)
        capacity = cap_scale
        _, _, gc = fractional_greedy(items, capacity)
        g_val, _ = greedy_01(items, capacity)
        d_val, _, dc = knapsack_dp(items, capacity)
        print(f"{n:>5}{capacity:>10} | {gc['comparisons']:>16}{gc['scans']:>13}{gc['memory_cells']:>11} | "
              f"{dc['cell_updates']:>16}{dc['memory_cells']:>14} | {g_val:>9}{d_val:>8}{g_val / d_val:>9.3f}")
    print("Analytical growth: greedy ~ n log n comparisons, O(n) memory; DP = n*(C+1) cell updates, O(n*C) memory.")
    print("Optimality: fractional greedy is provably optimal for FRACTIONAL knapsack; ratio-greedy has NO guarantee for 0/1;")
    print("            DP is exactly optimal for 0/1 (pseudo-polynomial: cost depends on the VALUE of C, not its bit-length).")
    items10 = [("I%d" % k, rng.randint(1, 20), rng.randint(1, 50)) for k in range(12)]
    assert brute_force_01(items10, 60) == knapsack_dp(items10, 60)[0]
    print("Sanity: DP optimum equals brute-force optimum on a 12-item instance.")

    print("\n" + "=" * 100)
    print("TASK 2.4  CHANGED REQUIREMENT - 'near-optimal is acceptable, answer extremely fast'")
    rng = random.Random(99)
    trials, optimal_hits, ratios, hybrid_ratios = 2000, 0, [], []
    for _ in range(trials):
        items, capacity = random_instance(rng, 10)
        g_val, _ = greedy_01(items, capacity)
        d_val, _, _ = knapsack_dp(items, capacity)
        best_single = max((v for _, w, v in items if w <= capacity), default=0)
        ratios.append(g_val / d_val)
        hybrid_ratios.append(max(g_val, best_single) / d_val)
        optimal_hits += g_val == d_val
    print(f"Over {trials} random 10-item instances (capacity = 40% of total weight):")
    print(f"  ratio-greedy hit the exact optimum in {optimal_hits / trials:.1%} of cases")
    print(f"  average quality = {sum(ratios) / trials:.4f}, worst quality = {min(ratios):.4f}")
    print(f"  greedy + 'best single item' guard: average = {sum(hybrid_ratios) / trials:.4f}, worst = {min(hybrid_ratios):.4f}")
    worst_known = greedy_01(bad, 10)[0] / knapsack_dp(bad, 10)[0]
    print(f"  my adversarial instance: quality = {worst_known:.3f}; making X heavier/valuable-per-weight can push this towards 0")
    adv = [("X", 2, 3), ("Y", 100, 99)]
    print(f"  extreme example items={adv}, C=100: greedy={greedy_01(adv, 100)[0]}, DP={knapsack_dp(adv, 100)[0]}"
          f" (quality {greedy_01(adv, 100)[0] / knapsack_dp(adv, 100)[0]:.3f}) -> no worst-case guarantee")
    print(f"  with the best-single-item guard greedy returns {max(greedy_01(adv, 100)[0], 99)} = optimal here (0.5-approximation guaranteed)")


if __name__ == "__main__":
    main()
