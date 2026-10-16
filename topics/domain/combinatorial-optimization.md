<!-- tags: [combinatorial-optimization] -->
<!-- status: final 2026-10-16T07:04Z -->
# Combinatorial optimization

[Combinatorial optimization](https://en.wikipedia.org/wiki/Combinatorial_optimization) is the
search for the *best* member of a finite set: the shortest pipe, the heaviest matching, the
special set with the smallest total. "Finite" is cold comfort — the sets here have $15!$,
$10^{16}$ or $2^{500}$ members. What unites the problems below is not a technique but a predicament: an optimum
provably exists, and you provably cannot find it by looking at all the candidates. Everything on
this page is a way of not looking.

## Choosing is not counting

It is worth separating this domain from its neighbour, [combinatorics](/topics/domain/combinatorics).
There, you must account for *every* configuration; a single one you miss or double-count corrupts
the answer. Here you need exactly one configuration — but you owe a proof that nothing else is
better.

That difference cuts both ways. It hands you a lever counting never gets: the moment you can show a
whole region of the space contains nothing better than what you already hold, you may discard it
unexamined. But it also imposes a debt. Brute force proves optimality for free, by exhaustion;
every shortcut you take instead has to pay that proof back some other way. Most wrong answers in
this domain are not wrong configurations — they are correct-looking configurations with no argument
behind them.

## Name the structure before you search

Almost every problem here is a classical problem in costume, and the disguise is usually thin.
Problem 345 asks for the maximum sum of matrix entries with no two sharing a row or column; a
selection of one entry per row and per column is a perfect matching in a bipartite graph, so this
is the [assignment problem](/topics/domain/assignment-problem) and $60$ years of literature apply.
Problem 60 asks for five primes that pairwise concatenate to primes — make each prime a node and
each valid pair an edge and it is a minimum-weight [clique](/topics/domain/clique-problem). Problem
185 (Number Mind) is a [constraint satisfaction problem](/topics/domain/constraint-satisfaction).
Problem 222 is a permutation-ordering problem with a travelling-salesman flavour. Problem 252 asks
for the largest "hole" among $500$ pseudo-random points, and is the *largest empty convex polygon*
problem of [computational geometry](/topics/domain/computational-geometry), which has a published
$O(n^3)$ algorithm (Dobkin, Edelsbrunner and Overmars) waiting to be used.

Naming it tells you immediately what is known: whether a polynomial algorithm exists, which bounds
are standard, and — often the most useful fact — that the general case is
[NP-hard](/topics/domain/np-hardness) and you should stop hunting for a clean algorithm and start
hunting for the specific structure *this* instance has.

## Five ways to avoid the whole space

**Order the search so the first solution found is the best one.** The cheapest possible proof of
optimality. Problem 60 (public, `solutions/public/p0060/`) builds cliques by extending only with
primes strictly greater than the last, over an ascending prime list:

```python
for prime in primes:
    if prime <= current_list[-1]:
        continue                                # strictly increasing: each set visited once
    for p in current_list:
        if not concatenate_is_prime(p, prime):  # prune before recursing, not after
            break
    else:
        yield (current_list + [prime])
```

Two things fall out of the ascending constraint. Each unordered set is reached in exactly one
order, so no duplicate work; and because the enumeration is ordered by value, the *first* complete
clique found already has the minimum sum. A single `next()` on the generator chain stops the search
there. No bound, no comparison, no second pass — the ordering *is* the proof.

**Collapse the history into a state.** The question that drives
[dynamic programming](/topics/technique/dynamic-programming) applies verbatim to optimisation:
what is the least you must remember about a partial solution to extend it correctly? Problem 345's
$15!$ orderings collapse the moment you notice that when assigning a row, only the *set* of
already-used columns matters, never the order they were used in. That is $2^{15}$ subsets instead
of $1.3\times10^{12}$ permutations — a bitmask DP in $O(2^n n)$, exact and instant. The general
shape, for a mask of used items where the row index is recovered as the popcount:

```python
for mask in range(1 << n):                      # increasing order: dependencies filled first
    row = mask.bit_count()                      # no need to store the row separately
    for col in unused_columns(mask):
        relax(dp, mask | (1 << col), dp[mask] + weight(row, col))
```

Note that the exponential $2^n$ here is a *win*: the polynomial [Hungarian
algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm) also solves problem 345, but at
$n = 15$ the bitmask sweep is faster to write, easier to get right, and fast enough. Asymptotics
decide nothing until you know the input size.

Sometimes there is no small state until you rewrite the constraint. In problem 252 a polygon is
admissible only if *no* point lies inside it, a condition on the whole shape that a chain of
vertices can't carry forward. The fix is a decomposition. Fix the polygon's lowest vertex $p$ as an
apex and fan the polygon into triangles $(p, v_i, v_{i+1})$. Then the polygon is empty exactly when
every fan triangle is empty and no point sits on an internal diagonal, and its area is the sum of
the triangle areas. Now emptiness, area and convexity all depend only on the last edge of the chain,
so the DP state is "best chain ending in edge $q_i \to q_j$" for each apex. The general move is to
find a decomposition that turns a global feasibility test into a local one. A memo cannot hold a
constraint like "nothing inside", but it can hold one edge.

**Bound and prune.** [Branch and bound](/topics/technique/branch-and-bound) needs two things: an
*incumbent* (some feasible solution, giving an upper bound on the optimum) and a *lower bound* on
anything a partial solution can still become. When the bound meets the incumbent, the subtree dies.
Problem 103 is the pattern in full — the statement itself supplies a near-optimal construction to
seed the incumbent, and a partial set's lower bound (its sum so far, plus the smallest values the
remaining elements could take) kills most branches early. A bound that is cheap and loose usually
beats one that is tight and expensive, because it is evaluated at every node.

