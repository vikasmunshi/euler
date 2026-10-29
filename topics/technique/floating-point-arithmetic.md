<!-- tags: [floating-point-arithmetic] -->
<!-- status: final -->
# Floating-point arithmetic

Project Euler answers are almost always exact: an integer, a count, a digit string. The quickest
way to get there often goes through a `double` anyway: a square root to invert a quadratic, a
logarithm to count digits, a division to explore expressions. [Floating-point
arithmetic](https://en.wikipedia.org/wiki/Floating-point_arithmetic) is fast and almost always
right. The problems below are about the "almost". Each one either shows a case where floats are
provably safe, or a case where they quietly return a wrong number, so this page tries to make the
line between the two something you can check rather than something you hope for.

## The idea

An IEEE 754 [`double`](/topics/technique/double-precision-floating-point-format) stores a 53-bit
significand. Three facts follow, and the rest of the page is
built from them:

1. **Integers are exact up to 2⁵³.** Any integer with magnitude ≤ 2⁵³ ≈ 9.007 × 10¹⁵ is stored
   exactly, and `+`, `−`, `×` on such integers are exact as long as the result also stays in range.
2. **Basic operations are correctly rounded.** `+ − × ÷` and `sqrt` return the representable value
   nearest the true result ([IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) requires it). So if
   the true result is representable, you get it *exactly*. `sqrt(49.0)` is `7.0`, not `6.9999…`.
3. **Everything else carries error.** `log`, `exp`, `pow` with non-integer exponents, and any value
   that is not a dyadic rational (1/3, 0.1, √2) are approximations, typically within one
   [ulp](https://en.wikipedia.org/wiki/Unit_in_the_last_place), and the error compounds through a
   chain of operations. David Goldberg's [*What Every Computer Scientist Should Know About
   Floating-Point Arithmetic*](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) is
   still the standard reference.

So a float computation can be trusted when every intermediate value is exact by rules 1 and 2, or
when its error is provably smaller than the gap the decision depends on. It cannot be trusted when
an inexact value meets an exact test such as `is_integer()`, `floor`, or `==`.

### Membership tests by inverting a quadratic (42, 44)

To test whether `n` is triangular, problem 42 solves `k(k+1)/2 = n` for `k` and asks whether the
root is whole. In other words, it asks whether `8n + 1` is a perfect square:

```python
def is_triangle_number(n: int) -> bool:
    return ((8 * n + 1) ** 0.5).is_integer()
```

By rule 2 this is exact when `8n + 1 = k²`: the true root `k` is representable, so `sqrt` returns
it. The risk is the other direction. A non-square `m = k² ± 1` has root about `k ± 1/(2k)`, and once
that offset drops below half an ulp of `k`, it rounds to `k` and the test says yes. That first
happens near `m ≈ 2⁵²`. I checked: `math.sqrt(2**52 + 1).is_integer()` is `True`. Word values in
problem 42 are a few hundred, so the test is safe there by about thirteen orders of magnitude.
Problem 44's pentagonal test, `(1 + sqrt(1 + 24n)) / 6`, adds an exact `+ 1` and a correctly
rounded `/ 6` to the same argument. Its pentagonal numbers stay in the low millions, so it is safe
too.

"Safe here" is not "safe". Both C ports make the check exact at any size: round the float root,
then confirm it in integers.

```c
long long k = llround(sqrt((double)m));
return k * k == m;                     /* the float is only a guess; the integers decide */
```

In Python, [`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) skips the float
entirely (`r = isqrt(m); r * r == m`). It is exact for any `int` and costs about the same at these
sizes. Use it when the argument has no small bound.

### Digit counts by logarithm (63)

A positive integer `x` has `⌊log₁₀ x⌋ + 1` digits. Problem 63 wants the `n`-digit `n`th powers,
and that formula turns "how many digits does `bⁿ` have?" into `⌊n · log₁₀ b⌋ + 1`, with no big
integer involved. The trouble is at the boundaries. `log₁₀ x` lands on an integer exactly when `x`
is a power of ten, and the numbers just below a power of ten are the ones the formula gets wrong:

```python
>>> math.log10(10**15 - 1)        # true value 14.99999999999999957…
15.0                              # → 16 digits; the number has 15
```

Both solutions use the logarithm only to narrow the search and let integers decide. The Python
version inverts the digit bounds to get a range of bases, `ceil((10**(n-1)) ** (1/n))`, widens the
upper end by one, and then counts digits exactly with `len(str(b**n))`. The C version uses
`floor(n * log10(b)) + 1` as a screen and confirms each hit with an integer power and digit count.
That pattern (*float to estimate, integer to confirm*) is the main habit this page is about. It
applies to every "how big is this?" estimate in the
[big-number](/topics/technique/arbitrary-precision-arithmetic) problems.

### Exact rational targets (93)

Problem 93 combines four digits with `+ − × ÷` and brackets, then asks which integers come out.
Division brings in thirds and sevenths, which a binary float cannot represent, and the integer test
at the end is exact. The two collide:

```python
>>> 5 / (4/3 - 1)
15.000000000000004
```

`4/3` rounds down, so `4/3 − 1` is slightly below `1/3`, and dividing by it lands just above 15.
`is_integer()` says no, and 15 drops out of the reachable set. I re-ran the Python solution's
search over all 126 digit sets with [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html)
in place of floats. The float version loses at least one reachable integer in **15** of them, and
for `{1, 3, 4, 5}` the consecutive run 1…n shrinks from 24 to 14. The winning set happens to come
out the same, which makes this the dangerous kind of bug: the answer is right for a reason that has
nothing to do with the code.

There are two sound fixes:

- **Compare with a tolerance.** The C port rounds to the nearest integer and accepts the result
  when `fabs(v − rounded) < 1e-9`. This is safe here because the error is a few ulps on values
  below about 3000, while two distinct rationals built from single digits differ by far more than
  10⁻⁹. A tolerance only works when you can bound both of those quantities.
- **Stay exact.** Over the rationals there is nothing to tune. `Fraction` arithmetic is slower,
  but a few thousand values per digit set is nothing, and `v.denominator == 1` is a test that cannot
  lie.

### A ceiling over a logarithm near 1 (318)

Problem 318 reduces, through the conjugate `y = √q − √p`, to a closed form per pair:
`N = ⌈d / (−2 log₁₀ y)⌉`. The trouble is that the interesting pairs have `y` just below 1, so the
quantity that matters is the small gap `ε = 1 − y`. Computing `√q − √p` subtracts two nearly
equal square roots, and `log` of a number near 1 then throws away the leading digits a second
time. The solution avoids both losses:

- It rationalises `ε` into a form whose numerator, `4p − (q − p − 1)²`, is an exact integer and
  whose denominator is a sum of positive terms. Nothing cancels, so `ε` keeps full relative
  precision however small it gets. This is the same move as 247.
- It takes `log1p(−ε)` instead of `log(1 − ε)`.
  [`log1p`](https://docs.python.org/3/library/math.html#math.log1p) exists for exactly this case:
  it computes `ln(1 + x)` from `x` itself, without first rounding `1 + x`.

I measured the difference on the pair with the smallest `ε` in range, where `N` is about six
million. The naive `log(sqrt(q) - sqrt(p))` has relative error 2.5 × 10⁻¹², which works out to
about 1.5 × 10⁻⁵ in absolute terms on the quotient. The rationalised `log1p` version has relative
error 10⁻¹⁶, which is within an ulp.

That still is not enough to trust a ceiling without thinking. `⌈x⌉` is fragile only when `x` is
close to an integer, so the solution states a band: if the float quotient is within 10⁻⁴ of an
integer, that one pair is recomputed in 60-digit `Decimal` (MPFR in the C port). The band is
far wider than the error bound, and it is almost never entered, so the exact path costs nothing.
Problem 800 has the same shape: floats settle everything outside a stated margin, and exact
arithmetic decides inside it. The difference is that 318's exact path is high-precision reals
rather than integers, because the quantity is irrational.

### The rest of the tag

The private problems apply the same rules at larger scale. Problem 800 compares `p^q · q^p` with
an enormous bound in log space (`q·ln p + p·ln q ≤ ln N`). The floats settle every pair outside a
narrow band around the boundary, and only a pair inside that band, a near-tie, falls back to the
exact integer comparison. Problem 247 computes the side of the largest square under a hyperbola
from a quadratic root. It rewrites `(√((x−y)² + 4) − (x + y)) / 2` in rationalised form so that it
never subtracts two nearly equal quantities. That is [catastrophic
cancellation](https://en.wikipedia.org/wiki/Catastrophic_cancellation), the classic way a quadratic
formula loses digits. Problem 235 needs a root to twelve decimal places, more than bisection on
doubles reliably delivers through a closed form full of `r − 1` near zero, so it bisects in
[`decimal`](https://docs.python.org/3/library/decimal.html) at chosen precision. Problems 190 and
395 want real-valued answers, where floats are the natural tool. 395 picks its recursion depth from
the tolerance it needs, so the error budget is set by the design, not found by trial.

## How to reason about it

Before trusting a float in an exact problem, ask four questions:

| Question | If yes | If no |
|---|---|---|
| Is every intermediate an integer ≤ 2⁵³, or a correctly rounded op whose exact result is representable? | The float is exact. Use it. | Go on. |
| Is the error provably smaller than the gap the decision depends on? | Use it, and write the bound down in a comment. | Go on. |
| Can the float be just a *guess* that an integer check confirms (42/44 in C, 63, 800), or that a high-precision recomputation confirms near the boundary (318)? | Do that. It costs one extra multiply, or one slow path taken almost never. | Go on. |
| Is the problem fundamentally about rationals or long decimals (93, 235)? | Use `Fraction`, `Decimal`, or scaled integers. | Rethink the formulation. |

Some pitfalls come up again and again:

- **`is_integer()` and `==` on a computed float** are only as good as the computation. They are
  fine after exact ops (42 at small `n`) and wrong after one inexact division (93).
- **`floor` and `ceil` near an integer boundary**, as in digit counts, bucket indices and
  `int(x ** (1/k))` for integer roots. Nudge the estimate and correct it in integers:
  `while r ** k > n: r -= 1`.
- **Subtracting nearly equal values** wipes out significant digits. Rearrange algebraically (247,
  318) before reaching for more precision. For logarithms and exponentials near 1, use `log1p` and
  `expm1`.
- **The 2⁵³ cliff.** C's `double` and Python's `float` share it. A test that passes at 10⁶ fails
  silently at 10¹⁶, so check how large the inputs can get, not just the values in the example.
- **C and Python can disagree** if one rounds and verifies while the other trusts the float, as
  the 93 pair shows. When porting, carry the exactness strategy across along with the algorithm.

The rule underneath all of these: a float may *propose* an answer as long as something exact
*decides* it, unless you can state the error bound that makes the float good enough to decide on
its own.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0800](/solutions/0800/) — Hybrid Integers

<!-- /problems -->
