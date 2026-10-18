<!-- tags: [triangular-tiling] -->
<!-- status: final 2026-10-18T10:12Z -->
# Triangular tiling

The [triangular tiling](https://en.wikipedia.org/wiki/Triangular_tiling) fills the plane with
equilateral triangles, six meeting at every vertex. Project Euler keeps drawing a big triangle cut
into $n^2$ small ones and asking something about it: the cheapest sub-triangle, the number of inked
triangles, the number of proper colourings, the path of a laser bouncing inside. These problems are
not hard because of their geometry. They are hard to *index*: 60° angles do not fit array
subscripts, and the up and down triangles alternate. Each solution below starts by choosing
coordinates that make the tiling look like $\mathbb{Z}^2$. Once that is done, the problem turns
into a familiar one: prefix sums, a line arrangement, a transfer matrix, or a gcd count.

## The idea: three coordinate systems

The tiling has three families of parallel lines, at 0°, 60° and 120°. Every useful coordinate
system takes two of them as axes:

| coordinates | a point / cell is | the third line family is | used in |
| --- | --- | --- | --- |
| **rows** | row $r$, position $j \le r$ | implicit in "$j$ and $j + 1$ below" | 150, 189 |
| **skew lattice** | $p\,\mathbf{e}_1 + q\,\mathbf{e}_2$, $\mathbf{e}_1, \mathbf{e}_2$ at 60° | $p + q = \text{const}$ | 202 |
| **affine right triangle** | $(x, y)$ with $x, y \ge 0,\ x + y \le n$ | $x + y = c$ | 163 |

These are really one choice. An [affine map](https://en.wikipedia.org/wiki/Affine_transformation)
sends the equilateral triangle to the right triangle with legs on the axes. It keeps straight
lines, parallelism, midpoints, incidence, and which side of a line a point is on. Anything a
problem asks about lines and cells survives the map. Lengths and angles do not survive, but none of
these problems needs them. Once mapped, the three directions are $x$, $y$ and $x + y$, all with
integer equations.

The second structural fact is **orientation parity**. Row $r$ (from the apex) holds $r$ up
triangles and $r - 1$ down triangles, alternating. Every edge joins an up triangle to a down one,
so the adjacency graph of the cells is bipartite. Down triangles within a row never touch each
other. The vertices have a matching property: the three corners of any small triangle carry three
different values of $(p - q) \bmod 3$. That gives a canonical 3-colouring of the lattice points.

## Four problems, four reductions

**Rows and prefix sums: 150.** A downward-widening sub-triangle with apex $(i, j)$ and height $h$
is the union of row segments $[j, j + k]$ in row $i + k$. In row coordinates it is a staircase of
contiguous runs. With a [prefix sum](/topics/technique/prefix-sum) per row, each segment costs two
reads, and growing the triangle by a row costs one addition. That gives $O(n^3)$ over all apexes
and heights, where summing from scratch would be $O(n^4)$. The triangular storage is the
implementation detail. The C keeps one flat array with row $r$ at offset $r(r+1)/2$ and the prefix
rows at $r(r+3)/2$, since each prefix row is one entry longer. The Python pads to an $n \times n$
NumPy matrix and gathers every segment of one apex row with a
[fancy index](/topics/technique/fancy-indexing).

**A line arrangement: 163.** The cross-hatched triangle adds the three medians of every small
triangle, so there are six line directions. After the affine map to the right triangle every line
is $ax + by = c$ with small integers: $y = c$, $x = c$, $x + y = c$ from the grid, and $x - y$,
$x + 2y$, $2x + y$ from the medians. A triangle in the figure is three lines from three different
directions whose pairwise intersections all lie in the closed big triangle and do not coincide.
The solution checks $\binom{6}{3} = 20$ direction triples and every line triple within them.
Intersections come from [Cramer's rule](https://en.wikipedia.org/wiki/Cramer%27s_rule), kept as
integer numerators over a determinant, and the inside test is cross-multiplied, so nothing is ever
divided. The affine map is what makes this possible. In the equilateral frame the median lines
have irrational slopes.

**A transfer matrix: 189.** Proper 3-colourings of $n^2$ cells, $3^{64}$ of them by brute force.
The row structure does the work. The only edges between rows are horizontal, joining each up
triangle in row $r$ to the down triangle beneath it. Within a row the down triangles are pairwise
non-adjacent. So once the up triangles of two consecutive rows are coloured, each down triangle
is constrained only by its three neighbours, independently of the others. The state is the
colouring of a row's up triangles, encoded in base 3, and a
[transfer-matrix](/topics/domain/transfer-matrix-method) sweep moves from row to row,
contracting one column at a time like a [tensor network](/topics/technique/tensor-network). The bipartite up/down structure is what makes the down
triangles summable without becoming part of the state.

**Unfolding into the lattice: 202.** A laser enters a corner of a mirrored triangle and must leave
by the same corner after $n$ bounces. Reflecting the *triangle* instead of the beam
([unfolding](https://en.wikipedia.org/wiki/Billiard_(geometry)#Unfolding)) tiles the plane and
straightens the path into a segment from the origin to some lattice point $(p, q)$ in skew
coordinates. The tiling then answers everything:

- the segment crosses $p - 1$, $q - 1$ and $p + q - 1$ lines of the three families, so there are
  $2(p + q) - 3$ bounces, and fixing $n$ fixes $p + q$;
- it ends at an image of the starting corner exactly when $p \equiv q \pmod 3$, the vertex
  3-colouring;
- it passes through no intermediate vertex (where it would escape) exactly when $\gcd(p, q) = 1$.

What remains is counting totatives of $S = p + q$ in one residue class mod 3, done by
[inclusion-exclusion](/topics/technique/inclusion-exclusion-principle) over the squarefree divisors
of $S$. The geometry never comes back.

The open problems on this tag use the same frame. 577 counts regular hexagons on the lattice
points, 702 has a flea jumping toward hexagon corners over a triangle grid, and 780 tiles a torus
with unit triangles.

## C and Python

Once the coordinates are fixed, both languages use the same index arithmetic. The differences are
the usual ones:

- **Triangular storage.** C stores triangles as one flat array with closed-form row offsets. Python
  either pads to a rectangle (150's NumPy matrix, zero above the diagonal) or uses lists of lists.
  Padding wastes half the memory but lets NumPy broadcast across a row.
- **Integer geometry.** 163's numerators, determinants and concurrency cross-products stay well
  inside 64 bits for $n = 36$, so the C stores each line as a struct of three `long long` and needs
  no wider type.
- **Floor versus truncation.** 202 counts members of a residue class in a range with
  `(count - target) // 3 + 1`. Python's `//` floors, so an empty range gives 0. C's `/` truncates
  toward zero and would give 1, so the C adds an explicit `if (count < target) return 0;`.
- **Base-3 states.** 189 encodes a row's colouring as a base-3 integer in both languages. The C
  allocates three `long long` arrays of $3^n$ and swaps pointers between sweeps. Python rebinds
  lists.

## How to reason about it

- **Map to a right triangle first.** If the question involves only lines, incidence and
  insideness, an affine map gives integer equations for free.
- **Use rows for cell data, skew coordinates for points and lines.** Cell sums and colourings
  (150, 189) sit naturally in rows. Paths, line crossings and lattice points (163, 202) sit in
  $(p, q)$.
- **Exploit the up/down alternation.** Cells of one orientation are pairwise independent given
  the other orientation, so they can be summed out of a DP state.
- **Unfold reflections.** A bouncing path in a triangle is a straight segment in the tiling, and
  then lattice tools (gcd for visibility, residues for vertex type) apply.
- **Count lines crossed by family.** In skew coordinates a segment to $(p, q)$ crosses
  $p - 1$, $q - 1$ and $p + q - 1$ lines. Most counting questions about paths start from there.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0202](/solutions/0202/) — Laserbeam
- ○ [0577](/solutions/0577/) — Counting Hexagons
- ○ [0702](/solutions/0702/) — Jumping Flea
- ○ [0780](/solutions/0780/) — Toriangulations

<!-- /problems -->
