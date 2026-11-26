"""Q2 - Merge Sort vs Quick Sort. Quick Sort pivot strategy: LAST element, stable list partition
(left = elements < pivot, right = elements >= pivot). Stable partition preserves relative order, so
inputs can be designed exactly to give balanced or maximally unbalanced splits."""
import sys, random, time
sys.setrecursionlimit(100000)

def merge_sort(a, st, d=1):
    st['depth'] = max(st['depth'], d)
    if len(a) <= 1: return a
    m = len(a) // 2
    L = merge_sort(a[:m], st, d + 1); R = merge_sort(a[m:], st, d + 1)
    out, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        st['cmp'] += 1
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else: out.append(R[j]); j += 1
    return out + L[i:] + R[j:]

def quick_sort(a, st, d=1):
    st['depth'] = max(st['depth'], d)
    if len(a) <= 1: return a
    p = a[-1]; rest = a[:-1]
    left = [x for x in rest if x < p]; right = [x for x in rest if x >= p]
    st['cmp'] += len(rest)
    if d <= 3: st['parts'].append((len(left), len(right)))   # record top partition sizes
    return quick_sort(left, st, d + 1) + [p] + quick_sort(right, st, d + 1)

def new(): return {'cmp': 0, 'depth': 0, 'parts': []}

def balanced_input(keys):
    """Arrange sorted keys so the LAST-element pivot is always the median."""
    if len(keys) <= 1: return list(keys)
    m = len(keys) // 2
    return balanced_input(keys[:m]) + balanced_input(keys[m + 1:]) + [keys[m]]

def run(f, a):
    st = new(); t = time.perf_counter(); r = f(list(a), st); t = time.perf_counter() - t
    assert r == sorted(a); return st, t

if __name__ == "__main__":
    random.seed(7)
    print("=== Q2: Merge Sort vs Quick Sort (pivot = last element) ===")
    print(f"{'n':>6} {'input':>9} | {'QS cmp':>9} {'QS depth':>8} {'QS ms':>8} | {'MS cmp':>8} {'MS depth':>8} {'MS ms':>7}")
    for n in [127, 255, 511, 1023, 2047]:
        keys = list(range(n))
        for name, a in [("balanced", balanced_input(keys)), ("random", random.sample(keys, n)),
                        ("sorted", keys), ("reverse", keys[::-1])]:
            q, tq = run(quick_sort, a); m, tm = run(merge_sort, a)
            print(f"{n:>6} {name:>9} | {q['cmp']:>9} {q['depth']:>8} {tq*1000:>8.2f} | {m['cmp']:>8} {m['depth']:>8} {tm*1000:>7.2f}")
        print()
    n = 1023; keys = list(range(n))
    for name, a in [("balanced", balanced_input(keys)), ("sorted (worst)", keys)]:
        q, _ = run(quick_sort, a)
        print(f"Top partition sizes (left,right) for n={n}, {name}: {q['parts'][:7]}")
    print("\nTheory: balanced -> depth ~ log2(n+1) = 10, comparisons ~ n log n.")
    print("        sorted   -> split (n-1, 0) every level: depth n, comparisons n(n-1)/2 =", n*(n-1)//2)
    print("90:10 split -> depth ~ log(n)/log(10/9) = %.1f for n=%d (still O(n log n), larger constant)" % (__import__('math').log(n)/__import__('math').log(10/9), n))
