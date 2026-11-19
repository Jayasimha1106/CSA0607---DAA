"""Q6 - Exhaustive search for the humanitarian airlift (0/1 knapsack)."""
import random, time, itertools, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def exhaustive_airlift(pkgs, limit):
    """Binary-mask enumeration: mask bit i == 1  <=>  package i is loaded. 2^n candidates."""
    n = len(pkgs); best_v = -1; best_mask = 0; cands = feas = 0
    for mask in range(1 << n):
        cands += 1
        w = v = 0
        for i in range(n):
            if mask >> i & 1:
                w += pkgs[i][1]; v += pkgs[i][2]
        if w <= limit:                      # feasibility check
            feas += 1
            if v > best_v: best_v, best_mask = v, mask      # keep best
    chosen = [pkgs[i][0] for i in range(n) if best_mask >> i & 1]
    return best_v, chosen, cands, feas

def exhaustive_recursive(pkgs, limit):
    """Include/exclude decision tree with running totals (same 2^n leaves, no inner loop)."""
    n = len(pkgs); best = [-1, 0]; cnt = [0, 0]
    def go(i, w, v, mask):
        if i == n:
            cnt[0] += 1
            if w <= limit:
                cnt[1] += 1
                if v > best[0]: best[0], best[1] = v, mask
            return
        go(i + 1, w, v, mask)
        go(i + 1, w + pkgs[i][1], v + pkgs[i][2], mask | (1 << i))
    go(0, 0, 0, 0)
    return best[0], [pkgs[i][0] for i in range(n) if best[1] >> i & 1], cnt[0], cnt[1]

def independent_check(pkgs, limit):             # verification with itertools (different code path)
    best = (-1, None)
    for r in range(len(pkgs) + 1):
        for comb in itertools.combinations(pkgs, r):
            if sum(c[1] for c in comb) <= limit:
                val = sum(c[2] for c in comb)
                if val > best[0]: best = (val, [c[0] for c in comb])
    return best

if __name__ == "__main__":
    small = [("P1", 5, 10), ("P2", 4, 40), ("P3", 6, 30), ("P4", 3, 50)]
    limit = 10
    print("CORRECTNESS CHECK  (payload limit = 10)")
    print("Mask  Items          Weight Value Feasible")
    for mask in range(16):
        it = [small[i] for i in range(4) if mask >> i & 1]
        w = sum(x[1] for x in it); v = sum(x[2] for x in it)
        print(f"{mask:04b}  {','.join(x[0] for x in it) or '-':14s}{w:6d}{v:6d}   {'YES' if w <= limit else 'no'}")
    print("Exhaustive (mask):      ", exhaustive_airlift(small, limit))
    print("Exhaustive (recursive): ", exhaustive_recursive(small, limit))
    print("Independent itertools:  ", independent_check(small, limit))
    print("Hand-verified optimum: {P2,P4} weight 7 value 90 ; {P2,P3} w10 v70 ; {P3,P4} w9 v80\n")

    random.seed(9)
    print("GROWTH INVESTIGATION (recursive enumeration, limit = 50% of total weight)")
    print(f"{'n':>4}{'2^n predicted':>15}{'candidates':>13}{'feasible':>11}{'time (s)':>10}{'time ratio':>11}")
    rows = []; prev = None
    for n in [10, 12, 14, 16, 18, 20, 22]:
        pk = [(f"P{i}", random.randint(1, 30), random.randint(1, 100)) for i in range(n)]
        lim = sum(p[1] for p in pk) // 2
        t = time.perf_counter(); v, ch, c, f = exhaustive_recursive(pk, lim); t = time.perf_counter() - t
        ratio = t / prev if prev else float("nan"); prev = t
        rows.append([n, 2 ** n, c, f, round(t, 4)])
        print(f"{n:4d}{2**n:15d}{c:13d}{f:11d}{t:10.4f}{ratio:11.2f}")
    k = rows[-1][4] / rows[-1][2]
    print(f"\nFitted cost per candidate = {k*1e6:.2f} microseconds")
    for lim_t in (1, 10, 60):
        import math
        print(f"  fixed response time {lim_t:3d} s  ->  largest n ~ {int(math.log2(lim_t / k))}")
    with open("../results/q6_raw.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "predicted_2^n", "candidates", "feasible", "time_s"]); w.writerows(rows)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5)); ns = [r[0] for r in rows]
    ax[0].semilogy(ns, [r[2] for r in rows], "o-", label="measured candidates"); ax[0].semilogy(ns, [2 ** n for n in ns], "x--", label="2^n"); ax[0].legend(); ax[0].set_title("Candidate combinations"); ax[0].grid(alpha=.3)
    ax[1].semilogy(ns, [r[4] for r in rows], "o-"); ax[1].axhline(1.0, color="r", ls="--", label="1 s response limit"); ax[1].legend(); ax[1].set_title("Execution time (s, log)"); ax[1].grid(alpha=.3)
    for a in ax: a.set_xlabel("n packages")
    plt.tight_layout(); plt.savefig("../graphs/q6_exhaustive.png", dpi=130)
