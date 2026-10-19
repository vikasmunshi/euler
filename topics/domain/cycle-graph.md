<!-- tags: [cycle-graph] -->
<!-- status: final 2026-10-19T09:40Z -->
# Cycle graph

A [cycle graph](https://en.wikipedia.org/wiki/Cycle_graph) $C_n$ is $n$ vertices joined in a single
ring: each vertex has exactly two neighbours, and the last connects back to the first. It is the
simplest graph with no ends, and that is what makes it both easy and awkward. Easy, because along the
ring everything is local. Awkward, because the wrap-around edge means there is no natural
first element: every position looks the same, so rotations of one arrangement look like different
answers. Problems about rings, circular chains and permutations all have this shape. The three solved
problems below each find a cycle, or reason about one, and each has to handle the same two
issues: **closing the ring** and **not counting rotations twice**.

## The idea — a path that closes, with no distinguished start

Three facts carry most cycle-graph reasoning:

- **A cycle is a path plus one closing edge.** Most algorithms build or count paths, the easy part,
  and then check or impose the closing constraint at the end.
- **Rotations are the same cycle.** A cycle of length $n$ written from each of its vertices gives $n$
  sequences, and $2n$ if it can also be read backwards. Fix a
  [canonical form](/topics/technique/canonical-form) (start at the smallest element, or store the
  sorted set) so that each cycle is counted once.
- **Every permutation is a disjoint union of cycles.** Iterating a bijection $\sigma$ from any start
  returns to the start, so the functional graph of $\sigma$ is a set of disjoint cycle graphs. Questions
  about $\sigma$ then factor over its cycles.

For counting, the classic cycle result is the number of
[independent sets](/topics/domain/independent-set-graph-theory) of $C_n$: the
[Lucas number](/topics/technique/lucas-number) $L_n$. On a path of $n$ vertices the count is the
Fibonacci number $F_{n+2}$. Closing the ring forbids choosing both ends. Split on whether vertex 1 is
chosen. If it is not, the rest is a path of $n - 1$. If it is, both neighbours are excluded, which
leaves a path of $n - 3$. That gives $F_{n+1} + F_{n-1} = L_n$.

## Three problems, three roles for the ring

**61, cyclical figurate numbers: find a directed cycle.** Six 4-digit numbers, one from each
polygonal family, must form a ring in which the last two digits of each are the first two of the
next. The public solution builds the directed "digit link" graph over all 4-digit figurate numbers,
then runs a [depth-first search](/topics/technique/depth-first-search) for paths of length six. The
ring is closed by one check when the path is full:

```python
if len(path) == target_length:
    if current % 100 == start // 100:
        return [tuple(path[:])]
```

Every cycle is found once from each of its six starting points, so the results are stored as
`tuple(sorted(path))`. The sorted set is the canonical form that removes rotations. A separate check
then confirms that the six numbers cover all six families, allowing for numbers that belong to two.

**68, magic 5-gon ring: constraints around a ring.** Ten numbers sit on a 5-gon: an inner cycle
$C_5$ and an outer spoke on each inner vertex. Each line, made of an outer value and two *adjacent*
inner values, must have the same sum. The ring structure decides the search. Choose only the inner
cycle, and each line forces its outer value, `outer[i] = S - (inner[i] + inner[(i+1) % n])`. The
`% n` is the closing edge. Rotations are removed by the problem's own convention: start from the line
with the smallest outer value. The solution places the smallest free number there first.

**209, circular logic: decompose a permutation into cycles.** The problem counts truth tables $\tau$ on
6-bit inputs with $\tau(x) \wedge \tau(\sigma(x)) = 0$ for a fixed map $\sigma$, a
[nonlinear feedback shift register](/topics/domain/nonlinear-feedback-shift-register). $\sigma$ is a
bijection, so its $2^6$ states split into disjoint cycles. On each one the constraint says "no two
consecutive states are both 1", which defines an independent set of $C_n$. Components are
independent, so the count is a product of Lucas numbers over the cycle lengths, a fixed point
contributing $L_1 = 1$. A search over $2^{64}$ truth tables becomes a walk around 64 states.

## Python and C

- **61**: Python stores the successor graph as a `dict[int, list[int]]` and collects cycles in a
  `set` of sorted tuples. C uses fixed static arrays: `successors[MAX_NUMS][MAX_NUMS]`, a `visited`
  flag array, and a result table with a linear `already_found` scan comparing sorted forms. That
  scan is a hand-written stand-in for the Python set's deduplication, and costs nothing at
  this size.
- **68**: Python enumerates inner rings with `itertools.permutations` and forces the outer values in a
  loop, aborting on a `KeyError` from `set.remove`. C backtracks over the inner positions with a
  `used[]` array and compares candidate numbers as strings (longer wins, then lexicographic), because
  the 16-digit result is built by concatenation.
- **209**: the same cycle walk over a `bytearray`/`unsigned char` seen-mask. Python multiplies the
  Lucas numbers into an unbounded `int`. C accumulates in `unsigned __int128` and formats the result
  itself, because, as its comment notes, the product already exceeds 64 bits at $k = 7$.

## How to reason about it

- **Build the path, check the closure last.** The wrap-around edge is one test at full length
  (61), or one modular index (68).
- **Pick a canonical start before you count.** A sorted set, or the smallest element first, removes
  the $n$-fold rotational duplicates. For counting arrangements of beads rather than listing them, use
  [necklace counting](/topics/domain/necklace-counting) (Burnside's lemma).
- **Iterate a bijection to find its cycles.** A seen-array and one walk per unvisited start
  decomposes any permutation in $O(n)$. Then any per-element constraint along $x \to \sigma(x)$ splits
  over the cycles.
- **Cycle counts are path counts plus a correction.** Count on the path, then add or subtract the
  configurations that the closing edge allows or forbids. A
  [transfer matrix](/topics/domain/transfer-matrix-method) handles this as a trace, $\operatorname{tr}(T^n)$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0209](/solutions/0209/) — Circular Logic
- ○ [0673](/solutions/0673/) — Beds and Desks
- ○ [0781](/solutions/0781/) — Feynman Diagrams
- ○ [0814](/solutions/0814/) — Mezzo-forte
- ○ [0824](/solutions/0824/) — Chess Sliders
- ○ [0843](/solutions/0843/) — Periodic Circles
- ○ [0846](/solutions/0846/) — Magic Bracelets
- ○ [0857](/solutions/0857/) — Beautiful Graphs

<!-- /problems -->
