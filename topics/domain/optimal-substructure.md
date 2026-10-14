<!-- tags: [optimal-substructure] -->
<!-- status: final -->
# Optimal substructure

A problem has **optimal substructure** when an optimal solution to it is built out of optimal
solutions to smaller instances of the same problem. It is the property that makes
[dynamic programming](/topics/technique/dynamic-programming) *correct*: if the best answer from here
is "the best first step plus the best answer from wherever that step lands", I can solve each
smaller instance once and assemble the big one from them. The path-sum problems — the triangles of
18 and 67, the matrices of 81 and 82 — are the cleanest illustration of it in Project Euler, and
the same argument quietly carries the tiling counts, the factorisation maximum and the
optimal-strategy problems further down the list.

## The idea

Take Problem 18: walk from the apex of a triangle to its base, stepping to one of the two adjacent
numbers in the row below, and maximise the sum. Let `best(r, c)` be the largest sum of a path that
*starts* at row `r`, column `c`. Then

    best(r, c) = v[r][c] + max(best(r+1, c), best(r+1, c+1))      best(last row, c) = v[last][c]

Why is that recurrence true, and not just plausible? The textbook proof is the
**cut-and-paste argument** (as in [CLRS](https://en.wikipedia.org/wiki/Introduction_to_Algorithms)'
chapter on dynamic programming): suppose an optimal path from `(r, c)` steps to `(r+1, c)` but then
follows a tail that is *not* the best path from `(r+1, c)`. Cut that tail out and paste in the
better one — the path is still legal (the tail's choices never depended on how we arrived) and its
sum went up, contradicting optimality. So every tail of an optimal path is itself optimal, and the
only real decision at each cell is which child to go to.

That one fact turns an exponential search into a polynomial one. A 15-row triangle has
2¹⁴ = 16 384 paths, which Problem 18 lets you enumerate; Problem 67's 100 rows have 2⁹⁹, which it
explicitly does not. But there are only `n(n+1)/2` *cells*, and each `best(r, c)` is needed by two
parents — the subproblems **overlap**, so solving each once is the whole saving. Optimal
substructure makes the recurrence right; overlapping subproblems make it fast. You need both.

The public solution to 18 (and 67, which is the same function on a bigger file) evaluates the
recurrence bottom-up, folding the last row into the one above until only the apex is left:

```python
def max_path_sum_triangle(triangle: list[list[int]]) -> int:
    triangle = copy.deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]
```

Going bottom-up is a choice of subproblem, not a requirement. "Best path *from* here" ends with the
answer sitting at the apex; "best path *to* here" runs top-down and needs a final `max` over the
base row. Either is fine — what matters is that each subproblem is finished before anyone reads it.

Note what the recurrence is *not*: greedy. Greedy descends to the larger child and never looks back,
and a triangle like `1 / 2 1 / 1 1 100` lures it to 4 when 102 was available. Optimal substructure
says the best path is made of best sub-paths; it does not say the locally best step is part of it.

## The grid: the same argument, different shapes

Problem 81 moves the walk to a square matrix — only right and down, minimise the sum from top-left
to bottom-right. The substructure is identical: `best(r, c) = v[r][c] + min(best(r+1, c), best(r, c+1))`.
The only new question is **evaluation order**. The cells form a
[directed acyclic graph](/topics/domain/directed-acyclic-graph) (every move goes right or down), and
any reverse topological order works; the repository's solution sweeps the anti-diagonals from the
bottom-right corner, though a plain reverse row-major sweep is equally valid.

Problem 82 is where it gets instructive. Now the path may start anywhere in the left column, end
anywhere in the right one, and move up, down *or* right. Up and down make the per-cell graph
**cyclic**, so a per-cell recurrence no longer has a well-founded order — `best(r, c)` would depend on
`best(r-1, c)`, which depends on `best(r, c)`. The substructure has not gone away; it has moved to a
coarser grain. Because every entry is positive, an optimal path never reverses direction inside a
column, so its stay in column `c` is a contiguous vertical run from the entry row `r` to some exit
row `t`, after which it steps right. That gives a recurrence over **columns**:

    best(r, c) = min over t of ( sum of column c between rows r and t ) + best(t, c+1)

and columns *are* acyclic, so the solution sweeps them right to left. Done literally that is
`O(n³)` (`n` rows, `n` exit choices, a range sum each) — the public solution's shape, and plenty
for an 80×80 matrix. The standard refinement is two relaxation passes per column — one downward,
`best(r) = min(best(r), best(r-1) + v[r][c])`, one upward — which brings it to `O(n²)`.

Problem 83 (up, down, left, right — not on this tag) is the end of that road: the graph is cyclic
in both directions and there is no column order left to exploit. The substructure *still* holds —
it is Bellman's [principle of optimality](https://en.wikipedia.org/wiki/Bellman_equation#Bellman's_principle_of_optimality)
for [shortest paths](/topics/domain/shortest-path-problem): every sub-path of a shortest path is a
shortest path — but you need [Dijkstra's algorithm](/topics/technique/dijkstras-algorithm) to
discover the order in which to finalise cells, rather than knowing it in advance.

## Beyond paths

The same shape — "the value of what remains depends only on where I am, not how I got here" —
recurs on problems that do not look like walks:

- **114 and 117** count tilings rather than optimise them, but the step is the same: the number of
  ways to fill the rest of a row depends only on how many units remain, so a suffix table over
  lengths replaces enumerating arrangements.
- **159** maximises a digital-root sum over the factorisations of `n`. Keep one factor whole; the
  remaining factors are a factorisation of the cofactor, and they can do no better than *its*
  maximum — a cut-and-paste argument over divisors, filled by a sieve-style push.
- **352** asks for the cheapest pooled-testing strategy, and its statement contains the line that
  *creates* the substructure: once you test a mixed sample, every sheep in it must be resolved
  before any other animal is examined. That rule makes each group an independent subproblem whose
  optimal cost depends only on its size and what is already known about it.
- **470** is optimal stopping: with `k` rolls left, the value of the game is the expectation of
  "the better of keeping this roll or playing on with `k-1`" — the
  [Bellman equation](https://en.wikipedia.org/wiki/Bellman_equation) in its plainest form.

## How to reason about it

Before writing the recurrence, try the cut-and-paste argument in your head: *if the remainder of
an optimal solution were not optimal for its own subproblem, could I swap in a better one and stay
legal?* The "stay legal" clause is where it fails, and these are the usual ways:

- **The state is too small.** If the best continuation depends on something the state forgot —
  cells already visited, a budget already spent, a direction already taken — then two arrivals at
  the "same" state are not interchangeable. The fix is to widen the state until they are; see
  [the memo key is the full state](/topics/takeaway/memo-key-is-the-full-state). The classic
  counterexample is the *longest simple path*: a sub-path of a longest simple path need not be
  longest, because the better sub-path may reuse vertices the rest of the path already used.
- **The weights can be negative.** Problem 82's "never reverse in a column" relies on positive
  entries; Dijkstra for 83 relies on them too. With negative weights the substructure of shortest
  paths survives only if there are no negative cycles, and the algorithm changes
  ([Bellman–Ford](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm)).
- **The order is wrong.** A correct recurrence evaluated before its dependencies are final gives
  a wrong answer with no error. Name the dependency direction — downward rows, reverse
  anti-diagonals, right-to-left columns, increasing cofactors — and sweep against it.

When the argument does go through, the payoff is large and predictable: the cost is the number of
distinct subproblems times the work to combine each one's choices, which is why 67's 2⁹⁹ paths cost
five thousand additions.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ○ [0352](/solutions/0352/) — Blood Tests
- ○ [0470](/solutions/0470/) — Super Ramvok

<!-- /problems -->
