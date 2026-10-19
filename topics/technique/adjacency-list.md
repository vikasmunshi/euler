<!-- tags: [adjacency-list] -->
<!-- status: final 2026-10-19T06:52Z -->
# Adjacency list

An [adjacency list](https://en.wikipedia.org/wiki/Adjacency_list) stores a graph as, for each
vertex, the list of its neighbours. It takes $O(V + E)$ space, against $O(V^2)$ for an
[adjacency matrix](/topics/technique/adjacency-matrix), and iterating a vertex's neighbours costs its
degree, not $V$. In Project Euler the graph is rarely given. It is a relation the solution
*builds*: "the last two digits of $a$ are the first two of $b$", "$p^2 + pq + q^2$ is square", "these two
brick rows share no seam". Once the relation is materialised as adjacency lists, the remaining work
is a standard graph algorithm. In the three solved problems below that is a cycle search (61), triangle
enumeration (143), and a layered path count (215). What distinguishes them is how the list is
stored, and the C ports make three different choices.

## The idea — precompute "who can follow whom"

The pattern has two phases:

1. **Build.** For every pair (or every generated pair) that satisfies the relation, append each
   vertex to the other's list, or only one way for a directed relation. This is the only place the relation is
   evaluated.
2. **Use.** Run the algorithm against the lists. Every "try the next step" loop becomes `for w in adj[v]`,
   which visits only legal moves.

The payoff is that an expensive or awkward test, such as a digit comparison, a perfect-square check or a
bitmask AND, is evaluated once per pair during the build instead of once per visit during a search
that may revisit the same pair many times. The choice of container depends on what the use phase
asks:

| question in the use phase | container |
|---|---|
| iterate neighbours | list or array |
| "is $w$ a neighbour of $v$?" | set, or a sorted array with binary search |
| common neighbours of $v$ and $w$ | set intersection, or a merge of two sorted arrays |

## Three graphs across the problems

**61, cyclical figurate numbers: a directed successor graph, then DFS for a 6-cycle.** The vertices are the
4-digit figurate numbers, fewer than 200 of them. There is an edge $a \to b$ when $a \bmod 100 = \lfloor b/100 \rfloor$, so
the last two digits of $a$ begin $b$. The answer is a directed 6-cycle using six different polygon types.
The public Python builds the successor lists once:

```python
number_to_next_graph: dict[int, list[int]] = {n: list() for vals in p_numbers.values() for n in vals}
for next_number in number_to_next_graph.keys():
    first_two_digits = next_number // 100
    for previous_number, successor_list in number_to_next_graph.items():
        if first_two_digits == previous_number % 100:
            successor_list.append(next_number)
```

[Backtracking](/topics/technique/backtracking) DFS from each vertex then follows only these
edges. The lists are short, so the search is nearly instant. Some numbers belong to two families, every
hexagonal number is triangular for instance, so the type-cover check runs on the finished cycle and
not on the edges.

**143, Torricelli triangles: an undirected graph, then triangles.** Integer distances
$p, q, r$ from the Fermat point need $p^2 + pq + q^2$, $q^2 + qr + r^2$ and $r^2 + rp + p^2$ all to be
squares. Each condition is an *edge*, so a valid $(p, q, r)$ is a **triangle** in the graph. Edges come
from the parametrisation of [Eisenstein triples](/topics/domain/eisenstein-triple), primitive ones times
every multiple, so the build is $O(L \log L)$ and the graph is sparse. Triangles are then found by
taking each edge $(p, q)$ with $p < q$ and intersecting the two neighbour lists for an $r > q$.

**215, crack-free walls: a compatibility graph, then a layered count.** The vertices are the 3329 ways to
tile one row of width 32 with bricks of length 2 and 3, each encoded as a seam bitmask. Rows $i, j$ are adjacent
when `rows[i] & rows[j] == 0`, meaning no shared seam. A wall of height $H$ is a walk of $H$ vertices,
so the count is $H - 1$ rounds of $c_i \leftarrow \sum_{j \in \mathrm{adj}(i)} c_j$: a
[transfer-matrix](/topics/domain/transfer-matrix-method) product written over adjacency lists. The
Python builds `compat` with one comprehension and each DP round is a sum over a list.

## Python and C — three storage choices

| problem | Python | C |
|---|---|---|
| 61 | `dict[int, list[int]]` | dense `int successors[600][600]` plus a `succ_counts[]` array, fixed-size and wasteful, but the vertex count is tiny |
| 143 | `dict[int, set[int]]`; triangles by `neighbors_p & adjacency[q]` | one growable `int` vector per vertex, each `qsort`ed and deduplicated once; triangles by a **two-pointer merge** of two sorted lists |
| 215 | `list[list[int]]` of compatible indices | **no list at all**: recompute `rows[i] & rows[j]` in the innermost loop |

Each is a reasonable answer to a different trade-off. 61's C pays $O(V^2)$ memory to avoid any
allocation, which costs nothing at $V < 600$. 143's C replaces hash-set intersection with sorted arrays,
which are cache-friendly, need no hashing, and are merged in linear time. That is a big part of the 11-fold speed-up
over Python. 215's C notices that the edge test is a single AND, cheaper than loading an index
from a list, so it keeps memory flat and makes the loop branch-light. It visits all $R^2$ pairs per
layer, against Python's $\sum_i \deg(i)$, but each step is a few instructions. The general point is that the adjacency list is worth storing
when the edge test costs more than reading an index from memory.

## How to reason about it

- **When a search keeps asking "what can follow this?", precompute the answer.** Build adjacency once
  and let the search iterate it.
- **Name the graph problem.** A chain that closes is a cycle (61), three mutual relations form a triangle (143),
  and stacked compatible layers form a walk count (215). Each has a standard algorithm.
- **Choose the container for the query.** Lists for iteration, sets or sorted arrays for membership and
  intersection.
- **In C, prefer sorted arrays to hash sets.** `qsort` once, then binary search or merge. That is fast and
  allocation-free.
- **Skip the list when the edge test is trivial.** A single bitwise AND or comparison is cheaper to
  recompute than to store and load.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0215](/solutions/0215/) — Crack-free Walls

<!-- /problems -->
