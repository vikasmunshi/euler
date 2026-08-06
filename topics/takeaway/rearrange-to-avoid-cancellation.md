<!-- tags: [rearrange-to-avoid-cancellation] -->
<!-- status: final -->
# Rearrange a formula to avoid cancellation

A formula that is exact on paper can still be wrong in `double`, and the culprit is almost always
one subtraction of two nearly equal quantities. The fix is rarely a wider type or a smarter
algorithm: it is algebra. Multiply through by a conjugate, factor differently, or reach for a
library primitive, and the same value comes out of an **addition** instead — same cost, same
result in exact arithmetic, ten more correct digits in floating point.

## The idea

A `double` carries $53$ significant bits, about $16$ decimal digits, and every operation rounds to
the nearest representable value with relative error at most
[machine epsilon](https://en.wikipedia.org/wiki/Machine_epsilon)
$\varepsilon \approx 1.1 \times 10^{-16}$. Multiplication, division, square roots and additions of
like-signed operands all preserve that bound: the relative error of the result stays within a small
multiple of $\varepsilon$, so error accumulates slowly and predictably.

Subtraction of near-equal values is the exception, and the reason is subtle. The subtraction itself
is typically **exact** — when $a$ and $b$ are within a factor of two,
[Sterbenz's lemma](https://en.wikipedia.org/wiki/Sterbenz_lemma) says $a - b$ is representable
exactly. What blows up is the error the operands *already carried*. Each input is really
$a(1 + \delta_a)$ and $b(1 + \delta_b)$ with $|\delta| \lesssim \varepsilon$, so the computed
difference has relative error roughly

$$\varepsilon \cdot \frac{|a| + |b|}{|a - b|}.$$

That amplification factor is the [condition number](https://en.wikipedia.org/wiki/Condition_number)
of the subtraction. If $a$ and $b$ agree in their first $k$ digits, it is about $10^{k}$: you keep
$16 - k$ digits and the rest is noise promoted to the leading position. This is
[catastrophic cancellation](https://en.wikipedia.org/wiki/Loss_of_significance) — catastrophic not
because a large error appears, but because a *pre-existing* small one is magnified until it is the
whole answer.

The rearrangement that fixes it is the conjugate. For a difference of square roots,

$$\sqrt{a} - \sqrt{b} \;=\; \frac{a - b}{\sqrt{a} + \sqrt{b}},$$

the ill-conditioned subtraction moves into the numerator, where $a - b$ is computed from operands
that are *not* the result of long chains of rounding, and the denominator — an addition of two
positives — is perfectly conditioned. The [quadratic formula](/topics/technique/quadratic-formula)
is the classic instance. Of the two roots of $ax^2 + bx + c$, the one whose numerator adds
$-b$ and $\pm\sqrt{b^2 - 4ac}$ with matching signs is safe; the other subtracts them and loses
digits whenever $4ac \ll b^2$. Multiplying by the conjugate, or equivalently using
[Vieta's formula](https://en.wikipedia.org/wiki/Vieta%27s_formulas) $x_1 x_2 = c/a$, gives the
stable companion:

$$x = \frac{-b + \sqrt{b^2 - 4ac}}{2a} \;=\; \frac{2c}{-b - \sqrt{b^2 - 4ac}}.$$

Problem 247 lives on exactly this edge. Its greedy packing of squares under $y = 1/x$ asks, at
every node of a region tree with hundreds of thousands of nodes, for the positive root of
$(x + s)(y + s) = 1$. Written straight from the quadratic formula that root is a difference of
$\sqrt{(x-y)^2 + 4}$ and $x + y$ — two quantities that converge as the packing marches right along
the bottom row and $x$ grows past $10^3$. Written as $2(1 - xy)$ over their **sum**, it is
computed from a numerator that is the region's genuine slack and a denominator that is a benign
addition. Measured against $50$-digit [decimal](https://docs.python.org/3/library/decimal.html)
arithmetic, on the simplified $y = 0$ case ($s = \tfrac{1}{2}(\sqrt{x^2+4} - x) = 2/(x + \sqrt{x^2+4})$):

| $x$ | relative error, difference form | relative error, sum form |
| --- | --- | --- |
| $10$ | $3.4 \times 10^{-15}$ | $8.6 \times 10^{-17}$ |
| $10^2$ | $2.8 \times 10^{-13}$ | $1.8 \times 10^{-16}$ |
| $1.2 \times 10^3$ | $2.5 \times 10^{-11}$ | $7.0 \times 10^{-17}$ |
| $10^6$ | $7.6 \times 10^{-6}$ | $3.2 \times 10^{-17}$ |

The right-hand column is flat at one rounding; the left-hand one degrades as $\varepsilon x^2$.
Both forms cost one square root.

## Condition the answer, not just the expression

Knowing an expression is ill-conditioned is only half the question. What matters is whether the
error survives into the thing you actually report. Problem 247 reports a **rank** — how many
squares are at least as large as a given one — so the arithmetic only has to order sides correctly
near the threshold. Along the bottom row the sides go as $s_k \approx 1/\sqrt{2k}$, so two
neighbours differ in relative terms by about $1/(2k) \approx 1/x^2$, while the difference form's
error is about $\varepsilon x^2$. The ratio of error to gap is $\varepsilon x^4$: at the main case,
$x$ reaches roughly $1.3 \times 10^3$ and the margin is four orders of magnitude; at the larger
$(3,4)$ case, $x \approx 9 \times 10^3$ and $\varepsilon x^4$ is of order one — the margin is gone.
A formulation that merely happens to work at the size you tested, and fails one step up, is not a
formulation you want. The rearrangement removes the question rather than answering it.

Determinism is a separate property from accuracy, and it is easy to conflate the two. A pruned
search that recomputes its own threshold by the identical sequence of operations gets a
bit-for-bit identical `double` back, so a `<` comparison against it is consistent without an
epsilon — but consistently comparing against a value that is wrong in its eleventh digit still
gives the wrong count. Reproducibility buys you the boundary case; conditioning buys you the
answer.

## The moves

Most cancellation has a standard rewrite. The pattern to recognise is *a small result assembled
from large nearly-equal parts*; the fix is to find an expression in which the small quantity is
produced directly.

| Ill-conditioned | Stable equivalent |
| --- | --- |
| $\sqrt{a} - \sqrt{b}$ | $(a - b) / (\sqrt{a} + \sqrt{b})$ |
| unlucky root of $ax^2+bx+c$ | conjugate form / Vieta's $x_1 x_2 = c/a$ |
| $e^x - 1$, small $x$ | [`expm1(x)`](https://docs.python.org/3/library/math.html#math.expm1) |
| $\log(1 + x)$, small $x$ | [`log1p(x)`](https://docs.python.org/3/library/math.html#math.log1p) |
| $1 - \cos x$, small $x$ | $2\sin^2(x/2)$ |
| $1/(1+x) - 1$ | $-x/(1+x)$ |
| $\dfrac{A}{B} - \dfrac{C}{D}$, both huge | factor the huge part out as a single product |

Problem 461 is the `expm1` case at full scale: it hunts for four indices whose $e^{k/n} - 1$ terms
sum closest to $\pi$, and for small $k/n$ that difference is two values near $1$ subtracted. Since
the search is decided by agreement in the far decimals, the library primitive — which computes
$e^x - 1$ without ever forming the intermediate near-$1$ value — is not a refinement but a
precondition.

Problem 235 shows the last row. Its bisection needs the sign of a quantity involving $r^n$ for
large $n$; written as a difference of two enormous quotients, the two sides annihilate and the sign
becomes noise. Written as $r^n \cdot \text{high} + \text{low}$, the enormous factor appears once, in
a product, and never has to cancel against a sibling. That arrangement pays a second dividend in C:
when $r^n$ overflows during the bracket search, a product yields a signed infinity, whose sign is
still usable by the bisection, where a difference of overflowing quotients yields a NaN and the
search dies.

Sometimes the luck runs the other way and you should notice. Problem 44 inverts the pentagonal
formula with the root that happens to add:

```python
def is_pentagonal_number(n: int) -> bool:
    """Test pentagonality in O(1) by inverting the quadratic: n = (1 + sqrt(1 + 24m)) / 6."""
    return ((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()
```

That is the well-conditioned root of the same quadratic — the sign in the numerator matches, so
nothing cancels, and the test is safe for every $n$ the problem reaches. Had the geometry called
for the other root, the identical-looking line would have quietly lost digits. Which root you took
is worth one deliberate thought, not an assumption.

## When no rearrangement exists

Rearrangement works when the cancellation is *local* — a couple of terms whose algebra you can
rewrite. It does not help when the cancellation is the structure of the computation. An
alternating [inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
sum whose terms span many orders of magnitude and whose total is tiny, as in problem 239, cannot
be re-associated into safety: there is no conjugate for a hundred-term alternating series. The
answer there is to leave floating point entirely, carry the whole computation in exact integers or
rationals ([arbitrary-precision arithmetic](/topics/technique/arbitrary-precision-arithmetic)), and
convert once at the very end — the same reflex as
[using exact arithmetic for equality checks](/topics/takeaway/exact-arithmetic-for-equality).

Higher-precision floating point is best treated as a **diagnostic**, not a repair. Re-running a
suspect computation at $40$ digits and comparing tells you how many of your `double` digits were
real; if the answer moves, precision was covering a structural problem that will reappear one input
size later.

## How to reason about it

- **Audit the subtractions.** Every other operation is safe by default. Scan a numeric routine for
  `-` between quantities that can approach each other, and for the differences hiding inside
  `expm1`-shaped expressions — `exp(a) - exp(b)`, `log(a) - log(b)`, `1 - cos`, `x - sin x`.
- **Estimate the loss before fixing it.** Digits lost is $\log_{10}\!\big((|a|+|b|)/|a-b|\big)$. If
  the operands agree to three digits you are still fine; to twelve, you have nothing left.
- **Make the small quantity the numerator.** The goal of the rewrite is that the genuinely small
  result is *computed*, not *left over*. If your rearranged form still ends with a near-zero
  difference on top, you moved the problem rather than solving it.
- **Prefer the library primitive.** `expm1`, `log1p`, `hypot`, `fma` exist precisely because these
  rewrites are error-prone; they are vetted, often correctly rounded, and no slower.
- **Ask what precision the *answer* needs.** A comparison needs the error to be smaller than the
  gap between neighbours; a rank among $10^7$ near-equal reals is a far harsher requirement than
  printing six decimals. Work that budget out before deciding `double` suffices — it is the same
  discipline as [reducing algebraically before coding](/topics/takeaway/reduce-before-coding).
- **Validate against an independent route.** Agreement between a `decimal` rerun, or an algorithm
  that never forms the difference at all, is the only real evidence that a floating-point result is
  sound.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0247](/solutions/0247/) — Squares Under a Hyperbola

<!-- /problems -->
