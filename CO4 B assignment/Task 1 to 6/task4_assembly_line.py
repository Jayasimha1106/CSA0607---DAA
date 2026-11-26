"""
CO4 Assignment 4B - Task 4: Assembly-line scheduling (two lines) by Dynamic Programming

Inputs (n stations, 0-based lists; station k of the report is index k-1):
  a1[k], a2[k]  processing time at station k on line 1 / line 2
  t1[k]         time to move from line 1 AFTER station k to line 2 BEFORE station k+1   (length n-1)
  t2[k]         time to move from line 2 AFTER station k to line 1 BEFORE station k+1   (length n-1)
  e1, e2        entry time to line 1 / 2        x1, x2   exit time from line 1 / 2

DP state:  f[l][k] = minimum time from entry until station k has been completed ON line l.
  f[1][0] = e1 + a1[0]                       f[2][0] = e2 + a2[0]
  f[1][k] = a1[k] + min( f[1][k-1]            (stay),
                         f[2][k-1] + t2[k-1]  (transfer from line 2) )
  f[2][k] = a2[k] + min( f[2][k-1]            (stay),
                         f[1][k-1] + t1[k-1]  (transfer from line 1) )
  answer  = min( f[1][n-1] + x1 , f[2][n-1] + x2 )
Predecessor tables from[l][k] store which line the product came from -> route reconstruction.
Tie-break: staying on the current line wins ties (a transfer must be STRICTLY better).
"""

from itertools import product

PREDICTIONS_43 = [
    "The optimal route WILL change (the expensive transfer is currently used by the optimal route).",
    "Most affected decision: reaching Line 2 at station 4 by transferring from Line 1 (after station 3).",
    "The total production time WILL increase (the old optimum is no longer attainable).",
]
PREDICTIONS_44 = [
    "The route WILL change: production avoids the slow Line-2 station 4 and stays on Line 1 at that station.",
    "The change occurs at station 4 (the slowed station).",
    "Total time will increase, but by clearly LESS than the +11 delay, because the alternative line absorbs most of it.",
]


def validate(a1, a2, t1, t2):
    n = len(a1)
    if n == 0 or len(a2) != n:
        raise ValueError("both lines need the same, non-zero number of stations")
    if len(t1) != n - 1 or len(t2) != n - 1:
        raise ValueError("transfer lists must have n-1 entries")
    if min(a1 + a2 + t1 + t2) < 0:
        raise ValueError("times cannot be negative")


def assembly_line_dp(a1, a2, t1, t2, e1, e2, x1, x2):
    """Return dict with total, route [(station, line)], tables f/from and per-station decision trace."""
    validate(a1, a2, t1, t2)
    n = len(a1)
    f = {1: [0] * n, 2: [0] * n}
    came = {1: [None] * n, 2: [None] * n}
    trace = []
    f[1][0], f[2][0] = e1 + a1[0], e2 + a2[0]
    for k in range(1, n):
        l1_stay, l1_move = f[1][k - 1] + a1[k], f[2][k - 1] + t2[k - 1] + a1[k]
        l2_stay, l2_move = f[2][k - 1] + a2[k], f[1][k - 1] + t1[k - 1] + a2[k]
        pick1 = "Stay" if l1_stay <= l1_move else "Transfer"
        pick2 = "Stay" if l2_stay <= l2_move else "Transfer"
        f[1][k], came[1][k] = min(l1_stay, l1_move), 1 if pick1 == "Stay" else 2
        f[2][k], came[2][k] = min(l2_stay, l2_move), 2 if pick2 == "Stay" else 1
        trace.append((k + 1, l1_stay, l1_move, pick1, f[1][k], l2_stay, l2_move, pick2, f[2][k]))
    finish1, finish2 = f[1][n - 1] + x1, f[2][n - 1] + x2
    last_line = 1 if finish1 <= finish2 else 2
    total = min(finish1, finish2)
    route, line = [], last_line
    for k in range(n - 1, -1, -1):
        route.append((k + 1, line))
        if k:
            line = came[line][k]
    route.reverse()
    return {"total": total, "route": route, "f": f, "came": came, "trace": trace,
            "finish": (finish1, finish2)}


