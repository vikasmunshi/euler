<!-- tags: [symmetry] -->
<!-- status: final 2026-11-09T17:07Z -->
# Symmetry

A [symmetry](https://en.wikipedia.org/wiki/Symmetry) of a problem is a transformation that leaves
the answer, or the part of it you are computing, unchanged. Examples are permuting a cuboid's
three dimensions, reflecting a lattice region, swapping the legs of a triangle, rotating a
regular polygon, flipping the sign of a vector, or reading a list backwards. The takeaway
[exploit symmetry](/blogs/takeaway/exploit-symmetry) explains the counting principle: orbits,
fixed points, Burnside. This page is about the *technique*, meaning the specific moves in code
that turn a symmetry into less work. The problems below use eight of them. Most make a search,
a sweep or a check smaller by the order of the symmetry group. The last two do more: they
replace the computation with a closed form or a recurrence.

## Eight ways to use a symmetry

**1. Enumerate one canonical representative.** When the answer doesn't depend on the order of
some parameters, enumerate them in sorted order and never see a permutation twice.
Problem 126 counts cuboid layers. Its loops run over $a \le b \le c$ only, because permuting the
dimensions gives identical layer counts, and each loop's bound is the smallest value the
remaining variables could still produce. The canonical order removes duplicates *and* supplies
the pruning. The same move works on structures, not just numbers. Problem 782 asks which counts
$k$ of ones an $n \times n$ binary matrix with few distinct rows and columns can have. It lists
block patterns only up to relabelling the blocks and complementing every entry. Complementing
keeps the complexity and sends $k \mapsto n^2 - k$, so the set of reachable $k$ is symmetric.
The code marks one half of each family and reflects it.

**2. Sweep a fundamental domain and multiply.** When a region is invariant under reflections,
sweep one piece of it and weight each point by the size of its orbit. Problem 246 counts lattice
points from which an ellipse is seen under a large angle. The ellipse's centre is a lattice point
and its axes are aligned, so the two mirror symmetries reduce the sweep to a quarter-plane.
Points on an axis are their own mirror images and are counted once, not twice. Problem 804
counts lattice points inside the ellipse $x^2 + xy + 41y^2 \le N$. Its axes are tilted, but
$(x, y) \mapsto (-x, -y)$ still preserves the form. So rows $y$ and $-y$ hold equally many points,
and row $0$ is the one that maps to itself. Problem 210 uses the same antipodal map on the
[taxicab](https://en.wikipedia.org/wiki/Taxicab_geometry) diamond, where it flips the sign of
$x + y$. That turns a half-plane count into a closed form.

The domain doesn't have to be a region. Problem 975 follows a path through the unit cube where two
height profiles agree. Both profiles satisfy $H(1 - x) = 1 - H(x)$, so the unique path from one
corner to the opposite one is its own image under the point reflection through the centre. The
walk stops halfway and doubles what it has added up. Unlike a region, a path's midpoint isn't
known in advance. The walk has to detect it: either a cell that is its own mirror, or a step
into the mirror of the cell it is leaving. Those are the fixed points again, now on a path, and
each of the two cases closes the sum differently.

**3. Use the symmetry of a row to stop early.** Problem 53 counts binomial coefficients above a
threshold. Each row of [Pascal's triangle](/blogs/technique/pascals-triangle) is symmetric, and it
increases up to the middle. So the first entry over the threshold fixes the whole qualifying
block, and the walk stops there:

```python
for r in range(0, n // 2 + 1):
    if c > threshold:
        count += n - 2 * r + 1               # entries r .. n - r all qualify, by symmetry
        break
    c = c * (n - r) // (r + 1)
```

**4. Follow the symmetry of a generator, not just the objects.** Problem 224 generates every
solution of a quadratic equation from one root by three linear maps, as a ternary tree. Swapping
the two legs conjugates one map into another and fixes the third. So one branch runs along the
diagonal of self-symmetric solutions, and the other two subtrees are mirror images of each other.
Walking the diagonal spine and expanding only one of the mirror subtrees counts each triangle
exactly once. That halves the work, and it needs no hash set to remove duplicates.

**5. Let one representative stand for all of them in a check.** When a configuration shares its
container's symmetry, a condition verified at one representative holds at every image.
Problem 761 tests whether a regular polygon inside a regular pool is safe for the runner. The
polygon has the pool's [dihedral symmetry](https://en.wikipedia.org/wiki/Dihedral_group), so one
vertex and one side stand for all of them. Even a "hugging" path that follows $j$ sides is the
first vertex's path shifted by $j$ edges. Problem 983 goes further. Its search ranges over sets of
vectors, and flipping the sign of one vector maps the projected hypercube onto a translate of
itself with centres and harmony points swapped. So the $2^{K-1}$ possible signings collapse to
just **two** genuinely different configurations, the cube and its dual, and only those two are
ever tested exactly. Problem 331's board is symmetric under $x \leftrightarrow y$, so each
column's black-disk count equals the matching row's. A formula over rows then covers the columns
for free.

**6. Quotient the state by a symmetry of the labels.** When a dynamic programme or
[transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) carries arbitrary labels,
such as colours, in its state, and the rules only ever ask whether two labels are *equal*, then
permuting the labels maps valid configurations to valid configurations. The state can forget
which labels it holds and keep only the pattern of equalities, with the number of label choices
moved into the transition weights. Problem 670 colours tilings of a $2 \times n$ strip with four
colours. A boundary state that remembers each row's colour and overhang has over a hundred
entries. But the two tiles at any boundary touch, so they always differ, and every ordered pair of
distinct colours looks the same to the future. The state shrinks to the two overhangs plus a
"vertical domino" flag, ten states in all, and a new tile that must avoid two known colours simply
contributes a weight of $2$. Matrix exponentiation costs $O(S^3 \log n)$, so cutting $S$ by an
order of magnitude cuts the work by about a thousand.

Problem 475 shows the companion move: **add labels to break a symmetry, then divide it back
out.** It counts ways to split $12n$ musicians into trios that never reuse a quartet. Unordered
trios are awkward to count, so the solution numbers them, which multiplies the count by exactly
$(4n)!$. It also forgets which member of a quartet went where, which divides by $4!$ per quartet.
What is left is a 0/1 incidence matrix between quartets and trios with fixed row and column sums.
The columns of that matrix are interchangeable too, so the row-by-row DP keeps only *how many*
columns hold 0, 1, 2 or 3 ones. That is a histogram of fill levels, $O(n^2)$ states instead of
exponentially many. The pitfall is the division. It is exact only when the group acts *freely*,
meaning no labelled arrangement is fixed by a non-trivial relabelling. Here that holds because the
trios are distinct non-empty sets. Where it fails, Burnside's lemma has to replace plain division.

**7. Pair terms by an involution and keep only the fixed points.** An
[involution](https://en.wikipedia.org/wiki/Involution_(mathematics)) is a symmetry of order two.
If it maps every term of a sum to a partner, and each pair adds up to a known constant, then the
sum collapses to a count of the terms that are their own partners. Problem 850 sums the
fractional parts $\{i^k / n\}$ over $i$. For odd $k$, $i \mapsto n - i$ sends $i^k$ to
$-i^k \pmod n$, so the residues $r$ and $n - r$ pair up and each pair contributes exactly $1$.
Only the $i$ with $n \mid i^k$ escape the pairing, so $f_k(n) = (n - z_k(n))/2$ for the number
$z_k(n)$ of such $i$. A sum of $n$ fractions becomes a count of fixed points, and that count is a
[multiplicative function](https://en.wikipedia.org/wiki/Multiplicative_function) the rest of the
solution can sum quickly. In 850 the pairing doesn't just save a factor of two. It removes the
fractional parts from the problem.

**8. Mirror a process into a smaller copy of itself.** Some processes are symmetric in time or
direction, so after one step the rest is the original process, reflected. Problem 539 removes
every other number from a list, alternating left-to-right and right-to-left passes. After the
first pass, $2, 4, \dots, 2M$ remain, and the next pass runs right to left. Read backwards, that
is the original game on $M$ items, so the survivor sits at position $P(M)$ *from the right*. The
reflection gives a [recurrence](https://en.wikipedia.org/wiki/Recurrence_relation),
$P(n) = 2(M + 1 - P(M))$ with $M = \lfloor n/2 \rfloor$, of depth $\log_2 n$. The sum of $P$ over
$1 \le k \le n$ then folds too, because $2m$ and $2m + 1$ share the same half. Without the mirror,
the right-to-left pass is a different game, and each direction would need its own recurrence.

## How to reason about it

- **Write down the group, then decide where it acts.** List the transformations that fix the
  problem: permutations, reflections, rotations, sign changes, complements, the swap of two
  players or two legs, the reversal of a list. Then ask whether each acts on the *inputs*
  (enumerate canonically), on the *region or path* (sweep a fundamental domain), on the
  *generator* (prune mirror subtrees), on the *candidate* (check one representative), on the
  *labels* in a state (keep only their equality pattern or a histogram), on the *terms of a sum*
  (pair them up) or on the *process* itself (recurse on the mirror image).
- **Account for points the symmetry fixes.** Axis points in 246, row $0$ in 804, the diagonal in
  224, the middle entry of an even Pascal row in 53, the self-mirror cell in 975. A point mapped
  to itself is one point, so it gets weight one. Most symmetry bugs are double-counted fixed
  points. In 850 the fixed points are the whole answer: everything else cancels.
- **Don't assume the optimum is symmetric. Check it.** It's tempting to search only symmetric
  candidates because the container is symmetric, but a symmetric problem can have an asymmetric
  optimum. 761 restricted its search to regular cores and then ran a free-form search over other
  shapes, which found nothing better. 983's claim that only the sign parity matters was confirmed
  by brute force over random class sets.
- **Verify the invariance on a small case.** Fold the computation by the symmetry and compare it
  with the unfolded brute force on a small input. 670 did this against a full enumeration of
  colourings up to $n = 7$, 975 against a full walk with no halving, and 539 against a direct
  simulation of the passes. An invariance that is almost true corrupts the answer silently, and a
  small case catches it immediately.
- **Expect more than a constant factor sometimes.** A reflection halves the work and a dihedral
  group divides it by $2n$. 983's sign collapse turns $2^{K-1}$ tests into $2$, an exponential
  saving. 539's mirror turns a simulation over $n$ numbers into $\log_2 n$ steps, and 850's
  pairing turns a sum of $n$ terms into a count that a multiplicative function can deliver.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0475](/solutions/0475/) — Music Festival
- ● [0539](/solutions/0539/) — Odd Elimination
- ● [0670](/solutions/0670/) — Colouring a Strip
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ● [0782](/solutions/0782/) — Distinct Rows and Columns
- ● [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ● [0850](/solutions/0850/) — Fractions of Powers
- ● [0933](/solutions/0933/) — Paper Cutting
- ● [0939](/solutions/0939/) — Partisan Nim
- ● [0975](/solutions/0975/) — A Winding Path
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
