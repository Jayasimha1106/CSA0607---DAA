# Task 7: Solving the Recurrence (4 marks)

T(n) = T(n/2) + c, T(1) = c1. Assume n = 2^k so n/2 is always an integer.

## Method 1: Iteration (backward substitution)
- T(n) = T(n/2) + c
- = T(n/4) + 2c
- = T(n/8) + 3c
- = ... = T(n/2^i) + i c

Base case when n/2^i = 1, i.e. i = log2 n:

**T(n) = c1 + c log2 n = Theta(log n)**

## Method 2: Master Theorem (verification)
Form T(n) = aT(n/b) + f(n) with a = 1, b = 2, f(n) = c = Theta(1). n^(log_b a) = n^0 = 1. f(n) = Theta(n^0), so **Case 2** applies: T(n) = Theta(n^0 log n) = Theta(log n). Applicable because a >= 1, b > 1 and f is positive.

## Method 3: Induction check
Claim T(n) <= c log2 n + c1. Base T(1) = c1 holds. Step: T(n) = T(n/2) + c <= c log2(n/2) + c1 + c = c log2 n + c1. Holds.

## Interpretation
Doubling the database adds only a constant amount of work (one more comparison). Recursion depth is log2 n, so about 20 stack frames at 10^6 records.