def brute_force(a1, a2, t1, t2, e1, e2, x1, x2):
    """Independent check: try every one of the 2^n line assignments."""
    n, best = len(a1), float("inf")
    a = {1: a1, 2: a2}
    for choice in product((1, 2), repeat=n):
        cost = (e1 if choice[0] == 1 else e2) + sum(a[choice[k]][k] for k in range(n))
        for k in range(n - 1):
            if choice[k] != choice[k + 1]:
                cost += t1[k] if choice[k] == 1 else t2[k]
        cost += x1 if choice[-1] == 1 else x2
        best = min(best, cost)
    return best


def transfers_of(route):
    return [(k1, l1, l2) for (k1, l1), (_, l2) in zip(route, route[1:]) if l1 != l2]


def print_result(title, data, e1, e2, x1, x2):
    print(f"--- {title} ---")
    print("Entry")
    prev_line = None
    for station, line in data["route"]:
        if prev_line is None:
            print(f" |  (entry time {e1 if line == 1 else e2})")
        elif prev_line != line:
            print(f" |  Transfer Line {prev_line} -> Line {line}")
        else:
            print(" |")
        print(f"Line {line} - Station {station}")
        prev_line = line
    print(f" |  (exit time {x1 if prev_line == 1 else x2})")
    print("Exit")
    print("Line chosen per station :", " ".join(f"S{s}:L{l}" for s, l in data["route"]))
    tp = transfers_of(data["route"])
    print("Transfer points         :", ", ".join(f"after station {s} (Line {a}->Line {b})" for s, a, b in tp) or "none")
    print(f"Minimum Production Time = {data['total']}")


def print_trace(data, e1, e2, a1, a2):
    f = data["f"]
    print(f"Station 1 initialisation: f1 = e1 + a1[1] = {f[1][0]}, f2 = e2 + a2[1] = {f[2][0]}")
    head = (f"{'Stn':>3} | {'L1 by Staying':>13}{'L1 by Transfer':>15}{'Selected':>10}{'f1':>5} | "
            f"{'L2 by Staying':>13}{'L2 by Transfer':>15}{'Selected':>10}{'f2':>5}")
    print(head)
    for st, s1, m1, p1, v1, s2, m2, p2, v2 in data["trace"]:
        print(f"{st:>3} | {s1:>13}{m1:>15}{p1:>10}{v1:>5} | {s2:>13}{m2:>15}{p2:>10}{v2:>5}")
    print(f"Exit: f1+x1 = {data['finish'][0]}, f2+x2 = {data['finish'][1]}  -> minimum = {data['total']}")


