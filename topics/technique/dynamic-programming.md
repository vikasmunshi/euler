<!-- tags: [dynamic-programming] -->
<!-- status: final -->
# Dynamic programming

[Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) (DP) solves a
problem by solving its smaller subproblems once, storing each answer, and building the
larger answers out of the stored ones. It is the tool for a specific shape of problem —
one where a brute-force search would recompute the same subproblem an exponential number
of times — and that shape recurs constantly in Project Euler: counting the ways to do
something, finding a best path, filling a grid, or evaluating a game position.

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
answers.

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

## How to reason about it

The work is almost entirely in **choosing the state**: the smallest set of variables
that fully describes a subproblem. Get the state right and the recurrence and the loop
order usually fall out; get it wrong — omit a variable the answer actually depends on —
and you have silently broken the optimal-substructure property. Once the state is fixed:

- **Evaluation order.** Bottom-up needs the dependencies of each state filled before it.
  A grid of right/down moves fills by rows or by anti-diagonals; a path-in-a-triangle
  fills from the bottom row up, so each cell already knows the best path below it
  (`solutions/public/p0018/`, and the 100-row `solutions/public/p0067/` that would defeat
  brute force). When the order is awkward to state explicitly, top-down memoization
  sidesteps it — the recursion visits dependencies first by construction.
- **Shrink the table.** If each state depends only on the previous row or the last few
  states, you do not need the whole table — keep a rolling row (the coin loop above keeps
  exactly one), or overwrite the grid in place, as the right/down min-path sum does
  (`solutions/public/p0081/`). When the moves are richer the state changes shape rather
  than just shrinking: allowing vertical detours too (`solutions/public/p0082/`) turns
  each column into its own one-dimensional minimisation, a reminder that the state must
  match the moves the problem actually allows.
- **Build it inside `solve()`.** The table, cache, or memo dict must be constructed on
  each call, sized to the inputs — not kept warm at module level. With `--runs=N` the
  harness times repeated `solve()` calls, and a cache that survives between runs makes
  every run after the first look free, understating the real cost.

The tell that a problem wants DP is a brute force that is correct but times out because
it re-explores the same partial states — a path halfway down a grid, an amount partway
made, a game position seen before. When you notice that, name the state, decide top-down
or bottom-up, and the exponential search collapses to a table. The problems below are all
that collapse in one guise or another.

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
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0301](/solutions/0301/) — Nim
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0679](/solutions/0679/) — Freefarea
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0710](/solutions/0710/) — One Million Members
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0961](/solutions/0961/) — Removing Digits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
