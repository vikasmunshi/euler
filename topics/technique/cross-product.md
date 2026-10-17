<!-- tags: [cross-product] -->
<!-- status: final 2026-10-17T07:16Z -->
# Cross product

The [cross product](https://en.wikipedia.org/wiki/Cross_product) of two plane vectors,
$u \times v = u_x v_y - u_y v_x$, is a single integer when the coordinates are integers. That one
number does two jobs. Its **sign** says which way $v$ turns from $u$. Its **magnitude** is the
area of the parallelogram they span. The five problems below use nothing more than that, and they
use it for four different questions: is a point inside a triangle (102), where two segments cross
(165), which of two directions comes first around a point (184, 252, 478), and how big a polygon
is (252). The [computational geometry](/topics/domain/computational-geometry) page explains why
orientation is the primitive behind the whole domain, and how degeneracy is handled. This page is
about the operation itself: what the number means, the identities the solutions rely on, and the
one place it stops being enough on its own.

## The idea — a determinant with a sign

In three dimensions $u \times v$ is a vector perpendicular to both. Embed the plane as $z = 0$
and only the $z$ component survives, so the "2D cross product" is that component, the
$2 \times 2$ determinant

$$u \times v = \det\begin{pmatrix} u_x & u_y \\ v_x & v_y \end{pmatrix} = |u|\,|v|\sin\theta,$$

where $\theta$ is the signed angle from $u$ to $v$. Three facts follow, and each solution below
leans on one of them:

| fact | statement | used for |
|---|---|---|
| orientation | $u \times v > 0$ iff $v$ is counter-clockwise of $u$ by less than a half turn; $= 0$ iff collinear | side-of-line tests, angular comparison |
| area | $\tfrac12 \lvert u \times v \rvert$ is the area of the triangle on $u$, $v$; the signed sum over a fan is the polygon's area ([shoelace formula](https://en.wikipedia.org/wiki/Shoelace_formula)) | containment by area, polygon area |
| linearity | antisymmetric ($v \times u = -u \times v$) and bilinear, so $(a - p) \times (b - p)$ expands cleanly | solving for a crossing by [Cramer's rule](https://en.wikipedia.org/wiki/Cramer%27s_rule) |

The [handedness](https://en.wikipedia.org/wiki/Cross_product#Cross_product_and_handedness)
convention fixes "positive means counter-clockwise" with the $y$ axis pointing up. Nothing
depends on the convention, but every predicate in a solution has to use the same one.

With integer coordinates the operation is exact: two multiplications and a subtraction, no
division, no square root, no trigonometry. If $|x|, |y| \le M$ the result is bounded by $2M^2$.
For these problems that is at most about $10^7$, far inside 64 bits, so on this page the C and
Python sides never disagree about the number. They differ only in how they organise the loop
around it.

## Inside a triangle — two readings of the same three numbers

Problem 102 asks whether the origin lies inside each of a thousand triangles. With $O$ as the
test point the three edge orientations collapse to cross products of the vertices themselves,
$d_1 = A \times B$, $d_2 = B \times C$, $d_3 = C \times A$. The two solutions read those numbers
in two ways:

- **`s0`, orientation.** $O$ is inside iff it is on the same side of all three directed edges,
  that is iff $d_1, d_2, d_3$ share a strict sign. This is the textbook test, and it works for
  either vertex order because it accepts all-positive *or* all-negative.
- **`s1`, area.** $d_1 + d_2 + d_3 = (B - A) \times (C - A)$ is twice the signed area of $ABC$,
  and each $|d_i|$ is twice the area of one of the three sub-triangles at $O$. The sub-areas tile
  $ABC$ exactly when $O$ is inside. So the test is $|d_1| + |d_2| + |d_3| = |d_1 + d_2 + d_3|$,
  the equality case of the [triangle inequality](/topics/technique/triangle-inequality) for real
  numbers, which holds iff all the $d_i$ have the same sign.

The two are not quite the same predicate. `s0`'s strict signs reject a zero, so it treats the
boundary as outside. `s1` lets a zero through, so it treats the boundary as inside. The puzzle's
data never puts the origin on an edge, so both give the same count. But if a statement says
"strictly", that is the difference you have to choose deliberately. The C port follows `s0`
line for line, in `long long`.

## Where two segments cross — Cramer's rule in cross products

Problem 165 counts the distinct points where pairs of five thousand segments cross properly.
Write the segments as $p + t r$ and $q + u s$. Crossing both sides of $p + t r = q + u s$ with
$s$, then with $r$, eliminates one unknown at a time:

$$t = \frac{(q - p) \times s}{r \times s}, \qquad u = \frac{(q - p) \times r}{r \times s}.$$

The same cross product $r \times s$ is the denominator of both. When it is zero the segments are
parallel and the pair is skipped. The solution never divides. It normalises the sign so the
denominator is positive, turns $0 < t < 1$ into $0 < t_{\text{num}} < \text{denom}$, and stores
the point as the integer triple $(p_x \cdot \text{denom} + t_{\text{num}} r_x,\ \dots,\ \text{denom})$
reduced by its gcd. That is the canonical-rational pattern from the
[computational geometry](/topics/domain/computational-geometry) page. The cross product's
contribution is that the denominator and both numerators are three instances of the *same*
operation.

The two languages organise the $\binom{n}{2}$ pairs differently. C runs the double loop and
collects the triples for a `qsort`, followed by a linear count of distinct keys. Python fixes
segment $i$ as scalars and evaluates the three cross products against every later segment at once
as `int64` NumPy vectors. It filters them with a boolean mask, takes the gcd with `np.gcd`, and
deduplicates the whole set with `np.unique(..., axis=0)`. The formula is identical. Only the loop
moved into the array library, in the style of
[array programming](/topics/technique/array-programming).

## Ordering directions — the comparator that needs a half-plane split

The tempting comparator, "$a$ comes before $b$ iff $a \times b > 0$", is only valid within a half
turn. Around the full circle it is not transitive: three directions $120°$ apart each beat the
next. The exact fix is to split the circle first, then compare by cross product inside each part:

```python
def angular_cmp(a, b):  # exact total order by polar angle, starting at the +x axis
    ha = 0 if a[1] > 0 or (a[1] == 0 and a[0] > 0) else 1
    hb = 0 if b[1] > 0 or (b[1] == 0 and b[0] > 0) else 1
    if ha != hb:
        return ha - hb
    c = a[0] * b[1] - a[1] * b[0]
    return -1 if c > 0 else (1 if c < 0 else 0)
```

It returns $0$ exactly when the two directions are positive multiples of each other, which is the
tie you want on a lattice. The three problems that sort directions show three ways of getting the
order:

- **478** (`s0`, the reference solution) uses exactly this comparator, through
  `functools.cmp_to_key`. Then it sweeps a
  [two-pointer](/topics/technique/two-pointer-technique) window while `cross(i, r) > 0`, which
  measures each direction's open half-plane. That half-plane count is the
  [separating-line](/topics/domain/hyperplane-separation-theorem) argument behind the problem. The
  fast `s1` drops the sweep altogether: a symmetry argument turns the per-direction counts into a
  closed form, so no cross product is left in it.
- **252** in C splits the circle into four groups instead of two, to match where `atan2` puts its
  cut, then compares by cross product inside a group. That is the same idea, written for `qsort`.
- **184** sorts by `atan2` in both languages, but uses the float only to *order*. Every decision
  the sweep makes is exact. "Within a half turn ahead" is `cross > 0`. "Same ray" is `cross == 0`
  with a positive dot product. "Antipodal" is `cross == 0` with a negative one. A rounding wobble
  among points on one ray changes which equal-direction point is listed first, and nothing else.

Python's NumPy side of 252 cannot use a comparator at all: `argsort` takes keys, not a
comparison function. So it makes the float key safe instead. It divides every difference vector
by its gcd, so collinear directions become *identical* integer pairs and get bit-identical
`arctan2` values. Then it turns the sorted angles into integer ranks, where equal rank means
exactly collinear. Distinct reduced directions on that grid are more than $10^{-7}$ apart in angle,
far above double-precision error. This is the general trade: a C port keeps the exact comparator
because `qsort` accepts one, and a vectorised port has to build an exact *key* instead.

## Area and side — problem 252's two uses

Problem 252 looks for the largest empty convex polygon among five hundred points. The cross
product appears in it twice more. For each fan point, the sign of
$(\text{here} - \text{apex}) \times (\text{other} - \text{here})$ sorts the other points into
successors (it turns left, $> 0$) and predecessors ($< 0$), with collinear points dropped. Each
fan triangle's contribution to the area is $(\text{here} - \text{apex}) \times (\text{next} -
\text{apex})$, which is a doubled area. The dynamic programme adds up those integers and halves
once, at output, which is why its trailing `.5` is exact. Both languages compute the same two
expressions. The difference is that C does it per point in nested loops, while Python does it for
a whole ring of points as one masked NumPy expression.

## How to reason about it

- **Ask the sign before you ask the angle.** "Left or right", "inside or outside", "before or
  after within a half turn" are all sign questions, and the sign is exact. Reach for `atan2` only
  when you need an order around the whole circle and cannot write the split comparator. Even then,
  keep the decisions on cross products, as 184 does.
- **Mind the half turn.** A bare cross-product comparator is not a total order. Split the circle
  (two half-planes, or four quadrants) or anchor the comparison at one direction, as the
  two-pointer sweeps do with their `j < i + n` bound.
- **Keep the denominator.** In an intersection the cross product $r \times s$ is a denominator.
  Compare numerators against it instead of dividing, and fix its sign first.
- **Carry twice the area.** $u \times v$ is a *doubled* area, an integer. Sum doubled areas and
  halve once at the end.
- **Check the width once.** $2M^2$ for coordinates up to $M$, and roughly $M$ times that again
  when, as in 165, you multiply a cross product by a coordinate to build a numerator. At these
  sizes `long long` and NumPy `int64` are ample, but the bound is worth writing down before
  trusting it ([watch integer width](/topics/takeaway/watch-integer-width)).
- **Zero is a decision.** A cross product of zero means collinear: on the edge, parallel, or on
  the same ray. Whether that counts is in the statement, and 102's two solutions show that two
  correct-looking tests can answer it differently.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0102](/solutions/0102/) — Triangle Containment
- ● [0165](/solutions/0165/) — Intersections
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0478](/solutions/0478/) — Mixtures

<!-- /problems -->
