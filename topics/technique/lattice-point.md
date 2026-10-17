<!-- tags: [lattice-point] -->
<!-- status: final 2026-10-17T07:23Z -->
# Lattice point

A [lattice point](https://en.wikipedia.org/wiki/Lattice_point) is a point with integer
coordinates, and the technique this page is about is *counting them without visiting them*. Cut
the region into lines (rows, columns, or a single ray). On each line, find the first and last
integer the region allows. The line then contributes `hi - lo + 1` points, and all the work is in
getting those two endpoints exactly right. The facts about the grid itself (primitive directions
and the gcd, $r_2(n)$, Pick's theorem, choosing coordinates) are on the
[integer lattice](/topics/domain/integer-lattice) page. This page is the counting mechanics that
the five solutions below share, and the places where their C and Python versions differ.

## The idea: one exact interval per line

A region that is convex along one axis meets each line parallel to that axis in an interval.
The interval's real endpoints usually involve a division or a square root. The lattice points on
the line are the integers between the endpoints, so the per-line question is always the same: what
is the *smallest integer* satisfying the lower constraint and the *largest integer* satisfying the
upper one? A strict or non-strict inequality changes that integer, so each endpoint has to be
written to match the inequality you actually have:

| constraint | integer endpoint |
|---|---|
| $b \le p/q$ | `p // q` |
| $b > p/q$ | `p // q + 1` |
| $b \ge p/q$ | `-(-p // q)` (ceiling) |
| $u^2 \le n$ | `isqrt(n)` |
| $u^2 > n$ | `isqrt(n) + 1` |

These rows assume $q > 0$; Python's `//` floors for any sign of $p$. A line then costs $O(1)$ (or one
[integer square root](/topics/technique/integer-square-root)), and a region with $R$ lines costs
$O(R)$ instead of $O(\text{area})$. The solutions use this at three dimensions:

- **A ray (1-D).** Problem 91 walks out from a point $P$ along the primitive perpendicular step
  and asks how many steps fit in the square. That is two upper bounds, one horizontal and one
  vertical, each a floor division, and the count is their minimum. No point on the ray is ever
  generated.
- **A line in the plane (1-D, from a linear equation).** Problem 313's grids, once a BFS has
  produced the closed form for the move count (see
  [small cases reveal the closed form](/topics/takeaway/small-cases-reveal-closed-form)), are the
  integer solutions of $3b + a = u$ with $2 \le a < b$. Substitute $a = u - 3b$, and the two
  constraints become $b > u/4$ and $b \le (u-2)/3$. The count is `hi - lo + 1` with
  `lo = u // 4 + 1` and `hi = (u - 2) // 3`. These are rows two and one of the table, applied once
  per prime: a linear [Diophantine equation](/topics/domain/diophantine-equation) counted, not
  solved. The square-grid case is a single congruence check, $(t + 11) \equiv 0 \pmod 8$.
- **A region (2-D, a row sweep).** Problem 246 counts the points from which an ellipse's two
  tangents meet at more than 45°. The region is the band between the ellipse and its
  [isoptic curve](/topics/domain/isoptic-curve). Each row $v$ gives an inner bound (the first $u$
  strictly outside the [ellipse](/topics/domain/ellipse)) and an outer bound (the last $u$ strictly
  inside the isoptic). The sweep runs up from $v = 0$ until the two bounds cross.

The other two solutions use the same per-line interval to *enumerate* rather than count, because
their question is which points exist, not how many there are:

- **Points on a curve (0-D per line).** Problem 983 needs every solution of $x^2 + y^2 = N$. The
  line $x = c$ meets the circle in at most two lattice points, found by one `isqrt` and an
  is-it-a-perfect-square test. The sweep costs $O(\sqrt N)$ and yields the norm-$N$ vectors the
  rest of the search is built from.
- **Values hit by a form.** Problem 229 asks which $n \le L$ are of the form $a^2 + d b^2$ with
  $a, b \ge 1$ for each of four values of $d$. Multiplicity doesn't matter, so the solution can't
  count; it marks. For each $b$ it still computes the exact range of $a$ by `isqrt`, here clipped
  to a cache-sized window of $n$ (`amin` from $a^2 > \mathit{lo} - 1 - c$, `amax` from
  $a^2 \le \mathit{hi} - 1 - c$). Then it marks $a^2 + c$ for every $a$ in that range. The
  interval arithmetic is the same, and the cost is now the number of lattice points under the
  form, about $L$ per form.

## Endpoints you can't get from one root

Problem 246 is the case to study, because its outer endpoint is a *nested* root,
$u^2 < \mathit{base} + 2\sqrt{t}$. One `isqrt` gives a seed, but `isqrt(base + 2*isqrt(t))` can
be wrong by one in either direction, because the inner floor has already thrown away information.
The solution starts slightly above the seed and steps down until the strict inequality holds. It
tests each candidate in integers, squaring a second time:

```python
k = u * u - base
ok = k < 0 or k * k < 4 * t      # u^2 < base + 2*sqrt(t), no root taken
```

That is seed-then-correct: an approximate root picks the starting point and an exact integer
predicate decides the answer, so the result doesn't depend on how good the seed was. The inner
bound uses the same pattern from below: `isqrt(rhs // b2)`, then step up while $u^2 b^2 \le
\mathit{rhs}$, because the integer division in the seed can land one short. See
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality) for why the
predicate, not the seed, has to carry the guarantee.

