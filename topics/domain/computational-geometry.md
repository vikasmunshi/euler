<!-- tags: [computational-geometry] -->
<!-- status: final -->
# Computational geometry

[Computational geometry](https://en.wikipedia.org/wiki/Computational_geometry) is what is left of
[geometry](/topics/domain/geometry) when the figure refuses to dissolve. On the geometry page the
recurring move is [reduce before coding](/topics/takeaway/reduce-before-coding): find the algebraic
object the picture is secretly describing and compute with that instead. The forty-six problems
here are the ones where that move only gets you halfway. You are handed five thousand segments, or
fifty thousand cuboids, or thirty-four thousand lattice points, and there is no formula that
collapses them — you have to *compute on the configuration itself*. The subject is what that costs
and how to make it exact.

## One primitive does almost all the work

Nearly every predicate in this list is the sign of a $2 \times 2$ determinant. For vectors
$u$ and $v$, the [cross product](/topics/technique/cross-product) $u \times v = u_x v_y - u_y v_x$
is twice the signed area of the triangle they span, and its sign is the *orientation*: positive
when $v$ turns counter-clockwise from $u$, negative when clockwise, zero when they are collinear.

```python
def cross(o, a, b):  # sign > 0 left turn, < 0 right turn, 0 collinear
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
```

That one three-multiplication expression, with no division and no square root, answers the
questions these problems actually ask:

| question | in terms of orientation |
| --- | --- |
| is a point inside a triangle? | the three directed edges give the same sign |
| do two segments cross properly? | each segment's endpoints straddle the other's line |
| is this vertex a convex turn? | the turn does not bend right |
| which of two directions is further counter-clockwise? | the cross product of the two directions |
| what is the area of a polygon? | the sum of the fan's signed areas |

Problem 102 is the primitive in its purest form: a fixed test point at the origin makes each edge
test a two-term cross product of vertex coordinates, and containment is "all three share a sign".
Problem 165 uses the same determinant twice — once as the denominator that detects parallelism,
once as the numerators that locate the crossing. Problem 184 sorts thirty-four thousand lattice
points by [polar angle](/topics/domain/polar-coordinate-system) and never calls `atan2` in the hot
path, because "is $P$ within a half turn ahead of $A$?" is `cross(A, P) > 0`. Problem 252 decides
convexity, emptiness and area with nothing else.

The practical consequence is worth stating plainly: **learn the orientation test, and refuse to
write anything else.** A line equation with a slope has a division and a vertical-line special
case. A comparison of angles has a transcendental function and a wrap-around at $\pi$. The
determinant has neither.

## Degeneracy is the problem, not an edge case

The naïve version of any of these algorithms is a page long and takes an afternoon. The correct
version is the same page plus a fortnight of arguing about whether an inequality is strict — and
that argument is the actual work.

Read the statements closely and you find the boundary conventions are *load-bearing*, deliberately
so. Problem 102 wants the origin strictly interior, so a vertex on an edge must not count.
Problem 165 wants *proper* intersections: shared endpoints, T-junctions and collinear overlaps are
all excluded, which is three separate exclusions dressed as one word. Problem 252 permits other
points on the perimeter of a hole but not in its interior, so its emptiness comparison is
non-strict on one side and strict on the other, and a point lying on an internal diagonal has to be
treated differently from a point lying on an edge.

[Lattice](/topics/domain/integer-lattice) inputs make this unavoidable rather than theoretical.
Among five hundred lattice points, exactly collinear triples *do* occur; on a grid of radius $105$,
$(1,0)$ and $(2,0)$ share a ray, so an angular sort has genuine ties. Problem 184's complement
count has to distinguish three collinear cases — same ray (cross $= 0$, dot $> 0$), antipodal
(cross $= 0$, dot $< 0$), and everything else — and gets the antipodal ones by a separate
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) argument over primitive
directions, because the half-open sweep provably misses them. That is
[decompose overlap](/topics/takeaway/decompose-overlap) applied to a geometric boundary.

Two habits keep this tractable:

- **Write the convention down before the first line of code.** Half-open intervals $[a, b)$,
  half-open arcs $[\theta, \theta + \pi)$, "strictly inside" versus "on the perimeter" — pick one
  and make every predicate agree with it. Problem 212's nested sweeps use half-open boxes precisely
  so that every boundary comparison stays a clean strict inequality.
- **Brute-force the small case.** Every one of these problems ships a worked example, and an
  $O(n^3)$ reference implementation over twenty points will find a sign error that a proof will
  not. Problem 184's sweep was verified exhaustively against the naïve triple loop before being
  trusted at $r = 105$.

## Integers, or a canonical rational — never a float

If a geometric quantity decides a *count*, it must be exact. This is the domain where
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality) stops being advice
and becomes a correctness requirement, because a float that is wrong in the last bit does not
produce a slightly wrong answer — it produces a different integer.

Three patterns cover almost every case:

