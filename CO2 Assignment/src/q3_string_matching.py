"""Q3 - Brute-force string matching: engineering best / worst / extra cases."""
import random, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def brute_force_match(text, pat, find_all=True):
    n, m = len(text), len(pat); comps = 0; hits = []
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comps += 1
            if text[i + j] != pat[j]: break
            j += 1
        if j == m:
            hits.append(i)
            if not find_all: break
    return hits, comps

random.seed(3)
n, m = 10000, 10
random_log = "".join(random.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(n))
tests = [
    ("T1 BEST: first char never matches", "A" * n, "B" + "A" * (m - 1), "n-m+1 = %d" % (n - m + 1)),
    ("T2 WORST: a^n vs a^(m-1)b",          "A" * n, "A" * (m - 1) + "B", "(n-m+1)*m = %d" % ((n - m + 1) * m)),
    ("T3 EXTRA: random log text",           random_log, "root", "~ n*1.04 (26-27 symbols)"),
    ("T4 EXTRA: pattern found at index 0 (stop at first)", "A" * n, "A" * m, "m = %d" % m),
    ("T5 EXTRA: mismatch near start of pattern vs end", ("AB" * (n // 2)), "ABABABABAC", "partial repeats"),
]
print(f"n = {n} (text length), m = {m} (pattern length)\n")
rows = []
for name, t, p, pred in tests:
    first_only = name.startswith("T4")
    hits, c = brute_force_match(t, p, find_all=not first_only)
    rows.append([name, len(t), len(p), c, len(hits)])
    print(f"{name}\n   predicted: {pred}\n   observed comparisons = {c}, matches = {len(hits)}\n")

print("Effect of pattern length on worst case (text = A^10000, pattern = A^(m-1) B):")
print(f"{'m':>5}{'comparisons':>14}{'(n-m+1)*m':>14}")
ms = [2, 5, 10, 20, 50, 100]; wc = []
for mm in ms:
    _, c = brute_force_match("A" * n, "A" * (mm - 1) + "B"); wc.append(c)
    print(f"{mm:5d}{c:14d}{(n-mm+1)*mm:14d}")

with open("../results/q3_raw.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["test", "n", "m", "comparisons", "matches"]); w.writerows(rows)

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].bar([r[0].split(" ")[0] for r in rows], [r[3] for r in rows], color="tab:blue"); ax[0].set_yscale("log")
ax[0].set_title("Character comparisons per test (n=10000, m=10)")
ax[1].plot(ms, wc, "o-"); ax[1].set_xlabel("pattern length m"); ax[1].set_ylabel("comparisons"); ax[1].set_title("Worst case grows with m (n fixed)"); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("../graphs/q3_string.png", dpi=130)
