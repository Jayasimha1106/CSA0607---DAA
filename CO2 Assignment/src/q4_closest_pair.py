"""Q4 - Brute-force closest pair of drones."""
import random, time, math, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def closest_pair_bf(pts):
    n = len(pts); best = float("inf"); pair = None; pairs = dist_calcs = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):            # j>i : each unordered pair once
            pairs += 1; dist_calcs += 1
            dx = xi - pts[j][0]; dy = yi - pts[j][1]
            d2 = dx * dx + dy * dy           # squared distance: sqrt not needed for comparison
            if d2 < best: best, pair = d2, (i, j)
    return math.sqrt(best), pair, pairs, dist_calcs

if __name__ == "__main__":
    random.seed(11)
    sizes = [100, 200, 400, 800, 1600, 3200]
    rows = []
    print(f"{'n':>6}{'pairs examined':>16}{'n(n-1)/2':>12}{'dist calcs':>12}{'time (s)':>10}{'min dist':>10}")
    for n in sizes:
        pts = [(random.uniform(0, 10000), random.uniform(0, 10000)) for _ in range(n)]
        t = time.perf_counter(); d, p, pr, dc = closest_pair_bf(pts); t = time.perf_counter() - t
        assert pr == n * (n - 1) // 2
        rows.append([n, pr, dc, round(t, 4)])
        print(f"{n:6d}{pr:16d}{n*(n-1)//2:12d}{dc:12d}{t:10.4f}{d:10.3f}")
    # growth check: time ratio when n doubles should be ~4
    print("\nGrowth check (n doubles -> pairs x4):")
    for a, b in zip(rows, rows[1:]):
        print(f"  n {a[0]:5d} -> {b[0]:5d}: pairs x{b[1]/a[1]:.2f}, time x{b[3]/a[3]:.2f}")
    # fit t = k * pairs, then extrapolate
    k = sum(r[3] for r in rows[-3:]) / sum(r[1] for r in rows[-3:])
    print(f"\nFitted cost per pair = {k*1e9:.1f} ns (pure Python)")
    for limit in (0.1, 1.0, 10.0):
        pairs_allowed = limit / k; n_max = (1 + math.sqrt(1 + 8 * pairs_allowed)) / 2
        print(f"  acceptable response time {limit:5.1f} s  ->  n_max ~ {n_max:,.0f} drones")
    with open("../results/q4_raw.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "pairs", "dist_calcs", "time_s"]); w.writerows(rows)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ns = [r[0] for r in rows]
    ax[0].plot(ns, [r[1] for r in rows], "o-", label="measured pairs"); ax[0].plot(ns, [n*(n-1)//2 for n in ns], "x--", label="n(n-1)/2"); ax[0].set_title("Pairs examined"); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].plot(ns, [r[3] for r in rows], "o-"); ax[1].axhline(1.0, color="r", ls="--", label="1 s acceptable limit"); ax[1].set_title("Execution time (s)"); ax[1].legend(); ax[1].grid(alpha=.3)
    for a in ax: a.set_xlabel("n drones")
    plt.tight_layout(); plt.savefig("../graphs/q4_closest_pair.png", dpi=130)
