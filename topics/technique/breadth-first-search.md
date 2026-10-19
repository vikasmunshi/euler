<!-- tags: [breadth-first-search] -->
<!-- status: final 2026-10-19T06:41Z -->
# Breadth-first search

[Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) (BFS) explores
a graph in order of distance from a source. It visits every vertex one edge away, then every vertex two
edges away, and so on, using a FIFO queue. That order is its useful property. In an unweighted
graph the first time BFS reaches a vertex is along a shortest path, and the queue always holds at
most two consecutive distance layers. The three solved problems below use that property in three
different ways: to find shortest paths in a puzzle's state space (244), to grow a sparse family of
numbers one digit at a time (387), and to build a string-matching automaton whose links point to
shallower nodes (679).

## The idea — process the graph in layers

The core loop is short. Here is a layer-synchronous form, which all three solutions use:

```python
frontier = [source]; dist[source] = 0
while frontier:
    nxt = []
    for v in frontier:
        for w in neighbours(v):
            if w not in dist:
                dist[w] = dist[v] + 1
                nxt.append(w)
    frontier = nxt
```

What this guarantees:

- **Correct distances in unweighted graphs.** Layer $d$ is exactly the set of vertices at distance
  $d$, so `dist` is correct as soon as it is written. That holds only when every edge costs the same.
  Weighted edges need [Dijkstra](/topics/technique/dijkstras-algorithm).
- **$O(V + E)$ time**, and each vertex enters the queue at most once.
- **Layers are complete before the next starts.** Anything that depends only on shallower vertices,
  such as a parent's label, a failure link or a digit sum, is ready when a vertex is processed.
- **Memory is the widest layer.** That is the cost compared with
  [depth-first search](/topics/technique/depth-first-search), which needs only the depth of the
  current path. When the frontier would be huge and distances are not needed, DFS is the cheaper walk.

## Three uses across the problems

**244, sliders: shortest paths, then enumerate them.** The 15-puzzle with coloured, not numbered,
tiles has at most $16 \cdot \binom{15}{7} = 102\,960$ states, so BFS covers all of it. Each state
packs into a 20-bit integer: the blank's cell above a 16-bit red-cell mask. A move is a two-bit
XOR, and `dist` is a flat byte array of $2^{20}$ entries. Three refinements make it a complete
solution:

- *Search from the target.* Moves are reversible, so one BFS out of the target gives every state its
  distance *to* the target. That is the label a path enumerator needs.
- *Stop when the start is labelled.* All shallower layers are complete by then, and a shortest path
  visits only those.
- *Enumerate along descending labels.* Edges from layer $d$ to $d - 1$ form a DAG whose paths are
  exactly the shortest move sequences, so a DFS over it, carrying the rolling checksum, sees each
  shortest path once. The checksums are summed *unreduced*. That rules out the shortcut of carrying
  (count, hash-sum) pairs through the BFS, because the modulus would lose how many values wrapped.
  See [15 puzzle](/topics/domain/15-puzzle).

**387, Harshad numbers: BFS as level-order generation.** Right-truncatable Harshad numbers are
closed under truncation: every prefix of one is also one. They therefore form a tree rooted at the
digits 1 to 9, and level $k$ of the tree holds the $k$-digit members. BFS grows it one digit per
layer. Each node carries `(value, digit_sum)`, so a child's digit sum is the parent's plus one
digit, and a child survives only if it divides by that sum. The tree is very sparse, with a few
thousand nodes even below $10^{32}$. So the search below $10^{14}$ is cheap, and each strong node only needs
[Miller–Rabin](/topics/technique/miller-rabin-primality-test) tests on four
one-digit extensions. Here BFS is not finding distances. It is used because the problem's structure is a
prefix tree and level order is the natural way to build it. DFS would work equally well.

**679, Freefarea: BFS orders the automaton construction.** Counting length-30 words over
$\{A, E, F, R\}$ that contain each of four keywords exactly once is a DP over the states of an
[Aho–Corasick](/topics/technique/aho-corasick-algorithm) automaton. Building that automaton is a
BFS over the keyword [trie](/topics/technique/trie). A node's failure link points to the node for
its longest proper suffix that is also a trie prefix. That node is strictly shallower, so in BFS
order its failure link and outputs are already final. The same pass completes the goto table and
ORs each node's output mask with its failure node's, so overlapping matches are reported in one
transition. Here BFS is used for its layer-completeness guarantee.

## Python and C

- **244**: Python uses a `bytearray` of $2^{20}$ for `dist`, a `collections.deque` as the queue
  (`len(frontier)` pops per layer), and a list of tuples as the DFS stack. C uses static arrays: a
  `dist[1 << 20]`, an `int` queue array with `head`/`tail` indices marking each layer's end, and
  three parallel stack arrays. The Python per-state cost is the roughly 19× gap; the algorithm is the same.
- **387**: the frontier is a Python list of tuples rebuilt each level. In C it is two growable
  `Frontier` buffers swapped between levels. Values go up to $10^{32}$, so C stores them as
  `unsigned __int128` and calls GMP's `mpz_powm` for primality tests past $2^{64}$. Python's `int`
  and `pow(a, d, n)` handle both ranges.
- **679**: Python builds the trie as a list of `dict`s, so it can test `ch in goto[node]`. C uses a
  fixed `goto_tbl[32][4]` with $-1$ for missing edges and a 32-slot array as the BFS queue. The tree
  has 13 nodes, so a fixed-size array is enough.

## How to reason about it

- **Use BFS for fewest moves when moves cost the same.** Puzzle states, word ladders and knight
  tours are all unweighted shortest-path problems.
- **Compress the state first.** An integer state indexes a flat array, which is far faster than a
  hash set of tuples, and the state count tells you whether exhaustive BFS is feasible at all.
- **With reversible moves, search from the goal.** One BFS then labels every state with its
  distance to the goal. Descending those labels enumerates every shortest path with no backtracking.
- **Use BFS when each node depends on shallower ones.** Failure links, prefix trees grown digit by
  digit, and anything defined from a parent are all computed correctly in level order.
- **Mind the frontier width.** BFS stores whole layers. If a layer would be enormous and only
  reachability or a count is needed, DFS or a DP over layers is cheaper.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0244](/solutions/0244/) — Sliders
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0679](/solutions/0679/) — Freefarea

<!-- /problems -->
