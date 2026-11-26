"""
CO4 Assignment 4B - Task 1: Word Wrap as a Document-Layout Engine (Dynamic Programming)

Model
-----
Words w[0..n-1] are placed on lines of maximum width W (one space between words on a line).
A NON-FINAL line with s unused spaces costs s^2.  The FINAL line costs 0.

DP state (suffix formulation)
-----------------------------
dp[i]  = minimum total penalty for laying out words i..n-1, given that a NEW line starts at word i.
dp[n]  = 0                                   (nothing left to place)
dp[i]  = min over j in (i+1..n) such that words i..j-1 fit in W of
             lineCost(i, j) + dp[j]
         lineCost(i, j) = 0            if j == n   (final line is free)
                        = slack(i,j)^2 otherwise
nxt[i] = the j that achieved dp[i]   (used to rebuild the lines)
Answer = dp[0].  Time O(n * k) where k = max words per line; space O(n).

Tie-break: strict '<' keeps the FIRST minimum, i.e. the candidate with the fewest words on line i.
"""

import itertools
import random

INF = float("inf")


# ----------------------------------------------------------------------------- algorithm
def validate_input(words, width):
    """Reject inputs for which no legal layout exists."""
    if width <= 0:
        raise ValueError("line width must be positive")
    for word in words:
        if len(word) > width:
            raise ValueError(f"word '{word}' (length {len(word)}) is longer than width {width}")


def word_wrap(words, width, record_states=False):
    """Return (min_penalty, lines, states).

    lines  : list of dicts {words, used, slack, penalty}
    states : per-i DP trace (only when record_states=True)
    """
    validate_input(words, width)
    n = len(words)
    if n == 0:
        return 0, [], []

    prefix = [0]                                   # prefix[k] = total letters of words[0..k-1]
    for word in words:
        prefix.append(prefix[-1] + len(word))

    def line_length(i, j):                         # words i..j-1 with single spaces
        return prefix[j] - prefix[i] + (j - i - 1)

    dp = [INF] * (n + 1)
    nxt = [-1] * (n + 1)
    dp[n] = 0
    states = []

    for i in range(n - 1, -1, -1):
        candidates = []
        for j in range(i + 1, n + 1):
            length = line_length(i, j)
            if length > width:                     # adding more words only makes it longer
                break
            slack = width - length
            line_cost = 0 if j == n else slack * slack
            total = line_cost + dp[j]
            candidates.append((j, slack, line_cost, total))
            if total < dp[i]:
                dp[i] = total
                nxt[i] = j
        if record_states:
            states.append({"i": i, "word": words[i], "candidates": candidates,
                           "dp": dp[i], "next": nxt[i]})

    lines, i = [], 0
    while i < n:
        j = nxt[i]
        slack = width - line_length(i, j)
        penalty = 0 if j == n else slack * slack
        lines.append({"words": words[i:j], "used": line_length(i, j), "slack": slack, "penalty": penalty})
        i = j
    assert sum(l["penalty"] for l in lines) == dp[0], "rebuilt layout disagrees with dp[0]"
    return dp[0], lines, states


def brute_force_min_penalty(words, width):
    """Independent reference: try every subset of break positions (2^(n-1) layouts)."""
    n = len(words)
    best = INF
    for mask in range(1 << max(n - 1, 0)):
        cuts = [0] + [k + 1 for k in range(n - 1) if mask >> k & 1] + [n]
        cost, ok = 0, True
        for a, b in zip(cuts, cuts[1:]):
            length = sum(len(w) for w in words[a:b]) + (b - a - 1)
            if length > width:
                ok = False
                break
            if b != n:
                cost += (width - length) ** 2
        if ok:
            best = min(best, cost)
    return best if n else 0


# ----------------------------------------------------------------------------- presentation
def print_layout(words, width, penalty, lines):
    print(f"Line width W = {width}")
    print(f"Minimum total penalty = {penalty}")
    print(f"{'Line':<5}{'Words on the line':<44}{'Used':>5}{'Unused':>8}{'Penalty':>9}")
    for number, line in enumerate(lines, 1):
        text = " ".join(line["words"])
        note = "  (final line - free)" if number == len(lines) else ""
        print(f"{number:<5}{text:<44}{line['used']:>5}{line['slack']:>8}{line['penalty']:>9}{note}")
    print("Ruler  :", "".join(str(k % 10) for k in range(1, width + 1)))
    for line in lines:
        print("Layout :", " ".join(line["words"]).ljust(width) + "|")