- **Keep the denominator instead of dividing.** A segment intersection is
  $t = t_{\text{num}} / \text{denom}$; normalise the sign so $\text{denom} > 0$ and the interior
  test $0 < t < 1$ becomes $0 < t_{\text{num}} < \text{denom}$, entirely in integers. No division
  ever happens.
- **Canonicalise before comparing.** When distinctness is the question — problem 165 asks for
  distinct crossing points, not crossing pairs — represent the point as an integer triple
  $(n_x, n_y, d)$ meaning $(n_x/d, n_y/d)$, divide through by the
  [gcd](/topics/technique/greatest-common-divisor-application), and fix $d > 0$. Equal points then
  have byte-identical keys and a [sort](/topics/technique/sorting-algorithm) or a hash set
  deduplicates them exactly. See [canonical form](/topics/technique/canonical-form).
- **Carry doubled areas.** Polygon areas are half-integers; hold twice the area as an integer
  throughout and halve once at the end. Problem 252's trailing `.5` is exact rather than a rounded
  float because of this.

The cost is that intermediate values grow. Cross products of coordinates near $10^5$ are fine in
64 bits; sums of $\binom{34608}{3}$-sized counts, or products of numerators, are not. Problem 184
reaches for `__int128` in C and relies on Python's arbitrary-precision integers on the other side —
the port's only real asymmetry. [Watch integer width](/topics/takeaway/watch-integer-width) is a
standing hazard here, and it is silent when you get it wrong.

## Four ways out of the quadratic

The default cost of "consider every pair" is $O(n^2)$ and of "consider every triple" is $O(n^3)$,
and the inputs are sized so that one of those is affordable and the next one up is not. The
escapes fall into four families.

**Sort by angle, then sweep.** Ordering is the single most productive preprocessing step in the
subject, and the order is almost always angular. Problem 184 turns a two-dimensional containment
question into a one-dimensional one — the origin is inside a triangle iff no angular gap between
consecutive vertices reaches $\pi$ — then counts the *complement* with a
[two-pointer](/topics/technique/two-pointer-technique) pass over the sorted points, because the arc
boundary advances monotonically as the anchor rotates. $\binom{N}{3} \approx 7 \times 10^{12}$
triples become one $O(N \log N)$ sort. Problem 252 sorts each apex's fan by direction so that a
chain can only extend forwards, which is exactly the shape a
[dynamic programming](/topics/technique/dynamic-programming) recurrence needs; the emptiness test
and the convexity test then both reduce to prefix conditions, settled by running maxima rather than
by rescanning.

