"""Task 3 - 0/1 Knapsack by dynamic programming with item reconstruction."""
import itertools, random


def knapsack(items, W):
    """items: list of (id, weight, value). Returns (best, chosen ids, DP table)."""
    n = len(items)
    DP = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        _, wi, vi = items[i - 1]
        for w in range(W + 1):
            DP[i][w] = DP[i - 1][w]                       # exclude item i
            if wi <= w and DP[i - 1][w - wi] + vi > DP[i][w]:
                DP[i][w] = DP[i - 1][w - wi] + vi         # include item i
    chosen, w = [], W
    for i in range(n, 0, -1):
        if DP[i][w] != DP[i - 1][w]:                      # value changed => item i was included
            chosen.append(items[i - 1][0])
            w -= items[i - 1][1]
    chosen.reverse()
    return DP[n][W], chosen, DP


def brute(items, W):
    best = 0
    for r in range(len(items) + 1):
        for sub in itertools.combinations(items, r):
            if sum(x[1] for x in sub) <= W:
                best = max(best, sum(x[2] for x in sub))
    return best


def print_table(items, W, DP):
    print("DP[i][w]      w=" + "".join(f"{w:>4}" for w in range(W + 1)))
    for i in range(len(items) + 1):
        label = "i=0 (none)" if i == 0 else f"i={i} ({items[i-1][0]})"
        print(f"{label:<14}  " + "".join(f"{DP[i][w]:>4}" for w in range(W + 1)))


if __name__ == "__main__":
    items = [("P", 2, 12), ("Q", 3, 20), ("R", 4, 25), ("S", 5, 30)]
    W = 7
    best, chosen, DP = knapsack(items, W)
    print_table(items, W, DP)
    print("\nKey decisions:")
    print(" DP[1][7] = max(DP[0][7]=0,  DP[0][5]+12=12) =", DP[1][7])
    print(" DP[2][7] = max(DP[1][7]=12, DP[1][4]+20=32) =", DP[2][7])
    print(" DP[3][7] = max(DP[2][7]=32, DP[2][3]+25=45) =", DP[3][7])
    print(" DP[4][7] = max(DP[3][7]=45, DP[3][2]+30=42) =", DP[4][7])
    print("\nOptimal value :", best)
    print("Items selected:", chosen, "| total weight =", sum(x[1] for x in items if x[0] in chosen))
    assert best == 45 and chosen == ["Q", "R"]

    print("\n=== Additional tests ===")
    tests = [("capacity 0", items, 0), ("capacity 1 (nothing fits)", items, 1),
             ("capacity 14 (all fit)", items, 14), ("exact single fit", items, 5)]
    for name, its, cap in tests:
        b, ch, _ = knapsack(its, cap)
        print(f"{name:<26} best={b:<3} items={ch}")
        assert b == brute(its, cap)
    random.seed(3)
    for _ in range(300):
        its = [(f"I{k}", random.randint(1, 8), random.randint(1, 30)) for k in range(random.randint(1, 7))]
        cap = random.randint(0, 20)
        b, ch, _ = knapsack(its, cap)
        assert b == brute(its, cap)
        assert sum(x[2] for x in its if x[0] in ch) == b and sum(x[1] for x in its if x[0] in ch) <= cap
    print("300 random instances: DP == brute force, reconstructed set valid")
    print("\nAll Task 3 tests passed.")
