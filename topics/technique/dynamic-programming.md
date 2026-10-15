<!-- tags: [dynamic-programming] -->
<!-- status: final -->
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

## How to reason about it

The work is almost entirely in **choosing the state**: the smallest set of variables
that fully describes a subproblem. Get the state right and the recurrence and the loop
order usually fall out; get it wrong — omit a variable the answer actually depends on —
and you have silently broken the optimal-substructure property. The state is a
*sufficient summary*, not the configuration: in 253 the set of placed pieces is
exponential, but given the history the empty cells are a uniform composition across the
gaps, so (pieces placed, segment count, which end gaps survive) carries everything the
next step's odds depend on. Once the state is fixed:

- **Evaluation order.** Bottom-up needs the dependencies of each state filled before it.
  A grid of right/down moves fills by rows or by anti-diagonals; a path-in-a-triangle
  fills from the bottom row up, so each cell already knows the best path below it
  (`solutions/public/p0018/`, and the 100-row `solutions/public/p0067/` that would defeat
  brute force). The order can be geometric: the largest empty convex polygon (252) is the
  Dobkin–Edelsbrunner–Overmars sweep, whose
  states are the last edge of a convex chain fanned from its lowest vertex, filled in
  angular order. When the order is awkward to state explicitly, top-down memoization
  sidesteps it — the recursion visits dependencies first by construction.
- **Price the transitions, not just the states.** Total cost is states × transitions per
  state. In 252 the predecessors that keep a chain convex form a prefix of an angularly
  sorted list, so a running maximum over that list answers each state's "best
  predecessor" in amortised constant time — `O(n³)` instead of `O(n⁴)`.
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
  small dimension (players) while a closed form absorbs the large one (days).
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
- ● [0301](/solutions/0301/) — Nim
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0679](/solutions/0679/) — Freefarea
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0710](/solutions/0710/) — One Million Members
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0961](/solutions/0961/) — Removing Digits
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0996](/solutions/0996/) — Overtakes
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
