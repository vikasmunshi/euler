<!-- tags: [geometry] -->
<!-- status: final -->
# Geometry

[Geometry](https://en.wikipedia.org/wiki/Geometry) is the mathematics of shape, size, position and
space. Seventy-one problems here carry the tag, and they look wildly unalike — a spider crossing a
cuboid, a laser rattling around an ellipse, twenty-one balls stacked in a pipe, a diagonal slicing
the corner of a rectangle. What they share is not a technique but a *posture*: **the figure is
never the answer.** You are asked for a count, a length, an extremum or a threshold index, and the
drawing is only the statement of the constraint. The work is finding the algebraic object that the
picture is secretly describing, and then computing with that instead.

## The picture is not the algorithm

The most-carried takeaway across this list is
[reduce before coding](/topics/takeaway/reduce-before-coding), and geometry is where it pays best,
because a naïve transcription of the picture is almost always ruinously expensive while the
reduction is almost always cheap.

Three examples of the same move, in escalating order of how far it travels:

- **Problem 86** (public, `solutions/public/p0086/`) asks for shortest paths across the *surface* of
  a cuboid. A path constrained to faces sounds like a search. Unfold the two faces it crosses into
  one plane and it is a straight line, so its length is $\sqrt{a^2 + (b+c)^2}$ by the
  [Pythagorean theorem](/topics/domain/pythagorean-theorem) — and the geometry is gone. What remains
  is a counting problem over integer triples, which is not geometry at all.
- **Problem 587** asks for the least $n$ at which a concave sliver drops below a fraction of an
  L-shaped region. The unlock is noticing what *doesn't* vary: fix the circle radius at $1$ and the
  L-section's area is $1 - \pi/4$ for every $n$. Only the diagonal's slope changes, so the ratio is
  a closed-form function of $n$ — an arcsine and a square root — and, being monotone, it yields to
  bracketing plus [binary search](/topics/technique/binary-search-algorithm) in $O(\log n)$
  evaluations.
- **Problem 228** asks how many sides a [Minkowski sum](https://en.wikipedia.org/wiki/Minkowski_addition)
  of forty-six regular polygons has. Summing convex shapes merges their edges sorted by direction,
  and parallel edges collapse into one — so the side count is just the number of *distinct edge
  directions*. Written as fractions of a turn those directions are $m/n$, and counting the reduced
  ones is [Euler's totient function](/topics/number-theory/euler). A question about polygons becomes
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

This is the domain's sharpest hazard, and it splits cleanly in two.

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
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).

Problem 246 shows how far this can be pushed. "Does the ellipse subtend more than $45^\circ$ from
$P$?" is an inequality in $\tan\theta$, which is a ratio of surds. Squaring and clearing
denominators turns it into two integer quantities $Q$ and $D$ with the condition $Q > 0$ and either
$D \le 0$ or $Q > D^2$ — an exact predicate on lattice points, no trigonometry evaluated at all.
When a geometric condition must be tested billions of times, converting it to an integer inequality
is usually the whole solution.

**If the answer is a real number, control the error instead.** Problems 144 (reflections in an
elliptical mirror), 177 (integer-angled quadrilaterals) and 587 are genuinely continuous, and
`double` is the right tool. What makes them safe is that each avoids *accumulating* error: 144
substitutes the ray into the conic and divides out the known root at $t = 0$, so the next bounce
costs one division and no square root; 177 precomputes a sine table indexed by whole degrees and
uses the tolerance the statement itself grants; 587 evaluates a closed form rather than integrating
numerically. The discipline is the same in each — do the algebra symbolically, then evaluate once.
See [floating-point arithmetic](/topics/technique/floating-point-arithmetic).

## The four shapes these problems take

Reading across the list, nearly every problem is one of four kinds, and knowing which you are in
tells you what to look for.

**Lattice counting.** Sixteen of these also carry [integer lattice](/topics/domain/integer-lattice).
The recurring machinery is primitive direction vectors reduced by $\gcd$, counting steps to a
boundary, and quartering the work by the figure's mirror symmetries
([exploit symmetry](/topics/takeaway/exploit-symmetry)). Problem 91's $O(N^2 \log N)$ count in place
of the obvious $O(N^4)$ is the archetype.

**Integrality constraints — geometry as number theory.** Eighteen also carry
[Diophantine equation](/topics/domain/diophantine-equation): integer sides, integer area, integer
angles, integer distances. Once the shape is written algebraically the constraint is arithmetic, and
[Pythagorean triples](/topics/domain/pythagorean-triple), [Heron's formula](/topics/domain/herons-formula)
and the [law of cosines](/topics/domain/law-of-cosines) are the usual bridges from the figure to the
equation.

**Optimisation over an arrangement.** Packing, placing, cutting, maximising an area. Here the
decisive step is proving a *structural* property before choosing an algorithm. Problem 222's gap
function is concave in the neighbouring radii, which forces the optimal stack into a valley — the
smallest ball in the middle — and that shape is exactly what makes an $O(n^2)$
[dynamic programme](/topics/technique/dynamic-programming) over the two chain ends correct rather
than merely plausible. Convexity, concavity or monotonicity is the licence for bisection or DP;
without it you are guessing.

**Simulation of a process.** Reflections, rolling, rotation, motion. The trap is re-deriving the
state from scratch each step. Solve one step in closed form, verify it is exact, and iterate;
if the process is periodic, find the period instead of running it out.

## How to reason about it

- **Restate the figure as an equation before you code.** If your first instinct is to draw a grid
  and search it, you have almost certainly missed a collapse.
- **Ask what is invariant.** A quantity unchanged by scale, affine shear, rotation or reflection
  lets you replace the problem with a tidier congruent copy — and the group of symmetries usually
  divides the search space too.
- **Ask what does *not* vary with the parameter.** Problem 587's constant L-section is the whole
  solution. Isolating the one thing that moves is often the entire reduction.
- **Classify by where the special feature sits.** Right angle at $O$, at $P$, or at $Q$; tangent
  point above or below; case by case. Splitting into disjoint, individually easy cases beats one
  unified expensive search.
- **Decide the arithmetic régime before the first line.** Discrete predicate → integers, exactly;
  continuous answer → closed form evaluated once, with a stated tolerance. Mixing them is how a
  correct algorithm returns a wrong count.
- **Establish monotonicity or convexity before choosing the search.** It is what turns "find the
  least $n$" into a bisection and "find the best arrangement" into a DP.
- **Check the small case in the statement.** Every one of these problems hands you a worked example.
  A reduction that reproduces it is probably right; one that doesn't is wrong now rather than after
  an hour of runtime.

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
- ○ [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ○ [0314](/solutions/0314/) — The Mouse on the Moon
- ○ [0332](/solutions/0332/) — Spherical Triangles
- ○ [0338](/solutions/0338/) — Cutting Rectangular Grid Paper
- ○ [0353](/solutions/0353/) — Risky Moon
- ○ [0363](/solutions/0363/) — Bézier Curves
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
- ○ [0510](/solutions/0510/) — Tangent Circles
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
- ○ [0761](/solutions/0761/) — Runner and Swimmer
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
- ○ [0935](/solutions/0935/) — Rolling Square
- ○ [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0966](/solutions/0966/) — Triangle Circle Intersection
- ○ [0972](/solutions/0972/) — Hyperbolic Plane
- ○ [0985](/solutions/0985/) — Telescoping Triangles
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
