"""Measurements for Part (d).  Run:  python experiments/run_experiments.py

Writes CSV files and PNG graphs into ../results.  All random data uses fixed seeds.
"""
import csv
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "Supporting_Files")
import corrected as C    # noqa: E402
import optimised as O    # noqa: E402
import original as ORIG  # noqa: E402


def write_csv(name, header, rows):
    with open(os.path.join(RES, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- closest pair
_real_sqrt = math.sqrt
_calls = [0]


def counting_sqrt(x):
    _calls[0] += 1
    return _real_sqrt(x)


def count_sqrt_calls(fn, events):
    """Distance computations of an UNMODIFIED brute-force function = number of sqrt calls."""
    _calls[0] = 0
    math.sqrt = counting_sqrt
    try:
        fn(events)
    finally:
        math.sqrt = _real_sqrt
    return _calls[0]


def timed(fn, *a):
    t = time.perf_counter()
    r = fn(*a)
    return r, time.perf_counter() - t


print("== closest_logins: distance computations ==")
rows = []
SIZES = [1000, 2000, 4000, 8000]
for dataset in ("uniform", "clustered", "same_x"):
    for n in SIZES:
        rng = random.Random(100 + n)
        if dataset == "uniform":
            ev = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(n)]
        elif dataset == "clustered":   # 20 city clusters, ~15 km spread
            centres = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(20)]
            ev = []
            for _ in range(n):
                cx, cy = rng.choice(centres)
                ev.append((rng.gauss(cx, 15), rng.gauss(cy, 15)))
        else:                          # worst case for x-pruning: every login on one meridian
            ev = [(500.0, rng.uniform(0, 1000)) for _ in range(n)]
        orig_n = count_sqrt_calls(ORIG.closest_logins, ev) if n <= 2000 else n * n   # n*n verified at n<=2000
        brute_n = count_sqrt_calls(C.closest_logins, ev)
        st = {}
        res_o = O.closest_logins(ev, st)
        res_b = C.closest_logins(ev)
        assert res_o == res_b, (dataset, n, res_o, res_b)
        _, t_b = timed(C.closest_logins, ev)
        _, t_o = timed(O.closest_logins, ev)
        rows.append([dataset, n, orig_n, brute_n, st["distance_computations"],
                     round(brute_n / st["distance_computations"], 1), round(t_b, 3), round(t_o, 4)])
        print(rows[-1], flush=True)
write_csv("closest_pair_measurements.csv",
          ["dataset", "n", "original_dist_comps(n^2)", "corrected_brute_dist_comps", "optimised_dist_comps",
           "reduction_factor", "brute_seconds", "optimised_seconds"], rows)

# --------------------------------------------------------------- insertion sort


class CInt(int):
    """int whose '<' comparisons are counted (lets us count comparisons in unmodified code)."""
    count = 0

    def __lt__(self, other):
        CInt.count += 1
        return int.__lt__(self, other)


K_LATE = 20


def make_alerts(n, kind, seed):
    rng = random.Random(seed)
    base = [(f"A{k}", rng.randint(1, 10)) for k in range(n)]
    if kind == "random":
        return base
    # nearly sorted = a queue that was already sorted, plus K_LATE alerts that arrived since the last sort
    arr = sorted(base[:n - K_LATE], key=lambda a: -a[1]) + base[n - K_LATE:]
    return arr


print("\n== sorting comparisons ==")
rows = []
for kind in ("random", "nearly_sorted"):
    for n in (1000, 2000, 5000, 10000, 50000):
        if kind == "random" and n == 50000:
            continue                                   # ~560 million comparisons; analytic value only
        data = make_alerts(n, kind, 7 + n)
        counted = [(a, CInt(s)) for a, s in data]
        CInt.count = 0
        r1, t1 = timed(C.sort_alerts, list(counted))
        ins = CInt.count
        CInt.count = 0
        r2, t2 = timed(O.sort_alerts, list(counted))
        tim = CInt.count
        assert [(a, int(s)) for a, s in r1] == [(a, int(s)) for a, s in r2]
        rows.append([kind, n, ins, tim, round(t1, 4), round(t2, 4)])
        print(rows[-1], flush=True)
write_csv("sort_comparisons.csv", ["input", "n", "insertion_comparisons", "timsort_comparisons",
                                   "insertion_seconds", "timsort_seconds"], rows)

# ---------------------------------------------------------------- blocklist
print("\n== blocklist look-ups ==")
b, q = 1000, 50000
rng = random.Random(5)
ips = [f"10.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}" for _ in range(b)]
ips = list(dict.fromkeys(ips))
queries = [rng.choice(ips) if rng.random() < 0.5 else f"192.168.{rng.randint(0, 255)}.{rng.randint(0, 255)}"
           for _ in range(q)]


