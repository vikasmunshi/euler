<!-- tags: [symmetry-in-mathematics] -->
<!-- status: final 2026-10-18T12:33Z -->
# Symmetry in mathematics

A [symmetry](https://en.wikipedia.org/wiki/Symmetry_in_mathematics) of a problem is
a transformation that changes the description and leaves the answer alone. Examples
are swapping a cuboid's dimensions, relabelling a quadrilateral's corners, or
permuting the colours in a palette. The general payoff is covered in
[Exploit symmetry and complementary counting](/topics/takeaway/exploit-symmetry):
count one representative per orbit and scale up. This page is about the step that
comes before it. Every problem below asks me to say *which group* acts and *how*,
and the right way to use the symmetry follows from that answer. The three solved
problems use the same idea in three ways: by sorting, by taking the minimum over an
explicit group, and by an invariance that turns a matrix into a scalar.

## The idea

The symmetries of an object form a [group](https://en.wikipedia.org/wiki/Group_(mathematics)):
composing two of them gives another, and each can be undone. The group
[acts](https://en.wikipedia.org/wiki/Group_action) on the things I am counting
and splits them into orbits. Naming the group exactly matters for two reasons.
First, it fixes the size of the problem: a group of order $|G|$ saves at most a
factor of $|G|$. Second, its structure suggests the implementation:

| Group | Acts on | Cheapest canonical form |
|---|---|---|
| [Symmetric group](https://en.wikipedia.org/wiki/Symmetric_group) $S_k$, coordinates permuted freely | a $k$-tuple of interchangeable values | sort the tuple: enumerate $a \le b \le c$ |
| [Dihedral group](https://en.wikipedia.org/wiki/Dihedral_group) $D_n$, rotations and reflections of an $n$-gon | labels around a cycle | apply all $2n$ elements and keep the lexicographic minimum |
| $S_c$ acting on a palette of $c$ colours | colourings | none needed: take the counts that are invariant under the group |

**Sorting is the canonical form for $S_k$.** In [Cuboid Layers](/solutions/0126/)
the number of cubes in each layer depends on $(a, b, c)$ only through the
symmetric functions $ab + bc + ca$ and $a + b + c$. That means $S_3$ acts on the
dimensions, and "the same cuboid" means "the same multiset of dimensions". The
canonical member of each orbit is the sorted triple, so the solution never
generates an orbit at all. It just enumerates $a \le b \le c$ in its loop bounds.
This gives up to a 6× saving, and nothing has to be divided back out afterwards.
That matters, because triples like $(a, a, c)$ have orbits of size 3 rather than
6, and dividing by $|S_3|$ would count them wrong.

**An explicit group when the symmetry is not a sort.** In [Integer Angled
Quadrilaterals](/solutions/0177/) a quadrilateral is described by eight corner
angles read around the figure. Starting the walk at a different vertex, or walking
the other way, gives a different 8-tuple for the same shape. Those relabellings
are $D_4$, the symmetry group of the square, with order 8. Sorting the tuple would
be wrong here: it would identify shapes that are genuinely different, because
$D_4$ moves the angles only in the patterned way that a rotation or reflection
does. So the solution builds the group from its two
[generators](https://en.wikipedia.org/wiki/Generating_set_of_a_group): $\rho$,
the rotation $A \to B \to C \to D$, and $\sigma$, the reflection across the
diagonal $AC$, both written as index permutations of the tuple. Composing $\sigma$
with powers of $\rho$ gives all eight elements. The canonical form of each hit is
the smallest of its eight relabellings, and the answer is the number of distinct
canonical forms. Writing down two generators and letting composition produce the
rest is less error-prone than listing eight permutations by hand. A wrong entry in
the list is a typo; a wrong generator gives a set that fails to have eight
elements, and that is easy to check.

**Invariance instead of enumeration.** [Coloured Configurations](/solutions/0194/)
uses the symmetry without ever forming an orbit. The state of its
[transfer matrix](/topics/domain/transfer-matrix-method) is the ordered colour pair
on a shared edge. Every permutation of the $c$ colours maps proper colourings to
proper colourings, and $S_c$ is transitive on the ordered pairs of distinct
colours, so every state looks the same from the inside. Every row of the matrix
therefore has the same sum, and the all-ones vector is an
[eigenvector](https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors) of every
unit's matrix. Each unit then multiplies the running total by a scalar, the order
of the units stops mattering, and the count becomes a closed form: a binomial
coefficient times two powers. The same symmetry also produces the scalars
themselves. To compute a row sum, the solution fixes one representative left edge
and sorts the right edges into equality classes relative to it ("same colour as
the left-bottom", "a new colour", …). It counts one member of each class and
weights it by the class size, which is orbit counting again, this time under the
stabiliser of the left edge.

## C and Python

The symmetry reasoning is the same in both languages. Only the way the orbit work
is carried out differs:

- **Cuboid Layers.** The sort costs nothing: it is the shape of the loop bounds,
  so the two versions are line for line the same. The only difference is the
  histogram, a `calloc`'d array in C and a list in Python.
- **Integer Angled Quadrilaterals.** Both versions pack an 8-tuple into two
  `uint64` keys, 16 bits per angle, so that comparing tuples lexicographically
  is a comparison of two integers. C relabels each hit eight times, keeps the
  minimum key, and finally runs `qsort` and counts the runs of equal keys. Python
  does the same thing on whole columns. Each relabelling is a NumPy fancy index
  over the table of every hit, the minimum is taken elementwise, and
  `np.unique(…, axis=0)` counts the distinct rows. The group is applied to every
  hit at once, not to one hit at a time.
- **Coloured Configurations.** Once the symmetry has reduced the problem to
  $\binom{a+b}{a}\,c(c-1)\,S_A^{a}S_B^{b} \bmod 10^8$, what differs is the
  arithmetic, not the symmetry. Python uses `math.comb` and three-argument `pow`.
  C builds the binomial coefficient from Pascal's triangle, because $10^8$ shares
  the factors 2 and 5 with the factorials, so there is no modular inverse to
  divide by.

## How to reason about it

- **Name the group before you write the loop.** "There's some symmetry" is not
  enough to act on. "$S_3$ on the dimensions" tells you to sort. "$D_4$ on the
  labels" tells you sorting is wrong and you must take a minimum over the group.
  "$S_c$ on the colours" tells you to look for a quantity that does not change
  under the group. The unsolved problems on this tag ask the same question about
  other groups: the rotation group of the cube for the
  [Rubik's Cube colourings](/solutions/0599/), and the symmetries of a box of dice
  in [Dice Box](/solutions/0997/). There, fixed points matter enough that
  [Burnside's lemma](https://en.wikipedia.org/wiki/Burnside%27s_lemma) is the
  tool, not a minimum over the orbit.
- **Check that the symmetry really is one.** In Cuboid Layers it is visible in the
  formula: the layer count is a function of symmetric polynomials of $a, b, c$.
  When it is not that visible, check it on small cases, by comparing the
  canonicalised count with the brute-force count of shapes.
- **Canonical forms beat dividing by $|G|$.** A sorted loop or an orbit minimum
  handles the tuples that are fixed by some symmetry automatically, such as a
  square cuboid or a quadrilateral that is its own mirror image. Dividing a
  labelled count by $|G|$ does not.
- **Look for the scalar.** When a group acts transitively on the states of a
  transfer matrix or a Markov chain, the row sums are all equal, and the
  matrix power collapses to a scalar power. That is often the difference between
  an iteration and a closed form.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0194](/solutions/0194/) — Coloured Configurations
- ○ [0392](/solutions/0392/) — Enmeshed Unit Circle
- ○ [0532](/solutions/0532/) — Nanobots on Geodesics
- ○ [0599](/solutions/0599/) — Distinct Colourings of a Rubik's Cube
- ○ [0741](/solutions/0741/) — Binary Grid Colouring
- ○ [0742](/solutions/0742/) — Minimum Area of a Convex Grid Polygon
- ○ [0997](/solutions/0997/) — Dice Box

<!-- /problems -->
