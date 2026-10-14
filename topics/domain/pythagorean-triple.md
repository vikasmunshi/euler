<!-- tags: [pythagorean-triple] -->
<!-- status: final 2026-10-14 -->
# Pythagorean triple

A [Pythagorean triple](https://en.wikipedia.org/wiki/Pythagorean_triple) is a triple of positive
integers `(a, b, c)` with `a² + b² = c²`, the side lengths of a right triangle with integer sides.
The equation is the oldest Diophantine equation there is, and it keeps coming back because it is
completely solved: every triple comes from a two-parameter formula, the primitive ones form a
tree, and how many triples a given number belongs to is a divisor count. A problem that mentions
"integer right triangles" rarely wants you to test `a² + b² = c²`. It wants you to *generate* the
triples from one of those structures and count, sieve or prune over what comes out.

## The idea

### Primitive triples and Euclid's formula

A triple is **primitive** when `gcd(a, b, c) = 1`; every other triple is `k` times a unique
primitive one. The primitive triples are given exactly by
[Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple#Generating_a_triple):

$$ a = m^2 - n^2, \qquad b = 2mn, \qquad c = m^2 + n^2, \qquad m > n > 0,\ \gcd(m, n) = 1,\ m - n \text{ odd}. $$

Each primitive triple comes from exactly one such pair `(m, n)` (up to swapping the legs). Both side
conditions matter. Drop the coprimality and you get scaled copies. Drop the parity condition and
`m, n` both odd gives *twice* a primitive triple, which you then count a second time when you add
multiples. The formula also makes the derived quantities simple: the perimeter is `2m(m + n)` and
the area is `mn(m − n)(m + n)`, so bounds on either turn straight into loop bounds on `m` and `n`.

That gives the basic pattern: enumerate primitives, then expand each one to all its multiples under
the bound. [Problem 75](/solutions/0075/) counts perimeters up to `L` that belong to exactly one
right triangle, and its generator is that pattern in a few lines:

```python
def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> typing.Generator[int, None, None]:
    for m in range(2, int((max_perimeter / 2) ** 0.5)):
        for n in range(m % 2 + 1, m, 2):
            if math.gcd(m, n) != 1:
                continue
            p, k = (2 * m * (m + n), 1)
            while (perimeter := (k * p)) <= max_perimeter:
                yield perimeter
                k += 1
```

A tally over the yielded perimeters is a sieve: the work is the number of (triple, multiple) pairs,
which is `O(L log L)`. [Problem 39](/solutions/0039/) uses the same sieve to find the most popular
perimeter. [Problem 9](/solutions/0009/) is small enough that a direct search over `a, b` with
`c = S − a − b` is fine. That is the right call at that size, but it does not scale. The
parametrisation also handles property tests: if a property survives scaling, check it on the
primitive and add all its multiples with one division. [Problem 139](/solutions/0139/) works this
way, because its tiling condition "`|a − b|` divides `c`" scales with `k`.

### Count by factoring: the difference of two squares

To ask "how many triples contain this number?", rearrange the equation into a product. For a fixed
leg `L`, `L² = c² − b² = (c − b)(c + b)`, so triangles with leg `L` match the factor pairs `d · e = L²`
with `d < e` and `d ≡ e (mod 2)`. The count is a
[divisor function](https://en.wikipedia.org/wiki/Divisor_function) value: `(τ(L²) − 1)/2` for odd
`L`, and the same expression with `L/2` in place of `L` for even `L`.
[Problem 176](/solutions/0176/) turns this round: it fixes the count and asks for the smallest leg,
which becomes "the smallest number whose square has a given number of divisors", and that is a
search over exponent patterns.

The hypotenuse side works through [sums of two squares](https://en.wikipedia.org/wiki/Sum_of_two_squares_theorem).
`c` is the hypotenuse of a primitive triple exactly when every prime factor of `c` is `≡ 1 (mod 4)`,
and the number of ways to write `c` depends only on the exponents of those primes. The clean way to
see this is the [Gaussian integers](https://en.wikipedia.org/wiki/Gaussian_integer):
`c² = (a + bi)(a − bi)`, and Euclid's formula is just `a + bi = (m + ni)²`. Problems that ask how
often a number occurs in triples (827), or that put a triple inside another triple, reduce to
factorisation statistics like these.

### The tree of primitive triples

Every primitive triple appears exactly once in an infinite ternary
[tree rooted at (3, 4, 5)](https://en.wikipedia.org/wiki/Tree_of_primitive_Pythagorean_triples).
Its three children are the products with the Berggren (Barning–Hall) matrices, for example

$$ (a, b, c) \mapsto (a - 2b + 2c,\ 2a - b + 2c,\ 2a - 2b + 3c). $$

Each child is strictly larger than its parent, so you can walk the tree depth-first and stop at any
branch that passes the bound. You never compute a `gcd`, and the primitivity comes for free. The
property that matters more is that the matrices preserve the
[quadratic form](https://en.wikipedia.org/wiki/Quadratic_form) `a² + b² − c²` for every input, not
only where it is zero. They therefore map solutions of `a² + b² = c² + 1` or `a² + b² = c² − 1`
to other solutions of the same equation. Problems 223 and 224 ("almost right-angled" triangles)
use exactly this: start from a few small seeds, walk the tree and prune by perimeter, and the work is
proportional to the number of solutions, which is far less than any search over two sides.

### Triples inside triples, and the structure modulo small primes

The parametrisation can be nested. If `c = m² + n²` must itself be a square `w²`, then `(m, n, w)` is
a primitive triple, and the problem moves down one level. [Problem 218](/solutions/0218/) is built
on that two-level structure. Combine it with the standard divisibility facts (in every triple one leg
is divisible by 3, one leg by 4, and one side by 5, so the area is divisible by 6) and the question
answers itself with no enumeration at all. Extra linear conditions often reduce to
[Pell equations](https://en.wikipedia.org/wiki/Pell%27s_equation) instead. Legs that differ by one
give `x² − 2y² = ±1`, which is how Problem 139 drops from a loop over `L` to a recurrence with
`O(log L)` steps.

### The geometric side: rational points on the circle

Divide by `c²` and a triple becomes a rational point `(a/c, b/c)` on the unit circle. Euclid's
formula is then the [rational parametrisation](https://en.wikipedia.org/wiki/Unit_circle#Trigonometric_functions_on_the_unit_circle)
`t ↦ ((1 − t²)/(1 + t²), 2t/(1 + t²))`, with `t = n/m`. That is why triples appear in problems with
no triangle in them: lattice points on circles and hypocycloids (450), circles through lattice
points (373), angles whose sine and cosine are both rational (904), and rational rotations. If a
problem needs "a rotation that maps lattice points to rational points", it needs a Pythagorean
triple.

## How to reason about it

- **Generate, don't test.** Checking `a² + b² = c²` over pairs is `O(N²)` and spends almost all of
  its time on misses. Euclid's formula or the tree generates only hits. The number of primitive
  triples with hypotenuse `≤ N` is about `N / 2π`, and with perimeter `≤ L` about `L ln 2 / π²`, so
  generation costs about what the answer does.
- **Split into primitive and multiple.** Decide whether the property you need survives scaling. If
  it does, work on primitives and count multiples with `⌊bound / p⌋`. If it doesn't, expand each
  primitive explicitly, as Problem 75's tally does.
- **Choose the generator by the structure.** Euclid's `(m, n)` loop suits bounds on perimeter, area
  or hypotenuse that you can invert. The tree suits pruning, needs no `gcd`, and extends to the
  "almost" equations `a² + b² − c² = k`. Factorisation suits "how many triples contain `x`".
- **Count without enumerating when the bound is huge.** At bounds like `10¹⁸`, even linear
  generation is too slow. Counting primitive triples then becomes a sum over `(m, n)` with a
  [Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function) correction for coprimality
  (Problem 540 is this). It is the same move as counting coprime pairs in a region.
- **Pitfalls.** Euclid's formula without the factor `k` misses every non-primitive triple. Leaving
  out the parity or `gcd` condition counts some triples twice. The legs come out in either order
  (`m² − n²` can be larger than `2mn`), so normalise before comparing or keying a dictionary.
  Test `c` with `math.isqrt`, never with a floating-point square root.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ○ [0292](/solutions/0292/) — Pythagorean Polygons
- ○ [0295](/solutions/0295/) — Lenticular Holes
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ○ [0373](/solutions/0373/) — Circumscribed Circles
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ○ [0450](/solutions/0450/) — Hypocycloid and Lattice Points
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ○ [0613](/solutions/0613/) — Pythagorean Ant
- ○ [0723](/solutions/0723/) — Pythagorean Quadrilaterals
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0827](/solutions/0827/) — Pythagorean Triple Occurrence
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ○ [0904](/solutions/0904/) — Pythagorean Angle
- ○ [0914](/solutions/0914/) — Triangles inside Circles
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
