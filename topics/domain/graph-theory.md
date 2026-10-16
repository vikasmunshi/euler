<!-- tags: [graph-theory] -->
<!-- status: final 2026-10-16T15:53Z -->
# Graph theory

[Graph theory](https://en.wikipedia.org/wiki/Graph_theory) studies things joined by pairwise
relations: a set of *vertices* and a set of *edges* between them, sometimes directed, sometimes
weighted. Project Euler names a graph outright only some of the time (107's network, 434's rigid
graphs, 857's coloured graphs). More often the graph is hidden in the statement: numbers whose
digits chain together (61), keylog facts about which digit comes first (79), sliding-puzzle
positions one move apart (244), brick rows that may be stacked on top of each other (215). This page
is a map. It covers how to spot the graph, how to hold it in memory, the traversals that walk it,
the shortest-path family, and the structural questions (trees, cycles, components, colourings)
that the later problems turn into counting problems. Each section links to the narrower page that
treats its idea in depth.

## Step zero: name the vertices and the edges

Almost all of the work is in choosing the model. Once I can say "a vertex is X, an edge means Y,"
the right algorithm usually follows from a table of standard ones. The problems below show how
varied that choice is:

| problem | a vertex is | an edge means | the question becomes |
|---|---|---|---|
| **61** | a 4-digit figurate number | last two digits of A = first two of B | a directed 6-cycle covering six families |
| **79** | a digit | "this digit was typed before that one" | a [topological order](/topics/technique/topological-sorting) |
| **83** | a matrix cell | a step up, down, left or right | a shortest path with weights on the vertices |
| **143** | a positive integer | `p² + pq + q²` is a perfect square | every triangle in a sparse graph |
| **186** | a telephone user | a successful call | the size of one connected component as edges arrive |
| **215** | a row of bricks | two rows share no seam | a count of walks of length `H − 1` |
| **244** | a board (blank position + colours) | one slide of a tile | every shortest path in an unweighted graph |
| **303** | a residue mod `n` | append a digit 0, 1 or 2 | the first time BFS reaches residue 0 |
| **425** | a prime | change one digit, or prepend one | a path that minimises the *largest* vertex on it |
| **881**, **931** | a divisor of `n` | the quotient is prime | levels and weights in a product of paths |

Two habits pay off here. First, **count the vertices before choosing an algorithm.** 244 is
tractable only because colouring the tiles shrinks the state space from roughly 10¹³ permutations
to about 10⁵ boards. 303 is tractable because the remainder mod `n` is all you need to remember
about a number, so the infinite set of numbers collapses to `n` vertices. Second, **put the
information on the vertex that the future depends on, and nothing more** (the
[memo key is the full state](/topics/takeaway/memo-key-is-the-full-state) takeaway, from the graph
side). A board in 244 must record the blank's position as well as the colours, because the colours
alone do not determine which moves are legal next.

## Representations

How you store the graph decides what is cheap to ask about it:

- An **[adjacency list](/topics/technique/adjacency-list)** maps each vertex to its neighbours.
  It is the default for sparse graphs: 61 (fewer than 200 numbers, short successor lists), 143 (an
  edge set built from a parametrisation of Eisenstein triples), and 215's compatibility lists.
  Enumerating a vertex's neighbours costs time proportional to its degree.
- An **[adjacency matrix](/topics/technique/adjacency-matrix)** gives an `O(1)` "is there an edge?"
  check and turns walk counting into matrix powers: entry `(i, j)` of `Aᵏ` counts the walks of
  length `k` from `i` to `j`. 107 *supplies* its network as a matrix (with `-` meaning no edge), but
  the solution immediately converts it to an edge list, because Kruskal wants edges sorted by
  weight.
- An **edge list** is the right shape when the algorithm consumes edges and not neighbourhoods:
  Kruskal in 107, and the stream of calls in 186.
- An **implicit graph** is never stored at all. A neighbour function generates it on demand. Grids
  (83's four neighbours), puzzle state spaces (244, 766) and residue graphs (303) all work this way:
  the vertex set is defined by a rule, and only the visited part ever exists in memory.

There is one more representation worth knowing, because it can make the edge test free. In 215 each
row is a bitmask of its seam positions, so "these two rows may be stacked" is `a & b == 0`. One
machine instruction replaces a set intersection (see
[bit manipulation](/topics/technique/bit-manipulation)).

## Traversals

There are two ways to walk a graph, and they answer different questions.

**[Depth-first search](/topics/technique/depth-first-search)** follows one branch to the end
before backing up. It suits searches for *structures*: cycles, complete assignments, every tiling.
In 61 it extends a path one number at a time and closes the cycle at depth six, as plain
[backtracking](/topics/technique/backtracking). The public solution's core shows the pattern:

```python
for next_num in number_mapping.get(current, []):
    if next_num not in visited:
        path.append(next_num)
        visited.add(next_num)
        result.extend(find_cyclic_paths(start, next_num, path, visited, number_mapping, target_length))
        path.pop()
        visited.remove(next_num)
```

The `visited` set keeps the path simple, and undoing it on the way out lets other branches reuse
the same vertex. That is the difference between a backtracking DFS and a reachability DFS, which
would leave every vertex marked. DFS also produces the finishing order that topological sorting
and strongly-connected-component algorithms depend on.

**[Breadth-first search](/topics/technique/breadth-first-search)** visits vertices in order of
increasing edge count from the start. It is the shortest-path algorithm for graphs where every edge
costs the same. 244 runs BFS over board states. Because it needs *every* shortest path, not only
the length, it runs the BFS backwards from the target, labelling each state with its distance to
the goal. A DFS then walks from the start through states whose label drops by exactly one at each
step. BFS supplies the distances, and DFS enumerates the paths along them. 303 is BFS in disguise: grow numbers digit by digit in increasing order, keep only the
first number to reach each residue, and the first number to reach residue 0 is the least multiple.

A third tool replaces traversal entirely when edges arrive over time and the only question is
"are these two connected?". A [disjoint-set](/topics/technique/disjoint-set-data-structure)
(union-find) structure answers it in near-constant amortised time and never stores an edge. 186
needs only the size of one component as a million calls stream in, and union-find with sizes at
the roots answers exactly that.

## Shortest paths

The [shortest path problem](/topics/domain/shortest-path-problem) page covers this family in
depth. The map is short: **the cheapest correct algorithm depends on whether the graph has cycles
and whether the weights are uniform.**

| graph | algorithm | problems |
|---|---|---|
| acyclic (a [DAG](/topics/domain/directed-acyclic-graph)) | one sweep in topological order, which is [dynamic programming](/topics/technique/dynamic-programming) | 67, 81 |
| cycles, all edges cost 1 | BFS | 244, 303 |
| cycles, non-negative weights | [Dijkstra's algorithm](/topics/technique/dijkstras-algorithm) | 83 |
| "cost" is the worst edge or vertex, not the sum | Dijkstra with `max` in place of `+`, or union-find in sorted order | 425 |

The move from 81 to 83 is the point at which the table changes rows. Once up and left moves are
allowed, the grid has cycles, no fill order exists, and Dijkstra has to discover the finalisation
order as it runs. 425 is the *bottleneck* variant: the best path minimises the largest prime it
passes through. Dijkstra's argument only needs the path cost to never decrease as the path gets
longer, which holds for `max` just as it does for `+`. Equivalently, add primes in increasing
order and record when each one joins 2's component, which is Kruskal's algorithm in another form.

## Structure: trees, cycles, components, colourings

From 270 onwards the tagged problems mostly *count* or *characterise* structures instead of
searching for one. Each structure has a classical theory behind it:

- **Spanning trees.** 107 asks for the
  [minimum spanning tree](/topics/domain/minimum-spanning-tree) (sum of all edges minus the MST
  weight), solved by [Kruskal's algorithm](/topics/technique/kruskals-algorithm) with union-find to
  reject edges that would close a cycle. 380's "exactly one path from the corner to every square"
  is the definition of a [spanning tree](/topics/domain/spanning-tree) of the grid graph, so
  counting mazes means counting spanning trees. The tool for that is
  [Kirchhoff's matrix-tree theorem](https://en.wikipedia.org/wiki/Kirchhoff%27s_theorem) or a
  [transfer matrix](/topics/domain/transfer-matrix-method) along the grid, not enumeration.
- **Cycles and paths that cover the graph.** An
  [Eulerian](/topics/domain/eulerian-path) cycle (every edge once, 289) exists exactly when every
  vertex has even degree, and counting them has its own theory. A
  [Hamiltonian](/topics/domain/hamiltonian-cycle) cycle or [path](/topics/domain/hamiltonian-path)
  (every vertex once: 312 on Sierpiński graphs, 669's Fibonacci seating, 490's frog) is NP-hard in
  general. These problems are solvable only because their graphs are self-similar or narrow, so a
  recursion or a small sliding window of state does the counting. 393's ants are a
  *cycle cover* of the grid: a permutation in which every ant moves to an adjacent cell and no two
  ants swap places. The [cycle graph](/topics/domain/cycle-graph) page collects the problems
  (61, 68, 846) whose answer *is* a ring.
- **Components.** [Connected components](/topics/domain/component-graph-theory) appear as
  incremental connectivity (186), as the largest black cluster of a random grid (701, a
  [percolation](https://en.wikipedia.org/wiki/Percolation_theory) question), and as strongly
  connected components of a directed grid (716). Collapsing those components always leaves a DAG.
- **Colourings and conflict graphs.** [Graph colouring](/topics/domain/graph-coloring) problems
  (857, 1002) usually come down to building the right *conflict graph*. In 1002, two pairs whose arcs
  would cross cannot be drawn on the same side of the row, so a valid drawing exists exactly when
  the crossing graph is bipartite, that is, 2-colourable. BFS finds out in linear time.
- **Small fixed shapes.** Triangles in 143, levels of the divisor graph in 881 and edge weights
  over it in 931. When the graph is sparse, "for each edge, intersect the endpoints' neighbour
  lists" finds every triangle in `O(E · d)`. When the graph has algebraic structure (a divisor
  graph is a product of paths, one per prime), the answer usually has a closed form that never
  builds the graph.
- **Functional graphs.** When every vertex has exactly one outgoing edge (522), the graph is a set
  of cycles with trees hanging off them. The [functional graph](/topics/domain/functional-graph)
  page covers that special case.

## Counting walks: where graphs meet linear algebra

215 is the bridge to the counting problems. A crack-free wall of height `H` is a walk of `H − 1`
steps in the compatibility graph. The layered DP the solution runs, `ways'[j] = Σ ways[i]` over
compatible `i`, is multiplication of a vector by the adjacency matrix, so the total is the sum of
the entries of `A^(H−1)` applied to the all-ones vector. When `H` is small, the DP loop is the
cheaper way to compute it. When `H` is astronomically large and the pattern count is small, the
same quantity yields to [matrix exponentiation](/topics/technique/matrix-exponentiation). The
[transfer matrix method](/topics/domain/transfer-matrix-method) generalises this: describe a long
thin structure as a walk through the states of one slice, and counting the structures becomes
counting walks.

## How to reason about it

- **Write the vertex/edge sentence first.** If you cannot say what a vertex is in one line, the
  model is not settled. If the vertex count is huge, look for a quotient (colours instead of
  numbered tiles, residues instead of numbers) before you look for a faster algorithm.
- **Let the question pick the algorithm.** Reachability → DFS/BFS or union-find; fewest steps →
  BFS; least weight → DAG sweep or Dijkstra; cheapest connected backbone → MST; "how many" →
  a recursion, a transfer matrix, or a theorem, almost never enumeration.
- **Prefer implicit graphs for state spaces.** A neighbour function plus a `visited` set builds
  only the part of the graph that the search actually reaches.
- **Check the hypotheses that make the fast algorithm correct.** A topological order needs no
  cycles (check, as 79's sink peeling does). Dijkstra needs non-negative weights and a cost that
  never decreases along a path. Kruskal needs an undirected graph. BFS distances are only shortest
  when every edge costs the same.
- **Recognise the NP-hard names and look for the escape.** Hamiltonian cycles, colourings with
  three or more colours and longest simple paths are hard in general. When Project Euler asks about
  them, the graph is special: a DAG, a narrow strip, a self-similar recursion or a bipartite
  conflict graph. Find which kind of special it is before writing a search.

| for more on | read |
|---|---|
| walking the graph | [depth-first search](/topics/technique/depth-first-search) · [breadth-first search](/topics/technique/breadth-first-search) · [disjoint-set](/topics/technique/disjoint-set-data-structure) |
| storing it | [adjacency list](/topics/technique/adjacency-list) · [adjacency matrix](/topics/technique/adjacency-matrix) · [adjacency](/topics/domain/adjacency-graph-theory) |
| paths and orders | [shortest path problem](/topics/domain/shortest-path-problem) · [DAG](/topics/domain/directed-acyclic-graph) · [topological sorting](/topics/technique/topological-sorting) · [Dijkstra](/topics/technique/dijkstras-algorithm) |
| trees | [minimum spanning tree](/topics/domain/minimum-spanning-tree) · [Kruskal](/topics/technique/kruskals-algorithm) · [spanning tree](/topics/domain/spanning-tree) · [tree](/topics/domain/tree-graph-theory) |
| cycles and covers | [cycle graph](/topics/domain/cycle-graph) · [Eulerian path](/topics/domain/eulerian-path) · [Hamiltonian cycle](/topics/domain/hamiltonian-cycle) · [functional graph](/topics/domain/functional-graph) · [cycle detection](/topics/technique/cycle-detection) |
| structure | [components](/topics/domain/component-graph-theory) · [graph colouring](/topics/domain/graph-coloring) · [planar graph](/topics/domain/planar-graph) · [transfer matrix method](/topics/domain/transfer-matrix-method) |

<!-- problems (generated by update-tags) -->
## Problems

- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0083](/solutions/0083/) — Path Sum: Four Ways
- ● [0107](/solutions/0107/) — Minimal Network
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0186](/solutions/0186/) — Connectedness of a Network
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0244](/solutions/0244/) — Sliders
- ○ [0270](/solutions/0270/) — Cutting Squares
- ○ [0289](/solutions/0289/) — Eulerian Cycles
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ○ [0380](/solutions/0380/) — Amazing Mazes!
- ○ [0393](/solutions/0393/) — Migrating Ants
- ○ [0425](/solutions/0425/) — Prime Connection
- ○ [0434](/solutions/0434/) — Rigid Graphs
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0490](/solutions/0490/) — Jumping Frog
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0553](/solutions/0553/) — Power Sets of Power Sets
- ○ [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0651](/solutions/0651/) — Patterned Cylinders
- ○ [0669](/solutions/0669/) — The King's Banquet
- ○ [0673](/solutions/0673/) — Beds and Desks
- ○ [0690](/solutions/0690/) — Tom and Jerry
- ○ [0701](/solutions/0701/) — Random Connected Area
- ○ [0713](/solutions/0713/) — Turán's Water Heating System
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0741](/solutions/0741/) — Binary Grid Colouring
- ○ [0766](/solutions/0766/) — Sliding Block Puzzle
- ○ [0781](/solutions/0781/) — Feynman Diagrams
- ○ [0846](/solutions/0846/) — Magic Bracelets
- ○ [0857](/solutions/0857/) — Beautiful Graphs
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0931](/solutions/0931/) — Totient Graph
- ○ [0975](/solutions/0975/) — A Winding Path
- ○ [0979](/solutions/0979/) — Heptagon Hopping
- ○ [0984](/solutions/0984/) — Knights and Horses
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1001](/solutions/1001/) — Connections I
- ○ [1002](/solutions/1002/) — Connections II

<!-- /problems -->
