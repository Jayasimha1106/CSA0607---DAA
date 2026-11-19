"""Three search strategies for a student registration-number database.

A: Linear search      (iterative, brute force, no preprocessing)
B: Binary search      (recursive, decrease-and-conquer, merge-sort preprocessing)
C: Hash table         (division hashing + separate chaining, build preprocessing)
Every routine counts key comparisons (the basic operation).
"""
import sys
sys.setrecursionlimit(10000)


# ---------- A: Linear search (iterative) ----------
def linear_search(arr, key):
    comps = 0
    for i, v in enumerate(arr):
        comps += 1
        if v == key:
            return i, comps
    return -1, comps


# ---------- B: Binary search (recursive) + merge sort preprocessing ----------
def binary_search(arr, key, low, high, counter):
    if low > high:                      # base case: empty range
        return -1
    mid = (low + high) // 2
    counter[0] += 1                     # one three-way comparison
    if arr[mid] == key:
        return mid
    if key < arr[mid]:
        return binary_search(arr, key, low, mid - 1, counter)
    return binary_search(arr, key, mid + 1, high, counter)


def merge_sort(a, counter):
    if len(a) <= 1:
        return a
    m = len(a) // 2
    left, right = merge_sort(a[:m], counter), merge_sort(a[m:], counter)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


# ---------- C: Hash table with separate chaining ----------
def next_prime(n):
    def is_prime(x):
        if x < 2:
            return False
        i = 2
        while i * i <= x:
            if x % i == 0:
                return False
            i += 1
        return True
    while not is_prime(n):
        n += 1
    return n


class HashTable:
    def __init__(self, keys, m=None):
        self.m = m or next_prime(max(len(keys), 2))
        self.table = [[] for _ in range(self.m)]
        for k in keys:
            self.table[k % self.m].append(k)

    def search(self, key):
        comps = 0
        for v in self.table[key % self.m]:
            comps += 1
            if v == key:
                return True, comps
        return False, comps
