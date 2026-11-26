"""Task 4 - WordBreak: faulty version, failing input, repaired version."""
import random
from functools import lru_cache


def word_break_faulty(text, dic, trace=False):
    n = len(text)
    DP = [False] * (n + 1)
    DP[0] = True
    for i in range(1, n + 1):
        DP[i] = False
        for j in range(0, i):
            if text[j:i] in dic:                 # DEFECT: DP[j] is never checked
                DP[i] = True
                if trace:
                    print(f"  i={i}: j={j} substring '{text[j:i]}' in dictionary -> DP[{i}]=TRUE   (but DP[{j}]={DP[j]})")
                break
        if trace and not DP[i]:
            print(f"  i={i}: no substring ending at {i} is in dictionary -> DP[{i}]=FALSE")
    return DP[n], DP


def word_break_fixed(text, dic, trace=False):
    n = len(text)
    DP = [False] * (n + 1)
    DP[0] = True
    for i in range(1, n + 1):
        DP[i] = False
        for j in range(0, i):
            if DP[j] and text[j:i] in dic:       # FIX: prefix text[0:j] must itself be segmentable
                DP[i] = True
                if trace:
                    print(f"  i={i}: j={j} DP[{j}]=TRUE and '{text[j:i]}' in dictionary -> DP[{i}]=TRUE")
                break
        if trace and not DP[i]:
            print(f"  i={i}: no j with DP[j]=TRUE and word in dictionary -> DP[{i}]=FALSE")
    return DP[n], DP


def reference(text, dic):
    @lru_cache(None)
    def go(s):
        return s == "" or any(s[:k] in dic and go(s[k:]) for k in range(1, len(s) + 1))
    return go(text)


if __name__ == "__main__":
    text, dic = "abcd", {"bcd"}
    print(f"=== Task 4.2 Failing input: Text='{text}', Dictionary={sorted(dic)} ===")
    r, DP = word_break_faulty(text, dic, trace=True)
    print("Faulty result :", r, "| DP =", DP)
    print("Correct answer:", reference(text, dic), "(the leading letter 'a' is not a dictionary word)")
    assert r is True and reference(text, dic) is False

    print("\n=== Task 4.3 Repaired algorithm on the same input ===")
    r, DP = word_break_fixed(text, dic, trace=True)
    print("Fixed result  :", r, "| DP =", DP)
    assert r is False

    text, dic = "leetcode", {"leet", "code"}
    print(f"\n=== Task 4.4 Regression: Text='{text}', Dictionary={sorted(dic)} ===")
    r1, D1 = word_break_faulty(text, dic)
    print("Original algorithm:", r1, D1)
    r2, D2 = word_break_fixed(text, dic, trace=True)
    print("Fixed algorithm   :", r2, D2)
    assert r1 is True and r2 is True and reference(text, dic) is True

    print("\n=== Randomised check (alphabet {a,b}) ===")
    random.seed(1)
    bad_faulty = 0
    for _ in range(2000):
        t = "".join(random.choice("ab") for _ in range(random.randint(1, 8)))
        d = {"".join(random.choice("ab") for _ in range(random.randint(1, 3))) for _ in range(random.randint(1, 3))}
        assert word_break_fixed(t, d)[0] == reference(t, d)
        bad_faulty += word_break_faulty(t, d)[0] != reference(t, d)
    print(f"Fixed algorithm matches the reference on 2000/2000 inputs; faulty algorithm wrong on {bad_faulty}.")
    print("\nAll Task 4 tests passed.")
