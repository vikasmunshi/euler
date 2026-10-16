<!-- tags: [15-puzzle] -->
<!-- status: final 2026-10-16T07:29Z -->
# 15 puzzle

The [15 puzzle](https://en.wikipedia.org/wiki/15_puzzle) is a $4 \times 4$ tray of fifteen
sliding tiles and one empty square: you slide a tile orthogonally into the gap, over and over,
until the board reaches some target arrangement. It is a Victorian parlour toy, but for a
programmer it is something better — a small, self-contained laboratory for **state-space
search**. Every question it raises ("can I get there?", "what is the fewest moves?", "how many
shortest ways are there?") is really a question about a graph you never write down in full, and
answering it is an exercise in modelling that graph well.

## The idea

Think of one arrangement of the board as a single *state*. A legal move — sliding a tile into the
blank — turns one state into another, so states are the vertices of a graph and moves are its
edges. Because a slide can always be undone by the reverse slide, the graph is undirected and
unweighted: the shortest solution is the shortest path, and shortest paths in an unweighted graph
are exactly what [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) (BFS)
computes. That single correspondence — *board arrangement ↔ vertex, slide ↔ edge, fewest moves ↔
BFS distance* — is the whole domain in one sentence, and it is why these problems are tagged
[graph theory](/topics/domain/graph-theory) and
[shortest path](/topics/technique/breadth-first-search) as much as puzzle.

Two facts about the graph shape everything you do with it:

- **Not every arrangement is reachable.** The reachable states form exactly half of all
  arrangements — a [parity](https://en.wikipedia.org/wiki/15_puzzle#Solvability) invariant (the
  sign of the tile permutation, combined with the blank's row) is preserved by every move, so
  configurations with the wrong parity simply live in a different connected component. Before you
  search for a path, it is worth knowing whether one can exist at all. The invariant is a
  property of *distinguishable* tiles, though: once two tiles share a colour, swapping them is an
  odd permutation that leaves the board looking the same, so both parity classes collapse onto
  the same coloured boards and the obstruction disappears.
- **The full graph is astronomically large.** With all tiles distinct there are $16!/2 \approx
  10^{13}$ reachable states, far too many to enumerate. The naive state — "the permutation of all
  tiles" — is almost never the state you actually want.

## How to reason about it

The recurring lever in these problems is **choosing the smallest state that still distinguishes
the outcomes you care about**. If the tiles are not all distinct, most of that $16!$ blow-up is
counting relabellings of positions you cannot tell apart, and collapsing them shrinks the graph
enough to search directly.

Problem 313 ("Sliding Game") is the clean case: one red counter must travel corner to corner and
*every other counter is interchangeable*. So a state is not a permutation at all — it is just the
pair *(cell of the red counter, cell of the blank)*, which reduces the reachable states to
$O((mn)^2)$ and lets a plain BFS return the exact minimum move count for any small grid in an
instant. The payoff goes further: run that BFS across a range of grid sizes, read off the
distances, and they fall on a couple of straight lines — the search *reveals a closed form*, which
then answers the real (huge) question with no search at all. That is a habit worth keeping: use a
correct-but-slow BFS as an oracle to discover the pattern, then prove and exploit it.

Problem 244 ("Sliders") applies the same collapse to colours — seven red tiles, eight blue —
and the state becomes *(blank cell, bitmask of red cells)*: at most $16 \binom{15}{7} = 102\,960$
boards instead of $10^{13}$, every one of them reachable (the parity point above, made concrete),
and a slide is a two-bit XOR on the mask. What it asks for is not the length of a shortest path
but a checksum summed over *all* shortest paths, and that changes how you use the BFS:

- **Search from the target, not the start.** Because moves are reversible, one BFS out of the
  target labels every state with its distance *to* the target — exactly the label a path walker
  needs. Stop when the start is labelled: every shorter layer is already complete, and a shortest
  path visits nothing else.
- **The shortest paths are the strictly descending edges.** From a state labelled $d$, step only
  to neighbours labelled $d-1$. Those edges form a layered
  [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph) whose root-to-sink paths are
  precisely the shortest move sequences, so a depth-first walk needs no visited set.
- **Check whether the quantity factors over the DAG before you write a DP.** Path *counts*, or a
  sum of hashes taken modulo $p$, propagate layer by layer as (count, sum) pairs. Problem 244's
  total does not: it is the plain sum of per-path checksums that were each reduced modulo $p$,
  and a DP over residues cannot know how many of them wrapped. So each path is walked explicitly,
  carrying its partial hash down the branch — affordable only because the shortest-path DAG turns
  out to be thin. Read the aggregation rule as carefully as the puzzle.

So the engineering through-line across the 15-puzzle problems is not any one algorithm but a
sequence of modelling decisions: recognise the board graph, check whether parity (still) applies,
compress the state down to what actually matters, and let BFS give you either the distance, the
layered DAG of all shortest paths, or the data from which a closed form falls out. A sketch of the reduced
step for the single-counter version is all of two lines —

```python
# state = (red_cell, blank_cell); one BFS layer explores every slide
for nbr in adjacent(blank_cell):
    yield (nbr, blank_cell) if nbr == red_cell else (red_cell, nbr)
```

— and that is enough to turn an intractable-looking sliding puzzle into an ordinary graph search.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0244](/solutions/0244/) — Sliders
- ● [0313](/solutions/0313/) — Sliding Game

<!-- /problems -->
