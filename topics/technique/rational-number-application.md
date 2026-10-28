<!-- tags: [rational-number-application] -->
<!-- status: final -->
# Rational number (application)

This page is about one working habit: when the true answer is a
[rational number](https://en.wikipedia.org/wiki/Rational_number), keep it one, exactly, until the
very last line, and do the single lossy step (rounding to the places asked for, or testing "is this
an integer?") on integers. What ℚ *is* and why its structure helps is on the
[rational number](/topics/domain/rational-number) domain page. Here the question is narrower and
practical. Where in a solution does exactness get lost? And which of three representations
should carry it: no fraction at all, a bare `(p, q)` pair, or a full rational type? Problems 257,
259 and 523 each pick a different one, and each pick is right for its problem.

## The idea

A `double` holds 53 bits of mantissa, and 1/3, 1/10 and nearly every other fraction is rounded the
moment it is stored. That error is harmless until an answer *depends on a boundary*. Three
boundaries recur:

- **an integrality test**: "keep the values that are positive integers", "c must be integral";
- **a comparison**: b ≤ c, p ≥ q·√k, where one side sits exactly on the edge;
- **a rounding half**: an answer whose exact decimal ends in …5 one place past the requested
  precision.

At a boundary, a value that is wrong by 10⁻¹⁶ can come out on the wrong side, and the error
surfaces as a wrong last digit or an off-by-one count. The fix is the same in all three cases.
Carry numerator and denominator as integers, and make the boundary decision with integer
arithmetic.

The three problems show the three ways to carry a rational, from cheapest to heaviest.

**1. Don't build the fraction, parametrise by it (257).** The area ratio in Angular Bisectors is a
rational function of the sides, and it has to come out as an integer k. Instead of computing ratios
and testing them, the solution writes the ratio (a+b)/b as a coprime pair p/q and derives the sides
from it. After that the loop is pure integer work: a gcd to find the smallest valid scaling, a floor
division to count the multiples. The one place where an irrational would appear, the bound
p ≥ q·√k, is computed as `isqrt(k*q*q - 1) + 1`, an
[integer square root](/topics/technique/integer-square-root), so no float can misplace the
b ≤ c boundary. No `Fraction` exists anywhere, and that is the best case: nothing to round, nothing
to normalise.

**2. A hand-rolled `(p, q)` pair (259).** Reachable Numbers enumerates every value an expression
over the digits 1…9 can take, then sums the positive integers among them. The set holds a very
large number of values, and every insertion is an add, subtract, multiply or divide followed by a
hash. Floats are out for two reasons. 1/3·3 must land on the same key as 1, and the final filter
"is this an integer?" is exactly the boundary above. Each value is therefore a tuple reduced to
[lowest terms](/topics/technique/irreducible-fraction) with the sign on the numerator, so equal
rationals hash identically and the filter is simply `q == 1`. The solution notes that the tuple is
about 5× faster than `Fraction`, because there is no object to construct, no operator dispatch and
no type checks. Python's arbitrary-precision `int` still gives the tuple unbounded height.

**3. A real rational type (523).** First Sort I asks for an expectation rounded to two decimals.
The derivation reduces it to a single sum of n − 1 terms (2ᵏ − 1)/(k + 1), detailed on
[expected value (application)](/topics/technique/expected-value-application). The denominators are
the unrelated integers 2…n, so the sum's denominator heads towards lcm(2…n) and its numerator
carries 2ⁿ-sized terms. Neither fits a machine word once n is large, and the problem's own worked
value lies exactly on a rounding half. Here `fractions.Fraction` is the right tool: the loop is
O(n), short and runs once, so object overhead is noise, and the type handles the reduction and the
growing height. The last step converts once, by integer arithmetic:

```python
scaled = (value * 10**digits + Fraction(1, 2)).__floor__()   # half-up, exact
whole, frac = divmod(scaled, 10**digits)
```

Note that this does *not* call `round()`. On an exact half, Python's `round` picks the even
neighbour (banker's rounding), and `float(value)` would hand it a value that may already sit on the
wrong side of the half.

## When `Fraction` is worth its cost

[`fractions.Fraction`](/topics/technique/fractions-fraction) is correct and convenient. It
normalises on every operation with a gcd, and it is slow: each `+` builds a new object, takes the
cross-products, then reduces. Weigh it as follows:

| situation | carry it as | why |
|---|---|---|
| the ratio only *defines* a shape, then you count | coprime integers `p, q` (257) | nothing rational survives into the loop |
| millions of operations, values hashed or compared | reduced `(p, q)` tuple + local `norm` (259) | same exactness, no object overhead |
| a short accumulation whose height grows, then one rounding | `Fraction` (523) | the overhead is irrelevant and the bookkeeping is free |
| a long, well-conditioned sum of positive terms, generous tolerance | `float`, after one exact cross-check | see 253 on the expected-value page |

The deciding question is not "are there fractions?" but "how many operations, and does a boundary
decide the answer?" If there are few operations, use `Fraction` without a second thought. If there
are many and a boundary decides, use the tuple. If no boundary decides, a float may be fine, but
check that once against an exact run.

## The C counterpart

C has no unbounded integers, so the choice above becomes a choice about
[height](https://en.wikipedia.org/wiki/Height_function), the size of max(|p|, |q|):

- **257** needs nothing special. Coprime `long long` p, q, a scalar gcd, and a careful square-root
  bound. The C seeds it from `sqrtl`, then nudges the guess up and down until p² ≥ kq² holds
  exactly in integers. That correction is what Python's `isqrt` already does internally.
- **259** stores each value as a `struct { long long p, q; }`, because the reduced values fit in 64
  bits. The cross-products in a + b or a ÷ b do not, so they are formed in
  [`__int128`](/topics/technique/int128) and reduced by a 128-bit gcd before being narrowed back.
  The set is an open-addressing hash table keyed on the canonical pair. This is the same design as
  the Python tuple, with the overflow analysis written out.
- **523** cannot bound its height at all: the lcm of 2…n outgrows any fixed width. So it uses
  [GMP](/topics/technique/gmp) `mpq_t`, the C analogue of `Fraction` (it is also canonicalised after
  each operation), and rounds with `mpz` integer division, mirroring the Python helper line for line.

The rule of thumb carries over directly. Use a fixed-width pair when a single extra product is the
risk (widen it to `__int128` at the multiply). Use GMP when an *accumulation* is, because summing
many rationals with unrelated denominators is the one operation whose height grows with the number
of terms.

## How to reason about it

- **Locate the boundary first.** Find the integrality test, the tie-prone comparison or the
  rounding half. If none exists and the arithmetic is benign, floats may do. If one exists, the
  values feeding it must be exact.
- **Prefer no fraction to any fraction.** If a ratio only fixes a shape, parametrise by coprime p/q
  and work in integers (257). Replace √ bounds with `isqrt`, and compare a/b < c/d as ad < cb.
- **Pick the representation by operation count.** Use the tuple in hot set DPs and `Fraction` in
  short accumulations. In C, use a 64-bit pair with `__int128` products, or `mpq_t` when the height
  is unbounded.
- **Round once, in integers, half-up on purpose.** ⌊x·10ᵈ + ½⌋ on the exact value, then `divmod`
  for the digits. Never `round(float(x), d)` when the problem's own example may sit on a half. See
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality) for the same
  discipline applied to comparisons.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0523](/solutions/0523/) — First Sort I

<!-- /problems -->
