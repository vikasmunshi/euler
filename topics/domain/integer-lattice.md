<!-- tags: [integer-lattice] -->
<!-- status: final -->
# Integer lattice

The [integer lattice](https://en.wikipedia.org/wiki/Integer_lattice) $\mathbb{Z}^n$ is the set of
points whose coordinates are all integers. It is the most natural place a geometry question can
live on a computer: no rounding, no tolerance, every coordinate an exact `int`. That is why Project
Euler keeps returning to it. Put a circle, a triangle or a parabola on the grid and ask how many
lattice points it touches, and a continuous question becomes a counting question, which you can
answer *exactly*. The forty-eight problems below vary a great deal on the surface, from right
triangles and tilted rectangles to hyperballs, tangent ellipses and hexagonal orchards. Underneath,
they lean on a short list of facts about the grid, and this page is about those facts.

## Three facts the grid gives you for free

**1. Directions are fractions, and the gcd reduces them.** A step $(a, b)$ between two lattice
points has a *primitive* version $(a/g, b/g)$ with $g = \gcd(a, b)$, the shortest lattice step
pointing the same way. The segment from $(0,0)$ to $(a,b)$ passes through exactly $g + 1$ lattice
points, and $(a, b)$ is "visible" from the origin, with nothing in the way, exactly when $g = 1$.
Nearly every direction-sensitive question on the grid comes down to the
[greatest common divisor](/topics/domain/greatest-common-divisor). Problem 91 is the cleanest public
example. To place a right angle at $P = (x, y)$, the perpendicular step has to be the primitive
vector $(-y/m,\ x/m)$ with $m = \gcd(x, y)$, and the number of lattice points reachable along it
before you leave the square is a plain integer division:

```python
min(x * m // y, m * (coordinate_limit - y) // x)   # for m = gcd(x, y)
```

The gcd is what makes both divisions exact. A floating-point slope would get the same answer most
of the time and the wrong one on exactly the cases that matter.

Counting *distinct directions*, as opposed to points, means counting primitive vectors, and the
standard tool is [Möbius inversion](/topics/domain/mobius-function). Count every vector, then
subtract the ones whose coordinates share a factor $d$:
$\#\text{primitive} = \sum_d \mu(d)\,\#\{\text{vectors in the region scaled down by } d\}$. This
is also where the familiar density $6/\pi^2$ of
[coprime pairs](/topics/domain/coprime-integers) comes from. Problem 388 (distinct lines through
the origin in a cube) and Problem 351 (points hidden from the centre of a
[hexagonal](/topics/domain/hexagonal-lattice) orchard) are both this sum. Problems 184 and 478 use
the same fact in a different role: they group lattice points by primitive ray, so that an angular
sweep can deal with collinear points as a whole group instead of tripping over ties.

**2. Points in a region are a sum over columns; points on a curve are a number-theory function.**
The number of lattice points inside the disc $x^2 + y^2 \le r^2$ is
$\sum_{x=-r}^{r} \bigl(2\lfloor\sqrt{r^2 - x^2}\rfloor + 1\bigr)$. That is one exact
[integer square root](https://docs.python.org/3/library/math.html#math.isqrt) per column, $O(r)$
work for a count that grows like $\pi r^2$. The error term is the
[Gauss circle problem](/topics/domain/gauss-circle-problem), and the same column-by-column idea
counts the points under a parabola (Problem 403) or inside an ellipse (Problem 229). In four
dimensions (Problem 596) slicing no longer scales, and the count turns into a divisor sum through
[Jacobi's four-square theorem](https://en.wikipedia.org/wiki/Jacobi%27s_four-square_theorem),
which is the move described next for circles, two dimensions up. The points *on* a
circle are a different kind of question. $x^2 + y^2 = n$ has
$r_2(n) = 4\bigl(d_1(n) - d_3(n)\bigr)$ solutions by
[Jacobi's two-square theorem](/topics/domain/sum-of-two-squares-theorem), where $d_k(n)$ counts
the divisors of $n$ that are $k \bmod 4$. So "how many lattice points lie on this circle?" becomes
"how is the squared radius factored?". Problem 233 is that translation and nothing else; the
geometry disappears once you have written the equation down. More general shapes
$a x^2 + b xy + c y^2 = n$ lead to [binary quadratic forms](/topics/domain/binary-quadratic-form).

**3. Area is exact, and Pick's theorem ties it to the count.** The signed area of a lattice
polygon is half an integer, given by the [cross product](/topics/technique/cross-product) (the
shoelace formula), with no division and no square root. [Pick's theorem](/topics/domain/picks-theorem),
$A = I + B/2 - 1$, links that area to the number of interior points $I$ and boundary points $B$,
and $B$ is a sum of edge gcds by fact 1. So if you know the vertices, you can count every lattice
point inside a polygon without enumerating any of them. Problems 742 (minimum-area convex grid
polygons) and 453 (simple lattice quadrilaterals) live in this territory, where area, convexity
and lattice-point counts all come out of determinants.

## Moving onto the lattice

Many of these problems don't start on $\mathbb{Z}^n$. Part of the work is choosing coordinates
that put them there, and the rule is to pick a map that sends lattice points to lattice points
in both directions:

- **Translate** to a lattice-point centre. Problem 246's ellipse is centred at an integer point,
  so shifting it to the origin is a bijection on the grid and the equation loses its linear terms.
- **Scale** away the halves. Problem 147 doubles every coordinate so that the cross-hatch's cell
  centres and edge midpoints become integer points. Problem 233 writes $u = 2x - N$ so that a
  circle with centre $(N/2, N/2)$ becomes $u^2 + v^2 = 2N^2$. In both cases you then have to check
  that only the right parity class maps back to the original lattice.
- **Apply an affine map** that sends the problem's natural frame to the standard one. Problem 478
  maps the mixture simplex onto the plane with the target at the origin. The hexagonal orchard is
  the triangular lattice, which is $\mathbb{Z}^2$ under a shear, so the gcd and Möbius machinery
  carries straight over.

A map with integer entries and determinant $\pm 1$ (a *unimodular* map) keeps the lattice exactly,
so counts, gcds and areas all survive the change. Problem 507 asks for the shortest vector of a
two-dimensional sub-lattice of $\mathbb{Z}^3$. That is
[lattice reduction](https://en.wikipedia.org/wiki/Lattice_reduction): a sequence of unimodular
basis changes (the [Lagrange–Gauss](https://en.wikipedia.org/wiki/Lattice_reduction#In_two_dimensions)
step in two dimensions) that never changes which points are in the lattice, only how short the
basis vectors are.

A few of the tagged problems (331, 289, 763, 790) use the grid mostly as a *board*, cells with
neighbours, and the lattice structure there is just indexing. The habits below still apply to
them, but the three facts do the heavy lifting elsewhere.

## How to reason about it

- **Stay in integers on purpose.** Lattice inputs produce exact ties: collinear triples, points
  exactly on the boundary, rays that share a direction. Floating point turns each of those into a
  coin toss. Use `math.isqrt`, the gcd and the cross product, and compare squared lengths rather
  than lengths. See [computational geometry](/topics/domain/computational-geometry) for how much
  of the work is getting the boundary cases right.
- **Read the boundary convention as part of the problem.** "Strictly inside" versus "on or inside"
  changes $I$ versus $I + B$ in Pick's formula, and changes the $\le$ in every column count. Decide
  it once and make every predicate follow it.
- **Use symmetry, then put the axes back.** The disc, the square and the ellipse have four-fold or
  eight-fold symmetry, so count one octant and multiply, then add back the points on the axes and
  diagonals separately, since multiplying counts them more than once. That is
  [exploit symmetry](/topics/takeaway/exploit-symmetry), and most off-by-a-few errors here come
  from it.
- **Ask whether the count is a number-theory function.** If the question is about points *on* a
  curve or *along* a direction, there is usually a divisor-sum or Möbius formula behind it, and
  enumerating the points is the slow path. That is
  [reduce before coding](/topics/takeaway/reduce-before-coding) in its lattice form: a problem
  that asks about $10^{10}$ or $10^{12}$ is telling you the answer is a sum over divisors, not
  over points.
- **Brute-force the small case.** Every problem here ships small worked values. A triple loop over
  a $10 \times 10$ grid is the reference that catches a missing axis point or a gcd that should
  have been a gcd minus one.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ○ [0264](/solutions/0264/) — Triangle Centres
- ○ [0270](/solutions/0270/) — Cutting Squares
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0283](/solutions/0283/) — Integer Sided Triangles with Integral Area/perimeter Ratio
- ○ [0289](/solutions/0289/) — Eulerian Cycles
- ○ [0292](/solutions/0292/) — Pythagorean Polygons
- ○ [0295](/solutions/0295/) — Lenticular Holes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ● [0331](/solutions/0331/) — Cross Flips
- ○ [0332](/solutions/0332/) — Spherical Triangles
- ○ [0351](/solutions/0351/) — Hexagonal Orchards
- ○ [0353](/solutions/0353/) — Risky Moon
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0373](/solutions/0373/) — Circumscribed Circles
- ○ [0385](/solutions/0385/) — Ellipses Inside Triangles
- ○ [0388](/solutions/0388/) — Distinct Lines
- ○ [0403](/solutions/0403/) — Lattice Points Enclosed by Parabola and Line
- ○ [0415](/solutions/0415/) — Titanic Sets
- ○ [0450](/solutions/0450/) — Hypocycloid and Lattice Points
- ○ [0453](/solutions/0453/) — Lattice Quadrilaterals
- ○ [0465](/solutions/0465/) — Polar Polygons
- ● [0478](/solutions/0478/) — Mixtures
- ○ [0507](/solutions/0507/) — Shortest Lattice Vector
- ○ [0510](/solutions/0510/) — Tangent Circles
- ○ [0514](/solutions/0514/) — Geoboard Shapes
- ○ [0562](/solutions/0562/) — Maximal Perimeter
- ○ [0577](/solutions/0577/) — Counting Hexagons
- ○ [0579](/solutions/0579/) — Lattice Points in Lattice Cubes
- ○ [0596](/solutions/0596/) — Number of Lattice Points in a Hyperball
- ○ [0604](/solutions/0604/) — Convex Path in Square
- ○ [0662](/solutions/0662/) — Fibonacci Paths
- ○ [0664](/solutions/0664/) — An Infinite Game
- ○ [0723](/solutions/0723/) — Pythagorean Quadrilaterals
- ○ [0736](/solutions/0736/) — Paths to Equality
- ○ [0742](/solutions/0742/) — Minimum Area of a Convex Grid Polygon
- ○ [0763](/solutions/0763/) — Amoebas in a 3D Grid
- ○ [0790](/solutions/0790/) — Clock Grid
- ○ [0879](/solutions/0879/) — Touch-screen Password
- ○ [0883](/solutions/0883/) — Remarkable Triangles
- ○ [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
