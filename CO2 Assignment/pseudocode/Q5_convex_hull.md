# Q5 – Pseudocode: Brute-Force Convex Hull (derived from the half-plane principle)
Geometric rule: for p=(x1,y1), q=(x2,y2) the line is a·x + b·y = c with a = y2-y1, b = x1-x2, c = x1·y2 - y1·x2.
Point r lies on one side iff  a·rx + b·ry - c  has a fixed sign (equivalently the cross product (q-p)×(r-p)).
```
Side(p, q, r) = (qx-px)*(ry-py) - (qy-py)*(rx-px)       # >0 left, <0 right, 0 collinear

ConvexHull(P):
  remove duplicate points
  tests = 0; edges = []
  for each pair (p, q) with index i < j:
      sawPositive = false; sawNegative = false; valid = true
      for each other point r:
          tests++; s = Side(p, q, r)
          if s > 0: sawPositive = true
          elif s < 0: sawNegative = true
          elif r NOT between p and q: valid = false; break      # collinear but beyond segment => pq not extreme
          if sawPositive and sawNegative: valid = false; break  # points on both sides => interior chord
      if valid: edges.append((p, q))
  vertices = all endpoints of accepted edges
  centre = mean(vertices)
  sort vertices by atan2(y-cy, x-cx)           # counter-clockwise boundary order
  return vertices, edges, tests
```
