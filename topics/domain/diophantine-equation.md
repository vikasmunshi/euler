<!-- tags: [diophantine-equation] -->
<!-- status: final 2026-10-15T10:56Z -->
# Diophantine equation

A [Diophantine equation](https://en.wikipedia.org/wiki/Diophantine_equation) is a
polynomial equation in which only **integer** solutions are admitted. That one word —
*integer* — changes everything. Over the reals, `x² - 2y² = 1` is an unremarkable curve;
over the integers it is [Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation),
with infinitely many solutions that march off to infinity in a rigid, predictable pattern.
This is the largest single domain in the archive precisely because "which integers satisfy
this?" is the question a huge fraction of number-theory problems are really asking, once you
strip away the story about triangles, discs, or reciprocals.

## The shape of the difficulty

The defining trap of a Diophantine problem is that the solutions are sparse but can be
enormous. You cannot search for them by their magnitude. Problem 66 asks for the fundamental
solution of `x² - Dy²= 1` over `D ≤ 1000`; for `D = 661` the smallest `x` already exceeds
`10¹⁷`, so any loop bounded by the size of the answer would never finish. Most of the craft of
solving these is to **stop searching over values and start exploiting structure** — to find
the algebraic identity or the recurrence that hands you the solutions directly.

Across the problems below, the same handful of structural moves recur.

### Eliminate a variable with a linear constraint

The gentlest case. When a Diophantine system pairs a hard equation with a *linear* one, the
linear equation lets you delete a variable and collapse the search a dimension. In
[Problem 9](/solutions/0009/) — a
[Pythagorean triple](https://en.wikipedia.org/wiki/Pythagorean_triple) `a² + b² = c²` with
the side constraint `a + b + c = 1000` — you never search for `c` at all:

```python
for a in range(1, s // 4 + 1):
    for b in range(a, s // 2):
        c = s - a - b            # the linear constraint fixes c; no third loop
        if a * a + b * b == c * c:
            return a * b * c
```

Two nested loops instead of three, exact integer arithmetic instead of a floating-point
square root. The lesson generalises: a linear side-condition is a free dimension of pruning.

### Reduce to Pell's equation, then iterate a recurrence

The workhorse pattern. Many geometric or probabilistic constraints, after
[completing the square](https://en.wikipedia.org/wiki/Completing_the_square) and clearing
denominators, become a **Pell** or **Pell-like** equation `x² - Dy² = N` for small constants
`D` and `N`. [Problem 100](/solutions/0100/) turns "two blue discs with probability exactly
½" into `x² - 2y² = -1`; [Problem 94](/solutions/0094/) turns "almost-equilateral triangle
with integer area" into a family built on `x² - 3y² = 1`. The decisive fact about Pell
equations is that their infinitely many solutions are **not scattered** — they satisfy a
fixed linear
[recurrence relation](https://en.wikipedia.org/wiki/Recurrence_relation). Once you know the
fundamental solution, every later one is a constant-time arithmetic update:

```
x' = 3x + 4y
y' = 2x + 3y      # Problem 100: each step is the next valid arrangement
```

Because the solutions grow geometrically (here by `3 + 2√2 ≈ 5.83` per step), you cross a
threshold of `10¹²` in about forty iterations — `O(log N)` in the bound rather than `O(N)`.
Finding the *fundamental* solution when it is not obvious is itself a classical algorithm:
the [continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) expansion of `√D`
is eventually periodic, and one specific convergent (chosen by the parity of the period
length) is guaranteed to be it — the method Problem 66 uses. When `D` is large the numerators
outrun 64 bits, so you reach for
[arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic).

### Factor the equation into a divisor count

The algebraic sleight-of-hand. An equation in two variables can sometimes be **factored**
into a product of shifted variables, at which point counting solutions becomes counting
divisors. The reciprocal equation `1/x + 1/y = 1/n` behind
[Problem 108](/solutions/0108/) and [Problem 110](/solutions/0110/) is the canonical example.
Multiply through and rearrange, then add `n²` to both sides so the left factors:

$$ (x - n)(y - n) = n^2 $$

This is [Simon's Favorite Factoring Trick](https://artofproblemsolving.com/wiki/index.php/Simon%27s_Favorite_Factoring_Trick).
Now every solution `(x, y)` is an ordered factorisation of `n²`, so the number of solutions
is governed by the [divisor-counting function](https://en.wikipedia.org/wiki/Divisor_function)
`τ(n²)` — a multiplicative function you compute from the prime exponents of `n` without ever
forming `n²`. Asking for the least `n` with more than a thousand solutions then reduces to a
search over [highly composite numbers](https://en.wikipedia.org/wiki/Highly_composite_number),
which is a tiny structured tree rather than a linear scan.

### Parametrise, then count whole families by division

When the question is *how many* solutions lie under a bound, generating them one by one is
the slow way even after the algebra is done. The faster way is to parametrise the solution
set so that each parameter choice stands for a whole family, and then count each family
with a single division.

[Problem 257](/solutions/0257/) shows the cleanest form. Its area ratio becomes
`(a+b)(a+c) / bc`. Before any search, notice that with `a ≤ b ≤ c` each of the two factors
`(a+b)/b` and `(a+c)/c` lies in `(1, 2]`. An integer ratio can therefore only be 2, 3 or 4,
so one open-ended equation becomes three fixed ones. Writing the first factor as a reduced
fraction `p/q` turns each primitive triangle into a [coprime](https://en.wikipedia.org/wiki/Coprime_integers)
pair `(p, q)`. Every triangle is then that primitive shape scaled by some `s`, so a pair whose
smallest member has perimeter `L` contributes `⌊N / L⌋` triangles in one step. The scaled
copies are never visited.

[Problem 251](/solutions/0251/) goes one step further. A condition on nested cube roots
reduces, through the cubic that `u + v` satisfies, to the integer equation
`27(a² − b²c) = (1 − 2a)³`. Divisibility by 27 forces `a ≡ 2 (mod 3)`. Splitting
`b` against `n` by their [gcd](https://en.wikipedia.org/wiki/Greatest_common_divisor) then
leaves a family in which the remaining variable `d` is bounded above by a linear inequality
and confined by a congruence to a single residue class. Counting the members of an
arithmetic progression below a ceiling takes one line:

```python
d_min = 3 * pow(8 * n1, -1, m) % m     # the one residue class the congruence allows
count += (D - d_min) // m + 1          # members of that class up to the ceiling D
```

The [modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) exists
only because the parametrisation made the pair coprime. That is the general pattern: a gcd
split creates the coprimality, and the coprimality makes the congruence solvable.
Problem 251 also has to choose its loop order. For small moduli the residue class is
dense, so the loop walks one parameter. For large moduli the class is almost empty, so it
walks the cofactor instead. Balancing the two costs puts the switch near `L^{1/4}`.

### When no structure appears, choose the side you search from

Not every Diophantine question gives way to algebra. [Problem 348](/solutions/0348/) asks
for palindromes that can be written as `a² + b³` in exactly four ways. Being a palindrome
is a property of base-10 digits, and the number of representations has no closed form, so
nothing reduces. What remains is a choice of direction. You can test each target
(palindromes, then every cube, then a perfect-square check on the remainder), or you can
generate every pair `(a, b)` and filter the sums. Both cost `O(N^{5/6})`, but pair
generation needs no square roots. For a fixed `b` the sums also form a contiguous run that
NumPy can produce and filter as one array. The unknown bound is handled by scanning one
decimal-length band `[10^{d−1}, 10^d)` at a time, since each finished band gives its
palindromes completely and in order. Even here the integer view matters: a 64-bit
`a² + b³` limits the method to 18 digits, and the solution enforces that with an explicit
guard.

## How to reason about one

When a problem admits only integer answers — and most Project Euler problems do — treat it as
a Diophantine equation and work through these questions before writing any loop:

- **Normalise first.** Clear denominators, complete the square, substitute. The messy
  statement almost always hides one of a few canonical forms: linear, Pell/Pell-like, or
  something that factors.
- **Is there a linear constraint to spend?** Each one eliminates a variable and a loop level.
- **Does it become `x² - Dy² = N`?** Then the solutions form a recurrence-generated family;
  find the fundamental solution (by inspection, or via continued fractions) and iterate. Never
  bound the loop by the size of the answer.
- **Does it factor?** If you can force a product `(…)(…) = k`, counting solutions becomes
  counting divisors of `k`, and the problem turns into a factorisation question.
- **Can an inequality bound the unknown value?** If the sides are ordered, a ratio or
  quotient often fits in a small interval (Problem 257's `(1, 4]`). One open equation
  then becomes a few fixed ones.
- **Counting, not listing?** Parametrise by primitive solutions, usually coprime pairs, and
  count each family's members with `⌊N / L⌋` or a residue-class count. Do not enumerate
  them.
- **Nothing reduces?** Pick the search direction by its constant factors as well as its
  exponent. Generating the solutions and filtering them can beat testing the targets when
  it avoids roots and vectorises.
- **Mind the integers themselves.** Solutions grow geometrically; a 64-bit type overflows
  fast. Know whether your language gives you big integers for free (Python) or whether you
  must carry them yourself (C), and prefer exact integer tests over floating-point ones — a
  Diophantine equality checked with a tolerance is a bug waiting to happen. Watch the
  intermediates too. The C port of Problem 251 silently wrapped a product `n₁²·e` used only
  in a bound test, and the count came out too high. The fix was to compare `n₁` with a
  precomputed integer-square-root cap so the product is never formed.

When the algebra works, the payoff is the same trade every time: a moment of algebra up
front buys an algorithm whose cost depends on the *structure* of the solution set, not on
how large the numbers get. When it does not work, as in Problem 348, the same integer
discipline still shapes the search.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0257](/solutions/0257/) — Angular Bisectors
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0283](/solutions/0283/) — Integer Sided Triangles with Integral Area/perimeter Ratio
- ○ [0291](/solutions/0291/) — Panaitopol Primes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ○ [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0404](/solutions/0404/) — Crisscross Ellipses
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ○ [0428](/solutions/0428/) — Necklace of Circles
- ○ [0438](/solutions/0438/) — Integer Part of Polynomial Equation's Solutions
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ○ [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0482](/solutions/0482/) — The Incenter of a Triangle
- ○ [0496](/solutions/0496/) — Incenter and Circumcenter of Triangle
- ○ [0510](/solutions/0510/) — Tangent Circles
- ○ [0513](/solutions/0513/) — Integral Median
- ○ [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ○ [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ○ [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ○ [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ○ [0681](/solutions/0681/) — Maximal Area
- ○ [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0753](/solutions/0753/) — Fermat Equation
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ○ [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0919](/solutions/0919/) — Fortunate Triangles
- ● [0932](/solutions/0932/) — $2025$
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ○ [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0991](/solutions/0991/) — Fruit Salad
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
