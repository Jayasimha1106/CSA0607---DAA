"""Q5 - Closest pair of points: brute force vs Divide & Conquer. Counts distance computations."""
import random, math, time

def dist(p, q, cnt):
    cnt[0] += 1
    return math.hypot(p[0] - q[0], p[1] - q[1])

def brute(P, cnt):
    best = (float('inf'), None)
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            d = dist(P[i], P[j], cnt)
            if d < best[0]: best = (d, (P[i], P[j]))
    return best

def closest_dc(P, cnt):
    Px = sorted(P)                                    # sorted by x once
    Py = sorted(P, key=lambda p: p[1])                # sorted by y once
    return _rec(Px, Py, cnt)

def _rec(Px, Py, cnt):
    n = len(Px)
    if n <= 3: return brute(Px, cnt)                  # base case
    mid = n // 2; midx = Px[mid][0]
    Lx, Rx = Px[:mid], Px[mid:]
    Lset = set(Lx)
    Ly = [p for p in Py if p in Lset]; Ry = [p for p in Py if p not in Lset]
    dl = _rec(Lx, Ly, cnt); dr = _rec(Rx, Ry, cnt)    # each call returns (min distance, pair)
    best = min(dl, dr, key=lambda t: t[0]); d = best[0]
    strip = [p for p in Py if abs(p[0] - midx) < d]   # only points within d of the dividing line, y-sorted
    for i in range(len(strip)):
        for j in range(i + 1, min(i + 8, len(strip))):  # at most 7 neighbours need checking
            if strip[j][1] - strip[i][1] >= d: break
            dd = dist(strip[i], strip[j], cnt)
            if dd < best[0]: best = (dd, (strip[i], strip[j])); d = dd
    return best

def points(n, kind="random"):
    if kind == "random":  return list({(random.randint(0, 10**6), random.randint(0, 10**6)) for _ in range(n)})
    if kind == "line":    return [(i * 3, 0) for i in range(n)]                       # collinear
    if kind == "cluster": return list({(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)})

if __name__ == "__main__":
    random.seed(11)
    print("=== Q5: Correctness ===")
    for _ in range(200):
        P = points(random.randint(2, 60)); a = brute(P, [0]); b = closest_dc(P, [0])
        assert abs(a[0] - b[0]) < 1e-9
    print("200 random trials: D&C distance == brute-force distance\n")
    print("=== Q5: Distance computations and time (random uniform points) ===")
    print(f"{'n':>7} {'brute dist':>12} {'n(n-1)/2':>12} {'D&C dist':>10} {'n log2 n':>10} {'brute ms':>10} {'D&C ms':>8}")
    for n in [10, 50, 100, 200, 500, 1000, 2000, 4000]:
        P = points(n); n = len(P); cb, cd = [0], [0]
        t = time.perf_counter(); brute(P, cb); tb = (time.perf_counter() - t) * 1000
        t = time.perf_counter(); closest_dc(P, cd); td = (time.perf_counter() - t) * 1000
        print(f"{n:>7} {cb[0]:>12} {n*(n-1)//2:>12} {cd[0]:>10} {n*math.log2(n):>10.0f} {tb:>10.2f} {td:>8.2f}")
    print("\n=== Q5: Other data distributions, n=1000 ===")
    for kind in ["random", "line", "cluster"]:
        P = points(1000, kind); cb, cd = [0], [0]; brute(P, cb); closest_dc(P, cd)
        print(f"  {kind:>8}: n={len(P):>5} brute={cb[0]:>7} D&C={cd[0]:>6}")
    print("\nTime crossover (small n): ")
    for n in [8, 16, 24, 32, 48, 64, 100]:
        P = points(n); reps = 200
        t = time.perf_counter(); [brute(P, [0]) for _ in range(reps)]; tb = (time.perf_counter() - t) / reps * 1e6
        t = time.perf_counter(); [closest_dc(P, [0]) for _ in range(reps)]; td = (time.perf_counter() - t) / reps * 1e6
        print(f"  n={n:>4}: brute {tb:>8.1f} us   D&C {td:>8.1f} us   -> {'D&C' if td < tb else 'brute'} faster")