def print_states(words, width, states):
    print(f"DP states for W = {width}   (dp[i] = best penalty for words i..n-1 when a new line starts at word i)")
    print(f"{'i':>2} {'word':<12}{'candidate line  i..j-1  ->  (j, slack, line cost, cost+dp[j])':<70}{'dp[i]':>6}{'next':>6}")
    for st in states:
        cand = "  ".join(f"({j},{s},{c},{t})" for j, s, c, t in st["candidates"])
        print(f"{st['i']:>2} {st['word']:<12}{cand:<70}{st['dp']:>6}{st['next']:>6}")
    print(f"{len(words):>2} {'<end>':<12}{'base case dp[n] = 0':<70}{0:>6}{'-':>6}")


def first_difference(lines_a, lines_b):
    """Index (1-based) of the first line whose word list differs, else None."""
    for k, (a, b) in enumerate(zip(lines_a, lines_b), 1):
        if a["words"] != b["words"]:
            return k
    return None if len(lines_a) == len(lines_b) else min(len(lines_a), len(lines_b)) + 1


# ----------------------------------------------------------------------------- experiments
TEXT = ("Dynamic programming solves a large layout problem by storing the best "
        "answer for every suffix of the paragraph")

PREDICTIONS = {            # written BEFORE the modified cases were executed
    26: "Arrangement WILL change; first change on line 1 (line 1 can now take one more word); total penalty will DECREASE.",
    32: "Arrangement WILL change; first change on line 1; total penalty will DECREASE (fewer penalised lines).",
    40: "Arrangement WILL change; first change on line 1; total penalty will DECREASE (only 2-3 lines, last is free).",
}


def main():
    words = TEXT.split()
    print("=" * 100)
    print("TASK 1.1  BASE CASE")
    print("Text  :", TEXT)
    print("Words :", len(words))
    base_width = 20
    base_penalty, base_lines, base_states = word_wrap(words, base_width, record_states=True)
    print_layout(words, base_width, base_penalty, base_lines)

    print("\n" + "=" * 100)
    print("TASK 1.2  DP STATES (base case)")
    print_states(words, base_width, base_states)

    print("\n" + "=" * 100)
    print("TASK 1.3  REQUIREMENT CHANGE - different line widths")
    previous = (base_penalty, base_lines)
    for width in (26, 32, 40):
        print(f"\n--- W: {base_width} -> {width} ---")
        print("PREDICTION (recorded before running):", PREDICTIONS[width])
        penalty, lines, _ = word_wrap(words, width)
        print_layout(words, width, penalty, lines)
        changed = first_difference(base_lines, lines)
        direction = "decrease" if penalty < base_penalty else ("increase" if penalty > base_penalty else "stay equal")
        print(f"ACTUAL: arrangement changed = {changed is not None}; first changed line = {changed}; "
              f"lines {len(base_lines)} -> {len(lines)}; penalty {base_penalty} -> {penalty} ({direction})")
    print("\nPenalty versus width (all widths 11..45):")
    print("W   :", " ".join(f"{w:>3}" for w in range(11, 46)))
    print("pen :", " ".join(f"{word_wrap(words, w)[0]:>3}" for w in range(11, 46)))

    print("\n" + "=" * 100)
    print("TASK 1.4  BOUNDARY TESTS")
    tests = [
        ("exact fit, one line: 'aaa bb c', W=8", ["aaa", "bb", "c"], 8, 0),
        ("one unused space before a break, W=7", ["aaa", "bb", "c"], 7, 1),
        ("single word equal to W", ["abcdef"], 6, 0),
        ("single word, much slack on final line", ["hi"], 40, 0),
        ("empty paragraph", [], 10, 0),
    ]
    for name, ws, w, expected in tests:
        penalty, lines, _ = word_wrap(ws, w)
        verdict = "PASS" if penalty == expected else "FAIL"
        print(f"{verdict}  {name:<45} expected={expected} actual={penalty} lines={[' '.join(l['words']) for l in lines]}")
    try:
        word_wrap(["extraordinary", "word"], 5)
    except ValueError as err:
        print("PASS  word longer than W is rejected ->", err)
    rng = random.Random(7)
    trials, mismatches = 400, 0
    for _ in range(trials):
        ws = ["x" * rng.randint(1, 8) for _ in range(rng.randint(1, 10))]
        w = rng.randint(8, 25)
        if word_wrap(ws, w)[0] != brute_force_min_penalty(ws, w):
            mismatches += 1
    print(f"Randomised DP vs brute force over {trials} paragraphs: mismatches = {mismatches}")


if __name__ == "__main__":
    main()
