"""Task B3 - Emergency-service Set Cover: exact (smallest-k-first combination search) vs greedy."""
from itertools import combinations
import random


def exact_cover(n_zones, centres):
    """Try every combination of size 1,2,3,... ; first size that covers everything is optimal.
    Returns (chosen_indices, combinations_examined). Zones are 0..n-1; centres = list of sets."""
    full = (1 << n_zones) - 1
    masks = [sum(1 << z for z in c) for c in centres]
    examined = 0
    if full == 0:
        return [], 0
    for k in range(1, len(centres) + 1):
        for combo in combinations(range(len(centres)), k):
            examined += 1
            cov = 0
            for i in combo:
                cov |= masks[i]
            if cov == full:
                return list(combo), examined
    return None, examined          # no cover exists


def greedy_cover(n_zones, centres):
    """Repeatedly pick the centre covering most currently-uncovered zones.
    Returns (chosen_indices, evaluations) where evaluations = # of |S & uncovered| computations."""
    uncovered = set(range(n_zones))
    selected, evals = [], 0
    while uncovered:
        best, best_gain = None, 0
        for i, c in enumerate(centres):
            evals += 1
            gain = len(c & uncovered)
            if gain > best_gain:                  # strict '>' : ties -> lowest index
                best, best_gain = i, gain
        if best is None:
            return None, evals                    # remaining zones cannot be covered
        selected.append(best)
        uncovered -= centres[best]
    return selected, evals


def random_instance(n_zones, n_centres, seed, density=0.25):
    rnd = random.Random(seed)
    centres = [set(z for z in range(n_zones) if rnd.random() < density) for _ in range(n_centres)]
    for z in range(n_zones):                      # guarantee feasibility
        if not any(z in c for c in centres):
            centres[rnd.randrange(n_centres)].add(z)
    return centres
