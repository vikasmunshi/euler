<!-- tags: [dynamic-programming] -->
<!-- status: final 2026-11-09T07:05Z -->
# Dynamic programming

[Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) (DP) solves a
problem by solving its smaller subproblems once, storing each answer, and building the
larger answers out of the stored ones. It is the tool for a specific shape of problem —
one where a brute-force search would recompute the same subproblem an exponential number
of times — and that shape recurs constantly in Project Euler: counting the ways to do
something, finding a best path, filling a grid, pushing probability through a random
process, or evaluating a game position.

## When it applies — two properties

A problem yields to DP when it has both of these:

- **Overlapping subproblems** — the naive recursion asks the same smaller question over
  and over. The number of *distinct* questions is small (polynomial), even though the
  recursion tree that asks them is huge. DP pays for each distinct question once.
- **Optimal substructure** — the answer to a problem is built from the answers to its
  subproblems by a fixed rule. "The best path to this cell is this cell's value plus the
  better of the two paths into it" is optimal substructure; so is "the number of ways to
  make *n* is the sum of the ways that use each coin."

If a subproblem's answer can change depending on *how* you reached it, the substructure
is not there and DP does not apply — that is the usual reason an attempted DP gives wrong
answers. For a random process the same requirement has a familiar name, the
[Markov property](https://en.wikipedia.org/wiki/Markov_property): the future may depend on
the state, never on the path that led to it.

## The two forms

The same recurrence can be filled two ways.

**Top-down (memoization).** Write the natural recursion, then cache its results keyed on
the arguments. The first call for a given state computes it; every later call reads the
cache. This is the smallest change to a brute-force solution — often a single decorator —
and it only ever computes the states the problem actually reaches.

**Bottom-up (tabulation).** Order the states so that every state's dependencies come
before it, then fill a table in that order with a loop. No recursion, no call-stack
limit, and the table's memory is explicit and easy to shrink.

Coin Sums (`solutions/public/p0031/`) is the recurrence at its cleanest — count the
unordered ways to make an amount from a set of coins, bottom-up:

```python
result = [1] + [0] * target_amount
for coin in coins:
    for i in range(coin, target_amount + 1):
        result[i] += result[i - coin]
return str(result[-1])
```

`result[i]` is the number of ways to make amount `i`. The two loops encode the whole
idea: putting `coins` on the outside and sweeping amounts upward counts *combinations*
rather than permutations (each coin's contribution is folded in once), and the upward
sweep is what lets a coin be reused any number of times. It runs in
`O(coins · amount)` time and `O(amount)` space — a single row, reused.

Flip the sweep and the meaning flips with it. Sweeping amounts **downward** reads only
values from before the current item was considered, so each item is used at most once —
the [0/1 knapsack](https://en.wikipedia.org/wiki/Knapsack_problem). Problem 249 is exactly
that: the number of subsets of the primes below a bound with each possible sum is the
coefficient list of `∏(1 + x^p)`, built one prime at a time. In numpy the whole sweep is
one overlapping slice update, `ways[w:] += ways[:-w]`, which numpy evaluates as if the
right-hand side were copied first — the downward-sweep semantics without the loop. With
counts this large the row is kept modulo a bound, and the reduction is batched only as
often as the `uint64` headroom requires: each add at most doubles a count.

Both forms *pull*: a state reads the states it depends on. A Markov chain is often easier
to *push* — walk the states in time order and send each state's probability forward along
its transitions. Problem 253 (a caterpillar assembled from randomly placed pieces) runs
that forward pass, one placement at a time.

## What a table entry can hold

The coin loop stores a count, but nothing about the method requires it. The entry is
whatever the recurrence combines, as long as the combining rule is fixed:

- **A probability, or a whole distribution.** In 253 each state carries the probability of
  being there; tracking the *running maximum* as one more coordinate turns "the expected
  peak" into a distribution over peaks, read off the final row.
- **A polynomial.** When the question asks for counts at every total of some secondary
  quantity, make each entry a [generating function](https://en.wikipedia.org/wiki/Generating_function)
  in that quantity and let the transitions multiply by powers of `y`. Problem 996
  (overtakes on a leader board) runs a position-by-position DP over a handful of
  polynomial-valued states, so a single pass counts the tuples at every number of
  overtakes at once — and the problem's huge day count never enters the DP, only a final
  binomial sum over the polynomial's coefficients.
- **A max (or min) instead of a sum.** Problem 395 bounds a Pythagorean tree by its
  [support function](https://en.wikipedia.org/wiki/Support_function) in four directions:
  each subtree's reach is the max of the square's own reach and its two children's,
  rotated and scaled. The recursion is infinite, so the DP runs over depth and is
  truncated — once with a tail that under-reaches (the square alone) and once with one
  that over-reaches (an invariant disk), which brackets the exact answer within a
  tolerance you choose.
- **A game value.** In the bit- and trit-removal games (882, 963) each number's
  [combinatorial game value](https://en.wikipedia.org/wiki/Surreal_number) is the simplest
  number strictly between its best Left option and its best Right option. Deleting a digit
  always gives a smaller number, so the values fill bottom-up in plain index order — stored
  as fixed-point integers, since they are dyadic rationals. Because values *add* over a
  sum of games, a position with thousands of piles is settled by a sum of table lookups.
  The Fibonacci Tree Game (400) adds a second layer. Its tree has more nodes than
  there are atoms in the universe, but only `k` distinct subtree *shapes*, and every
  node's [Grundy value](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
  stays small. So the DP works with pairs (shape, target value). It counts the moves
  inside a shape that leave its root at each value, which turns "how many winning first
  moves" into a vector per level, pushed down two levels at a time.
- **A saturated count.** When the question is only "is there exactly one?", as in Special
  Partitions (333), the counts can be capped at 2. Adding non-negative numbers keeps "none,
  one, many" correct, so each entry fits in a byte and overflow cannot happen.
- **A yes/no at a level, instead of a minimum.** Flexible Digit Sum (637) defines `f(n)` as
  the fewest split-and-sum steps that bring `n` down to one digit. Taking a minimum over
  all `2^(L−1)` splits for each number is too expensive, but `f` never goes above 3. So
  the solution asks a weaker question one level at a time: is `f(n) ≤ t`? That holds as
  soon as *one* split lands on a number already known to be at level `t − 1`, so a single
  witness settles each entry, and a bitset filter finds that witness for almost every
  number.
- **A count and a running total, side by side.** Non-attacking Frogs (988) asks for the sum
  of positions over all valid configurations, not their number. Each entry carries a pair:
  how many configurations end at this cell, and the total of their positions. Appending a
  cell to `cnt` configurations adds its own position once to each, so
  `sum ← sum + g·cnt` rides along with the count update. Any additive statistic of the
  objects being counted can be carried this way, one extra moment per entry.
- **A signed term of an inclusion–exclusion.** Straight Eight (987) counts eight disjoint
  straights, none of them a flush. "Not a flush" ties all five ranks of a straight
  together, which no rank-by-rank state can see. So the DP does not enforce it. It sums
  over sets of straights *forced* to be flushes, with sign `(−1)^|F|`, and once those are
  fixed the count factorises rank by rank. The table holds signed weights, and the
  [inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
  cancellation happens in the final sum. The general move: when a constraint is global,
  turn its negation into a summed-over choice and let the DP carry the sign.
- **A cost on a DAG — a shortest path.** In 995 the smallest integer whose divisors
  factor a cyclic group is built along a chain of subgroups, and each step's cost is
  fixed by the step. The states are the divisors of `p − 1`, every step goes to a proper
  multiple, so filling them in increasing order relaxes every edge once: a
  [shortest path in a DAG](https://en.wikipedia.org/wiki/Shortest_path_problem#Directed_acyclic_graphs)
  is a min-plus DP. The integers involved have hundreds of thousands of digits, so the
  entries hold `ln` of the product rather than the product: a multiplicative cost becomes
  an additive one, and the path never has to build the number it minimises.

## How to reason about it

The work is almost entirely in **choosing the state**: the smallest set of variables
that fully describes a subproblem. Get the state right and the recurrence and the loop
order usually fall out; get it wrong — omit a variable the answer actually depends on —
and you have silently broken the optimal-substructure property. The state is a
*sufficient summary*, not the configuration: in 253 the set of placed pieces is
exponential, but given the history the empty cells are a uniform composition across the
gaps, so (pieces placed, segment count, which end gaps survive) carries everything the
next step's odds depend on. Four more ways to find the state:

- **Keep only what the condition compares.** A *digit DP* walks a number one column at a
  time. In Digital Signature (290) the condition is `s(n) = s(137n)`, and long
  multiplication makes each output digit depend only on the current digit and the incoming
  carry. Two prefixes with the same carry and the same running *difference* of digit sums
  have the same future. Tracking that difference, rather than both sums, turns a 3-D state
  into a 2-D one, and `10^18` candidates become a few million table updates.
- **Condition on the event that splits the problem.** Tidying Up B (866) uses the same
  random caterpillar as 253, but now it asks for the expected *product* of the segment
  scores. Pushing forward through time would have to carry that product along. Look at the
  *last* piece placed instead. Before it goes down, no segment can cross its position, so
  the pieces to its left and right form two independent smaller caterpillars. The
  expectation then factorises into a [Catalan](https://en.wikipedia.org/wiki/Catalan_number)-style
  self-convolution, `E(N) = (2N−1) Σ E(i)·E(N−1−i)`, which fills bottom-up in `O(N²)`.
  This is the move behind interval DP in general: choose the step that cuts a problem
  into independent pieces, and the recurrence follows.
- **Count the interchangeable things by class.** Music Festival (475) partitions musicians
  into trios that never reuse a quartet. Tracking which people remain is exponential. A
  [double-counting](https://en.wikipedia.org/wiki/Double_counting_(proof_technique)) step
  first reduces the question to 0/1 matrices with fixed row and column sums. The matrix is
  then filled one row at a time. Columns with the same number of ones are
  interchangeable, so the state is the *histogram* of column fill levels, not the columns
  themselves, and the row and column-sum invariants leave only two free counters. Each
  transition picks how many of the new ones land on each fill level, weighted by a
  product of binomials. Whenever the objects are interchangeable, the state should count
  how many sit in each class, not name them.
- **Build from the objects already counted.** Peerless Trees (936) counts unlabelled
  trees in which adjacent vertices have different degrees. A rooted tree is a root plus a
  *multiset* of smaller rooted trees, so the table of trees of size `< m` is the stock
  of items for a bounded knapsack that produces the trees of size `m`. Choosing `j` copies
  from `b` kinds contributes the
  [multiset coefficient](https://en.wikipedia.org/wiki/Multiset#Counting_multisets)
  `C(b+j−1, j)`, not `b^j`, which is what keeps unlabelled trees from being counted once
  per ordering. The degree condition is local, so the root's child count is the only
  extra coordinate. [Otter's theorem](https://en.wikipedia.org/wiki/Otter%27s_dissimilarity_theorem)
  then turns rooted counts into unrooted ones. The table feeds itself: each size's output
  becomes the next size's input.

Once the state is fixed:

- **Evaluation order.** Bottom-up needs the dependencies of each state filled before it.
  A grid of right/down moves fills by rows or by anti-diagonals; a path-in-a-triangle
  fills from the bottom row up, so each cell already knows the best path below it
  (`solutions/public/p0018/`, and the 100-row `solutions/public/p0067/` that would defeat
  brute force). The order can be geometric: the largest empty convex polygon (252) is the
  Dobkin–Edelsbrunner–Overmars sweep, whose
  states are the last edge of a convex chain fanned from its lowest vertex, filled in
  angular order. When the order is awkward to state explicitly, top-down memoization
  sidesteps it — the recursion visits dependencies first by construction. The order can
  also be what makes vectorising possible. In 333 every entry for `n` reads only indices
  below `n/2`, so a whole block `[2^k, 2^(k+1))` depends only on earlier blocks and can be
  filled in one NumPy step. That replaces a Python loop over `n` with `log₂ N` array
  operations.
- **Price the transitions, not just the states.** Total cost is states × transitions per
  state. In 252 the predecessors that keep a chain convex form a prefix of an angularly
  sorted list, so a running maximum over that list answers each state's "best
  predecessor" in amortised constant time — `O(n³)` instead of `O(n⁴)`. In 988 the valid
  configurations are exactly the antichains of a staircase-shaped grid, so each cell sums
  over a quadrant "earlier rows, later columns". Per-column accumulators over finished
  rows, scanned with a running suffix sum, answer that 2-D range in `O(1)` per cell.
- **Compute only the states somebody reads.** Connections I (1001) counts the sets of
  pairwise non-crossing arcs: an interval DP `C_r[l]` over every range `[l, r]`, which is
  `N²` states for `N = 40 000`. Tracing which entries the recurrence actually reads shows
  that only one column per right end is ever needed, and each only down to its left end.
  That cuts the work to the sum of the interval lengths. The needed columns are also
  independent of each other. So the Python solution sweeps `l` once per *block* of 512
  columns and updates the whole block as a NumPy vector. Instead of storing the full
  table, it keeps a snapshot of the block's row at each right end until the matching left
  end consumes it.
- **Shrink the table.** If each state depends only on the previous row or the last few
  states, you do not need the whole table — keep a rolling row (the coin loop above keeps
  exactly one), or overwrite the grid in place, as the right/down min-path sum does
  (`solutions/public/p0081/`). When the moves are richer the state changes shape rather
  than just shrinking: allowing vertical detours too (`solutions/public/p0082/`) turns
  each column into its own one-dimensional minimisation, a reminder that the state must
  match the moves the problem actually allows.
- **Let the DP do only the hard part.** A table is the right tool for the tangled slice of
  a count, not necessarily for all of it. Top Dice (240) classifies each roll by its
  pivot — the value of the last die in the top group — so a small ordered-sum DP counts
  the dice above it while a multinomial and a power count the rest. In 951 a short
  argument first reduces "the deck is fair" to "some run has length exactly 2", and the DP
  then only counts run-length compositions that avoid it. And in 996 the DP runs over the
  small dimension (players) while a closed form absorbs the large one (days). Cribbage
  (928) uses the DP as one stage inside a search. A depth-first enumeration of rank counts
  carries a subset-sum table for the fifteens along the path, so each node does one
  knapsack step that all its children share. A meet-in-the-middle split at the 9–10
  boundary joins the two halves on a small interface, because the ten-valued cards
  touch the low cards only through that table and the open run.
- **Stop the table early when the recurrence is linear.** In 5-Smooth Pairs (682) a small
  knapsack table gives the first 81 terms of the count, and then the DP's job is done.
  Those terms show that the generating function is rational with a known denominator of
  degree 40. The solution checks this by asserting that the higher coefficients cancel,
  and then the [Bostan–Mori](https://arxiv.org/abs/2008.08822) halving step extracts the
  `n`-th coefficient in `O(d² log n)`. A DP whose rows follow a constant-coefficient linear
  recurrence does not have to be filled all the way to `n`.
- **Build it inside `solve()`.** The table, cache, or memo dict must be constructed on
  each call, sized to the inputs — not kept warm at module level. With `--runs=N` the
  harness times repeated `solve()` calls, and a cache that survives between runs makes
  every run after the first look free, understating the real cost.

The tell that a problem wants DP is a brute force that is correct but times out because
it re-explores the same partial states — a path halfway down a grid, an amount partway
made, a game position seen before, a random process in a configuration that only differs
by details the future cannot see. When you notice that, name the state, decide what an
entry holds and which direction to fill, and the exponential search collapses to a table.
The problems below are all that collapse in one guise or another.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0031](/solutions/0031/) — Coin Sums
- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0161](/solutions/0161/) — Triominoes
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0205](/solutions/0205/) — Dice Game
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0220](/solutions/0220/) — Heighway Dragon
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0232](/solutions/0232/) — The Race
- ● [0240](/solutions/0240/) — Top Dice
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0290](/solutions/0290/) — Digital Signature
- ● [0301](/solutions/0301/) — Nim
- ● [0333](/solutions/0333/) — Special Partitions
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ● [0475](/solutions/0475/) — Music Festival
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0679](/solutions/0679/) — Freefarea
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0710](/solutions/0710/) — One Million Members
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0866](/solutions/0866/) — Tidying Up B
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0923](/solutions/0923/) — Young's Game B
- ● [0928](/solutions/0928/) — Cribbage
- ● [0936](/solutions/0936/) — Peerless Trees
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0949](/solutions/0949/) — Left vs Right II
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0961](/solutions/0961/) — Removing Digits
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0987](/solutions/0987/) — Straight Eight
- ● [0988](/solutions/0988/) — Non-attacking Frogs
- ● [0990](/solutions/0990/) — Addition Equations
- ● [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ● [0996](/solutions/0996/) — Overtakes
- ● [1000](/solutions/1000/) — Problem $1000$
- ● [1001](/solutions/1001/) — Connections I

<!-- /problems -->
