"""Q5 - Brute-force convex hull derived from the 'all points on one side of a line' principle."""
import random, math, time, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def side(p, q, r):
    """Sign of the cross product (q-p) x (r-p): >0 left of p->q, <0 right, 0 collinear.
       Equivalent to the sign of a*x + b*y - c for the line through p,q."""
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

def between(p, q, r):          # collinear r lies on segment pq
    return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])

def convex_hull_bf(points):
    pts = list(dict.fromkeys(points))             # remove duplicate points
    n = len(pts); tests = 0; edges = []
    if n < 3: return pts, edges, tests
    for i in range(n):
        for j in range(i + 1, n):
            p, q = pts[i], pts[j]; pos = neg = False; ok = True
            for k in range(n):
                if k == i or k == j: continue
                tests += 1
                s = side(p, q, pts[k])
                if s > 0: pos = True
                elif s < 0: neg = True
                elif not between(p, q, pts[k]):   # collinear but outside segment -> pq is not an extreme edge
                    ok = False; break
                if pos and neg: ok = False; break  # points on both sides -> reject early
            if ok: edges.append((p, q))
    verts = set()
    for p, q in edges: verts.update((p, q))
    verts = list(verts)
    if len(verts) > 2:
        cx = sum(v[0] for v in verts) / len(verts); cy = sum(v[1] for v in verts) / len(verts)
        verts.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))     # CCW boundary order
    return verts, edges, tests

def plot(ax, pts, hull, title):
    ax.scatter(*zip(*pts), s=18, c="tab:blue"); 
    if len(hull) > 1:
        h = hull + [hull[0]]; ax.plot(*zip(*h), "r-", lw=1.5); ax.scatter(*zip(*hull), s=40, c="r", zorder=3)
    ax.set_title(title, fontsize=9); ax.set_aspect("equal"); ax.grid(alpha=.3)

if __name__ == "__main__":
    random.seed(5)
    tests = {}
    tests["A: 25 random pts (boundary + interior)"] = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(25)]
    sq = [(0, 0), (10, 0), (10, 10), (0, 10)]
    tests["B1 (challenge): square + collinear edge pts + duplicates + interior"] = sq + [(5, 0), (10, 5), (5, 10), (0, 5), (5, 5), (3, 3), (7, 2), (0, 0), (10, 10)]
    tests["B2 (challenge): all points collinear"] = [(i, 2 * i) for i in range(8)]
    tests["B3 (challenge): points on a circle + centre"] = [(round(50 + 40 * math.cos(2 * math.pi * k / 12)), round(50 + 40 * math.sin(2 * math.pi * k / 12))) for k in range(12)] + [(50, 50)]
    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, (name, pts) in zip(axs.flat, tests.items()):
        hull, edges, c = convex_hull_bf(pts)
        print(f"{name}\n   n = {len(set(pts))} distinct points, hull vertices = {len(hull)}, hull edges accepted = {len(edges)}, side-tests = {c}")
        print(f"   hull (CCW): {hull}\n")
        plot(ax, pts, hull, name)
    plt.tight_layout(); plt.savefig("../graphs/q5_hull_tests.png", dpi=120)

    # growth analysis
    print("Computational work vs n (random points):")
    print(f"{'n':>5}{'side tests':>14}{'worst n^2(n-2)/2':>18}{'time (s)':>10}{'hull size':>10}")
    rows = []
    for n in [10, 20, 40, 80, 160, 320]:
        pts = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]
        t = time.perf_counter(); h, e, c = convex_hull_bf(pts); t = time.perf_counter() - t
        w = n * (n - 1) // 2 * (n - 2)
        rows.append([n, c, w, round(t, 4), len(h)]); print(f"{n:5d}{c:14d}{w:18d}{t:10.4f}{len(h):10d}")
    for a, b in zip(rows, rows[1:]): print(f"  n x2: tests x{b[1]/a[1]:.2f}, time x{b[3]/max(a[3],1e-9):.2f}")
    with open("../results/q5_raw.csv", "w", newline="") as f:
        w_ = csv.writer(f); w_.writerow(["n", "side_tests", "worst_case", "time_s", "hull_size"]); w_.writerows(rows)
    plt.figure(figsize=(6, 4.5)); ns = [r[0] for r in rows]
    plt.loglog(ns, [r[1] for r in rows], "o-", label="measured (early exit)"); plt.loglog(ns, [r[2] for r in rows], "x--", label="worst case n(n-1)(n-2)/2")
    plt.xlabel("n"); plt.ylabel("side tests"); plt.legend(); plt.grid(alpha=.3, which="both"); plt.title("Q5: work growth"); plt.tight_layout(); plt.savefig("../graphs/q5_growth.png", dpi=130)
