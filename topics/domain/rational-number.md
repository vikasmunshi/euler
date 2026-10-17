<!-- tags: [rational-number] -->
<!-- status: final 2026-10-17T06:59Z -->
# Rational number

A [rational number](https://en.wikipedia.org/wiki/Rational_number) is a ratio p/q of integers with
q ≠ 0. The problems below are not just *computed* with fractions. They are *about* ℚ: the set of
capacitances a circuit can reach, the values an arithmetic expression over 1…9 can take, a triangle
shape fixed by a side ratio, a rate one supplier beats another by. Three properties of ℚ keep doing
the work. It is closed under + − × ÷. Every element has one canonical form. And a rational
condition can always be turned into an integer one by clearing denominators. This page is about
using those properties. The Python type is covered on
[fractions.Fraction](/topics/technique/fractions-fraction), and the general rule "compare exactly,
never by float" on [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).

## The idea

**Canonical form makes ℚ hashable.** 2/4, 1/2 and −1/−2 are one number written three ways. A set,
a dict key, or a sort-then-dedupe pass needs one written form per number. The usual choice is the
[irreducible fraction](/topics/technique/irreducible-fraction): divide both parts by
[gcd](/topics/technique/math-gcd)(p, q), then move the sign onto the numerator so q > 0. Zero needs
no special case, because gcd(0, q) = q sends 0/q to 0/1. Every solution here that collects
rationals in a set starts from this normaliser.

**Closure turns "which values are reachable?" into a set DP.** The field operations never leave
ℚ, so a problem that combines values over and over (series and parallel joins, the four operators
of arithmetic) has a reachable set that stays inside ℚ and can be enumerated exactly.

- **Problem 155** (capacitor circuits) keeps `exact[k]`, the capacitances reachable with exactly k
  unit capacitors. A parallel join adds two values. A series join gives ab/(a+b), and its
  denominator is the parallel sum's numerator, so the solution computes `an*bd + bn*ad` once and
  uses it for both results.
- **Problem 259** (reachable numbers) is the same DP over intervals of the digit string
  `123456789`. The value set of a run is the concatenated number plus every left ∘ right
  combination over every split point. Subtraction brings in negatives and zero, and division
  brings in negative denominators and the r = 0 case, which has to be skipped. Only at the end
  does it keep the elements with q = 1 and p > 0.

Both Python solutions store a value as a bare `(p, q)` tuple, reduced by a local `norm` (259 notes
it runs about 5× faster than `Fraction`). Both C solutions write an open-addressing
[hash table](/topics/technique/hash-table) keyed on the pair. The canonical form is what makes
that table correct: two hashes agree only when the reduced pairs are identical.

**A reduced ratio parametrises a family of integer objects.** When a condition depends only on a
ratio, write the ratio as coprime p/q. Each coprime pair is then one *primitive shape*, and the
integer solutions are its multiples. The smallest multiple that makes everything integral comes
from a gcd.

- **Problem 257** (angular bisectors) shows that the area ratio is (a+b)(a+c)/(bc), and that it can
  only be the integer k = 2, 3 or 4. Writing (a+b)/b = p/q in lowest terms gives a = (p−q)s and
  b = qs, with c a rational multiple of s. Then c is an integer exactly when s is a multiple of
  r/gcd(p(p−q), r), where r = kq − p. Each coprime (p, q) inside the triangle-inequality window
  therefore contributes ⌊limit / L⌋ triangles, where L is the perimeter of its primitive shape.
  The count is a sum over coprime pairs, with no search over triangles at all.
- **Problem 236** (luxury hampers) looks for the ratios m = p/q by which one supplier's spoilage
  rate beats the other's on every product and overall. First the products are pooled by their
  reduced B_i/A_i, because that ratio is all the equations depend on. Requiring b_i = m·(B_i/A_i)·a_i
  to be an integer forces a_i to be a multiple of dq/gcd(dq, np). Clearing every denominator turns
  the overall rate into one linear [Diophantine equation](/topics/domain/diophantine-equation)
  in the pooled counts, which the [extended Euclidean
  algorithm](/topics/technique/extended-euclidean-algorithm) tests against the supply bounds.

Coprimality matters here, and not only to save work. Each rational has to be counted once. In 257,
the (p, q) = (4, 2) "shape" would be (2, 1) again and would double-count every triangle, which is
why the Python filters `p[np.gcd(p, q) == 1]`.

**Clearing denominators carries integer theorems over to ℚ.** Problem 180 (golden triplets) reduces
its three functions to x^n + y^n = z^n over rationals in (0, 1). Multiplying through by the common
denominator turns a rational solution into an integer one, so
[Fermat's Last Theorem](https://en.wikipedia.org/wiki/Fermat%27s_Last_Theorem) rules out
|n| ≥ 3. Negative n is the same equation on the reciprocals. The cases n = ±2 then need √(x² + y²)
to be rational, and for a *reduced* p/q that holds exactly when p and q are both perfect squares.
If they were not, a root (a/b)² = p/q with gcd(a, b) = 1 would give two different reduced forms of
one number. The canonical form decides it again: two `isqrt` calls and two multiplications replace
any floating-point test of whether something "looks like a square". Problem 33 does the same thing
on a small scale. The cancellation (10n + x)/(10x + d) = n/d is tested as the cross-multiplied
integer equation, never as a quotient.

## How big the numbers get, and what C does about it

In Python, ℚ is unbounded for free. In C, each solution first has to estimate the
[height](https://en.wikipedia.org/wiki/Height_function) max(|p|, |q|) of what it handles.
Multiplying two fractions roughly multiplies their heights, and adding a/b + c/d produces a
denominator up to bd before reduction. So the analysis comes down to how many operations stand
between the seed values and the result. The four C siblings arrive at four different answers:

| problem | where the heights stay | C representation |
|---|---|---|
| 155 | small: the joins keep values near Fibonacci ratios | `int32_t` storage, `long long` products before the gcd |
| 259 | stored values fit 64 bits, products of two of them do not | `long long` pair, `__int128` cross-products reduced by a 128-bit gcd |
| 236 | ratios are small, the cleared-denominator coefficients are not | [`__int128`](/topics/technique/int128) coefficients and gcd |
| 180 | each x, y, z and sum is small, but the *total* of all sums is not | 64-bit `frac` struct per value, [GMP](/topics/technique/gmp) `mpq_t` for the running total |

Problem 180 is the case to remember. Each sum s = x + y + z has a denominator no larger than a
product of three small ones. Adding hundreds of *distinct* such sums pushes the denominator of the
total towards lcm(1…k), far beyond 64 bits, even though no single term is large. Summing many
rationals with unrelated denominators is the one operation whose height grows with the *count* of
terms. That is why 180 is the only solution here that needs a rational bignum. The two languages
also deduplicate differently. Python's `set[Fraction]` hashes by value. The C version collects
every candidate, `qsort`s by cross-multiplying in `__int128`, and skips adjacent duplicates. The
result is the same set, reached by sorting instead of hashing.

Problem 257's two sides differ for a different reason. The rational structure lives entirely in the
parametrisation, and the inner loop is plain integers, so the Python vectorises the scan over p with
NumPy (`np.gcd` for the coprimality mask and for the scaling step), while the C loops over p with a
scalar gcd.

## How to reason about it

- **Ask whether the problem lives in ℚ or merely touches it.** If values are combined and compared
  over and over (155, 259, 180), fix a canonical form and make it the set key. If a single ratio
  defines a shape (257, 236), parametrise by coprime p/q and count multiples. That way no fraction
  is ever built.
- **Normalise the sign, not only the gcd.** Once subtraction or division can produce a negative
  denominator, 1/−2 and −1/2 hash differently unless `norm` flips them. Zero must come out as 0/1,
  and a zero divisor must be skipped before it reaches the normaliser.
- **Clear denominators to reach integer tools.** Rationality of a root, FLT, linear Diophantine
  solvability and divisibility conditions are all statements about integers. Multiply out first,
  then reason.
- **Bound heights before choosing a C type, and watch the sums.** Products and pairwise sums
  roughly double the bit length. A long sum of rationals with unrelated denominators can grow
  without limit. Use `__int128` when one extra product is the problem, and GMP when an accumulation
  is.
- **Use the tuple, not the class, in a hot set DP.** A reduced `(p, q)` tuple hashes and compares
  as fast as any tuple. `Fraction` runs the same gcd inside a much heavier object (see
  [fractions.Fraction](/topics/technique/fractions-fraction) for when that trade is worth it).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0259](/solutions/0259/) — Reachable Numbers
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ○ [0422](/solutions/0422/) — Sequence of Points on a Hyperbola
- ○ [0450](/solutions/0450/) — Hypocycloid and Lattice Points
- ○ [0809](/solutions/0809/) — Rational Recurrence Relation
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0972](/solutions/0972/) — Hyperbolic Plane
- ○ [0991](/solutions/0991/) — Fruit Salad

<!-- /problems -->
