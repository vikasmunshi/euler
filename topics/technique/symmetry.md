<!-- tags: [symmetry] -->
<!-- status: final 2026-10-30T06:43Z -->
# Symmetry

A [symmetry](https://en.wikipedia.org/wiki/Symmetry) of a problem is a transformation that leaves
the answer, or the part of it you are computing, unchanged. Examples are permuting a cuboid's
three dimensions, reflecting a lattice region, swapping the legs of a triangle, rotating a
regular polygon, or flipping the sign of a vector. The takeaway
[exploit symmetry](/topics/takeaway/exploit-symmetry) explains the counting principle: orbits,
fixed points, Burnside. This page is about the *technique*, meaning the specific moves in code
that turn a symmetry into less work. The problems below use six of them. Each makes a search,
a sweep or a check smaller by the order of the symmetry group, and sometimes by much more.

## Six ways to use a symmetry

**1. Enumerate one canonical representative.** When the answer doesn't depend on the order of
some parameters, enumerate them in sorted order and never see a permutation twice.
Problem 126 counts cuboid layers. Its loops run over $a \le b \le c$ only, because permuting the
dimensions gives identical layer counts, and each loop's bound is the smallest value the
remaining variables could still produce. The canonical order removes duplicates *and* supplies
the pruning.

**2. Sweep a fundamental domain and multiply.** When a region is invariant under reflections,
sweep one piece of it and weight each point by the size of its orbit. Problem 246 counts lattice
points from which an ellipse is seen under a large angle. The ellipse's centre is a lattice point
and its axes are aligned, so the two mirror symmetries reduce the sweep to a quarter-plane.
Points on an axis are their own mirror images and are counted once, not twice. Problem 210 uses
the antipodal map $(x, y) \mapsto (-x, -y)$ of the
[taxicab](https://en.wikipedia.org/wiki/Taxicab_geometry) diamond, which flips the sign of
$x + y$. That turns a half-plane count into a closed form.

**3. Use the symmetry of a row to stop early.** Problem 53 counts binomial coefficients above a
threshold. Each row of [Pascal's triangle](/topics/technique/pascals-triangle) is symmetric, and it
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

## How to reason about it

- **Write down the group, then decide where it acts.** List the transformations that fix the
  problem: permutations, reflections, rotations, sign changes, the swap of two players or two
  legs. Then ask whether each acts on the *inputs* (enumerate canonically), on the *region*
  (sweep a fundamental domain), on the *generator* (prune mirror subtrees), on the *candidate*
  (check one representative) or on the *labels* in a state (keep only their equality pattern).
- **Account for points the symmetry fixes.** Axis points in 246, the diagonal in 224, the middle
  entry of an even Pascal row in 53. A point mapped to itself is one point, so it gets weight
  one. Most symmetry bugs are double-counted fixed points.
- **Don't assume the optimum is symmetric. Check it.** It's tempting to search only symmetric
  candidates because the container is symmetric, but a symmetric problem can have an asymmetric
  optimum. 761 restricted its search to regular cores and then ran a free-form search over other
  shapes, which found nothing better. 983's claim that only the sign parity matters was confirmed
  by brute force over random class sets.
- **Verify the invariance on a small case.** Fold the computation by the symmetry and compare it
  with the unfolded brute force on a small input, as 670 did against a full enumeration of
  colourings up to $n = 7$. An invariance that is almost true corrupts the
  answer silently, and a small case catches it immediately.
- **Expect more than a constant factor sometimes.** A reflection halves the work and a dihedral
  group divides it by $2n$. 983's sign collapse turns $2^{K-1}$ tests into $2$, an exponential
  saving, which keeps its expensive exact test cheap wherever it is needed.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0670](/solutions/0670/) — Colouring a Strip
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
