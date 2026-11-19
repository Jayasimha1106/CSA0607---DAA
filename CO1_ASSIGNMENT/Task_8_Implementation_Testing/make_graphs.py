"""Generate graphs and markdown tables from results.csv. Run after run_benchmark.py."""
import csv, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(ROOT, 'Report', 'Tables_and_Graphs')
rows = list(csv.DictReader(open(os.path.join(ROOT, 'Task_9_Experimental_Performance', 'results.csv'))))
f = lambda k: [float(r[k]) for r in rows]
n = f('n')

# 1. comparisons vs n
plt.figure(figsize=(6, 4))
plt.loglog(n, f('linear_avg_comps'), 'o-', label='Linear (measured)')
plt.loglog(n, f('binary_avg_comps'), 's-', label='Binary (measured)')
plt.loglog(n, f('hash_avg_comps'), '^-', label='Hash (measured)')
plt.loglog(n, [math.log2(x) for x in n], 'k--', lw=0.8, label='log2 n (theory)')
plt.xlabel('n (records)'); plt.ylabel('avg comparisons per search'); plt.title('Comparisons vs n')
plt.legend(); plt.grid(True, which='both', alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, 'graph1_comparisons.png'), dpi=150); plt.close()

# 2. search time vs n
plt.figure(figsize=(6, 4))
plt.loglog(n, f('linear_sec_per_search'), 'o-', label='Linear')
plt.loglog(n, f('binary_sec_per_search'), 's-', label='Binary')
plt.loglog(n, f('hash_sec_per_search'), '^-', label='Hash')
plt.xlabel('n (records)'); plt.ylabel('seconds per search'); plt.title('Search time vs n')
plt.legend(); plt.grid(True, which='both', alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, 'graph2_search_time.png'), dpi=150); plt.close()

# 3. preprocessing
plt.figure(figsize=(6, 4))
plt.loglog(n, f('sort_sec'), 's-', label='Merge sort (for binary)')
plt.loglog(n, f('hash_build_sec'), '^-', label='Hash table build')
plt.xlabel('n (records)'); plt.ylabel('seconds'); plt.title('Preprocessing time vs n')
plt.legend(); plt.grid(True, which='both', alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, 'graph3_preprocessing.png'), dpi=150); plt.close()

# 4. total time for q searches at n = 1,000,000 (preprocessing included)
r = rows[-1]
qs = [10 ** i for i in range(0, 8)]
tot = lambda pre, per: [pre + q * per for q in qs]
plt.figure(figsize=(6, 4))
plt.loglog(qs, tot(0, float(r['linear_sec_per_search'])), 'o-', label='Linear')
plt.loglog(qs, tot(float(r['sort_sec']), float(r['binary_sec_per_search'])), 's-', label='Sort + binary')
plt.loglog(qs, tot(float(r['hash_build_sec']), float(r['hash_sec_per_search'])), '^-', label='Hash build + search')
plt.xlabel('number of searches q'); plt.ylabel('total seconds'); plt.title('Total cost incl. preprocessing, n = 1,000,000')
plt.legend(); plt.grid(True, which='both', alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, 'graph4_total_cost_n1M.png'), dpi=150); plt.close()

# Markdown tables
with open(os.path.join(OUT, 'results_tables.md'), 'w') as t:
    t.write('| n | Linear avg comps | Binary avg comps | Hash avg comps | Load factor |\n|---|---|---|---|---|\n')
    for x in rows:
        t.write(f"| {int(float(x['n'])):,} | {float(x['linear_avg_comps']):,.1f} | {float(x['binary_avg_comps']):.2f} | {float(x['hash_avg_comps']):.3f} | {float(x['load_factor']):.4f} |\n")
    t.write('\n| n | Linear (s/search) | Binary (s/search) | Hash (s/search) | Sort (s) | Hash build (s) |\n|---|---|---|---|---|---|\n')
    for x in rows:
        t.write(f"| {int(float(x['n'])):,} | {float(x['linear_sec_per_search']):.3e} | {float(x['binary_sec_per_search']):.3e} | {float(x['hash_sec_per_search']):.3e} | {float(x['sort_sec']):.4f} | {float(x['hash_build_sec']):.4f} |\n")

# Break-even + Day-4 numbers
la, bs, hs = float(r['linear_sec_per_search']), float(r['binary_sec_per_search']), float(r['hash_sec_per_search'])
so, hb = float(r['sort_sec']), float(r['hash_build_sec'])
daily = 50000 * 24
with open(os.path.join(OUT, 'day4_numbers.md'), 'w') as t:
    t.write(f'- Break-even vs linear (n=1e6): sort+binary after {so/(la-bs):.0f} searches; hash after {hb/(la-hs):.0f} searches\n')
    t.write(f'- Searches per day at 50,000/h: {daily:,}; per second: {50000/3600:.1f}\n')
    t.write(f'- Daily search CPU time: linear {daily*la:,.0f} s ({daily*la/3600:.1f} h); binary {daily*bs:.2f} s (+{so:.2f} s sort); hash {daily*hs:.2f} s (+{hb:.2f} s build)\n')
    t.write(f'- Linear CPU utilisation at 13.9 req/s: {50000/3600*la*100:.0f}% of one core; binary {50000/3600*bs*100:.4f}%; hash {50000/3600*hs*100:.4f}%\n')
print(open(os.path.join(OUT, 'day4_numbers.md')).read())
