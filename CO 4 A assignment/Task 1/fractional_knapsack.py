"""Task 1 - LoadVehicle: Fractional Knapsack (greedy by value/weight ratio)."""
from fractions import Fraction as F


def load_vehicle(packages, capacity):
    """packages: list of (id, weight, value). Returns (total_value, plan, remaining, trace)."""
    items = [(pid, F(w), F(v), F(v, w)) for pid, w, v in packages if w > 0]
    items.sort(key=lambda t: (-t[3], t[0]))          # ratio descending, ID breaks ties
    remaining, total, plan, trace = F(capacity), F(0), [], []
    for pid, w, v, r in items:
        if remaining <= 0:
            break
        frac = F(1) if w <= remaining else remaining / w
        taken_w, gained = w * frac, v * frac
        remaining -= taken_w
        total += gained
        plan.append((pid, frac, taken_w, gained))
        trace.append((pid, w, v, r, frac, remaining, total))
    return total, plan, remaining, trace


def show(title, packages, capacity):
    total, plan, rem, trace = load_vehicle(packages, capacity)
    print(f"\n=== {title} | capacity = {capacity} ===")
    print(f"{'Pkg':<4}{'W':>4}{'V':>5}{'V/W':>7}{'fraction':>10}{'remaining':>11}{'total':>8}")
    for pid, w, v, r, fr, rem_, tot in trace:
        print(f"{pid:<4}{str(w):>4}{str(v):>5}{float(r):>7.2f}{str(fr):>10}{str(rem_):>11}{float(tot):>8.2f}")
    print("Plan  :", [(p, str(f)) for p, f, _, _ in plan])
    print(f"Total value = {float(total):.2f}, unused capacity = {float(rem):.2f}")
    return total


def alt_greedy(packages, capacity, key):
    """Alternative greedy orderings (by value or by weight) to show the ratio rule is better."""
    rem, tot = F(capacity), F(0)
    for _, w, v in sorted(packages, key=key):
        if rem <= 0:
            break
        fr = min(F(1), rem / w)
        rem -= w * fr
        tot += v * fr
    return tot


if __name__ == "__main__":
    base = [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]
    t = show("Test 1: partial last package", base, 50)
    assert t == 240
    print("Compare: highest-value-first =", float(alt_greedy(base, 50, lambda x: -x[2])),
          "| lightest-first =", float(alt_greedy(base, 50, lambda x: x[1])))
    t = show("Test 2: exact fit", base, 30); assert t == 160
    t = show("Test 3: capacity 0", base, 0); assert t == 0
    t = show("Test 4: capacity exceeds total weight", base, 100); assert t == 280
    t = show("Test 5: equal ratios (tie)", [("X", 4, 8), ("Y", 2, 4), ("Z", 6, 12)], 7); assert t == 14
    print("\nAll Task 1 tests passed.")