Watch the feasibility test, too. Problem 103's two solution variants run the *identical* search and
differ in one line — which of the two validity conditions is checked first, the $O(n^2)$ one or the
$O(2^n)$ one — and that single choice dominates the runtime. See
[order checks by cost](/topics/takeaway/cheap-checks-first).

**Prove structure and delete the search.** The best outcome is discovering the optimum has a shape,
after which you construct it rather than find it. Problem 222 minimises the length of a pipe
holding $21$ balls of different radii; the cost of adjacent balls is a *concave* function of their
radii, and concavity implies a large–small pairing is cheaper than two medium ones. That forces the
optimum into a "valley" — smallest ball in the middle, radii rising to both ends — and the
$21!$ orderings become an $O(n^2)$ DP. Problem 190 goes further: maximising $x_1x_2^2\cdots x_m^m$
subject to $\sum x_i = m$ is a [Lagrange
multiplier](https://en.wikipedia.org/wiki/Lagrange_multiplier) exercise whose stationarity condition
gives $x_i = 2i/(m+1)$ directly, and the search vanishes into a
[closed form](/topics/technique/closed-form-expression). See
[reduce algebraically before coding](/topics/takeaway/reduce-before-coding).

The structure can also describe *all* the optima rather than just one. Problem 336 runs a fixed
greedy [pancake-style](/topics/domain/pancake-sorting) sort on a train of carriages and asks about
the arrangements that force its worst case. A bound comes first: each placement costs at most two
reversals, so the worst case is $2n-3$. It is attained exactly when every placement finds its
carriage strictly inside the unsorted suffix. Filtering all $11!$ permutations against that
condition would work. The better observation is that the sort is deterministic, so you can
[run it backwards](/topics/takeaway/run-the-process-backwards): start from the sorted train and
undo each placement in every way that keeps it maximal. The choices are in bijection with the
maximisers, so the method *generates* the $(n-2)!$ optima and never visits anything else. The
count matches the statement's examples, a free check of the
theory ([calibrate on known answers](/topics/takeaway/calibrate-theory-on-known-answers)). If the
optimum set has a shape you can describe, building that set beats sifting for it.

Be careful here, and this is the domain's sharpest trap: a plausible structural intuition is not a
proof. Problem 222's optimum puts the two *largest* balls at the exposed ends, which reads as
backwards until you do the concavity argument. [Greedy](/topics/technique/greedy-algorithm) choices
feel right constantly and are correct only when an exchange argument says so; the
[knapsack problem](/topics/technique/knapsack-problem) is the standard demonstration that "take the
best-looking item next" is simply wrong. Verify a conjectured structure by brute-forcing the small
cases against it before you trust it at full size.

**When nothing bounds it, search stochastically — but carry a certificate.** Some instances offer
no useful bound and no exploitable structure. Problem 185's $10^{16}$ candidate strings are one:
the fix is to stop treating it as a search and treat it as minimisation. Define an energy — the
summed squared deviation between each clue's required match count and the candidate's actual one —
and run [simulated annealing](/topics/technique/simulated-annealing) on it, accepting worsening
moves with probability $e^{-\Delta E/T}$ so the search can climb out of local minima, with random
restarts when a run freezes.

What makes this respectable rather than hopeful is the certificate. The problem states the secret
is unique and consistent with every clue, so $E = 0$ holds *only* at the answer. The search may be
stochastic, but its stopping condition is a proof. That is the pattern to imitate whenever you
reach for a metaheuristic: find the property that makes a hit self-verifying. Without one, you have
a good guess and no way to know it.

## How to reason about it

The cue is a superlative — *minimum*, *maximum*, *shortest*, *optimum*, *best* — over a set of
discrete arrangements too large to enumerate. When you catch it:

- **Model first, then optimise.** Write down the feasible set, the objective, and the constraints
  explicitly. Then try to recognise the result: matching, clique, cover, packing, path, partition,
  scheduling. A named problem comes with algorithms and bounds attached.
- **Check whether it is actually hard.** Not every superlative implies a search. A minimum path
  through a grid of right/down moves is a shortest path in a DAG and falls to one DP sweep —
  `solutions/public/p0081/` does it in place, in $O(n^2)$, with no search at all. See
  [shortest path](/topics/domain/shortest-path-problem).
- **Find the state.** If a partial solution's future depends only on a small summary of it, you
  have a DP and probably an exact answer. Try this before any heuristic.
- **Get a feasible solution early.** Even a mediocre one is an incumbent, and an incumbent is what
  makes pruning possible. A greedy construction is usually the right seed.
- **Ask what stops the search.** Exhaustion, a matched bound, a structural argument, or a
  self-verifying certificate — one of these, decided up front. If you cannot name yours, you are
  writing a heuristic and should say so.
- **Brute-force the small cases anyway.** Not to reach the answer, but to validate a conjectured
  structure and to test the fast implementation against ground truth. Every structural shortcut on
  this page was checked that way first.

The recurring lesson is that the leverage is almost never in the search code. It is in the
observation made just before it — that order does not matter, that the cost function is concave,
that the constraint has a multiplier, that a global condition splits into a fan of local ones, that
a deterministic process can be run in reverse — each of which deletes more of the space than any amount of
optimisation inside the loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0185](/solutions/0185/) — Number Mind
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0252](/solutions/0252/) — Convex Holes
- ○ [0275](/solutions/0275/) — Balanced Sculptures
- ○ [0300](/solutions/0300/) — Protein Folding
- ○ [0327](/solutions/0327/) — Rooms of Doom
- ○ [0328](/solutions/0328/) — Lowest-cost Search
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ○ [0339](/solutions/0339/) — Peredur Fab Efrawg
- ● [0345](/solutions/0345/) — Matrix Sum
- ○ [0352](/solutions/0352/) — Blood Tests
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ○ [0406](/solutions/0406/) — Guessing Game
- ○ [0424](/solutions/0424/) — Kakuro
- ○ [0434](/solutions/0434/) — Rigid Graphs
- ○ [0453](/solutions/0453/) — Lattice Quadrilaterals
- ○ [0470](/solutions/0470/) — Super Ramvok
- ○ [0503](/solutions/0503/) — Compromise or Persist
- ○ [0534](/solutions/0534/) — Weak Queens
- ○ [0554](/solutions/0554/) — Centaurs on a Chess Board
- ○ [0594](/solutions/0594/) — Rhombus Tilings
- ○ [0667](/solutions/0667/) — Moving Pentagon
- ○ [0726](/solutions/0726/) — Falling Bottles
- ○ [0732](/solutions/0732/) — Standing on the Shoulders of Trolls
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ○ [0765](/solutions/0765/) — Trillionaire
- ○ [0775](/solutions/0775/) — Saving Paper
- ○ [0782](/solutions/0782/) — Distinct Rows and Columns
- ○ [0789](/solutions/0789/) — Minimal Pairing Modulo $p$
- ○ [0794](/solutions/0794/) — Seventeen Points
- ○ [0821](/solutions/0821/) — 123-Separable
- ○ [0828](/solutions/0828/) — Numbers Challenge
- ○ [0855](/solutions/0855/) — Delphi Paper
- ○ [0863](/solutions/0863/) — Different Dice
- ○ [0867](/solutions/0867/) — Tiling Dodecagon
- ○ [0871](/solutions/0871/) — Drifting Subsets
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ○ [0886](/solutions/0886/) — Coprime Permutations
- ○ [0887](/solutions/0887/) — Bounded Binary Search
- ○ [0893](/solutions/0893/) — Matchsticks
- ○ [0966](/solutions/0966/) — Triangle Circle Intersection
- ○ [1002](/solutions/1002/) — Connections II

<!-- /problems -->
