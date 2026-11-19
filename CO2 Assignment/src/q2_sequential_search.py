"""Q2 - Sequential search experiments: aircraft tool tracking."""
import random, time, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def sequential_search(records, tool_id):
    comparisons = 0
    for i, r in enumerate(records):
        comparisons += 1
        if r[0] == tool_id:
            return i, comparisons
    return -1, comparisons

def make_records(n):
    ids = random.sample(range(1, 10 * n + 1), n)
    return [(f"T-{t}", f"TECH-{random.randint(1, 500)}", f"{random.randint(0,23):02d}:{random.randint(0,59):02d}", f"BAY-{random.randint(1, 12)}") for t in ids]

random.seed(7)
sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
rows = []
print("PART A: comparisons for successful (first / middle / last / random-avg) and unsuccessful search")
print(f"{'n':>8}{'first':>8}{'middle':>9}{'last':>9}{'avg(1000 rnd)':>15}{'miss':>9}{'theory avg (n+1)/2':>20}")
for n in sizes:
    rec = make_records(n)
    first = sequential_search(rec, rec[0][0])[1]
    mid = sequential_search(rec, rec[n // 2][0])[1]
    last = sequential_search(rec, rec[-1][0])[1]
    avg = sum(sequential_search(rec, random.choice(rec)[0])[1] for _ in range(1000)) / 1000
    miss = sequential_search(rec, "T-NOT-ISSUED")[1]
    rows.append([n, first, mid, last, round(avg, 1), miss])
    print(f"{n:8d}{first:8d}{mid:9d}{last:9d}{avg:15.1f}{miss:9d}{(n+1)/2:20.1f}")

# Time per lookup and operating boundary
print("\nPART B: measured time per sequential lookup (worst case = unsuccessful), Python")
tt = []
for n in sizes:
    rec = make_records(n)
    t = time.perf_counter()
    for _ in range(20): sequential_search(rec, "T-NOT-ISSUED")
    ms = (time.perf_counter() - t) / 20 * 1000
    tt.append(ms); print(f"n={n:7d}  {ms:9.4f} ms per search")

# Frequency analysis: sequential scan vs. hash index
print("\nPART C: total comparison-equivalents per day (avg successful search = n/2 comparisons)")
print("Hash index cost model: 1 probe per lookup + 1 update per issue/return (assume 2 updates per active record per day).")
print(f"{'scenario':38s}{'n':>8}{'searches/day':>14}{'sequential':>14}{'hash index':>12}")
sc = [("1 hangar, low load", 200, 100), ("1 hangar, busy", 200, 2000),
      ("20 facilities (central list)", 4000, 40000), ("20 facilities, peak", 4000, 400000)]
for name, n, q in sc:
    seq = q * n / 2; hsh = q * 1 + 2 * n
    print(f"{name:38s}{n:8d}{q:14d}{seq:14.0f}{hsh:12.0f}")

with open("../results/q2_raw.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["n", "first", "middle", "last", "avg_random", "unsuccessful"]); w.writerows(rows)

plt.figure(figsize=(7, 5))
plt.plot(sizes, [r[2] for r in rows], "o-", label="middle position")
plt.plot(sizes, [r[3] for r in rows], "s-", label="last position")
plt.plot(sizes, [r[4] for r in rows], "^--", label="average (random)")
plt.plot(sizes, [r[5] for r in rows], "x-", label="unsuccessful")
plt.xscale("log"); plt.yscale("log"); plt.xlabel("list size n"); plt.ylabel("comparisons"); plt.legend(); plt.grid(alpha=.3)
plt.title("Q2: Sequential search comparisons vs n"); plt.tight_layout(); plt.savefig("../graphs/q2_sequential.png", dpi=130)
