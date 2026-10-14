<!-- tags: [lattice-path] -->
<!-- status: final -->
# Lattice path

A **lattice path** is a walk on the integer grid ℤ² made from a fixed set of steps — most often
the two *monotone* steps right `(1, 0)` and down `(0, 1)`. Project Euler comes back to them for two
different reasons. Sometimes it asks *how many* paths there are, and the answer is a binomial
coefficient. Sometimes it puts a number in every cell and asks for the *best* path, and the answer
is a dynamic program. The point of this page is that those are the same computation: one
recurrence over the grid, with addition and multiplication swapped for `min` and `+`.

## Counting: the central binomial coefficient

Problem 15 asks for the number of right/down routes from the top-left to the bottom-right corner of
a 20 × 20 grid. Any such route takes exactly 20 right steps and 20 down steps, 40 in all, and it is
fully determined by *which* 20 of the 40 positions hold the right steps. So the count is

    paths(m, n) = C(m + n, m)            and on the square grid    paths(n, n) = C(2n, n)

the [central binomial coefficient](/topics/domain/central-binomial-coefficient)
([OEIS A000984](https://oeis.org/A000984): 1, 2, 6, 20, 70, …). The public solution is one line:

```python
return str(math.factorial(2 * lattice_size) // math.factorial(lattice_size) ** 2)
```

The bijection — a path *is* a word of `R`s and `D`s, and a word is a choice of positions — is the
whole idea, and it is worth having to hand because it generalises cleanly: with three step types it
becomes a multinomial, in `d` dimensions `(n₁ + … + n_d)! / (n₁! ⋯ n_d!)`, and counting paths that
must pass *through* a point multiplies two binomials together.

There is a second way to the same number, and it is the one that scales to harder problems. The
last step into cell `(r, c)` came either from above or from the left, so

    N(r, c) = N(r−1, c) + N(r, c−1)        N(0, c) = N(r, 0) = 1

which is [Pascal's rule](https://en.wikipedia.org/wiki/Pascal%27s_rule) written on the grid — the
grid *is* Pascal's triangle turned 45°, with `C(r + c, r)` in cell `(r, c)`. The closed form costs
O(n) big-integer multiplications; the table costs O(n²) additions. For an empty grid the formula
wins. The table wins the moment the grid stops being empty.

## Optimising: the same recurrence, another semiring

Problem 81 writes an integer in each cell of an 80 × 80 matrix and asks for the right/down path with
the smallest sum. Take the counting recurrence and change two operators:

    N(r, c)    = N(r−1, c)    +   N(r, c−1)                   (count paths)
    best(r, c) = v[r][c]  +  min(best(r−1, c), best(r, c−1))  (cheapest path)

Counting combines the predecessors with `+` and extends a path by `×1`; optimising combines them
with `min` and extends a path by `+ v`. Both are the same sweep over a
[directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) whose nodes are cells
and whose edges are the allowed steps; what changes is the
[semiring](https://en.wikipedia.org/wiki/Semiring) — `(+, ×)` for counting, `(min, +)` for
shortest paths, `(max, +)` for the triangles of 18 and 67. Why `min` gives the right answer, and not
just a plausible one, is the cut-and-paste argument on the
[optimal substructure](/topics/domain/optimal-substructure) page. What the lattice adds is the
**order**: monotone steps make the grid acyclic, so *any* order that finishes a cell's predecessors
first is correct — row by row, column by column, or, as the public solution to 81 does it, along
anti-diagonals from the far corner. One pass, O(n²), and the closed form is gone for good: there is
no formula for a weighted grid.

## When the steps stop being monotone

Problem 82 allows right, up *and* down. The graph now has cycles within each column (up then down),
so "predecessors first" no longer has an answer. What saves it is that the cycles are confined to a
column: moves between columns are still one-way. So I sweep column by column, right to left, and
solve each column as a 1-D problem. Entering column `c` at row `i` and stepping right at row `j`
costs the range sum of `v[i..j][c]` plus the solved cost to the right of `(j, c)`.

Minimising that over every `(i, j)` pair is at least O(n²) per column, and the public solution does
essentially that, recomputing each range sum as it goes. The cheaper way runs two passes per column, since an optimal path never doubles back on
itself inside a column:

    cost[i] = v[i][c] + right[i]                       # step straight right
    cost[i] = min(cost[i], v[i][c] + cost[i−1])        # top-down: arrive from above
    cost[i] = min(cost[i], v[i][c] + cost[i+1])        # bottom-up: arrive from below

That's O(n) per column and O(n²) in all, the same as 81. The lesson generalises: when a step set
breaks acyclicity only *locally*, find the direction that is still one-way and run the DP along it,
relaxing the cyclic part inside each slice. When the cycles are global — Problem 83 allows all four
directions — no sweep order exists, and the DP becomes
[Dijkstra's algorithm](/topics/technique/dijkstras-algorithm): the same `min`-plus relaxation, with
the order discovered at run time by a priority queue instead of fixed by the geometry.

## How to reason about it

- **Count with the formula, count around obstacles with the table.** On an empty rectangle, use
  `C(m + n, m)`. With a few forbidden points (Problem 408's blocked cells are one example), the
  table is too big, but the formula still works between points: sort the blockers in path order and
  let `f(p) = C(origin → p) − Σ f(q) · C(q → p)` over the blockers `q` that come before `p`. That's
  [inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over the first blocker hit,
  and it costs O(k²) binomials for `k` blockers, whatever the grid size.
- **Weights on the path, not the cells, can keep a closed form.** Give each path the weight `q^area`
  (the area under it), and the sum over all paths is the
  [Gaussian binomial](/topics/technique/gaussian-binomial-coefficient) `[m+n choose m]_q` — the
  q-analogue of the count above, and the shape behind Problem 638.
- **Monotone paths through points are chains.** The most marked points a single up-right path can
  visit is the longest chain in the product order: sort by `x`, then take the longest
  non-decreasing subsequence in `y`. Problem 411 is this question at scale.
- **Exact counts overflow fast.** `C(40, 20)` already needs 38 bits, and `C(2n, n) ≈ 4ⁿ / √(πn)`
  grows by about a factor of four per step. Use Python big integers, or work modulo the problem's
  prime with precomputed factorials and inverse factorials.
- **Check the step set before reaching for a formula.** Right/down gives binomials; adding a
  diagonal step gives the [Delannoy numbers](https://en.wikipedia.org/wiki/Delannoy_number); not
  crossing the diagonal gives the [Catalan numbers](/topics/domain/catalan-number); arbitrary
  steps (Problem 662's Fibonacci-length jumps, Problem 300's self-avoiding folds) usually leave you
  with just the recurrence, and the work is finding an order to evaluate it in.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ○ [0295](/solutions/0295/) — Lenticular Holes
- ○ [0300](/solutions/0300/) — Protein Folding
- ○ [0354](/solutions/0354/) — Distances in a Bee's Honeycomb
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ○ [0403](/solutions/0403/) — Lattice Points Enclosed by Parabola and Line
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0411](/solutions/0411/) — Uphill Paths
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ○ [0460](/solutions/0460/) — An Ant on the Move
- ○ [0628](/solutions/0628/) — Open Chess Positions
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ○ [0662](/solutions/0662/) — Fibonacci Paths
- ○ [1005](/solutions/1005/) — Median Prime List

<!-- /problems -->
