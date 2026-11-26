"""Task 6 - Energy-aware job scheduling = Weighted Interval Scheduling (dynamic programming)."""
import bisect, itertools, random


def schedule(jobs, trace=False):
    """jobs: list of (id, start, finish, value). Returns (best, selected ids)."""
    J = sorted(jobs, key=lambda j: (j[2], j[1], j[0]))           # sort by finish time
    n = len(J)
    fin = [j[2] for j in J]
    # p[k] = number of earlier jobs (in sorted order) whose finish <= start of job k
    p = [0] * (n + 1)
    for k in range(1, n + 1):
        p[k] = bisect.bisect_right(fin, J[k - 1][1], 0, k - 1)
    OPT = [0] * (n + 1)
    take = [False] * (n + 1)
    if trace:
        print(f"{'k':<3}{'job':<5}{'s':>3}{'f':>4}{'v':>4}{'p(k)':>6}{'include=v+OPT[p]':>19}{'exclude':>9}{'OPT[k]':>8}  decision")
    for k in range(1, n + 1):
        inc = J[k - 1][3] + OPT[p[k]]
        exc = OPT[k - 1]
        if inc > exc:
            OPT[k], take[k] = inc, True
        else:
            OPT[k] = exc
        if trace:
            jid, s, f, v = J[k - 1]
            print(f"{k:<3}{jid:<5}{s:>3}{f:>4}{v:>4}{p[k]:>6}{f'{v}+{OPT[p[k]]}={inc}':>19}{exc:>9}{OPT[k]:>8}  {'INCLUDE' if take[k] else 'EXCLUDE'}")
    sel, k = [], n
    while k > 0:
        if take[k]:
            sel.append(J[k - 1][0]); k = p[k]
        else:
            k -= 1
    sel.reverse()
    if trace:
        print("OPT array:", OPT)
        print("p array  :", p[1:])
    return OPT[n], sel


def brute(jobs):
    best = 0
    for r in range(len(jobs) + 1):
        for sub in itertools.combinations(jobs, r):
            s = sorted(sub, key=lambda j: j[1])
            if all(s[i][2] <= s[i + 1][1] for i in range(len(s) - 1)):
                best = max(best, sum(j[3] for j in sub))
    return best


def greedy_value(jobs):
    tot, chosen = 0, []
    for j in sorted(jobs, key=lambda j: -j[3]):
        if all(j[2] <= c[1] or c[2] <= j[1] for c in chosen):
            chosen.append(j); tot += j[3]
    return tot, [c[0] for c in chosen]


def greedy_finish(jobs):
    tot, last, chosen = 0, -10**9, []
    for j in sorted(jobs, key=lambda j: j[2]):
        if j[1] >= last:
            chosen.append(j[0]); tot += j[3]; last = j[2]
    return tot, chosen


if __name__ == "__main__":
    jobs = [("J1", 1, 3, 20), ("J2", 2, 5, 50), ("J3", 4, 6, 30), ("J4", 6, 8, 40),
            ("J5", 5, 9, 60), ("J6", 8, 10, 30), ("J7", 9, 11, 50), ("J8", 11, 13, 40)]
    print("=== Stage 5 Desk-check: given dataset ===")
    best, sel = schedule(jobs, trace=True)
    print("Selected jobs:", sel, "| Total energy saving =", best)
    assert best == 200 == brute(jobs) and sel == ["J2", "J5", "J7", "J8"]
    print("For comparison: greedy highest-value =", greedy_value(jobs), "| greedy earliest-finish =", greedy_finish(jobs))

    print("\n=== Stage 6 Adversarial Test A: long high-value job vs three shorter jobs ===")
    A = [("S1", 0, 3, 20), ("S2", 3, 6, 20), ("M", 2, 8, 15), ("S3", 6, 10, 20), ("L", 0, 10, 50)]
    best, sel = schedule(A, trace=True)
    print("DP result:", best, sel, "| brute force:", brute(A))
    print("Greedy highest-value:", greedy_value(A), "-> suboptimal")
    assert best == brute(A) == 60

    print("\n=== Stage 6 Adversarial Test B: earliest-finish trap ===")
    B = [("E", 0, 2, 1), ("F", 2, 4, 2), ("G", 4, 6, 2), ("I", 6, 8, 2), ("H", 1, 10, 100)]
    best, sel = schedule(B, trace=True)
    print("DP result:", best, sel, "| brute force:", brute(B))
    print("Greedy earliest-finish:", greedy_finish(B), "-> suboptimal")
    assert best == brute(B) == 100

    print("\n=== Boundary tests ===")
    for name, js in [("touching jobs [0,2],[2,4]", [("a", 0, 2, 5), ("b", 2, 4, 6)]),
                     ("identical interval", [("a", 1, 3, 5), ("b", 1, 3, 9)]),
                     ("single job", [("a", 1, 3, 5)])]:
        b, s = schedule(js); print(f"{name:<28} best={b} selected={s}"); assert b == brute(js)
    random.seed(6)
    for _ in range(500):
        js = []
        for k in range(random.randint(1, 9)):
            s = random.randint(0, 12); js.append((f"J{k}", s, s + random.randint(1, 6), random.randint(1, 60)))
        b, s = schedule(js)
        assert b == brute(js)
        chosen = sorted([j for j in js if j[0] in s], key=lambda j: j[1])
        assert all(chosen[i][2] <= chosen[i + 1][1] for i in range(len(chosen) - 1)) and sum(j[3] for j in chosen) == b
    print("500 random instances: DP == brute force, selected set non-overlapping")
    print("\nAll Task 6 tests passed.")
