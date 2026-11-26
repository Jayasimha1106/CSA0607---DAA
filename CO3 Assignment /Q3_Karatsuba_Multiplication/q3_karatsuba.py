"""Q3 - Standard (grade-school) vs Karatsuba multiplication on decimal digit strings.
Both count single-digit multiplications. Numbers are handled as digit lists (no built-in big multiply)."""
import random, time

def to_digits(x): return [int(c) for c in str(x)[::-1]]            # little-endian
def from_digits(d):
    while len(d) > 1 and d[-1] == 0: d = d[:-1]
    return int(''.join(map(str, d[::-1])))

def school(a, b, cnt):
    res = [0] * (len(a) + len(b))
    for i, x in enumerate(a):
        carry = 0
        for j, y in enumerate(b):
            cnt[0] += 1
            t = res[i + j] + x * y + carry
            res[i + j] = t % 10; carry = t // 10
        res[i + len(b)] += carry
    return res

def add(a, b):
    n = max(len(a), len(b)); r = []; c = 0
    for i in range(n):
        s = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) + c
        r.append(s % 10); c = s // 10
    if c: r.append(c)
    return r

def sub(a, b):                                                        # a >= b
    r = []; br = 0
    for i in range(len(a)):
        s = a[i] - (b[i] if i < len(b) else 0) - br
        if s < 0: s += 10; br = 1
        else: br = 0
        r.append(s)
    return r

def shift(a, k): return [0] * k + a

def karatsuba(a, b, cnt, cutoff=1):
    n = max(len(a), len(b))
    if n <= cutoff:
        return school(a, b, cnt)
    a = a + [0] * (n - len(a)); b = b + [0] * (n - len(b))
    m = n // 2
    a0, a1 = a[:m], a[m:]; b0, b1 = b[:m], b[m:]                      # x = x1*10^m + x0
    z0 = karatsuba(a0, b0, cnt, cutoff)
    z2 = karatsuba(a1, b1, cnt, cutoff)
    z1 = karatsuba(add(a0, a1), add(b0, b1), cnt, cutoff)              # (a0+a1)(b0+b1)
    mid = sub(sub(z1, z0), z2)                                        # a0b1 + a1b0
    return add(add(z0, shift(mid, m)), shift(z2, 2 * m))

def rnd(n): return random.randint(10**(n-1), 10**n - 1)

def timeit(f, reps):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); best = min(best, time.perf_counter() - t)
    return best

if __name__ == "__main__":
    random.seed(3)
    print("=== Q3: Correctness ===")
    for n in [1, 2, 5, 17, 64, 100]:
        x, y = rnd(n), rnd(n); c = [0]
        assert from_digits(karatsuba(to_digits(x), to_digits(y), c)) == x * y
        assert from_digits(school(to_digits(x), to_digits(y), [0])) == x * y
    print("All checks passed (vs Python's built-in x*y).\n")
    print("=== Q3: Multiplication counts (single-digit mults, cutoff = 1 digit) ===")
    print(f"{'digits':>7} {'school n^2':>11} {'karatsuba':>10} {'n^1.585':>9} {'ratio K/S':>10}")
    for n in [2, 4, 8, 16, 32, 64, 128, 256, 512]:
        x, y = rnd(n), rnd(n); cs, ck = [0], [0]
        school(to_digits(x), to_digits(y), cs); karatsuba(to_digits(x), to_digits(y), ck)
        print(f"{n:>7} {cs[0]:>11} {ck[0]:>10} {n**1.585:>9.0f} {ck[0]/cs[0]:>10.3f}")
    print("\n=== Q3: Crossover timing (best of 5 runs, ms, pure-Python digit lists) ===")
    print(f"{'digits':>7} {'school':>9} {'karat(cut=1)':>13} {'karat(cut=16)':>14} {'winner':>14}")
    for n in [4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 512, 1024]:
        a, b = to_digits(rnd(n)), to_digits(rnd(n))
        ts = timeit(lambda: school(a, b, [0]), 5) * 1000
        tk = timeit(lambda: karatsuba(a, b, [0]), 5) * 1000
        th = timeit(lambda: karatsuba(a, b, [0], 16), 5) * 1000
        print(f"{n:>7} {ts:>9.3f} {tk:>13.3f} {th:>14.3f} {('school' if ts < min(tk, th) else 'karatsuba' if tk <= th else 'hybrid'):>14}")
