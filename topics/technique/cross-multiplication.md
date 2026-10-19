<!-- tags: [cross-multiplication] -->
<!-- status: final 2026-10-19T06:48Z -->
# Cross-multiplication

[Cross-multiplication](https://en.wikipedia.org/wiki/Cross-multiplication) replaces a test on
fractions with a test on integers: $\frac{p}{q} = \frac{r}{s} \iff ps = rq$, and for positive
denominators $\frac{p}{q} < \frac{r}{s} \iff ps < rq$. The point in code is *exactness*. A
division in floating point rounds, and an equality or a strict inequality evaluated on rounded values can
go the wrong way exactly at the boundary the problem cares about. The cross-multiplied form uses
only integer multiplication, so it is exact as long as the products fit. The three solved problems
below use it for a digit puzzle's equality (33), a "proportion reaches exactly 99%" stopping test
(112), and a geometric boundary where a point *on* the curve must be excluded (246).

## The idea — move the denominators to the other side

Every use is the same algebra applied with a little care:

- **Equality.** $p/q = r/s \iff ps = rq$ (for $q, s \ne 0$). No signs to watch.
- **Inequality.** Multiplying by $qs$ preserves direction only when $qs > 0$. With denominators known to be positive,
  which covers counts, lengths and squared quantities, $p/q < r/s \iff ps < rq$. Otherwise, normalise
  signs first.
- **Square roots, too.** $x < \sqrt{t}$ (with $t \ge 0$) is $x < 0$ or $x^2 < t$. Each square root is
  removed by a case split on sign and a squaring, so a comparison involving a root also stays in
  integers.
- **Width.** $ps$ is roughly the square of the inputs. Check it fits, or use `__int128` or Python's
  unbounded `int`.

The alternative is to keep fractions as fractions, with Python's
[`fractions.Fraction`](/topics/technique/fractions-fraction). That is equally exact but allocates and reduces by gcd on every
operation. Cross-multiplication is the zero-cost version when you only need to *compare*.

## Three uses across the problems

**33, digit cancelling fractions: an exact equality.** Two-digit fractions $\frac{10a + x}{10x + b}$
that "cancel" the shared digit $x$ correctly satisfy $\frac{10a+x}{10x+b} = \frac{a}{b}$. The test is
written cross-multiplied, so a few hundred candidate triples are checked with exact integer equality.
The public Python:

```python
if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator
```

The four matches are then multiplied together. Python folds them as `Fraction`s, which reduce
automatically. C multiplies the numerators and denominators separately and divides both by their gcd at the end,
which is cross-multiplication's partner idea: postpone the division to a single exact step.

**112, bouncy numbers: an exact proportion.** Scan $n = 1, 2, \dots$, counting bouncy numbers, and
stop when the proportion is *exactly* 99%. As floats, `bouncy / n == 0.99` is fragile: $0.99$ is not
representable in binary, and the quotient is rounded. Cross-multiplied, it is
`bouncy * 100 == target * n`, an equality of integers that holds exactly when it should. The
same form is what lets the solution be checked against the stated 50% and 90% milestones.

**246, tangents to an ellipse: a strict boundary in integers.** Lattice points from which an ellipse
subtends more than $45^\circ$ form a band between the ellipse and an isoptic curve. Both ends of each
row's band are found by exact integer tests, and cross-multiplication does the work at both:

- *Inner end, strictly outside the ellipse:* $\frac{u^2}{a^2} + \frac{v^2}{b^2} > 1$ becomes
  $u^2 b^2 > a^2(b^2 - v^2)$. A point exactly on the ellipse has only one tangent and must be
  excluded. Any rounding there could admit it.
- *Outer end, the isoptic bound:* $u^2 < \text{base} + 2\sqrt{t}$ becomes "$k = u^2 - \text{base} < 0$,
  or $k^2 < 4t$", the square-root rule above.

A float `isqrt` estimate seeds each search, and the exact predicate then corrects it, so the boundary
decision never depends on floating-point accuracy.

## Python and C

- **Width.** All three fit in 64 bits. 33's products are below $10^4$, and 112's are below $10^9$. 246's
  $u^2 b^2$ reaches about $1.8 \times 10^{15}$ and $4t$ about $4.4 \times 10^{16}$, inside `long long`. The 246
  notes check that explicitly. Python never needs the check.
- **Fractions.** 33's Python keeps the product as an exact `Fraction` folded with `functools.reduce`,
  so `.denominator` is already reduced. C accumulates two `long long` products and divides by
  `gcd` once.
- **Square roots.** Python's `math.isqrt` is exact. C seeds from `sqrtl` and corrects with `while`
  loops before any cross-multiplied test uses the result, so both languages make identical boundary
  decisions.

## How to reason about it

- **Never compare quotients for equality in floating point.** Cross-multiply, or use `Fraction`.
- **Know the signs before cross-multiplying an inequality.** Positive denominators keep the direction.
  Otherwise, normalise first.
- **Remove square roots by case split and squaring.** $x < \sqrt t \iff x < 0 \lor x^2 < t$, which keeps
  geometric boundaries exact.
- **Use floats only for a starting estimate.** A float may seed a search for the boundary, but the
  final decision should be an exact integer predicate.
- **Check the product width.** Cross-multiplication roughly squares magnitudes. Plan for `__int128` or
  Python when the inputs approach $2^{31}$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0246](/solutions/0246/) — Tangents to an Ellipse

<!-- /problems -->
