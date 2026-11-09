<!-- tags: [geometry] -->
<!-- status: final 2026-11-09T07:10Z -->
# Geometry

[Geometry](https://en.wikipedia.org/wiki/Geometry) is the mathematics of shape, size, position and
space. Seventy problems here carry the tag, and they look wildly unalike — a spider crossing a
cuboid, a laser rattling around an ellipse, twenty-one balls stacked in a pipe, squares packed
greedily under a hyperbola, a runner chasing a swimmer round the edge of a hexagonal pool, a square
tumbling round the inside of a bigger one. What they share is not a technique but a *posture*: **the figure is
never the answer.** You are asked for a count, a length, an extremum or a threshold index, and the
drawing is only the statement of the constraint. The work is finding the algebraic object that the
picture is secretly describing, and then computing with that instead.

## The picture is not the algorithm

The most-carried takeaway across this list is
[reduce before coding](/blogs/takeaway/reduce-before-coding), and geometry is where it pays best,
because a naïve transcription of the picture is almost always ruinously expensive while the
reduction is almost always cheap.

Three examples of the same move, in escalating order of how far it travels:

- **Problem 86** (public, `solutions/public/p0086/`) asks for shortest paths across the *surface* of
  a cuboid. A path constrained to faces sounds like a search. Unfold the two faces it crosses into
  one plane and it is a straight line, so its length is $\sqrt{a^2 + (b+c)^2}$ by the
  [Pythagorean theorem](/blogs/domain/pythagorean-theorem) — and the geometry is gone. What remains
  is a counting problem over integer triples, which is not geometry at all.
- **Problem 587** asks for the least $n$ at which a concave sliver drops below a fraction of an
  L-shaped region. The unlock is noticing what *doesn't* vary: fix the circle radius at $1$ and the
  L-section's area is $1 - \pi/4$ for every $n$. Only the diagonal's slope changes, so the ratio is
  a closed-form function of $n$ — an arcsine and a square root — and, being monotone, it yields to
  bracketing plus [binary search](/blogs/technique/binary-search-algorithm) in $O(\log n)$
  evaluations.
- **Problem 228** asks how many sides a [Minkowski sum](https://en.wikipedia.org/wiki/Minkowski_addition)
  of forty-six regular polygons has. Summing convex shapes merges their edges sorted by direction,
  and parallel edges collapse into one — so the side count is just the number of *distinct edge
  directions*. Written as fractions of a turn those directions are $m/n$, and counting the reduced
  ones is [Euler's totient function](/blogs/number-theory/euler). A question about polygons becomes
  a totient sieve.

That last one is the pattern at full strength: the geometric insight is one sentence, and it
converts the problem into a different domain entirely, where the standard tools already exist.

## Pick the coordinates that make the algebra tidy

Geometric quantities are invariant under a group of transformations, and you are free to work with
whichever representative has the nicest arithmetic. This is a design decision, not a detail.

Problem 163 counts every triangle visible in a cross-hatched equilateral triangle. Equilateral
geometry means $\sqrt{3}$ everywhere. But triangle counting depends only on incidence, parallelism,
collinearity and inside-ness — all preserved by any
[affine transformation](https://en.wikipedia.org/wiki/Affine_transformation) — so the figure can be
sheared into the right triangle $\{x \ge 0,\ y \ge 0,\ x + y \le n\}$, where the six families of
drawn lines have integer equations like $x + 2y = c$. The count is unchanged and every intersection
is now a ratio of integers.

Problem 246 does the translation version: its ellipse is defined by a circle-and-point construction,
but rearranging gives $d(X,M) + d(X,G) = r$ — the classical two-focus definition — and the centre
happens to land on a lattice point, so shifting it to the origin maps lattice points bijectively
onto lattice points and reduces the conic to $u^2/a^2 + v^2/b^2 = 1$. Problem 222 picks the
*configuration*: place consecutive balls on opposite sides of the pipe axis and the axial gap
collapses to $2\sqrt{R(a + b - R)}$, one formula standing in for the whole three-dimensional
arrangement.

Before writing a line, ask which normalisation — affine, translation, rotation, scale, or a choice
of parametrisation — turns your irrational constants into integers.

## Exact where it must be, floating where it may

This is the domain's sharpest hazard. It splits into two clean cases, plus a third that sits between them.

**If a predicate decides membership, get to integers.** Any test of the form "is this a perfect
square", "do these three lines meet inside the region", "is this angle exactly right" must not be
decided by comparing floats. Problem 163 keeps Cramer's-rule intersections as integer numerators
over an integer denominator and tests containment by cross-multiplication; problem 86 rounds
$\sqrt{n}$ and squares it back rather than trusting the square root; problem 91 uses a
$\gcd$ so that both step counts divide exactly:

```python
triangles_at_p_or_q = sum(
    min(x * m // y, m * (coordinate_limit - y) // x)
    for x in range(1, coordinate_limit + 1)
    for y in range(1, coordinate_limit)
    for m in [math.gcd(x, y)]
)
```

Every operation there is integer arithmetic on a problem posed in the plane. See
[exact arithmetic for equality](/blogs/takeaway/exact-arithmetic-for-equality).

Problem 246 shows how far this can be pushed. "Does the ellipse subtend more than $45^\circ$ from
$P$?" is an inequality in $\tan\theta$, which is a ratio of surds. Squaring and clearing
denominators turns it into two integer quantities $Q$ and $D$ with the condition $Q > 0$ and either
$D \le 0$ or $Q > D^2$ — an exact predicate on lattice points, no trigonometry evaluated at all.
When a geometric condition must be tested billions of times, converting it to an integer inequality
is usually the whole solution.

Problem 998 shows why no tolerance can stand in for that conversion. It asks which integer-sided
triangles fit a minimum bounding square of integer side. A brute-force minimiser with a $10^{-7}$
tolerance accepts the triangle $(21, 23, 24)$, whose best square is $20.9998\ldots$; tighten it to
$10^{-11}$ and it still accepts a whole family led by $(55, 61, 62)$, whose square falls short of
$55$ by about $3.6 \times 10^{-13}$. Every epsilon has a near-miss below it. The fix was to show
that the deciding condition, "the apex angle is at least $45^\circ$", is by the tangent addition
formula the integer inequality $s^2 - (x+y)s - xy \le 0$, and to test that instead.

**If the answer is a real number, control the error instead.** Problems 144 (reflections in an
elliptical mirror), 177 (integer-angled quadrilaterals) and 587 are genuinely continuous, and
`double` is the right tool. What makes them safe is that each avoids *accumulating* error: 144
substitutes the ray into the conic and divides out the known root at $t = 0$, so the next bounce
costs one division and no square root; 177 precomputes a sine table indexed by whole degrees and
uses the tolerance the statement itself grants; 587 evaluates a closed form rather than integrating
numerically. The discipline is the same in each — do the algebra symbolically, then evaluate once.
See [floating-point arithmetic](/blogs/technique/floating-point-arithmetic).

One problem can need both régimes, and the job is to sort its quantities between them
([exact where possible, numeric where necessary](/blogs/takeaway/exact-where-possible-numeric-where-necessary)).
Problem 363 fits a cubic [Bézier curve](https://en.wikipedia.org/wiki/B%C3%A9zier_curve) to a
quarter circle and asks how much longer the curve is. The constraint is on *area*, and
[Green's theorem](/blogs/technique/greens-theorem) makes area algebraic. Writing the area as
$\tfrac12\oint (x\,dy - y\,dx)$, the two radial sides contribute nothing, so only the curve counts,
and its integrand is a polynomial in $t$. The area is therefore an exact quadratic in the control
parameter, and solving it is one use of the quadratic formula. *Length* is
$\int \sqrt{x'^2 + y'^2}\,dt$: the square root of a quartic, with no elementary antiderivative.
Only that integral is done numerically, with the [Romberg method](/blogs/technique/romberg-method),
which reaches double precision on a smooth integrand and reports when it has converged. That
matters here because the curve hugs the circle to within a few parts in $10^7$, so the length is
needed to about twelve digits.

**If a discrete answer rests on real comparisons, make them agree with each other.** Problem 247
breaks the clean split. Squares are packed greedily under $y = 1/x$, and the answer is a *rank*: a
count of the squares at least as large as a given one. That is an integer, but it is decided by
comparing millions of nearly equal real side lengths, each the root of $(x + s)(y + s) = 1$ with
nested square roots in its corner, so there are no integers to retreat to. Two choices make plain
`double` correct anyway. First, how the root is written. The textbook form
$s = \bigl(\sqrt{(x-y)^2 + 4} - (x+y)\bigr)/2$ subtracts two nearly equal numbers once $x$ is large,
which is [catastrophic cancellation](/blogs/technique/catastrophic-cancellation). The equivalent
$s = 2(1 - xy)/\bigl((x+y) + \sqrt{(x-y)^2 + 4}\bigr)$ adds them instead and keeps every digit
([rearrange to avoid cancellation](/blogs/takeaway/rearrange-to-avoid-cancellation)). Second, the
threshold is computed along the same sequence of operations that the counting walk later repeats,
so the two values are bit-for-bit identical and a plain `<` puts the boundary square on the right
side with no epsilon. Comparisons do not need exact values; they need values computed the same way.

## The four shapes these problems take

Reading across the list, nearly every problem is one of four kinds, and knowing which you are in
tells you what to look for.

**Lattice counting.** Fifteen of these also carry [integer lattice](/blogs/domain/integer-lattice).
The recurring machinery is primitive direction vectors reduced by $\gcd$, counting steps to a
boundary, and quartering the work by the figure's mirror symmetries
([exploit symmetry](/blogs/takeaway/exploit-symmetry)). Problem 91's $O(N^2 \log N)$ count in place
of the obvious $O(N^4)$ is the archetype.

**Integrality constraints — geometry as number theory.** Eighteen also carry
[Diophantine equation](/blogs/domain/diophantine-equation): integer sides, integer area, integer
angles, integer distances. Once the shape is written algebraically the constraint is arithmetic, and
[Pythagorean triples](/blogs/domain/pythagorean-triple), [Heron's formula](/blogs/domain/herons-formula)
and the [law of cosines](/blogs/domain/law-of-cosines) are the usual bridges from the figure to the
equation. The bridge is half the work; the other half is replacing a search over the equation's
solutions with a *parametrised family* of them. The recent solves show three steps that keep
recurring.

1. *Show that rationality forces integrality.* In problem 309 (the
   [crossed ladders](/blogs/domain/crossed-ladders-problem)) the crossing height satisfies
   $1/h = 1/a + 1/b$, where $a$ and $b$ are the heights the ladders reach on the walls. Those heights
   start out only as square roots. If $a$ were irrational, $1/a + 1/b$ could be rational only with
   $a$ and $b$ sharing the same surd, and then $1/h$ would be irrational. So $a$ and $b$ are
   integers, and the figure is two [Pythagorean triples](/blogs/domain/pythagorean-triple) sharing
   the leg $w$. Problem 510 makes the same move: three circles tangent to a line satisfy
   $1/\sqrt{r_C} = 1/\sqrt{r_A} + 1/\sqrt{r_B}$, a degenerate case of
   [Descartes' theorem](/blogs/technique/descartes-circle-theorem) in which the line is a circle of
   curvature zero. Integer radii force $\sqrt{r_A r_B}$ to be rational, so $r_A / r_B$ is the square
   of a reduced ratio $u/v$.
2. *Write the solutions down instead of searching for them.* Once the ratio is reduced, a short
   coprimality argument gives problem 510 the complete family
   $\bigl(t\,u^2(u+v)^2,\ t\,v^2(u+v)^2,\ t\,u^2v^2\bigr)$, with each solution appearing exactly once
   ([parametrise by reduced ratio](/blogs/takeaway/parametrise-by-reduced-ratio)). Problem 962
   needs a stronger tool. Its perfect-square condition on a bisector-and-tangent length reduces to
   the conic $g^2 - w^2 = D m^2$, which has the obvious rational point $(1:1:0)$. Every line through
   that point with rational slope $\beta/\alpha$ meets the conic in exactly one other rational
   point, and that point is a quadratic polynomial in $(\alpha, \beta)$. This is the
   [rational parametrisation of a conic](/blogs/technique/rational-parametrization-of-a-conic),
   the same chord trick that yields [Euclid's formula](/blogs/technique/euclids-formula) for
   Pythagorean triples, applied to a conic of a different shape.
3. *Sum the scale factor in closed form.* Every family has a free multiplier, $t$ in problem 510 and
   $\lambda$ in problem 962, and a loop over it brings back the linear cost the parametrisation
   removed: problem 510's smallest pair alone has $n/4$ multiples. Instead, $\lfloor N/\text{base}
   \rfloor$ counts the multiples and a triangular number sums them
   ([closed form over iteration](/blogs/takeaway/closed-form-over-iteration)).

Gluing two right triangles along a common leg is a shape in its own right. Problem 309 does it with
the two ladders. Problem 998 does it with a triangle split by its height onto a base lying along a
side of the square. Both reduce to the same computation: generate every triple once from Euclid's
formula, bucket the triples by the shared leg, and test pairs within each bucket
([aggregate by value](/blogs/takeaway/aggregate-by-value)). The cost is $\sum_w k_w^2$, where $k_w$
is the number of triples with leg $w$. Most legs belong to only a few triples, so the sum stays
small, and the search over all side lengths never happens.

**Optimisation over an arrangement.** Packing, placing, cutting, maximising an area. Here the
decisive step is proving a *structural* property before choosing an algorithm. Problem 222's gap
function is concave in the neighbouring radii, which forces the optimal stack into a valley — the
smallest ball in the middle — and that shape is exactly what makes an $O(n^2)$
[dynamic programme](/blogs/technique/dynamic-programming) over the two chain ends correct rather
than merely plausible. Problem 247's greedy packing has a structural property of a different kind:
each square splits what it leaves behind into exactly two regions of the *same shape* as the
original, one to its right and one above it, each described entirely by its corner. So the packing
is a [binary tree](/blogs/domain/binary-tree), and a square's index is the count of right and up
steps on its path. Sides shrink down every branch, so a
[depth-first search](/blogs/technique/depth-first-search) can drop a whole subtree as soon as it
falls below the threshold, and it never has to sort anything. Convexity, concavity, monotonicity or
self-similarity is the licence for bisection, DP or pruning; without it you are guessing.
Problem 998 replaces the search by listing where the optimum can be. A bounding square is fixed
by its tilt $\theta$, and its side is the upper envelope of six sinusoidal arcs, one per edge and
axis. The minimum of such an envelope sits either at the bottom of one arc or where two arcs cross.
An arc's bottom gives side $L/\sqrt2$, which is never an integer, so only crossings remain. They
come in two geometric kinds, height crossings and corner crossings, and each can be enumerated
directly. No angle is ever searched.

**Motion — simulated or played.** Reflections, rolling, rotation, pursuit. When the motion is a
process, the trap is re-deriving the state from scratch each step. Solve one step in closed form,
verify it is exact, and iterate; if the process is periodic, find the period instead of running it
out. Problem 935 takes this furthest. A small square of side $b$ rolls around the inside of a unit
square, and the question is how many steps it takes to return. The key is to stop following the
square and record only its state at each corner: the offset $y$ at which it tips into the corner.
One wall's worth of rolling is then the single map $y \mapsto 1/b - \sqrt{1 - y^2} \pmod 1$. That map
is an orientation-preserving homeomorphism of the circle, so it has a
[rotation number](/blogs/domain/rotation-number) that grows with $1/b$. The motion returns to its
start exactly when $0$ is a [periodic point](/blogs/domain/periodic-point), and for each reduced
rotation number $p/q$ there is exactly one such $b$. The step count is a simple formula in $p$ and
$q$. The geometry has now become a count of coprime pairs in a triangle, a number-theory problem,
which [Möbius inversion](/blogs/technique/mobius-function-application) handles in $O(N^{2/3})$. The
literal rolling simulator was still worth writing, as a check on the reduction rather than as the
algorithm. When the motion is a [differential game](/blogs/domain/differential-game), as in problem 761
(a swimmer trying to leave a pool before the runner on its edge reaches her landing point), you do
not simulate at all. The payoff does not depend on position, so optimal play is straight dashes at
full speed. The best landing point obeys a refraction rule much like
[Snell's law](https://en.wikipedia.org/wiki/Snell%27s_law): the swimmer meets the edge at angle
$\arcsin(1/v)$ from the normal. The question then becomes a static one about shape: is there a
central convex region where the runner is safe wherever he stands? The critical speed is the
smallest $v$ at which such a region exists. For the circle that region is a disk, and the answer is
the classical tangent escape, $\tan\theta = \theta + \pi$. For polygons it is a smaller copy of the
pool sharing its symmetry, so checking one vertex and one side covers all of them. The search over
its size uses [golden-section search](/blogs/technique/golden-section-search), and the root in $v$
uses [regula falsi](/blogs/technique/regula-falsi), because the slack is close to linear in $v$
near the root.

## How to reason about it

- **Restate the figure as an equation before you code.** If your first instinct is to draw a grid
  and search it, you have almost certainly missed a collapse.
- **Ask what is invariant.** A quantity unchanged by scale, affine shear, rotation or reflection
  lets you replace the problem with a tidier congruent copy — and the group of symmetries usually
  divides the search space too.
- **Ask whether a root must be rational, then parametrise.** Integer sides that pass through a square
  root usually force a rational ratio, and a rational ratio gives a family you can write down:
  Euclid's formula, a reduced ratio $u/v$, or lines through a known point of a conic. Sum the free
  multiplier in closed form; never loop over it.
- **Find the candidate points of an extremum before you search.** An envelope of smooth arcs
  bottoms out at an arc minimum or at a crossing. Listing those turns a continuous optimisation into
  a finite, and often integer, case analysis.
- **Ask what does *not* vary with the parameter.** Problem 587's constant L-section is the whole
  solution. Isolating the one thing that moves is often the entire reduction.
- **Classify by where the special feature sits.** Right angle at $O$, at $P$, or at $Q$; tangent
  point above or below; case by case. Splitting into disjoint, individually easy cases beats one
  unified expensive search.
- **Decide the arithmetic régime before the first line.** Discrete predicate → integers, exactly;
  continuous answer → closed form evaluated once, with a stated tolerance; a count over real
  comparisons → cancellation-free formulas, with every compared value computed the same way.
  Mixing them is how a correct algorithm returns a wrong count.
- **Establish monotonicity or convexity before choosing the search.** It is what turns "find the
  least $n$" into a bisection and "find the best arrangement" into a DP.
- **Check the small case in the statement.** Every one of these problems hands you a worked example.
  A reduction that reproduces it is probably right; one that doesn't is wrong now rather than after
  an hour of runtime. Problem 761 gives two known answers, for the circle and the square, before
  asking for the hexagon, and they show the right order of work: the criterion was accepted only once
  it matched both to all eight digits, *then* applied to the hexagon. The code searches for the core
  shape instead of hard-coding one shape's algebra, so the extra polygons act as more checks
  ([calibrate theory on known answers](/blogs/takeaway/calibrate-theory-on-known-answers)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0144](/solutions/0144/) — Laser Beam Reflections
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ○ [0264](/solutions/0264/) — Triangle Centres
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0285](/solutions/0285/) — Pythagorean Odds
- ○ [0295](/solutions/0295/) — Lenticular Holes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ● [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ○ [0314](/solutions/0314/) — The Mouse on the Moon
- ○ [0332](/solutions/0332/) — Spherical Triangles
- ○ [0338](/solutions/0338/) — Cutting Rectangular Grid Paper
- ○ [0353](/solutions/0353/) — Risky Moon
- ● [0363](/solutions/0363/) — Bézier Curves
- ○ [0373](/solutions/0373/) — Circumscribed Circles
- ○ [0385](/solutions/0385/) — Ellipses Inside Triangles
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0404](/solutions/0404/) — Crisscross Ellipses
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0428](/solutions/0428/) — Necklace of Circles
- ○ [0431](/solutions/0431/) — Square Space Silo
- ○ [0460](/solutions/0460/) — An Ant on the Move
- ○ [0465](/solutions/0465/) — Polar Polygons
- ○ [0476](/solutions/0476/) — Circle Packing II
- ● [0510](/solutions/0510/) — Tangent Circles
- ○ [0525](/solutions/0525/) — Rolling Ellipse
- ○ [0532](/solutions/0532/) — Nanobots on Geodesics
- ○ [0547](/solutions/0547/) — Distance of Random Points Within Hollow Square Laminae
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ○ [0563](/solutions/0563/) — Robot Welders
- ○ [0566](/solutions/0566/) — Cake Icing Puzzle
- ○ [0579](/solutions/0579/) — Lattice Points in Lattice Cubes
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ● [0587](/solutions/0587/) — Concave Triangle
- ○ [0600](/solutions/0600/) — Integer Sided Equiangular Hexagons
- ○ [0607](/solutions/0607/) — Marsh Crossing
- ○ [0613](/solutions/0613/) — Pythagorean Ant
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0644](/solutions/0644/) — Squares on the Line
- ○ [0667](/solutions/0667/) — Moving Pentagon
- ○ [0681](/solutions/0681/) — Maximal Area
- ○ [0727](/solutions/0727/) — Triangle of Circular Arcs
- ○ [0737](/solutions/0737/) — Coin Loops
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ○ [0775](/solutions/0775/) — Saving Paper
- ○ [0786](/solutions/0786/) — Billiard
- ○ [0841](/solutions/0841/) — Regular Star Polygons
- ○ [0855](/solutions/0855/) — Delphi Paper
- ○ [0883](/solutions/0883/) — Remarkable Triangles
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0894](/solutions/0894/) — Spiral of Circles
- ○ [0897](/solutions/0897/) — Maximal $n$-gon in a region
- ○ [0904](/solutions/0904/) — Pythagorean Angle
- ○ [0914](/solutions/0914/) — Triangles inside Circles
- ○ [0919](/solutions/0919/) — Fortunate Triangles
- ● [0935](/solutions/0935/) — Rolling Square
- ● [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0966](/solutions/0966/) — Triangle Circle Intersection
- ○ [0985](/solutions/0985/) — Telescoping Triangles
- ● [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
