<!-- tags: [pythagorean-theorem] -->
<!-- status: final 2026-10-18T10:22Z -->
# Pythagorean theorem

The [Pythagorean theorem](https://en.wikipedia.org/wiki/Pythagorean_theorem) says the legs and
hypotenuse of a right triangle satisfy $a^2 + b^2 = c^2$. Its converse says that equation forces a
right angle. Integer solutions, the [Pythagorean triples](/topics/domain/pythagorean-triple), have
their own page and their own [tree](/topics/technique/tree-of-primitive-pythagorean-triples). This
page is about the theorem as a *step* in a solution: how a spider's route, a right angle on a grid,
an isosceles triangle and a fractal each turn into $a^2 + b^2 = c^2$, and what to do with the
equation once you have it. In each problem below the work is in finding the right triangle. After
that the theorem turns geometry into algebra, and the algebra is usually easier.

## The idea

There are three readings of the same identity, and the problems use all of them:

- **Distance.** The Euclidean length of $(x, y)$ is $\sqrt{x^2 + y^2}$. Asking for an *integer*
  length means asking for a square sum, and that is a number-theory question.
- **Orthogonality.** By the converse, $\vec u \perp \vec v$ exactly when
  $|\vec u|^2 + |\vec v|^2 = |\vec u - \vec v|^2$. That expands to the
  [dot product](https://en.wikipedia.org/wiki/Dot_product) $\vec u \cdot \vec v = 0$, which on
  integer points is exact integer arithmetic with no square roots.
- **Similarity.** A right triangle with legs $a, b$ and hypotenuse $h$ contains two smaller right
  triangles similar to it, with scale factors $a/h$ and $b/h$, and $(a/h)^2 + (b/h)^2 = 1$. The
  theorem is the statement that the two scales are complementary.

## Four problems, four right triangles

**Unfolding: 86.** The shortest path a spider can walk over the surface of an $a \times b \times c$
cuboid becomes a straight line once the two faces it crosses are unfolded flat. With $a \ge b \ge c$
the best unfolding gives $\sqrt{a^2 + (b + c)^2}$, the hypotenuse of a right triangle with legs $a$
and $b + c$. Integer length means $a^2 + s^2$ is a perfect square with $s = b + c$. Since the test
only depends on $s$, the search loops over $(a, s)$ and counts the $(b, c)$ pairs per $s$ in closed
form, which is far fewer square tests than looping over $(a, b, c)$. The theorem reduced a
3D-geometry question to "is this a square?", and the substitution $s = b + c$ followed from the
formula.

**A right angle on a lattice: 91.** Count triangles $OPQ$ with a right angle, where $P$ and $Q$
are lattice points in $[0, N]^2$. A right angle at $P = (x, y)$ means $Q - P \perp P$, so $Q$ lies on
the line through $P$ in direction $(-y, x)$. Dividing by $m = \gcd(x, y)$ gives the shortest lattice
step along that line, and the count is how many steps fit in the grid. That makes the problem
$O(N^2 \log N)$ instead of a four-coordinate search. Brute force would test the theorem itself on
every triple of points. The solution instead solves the orthogonality condition directly for the
points that satisfy it.

**The altitude of an isosceles triangle: 138.** The altitude from the apex bisects the base, so leg
$L$, half-base $k$ and height $h$ form a right triangle, $L^2 = h^2 + k^2$. With $h = 2k \pm 1$ and
completing the square, this becomes $(5k \pm 2)^2 - 5L^2 = -1$, a negative
[Pell equation](/topics/technique/pells-equation). Its solutions come from a linear recurrence
$(x, y) \to (9x + 20y,\ 4x + 9y)$, so the triangles are generated directly instead of searched for.
The theorem supplies one quadratic Diophantine equation, and the problem is mostly that equation.

**Similar copies: 395.** The Pythagorean tree puts a right triangle on top of a square, then squares
on both legs, and repeats. Each leg square is the parent scaled by $b/h$ or $a/h$ and rotated. The
right angle gives the key fact: the two child rotations differ by exactly $\pi/2$, since
$\arg(1 - w) = \arg w - \pi/2$ in the solution's complex coordinates. So after $n$ steps with $m$
right turns, a subtree's orientation depends only on $n$ and $m \bmod 4$. The exponential tree of
subtrees collapses into a four-wide DP over depth for the bounding box. Here the theorem appears as
the geometry of [similar](/topics/domain/similarity-geometry) triangles, not as an equation on
side lengths.

## Keep the square, drop the root

In three of the four problems the square root never needs to be taken. 91 tests orthogonality
with an integer dot product. 138 works with $L^2$ inside a Pell equation. 86 needs to know whether
$a^2 + s^2$ is a perfect square, and the two languages answer that differently:

| | Python | C |
| --- | --- | --- |
| 86 square test | `math.sqrt(a**2 + s**2).is_integer()` | round the `sqrt`, then `isq * isq == val` |
| 91 lattice step | `math.gcd`, exact `//` | `int m = gcd(x, y)`, cast to `long long` before `x * m` |
| 138 Pell values | built-in `int` | a base-$10^9$ limb `BigInt` with just add, scalar multiply, divide and mod by 5 |
| 395 rotations | Python `complex` | `<complex.h>`, matching to every printed digit |

86's Python float test is exact only because $a^2 + s^2$ stays below about $6.6 \times 10^6$, far
under $2^{53}$. The C version confirms its rounded root with an integer square, which stays correct
at any size (see [sqrt](/topics/technique/sqrt) for the general rule). 138 is the other extreme: the
leg lengths grow exponentially, and the 96th has over 120 digits. Python does not need to change
anything, while the C needs its own big-integer type. When the theorem leads to a recurrence, check
the growth rate before choosing the integer type.

## How to reason about it

- **Look for the right triangle.** Unfold a surface, drop an altitude, read a perpendicular step.
  The theorem only helps once some length is a hypotenuse.
- **Integer length means a square sum.** Turn it into a Pythagorean-triple or perfect-square
  question, and substitute away variables that appear only through a sum.
- **Right angles are dot products.** On lattice points, test or solve $\vec u \cdot \vec v = 0$ in
  integers, and use the gcd to find the primitive perpendicular step.
- **A fixed relation between sides plus the theorem gives a Pell equation.** Complete the square
  and generate solutions by recurrence. Expect exponential growth.
- **Similar right triangles scale by $a/h$ and $b/h$, rotated a quarter-turn apart.** In a
  self-similar construction that quarter-turn makes orientations periodic.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0395](/solutions/0395/) — Pythagorean Tree

<!-- /problems -->
