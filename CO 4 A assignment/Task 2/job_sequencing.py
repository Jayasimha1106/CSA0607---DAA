"""Task 2 - Job Sequencing with Deadlines (greedy: highest profit first, latest free slot)."""
import itertools, random


def job_sequencing(jobs, trace=False):
    """jobs: list of (id, deadline, profit). Returns (schedule by slot, total_profit)."""
    order = sorted(jobs, key=lambda j: (-j[2], j[0]))
    max_d = max(d for _, d, _ in jobs)
    slot = [None] * (max_d + 1)                       # slot[1..max_d]
    total = 0
    for jid, d, p in order:
        t = min(d, max_d)
        while t >= 1 and slot[t] is not None:
            t -= 1
        if t >= 1:
            slot[t] = jid
            total += p
            if trace:
                print(f"  {jid} (d={d}, p={p}): latest free slot <= {d} is {t} -> SCHEDULE | slots={slot[1:]} profit={total}")
        elif trace:
            print(f"  {jid} (d={d}, p={p}): no free slot in 1..{d} -> REJECT   | slots={slot[1:]} profit={total}")
    return slot[1:], total


def brute_force(jobs):
    best = 0
    for r in range(len(jobs) + 1):
        for sub in itertools.combinations(jobs, r):
            # feasible iff, sorted by deadline, the k-th job has deadline >= k
            ok = all(d >= k for k, (_, d, _) in enumerate(sorted(sub, key=lambda j: j[1]), 1))
            if ok:
                best = max(best, sum(p for _, _, p in sub))
    return best


if __name__ == "__main__":
    jobs = [("A", 2, 80), ("B", 1, 35), ("C", 2, 60), ("D", 3, 40), ("E", 1, 25)]
    print("=== Task 2.4 Desk-check (given instance) ===")
    s, t = job_sequencing(jobs, trace=True)
    print("Final schedule (slot1, slot2, slot3):", s, "| Total profit =", t)
    assert t == 180 == brute_force(jobs)

    print("\n=== Task 2.5 Challenge: change B's profit 35 -> 90 ===")
    jobs2 = [("A", 2, 80), ("B", 1, 90), ("C", 2, 60), ("D", 3, 40), ("E", 1, 25)]
    s, t = job_sequencing(jobs2, trace=True)
    print("Final schedule (slot1, slot2, slot3):", s, "| Total profit =", t)
    assert t == 210 == brute_force(jobs2)

    print("\n=== Additional tests ===")
    for name, js, exp in [
        ("single job", [("X", 1, 10)], 10),
        ("all deadline 1", [("P", 1, 5), ("Q", 1, 9), ("R", 1, 7)], 9),
        ("deadline > n", [("P", 9, 5), ("Q", 9, 9)], 14),
    ]:
        s, t = job_sequencing(js)
        print(f"{name:<16} schedule={s} profit={t} expected={exp}")
        assert t == exp
    random.seed(4)
    for _ in range(300):
        n = random.randint(1, 7)
        js = [(f"J{i}", random.randint(1, 5), random.randint(1, 50)) for i in range(n)]
        assert job_sequencing(js)[1] == brute_force(js), js
    print("300 random instances: greedy == brute-force optimum")
    print("\nAll Task 2 tests passed.")