**Sweep a line and lose a dimension.** The [sweep line](/topics/technique/sweep-line-algorithm)
turns a $d$-dimensional measure into a stack of $(d-1)$-dimensional ones. Problem 212 —
[Klee's measure problem](/topics/domain/klees-measure-problem) in three dimensions — computes a
union volume by compressing distinct $x$-coordinates into slabs, measuring each slab's rectangle
union by the same trick over $y$, and each of *those* by merging $z$-intervals. Three nested
sweeps, each a dozen lines, no inclusion–exclusion over $2^k$ subsets.

**Index space, not pairs.** If interactions are local, do not enumerate pairs at all. Problem 212's
cuboids have side at most $399$, so bucketing space into a
[grid index](/topics/technique/grid-spatial-index) of cells of side $400$ means a cuboid registers
in at most eight buckets and can only meet cuboids sharing one. Fifty thousand objects, an average
of three overlaps each, and the quadratic never happens. This is
[size the work to the input](/topics/takeaway/size-work-to-the-input) in its most literal form: the
grid resolution is read off the largest object.

**Recurse on structure.** When the configuration is generated rather than given, recurse on the
generator. Problem 199 fills an [Apollonian gasket](https://en.wikipedia.org/wiki/Apollonian_gasket)
using the [Descartes circle theorem](/topics/technique/descartes-circle-theorem) — each gap is
identified entirely by its three bounding curvatures, so congruent gaps merge and $3^n$ circles
become a handful of distinct states ([exploit symmetry](/topics/takeaway/exploit-symmetry)).
Problem 226 integrates under the blancmange curve by exploiting its
[self-similarity](/topics/domain/self-similarity): on a dyadic interval the curve is a straight
chord plus a scaled copy of itself, which gives the integral in closed form and lets a
[branch-and-bound](/topics/technique/branch-and-bound-search) recursion reach eight decimals in
under two hundred interval evaluations. Problem 287's quadtree is the same idea as a data
structure: describe the region, not the pixels.

## When the answer really is a real number

A minority of these problems are genuinely continuous — an area, a crossing time, a threshold index
— and there [floating point](/topics/technique/floating-point-arithmetic) is the right tool. What
separates the safe uses from the unsafe ones is not precision but *accumulation*.

Problem 587 is the model. Fix the radius at $1$ and the L-shaped section has constant area
$1 - \pi/4$ for every $n$; only the diagonal's slope varies. The concave sliver's area is then a
[closed form](/topics/technique/closed-form-expression) — a quadratic root, an arcsine, a square
root — evaluated *once* per candidate, and because the ratio is
[monotone](/topics/technique/monotonic-function) in $n$, finding the least $n$ below a threshold is
an exponential bracket plus a [bisection](/topics/technique/binary-search-algorithm), $O(\log n)$
evaluations of an expression whose error is a few ulps. Compare the alternative: numerically
integrating a fractal-adjacent region at spacing $2^{-M}$ converges linearly, so eight decimals
would want $2^{30}$ samples. Do the calculus symbolically, then evaluate.

The division is clean, and worth deciding before you write anything:

| the answer is… | arithmetic régime |
| --- | --- |
| a count, a set size, an exact area | integers or canonical rationals, strict predicates |
| a real quantity to $k$ decimals | closed form evaluated once, error bounded not accumulated |

Mixing them is how a provably correct algorithm returns a wrong count.

## How to reason about it

- **Reach for orientation first.** Before writing a slope, an angle or a line equation, ask whether
  the sign of a cross product answers the question. It usually does, and it is exact.
- **Fix the boundary convention in writing.** Open or closed, strict or non-strict, half-open
  intervals and half-open arcs — decide once, then make every predicate obey it. Most wrong answers
  in this domain are off by exactly the degenerate cases.
- **Assume the degeneracies are present.** Lattice inputs guarantee collinear triples and shared
  rays. A pseudo-random generator over a small range guarantees coincident points. Handle them by
  construction, not by hoping.
- **Sort, then sweep.** Angular order is the preprocessing that turns pair enumeration into a
  linear pass, and it is what makes the two-pointer and prefix-maximum tricks legal.
- **Exploit locality before cleverness.** If objects are small relative to the space, a grid bucket
  beats any asymptotically superior algorithm you were about to implement.
- **Verify against brute force on the statement's example.** The naïve $O(n^3)$ version is twenty
  minutes of work and is the only thing that will catch a sign convention error.
- **Watch the width.** Doubled areas, products of numerators and $\binom{N}{3}$ counts overflow 64
  bits quietly; check the bound before the port to C, not after.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0102](/solutions/0102/) — Triangle Containment
- ● [0165](/solutions/0165/) — Intersections
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0252](/solutions/0252/) — Convex Holes
- ○ [0262](/solutions/0262/) — Mountain Range
- ○ [0270](/solutions/0270/) — Cutting Squares
- ○ [0287](/solutions/0287/) — Quadtree Encoding (a Simple Compression Algorithm)
- ○ [0292](/solutions/0292/) — Pythagorean Polygons
- ○ [0314](/solutions/0314/) — The Mouse on the Moon
- ○ [0317](/solutions/0317/) — Firecracker
- ○ [0392](/solutions/0392/) — Enmeshed Unit Circle
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0415](/solutions/0415/) — Titanic Sets
- ○ [0431](/solutions/0431/) — Square Space Silo
- ○ [0449](/solutions/0449/) — Chocolate Covered Candy
- ○ [0453](/solutions/0453/) — Lattice Quadrilaterals
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0460](/solutions/0460/) — An Ant on the Move
- ○ [0476](/solutions/0476/) — Circle Packing II
- ○ [0514](/solutions/0514/) — Geoboard Shapes
- ○ [0525](/solutions/0525/) — Rolling Ellipse
- ○ [0547](/solutions/0547/) — Distance of Random Points Within Hollow Square Laminae
- ○ [0562](/solutions/0562/) — Maximal Perimeter
- ○ [0569](/solutions/0569/) — Prime Mountain Range
- ● [0587](/solutions/0587/) — Concave Triangle
- ○ [0604](/solutions/0604/) — Convex Path in Square
- ○ [0607](/solutions/0607/) — Marsh Crossing
- ○ [0630](/solutions/0630/) — Crossed Lines
- ○ [0667](/solutions/0667/) — Moving Pentagon
- ○ [0695](/solutions/0695/) — Random Rectangles
- ○ [0702](/solutions/0702/) — Jumping Flea
- ○ [0742](/solutions/0742/) — Minimum Area of a Convex Grid Polygon
- ○ [0786](/solutions/0786/) — Billiard
- ○ [0807](/solutions/0807/) — Loops of Ropes
- ○ [0842](/solutions/0842/) — Irregular Star Polygons
- ○ [0879](/solutions/0879/) — Touch-screen Password
- ○ [0897](/solutions/0897/) — Maximal $n$-gon in a region
- ○ [0957](/solutions/0957/) — Point Genesis
- ○ [0966](/solutions/0966/) — Triangle Circle Intersection
- ○ [0972](/solutions/0972/) — Hyperbolic Plane
- ○ [0983](/solutions/0983/) — Consonant Circle Crossing
- ○ [0994](/solutions/0994/) — Counting Triangles
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
