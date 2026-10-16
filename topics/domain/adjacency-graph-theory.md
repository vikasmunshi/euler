<!-- tags: [adjacency-graph-theory] -->
<!-- status: final 2026-10-16T07:30Z -->
# Adjacency (graph theory)

Two vertices are [adjacent](https://en.wikipedia.org/wiki/Adjacency_(graph_theory)) when an edge
joins them; that is the whole definition. None of the problems below gives you a graph, though.
They give you triangles that "neighbour", ants that step to an "adjacent square", black cells
"sharing an edge", a knight and a horse with the same move, tennis players of "adjacent rank". Each
one hides a graph inside a rule about who touches whom, and the rule nearly always decides two
things: whether you have modelled the problem correctly, and how much state a fast algorithm has
to carry.

## The relation is the model

The first job is to write the adjacency relation down exactly, because the statements are precise
in ways that are easy to skim past:

- **Edge, not vertex.** Problem 189 colours a triangular grid so that neighbours differ, and says
  outright that triangles sharing only a corner are *not* neighbours. Read it the other way and
  you are counting colourings of a different, denser graph, and getting a different number.
- **Boundaries thin the degree.** In problem 393 an interior square of the grid has four
  neighbours, an edge square three and a corner two. The grid graph is not regular, and any
  formula that assumes four neighbours everywhere is wrong at the rim.
- **The same displacement can give two relations.** Problem 984 sets up the knight and the Chinese
  horse with identical move vectors. Knight adjacency is fixed by the board. Horse adjacency also
  depends on *occupancy*, because a piece on the orthogonal square blocks the move. One problem,
  one board, two graphs, and the question ("knight-connected" but "horse-disjoint") is about how
  they interact.
- **A one-dimensional board is a path.** In problem 996 a match is only ever played between
  adjacent ranks, so every overtake is an
  [adjacent transposition](https://en.wikipedia.org/wiki/Transposition_(mathematics)): a swap
  along an edge of the path graph $1 - 2 - \cdots - n$.

In code you almost never build this graph as an
[adjacency matrix](https://en.wikipedia.org/wiki/Adjacency_matrix) or an
[adjacency list](https://en.wikipedia.org/wiki/Adjacency_list). The adjacency *is* a function, a
`neighbours(cell)` generator that applies the move vectors and clips at the border:

```python
def neighbours(r, c, rows, cols):
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if 0 <= r + dr < rows and 0 <= c + dc < cols:
            yield r + dr, c + dc
```

All the mistakes listed above end up inside that function. So check it once against a
brute-force enumeration on tiny instances before anything fast is built on it. Problem 189's
solution does exactly that: a backtracking solver on grids of side $1$ to $5$ "pins down the
adjacency model" before the real algorithm is trusted. When the statement includes a small
example, such as problem 393's $f(4) = 88$ or problem 701's $E(2,2)$, that example tests your
relation more than it tests your algorithm.

## Locality is what makes it tractable

Adjacency in these problems is *local*: a cell touches only cells within a fixed, small distance.
That locality is the lever. Sweep the structure in some order, say row by row, and at any moment
only a thin **frontier** of already-placed vertices can still have edges to vertices you have not
placed yet. Everything behind the frontier is finished. Its influence on the future goes only
through the frontier, so it can be summarised as a count indexed by the frontier's state. This is
the [transfer-matrix method](/topics/domain/transfer-matrix-method), and it is
[dynamic programming](/topics/technique/dynamic-programming) where the state is the boundary.

The cost is decided by what one frontier state has to record. That is fixed by the question, not
by the graph:

| What the question asks about | What the frontier must remember |
| --- | --- |
| a local constraint (proper colouring, no two adjacent pieces) | each frontier vertex's label |
| a bijection along edges (every ant moves to a neighbour) | which frontier squares are already sources or targets |
| [connectivity](/topics/domain/component-graph-theory) (largest connected region, connected sets) | a *partition* of the frontier into components, plus their sizes |

Problem 189 sits in the first row and shows the extra structure that adjacency can add. In each
row of the triangular grid the downward-pointing triangles are mutually non-adjacent: each one
touches only upward triangles. So once the upward triangles of two consecutive rows are fixed,
every downward triangle has exactly three constrained neighbours and is *independent* of all the
others. The count for that row then factors into a product of small per-triangle terms instead of
a joint enumeration. Problem 189's solution builds its row-to-row transfer on this, and then
contracts it one column at a time, as a [tensor network](/topics/technique/tensor-network), so the
working set never exceeds $3^n$. A non-adjacency, an *absent* edge, is often the most useful
structural fact you can find.

Problem 393 is the second row. Since every ant moves and no two land together, the moves form a
permutation in which each ant goes to an adjacent square, a
[cycle cover](https://en.wikipedia.org/wiki/Vertex_cycle_cover) of the grid graph. "No two ants
cross the same edge" removes the cycles of length $2$, so the only thing left out is two
neighbours swapping places. Problem 701 is the third row: the largest
[connected component](/topics/domain/component-graph-theory) is a global quantity, so a sweep has
to carry the frontier's connectivity pattern, and that pattern is the state that grows quickly.

## What adjacency forbids

Sometimes the leverage runs the other way. Problem 996 starts as a leader board, but restricting
swaps to adjacent ranks makes it a statement about the path graph. The question is which tuples
of per-player overtake counts are possible once everyone is back where they started. The answer
uses two graphs, and it helps to keep them apart:

- **The players' crossing multigraph.** Two players can only change order by swapping as direct
  neighbours, and each pair has to end in its original order. So any pair crosses an even number
  of times, and the crossings alternate between the two players. If a pair crosses $2t$ times,
  each of them gets $t$ overtakes from it. A player's overtake count is then their
  [degree](/topics/domain/degree-graph-theory) in a loopless multigraph on the *players*. That
  multigraph is not the board. It forces an even total, and no count can exceed half the total.
- **The board's path, through its walls.** A player with zero overtakes never moves up. Since
  they also have to end at home, they never move down either, so nobody passes them. The board
  splits at every such player, a [cut vertex](https://en.wikipedia.org/wiki/Biconnected_component)
  created by the dynamics. A positive run of length one is therefore impossible, because a lone
  player between two walls has nobody to swap with.

The surprise is how little else the path rules out. Inside a run of at least two positive
counts, the even-sum and half-sum conditions are also *sufficient*. Players move, so any two of
them in the same segment can eventually become neighbours, and the realisable tuples are exactly
the degree sequences you would get if every pair could meet. The adjacency restriction matters
only at the walls. This characterisation was a conjecture until a breadth-first brute force over
(permutation, counts) states for all $n \le 7$ agreed with it exactly. See
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence).

The counting step then uses the locality from the previous section in its smallest form. The
board is a path, so the frontier of a left-to-right sweep is one position, and the state only has
to record how the current run stands: just after a wall, at length one (not allowed to close yet),
or at length two or more. Each of these states carries a polynomial in the total overtake count,
built with a [generating function](/topics/domain/generating-function), and the sweep costs
$O(n^2)$ whatever the number of days.

## How to reason about it

- **Write the relation as a predicate before you write any algorithm.** Check edge versus vertex
  contact, the boundary, wraparound, blocking, and direction. Then put it in exactly one
  `neighbours` function, so that every part of the code uses the same graph.
- **Test the relation, not just the answer.** Brute-force the smallest instances and match the
  statement's worked example. A wrong adjacency usually produces a plausible number.
- **Look for independent sets in the structure.** Vertices with no edges between them, like
  problem 189's downward triangles, can be counted independently once their neighbours are fixed.
  That turns a joint sum into a product.
- **Size the frontier, not the graph.** Bounded-distance adjacency on a grid of width $w$ gives a
  frontier of about $w$ vertices. Whether the method works depends on what each frontier vertex
  has to record: a colour, an in/out flag, or a connectivity label.
- **Ask what the adjacency rules out.** A restriction to neighbouring moves often brings parity,
  alternation, or separation with it, as in problem 996. Those facts can remove most of the search
  before it starts. Then check what the restriction does *not* rule out: in problem 996 it acts
  only at the walls, and between them the board behaves as if every pair could meet.
- **Reach for the matrix when you need walks.** If the question counts paths or walks of a given
  length, the $(i,j)$ entry of $A^k$ counts the walks of length $k$ from $i$ to $j$, and
  [matrix exponentiation](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) reaches large
  $k$ in $O(\log k)$ multiplications. That is the same transfer matrix, viewed from the other side.

The common thread: the graph is never handed to you. You write it down from the statement's
wording, and how carefully you write it down decides both whether the answer is right and how
fast you can get it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ○ [0393](/solutions/0393/) — Migrating Ants
- ○ [0701](/solutions/0701/) — Random Connected Area
- ○ [0984](/solutions/0984/) — Knights and Horses
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
