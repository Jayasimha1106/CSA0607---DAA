"""Q1 - Selection / Bubble / Insertion sort under different data conditions."""
import random, time, csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def selection_sort(a):
    a = a[:]; c = s = 0; n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            c += 1
            if a[j] < a[m]: m = j
        if m != i:
            a[i], a[m] = a[m], a[i]; s += 1
    return a, c, s

def bubble_sort(a):                      # with early-exit flag
    a = a[:]; c = s = 0; n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            c += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]; s += 1; swapped = True
        if not swapped: break
    return a, c, s

def insertion_sort(a):                   # s counts element shifts/movements
    a = a[:]; c = s = 0
    for i in range(1, len(a)):
        v = a[i]; j = i - 1
        while j >= 0:
            c += 1
            if a[j] > v:
                a[j + 1] = a[j]; s += 1; j -= 1
            else: break
        a[j + 1] = v
    return a, c, s

N = 1000
random.seed(42)
base = list(range(1, N + 1))

def nearly_sorted_appended(frac_new=0.05):      # 95% sorted + small batch of NEW orders appended
    k = int(N * frac_new)
    old = sorted(random.sample(range(1, 10 * N), N - k))
    new = random.sample(range(1, 10 * N), k)
    return old + new

def nearly_sorted_scattered(frac=0.05):         # ~5% of positions disturbed by random swaps
    a = base[:]
    for _ in range(int(N * frac / 2)):
        i, j = random.randrange(N), random.randrange(N); a[i], a[j] = a[j], a[i]
    return a

datasets = {
    "D1 Random":                 random.sample(range(1, 10 * N), N),
    "D2 Already sorted":         base[:],
    "D3 Reverse sorted":         base[::-1],
    "D4 95% sorted + new batch": nearly_sorted_appended(),
    "D5 95% sorted scattered":   nearly_sorted_scattered(),
    "D6 Edge: all equal scores": [500] * N,
    "D7 Edge: min value at end": base[1:] + [0],
}
algs = {"Selection": selection_sort, "Bubble": bubble_sort, "Insertion": insertion_sort}

rows = []
print(f"n = {N}")
print(f"{'Dataset':28s}{'Algorithm':11s}{'Comparisons':>12s}{'Swaps/Moves':>13s}{'Time(ms)':>10s}")
for dn, data in datasets.items():
    for an, f in algs.items():
        t = time.perf_counter(); out, c, s = f(data); t = (time.perf_counter() - t) * 1000
        assert out == sorted(data)
        rows.append([dn, an, c, s, round(t, 3)])
        print(f"{dn:28s}{an:11s}{c:12d}{s:13d}{t:10.3f}")
    print()
print("Theory for n=%d: n(n-1)/2 = %d ; n-1 = %d" % (N, N*(N-1)//2, N-1))

with open("../results/q1_raw.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["dataset", "algorithm", "comparisons", "swaps_moves", "time_ms"]); w.writerows(rows)

names = list(datasets); x = range(len(names)); wd = 0.27
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
for k, an in enumerate(algs):
    ax[0].bar([i + k * wd for i in x], [r[2] for r in rows if r[1] == an], wd, label=an)
    ax[1].bar([i + k * wd for i in x], [r[3] for r in rows if r[1] == an], wd, label=an)
for a_, t in zip(ax, ["Comparisons", "Swaps / Movements"]):
    a_.set_xticks([i + wd for i in x]); a_.set_xticklabels([n.split(" ")[0] for n in names]); a_.set_title(t + f" (n={N}, symlog scale)"); a_.legend(); a_.set_yscale("symlog")
plt.tight_layout(); plt.savefig("../graphs/q1_sorting.png", dpi=130)
