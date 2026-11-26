from math import comb
from set_cover import exact_cover, greedy_cover, random_instance

def fmt(sol): return "-" if sol is None else "{" + ",".join(f"S{i+1}" for i in sol) + "}"

print("=== B3.1 Correctness on small instances (3 random + 1 hand-made, not cherry-picked) ===")
print(f"{'Inst':5}{'Zones':>6}{'Centres':>8}{'Exact':>7}{'Greedy':>8}{'Same?':>7}   Exact set / Greedy set")
insts = [("1", 10, random_instance(10, 8, 11)), ("2", 12, random_instance(12, 10, 22)),
         ("3", 14, random_instance(14, 12, 33)), ("4", 15, random_instance(15, 12, 7, 0.2)),
         ("5", 16, random_instance(16, 12, 8, 0.2))]
for name, n, cs in insts:
    e, _ = exact_cover(n, cs); g, _ = greedy_cover(n, cs)
    print(f"{name:5}{n:>6}{len(cs):>8}{len(e):>7}{len(g):>8}{'Yes' if len(e)==len(g) else 'NO':>7}   {fmt(e)} / {fmt(g)}")

print("\n=== B3.2 Counterexample ===")
U = 6
cs = [{0,1,2,3}, {0,1,4}, {2,3,5}, {4}, {5}]   # S1..S5 ; zones Z1..Z6 = 0..5
e, ee = exact_cover(U, cs); g, ge = greedy_cover(U, cs)
print("Zones Z1..Z6; S1={Z1,Z2,Z3,Z4} S2={Z1,Z2,Z5} S3={Z3,Z4,Z6} S4={Z5} S5={Z6}")
print("Exact :", fmt(e), "size", len(e), " Greedy:", fmt(g), "size", len(g))
unc = set(range(U))
for step, i in enumerate(g, 1):
    gains = [len(c & unc) for c in cs]
    print(f"  greedy step {step}: uncovered={sorted(z+1 for z in unc)} gains={gains} -> pick S{i+1}")
    unc -= cs[i]
assert len(g) > len(e)

print("\n=== B3.3 Scaling (random instances, density 0.12, seed 5) ===")
print(f"{'Zones':>6}{'Centres':>8}{'ExactCombos':>13}{'Worst 2^k':>11}{'GreedyEvals':>13}{'Exact':>7}{'Greedy':>8}")
for n, k in [(10, 8), (20, 12), (30, 16), (40, 20), (50, 24), (60, 26)]:
    cs = random_instance(n, k, 5, 0.12)
    e, ee = exact_cover(n, cs); g, ge = greedy_cover(n, cs)
    print(f"{n:>6}{k:>8}{ee:>13}{2**k:>11}{ge:>13}{len(e):>7}{len(g):>8}")
