"""Q7 - Diagnose / Redesign / Validate.  Chosen solution: Q4 brute-force closest pair.
Redesign: 'Order-and-prune' sweep.  Sort once along the more spread-out axis, then for each point only
examine later points whose coordinate gap along that axis is smaller than the best distance found so far."""
import random, time, math, csv
from q4_closest_pair import closest_pair_bf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def closest_pair_prune(pts):
    n = len(pts)
    spread = lambda k: max(p[k] for p in pts) - min(p[k] for p in pts)
    ax = 0 if spread(0) >= spread(1) else 1            # preprocessing 1: choose axis with larger spread
    order = sorted(pts, key=lambda p: p[ax])           # preprocessing 2: sort, O(n log n)
    best = float("inf"); calcs = 0; pairs_seen = 0
    for i in range(n - 1):
        pi = order[i]
        for j in range(i + 1, n):
            gap = order[j][ax] - pi[ax]
            if gap * gap >= best: break                # PRUNE: every later point is at least this far away
            calcs += 1
            dx = pi[0] - order[j][0]; dy = pi[1] - order[j][1]
            d2 = dx * dx + dy * dy
            if d2 < best: best = d2
    return math.sqrt(best), calcs

def gen(name, n, rng):
    if name == "uniform":   return [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(n)]
    if name == "clustered":
        cs = [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(8)]
        return [(c[0] + rng.gauss(0, 150), c[1] + rng.gauss(0, 150)) for c in (rng.choice(cs) for _ in range(n))]
    if name == "vertical line (x equal)": return [(5000.0, rng.uniform(0, 10000)) for _ in range(n)]
    if name == "two columns (adversarial)": return [(rng.choice([0.0, 10000.0]), rng.uniform(0, 10000)) for _ in range(n)]

if __name__ == "__main__":
    print("PREDICTION (made before running): distance calculations drop from n(n-1)/2 to roughly O(n)-O(n^1.5)")
    print("for uniform data (>=90% fewer at n=3200); worst case for the pruning = points that share the sort-axis value.\n")
    rng = random.Random(11); rows = []
    for dist in ["uniform", "clustered", "vertical line (x equal)", "two columns (adversarial)"]:
        print(f"== {dist} ==")
        print(f"{'n':>6}{'orig calcs':>12}{'new calcs':>11}{'reduction':>11}{'orig t(s)':>11}{'new t(s)':>10}{'speedup':>9}")
        for n in [100, 200, 400, 800, 1600, 3200]:
            pts = gen(dist, n, rng)
            t = time.perf_counter(); d1, _, _, c1 = closest_pair_bf(pts); t1 = time.perf_counter() - t
            t = time.perf_counter(); d2, c2 = closest_pair_prune(pts); t2 = time.perf_counter() - t
            assert abs(d1 - d2) < 1e-9, "results differ!"
            rows.append([dist, n, c1, c2, round(t1, 4), round(t2, 4)])
            print(f"{n:6d}{c1:12d}{c2:11d}{100*(1-c2/c1):10.2f}%{t1:11.4f}{t2:10.4f}{t1/max(t2,1e-9):8.1f}x")
        print()
    print("All redesigned results matched brute force (assertion passed).")
    # large-n demo where brute force would be impractical
    big = gen("uniform", 100000, rng)
    t = time.perf_counter(); d, c = closest_pair_prune(big); t = time.perf_counter() - t
    print(f"\nRedesign at n=100000 (brute force would need {100000*99999//2:,} calcs): {c:,} calcs, {t:.2f} s")
    with open("../results/q7_raw.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["distribution", "n", "orig_calcs", "new_calcs", "orig_time_s", "new_time_s"]); w.writerows(rows)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for dist in ["uniform", "clustered", "two columns (adversarial)"]:
        rr = [r for r in rows if r[0] == dist]
        ax[0].loglog([r[1] for r in rr], [r[3] for r in rr], "o-", label=f"redesign: {dist}")
    rr = [r for r in rows if r[0] == "uniform"]
    ax[0].loglog([r[1] for r in rr], [r[2] for r in rr], "k--", label="original (all dists)")
    ax[0].set_xlabel("n"); ax[0].set_ylabel("distance calculations"); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3, which="both"); ax[0].set_title("Distance calculations")
    ax[1].plot([r[1] for r in rr], [r[4] for r in rr], "k--o", label="original"); ax[1].plot([r[1] for r in rr], [r[5] for r in rr], "g-o", label="redesign (uniform)")
    ax[1].set_xlabel("n"); ax[1].set_ylabel("time (s)"); ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_title("Execution time")
    plt.tight_layout(); plt.savefig("../graphs/q7_redesign.png", dpi=130)
