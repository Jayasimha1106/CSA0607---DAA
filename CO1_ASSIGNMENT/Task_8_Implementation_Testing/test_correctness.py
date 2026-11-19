"""Edge-case and correctness tests. Run: python test_correctness.py"""
import random
from search_algorithms import *


def all_three(data, key):
    a = linear_search(data, key)[0] != -1
    srt = merge_sort(list(data), [0])
    b = binary_search(srt, key, 0, len(srt) - 1, [0]) != -1
    c = HashTable(data).search(key)[0] if data else False
    return a, b, c


def check(name, data, key, expected):
    got = all_three(data, key)
    assert got == (expected,) * 3, f'FAIL {name}: {got}'
    print(f'PASS  {name}')


check('empty database', [], 5, False)
check('single record, present', [7], 7, True)
check('single record, absent', [7], 8, False)
data = random.Random(1).sample(range(10_000, 99_999), 1000)
check('first element (linear best case)', data, data[0], True)
check('last element (linear worst case)', data, data[-1], True)
srt = sorted(data)
check('middle element (binary best case)', data, srt[(len(srt) - 1) // 2], True)
check('absent key below range', data, 1, False)
check('absent key above range', data, 10**9, False)
check('random present key', data, data[537], True)

# bulk randomized agreement with Python set membership
rnd = random.Random(2)
for n in (1, 2, 3, 10, 100, 1000):
    d = rnd.sample(range(1, 10**6), n)
    s = set(d); srt = merge_sort(list(d), [0]); ht = HashTable(d)
    for _ in range(300):
        k = rnd.choice(d) if rnd.random() < 0.5 else rnd.randint(1, 10**6)
        e = k in s
        assert (linear_search(d, k)[0] != -1) == e
        assert (binary_search(srt, k, 0, n - 1, [0]) != -1) == e
        assert ht.search(k)[0] == e
    print(f'PASS  randomized agreement, n={n}')
print('ALL TESTS PASSED')
