"""Pseudocode strings shared by pseudocode/pseudocode.md and the Word report."""

CORRECTED = {
"sort_alerts (corrected insertion sort)": """\
ALGORITHM SortAlerts(A[0..n-1])        // severity high -> low, stable
    for i <- 1 to n-1 do
        key <- A[i]
        j   <- i - 1
        while j >= 0 AND A[j].severity < key.severity do   // strict '<' keeps arrival order
            A[j+1] <- A[j]                                  // shift weaker alert right
            j      <- j - 1
        A[j+1] <- key                                       // insert in the freed slot
    return A""",
"is_blocked (corrected sequential search)": """\
ALGORITHM IsBlocked(L[0..b-1], ip)
    for i <- 0 to b-1 do
        if L[i] = ip then return TRUE                       // found: stop at once
    return FALSE                                            // only after ALL entries were checked""",
"find_signature (corrected brute-force matching)": """\
ALGORITHM FindSignature(T[0..n-1], P[0..m-1])
    hits <- empty list
    if m = 0 then return hits
    for i <- 0 to n-m do                                    // n-m+1 alignments (none if m > n)
        j <- 0
        while j < m AND T[i+j] = P[j] do j <- j + 1
        if j = m then append i to hits                      // all m characters matched
    return hits""",
"closest_logins (corrected brute force)": """\
ALGORITHM ClosestPairBF(E[0..n-1])                          // E[k] = (x, y)
    if n < 2 then return (NONE, NONE)
    best <- +INFINITY ; pair <- NONE
    for i <- 0 to n-2 do
        for j <- i+1 to n-1 do                              // each unordered pair once
            d <- sqrt( (E[i].x - E[j].x)^2 + (E[i].y - E[j].y)^2 )
            if d < best then best <- d ; pair <- (i, j)
    return (pair, best)""",
}

OPTIMISED = {
"sort_alerts (optimised)": """\
ALGORITHM SortAlertsFast(A[0..n-1])
    // stable, adaptive merge-based sort (Timsort):
    // 1. split A into natural runs (already ordered stretches); extend short runs by insertion sort
    // 2. merge neighbouring runs with a stable merge (ties taken from the left run)
    sort A by key = severity, descending, stable
    return A                                                // O(n) if nearly sorted, O(n log n) worst""",
"is_blocked (optimised, repeated look-ups)": """\
ALGORITHM BuildBlocklist(L[0..b-1])                         // once per blocklist update: O(b)
    S <- empty hash set
    for each ip in L do insert ip into S
    return S

ALGORITHM IsBlockedFast(S, ip)                              // per alert: O(1) average
    return ( ip in S )""",
"find_signature (optimised)": """\
ALGORITHM FindSignatureFast(T[0..n-1], P[0..m-1])
    if m = 0 OR m > n then return empty list                // no alignment can exist
    hits <- empty list
    for i <- 0 to n-m do                                    // only feasible alignments
        j <- 0
        while j < m do
            if T[i+j] != P[j] then break                    // first mismatch ends this alignment
            j <- j + 1
        if j = m then append i to hits
    return hits                                             // no comparison is repeated or wasted""",
"closest_logins (optimised)": """\
ALGORITHM ClosestPairFast(E[0..n-1])
    if n < 2 then return (NONE, NONE)
    order <- indices 0..n-1 sorted by E[k].x                // O(n log n)
    best  <- +INFINITY                                      // best SQUARED distance
    for a <- 0 to n-2 do
        i <- order[a]
        for b <- a+1 to n-1 do
            j  <- order[b]
            dx <- E[j].x - E[i].x
            if dx*dx > best then break                      // PRUNE: later points are even further in x
            d2 <- dx*dx + (E[j].y - E[i].y)^2               // no square root
            if d2 < best OR (d2 = best AND (i,j) smaller than current pair)
                then best <- d2 ; pair <- (min(i,j), max(i,j))
    return (pair, sqrt(best))                               // ONE square root""",
}
