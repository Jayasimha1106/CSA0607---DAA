"""Q1 - Max/Min by Divide & Conquer and Binary Search, with comparison counting."""
import math, random

def max_min(a, lo, hi, cnt):
    """Returns (min, max) of a[lo..hi]; cnt[0] counts element comparisons."""
    if lo == hi:
        return a[lo], a[lo]
    if hi == lo + 1:
        cnt[0] += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    mn1, mx1 = max_min(a, lo, mid, cnt)
    mn2, mx2 = max_min(a, mid + 1, hi, cnt)
    cnt[0] += 2
    return min(mn1, mn2), max(mx1, mx2)

def predicted(n):
    def T(m):
        if m == 1: return 0
        if m == 2: return 1
        return T(m // 2) + T(m - m // 2) + 2
    return T(n)

def binary_search(a, target):
    lo, hi, cnt = 0, len(a) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        cnt += 1
        if a[mid] == target: return mid, cnt
        if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1, cnt

if __name__ == "__main__":
    random.seed(1)
    print("=== Q1 Part A: Divide & Conquer Max/Min ===")
    print("Sanity (min,max) of [5,2,9,1,7,3,8]:", max_min([5, 2, 9, 1, 7, 3, 8], 0, 6, [0]))
    print(f"{'n':>6} {'D&C obs':>8} {'Predicted':>9} {'3n/2-2':>8} {'Naive 2(n-1)':>13} {'Diff':>5}")
    for n in [2, 4, 8, 16, 64, 256, 1024, 4096, 10, 100, 1000, 5000]:
        a = random.sample(range(10 * n), n)
        c = [0]; mn, mx = max_min(a, 0, n - 1, c)
        assert mn == min(a) and mx == max(a)
        print(f"{n:>6} {c[0]:>8} {predicted(n):>9} {1.5*n-2:>8.1f} {2*(n-1):>13} {c[0]-predicted(n):>5}")
    print("\nData-independence check (n=1024):")
    n = 1024
    for name, a in [("random", random.sample(range(n), n)), ("sorted", list(range(n))),
                    ("reverse", list(range(n, 0, -1))), ("all-equal", [7] * n)]:
        c = [0]; max_min(a, 0, n - 1, c); print(f"  {name:>9}: {c[0]} comparisons")

    print("\n=== Q1 Part B: Binary Search ===")
    print(f"{'n':>8} {'succ avg':>9} {'succ max':>9} {'unsucc max':>11} {'floor(log2n)+1':>15}")
    for n in [16, 100, 1000, 10**4, 10**5, 10**6]:
        a = list(range(0, 2 * n, 2))
        succ = [binary_search(a, x)[1] for x in random.sample(a, min(n, 2000))]
        uns = [binary_search(a, x)[1] for x in random.sample(range(1, 2 * n, 2), min(n, 2000))]
        print(f"{n:>8} {sum(succ)/len(succ):>9.2f} {max(succ):>9} {max(uns):>11} {int(math.log2(n))+1:>15}")
    a = list(range(0, 40, 2))
    print("\nTrace a=0,2,..,38: target 26 ->", binary_search(a, 26), "| target 27 ->", binary_search(a, 27))