Symmetry multiplies a row's count, and the multiplier follows the same endpoint discipline.
Problem 246 counts $u \ge 0$ and doubles. A row whose inner bound is $0$ contains the axis point
$u = 0$, so it contributes $2\cdot\mathit{high} + 1$, not $2(\mathit{high} - \mathit{low} + 1)$.
The $v = 0$ row is counted once and every other row twice. Problem 983 handles the same issue
when it expands $(x, y)$ into its sign variants: two variants if a coordinate is zero, four
otherwise.

## Where C and Python differ

The algorithms match line for line. The differences are in the integer primitives each language
provides.

- **The square root.** Python has an exact `math.isqrt` for integers of any size
  ([math-isqrt](/topics/technique/math-isqrt)). C doesn't, and the three C solutions each supply
  their own: Problem 246 takes `sqrtl` and corrects it with two `while` loops, Problem 983 does the
  same from a `double`, and Problem 229 uses an all-integer Newton iteration. Inputs here stay below
  $2^{53}$, where a `double` root is already within one of the answer, but the correction loops are
  what make the result exact rather than merely usually right (see
  [double-precision floating-point format](/topics/technique/double-precision-floating-point-format)).
- **Floor versus truncation.** Python's `//` rounds toward $-\infty$; C's `/` rounds toward
  zero. The table above is written for floor. Problem 313's `u / 4 + 1` and `(u - 2) / 3` are
  correct in C only because $u$ is always large and positive there. If a numerator can go negative,
  for example a lower bound that dips below the origin, the C version needs an explicit floor.
- **Overflow.** Problem 91's `x * m` fits in an `int` for the given limit, but the C code casts to
  `long long` before multiplying anyway, so the bound doesn't depend on the input. Problem 246's
  `k * k < 4 * t` is the place to check: with semi-axes in the thousands, $k^2$ peaks at a few times
  $10^{16}$, about 200 times below the `long long` limit. Python has no such check to make.
- **Marking a whole interval.** Problem 229's Python marks an interval with one
  [fancy-indexed](/topics/technique/fancy-indexing) assignment, `mark[a * a + c] = True` over an
  `np.arange`, and combines the four forms with `&=` on boolean arrays. The C version runs a scalar
  `for` loop over the same `[amin, amax]` into a byte array, then ANDs and sums in a final pass.
  The window blocking is there in both versions for the same reason: the targets $a^2 + c$ are
  spread out, and keeping them inside a window of a few tens of megabytes keeps the writes local.
- **Sign expansion.** Problem 983's Python sweeps $x$ over $[-\sqrt N, \sqrt N]$ and appends $\pm y$.
  The C version sweeps only $x \ge 0$ and writes out all four sign variants, collecting the
  $\pm$-class representatives in the same pass. Both produce the same set; C does a quarter of the
  root computations.

## How to reason about it

- **Choose the sweep axis so that every line meets the region in one interval.** If a line can
  meet it in two pieces, as in Problem 246's annulus-like band, use the symmetry (count $u \ge 0$)
  until each piece is a single interval.
- **Write every endpoint from its inequality, using the table.** Most off-by-one errors in
  lattice counting are a `<` written where the problem said `≤`, or a floor used where a ceiling
  was needed.
- **Never trust a root you can't verify.** Seed with whatever root is cheap, then correct with an
  integer comparison. With a nested root, square twice; don't compare floats.
- **Count when the question is "how many", mark when it is "which".** Problem 229 can't sum
  interval lengths, because one $n$ can have several representations. Problem 313 can, because each
  solution $(a, b)$ is a distinct grid.
- **Check the sweep against a brute force on a small case.** A double loop over a small box,
  testing the defining inequality directly, catches a lost axis row or a reversed strictness
  immediately.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
