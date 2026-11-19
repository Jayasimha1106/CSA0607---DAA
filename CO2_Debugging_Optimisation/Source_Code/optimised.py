"""SentinelOps SOC alert-triage module -- CORRECTED and OPTIMISED version.

Public API (same names and return values as the corrected module):
    sort_alerts(alerts)            sort by severity, highest first, stable
    sort_alerts_insertion(alerts)  corrected insertion sort (kept for comparison)
    build_blocklist(ips)           one-off O(b) preparation of a blocklist
    is_blocked(blocklist, ip)      membership test (O(1) on a prepared blocklist)
    find_signature(log, pattern)   all start positions of pattern in log
    closest_logins(events)         closest pair of (x, y) login locations

Every function accepts an optional ``stats`` dict that receives operation
counts, so the measured code is exactly the shipped code.
"""
import math


def sort_alerts_insertion(alerts, stats=None):
    """Stable insertion sort on severity (index 1), highest first, in place.

    Theta(n + I) where I is the number of inversions, so it is excellent on
    nearly sorted input but Theta(n^2) on random input.
    """
    comparisons = 0
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if alerts[j][1] < key[1]:       # strict '<' keeps equal severities in arrival order
                alerts[j + 1] = alerts[j]
                j -= 1
            else:
                break
        alerts[j + 1] = key
    if stats is not None:
        stats["comparisons"] = comparisons
    return alerts


def sort_alerts(alerts):
    """Sort alerts in place by severity, highest first; equal severities keep
    arrival order.

    Uses Timsort (list.sort): stable, O(n) on already/nearly sorted data and
    O(n log n) worst case.  ``reverse=True`` preserves stability.
    """
    alerts.sort(key=lambda a: a[1], reverse=True)
    return alerts


def build_blocklist(ips):
    """Turn a list of blocked IPs into a hash set (O(b), done once)."""
    return frozenset(ips)


def is_blocked(blocklist, ip):
    """Return True if ``ip`` is on the blocklist.

    A prepared blocklist (set/frozenset from build_blocklist) gives O(1)
    average look-ups.  A plain list falls back to sequential search, O(b).
    """
    if isinstance(blocklist, (set, frozenset)):
        return ip in blocklist
    for entry in blocklist:                  # sequential search
        if entry == ip:
            return True
    return False


def find_signature(log, pattern, stats=None):
    """Return every start index where ``pattern`` occurs in ``log`` (overlaps
    included).  An empty pattern, or a pattern longer than the log, gives [].

    Brute force with an early exit: every character comparison either extends
    the current match or ends this alignment, so none is wasted.  Only the
    n - m + 1 feasible alignments are tried.
    """
    n, m = len(log), len(pattern)
    if m == 0 or m > n:
        return []
    hits = []
    comparisons = 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if log[i + j] != pattern[j]:
                break                        # mismatch: abandon this alignment at once
            j += 1
        if j == m:                           # reached only after m successful matches
            hits.append(i)
    if stats is not None:
        stats["comparisons"] = comparisons
    return hits


def closest_logins(events, stats=None):
    """Closest pair of login locations; returns ((i, j), distance) with i < j.

    Optimisations over plain brute force:
      * each unordered pair is examined once (no self / repeated pairs);
      * squared distances are compared, a single sqrt is taken at the end;
      * events are visited in order of x; once the x-gap alone exceeds the
        best distance found so far, no later point can be closer, so the
        inner loop stops (pruning).
    Ties are resolved to the lexicographically smallest (i, j), exactly like
    the corrected brute-force version.  Fewer than two events -> (None, None).
    """
    n = len(events)
    if n < 2:
        return None, None
    order = sorted(range(n), key=lambda k: events[k][0])
    best = float("inf")                      # best SQUARED distance so far
    best_pair = None
    computed = 0
    for a in range(n - 1):
        i = order[a]
        xi, yi = events[i]
        for b in range(a + 1, n):
            j = order[b]
            dx = events[j][0] - xi
            dx2 = dx * dx
            if dx2 > best:                   # strict '>' keeps tie candidates alive
                break                        # all later points are even further in x
            dy = events[j][1] - yi
            d2 = dx2 + dy * dy
            computed += 1
            pair = (i, j) if i < j else (j, i)
            if d2 < best or (d2 == best and pair < best_pair):
                best, best_pair = d2, pair
    if stats is not None:
        stats["distance_computations"] = computed
    return best_pair, math.sqrt(best)
