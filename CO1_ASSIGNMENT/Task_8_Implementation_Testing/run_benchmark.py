"""Benchmark all three algorithms. Run: python run_benchmark.py
Writes ../Task_9_Experimental_Performance/results.csv"""
import os, random, time
from search_algorithms import *

SIZES = (1_000, 10_000, 100_000, 1_000_000)
QUERIES = 200            # half present, half absent (same queries for all algorithms)
DATA_SEED, QUERY_SEED = 42, 7
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'Task_9_Experimental_Performance', 'results.csv')


def make_data(n):
    return random.Random(DATA_SEED).sample(range(10_000_000, 99_999_999), n)


def run(n):
    data = make_data(n)
    rnd = random.Random(QUERY_SEED)
    tests = [rnd.choice(data) for _ in range(QUERIES // 2)] + \
            [rnd.randint(100_000_000, 110_000_000) for _ in range(QUERIES // 2)]
    q = len(tests)

    t0 = time.perf_counter(); ca = 0
    for k in tests:
        ca += linear_search(data, k)[1]
    ta = time.perf_counter() - t0

    cs = [0]; t0 = time.perf_counter()
    srt = merge_sort(data, cs)
    tsort = time.perf_counter() - t0
    cb = [0]; t0 = time.perf_counter()
    for k in tests:
        binary_search(srt, k, 0, n - 1, cb)
    tb = time.perf_counter() - t0

    t0 = time.perf_counter(); ht = HashTable(data)
    tbuild = time.perf_counter() - t0
    cc = 0; t0 = time.perf_counter()
    for k in tests:
        cc += ht.search(k)[1]
    tc = time.perf_counter() - t0

    s = set(data)                       # correctness check on every query
    for k in tests:
        e = k in s
        assert (linear_search(data, k)[0] != -1) == e
        assert (binary_search(srt, k, 0, n - 1, [0]) != -1) == e
        assert ht.search(k)[0] == e

    return [n, q, ta / q, ca / q, tsort, cs[0], tb / q, cb[0] / q,
            tbuild, tc / q, cc / q, n / ht.m]


if __name__ == '__main__':
    hdr = ['n', 'queries', 'linear_sec_per_search', 'linear_avg_comps', 'sort_sec', 'sort_comps',
           'binary_sec_per_search', 'binary_avg_comps', 'hash_build_sec',
           'hash_sec_per_search', 'hash_avg_comps', 'load_factor']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(','.join(hdr) + '\n')
        for n in SIZES:
            row = run(n)
            f.write(','.join(f'{x:.9g}' if isinstance(x, float) else str(x) for x in row) + '\n')
            print('done n =', n, flush=True)
    print('wrote', os.path.abspath(OUT))
