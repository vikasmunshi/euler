<!-- tags: [fractal] -->
<!-- status: final 2026-10-18T12:36Z -->
# Fractal

A [fractal](https://en.wikipedia.org/wiki/Fractal) has detail at every scale: zoom in anywhere and
there is more structure, never a smooth piece. That is what makes fractal problems awkward for
ordinary numerics. Sampling, quadrature and "refine until the digits settle" all assume that the
object looks simple once you get close enough, and a fractal never does. The three solved problems
below ask for a number about a fractal (an uncovered area, an area under a curve, a bounding box),
and each gets an exact or rigorously bounded answer without ever resolving the infinite detail.
How the recursion is turned into code (summarising a copy, collapsing identical copies, descending
to a prefix) is the subject of the [self-similarity](/topics/domain/self-similarity) page. This
page is about the fractal half of the story: why brute-force resolution fails, and what goes in
its place.

## The idea — infinitely many pieces, geometrically small

Every fractal here is the limit of a construction that replaces each piece by a few smaller ones:

| problem | one step of the construction | pieces after $n$ steps | size of a piece |
|---|---|---|---|
| 199 Iterative Circle Packing | a curvilinear gap gets its inscribed circle, leaving 3 gaps | $4 \cdot 3^n$ gaps | shrinks with curvature |
| 226 A Scoop of Blancmange | a dyadic interval splits in two; the curve on it is chord + a scaled copy | $2^n$ intervals | width $2^{-n}$ |
| 395 Pythagorean Tree | a square sprouts two similar squares | $2^n$ squares | $r^n$, $r = \max(a, b)/c$ |

Two things follow from that table. First, the piece count grows exponentially, so the cost of
reaching accuracy $\varepsilon$ by visiting every piece is roughly $\varepsilon^{-D}$, where $D$ is
the [fractal dimension](https://en.wikipedia.org/wiki/Fractal_dimension). The
[Apollonian gasket](https://en.wikipedia.org/wiki/Apollonian_gasket) of 199 has $D \approx 1.3057$,
and the area it leaves uncovered tends to zero, but slowly. Second, each piece is a
[contraction](/topics/domain/contraction-mapping) of its parent, so whatever lies below level $n$
fits inside a region of size $O(r^n)$. The first fact says you cannot enumerate your way to the
limit. The second says you do not need to: the tail is bounded, and you can stop where the bound
drops below the tolerance.

## Why the naive numerics fail

Problem 226 shows the failure most clearly. The
[blancmange (Takagi) curve](https://en.wikipedia.org/wiki/Blancmange_curve)
$T(x) = \sum_n s(2^n x)/2^n$, with $s$ the distance to the nearest integer, is continuous but
nowhere differentiable. On a dyadic interval of width $w$ it equals the chord between its endpoints
plus a copy of $T$ shrunk by $w$ in both directions. Since $\int_0^1 T = \tfrac12$, the
[trapezoidal rule](/topics/technique/trapezoidal-rule) on that interval misses by exactly $w^2/2$.
Summed over a unit length, the error is exactly $w/2$. That is linear convergence, against the
$O(w^2)$ the rule gives a smooth function, so eight decimals by plain quadrature would take about
$10^8$ intervals, and the circle's boundary still has to be handled on top of that.

The fix is to turn the same self-affinity around. It makes the error *exactly* computable, so it
can be added back: $\int_a^b T = w\,(T(a)+T(b))/2 + w^2/2$. It also gives a guaranteed envelope:
$T$ never rises more than $2w/3$ above its chord. With an exact integral and a hard bound for every
dyadic interval, the solution never approximates the fractal at all. It *certifies* intervals. An
interval whose envelope lies inside the disk is integrated in closed form (Takagi part minus the
circular-segment part). One whose envelope lies below the disk contributes zero. Only the intervals
where the curve actually crosses the circle's lower arc are subdivided. Those form a set much
thinner than the curve, so well under a thousand interval evaluations reach eight decimals.

## Three ways to stop the recursion

Since a fractal has no bottom level, the real design decision in each solution is where to stop and
why that is safe.

- **The problem stops it (199).** The packing runs for a fixed number of iterations, so nothing is
  truncated and the only question is cost. Each new circle's curvature comes from the
  [Descartes circle theorem](/topics/technique/descartes-circle-theorem), and its area is
  $(1/k)^2$ of the unit disk. Every gap is determined by its curvature triple, so the Python side
  keeps a multiset of triples and does one step per *distinct* gap shape rather than per gap.
- **Exact local information stops it (226).** An interval stops being refined as soon as it is
  certified, so the depth adapts to where the curve meets the circle. A hard floor at $2^{-45}$
  covers the measure-zero tangencies, and the residue left there is far below the eighth decimal.
  Dyadic endpoints matter here as well. At $x = i/2^k$ the Takagi series has only $k$ non-zero
  terms, and each term is a rational with power-of-two denominator, so every $T(a)$ the method uses
  is computed exactly in integer arithmetic rather than by truncating an infinite sum.
- **A contraction bound stops it (395).** The tree is the attractor of two complex similarities,
  and its bounding box comes from the [support function](/topics/technique/support-function) in
  the four axis directions. The solution finds a disk the two maps send into itself
  ($|f(c) - c| + |w|\,R \le R$), so at depth $n$ every subtree lies inside a disk of radius
  $r^n R$. It picks $n = \lceil \log(\varepsilon / 2R) / \log r \rceil$, which is a couple of
  hundred levels for the 3-4-5 tree. Then it runs the depth DP twice, once replacing the deeper
  tree by the bare square (which can only under-reach) and once by the whole disk (which can only
  over-reach). The true extent lies between the two, and the gap between them is the error bar.
  It is printed under `--show`.

The common rule: **derive the stopping depth from the contraction ratio and the size of a bounding
region, not from watching the output stop changing.** A fractal's extremes can be set by a branch
many levels down, and when two branches nearly tie for an extreme, the output can sit still for a
while and then move. That is why 395 computes a bracket instead of trusting convergence.

## Python and C

The algorithms match on both sides. Where the languages differ, the difference is in how each one
pays for the infinite structure:

- **Collapse versus enumerate (199).** The Python side merges congruent gaps in a `dict` keyed by
  the sorted curvature triple. The C side recurses over every gap, $4 \cdot 3^n$ of them, which is
  around $10^5$ calls at the requested depth and so still instant. That is the
  $\varepsilon^{-D}$ cost model above, accepted deliberately because $n$ is small. At a larger
  depth only the collapsed version would survive.
- **Exact dyadic values (226).** Python's unbounded `int` makes `(i << n) % 2**k` exact for any
  depth. The C side does the same with `long long`. The modulus only needs the low $k$ bits of
  `i << n`, but a *signed* shift whose result passes bit 63 is undefined behaviour, and $k + n$
  approaches 90 near the depth floor. An unsigned shift masked with `base - 1` gives the same low
  bits without relying on wraparound. Keep that in mind before raising `kmax`.
- **Explicit stacks.** 226 walks its intervals with an explicit stack in both languages. The C
  side uses a fixed 128-entry array, which is enough because a depth-first walk to depth 45 holds
  at most one pending sibling per level.
- **Complex similarities (395).** The maps $z \mapsto s + w z$ read directly as C99
  `<complex.h>` (`cabs`, `conj`, `creal`, `cpow`), so the C side is a line-for-line translation of
  the Python `complex` arithmetic. The `-inf` tail of the lower-bound run is `float('-inf')` on one
  side and `-INFINITY` on the other.

## How to reason about it

- **Do not sample a fractal.** If the integrand or boundary is fractal, a fixed-step method
  converges at best linearly. Look for the self-similarity identity that gives the exact
  contribution of a whole piece, and use it to certify pieces instead of approximating them.
- **Work out the dimension or the branching factor before choosing enumeration.** $3^n$ gaps or
  $2^n$ branches are fine at small $n$, and fatal once the tolerance forces a large one.
- **Bracket, then stop.** Two truncations, one that can only under-estimate and one that can only
  over-estimate, turn "probably converged" into a proof. The cost is running the recursion twice.
- **Choose evaluation points the fractal is simple at.** Dyadic points for Takagi, tangency
  triples for Apollonian gaps: the structure is self-similar around them, so values there are exact.

See also [Banach's fixed-point theorem](/topics/domain/banach-fixed-point-theorem), which explains
why an attractor exists and why its truncation error shrinks geometrically.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ○ [0570](/solutions/0570/) — Snowflakes
- ○ [0702](/solutions/0702/) — Jumping Flea

<!-- /problems -->
