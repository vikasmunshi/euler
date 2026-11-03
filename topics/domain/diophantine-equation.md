<!-- tags: [diophantine-equation] -->
<!-- status: final 2026-11-03T17:30Z -->
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

A linear equation is not always the easy part, though. Once the unknowns must be
**non-negative**, `ax + by + cz = n` becomes the
[coin problem](https://en.wikipedia.org/wiki/Coin_problem). [Problem 718](/solutions/0718/)
asks for the sum of every `n` that `17ᵖa + 19ᵖb + 23ᵖc` cannot reach. The reachable values
form a [numerical semigroup](https://en.wikipedia.org/wiki/Numerical_semigroup) with finitely
many gaps, but at `p = 6` the gaps run into the quadrillions. The way through is the
[Apéry set](https://en.wikipedia.org/wiki/Numerical_semigroup#Ap%C3%A9ry_set): for each residue
`r` modulo the smallest generator `x`, find the least reachable value `w_r` in that class.
Everything above `w_r` in the class is reachable and everything below it is a gap. So the gaps
in each class form one arithmetic progression, and its count and sum have closed forms. The
cost is linear in `x` and does not depend on how far the gaps extend. With three generators,
walking the residues in steps of `z` reduces the Apéry set to a running minimum of one array.

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

Pell equations can also prove that a search is **finite**. [Problem 581](/solutions/0581/)
needs every `n` for which `n` and `n + 1` are both 47-smooth. With `x = 2n + 1` and `q` the
squarefree part of `n(n+1)`, the condition becomes `x² − 2q·y² = 1`. Here `q` is a product of
some subset of the fifteen primes up to 47, so there are only `2¹⁵` equations to check. That
is [Størmer's theorem](https://en.wikipedia.org/wiki/St%C3%B8rmer%27s_theorem). Lehmer's
refinement adds two cheap filters. If the fundamental `y₁` is not smooth, no later solution is,
because `y₁` divides every `yₖ`. If some `yₖ` is smooth, then `k ≤ max(3, (p+1)/2)`. An
unbounded problem about consecutive smooth numbers therefore becomes a fixed list of Pell
equations, each with a short run of powers. The equation tells you where the search can stop
as well as how to generate solutions.

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

A factorisation can also give you the *least* solution directly. In
[Problem 955](/solutions/0955/), a sequence jumps from one triangular number `t(x)` to the
next. The size of each jump is the least `j ≥ 1` with `t(x) + t(j) = t(y)`. Multiplying by 8
and taking a difference of squares turns this into `x(x+1) = p·q`, where `q − p = 2j + 1`.
The trivial pair `(x, x+1)` gives `j = 0`. The smallest real jump therefore comes from the
factor pair **closest** to the trivial one, which is the largest suitable divisor of `x(x+1)`
below `x`. Each step costs a factorisation of `x` and `x + 1` separately (they are coprime) by
[Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm), so the method never
scans gaps that reach into the trillions.

Factoring can also be what makes a condition such as *"is prime"* tractable.
[Problem 291](/solutions/0291/) asks for primes `p = (x⁴ − y⁴)/(x³ + y³)`. Cancel `x + y`, put
`x = ga` and `y = gb` with `a` and `b` coprime, and coprimality forces the leftover denominator
to divide `g`. The prime is then a product of three positive integers, so two of them must
equal 1, and the two-variable equation collapses to the one-variable form `p = n² + (n+1)²`.
What remains is to count the primes among the values of a quadratic. A
[polynomial sieve](https://en.wikipedia.org/wiki/Sieve_theory) handles this: an odd prime `q`
divides some value only when `−1` is a square mod `q`, which means `q ≡ 1 (mod 4)`. Each such
`q` then strikes exactly two residue classes of `n`. This is Eratosthenes run over the values
of `f(n)` instead of over the integers.

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

The parametrisation usually comes from one lemma: **if coprime factors multiply to a square,
each factor is a square** (up to a unit, or a factor of 2 you track separately). In
[Problem 518](/solutions/0518/), three numbers are in geometric progression when `y² = xz`.
Writing the ratio in lowest terms as `q/p` forces `p²` to divide `x`. That gives the complete
and unique family `(kp², kpq, kq²)` with `p` and `q` coprime, so a pairwise divisibility
search becomes a walk over three small parameters. [Problem 764](/solutions/0764/) uses the
lemma twice. It reads `16x² + y⁴ = z²` as a Pythagorean triple `(4x, y², z)` and takes the
triple from [Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple#Generating_a_triple).
Requiring the leg `y²` to be a square forces `m ± n` (when `y` is odd) or `m` and `2n` (when `y`
is even) to be squares themselves. The result is two quartic families in a coprime pair
`(a, b)`. Because `z` grows like the fourth power of the parameters, the enumeration costs
`O(N^{1/2})`.

A parametrised family can also be **joined against itself**. In
[Problem 309](/solutions/0309/), crossed ladders reduce to two Pythagorean triples that share a
leg `w`, together with the condition `(a + b) | ab` on the other legs. You first show that
`a` and `b` must be integers: an irrational pair would make `1/h` irrational. Then you
generate every triple once with Euclid's formula, group the triples by their shared leg, and
test pairs only within each group. Each leg belongs to only a handful of triples, so the
quadratic pair test inside a group costs almost nothing.

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

### When the unknown is its own exponent, iterate to a fixed point

Some Diophantine conditions are congruences rather than equalities, and the unknown sits in
the exponent. [Problem 455](/solutions/0455/) asks, for each base `n`, for the `x < 10⁹`
whose last nine digits of `nˣ` spell `x` itself, that is `nˣ ≡ x (mod 10⁹)`. Nothing
factors and no recurrence applies, and a scan over `10⁹` exponents for each of a million
bases is out of the question. The useful structure is that `x` is a **fixed point** of the
map `T(x) = nˣ mod 10⁹`.

Iterating that map from `x = 1` builds the power tower `n, nⁿ, n^(nⁿ), …` modulo `10⁹`.
Such [towers](https://en.wikipedia.org/wiki/Tetration) become constant after a few levels.
Once the exponent is large, `nᵃ mod m` depends only on `a` modulo the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) `λ(m)`. The level
below therefore only matters modulo `λ(m)`, the one below that modulo `λ(λ(m))`, and the
chain of moduli shrinks to 1 within a handful of steps. The settled value satisfies
`T(x) = x` by construction, so a dozen rounds of
[fixed-point iteration](https://en.wikipedia.org/wiki/Fixed-point_iteration) replace the
search. Each round is one modular exponentiation per base, and every base can be run in
lockstep as a vectorised array. Two pieces of ordinary Diophantine reasoning finish the job.
A divisibility argument rules out the multiples of ten before any iteration. If `10 | n`,
then `nˣ` ends in 0, so `x` must too. That makes `x ≥ 10`, so `10⁹` divides `nˣ` and forces
`x ≡ 0`, which is excluded. Then the claim that the tower's limit is the
*largest* solution, which the problem asks for, is not something the iteration proves. The
solution checks it by exhaustive search on the scaled-down moduli `10³`, `10⁴` and `10⁵`
before relying on it.

### Vieta jumping: the solutions form a tree

Some equations are quadratic in each variable taken separately. Then every solution has a
neighbour. In the Markov-type equation `x₁² + … + x_k² = k·x₁⋯x_k` of
[Problem 844](/solutions/0844/), fix all the variables but one. That one is a root of a
quadratic, and by [Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas) the other
root `kP − x` is also a positive integer. Swapping one root for the other is
[Vieta jumping](https://en.wikipedia.org/wiki/Vieta_jumping). If you always swap out the
largest entry, the tuple shrinks down to a fundamental solution, which here is all ones.
Run in the other direction, the same move makes every solution a node of a single tree, and the
values only grow along each branch. A depth-first search pruned at the bound therefore lists
every solution, and the tree has only `O(log² N)` nodes because the values grow doubly
exponentially. The problem has one more layer, a sum over `k` up to `10¹⁸`. The tree has the
same shape for every large `k`, so each node is a fixed polynomial in `k`. The sum over `k`
then becomes a few dozen [power sums](https://en.wikipedia.org/wiki/Faulhaber%27s_formula)
instead of 10¹⁸ trees.

### When the function is injective, solve by structure

In some problems the arithmetic turns out to carry no information at all.
[Problem 674](/solutions/0674/) asks when two nested expressions in
`I(x, y) = (1+x+y)² + y − x` are equal. For a fixed `s = x + y`, the values of `I` fill a
window around `(s+1)²`, and the windows for different `s` never overlap. So `I` is
**injective** on non-negative pairs, much like a
[pairing function](https://en.wikipedia.org/wiki/Pairing_function), and two expressions are
equal exactly when their trees match after the variables are substituted. Solving the
equation is then first-order
[unification](https://en.wikipedia.org/wiki/Unification_(computer_science)): union-find over
a hash-consed term DAG, with an occurs check to reject equations like `x = I(x, z)`. `I`
increases in each argument, so the least solution is the most general unifier with every free
variable set to 0. The lesson is to ask, before computing anything, whether the equation
holds only for identical inputs.

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
  If the unknowns must be non-negative, it is a Frobenius problem: count the gaps per residue
  class with the Apéry set, never one by one.
- **Does it become `x² - Dy² = N`?** Then the solutions form a recurrence-generated family;
  find the fundamental solution (by inspection, or via continued fractions) and iterate. Never
  bound the loop by the size of the answer. A family of Pell equations with Lehmer's bounds
  can also show that a smoothness search is finite.
- **Does it factor?** If you can force a product `(…)(…) = k`, counting solutions becomes
  counting divisors of `k`, and the problem turns into a factorisation question. The divisor
  nearest the trivial one gives the least solution. A prime equal to a product forces every
  factor but one to be 1.
- **Do coprime factors multiply to a square?** Then each factor is a square, and the
  solutions are parametrised by a coprime pair.
- **Is it quadratic in each variable?** Vieta jumping links the solutions into a tree rooted
  at a fundamental solution, and a pruned DFS walks all of it.
- **Is the operation injective?** Then equality means the expression trees match: unify
  them instead of doing arithmetic.
- **Can an inequality bound the unknown value?** If the sides are ordered, a ratio or
  quotient often fits in a small interval (Problem 257's `(1, 4]`). One open equation
  then becomes a few fixed ones.
- **Counting, not listing?** Parametrise by primitive solutions, usually coprime pairs, and
  count each family's members with `⌊N / L⌋` or a residue-class count. Do not enumerate
  them.
- **Is the unknown in the exponent of a congruence?** Look for a fixed point. Iterating
  `x ← nˣ mod m` settles quickly because the Carmichael chain `m, λ(m), λ(λ(m)), …` is
  short. Verify on small moduli that the limit is the solution the problem wants.
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
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ● [0309](/solutions/0309/) — Integer Ladders
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
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0482](/solutions/0482/) — The Incenter of a Triangle
- ○ [0496](/solutions/0496/) — Incenter and Circumcenter of Triangle
- ○ [0510](/solutions/0510/) — Tangent Circles
- ○ [0513](/solutions/0513/) — Integral Median
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ○ [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ○ [0681](/solutions/0681/) — Maximal Area
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0753](/solutions/0753/) — Fermat Equation
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0919](/solutions/0919/) — Fortunate Triangles
- ● [0932](/solutions/0932/) — $2025$
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ● [0955](/solutions/0955/) — Finding Triangles
- ○ [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0991](/solutions/0991/) — Fruit Salad
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
