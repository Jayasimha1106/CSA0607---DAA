"""SentinelOps SOC alert-triage module -- CORRECTED version.

Only the nine defects (D1-D9) were fixed; the structure of the original
brute-force code is kept.  Two boundary guards (not counted as defects) were
added: an empty pattern returns [] and fewer than two logins returns (None, None).
"""
import math


def sort_alerts(alerts):  # insertion sort by severity, highest first (stable)
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j >= 0 and alerts[j][1] < key[1]:      # D1: was  j > 0
            alerts[j + 1] = alerts[j]
            j -= 1
        alerts[j + 1] = key                           # D2: was  alerts[j] = key
    return alerts


def is_blocked(blocklist, ip):  # sequential search
    for i in range(len(blocklist)):
        if blocklist[i] == ip:
            return True                               # D3: was  return False
    return False                                      # D4: 'else: return False' inside the loop removed


def find_signature(log, pattern):  # brute-force string matching, all occurrences
    n, m = len(log), len(pattern)
    if m == 0:                                        # boundary guard
        return []
    hits = []
    for i in range(n - m + 1):                        # D5: was  range(n - m)
        for j in range(m):
            if log[i + j] != pattern[j]:
                break
        else:                                         # D6: was  'if j == m - 1' (true after a last-char mismatch)
            hits.append(i)
    return hits


def closest_logins(events):  # brute-force closest pair of login locations
    if len(events) < 2:                               # boundary guard
        return None, None
    min_dist = float("inf")                           # D7: was  0
    pair = None
    for i in range(len(events)):
        for j in range(i + 1, len(events)):           # D9: was  range(len(events))  (self + repeated pairs)
            d = math.sqrt((events[i][0] - events[j][0]) ** 2 +
                          (events[i][1] - events[j][1]) ** 2)
            if d < min_dist:                          # D8: was  d > min_dist
                min_dist = d
                pair = (i, j)
    return pair, min_dist
