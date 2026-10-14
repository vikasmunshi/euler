<!-- tags: [directed-acyclic-graph] -->
<!-- status: final -->
# Directed acyclic graph

A [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (DAG) is a set
of nodes joined by one-way edges, with no way to follow the arrows and end up back where you
started. That one restriction ("no cycles") is what makes a DAG useful: its nodes can always be
lined up so that every edge points forward, and once they are lined up, questions that are hard on
general graphs become a single left-to-right sweep. In Project Euler a DAG is rarely named in the
statement. It turns up as a set of "X comes before Y" facts (Problem 79), as a triangle or grid you
may only walk down and to the right (67, 81), or as what is left when you shrink each strongly
connected component of a messier graph to a single node (716).

## The idea: an order that respects every arrow

A **topological order** of a DAG lists its nodes so that for every edge `u → v`, `u` comes before
`v`. Every DAG has at least one; a directed graph with a cycle has none, because no node on the
cycle can go first. So finding a topological order and proving the graph is acyclic are the same
job. There are two standard algorithms (see
[topological sorting](/topics/technique/topological-sorting)), both linear in nodes plus edges:

- **Kahn's algorithm**: repeatedly take a node with no incoming edges (a *source*), output it,
  and delete its edges. If you run out of sources while nodes remain, the remaining nodes contain
  a cycle.
- **Depth-first search**: output each node once all of its descendants are finished. Read
  backwards, that list is a topological order. Meeting a node that is still on the DFS stack
  means you have found a back edge, which is a cycle.

Problem 79 is Kahn's algorithm with the arrows reversed. Each successful login like `319` gives
two facts: 3 precedes 1, and 1 precedes 9. Every distinct digit becomes a node and every fact
becomes an edge. The shortest passcode is then a topological order of that graph, provided each
digit appears only once. The public solution peels off *sinks* (digits nothing has to follow) and
prepends them, so the passcode is built from the right-hand end:

```python
while successor_graph:
    for char, after in successor_graph.items():
        if not after:                      # a sink: nothing must follow it
            passcode = char + passcode
            break
    else:
        raise ValueError("No successor found - possible circular dependency in the constraints")
    del successor_graph[char]
    for after in successor_graph.values():
        if char in after:
            after.remove(char)
```

The `for … else` branch is the cycle check built into the algorithm. If no sink exists, the
constraints contradict each other and no passcode can satisfy them. There is also a question the
code does not ask: is the answer **unique**? A topological order is unique exactly when every
consecutive pair in it is joined by an edge, i.e. when the DAG has a
[Hamiltonian path](https://en.wikipedia.org/wiki/Topological_sorting#Uniqueness). If at some step
two sinks are available at once, the keylog cannot tell them apart, and "the" passcode depends on
which one the loop happens to pick. Problem 79's keylog leaves exactly one choice at every step,
but checking that is a single extra line, and it is worth writing whenever you rely on a
topological order being the answer and not just *an* answer.

## Paths on a DAG: the sweep that replaces search

The second thing an order gives you is cheap path optimisation. Process the nodes in topological
order and give each one the best value over its predecessors plus its own weight:

    best(v) = w(v) + max over edges u → v of best(u)

When `v` is reached, every `u` that feeds into it has already been finalised, because the order
guarantees it. One pass, `O(V + E)`, and no priority queue. This is the general framework behind
[dynamic programming](/topics/technique/dynamic-programming): the subproblems are the nodes, the
"depends on" relation is the edges, and any valid DP fill order is a topological order of that
graph. If the dependency graph had a cycle, no fill order would work.

Problems 67 and 81 show this in its plainest form:

| | nodes | edges | objective | a topological order |
|---|---|---|---|---|
| **67** triangle | the `n(n+1)/2` cells | each cell → its two children below | longest path, apex to base | row by row |
| **81** matrix | the `n²` cells | each cell → right and down neighbours | shortest path, corner to corner | rows, columns, or anti-diagonals |

The weights sit on nodes, not edges, but that changes nothing: put each node's weight on the edges
that leave it (or enter it). The triangle solution folds the bottom row into the one above it,
which is the sweep run in *reverse* topological order ("best path from here"). The matrix solution
walks the anti-diagonals backwards from the bottom-right corner for the same reason. Any order that
finishes a cell's successors before the cell itself is correct. The
[optimal substructure](/topics/domain/optimal-substructure) page covers why the recurrence is
correct; this page is about why the order is always available.

Two facts make the DAG view worth having in your head:

- **Longest path is easy here and hard elsewhere.** On a general graph the
  [longest simple path](https://en.wikipedia.org/wiki/Longest_path_problem) is NP-hard: a longer
  route can always loop back through vertices it has already used, and ruling that out is the
  expensive part. A DAG cannot loop back, so every path is simple, and "max" is as cheap as "min".
  Problem 67 can say "maximum" with a 100-row triangle and still be a one-second problem for this
  reason, not because 2⁹⁹ paths are somehow manageable.
- **Negative weights are harmless.** Dijkstra needs non-negative edges and Bellman–Ford needs no
  negative cycles. A DAG has no cycles, negative or otherwise, so the sweep handles any weights.
  Longest path is shortest path with the weights negated, one algorithm for both.

The contrast shows up the moment the grid stops being acyclic. Problem 82 lets the path move up
as well as down, and Problem 83 lets it move in all four directions. A cell can then be reached
from a cell that it itself feeds, there is no topological order left, and the solution has to
either find a coarser acyclic structure (82's columns) or let
[Dijkstra's algorithm](/topics/technique/dijkstras-algorithm) discover the finalisation order as
it runs (83). See the [shortest path problem](/topics/domain/shortest-path-problem) page for that
side of things.

## Every directed graph has a DAG inside it

Problem 716 starts from a graph that is *not* acyclic: a grid where each row line and each column
line is given a direction. Two nodes are strongly connected if each can reach the other, and the
problem counts the
[strongly connected components](https://en.wikipedia.org/wiki/Strongly_connected_component),
summed over all `2^H · 2^W` ways of orienting the lines. The bridge to this page is the
**condensation**. Collapse each strongly connected component to one node, keep the edges between
components, and the result is always a DAG. Any cycle that crossed components would merge them
into one. So counting components means counting the nodes of a DAG, and DAGs have structure
you can count with: at least one source, at least one sink, and an order. Here that order comes
from the direction of the lines. Reasoning about which parts of the grid must be sources or sinks
of the condensation turns a graph-traversal problem into a combinatorial one.

## How to reason about it

- **Look for the arrow before the algorithm.** "Before/after", "only right or down", "depends on",
  "can reach": if the relation can never loop back on itself, you have a DAG and an order for free.
  A grid that only moves right and down is acyclic by construction. A set of keylog facts is
  acyclic only because the puzzle promises it is, so check.
- **The order is the algorithm.** Once nodes are processed in topological order, longest path,
  shortest path, path counting ([lattice paths](/topics/domain/lattice-path) are path *counts* on
  the same grid DAG as 81) and reachability are all the same one-line relaxation with a different
  operator: `max`, `min`, `+` or `or`.
- **Pick the cheapest valid order.** For implicit DAGs such as grids and triangles, never run a
  general topological sort. Row-major or anti-diagonal order is already valid and costs nothing.
  Keep Kahn's algorithm or DFS for explicit graphs like 79's, where the order is the unknown.
- **When the graph has cycles, condense it.** Strongly connected components (via
  [Tarjan's](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm) or
  Kosaraju's algorithm) turn any directed graph into a DAG of components. That is the usual first
  step before a DAG method can be applied, and in 716 the condensation is exactly what is being
  counted.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ○ [0716](/solutions/0716/) — Grid Graphs

<!-- /problems -->