def main():
    a1 = [7, 9, 3, 4, 8, 4]
    a2 = [8, 5, 6, 4, 5, 7]
    t1 = [2, 3, 1, 3, 4]
    t2 = [2, 1, 2, 2, 1]
    e1, e2, x1, x2 = 2, 4, 3, 6
    print("=" * 100)
    print("TASK 4.1  OPTIMISATION ENGINE")
    print("Line 1 processing :", a1)
    print("Line 2 processing :", a2)
    print("Transfer L1->L2 after station k:", t1)
    print("Transfer L2->L1 after station k:", t2)
    print(f"Entry times e1={e1}, e2={e2}; exit times x1={x1}, x2={x2}")
    base = assembly_line_dp(a1, a2, t1, t2, e1, e2, x1, x2)
    print_result("Baseline optimum", base, e1, e2, x1, x2)
    ref = brute_force(a1, a2, t1, t2, e1, e2, x1, x2)
    print(f"Brute force over all 2^{len(a1)} = {2 ** len(a1)} line assignments gives {ref}  -> {'MATCH' if ref == base['total'] else 'MISMATCH'}")

    print("\n" + "=" * 100)
    print("TASK 4.2  DP DECISIONS PER STATION")
    print_trace(base, e1, e2, a1, a2)

    print("\n" + "=" * 100)
    print("TASK 4.3  PREDICT BEFORE YOU EXECUTE - transfer L1->L2 after station 3 increased from 1 to 20")
    for p in PREDICTIONS_43:
        print("PREDICTION (recorded before running):", p)
    t1_mod = t1[:]
    t1_mod[2] = 20
    mod = assembly_line_dp(a1, a2, t1_mod, t2, e1, e2, x1, x2)
    print_result("Modified run", mod, e1, e2, x1, x2)
    print_trace(mod, e1, e2, a1, a2)
    print(f"ACTUAL: route changed = {mod['route'] != base['route']}; total {base['total']} -> {mod['total']}; "
          f"brute force check = {brute_force(a1, a2, t1_mod, t2, e1, e2, x1, x2)}")

    print("\n" + "=" * 100)
    print("TASK 4.4  PRODUCTION DISRUPTION - Line 2 station 4 slows from 4 to 15")
    for p in PREDICTIONS_44:
        print("PREDICTION (recorded before running):", p)
    a2_slow = a2[:]
    a2_slow[3] = 15
    dis = assembly_line_dp(a1, a2_slow, t1, t2, e1, e2, x1, x2)
    print_result("Disrupted run", dis, e1, e2, x1, x2)
    print_trace(dis, e1, e2, a1, a2_slow)
    first_change = next((s for (s, l), (_, l0) in zip(dis["route"], base["route"]) if l != l0), None)
    print(f"ACTUAL: route changed = {dis['route'] != base['route']}; first station whose line changed = {first_change}; "
          f"total {base['total']} -> {dis['total']} (+{dis['total'] - base['total']}); "
          f"brute force check = {brute_force(a1, a2_slow, t1, t2, e1, e2, x1, x2)}")
    print("Check - cost of keeping the OLD route under the disruption:",
          sum(({1: a1, 2: a2_slow}[l][s - 1]) for s, l in base["route"])
          + (e1 if base["route"][0][1] == 1 else e2)
          + sum((t1 if a == 1 else t2)[s - 1] for s, a, b in transfers_of(base["route"]))
          + (x1 if base["route"][-1][1] == 1 else x2))

    print("\n" + "=" * 100)
    print("BOUNDARY / FAILURE TESTS")
    one = assembly_line_dp([5], [3], [], [], 1, 1, 1, 1)
    print("n = 1 station:", one["route"], "total", one["total"], "(expected Line 2: 1+3+1 = 5)")
    tie = assembly_line_dp([2, 2], [2, 2], [0], [0], 0, 0, 0, 0)
    print("All-equal tie case route (Stay preferred):", tie["route"], "total", tie["total"])
    free = assembly_line_dp([1, 100], [100, 1], [0], [0], 0, 0, 0, 0)
    print("Free transfers, opposite fast lines:", free["route"], "total", free["total"], "(expected 2)")
    try:
        assembly_line_dp([1, 2], [1], [1], [1], 0, 0, 0, 0)
    except ValueError as err:
        print("Invalid input rejected:", err)
    import random
    rng, bad = random.Random(5), 0
    for _ in range(500):
        n = rng.randint(1, 9)
        args = ([rng.randint(1, 9) for _ in range(n)], [rng.randint(1, 9) for _ in range(n)],
                [rng.randint(0, 6) for _ in range(n - 1)], [rng.randint(0, 6) for _ in range(n - 1)],
                rng.randint(0, 5), rng.randint(0, 5), rng.randint(0, 5), rng.randint(0, 5))
        bad += assembly_line_dp(*args)["total"] != brute_force(*args)
    print("Random regression: DP vs brute force on 500 instances, mismatches =", bad)


if __name__ == "__main__":
    main()
