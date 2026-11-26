"""Q6 - (A) Median of Medians vs QuickSelect, (B) Meet-in-the-Middle subset sum vs 2^n enumeration."""
import random, time, itertools, bisect

# ---------- A: selection (k-th smallest, k is 1-based) ----------
def mom_select(a, k, st):
    if len(a) <= 5:
        st['cmp'] += len(a) * len(a); return sorted(a)[k - 1]
    groups = [sorted(a[i:i + 5]) for i in range(0, len(a), 5)]
    st['cmp'] += 10 * len(groups)
    medians = [g[len(g) // 2] for g in groups]
    pivot = mom_select(medians, (len(medians) + 1) // 2, st)          # median of medians
    return _finish(a, k, pivot, st, lambda b, kk: mom_select(b, kk, st))

def quickselect(a, k, st, pivot_fn):
    if len(a) == 1: return a[0]
    return _finish(a, k, pivot_fn(a), st, lambda b, kk: quickselect(b, kk, st, pivot_fn))

def _finish(a, k, pivot, st, rec):
    st['cmp'] += len(a)
    lo = [x for x in a if x < pivot]; eq = [x for x in a if x == pivot]; hi = [x for x in a if x > pivot]
    if k <= len(lo): return rec(lo, k)
    if k <= len(lo) + len(eq): return pivot
    return rec(hi, k - len(lo) - len(eq))

# ---------- B: meet in the middle ----------
def subset_sums(items):
    s = [0]
    for x in items: s += [y + x for y in s]
    return s

def mitm_subset_sum(items, target):
    h = len(items) // 2
    L = subset_sums(items[:h]); R = sorted(subset_sums(items[h:]))
    for x in L:                                         # binary search complement in R
        i = bisect.bisect_left(R, target - x)
        if i < len(R) and R[i] == target - x: return True, len(L) + len(R)
    return False, len(L) + len(R)

def brute_subset_sum(items, target):
    ops = 0
    for mask in range(1 << len(items)):
        ops += 1
        if sum(x for i, x in enumerate(items) if mask >> i & 1) == target: return True, ops
    return False, ops

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(200000); random.seed(2)
    print("=== Q6A: Median of Medians vs QuickSelect (find median) ===")
    first = lambda a: a[0]; rnd_p = lambda a: random.choice(a)
    print(f"{'n':>7} {'MoM cmp':>10} {'QS-random':>10} {'QS-first pivot (sorted input)':>30}")
    for n in [100, 500, 1000, 2000, 3000]:
        a = random.sample(range(10 * n), n); k = (n + 1) // 2
        s1, s2, s3 = {'cmp': 0}, {'cmp': 0}, {'cmp': 0}
        r1 = mom_select(a, k, s1); r2 = quickselect(a, k, s2, rnd_p)
        r3 = quickselect(sorted(a), n, s3, first)               # deterministic poor pivot: sorted input, ask for max
        assert r1 == r2 == sorted(a)[k - 1] and r3 == max(a)
        print(f"{n:>7} {s1['cmp']:>10} {s2['cmp']:>10} {s3['cmp']:>30}")
    print("MoM stays ~linear (<= ~22n); first-element pivot on sorted input is quadratic (~n^2/2).")
    worst = 0
    for _ in range(300):
        a = random.sample(range(5000), 1000); s = {'cmp': 0}; quickselect(a, 500, s, rnd_p); worst = max(worst, s['cmp'])
    print(f"Randomised QuickSelect, 300 runs, n=1000: worst run used {worst} cmp (average-case ~3.4n, but not bounded).\n")

    print("=== Q6B: Meet-in-the-Middle Subset Sum ===")
    print(f"{'n':>4} {'2^n':>12} {'MITM states (2*2^(n/2))':>25} {'extra memory (ints)':>20} {'brute ms':>9} {'MITM ms':>8}")
    for n in [10, 16, 20, 22, 24, 40, 50]:
        items = [random.randint(10**4, 10**6) for _ in range(n)]; target = sum(items) // 2 + 1
        tb = '-'
        if n <= 20:
            t = time.perf_counter(); b = brute_subset_sum(items, target)[0]; tb = f"{(time.perf_counter()-t)*1000:.1f}"
        t = time.perf_counter(); m, st = mitm_subset_sum(items, target); tm = (time.perf_counter() - t) * 1000
        if n <= 20: assert b == m
        print(f"{n:>4} {2**n:>12} {st:>25} {2**(n//2)+2**(n-n//2):>20} {tb:>9} {tm:>8.1f}")
    print("n > 20 brute force is skipped (too slow); MITM uses O(2^(n/2)) time AND memory (time-memory trade-off).")
    items = [3, 34, 4, 12, 5, 2]; print("Sanity [3,34,4,12,5,2] target 9:", mitm_subset_sum(items, 9)[0], "| target 30:", mitm_subset_sum(items, 30)[0])
