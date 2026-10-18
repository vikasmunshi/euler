<!-- tags: [law-of-cosines] -->
<!-- status: final -->
# Law of cosines

The [law of cosines](https://en.wikipedia.org/wiki/Law_of_cosines),
$c^2 = a^2 + b^2 - 2ab\cos\gamma$, is how an *angle* condition on an integer triangle turns into a
*Diophantine* one. Fix the angle and the cosine becomes a constant, and the condition "the sides
are integers and the angle is $\gamma$" becomes "the integer point $(a, b, c)$ lies on one quadratic
form". Project Euler returns to this often because the interesting angles (60°, 90°, 120°, or "just
past 90°") all have rational cosines, so the form has integer coefficients and its solutions can be
*generated* rather than searched for. The three solved problems below fix the angle at 120°, 60° and
$90^\circ + \varepsilon$, and each one works by enumerating solutions of the resulting form.

## The idea — fix the angle, get a form

With $\cos\gamma = t$, the triangle condition is $c^2 = a^2 - 2t\,ab + b^2$. For the angles that
come up:

| angle $\gamma$ | $\cos\gamma$ | form | name of the triples | problem |
|---|---|---|---|---|
| 90° | $0$ | $c^2 = a^2 + b^2$ | [Pythagorean](/topics/domain/pythagorean-triple) | (background) |
| 120° | $-\tfrac12$ | $c^2 = a^2 + ab + b^2$ | [Eisenstein](/topics/domain/eisenstein-triple) | 143 |
| 60° | $\tfrac12$ | $c^2 = a^2 - ab + b^2$ | Eisenstein (60° type) | 195 |
| just obtuse | $-\tfrac{1}{2ab}$ | $c^2 = a^2 + b^2 + 1$ | "almost right-angled" | 224 |

The list is short for a reason. By [Niven's theorem](https://en.wikipedia.org/wiki/Niven%27s_theorem),
the only angles of a triangle that are a whole (or rational) number of degrees *and* have a rational
cosine are 60°, 90° and 120°. Other angles with rational cosine exist, such as $\arccos\tfrac13$,
but problems rarely name them. The last row is different in kind. The angle is not
fixed; the form $a^2 + b^2 - c^2$ is held at the constant value $-1$, which forces the angle to sit
just past 90°.

Once the problem is a form, there are two standard ways to list its solutions.

**Parametrise the conic.** Dividing by $c^2$ puts $(a/c, b/c)$ on a conic with an obvious rational
point. Every line of rational slope through that point meets the conic at exactly one more rational
point, so the rational points, and hence the primitive integer triples, come from a pair of coprime
integers $(m, n)$. For 120° this gives

$$a = m^2 - n^2,\qquad b = 2mn + n^2,\qquad c = m^2 + mn + n^2,$$

and for 60°, $a = m^2 - k^2$, $b = 2mk - k^2$, $c = m^2 - mk + k^2$. The congruence conditions
(here, on $m \pm n \bmod 3$) decide when the raw triple is primitive and when it is three times a
smaller one. This is the same derivation as [Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple#Generating_a_triple)
for the right angle, with a different conic.

**Walk the form's symmetry group.** A linear map that preserves $a^2 + b^2 - c^2$ sends solutions
at any level $k$ to solutions at level $k$. The three
[Barning–Hall matrices](/topics/technique/tree-of-primitive-pythagorean-triples) that grow the
tree of Pythagorean triples (level 0) are such maps, so applied to a root at level $-1$ they grow a
tree of almost-right-angled triangles instead. Each matrix strictly increases the perimeter, which
makes a perimeter-bounded walk finite.

The 60° and 120° forms are tied to each other by a shear:
$(a+b)^2 - (a+b)b + b^2 = a^2 + ab + b^2$. Geometrically, gluing an equilateral triangle of side $b$
onto the side $b$ of a 120° triangle produces a 60° triangle with the same third side. It is a
handy check that a parametrisation for one angle is right, given one for the other.

## How each solution uses it

**143, Torricelli triangles (120°).** At the
[Fermat–Torricelli point](/topics/domain/fermat-point) the three segments $p, q, r$ to the vertices
meet at 120° to each other, so by the law of cosines each side of the triangle satisfies
$\text{side}^2 = p^2 + pq + q^2$. The problem therefore asks for triples $p, q, r$ in which *every
pair* is an Eisenstein pair. The solution treats that as a graph: the parametrisation above, with
all multiples $k(a, b)$, lists every edge $\{p, q\}$ with $p + q$ below the limit, and a Torricelli
triple is a triangle in the graph. For each edge $(p, q)$ with $p < q$, the candidates $r$ are the
common neighbours of $p$ and $q$. A prune ($p + 2q \ge L$ means even the smallest $r > q$ is too big)
skips most edges. The problem asks for the sum of *distinct* totals $p + q + r$, so the totals go
into a set.

**195, 60° triangles with bounded inradius.** The law of cosines gives the sides and the
half-angle formula gives the inradius, $r = (s - c)\tan(\gamma/2) = (a + b - c)/(2\sqrt3)$. The
irrational factor is moved to the bound side: $r \le n$ exactly when the integer $a + b - c$ is at
most $\lfloor 2\sqrt3\,n \rfloor = \lfloor\sqrt{12n^2}\rfloor$, which `isqrt` computes with no
floating-point rounding. For the parametrised triple, $a + b - c$ comes out as $3kp$ with
$p = m - k$, divided by the triple's gcd ($3$ when $p \equiv k \pmod 3$, else $1$). Every triangle is
a multiple $d$ of a primitive one and scales $a + b - c$ by $d$, so each primitive triangle
contributes $\lfloor Q / q_\text{prim} \rfloor$ triangles at once. The non-primitive ones are never
generated. The swap $(m, k) \leftrightarrow (m, m-k)$ produces the same triangle with $a$ and $b$
exchanged, so the solution keeps only $p > k$. That also drops the equilateral triangle, which the
problem excludes because it has three 60° angles.

**224, almost right-angled triangles.** Here the form is fixed at $a^2 + b^2 - c^2 = -1$ and the
solution set is a single Barning tree rooted at $(2, 2, 3)$. The tree is symmetric under swapping
$a$ and $b$: the B-matrix branch is the diagonal $a = b$ (a Pell sequence, $2a^2 + 1 = c^2$), and
the A- and C-subtrees mirror each other. Counting each triangle once (with $a \le b$) therefore
means counting the spine and expanding only the A-child of each spine node. That
[symmetry](/topics/takeaway/exploit-symmetry) halves the walk and removes any need to deduplicate.

## Python and C

The algorithms are the same in both languages; the containers are not.

- **143** is where they differ most. Python builds a `dict` of `set`s and finds common neighbours
  with `neighbors_p & adjacency[q]`, a hash intersection. C has no set, so it stores each
  adjacency list as a growable `int` array, sorts it with `qsort`, removes duplicate entries (the
  `set` did that for free in Python), and intersects two lists with a two-pointer merge. The
  distinct totals are a Python `set` and a C bitset over $[0, L]$, summed by peeling set bits with
  `__builtin_ctzll`. Because the totals are bounded by $L$, a bitset is the natural C stand-in for
  a set of small integers.
- **195** is a line-for-line port. The only extra piece is the integer square root: Python has
  `math.isqrt`, and C takes `sqrtl` and then corrects it with a step in each direction, which is
  the usual way to get an exact floor from a floating-point root. The bound $12n^2$ is computed in
  `long long`.
- **224** uses an explicit stack in both languages (recursion depth is not a concern, but a list
  is the simpler loop). C grows its `Triple` array by doubling; the spine pushes happen before the
  growth check, which is safe only because the spine is logarithmically short.

## How to reason about it

- **Turn the angle into a form first.** "Integer sides and a 120° angle" is a problem about
  $a^2 + ab + b^2 = c^2$, and from that point on it is number theory, not trigonometry. Keep
  $\sqrt3$ and other irrationals out of the inner loop by squaring the condition or moving the
  factor onto the bound.
- **Generate primitives, then count multiples.** If the quantity being bounded (perimeter,
  $a + b - c$, a side) scales linearly with the triangle, each primitive contributes
  $\lfloor \text{bound}/\text{value} \rfloor$ in one division, as in 195. Enumerating multiples is
  needed only when they interact, as the edges of 143's graph do.
- **Check the primitivity and canonical-order conditions on small cases.** The $\bmod 3$
  conditions and the $p > k$ ordering are where these parametrisations go wrong. A brute-force
  count over small sides catches a missing factor of 3 or a double count at once.
- **When the form is not zero, look for its symmetry group.** A level set like
  $a^2 + b^2 - c^2 = -1$ has no simple chord parametrisation, but it is preserved by the same
  matrices as the Pythagorean case, and a tree walk from the smallest solution lists everything.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0496](/solutions/0496/) — Incenter and Circumcenter of Triangle
- ○ [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ○ [0919](/solutions/0919/) — Fortunate Triangles

<!-- /problems -->
