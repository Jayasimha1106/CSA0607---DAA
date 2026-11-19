"""Apply the nine fixes ONE AT A TIME to the original source and re-test after each.

Run:  python experiments/debug_steps.py
Also prints the insertion-sort trace and the string-alignment table used in the report.
"""
import math
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "original.py")
text = open(SRC).read()

FIXES = [
    ("D1", "sort_alerts",    "while j > 0 and", "while j >= 0 and"),
    ("D2", "sort_alerts",    "        alerts[j] = key", "        alerts[j + 1] = key"),
    ("D3", "is_blocked",     "        if blocklist[i] == ip:\n            return False\n        else:\n            return False",
                             "        if blocklist[i] == ip:\n            return True\n        else:\n            return False"),
    ("D4", "is_blocked",     "        else:\n            return False", "    return False"),
    ("D5", "find_signature", "range(n - m)", "range(n - m + 1)"),
    ("D6", "find_signature", "        if j == m - 1:\n            hits.append(i)",
                             "        else:\n            hits.append(i)"),
    ("D7", "closest_logins", "min_dist = 0", "min_dist = float('inf')"),
    ("D8", "closest_logins", "if d > min_dist:", "if d < min_dist:"),
    ("D9", "closest_logins", "for j in range(len(events)):", "for j in range(i + 1, len(events)):"),
]
# D6 needs the for-else form: the 'else' must belong to the inner for loop
text_for_else = None

ALERTS = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
BL = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
EV = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]


def load(src):
    ns = {"math": math}
    exec(compile(src, "<step>", "exec"), ns)
    return ns


def run_tests(ns):
    return {
        "sort_alerts": ns["sort_alerts"](list(ALERTS)),
        "is_blocked": [ns["is_blocked"](BL, q) for q in ("10.0.0.9", "10.0.0.5", "8.8.8.8")],
        "is_blocked([])": ns["is_blocked"]([], "10.0.0.5"),
        "find_signature": ns["find_signature"]("FAILFAIXFAIL", "FAIL"),
        "closest_logins": ns["closest_logins"](EV),
    }


print("=== cumulative fixes: re-test after every correction ===")
cur = text
print("start (original):", run_tests(load(cur)))
for fid, fn, old, new in FIXES:
    if fid == "D6":
        # restructure so the 'else' pairs with the inner for-loop
        old = "            if log[i + j] != pattern[j]:\n                break\n        if j == m - 1:\n            hits.append(i)"
        new = "            if log[i + j] != pattern[j]:\n                break\n        else:\n            hits.append(i)"
    if fid == "D4":
        old = "            return True\n        else:\n            return False"
        new = "            return True\n    return False"
    assert old in cur, (fid, "pattern not found")
    cur = cur.replace(old, new, 1)
    print(f"\nafter {fid} ({fn}):")
    for k, v in run_tests(load(cur)).items():
        print(f"   {k:16s} -> {v}")

print("\n=== insertion-sort trace: BUGGY (D1, D2) ===")
a = list(ALERTS)
print("start:", a)
for i in range(1, len(a)):
    key = a[i]; j = i - 1
    while j > 0 and a[j][1] < key[1]:
        a[j + 1] = a[j]; j -= 1
    a[j] = key
    print(f"i={i} key={key}  final j={j} -> {a}")

print("\n=== insertion-sort trace: CORRECTED ===")
a = list(ALERTS)
print("start:", a)
for i in range(1, len(a)):
    key = a[i]; j = i - 1; steps = 0
    while j >= 0 and a[j][1] < key[1]:
        a[j + 1] = a[j]; j -= 1; steps += 1
    a[j + 1] = key
    print(f"i={i} key={key}  shifts={steps} insert at {j + 1} -> {a}")

print("\n=== alignment table  log='FAILFAIXFAIL'  pattern='FAIL' ===")
log, pat = "FAILFAIXFAIL", "FAIL"
n, m = len(log), len(pat)
for i in range(n - m + 1):
    cmp = []
    j = 0
    while j < m:
        ok = log[i + j] == pat[j]
        cmp.append(f"{log[i+j]}{'=' if ok else '!'}{pat[j]}")
        if not ok:
            break
        j += 1
    full = j == m
    orig_vis = "visited" if i < n - m else "NEVER visited (range(n-m))"
    orig_hit = (j >= m - 1) if i < n - m else False
    print(f"i={i}: {' '.join(cmp):24s} true match={full!s:5s} original loop: {orig_vis}; original reports hit={orig_hit}")