class CStr(str):
    count = 0

    def __eq__(self, other):
        CStr.count += 1
        return str.__eq__(self, other)

    __hash__ = str.__hash__


cl = [CStr(x) for x in ips]
CStr.count = 0
for qq in queries[:5000]:
    C.is_blocked(cl, qq)
seq_cmp_5000 = CStr.count
t = time.perf_counter()
r_seq = [C.is_blocked(ips, x) for x in queries]
t_seq = time.perf_counter() - t
t = time.perf_counter()
bs = O.build_blocklist(ips)
t_build = time.perf_counter() - t
t = time.perf_counter()
r_set = [O.is_blocked(bs, x) for x in queries]
t_set = time.perf_counter() - t
assert r_seq == r_set
rows = [[len(ips), q, seq_cmp_5000 / 5000, round(t_seq, 3), round(t_build, 5), round(t_set, 4)]]
print(rows)
write_csv("blocklist_measurements.csv", ["b", "queries", "avg_comparisons_per_lookup_sequential(measured on 5000)",
                                         "sequential_seconds_for_all_queries", "set_build_seconds",
                                         "set_lookup_seconds_for_all_queries"], rows)

# ------------------------------------------------------------------ signature
print("\n== signature scan: character comparisons ==")


def count_cmp_original(log, pat):
    n, m = len(log), len(pat)
    c = 0
    for i in range(n - m):
        for j in range(m):
            c += 1
            if log[i + j] != pat[j]:
                break
    return c


rows = []
cases = [("test log FAILFAIXFAIL / FAIL", "FAILFAIXFAIL", "FAIL")]
rng = random.Random(9)
cases.append(("random DNA 100,000 chars / 8-mer", "".join(rng.choice("ACGT") for _ in range(100000)), "ACGTACGT"))
cases.append(("worst case a*100,000 / a^7 b", "a" * 100000, "aaaaaaab"))
cases.append(("best case b*100,000 / FAIL", "b" * 100000, "FAIL"))
for name, lg, pt in cases:
    st = {}
    hits = O.find_signature(lg, pt, st)
    assert hits == C.find_signature(lg, pt)
    # independent formula: per alignment, (length of the matching prefix + 1 mismatch) or m on a full match
    need = 0
    for i in range(len(lg) - len(pt) + 1):
        k = 0
        while k < len(pt) and lg[i + k] == pt[k]:
            k += 1
        need += k if k == len(pt) else k + 1
    assert need == st["comparisons"], (need, st["comparisons"])   # no comparison is redundant
    rows.append([name, len(lg), len(pt), count_cmp_original(lg, pt), st["comparisons"], len(hits)])
    print(rows[-1])
write_csv("signature_measurements.csv", ["case", "n", "m", "original_char_comparisons(buggy loop)",
                                         "optimised_char_comparisons", "hits"], rows)

# ------------------------------------------------------------------- graphs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
cp = list(csv.DictReader(open(os.path.join(RES, "closest_pair_measurements.csv"))))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ns = SIZES
for ds, style, col in (("uniform", "-o", "#1f77b4"), ("clustered", "-s", "#2ca02c"), ("same_x", "-^", "#d62728")):
    ax.plot(ns, [int(r["optimised_dist_comps"]) for r in cp if r["dataset"] == ds], style, color=col, label=f"optimised ({ds})")
ax.plot(ns, [int(r["corrected_brute_dist_comps"]) for r in cp if r["dataset"] == "uniform"], "k--o", label="brute force n(n-1)/2")
ax.set_yscale("log"); ax.set_xlabel("number of login events n"); ax.set_ylabel("distance computations (log scale)")
ax.set_title("closest_logins: distance computations"); ax.legend(fontsize=8); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(RES, "graph_closest_pair.png"), dpi=170); plt.close(fig)

so = list(csv.DictReader(open(os.path.join(RES, "sort_comparisons.csv"))))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
for kind, ykey, style, col, lab in (("random", "insertion_comparisons", "-o", "#d62728", "insertion sort, random"),
                                    ("nearly_sorted", "insertion_comparisons", "-s", "#1f77b4", "insertion sort, nearly sorted"),
                                    ("random", "timsort_comparisons", "--^", "#7f7f7f", "Timsort, random"),
                                    ("nearly_sorted", "timsort_comparisons", "--v", "#2ca02c", "Timsort, nearly sorted")):
    pts = [(int(r["n"]), int(r[ykey])) for r in so if r["input"] == kind]
    ax.plot(*zip(*pts), style, color=col, label=lab)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("number of alerts n"); ax.set_ylabel("comparisons (log scale)")
ax.set_title("Alert sorting: comparisons"); ax.legend(fontsize=8); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(RES, "graph_sorting.png"), dpi=170); plt.close(fig)
print("\ngraphs written")
