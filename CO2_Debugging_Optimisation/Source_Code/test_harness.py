"""Test harness for the SentinelOps module (corrected + optimised).

Run:  python Source_Code/test_harness.py
Exit status is 0 only if every check passes.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corrected as C   # noqa: E402
import optimised as O   # noqa: E402

passed = failed = 0


def check(name, actual, expected):
    """Record one test result."""
    global passed, failed
    ok = actual == expected
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok else f"\n       expected {expected!r}\n       actual   {actual!r}"))


ALERTS = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
SORTED = [("A2", 9), ("A4", 9), ("A3", 5), ("A1", 3), ("A5", 1)]
BL = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
EVENTS = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
SQRT2 = math.sqrt(2)

print("--- sort_alerts ---")
for tag, f in (("corrected insertion", C.sort_alerts), ("optimised insertion", O.sort_alerts_insertion),
               ("optimised timsort", O.sort_alerts)):
    check(f"{tag}: sample data", f(list(ALERTS)), SORTED)
    check(f"{tag}: empty list", f([]), [])
    check(f"{tag}: single alert", f([("X", 4)]), [("X", 4)])
    check(f"{tag}: all equal severity keeps arrival order", f([("a", 5), ("b", 5), ("c", 5)]), [("a", 5), ("b", 5), ("c", 5)])
    check(f"{tag}: already sorted", f(list(SORTED)), SORTED)
    check(f"{tag}: reverse order", f(list(reversed(SORTED))), [("A4", 9), ("A2", 9), ("A3", 5), ("A1", 3), ("A5", 1)])
    check(f"{tag}: lowest severity first in input", f([("L", 1), ("H", 9)]), [("H", 9), ("L", 1)])
    check(f"{tag}: no alert lost or duplicated", sorted(f(list(ALERTS))), sorted(ALERTS))

print("--- is_blocked ---")
prepared = O.build_blocklist(BL)
for tag, f, bl in (("corrected list", C.is_blocked, BL), ("optimised list", O.is_blocked, BL),
                   ("optimised set", O.is_blocked, prepared)):
    check(f"{tag}: first entry", f(bl, "10.0.0.5"), True)
    check(f"{tag}: middle entry", f(bl, "10.0.0.9"), True)
    check(f"{tag}: last entry", f(bl, "172.16.4.2"), True)
    check(f"{tag}: absent IP", f(bl, "8.8.8.8"), False)
    check(f"{tag}: prefix of a listed IP is not blocked", f(bl, "10.0.0"), False)
check("corrected: empty blocklist", C.is_blocked([], "10.0.0.5"), False)
check("optimised: empty list", O.is_blocked([], "10.0.0.5"), False)
check("optimised: empty set", O.is_blocked(O.build_blocklist([]), "10.0.0.5"), False)

print("--- find_signature ---")
for tag, f in (("corrected", C.find_signature), ("optimised", O.find_signature)):
    check(f"{tag}: sample log", f("FAILFAIXFAIL", "FAIL"), [0, 8])
    check(f"{tag}: pattern at very end", f("xxxxFAIL", "FAIL"), [4])
    check(f"{tag}: pattern at very start", f("FAILxxxx", "FAIL"), [0])
    check(f"{tag}: pattern equals log", f("FAIL", "FAIL"), [0])
    check(f"{tag}: pattern longer than log", f("FAI", "FAIL"), [])
    check(f"{tag}: no occurrence", f("ABCDEFG", "FAIL"), [])
    check(f"{tag}: last-char mismatch is not a hit", f("FAIX", "FAIL"), [])
    check(f"{tag}: overlapping occurrences", f("aaaa", "aa"), [0, 1, 2])
    check(f"{tag}: empty log", f("", "FAIL"), [])
    check(f"{tag}: empty pattern", f("abc", ""), [])
    check(f"{tag}: single-character pattern", f("abcabc", "c"), [2, 5])

print("--- closest_logins ---")
for tag, f in (("corrected", C.closest_logins), ("optimised", O.closest_logins)):
    check(f"{tag}: sample events", f(EVENTS), ((0, 5), SQRT2))
    check(f"{tag}: empty list", f([]), (None, None))
    check(f"{tag}: one event", f([(1, 1)]), (None, None))
    check(f"{tag}: two events", f([(0, 0), (3, 4)]), ((0, 1), 5.0))
    check(f"{tag}: duplicate location gives distance 0", f([(0, 0), (9, 9), (0, 0)]), ((0, 2), 0.0))
    check(f"{tag}: tie -> smallest (i, j)", f([(0, 0), (1, 0), (5, 5), (6, 5)]), ((0, 1), 1.0))
    check(f"{tag}: all on one vertical line", f([(0, 0), (0, 10), (0, 11), (0, 30)]), ((1, 2), 1.0))

print("--- randomised differential tests (optimised vs corrected / reference) ---")
rng = random.Random(2026)
ok_sort = ok_sig = ok_cp = ok_bl = True
for _ in range(500):
    n = rng.randint(0, 40)
    al = [(f"A{k}", rng.randint(1, 6)) for k in range(n)]
    ref = sorted(al, key=lambda a: -a[1])                       # stable reference
    ok_sort &= C.sort_alerts(list(al)) == ref == O.sort_alerts(list(al)) == O.sort_alerts_insertion(list(al))
    log = "".join(rng.choice("ab") for _ in range(rng.randint(0, 30)))
    pat = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
    expect = [i for i in range(len(log) - len(pat) + 1) if log[i:i + len(pat)] == pat]
    ok_sig &= C.find_signature(log, pat) == O.find_signature(log, pat) == expect
    ev = [(rng.randint(0, 15), rng.randint(0, 15)) for _ in range(rng.randint(0, 30))]
    ok_cp &= C.closest_logins(ev) == O.closest_logins(ev)
    bl = [f"10.0.0.{rng.randint(0, 20)}" for _ in range(rng.randint(0, 10))]
    q = f"10.0.0.{rng.randint(0, 20)}"
    ok_bl &= C.is_blocked(bl, q) == O.is_blocked(bl, q) == O.is_blocked(O.build_blocklist(bl), q) == (q in bl)
check("500 random cases: sorting identical to stable reference", ok_sort, True)
check("500 random cases: is_blocked identical", ok_bl, True)
check("500 random cases: find_signature identical to slicing reference", ok_sig, True)
check("500 random cases: closest_logins identical (pair AND distance, incl. ties)", ok_cp, True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
