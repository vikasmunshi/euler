<!-- tags: [graph-coloring] -->
<!-- status: final -->
# Graph coloring

A [proper colouring](https://en.wikipedia.org/wiki/Graph_coloring) gives every vertex of a graph a
colour so that no edge joins two vertices of the same colour. Project Euler almost never asks
*whether* a graph can be coloured; it asks *how many ways* — and the graph is nearly always a long
thin thing: a strip, a triangular grid swept row by row, a chain of identical gadgets glued end to
end. That shape is the whole game. A count that looks like $q^{\text{huge}}$ brute force collapses
into a small state machine run along the long axis, and then colour symmetry usually shrinks the
machine further still.

## The idea: cut the graph where it is thin

Take a graph that is long in one direction and narrow in the other. Slice it across the long axis.
Whatever lies to the left of a cut can only influence what lies to the right through the vertices
*on* the cut — the colour of a vertex two columns back is invisible once its neighbours are fixed.
So the colouring of the cut is a complete summary of the past: a **state**. Counting then becomes:

1. enumerate the possible states of one cut;
2. for each pair of consecutive states $(s, s')$, count the ways $T[s][s']$ to colour the private
   vertices between the two cuts compatibly with both — the
   [transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) (see
   [transfer-matrix method](/topics/domain/transfer-matrix-method));
3. multiply: the count for a strip of $n$ pieces is $\mathbf{a}^{\mathsf T} T^{\,n-1} \mathbf{b}$, with
   $\mathbf{a}$ the ways to start and $\mathbf{b}$ the ways to finish.

That is [dynamic programming](/topics/technique/dynamic-programming) with the matrix written down.
The smallest worked example is the $2 \times n$ ladder (two rows of $n$ cells, edge-adjacent cells
must differ) with $q$ colours. A cut is one column, a state is an ordered pair $(t, b)$ with
$t \ne b$, and the next column $(t', b')$ needs $t' \ne t$, $b' \ne b$, $t' \ne b'$:

```python
def ladder(q, n):                       # proper q-colourings of the 2 x n grid
    states = [(t, b) for t in range(q) for b in range(q) if t != b]
    count = {s: 1 for s in states}      # first column: any valid pair
    for _ in range(n - 1):
        count = {(t2, b2): sum(c for (t, b), c in count.items() if t != t2 and b != b2)
                 for (t2, b2) in states}
    return sum(count.values())
```

Every step is $O(S^2)$ for $S$ states, and $n$ steps cost $O(nS^2)$ — linear in the length,
however long the strip. When $n$ itself is astronomical, replace the loop by
[matrix exponentiation](/topics/technique/matrix-exponentiation): $T^{\,n-1}$ by
[repeated squaring](/topics/technique/exponentiation-by-squaring) is $O(S^3 \log n)$.

## Where symmetry cuts the work

The state space above is wasteful: a proper colouring stays proper if you permute the colour names,
so the transfer counts out of $(0, 1)$ and out of $(2, 3)$ are identical. Two consequences recur.

**Row sums can be constant.** In the ladder, every state $(t, b)$ has exactly $q^2 - 3q + 3$
successors, whichever two colours it uses. A constant row sum means the all-ones vector is an
eigenvector of $T$, and the whole matrix power collapses to a scalar power:

$$\#\text{ladder}(q, n) = q(q-1)\,(q^2 - 3q + 3)^{\,n-1}.$$

(Check: $q = 3, n = 2$ gives $18$, the [chromatic polynomial](/topics/domain/chromatic-polynomial)
of the 4-cycle at $3$.) Problem 194 is this trick at full strength. Its configurations are chains
of two gadget types $A$ and $B$, seven vertices each, glued along shared vertical edges; the
interface is an ordered colour pair, and because any pair can be carried to any other by a colour
permutation, each gadget multiplies the running count by a single number — its row sum. The order
of the gadgets stops mattering, a binomial coefficient counts the arrangements, and a problem that
looks like $c(c-1)$-dimensional linear algebra becomes two closed-form scalars and a modular power.
The only real work is deriving each gadget's row sum, by splitting the far edge into equality
classes relative to the near one (which colours coincide, which are fresh) and weighting each class
by its size.

**Otherwise, quotient the states.** When row sums are not uniform, symmetry still lets you replace
*which colours* a state uses by *which coincidences* it has — the state becomes the equality
pattern of the cut (a [set partition](https://en.wikipedia.org/wiki/Partition_of_a_set)), and the
transfer weights become counts of admissible fresh colours ($q - k$ where $k$ colours are already
forbidden). Problem 670 shows the payoff. Its $2 \times n$ strip is tiled by horizontal tiles of
length 1–3 and vertical dominoes, four-coloured with edge-adjacent tiles differing. The naive
boundary state — each row's tile colour plus how far it still overhangs — runs to over a hundred
values; but the two tiles at a boundary always touch, so their colours are always distinct and
all such pairs are equivalent. Drop the colours, keep the overhangs: ten states, colour choices
folded into the weights as small integers (2, 3, 6), and a $10 \times 10$ matrix raised to the
power $10^{16}$ in about fifty squarings.

## When the cut is wide: contract it a cell at a time

The transfer matrix has $S^2$ entries, and $S$ grows exponentially with the width of the cut —
$q^w$ states for a width-$w$ boundary. Problem 189 (a triangular grid of $n^2$ small triangles,
three colours) is the cautionary case: sweep row by row, and row $r$'s state is the colouring of its
$r$ upward-pointing triangles, $3^r$ states. A full row-to-row matrix at the bottom is millions of
pairs, each with an $r$-term product. Two observations rescue it:

- **Local independence.** Within a row the downward triangles never touch each other; once the
  upward triangles above and beside them are fixed, each downward triangle independently has
  "colours not in $\{a, b, d\}$" choices. The transfer weight factorises into a product of tiny
  per-column factors.
- **Per-column contraction.** A product of per-column factors means the sum over the old row can be
  done *one column at a time*: carry a mixed state holding the new row's colours to the left of a
  pointer and the old row's to the right, and advance the pointer, summing out one old cell per
  step. This is the [broken-profile](/topics/domain/broken-profile) idea from tiling DP, and it
  turns $S^2$ work per row into roughly $S \cdot q$ per column.

So the decision ladder for a colouring count is: find the thin direction; take the cut's colouring
as state; quotient by colour permutations; if the row sums turn out constant, collapse to a scalar;
if the length is huge, exponentiate the matrix; if the width is large, contract cell by cell
rather than row by row.

## Pitfalls

- **Pin the adjacency model before counting.** "Sharing an edge" versus "touching at a corner",
  whether a gadget's bottom edge exists, whether the first and last columns wrap around. Problem
  671 is 670 on a loop with $k$ colours: closing the strip turns the end-to-end product into a
  *trace* $\operatorname{tr} T^{\,n}$ — but a colour-quotiented state has forgotten *which* colours
  meet at the seam, so the quotient must keep enough of them to check the wrap-around. Every solution here was checked against a brute-force enumerator on small
  sizes — for the triangular grid, $3, 24, 528$ colourings for $n = 1, 2, 3$ — before the fast
  method was trusted.
- **Quotienting changes the boundary vectors.** Once states are equality patterns, the start vector
  must count how many concrete colourings each pattern stands for (670 starts its two-row states at
  $4 \cdot 3 = 12$, its single-domino state at $4$), or the totals come out scaled wrong.
- **Constant row sums are a theorem, not a hope.** They hold when the colour-permutation group
  acts transitively on the states — every interface colouring equivalent to every other. With a
  wider cut (three mutually non-adjacent vertices can be all-equal or all-distinct) that fails, and
  you need the quotient matrix instead.
- **Watch the modulus.** These counts dwarf 64 bits within a few dozen columns. Reduce after every
  product, and remember that a composite modulus such as $10^8$ shares factors with factorials, so
  binomials must be built additively (Pascal's triangle) rather than by modular inverse.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0194](/solutions/0194/) — Coloured Configurations
- ○ [0519](/solutions/0519/) — Tricoloured Coin Fountains
- ○ [0544](/solutions/0544/) — Chromatic Conundrum
- ○ [0554](/solutions/0554/) — Centaurs on a Chess Board
- ● [0670](/solutions/0670/) — Colouring a Strip
- ○ [0671](/solutions/0671/) — Colouring a Loop
- ○ [0677](/solutions/0677/) — Coloured Graphs
- ○ [0857](/solutions/0857/) — Beautiful Graphs
- ○ [0892](/solutions/0892/) — Zebra Circles
- ○ [1002](/solutions/1002/) — Connections II

<!-- /problems -->
