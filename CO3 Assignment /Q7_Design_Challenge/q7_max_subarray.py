"""Q7 - Final joint design: Maximum Subarray Sum by Divide & Conquer.
Each subproblem returns a 4-tuple (total, best_prefix, best_suffix, best) - no scanning of the middle is needed."""
import random, time, sys
sys.setrecursionlimit(10000)
NEG = float('-inf')

def dc(a, lo, hi, cnt):
    if lo == hi:                                   # base case: single element
        x = a[lo]; return (x, x, x, x)
    mid = (lo + hi) // 2
    L = dc(a, lo, mid, cnt); R = dc(a, mid + 1, hi, cnt)
    cnt[0] += 5                                    # combine: 1 add + 4 max-comparisons
    total = L[0] + R[0]
    prefix = max(L[1], L[0] + R[1])
    suffix = max(R[2], R[0] + L[2])
    best = max(L[3], R[3], L[2] + R[1])            # entirely left, entirely right, or crossing the midpoint
    return (total, prefix, suffix, best)

def brute(a, cnt):
    best = NEG
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]; cnt[0] += 1
            if s > best: best = s
    return best

def kadane(a):
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x); best = max(best, cur)
    return best

def tests():
    cases = [[5], [-3], [-2, -1, -5], [1, 2, 3], [-1, 4, -2, 5, -3], [2, -1, 2, -1, 2], [0, 0, 0], [-2, 1, -3, 4, -1, 2, 1, -5, 4]]
    for c in cases:
        assert dc(c, 0, len(c) - 1, [0])[3] == brute(c, [0]) == kadane(c), c
    random.seed(4)
    for _ in range(500):
        n = random.randint(1, 40); a = [random.randint(-20, 20) for _ in range(n)]
        assert dc(a, 0, n - 1, [0])[3] == brute(a, [0]) == kadane(a)
    print("All 508 correctness tests passed (D&C == brute force == Kadane), incl. all-negative, single element, zeros.")

if __name__ == "__main__":
    print("=== Q7: Maximum Subarray - D&C design ==="); tests()
    random.seed(9)
    print(f"\n{'n':>7} {'brute ops n(n+1)/2':>19} {'D&C ops (5(n-1))':>17} {'brute ms':>9} {'D&C ms':>8} {'Kadane ms':>10}")
    for n in [16, 64, 256, 1024, 2048, 4096, 8192]:
        a = [random.randint(-100, 100) for _ in range(n)]
        cb, cd = [0], [0]
        t = time.perf_counter(); rb = brute(a, cb); tb = (time.perf_counter() - t) * 1000
        t = time.perf_counter(); rd = dc(a, 0, n - 1, cd)[3]; td = (time.perf_counter() - t) * 1000
        t = time.perf_counter(); rk = kadane(a); tk = (time.perf_counter() - t) * 1000
        assert rb == rd == rk
        print(f"{n:>7} {cb[0]:>19} {cd[0]:>17} {tb:>9.2f} {td:>8.2f} {tk:>10.3f}")
    print("\nRecurrence T(n)=2T(n/2)+O(1) -> Theta(n). Observed ops = 5(n-1) exactly.")
    print("Note: Kadane's O(n) single-scan DP is even simpler; D&C is still valuable for parallelism and as a D&C exercise.")
