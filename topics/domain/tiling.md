<!-- tags: [tiling] -->
<!-- status: final -->
# Tiling

A [tiling](https://en.wikipedia.org/wiki/Tessellation) covers a region with pieces that don't
overlap and leave no gaps. Project Euler comes back to it again and again because one simple
picture (fill this board with these pieces) can hide very different problems. Most of the
problems below ask *how many* tilings there are. A few ask whether a tiling exists at all, and a
few use a fixed tiling as a coordinate system for a question about something else. What links
them is the property that makes tilings countable: **a piece only interacts with the pieces it
touches.** Every technique on this page uses that locality in some way.

## The idea: cover exactly once, decide in a fixed order

A tiling is an [exact cover](/topics/technique/exact-cover): each cell of the board must be
covered by exactly one piece. Counting exact covers by search is hopeless at Project Euler sizes,
and the search also overcounts. Place pieces in arbitrary order and the same tiling shows up once
for every order in which you could have laid it down.

The fix, and the first idea to learn here, is to put a **canonical order** on the decisions:

> Always cover the *first* uncovered cell, in a fixed scan order.

Every piece you try must then contain that cell. Each finished tiling is reached by exactly one
sequence of choices, so the count is correct by construction and no deduplication is needed. In
one dimension the rule turns into a recurrence straight away. In problem 117 a row of length $n$
is tiled with pieces of length 1 to 4, and you classify each tiling by the piece that covers the
last cell:

$$T(n) = T(n-1) + T(n-2) + T(n-3) + T(n-4), \qquad T(0) = 1.$$

The four cases are disjoint and together cover every tiling, so the counts simply add. Problems
115 and 116 use the same skeleton with different piece rules, such as a minimum block length or a
gap between blocks. Problem 440 takes the same kind of strip recurrence as its starting point and
then asks a number-theoretic question about its values. Its count satisfies a linear recurrence,
and gcd identities of Fibonacci-like sequences carry the problem from there.

## Two dimensions: the frontier is the state

On a wider board you can't classify by "the last piece" directly, but the canonical order still
works if you remember the right amount. Scan the board cell by cell. Pieces you've already placed
only stick out a short distance ahead of the scan position, so whether the rest of the board can
be finished depends only on **which cells in a thin frontier are already filled**. That frontier
fits in a bitmask, and the pair (position, mask) becomes a
[dynamic-programming](/topics/technique/dynamic-programming) state:

```python
if mask & 1:                       # current cell already filled by an earlier piece
    return count(pos + 1, mask >> 1)
# otherwise: try each piece anchored at this cell, set its bits, recurse on (pos + 1, new_mask >> 1)
```

This is the [broken-profile](/topics/domain/broken-profile) DP, and problem 161 (triominoes on a
rectangle) is the clearest example. Two engineering details matter. The mask must reach as far
ahead as the tallest piece. And since the state count grows exponentially in the profile width,
**always scan along the shorter side**: transposing the board doesn't change the count.

A coarser version works when the board breaks into whole rows or layers. Problem 215 enumerates
every way to tile a single row of bricks and encodes each row as a bitmask of its internal seams.
"No running crack" between two stacked rows then becomes `a & b == 0`, and the wall count is a
layered walk over the compatibility graph of rows. This is the
[transfer-matrix method](/topics/domain/transfer-matrix-method): states are row profiles, the
matrix entries say which profiles may be adjacent, and an $H$-layer count is a power of that
matrix. Problems 670 and 671 use the same structure for a $2 \times n$ strip with colour and
corner constraints. Problem 671 closes the strip into a loop, and the count becomes a *trace* of
the matrix power rather than a sum over its entries. Problem 324 asks for a $3 \times 3 \times n$
tower at a height of $10^{10000}$. No table reaches that, but the transfer matrix is small and
fixed, so [matrix exponentiation](/topics/technique/matrix-exponentiation) (or the
[linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients) it satisfies)
gets there in a logarithmic number of steps.

## When the tiling is a lens, not a count

Some problems on this list barely count anything. Here the tiling either gives the problem its
geometry or sets a condition that has to be turned into number theory.

- **The tiling as a coordinate system.** Problem 128 numbers the cells of a
  [hexagonal lattice](/topics/domain/hexagonal-lattice) in a spiral and asks about differences
  between neighbours. The work is writing a tile's six neighbours in closed form for ring $k$,
  which rules out every position except two per ring. Problem 979's frog walks on the hyperbolic
  $\{7,3\}$ tiling, where it is the adjacency structure that matters, not area.
- **Tileability as a divisibility test.** In problem 139, four copies of a
  [Pythagorean triangle](/topics/domain/pythagorean-triple) leave a square hole, and the
  $c \times c$ square can be tiled by copies of that hole exactly when $|a-b|$ divides $c$. The
  geometry reduces to one modulus check, and then to
  [Pell's equation](/topics/technique/pells-equation).
- **Tileability as a pattern found from data.** Problem 256 asks which rooms have no tatami
  tiling (no point where four mats meet). A row-by-row exhaustive checker run on small rooms shows
  a clean band structure in the bad lengths. Once that structure is written down, a single room
  is an $O(1)$ test, and the problem becomes counting divisor pairs. This is
  [small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence) in its
  purest form.
- **Self-similar and greedy tilings.** Problem 247 packs squares greedily under $y = 1/x$. Each
  square splits the remaining region into two independent pieces of the same shape, so the packing
  is a binary tree you can prune by size. Problem 405's substitution tiling is self-similar too,
  so its four-corner count follows a recurrence across generations rather than across space.

Problems 594, 867 and 780 (rhombus tilings of octagons, dodecagons tiled by regular polygons,
triangulated tori) are the same counting problem on non-square lattices. A frontier-and-profile
state still works, but deciding what the frontier *is* gets much harder.

## How to reason about it

- **Fix a canonical order first.** "Cover the first empty cell" is what makes a count correct
  rather than an overcount. If your search can place the same piece set in two different orders,
  your answer will be too large.
- **Ask what the future depends on.** For a strip, it's the remaining length. For a rectangle,
  it's a frontier mask. For a stack of layers, it's the previous layer. That summary is your memo
  key, and it has to be *complete* (see
  [the memo key is the full state](/topics/takeaway/memo-key-is-the-full-state)). A constraint
  like "no four corners meet" may need extra bits in the state beyond occupancy.
- **Choose the narrow dimension.** Profile DP costs grow exponentially in the profile width and
  linearly in the length.
- **When the length is astronomical, look for the matrix.** A fixed transfer matrix means a
  linear recurrence, which means $O(\log n)$ by exponentiation, usually modulo a prime given in
  the problem.
- **Closed loops and symmetry change the bookkeeping.** A cylinder or torus needs a trace or
  explicit wrap-around states. Problems that count rotated tilings as distinct (most of them, as
  the statements spell out) let you skip [symmetry reduction](/topics/takeaway/exploit-symmetry).
  When they don't, you need Burnside's lemma.
- **Check against small boards.** Every one of these problems gives small values. A brute-force
  tiler that reproduces them is the cheapest way to test a clever state encoding, and its output
  is often the best route to a formula.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0161](/solutions/0161/) — Triominoes
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0338](/solutions/0338/) — Cutting Rectangular Grid Paper
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0594](/solutions/0594/) — Rhombus Tilings
- ○ [0670](/solutions/0670/) — Colouring a Strip
- ○ [0671](/solutions/0671/) — Colouring a Loop
- ○ [0766](/solutions/0766/) — Sliding Block Puzzle
- ○ [0780](/solutions/0780/) — Toriangulations
- ○ [0867](/solutions/0867/) — Tiling Dodecagon
- ○ [0979](/solutions/0979/) — Heptagon Hopping

<!-- /problems -->
