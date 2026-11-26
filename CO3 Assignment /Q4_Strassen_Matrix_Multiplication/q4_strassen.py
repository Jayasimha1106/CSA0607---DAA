"""Q4 - Conventional vs Strassen matrix multiplication (pure Python lists), with padding to power of two."""
import random, time

def conv(A, B, c):
    n, m, p = len(A), len(B), len(B[0])
    C = [[0] * p for _ in range(n)]
    for i in range(n):
        Ai = A[i]; Ci = C[i]
        for k in range(m):
            a = Ai[k]; Bk = B[k]
            for j in range(p):
                Ci[j] += a * Bk[j]
    c['mul'] += n * m * p
    return C

def add(A, B): return [[x + y for x, y in zip(r, s)] for r, s in zip(A, B)]
def sub(A, B): return [[x - y for x, y in zip(r, s)] for r, s in zip(A, B)]

def strassen(A, B, c, cutoff=1):
    n = len(A)
    if n <= cutoff:
        return conv(A, B, c)
    h = n // 2
    sp = lambda M, r, q: [row[q:q + h] for row in M[r:r + h]]
    A11, A12, A21, A22 = sp(A, 0, 0), sp(A, 0, h), sp(A, h, 0), sp(A, h, h)
    B11, B12, B21, B22 = sp(B, 0, 0), sp(B, 0, h), sp(B, h, 0), sp(B, h, h)
    c['add'] += 18 * h * h
    M1 = strassen(add(A11, A22), add(B11, B22), c, cutoff)
    M2 = strassen(add(A21, A22), B11, c, cutoff)
    M3 = strassen(A11, sub(B12, B22), c, cutoff)
    M4 = strassen(A22, sub(B21, B11), c, cutoff)
    M5 = strassen(add(A11, A12), B22, c, cutoff)
    M6 = strassen(sub(A21, A11), add(B11, B12), c, cutoff)
    M7 = strassen(sub(A12, A22), add(B21, B22), c, cutoff)
    C11 = add(sub(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(add(sub(M1, M2), M3), M6)
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]

def pad_size(n):
    p = 1
    while p < n: p *= 2
    return p

def strassen_any(A, B, c, cutoff=1):
    """Handles any n x n by zero-padding to the next power of two and cropping the result."""
    n = len(A); p = pad_size(n)
    Ap = [r + [0] * (p - n) for r in A] + [[0] * p for _ in range(p - n)]
    Bp = [r + [0] * (p - n) for r in B] + [[0] * p for _ in range(p - n)]
    C = strassen(Ap, Bp, c, cutoff)
    return [r[:n] for r in C[:n]]

def rnd(n): return [[random.randint(-9, 9) for _ in range(n)] for _ in range(n)]
def best(f, reps):
    b = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); b = min(b, time.perf_counter() - t)
    return b * 1000

if __name__ == "__main__":
    random.seed(5)
    print("=== Q4: Correctness (vs conventional) ===")
    for n in [1, 2, 3, 5, 8, 13, 30, 33, 64]:
        A, B = rnd(n), rnd(n)
        assert strassen_any(A, B, {'mul': 0, 'add': 0}) == conv(A, B, {'mul': 0})
    print("Passed for n = 1,2,3,5,8,13,30,33,64 (incl. non powers of two via padding)\n")
    print("=== Q4: Scalar multiplication counts (cutoff = 1) ===")
    print(f"{'n':>5} {'conventional n^3':>17} {'strassen 7^k':>13} {'ratio':>7} {'additions(S)':>13}")
    for n in [2, 4, 8, 16, 32, 64, 128]:
        c = {'mul': 0, 'add': 0}; strassen(rnd(n), rnd(n), c)
        print(f"{n:>5} {n**3:>17} {c['mul']:>13} {c['mul']/n**3:>7.3f} {c['add']:>13}")
    print("\n=== Q4: Padding overhead for non powers of two ===")
    print(f"{'n':>5} {'padded':>7} {'mults (S)':>10} {'n^3':>10} {'S/n^3':>7}")
    for n in [33, 65, 100]:
        c = {'mul': 0, 'add': 0}; strassen_any(rnd(n), rnd(n), c)
        print(f"{n:>5} {pad_size(n):>7} {c['mul']:>10} {n**3:>10} {c['mul']/n**3:>7.3f}")
    print("\n=== Q4: Timing, best of 3 (ms) ===")
    print(f"{'n':>5} {'conv':>10} {'strassen(cut=1)':>16} {'strassen(cut=32)':>17} {'winner':>9}")
    for n in [8, 16, 32, 64, 128, 256]:
        A, B = rnd(n), rnd(n)
        tc = best(lambda: conv(A, B, {'mul': 0}), 3)
        t1 = best(lambda: strassen(A, B, {'mul': 0, 'add': 0}), 1 if n >= 128 else 3)
        t32 = best(lambda: strassen(A, B, {'mul': 0, 'add': 0}, 32), 3)
        print(f"{n:>5} {tc:>10.2f} {t1:>16.2f} {t32:>17.2f} {('conv' if tc <= min(t1, t32) else 'strassen'):>9}")
