<!-- tags: [tree-of-primitive-pythagorean-triples] -->
<!-- status: final 2026-10-17T07:13Z -->
# Tree of primitive Pythagorean triples

The [tree of primitive Pythagorean triples](https://en.wikipedia.org/wiki/Tree_of_primitive_Pythagorean_triples)
(Berggren 1934, rediscovered by Barning and Hall) is a way to *walk* the primitive triples rather
than *parametrise* them. Three fixed integer matrices take any primitive triple to three larger
ones, and starting from `(3, 4, 5)` they reach every primitive triple exactly once. The
[Pythagorean triple](/topics/domain/pythagorean-triple) page covers what the triples are, where the
tree sits next to Euclid's formula, and why Problems 223 and 224 need it. This page is about the
walk: why it is a tree, how to traverse it in Python and in C, what the traversal costs, and how
the solutions below deal with roots and duplicates once the tree is applied to the "almost
Pythagorean" equations.

## The idea

### Three children, one parent

Write the triple as a column `(a, b, c)`. The three Berggren children are

| branch | child | first child of `(3, 4, 5)` |
|---|---|---|
| A | `(a − 2b + 2c,  2a − b + 2c,  2a − 2b + 3c)` | `(5, 12, 13)` |
| B | `(a + 2b + 2c,  2a + b + 2c,  2a + 2b + 3c)` | `(21, 20, 29)` |
| C | `(−a + 2b + 2c, −2a + b + 2c, −2a + 2b + 3c)` | `(15, 8, 17)` |

Producing children is the easy part. What makes this a *tree*, with no triple reached twice and
none missed, is that there is also exactly one **parent**:

$$ (a, b, c) \mapsto \bigl(|a + 2b - 2c|,\ |2a + b - 2c|,\ 3c - 2a - 2b\bigr). $$

The new hypotenuse `3c − 2a − 2b` is smaller than `c` exactly when `a + b > c`, which is the
triangle inequality, so it always holds. Repeated descent therefore has to stop, and the only
place it can stop among primitive triples is `(3, 4, 5)`. Every primitive triple has one path up
to the root, which is the same as saying it appears once in the tree below the root. That is why
the walk needs no `gcd` test, no parity filter and no visited-set. Primitivity is preserved
because the matrices have determinant ±1: a common factor of the child would also divide the
parent.

The tree is Euclid's formula seen differently. On the generator pair `(m, n)` the three branches
are `(2m − n, m)`, `(2m + n, m)` and `(m + 2n, n)`, starting from `(2, 1)`. Each of those maps
keeps `gcd(m, n) = 1` and `m − n` odd, so the conditions Euclid's loop checks are carried by the
tree for free.

Two properties matter for the walk:

- **Monotone growth.** Each child has a larger hypotenuse *and* a larger perimeter than its parent.
  For branch A the perimeter rises by `4a + 6(c − b) > 0`, and B and C are clearly larger. A
  node over the bound therefore rules out its whole subtree, so a perimeter- or
  hypotenuse-bounded walk visits only the triples under the bound plus at most three rejected
  children for each of them.
- **The leg order is set by parity, not size.** With these matrices the first leg is always the
  odd one: `(21, 20, 29)` has `a > b` and `(15, 8, 17)` has `a > b`, but `(5, 12, 13)` has
  `a < b`. Any test that cares about which leg is shorter has to normalise. Problem 139 uses
  `|a − b|` for this reason.

### The walk is a depth-first search on an explicit stack

Every solution here walks the tree [depth-first](/topics/technique/depth-first-search) from an
explicit [stack](/topics/technique/stack-abstract-data-type), and the choice matters. A
breadth-first walk would keep a whole level in memory, and the levels grow as `3ᵈ`. A depth-first
frontier holds at most two pending siblings per level, so it is `O(depth)`. The depth is set by
the slowest branch. Repeating A gives the thin triples `(2k + 1, 2k² + 2k, 2k² + 2k + 1)`, whose
hypotenuse grows only quadratically, so the depth is about `√(c_max / 2)`. Repeating B grows
geometrically, by about `3 + 2√2` per step. Recursion would work, but at a depth of thousands it
would exceed Python's recursion limit, so the stack is explicit in both languages.

Because Problem 75 is public, its perimeter generator can be shown rewritten as a tree walk. It
yields the same multiset of perimeters as the Euclid loop on the
[Pythagorean triple](/topics/domain/pythagorean-triple) page, with no `gcd` call:

```python
def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> typing.Generator[int, None, None]:
    stack = [(3, 4, 5)]
    while stack:
        a, b, c = stack.pop()
        if (p := a + b + c) > max_perimeter:
            continue                                   # prunes the whole subtree
        yield from range(p, max_perimeter + 1, p)      # the primitive and its multiples
        stack += [(a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c),
                  (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c),
                  (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)]
```

The tree gives primitives only. Scaling stays a separate step: an explicit loop over multiples
when each one must be tallied (39, 75), or a single `⌊(L − 1) / p⌋` when the property survives
scaling and only the count matters (139).

### How the solutions use it

- **39 and 75** carry the tag but enumerate with Euclid's `(m, n)` loop, which reaches the same
  primitives in a different order. For a sieve that tallies perimeters into a dense array, the
  order doesn't matter, and the loop has the advantage that its bounds invert to closed form.
- **139** has both versions side by side: `s0` is the Euclid loop with `gcd`, `s1` is the tree walk
  (plus `s2`, a Pell recurrence that skips enumeration altogether). In `s1` each node tests whether
  `|a − b|` divides `c` and adds its multiples in one division.
- **218** walks the *inner* level of a two-level structure. A perfect triangle's hypotenuse is
  `w²`, where `(u, v, w)` is itself primitive, so the walk is over triples with `w ≤ √N` and is
  bounded on `c` instead of the perimeter. The walk tests the 84-divisibility condition directly on
  every node, so the count does not rest on the divisibility argument alone.
- **223 and 224** use the property that matters most. The matrices preserve the quadratic form
  `a² + b² − c²` for any input, because they lie in the integer
  [Lorentz group](https://en.wikipedia.org/wiki/Indefinite_orthogonal_group) `O(2, 1; ℤ)`, and not
  only where the form is zero. So the same three children map solutions of `a² + b² = c² + 1` (223)
  and `a² + b² = c² − 1` (224) to more solutions of the same equation. What changes is the roots
  and the bookkeeping.

### Roots and duplicates off the Pythagorean case

Run the parent map on a solution of the "almost" equation and it still decreases `c`, until it
would leave the positive triangles. The places where it stops are the roots: `(1, 1, 1)` and
`(1, 2, 2)` for 223, and `(2, 2, 3)` alone for 224. Start the stack with *all* the roots, or a
whole family of solutions is silently missing.

The other change is symmetry. A Pythagorean triple never has `a = b` (`√2` is irrational), but
these equations do, and on a node with `a = b` two branches produce the same triangle with its legs
swapped. The two solutions remove the duplicate in different ways:

- **223** keeps every node ordered `a ≤ b` by swapping B's output legs, and on a symmetric node it
  skips branch C, which there produces the same child as A. Each node then emits two or three
  children and every triangle appears once.
- **224** uses the mirror symmetry of the whole tree: swapping the legs swaps the A and C subtrees
  and fixes B. The B branch from `(2, 2, 3)` is the diagonal spine `a = b` (a
  [Pell](/topics/technique/pells-equation) sequence `2a² + 1 = c²`), so the solution walks the
  spine once, counts each spine node, and expands only the A child of each spine node with all three
  matrices. Each mirror pair is counted once, through its A-side representative.

Both are `O(answer)` with no visited-set. The 224 approach is the more structural of the two, and
it removes the per-node `a != b` branch from the inner loop.

## Python and C

The walk is the same in both languages. What differs is what a node costs:

- **Python** pays for each node as an allocated tuple, an unpack, nine multiply-adds on
  arbitrary-precision ints, and three `append`s. That is a per-node cost the `(m, n)` loop does not
  have. In 139 the Python tree walk (`s1`, about 3.8 s) is in fact *slower* than the Euclid loop
  (`s0`, about 2.4 s), because `math.gcd` is a single C call while the tree does all its arithmetic
  in bytecode. 223, at its perimeter bound of 2.5 · 10⁷, takes over half a minute in Python
  against 0.3 s in C. The usual Python micro-tuning helps a little (223 binds `stack.append` / `stack.pop` to
  locals), but no change in Python closes a gap of that size.
- **C** reverses the 139 comparison. The tree walk is about 8× *faster* than the Euclid loop
  there (36 ms against 305 ms), because now the `gcd`, a chain of integer divisions, is the
  expensive part and the children are a few adds and shifts. The C ports keep a `Triple` struct
  stack grown by `realloc` doubling (139, 223, 224). 218 instead uses a flat `long long` array
  presized to `3 · (2 · depth + slack)` from the depth bound above, so it never grows inside the
  loop.
- **Integer width.** Children are built from `±a ± 2b + 3c`, and a pushed-but-unpruned child's
  perimeter can be up to about 7× the bound, so in C the coordinates are `long long` even when the bound fits in
  an `int` ([watch the integer width](/topics/takeaway/watch-integer-width)). They must also be
  **signed**: the intermediate `a − 2b` is negative, and with `unsigned` it would wrap before
  `+ 2c` brought it back up.
- **Prune at pop or at push.** 139 tests a child's perimeter before pushing it *and* the popped
  node after, which keeps rejected children off the stack but repeats the sum. The others push
  unconditionally and prune on pop, which is simpler and costs at most three dead entries per live
  node. Both are correct. Pick one and keep it the same in the Python and C versions.

## How to reason about it

- **Use the tree when you would otherwise filter.** If a Euclid loop would spend its time rejecting
  pairs on `gcd` or parity, or the bound is on a quantity that is awkward to invert into `(m, n)`
  limits, the tree reaches the same primitives with neither. If the loop bounds invert cleanly and
  the language makes `gcd` cheap relative to the loop body (Python), the plain loop may well win.
  Measure before choosing.
- **Use the tree when the equation is not Pythagorean but the form is.** Any `a² + b² − c² = k` is
  preserved by the same three matrices. The tree is then often the *only* reasonable generator,
  because no Euclid-style formula exists. Find the roots by descent, and handle the `a = b`
  symmetry explicitly.
- **Prune on a monotone quantity.** Hypotenuse and perimeter both grow from parent to child, so a
  bound on either prunes the whole subtree. Before pruning on any other quantity, check that it is
  monotone along all three branches. If it isn't, the cut silently loses triples.
- **Pitfalls.** Forgetting the extra roots in the almost-Pythagorean cases. Assuming `a < b` from
  the matrices. Walking breadth-first, so the frontier grows exponentially. Recursing past
  Python's recursion limit. Using unsigned arithmetic in C, where the negative intermediates wrap.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II

<!-- /problems -->
