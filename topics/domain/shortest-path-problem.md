<!-- tags: [shortest-path-problem] -->
<!-- status: final -->
# Shortest path problem

The [shortest path problem](https://en.wikipedia.org/wiki/Shortest_path_problem) asks for the
cheapest route between two nodes of a weighted graph. It recurs across the problems below not
because they are about graphs — almost none of them mention one — but because *anything with
states and transitions is a graph*, and once you see it as one, sixty years of settled algorithms
apply. The work in these problems is rarely the search. It is the modelling before it, and the
choice of algorithm that the model then forces.

## Naming the graph

Modelling means answering three questions, in order: what is a node, what is an edge, and what does
an edge cost. The answers are often not the ones the statement hands you.

In problems 81–83 the node is a grid cell and the cost is the cell's value — the natural reading.
Elsewhere the disguise is thicker. In problem 244 a node is an entire *board configuration* of a
sliding puzzle and an edge is one legal move; in problem 736 a node is a lattice point $(a,b)$ and
the two functions given in the statement are its only two outgoing edges; in problem 353 a node is
a station on a sphere and an edge is a great-circle road between any two of them. Problem 262 is
the hardest to name, because its graph does not exist until you build it: the terrain is a
continuous surface, and you must decide what a node even is.

Two things are worth noticing about that list. First, the number of nodes is usually enormous but
the number of edges *per node* is tiny — four moves, two functions, four grid neighbours. That is
the signature of an **implicit graph**: you never build an adjacency structure, you write a
`neighbours(state)` function and let the search call it. Second, the cost is a property of the
statement rather than of the geometry, and it is where the interesting problems put their teeth.

## The edge structure picks the algorithm

This is the decision that matters, and it is nearly mechanical once the graph is named:

| Edge structure | Algorithm | Cost |
|---|---|---|
| Acyclic (a [DAG](/topics/domain/directed-acyclic-graph)) | [DP](/topics/technique/dynamic-programming) in topological order | $O(V+E)$ |
| Cycles, all edges equal weight | [BFS](/topics/technique/breadth-first-search) | $O(V+E)$ |
| Cycles, non-negative weights | [Dijkstra](/topics/technique/dijkstras-algorithm) | $O(E \log V)$ |
| Negative weights | [Bellman–Ford](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm) | $O(VE)$ |
| One target, admissible heuristic | [A\*](https://en.wikipedia.org/wiki/A*_search_algorithm) | Dijkstra, better constants |

Problems 81 and 83 are the same $80 \times 80$ matrix and differ only in the permitted directions,
which makes them the cleanest demonstration of that table anywhere in the archive. In 81 you may
move right and down, so the graph is acyclic: every cell's predecessors are strictly closer to the
origin, and a single sweep in topological order — `solutions/public/p0081/` sweeps reverse
anti-diagonals, in place, in $O(n^2)$ — is exact. In 83 you may also move up and left. That one
change creates cycles, the topological order evaporates, and the DP is not merely slower but
*wrong*: there is no order in which every cell's dependencies are already final. What rescues it is
that the weights are positive, which is exactly Dijkstra's precondition:

```python
while target in unvisited:
    current = min(unvisited, key=lambda node: distances[node])   # finalise the nearest
    for neighbor in (up, down, left, right):
        if in_bounds(neighbor) and neighbor in unvisited:
            new_distance = distances[current] + node_weights[neighbor]
            if new_distance < distances[neighbor]:               # relax
                distances[neighbor] = new_distance
    unvisited.remove(current)
```

The invariant is worth stating plainly, because it is the whole reason the algorithm is allowed to
commit: when a node is chosen as the nearest unvisited one, its distance is already final, since
any other route to it would have to leave through a strictly farther node and edges only add
non-negative weight. That argument is what fails the moment a weight can be negative, and it is why
"can a cost ever be negative?" is worth asking before writing any relaxation loop.

Note the linear `min` scan above rather than a heap. It makes the loop $O(V^2)$, which at
$V = 6400$ costs less than the heap bookkeeping would; the same code at $V = 10^6$ would need the
priority queue. Note too where the loop stops: when the *target* is finalised, not when the grid is
exhausted. See [size the work to the input](/topics/takeaway/size-work-to-the-input).

Problem 82 sits between the two and shows a third option — exploit the shape and skip the general
algorithm. Movement is up, down and right, so a path enters a column, runs a contiguous vertical
stretch, and exits right, never re-entering. The cost of a detour is therefore a *range sum*, and
each column reduces to a one-dimensional minimisation over the column to its right, sweeping right
to left in $O(n^3)$ with no queue and no visited set. A general algorithm applied to a specific
structure is always correct and often the wrong tool.

## The cost function is where the difficulty hides

Once the graph is named, most of these problems are not hard because the search is hard. They are
hard because the cost is not the distance.

Problem 353 is the sharpest case. Stations sit on a sphere, roads follow great arcs, and the risk
of a road of length $d$ is $(d/\pi r)^2$ — a *convex* function of distance, so risk is
superadditive: splitting one long hop into two shorter ones strictly reduces the total. The
geometrically direct route is therefore never the cheapest, which inverts the usual intuition that
a straight line is optimal. The graph is complete over the lattice points of the sphere and the
weights are non-negative, so Dijkstra applies untouched; all the work is in enumerating the
stations, exploiting symmetry, and pruning the edge set to hops that could plausibly appear in an
optimal chain.

Problem 262 carries the opposite difficulty: the cost *is* Euclidean distance, and that is the
problem. A shortest path in the plane around obstacles is a sequence of straight segments bending
only at obstacle boundaries — a [visibility](https://en.wikipedia.org/wiki/Visibility_graph)
question, not a grid question. Discretise the terrain into a lattice and run Dijkstra on it and you
get a confident, stable, wrong answer, because the shortest path in a 4- or 8-connected grid
measures length in the grid's metric rather than the Euclidean one and converges to a value above
the true one however fine the mesh. The lesson generalises: *discretising a continuous problem
changes its metric*, so if the answer is a length you must either work in the continuous geometry
or bound the discretisation error rather than assume it vanishes. That problem also needs a
threshold elevation, found by [binary search](/topics/technique/binary-search-algorithm) on a
connectivity predicate — a shortest-path question answered first with a reachability question,
which is usually the cheaper half.

## When the graph will not fit

The state space is normally far too large to enumerate up front, and sometimes too large to
enumerate at all. Two distinct escapes:

**Encode the state so tightly it can be an array index.** Problem 244's puzzle has interchangeable
tiles within a colour, so two boards agreeing on colours are the *same node* — a canonicalisation
that collapses the [15-puzzle](/topics/domain/15-puzzle)'s $\approx 10^{13}$ permutations to about
$10^5$ states. Each state then packs into twenty bits (the blank cell's index, plus a bitmask of
one colour's cells), so the distance table is a flat byte array indexed directly by the state and a
move is a couple of exclusive-ors. The pattern — *find the equivalence that makes distinct
configurations the same node, then choose an encoding that is both canonical and an integer* — is
what turns an intractable search into a BFS that finishes instantly. Every move there costs the
same, so BFS is not merely adequate but optimal; reaching for Dijkstra when all edges have unit
weight is paying $\log V$ for nothing.

**Find structure in the weights and delete the search.** Problem 917 is a right/down grid path —
problem 81 again — over a $10^7 \times 10^7$ matrix, which is $10^{14}$ cells, and no amount of
tuning saves the DP sweep. But the matrix is not arbitrary: its entries have the form
$M_{i,j} = a_i + b_j$, and a cost that separates into a row part and a column part means the sum
along a path decomposes into terms that can be reasoned about directly rather than accumulated cell
by cell. When a shortest-path instance is too large by orders of magnitude, the intended solution
is essentially never a faster search; it is an argument about the cost function that makes
searching unnecessary. Problem 736 is the same lesson from the other side — its graph is infinite,
so searching outward is viable only once you have an argument bounding where the answer can be.

## Counting paths is a different question from measuring them

Shortest-path algorithms return a *length*. Several problems want something about the paths
themselves — how many are minimal, or an aggregate over all of them — and the two goals separate
cleanly:

1. Run BFS or Dijkstra once to label every node with its true distance from the source.
2. Walk the resulting layered structure: an edge $u \to v$ lies on some shortest path exactly when
   $d(u) + w(u,v) = d(v)$. Those edges form a DAG, and any question about shortest paths becomes a
   DP over it.

Step 2 is usually cheap, and it is where problem 244 lands: distances first, then a walk of the
strictly descending layers to enumerate the minimal paths and aggregate over them. Two traps sit
here. First, the aggregate may resist being folded into the DP — 244's is a sum of values each
already reduced modulo a constant, and a running total carried through the layers recovers the
answer only *modulo* that constant, because modular arithmetic cannot count how many terms wrapped
(see [exact sums resist modular
shortcuts](/topics/takeaway/exact-sums-resist-modular-shortcuts)). When that happens the paths must
be produced explicitly, and the search's job shrinks to proving how few of them there are. Second,
parity and similar invariants often pin the answer's shape before any code runs: in 244 the blank
tile starts and ends on the same cell and each move displaces it by one, so its net displacement is
zero and every path — minimal or not — has even length. A five-line argument that constrains the
result is worth more than a fast search, and costs nothing to check.

## How to reason about it

The cue is a superlative over routes: *shortest*, *cheapest*, *fewest moves*, *minimal risk*, or a
sequence of transformations reaching a target. When you catch it:

- **Write down node, edge, and cost explicitly**, in that order, before touching an algorithm. Most
  errors in this domain are modelling errors dressed as bugs.
- **Ask whether the graph is acyclic.** If it is, you want a DP sweep, not a search — Dijkstra on a
  DAG is correct but wasteful. The move set answers this: adding one backwards direction is the
  whole difference between problem 81 and problem 83.
- **Ask whether all edges cost the same.** If so, BFS is exact and beats every weighted algorithm.
- **Ask whether any cost can be negative.** If so, Dijkstra's finalisation argument breaks and you
  need Bellman–Ford, or a reformulation that makes the weights non-negative.
- **Keep the graph implicit.** A `neighbours(state)` function plus a canonical integer encoding
  scales to state spaces no adjacency list would hold.
- **Distinguish the distance from the path.** Compute distances first; recover paths, counts, or
  aggregates afterwards from the equality $d(u) + w(u,v) = d(v)$.
- **If the instance is absurdly large, stop optimising the search.** Look for structure in the cost
  function; that is where the intended solution lives.

The through-line is that shortest path is one of the few domains where recognising the problem is
almost the whole of solving it. The algorithms are short, well understood, and not yours to invent.
What is yours is the model.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0083](/solutions/0083/) — Path Sum: Four Ways
- ● [0244](/solutions/0244/) — Sliders
- ○ [0262](/solutions/0262/) — Mountain Range
- ○ [0353](/solutions/0353/) — Risky Moon
- ○ [0736](/solutions/0736/) — Paths to Equality
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost

<!-- /problems -->
