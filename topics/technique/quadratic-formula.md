<!-- tags: [quadratic-formula] -->
<!-- status: final -->
# Quadratic formula

The [quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula) is the first closed form
most engineers learn and the last one they think of as a performance tool. In the problems below it
is almost never used to "solve an equation" as an end in itself. It is used to **delete a search**:
an unbounded scan becomes a constant-time test, a `while` loop with a check in its body becomes a
`for` loop with a known trip count, a two-sided constraint becomes an interval, and a factorisation
becomes a square root.

## The idea

For `ax² + bx + c = 0` the roots are `x = (-b ± √Δ) / 2a` with discriminant `Δ = b² - 4ac`. That is
three separate pieces of information, and these problems use them separately:

- **The roots** — the actual values, when you want an intersection point or a side length.
- **The discriminant** — whether roots exist at all, and over the integers whether they are
  *integers*: `Δ` must be a [perfect square](https://en.wikipedia.org/wiki/Square_number).
- **The sign structure** — an upward parabola is `≤ 0` exactly *between* its roots, which turns a
  quadratic inequality into a closed interval.

Most of the leverage comes from the last two. You often never compute a root at all.

## Inverting a closed form

Any figurate number is a quadratic in its index, so its membership test is the formula run backwards.
Triangular `T(n) = n(n+1)/2` rearranges to `n² + n - 2T = 0` with `Δ = 8T + 1`; pentagonal gives
`24P + 1`; hexagonal gives `8H + 1`. So *"is this number triangular?"* is *"is `8T + 1` a perfect
square?"* — no table, no upper bound, no memory.

Problem 45 pushes it one step further, fusing two tests into one modulo:

```python
if (1 + 24 * triangular_number) ** 0.5 % 6 == 5.0:      # pentagonal
    if (1 + 8 * triangular_number) ** 0.5 % 4 == 3.0:   # hexagonal
```

The inverse of the pentagonal form is `n = (1 + √(1 + 24P)) / 6`, so the root must be both an exact
integer *and* congruent to `5 mod 6` for that division to land on an integer. A float `%` returning
exactly `5.0` asserts both at once. Problem 42 uses the same move to classify thousands of word
values against a set it never builds — [closed form over
iteration](/topics/takeaway/closed-form-over-iteration) in its cheapest form.

## Bounding a loop

If a quantity you are sweeping is quadratic in the loop index, the loop's bound is a root. Problem
141 generates candidates as `n = k²·p³q + k·q²` and needs every `k` with `n < limit`; rather than
incrementing `k` and testing, it solves `a·k² + b·k - (limit-1) = 0` and floors the positive root.
The trip count is known before the loop starts and the comparison leaves the hot body entirely.

The inequality form is stronger still, because it bounds from *both* sides. Problem 932 needs its
right-hand digit block to have exactly `d` digits, which rearranges to `s² - (m+1)s + low·m ≤ 0`;
the parabola opens upward, so the feasible `s` are precisely the closed interval between the two
roots. A predicate that would have filtered candidates instead enumerates them. Problem 246 applies
the same shape one level up: its visual-angle predicate is a quadratic in `w = u²`, and showing the
discriminant is positive for every row is what proves a two-branch condition collapses into a single
band per row.

These bounds are *iteration counts*, so an off-by-one is a wrong answer rather than a crash. Both
problems handle that the same way, and it is the right instinct: compute the endpoint approximately,
pad outward by a couple of units, and let an exact integer test walk back in. That is far cheaper
than proving your rounding was correct.

## Two roots, one meaning

When the quadratic comes from geometry, both roots are real and both are *somewhere on the picture* —
only one is the answer. Problem 587 intersects the line `y = mx` with a unit circle, giving
`(1+m²)x² - 2(1+m)x + 1 = 0`, whose discriminant collapses beautifully: `(1+m)² - (1+m²) = 2m`, so
`x = ((1+m) ± √(2m)) / (1+m²)`. The two roots are the two crossings of the arc, and only the smaller
one bounds the region being integrated. Problem 247 solves `(x+s)(y+s) = 1` for the side of the
largest square fitting a corner and wants the positive root.

Picking the wrong branch is the most dangerous failure mode in this whole technique, because nothing
errors — you get a real number, of a plausible magnitude, describing a different point.

## Where it breaks numerically

The formula is exact; the evaluation is not. Four failure modes recur, in rough order of how often
they bite:

**Catastrophic cancellation.** When `4ac` is small next to `b²`, `√Δ ≈ |b|`, and the root formed by
*subtracting* them is a difference of nearly equal floats — the leading digits annihilate and you
keep noise. The fix is the rationalised form, obtained by multiplying through by the conjugate:

```
x = (-b - √Δ) / 2a        →        x = 2c / (-b + √Δ)
```

Identical in exact arithmetic, and immune in floating point because the surviving operation is an
addition. Problem 247 makes this substitution the load-bearing decision of the whole solution: at
`x ≈ 1200` the naive form carries a relative error around `2 × 10⁻¹¹`, the rationalised form around
`7 × 10⁻¹⁷` — the difference between a ranking of ten million near-equal reals being wrong and being
exact under plain `double`. The rule to remember: **take the root that adds, and recover the other
from the constant term.**

**Float `sqrt` on large integers.** `math.sqrt(n).is_integer()` is a perfect-square test only while
`n` stays inside the mantissa. Above roughly `2⁵²` it starts returning `True` for non-squares —
`4503599761588226` is not a square and `math.sqrt` says it is. Use
[`math.isqrt`](/topics/technique/integer-square-root) and compare `r*r == n`. The figurate solutions
above are safe because their discriminants stay near `10¹⁰`; anything sweeping to `10¹⁸` is not.

**Taking the root when you did not need to.** The strongest version of the fix is to never leave the
integers. Problem 246 needs `u² < A + 2√t`; setting `k = u² - A` makes that exactly *"`k < 0`, or
`k² < 4t`"* — squaring the comparison instead of rooting the operand. The boundary is then decided by
[exact arithmetic](/topics/takeaway/exact-arithmetic-for-equality), so a lattice point lying
precisely on the ellipse is excluded because the problem says so, not because a rounding happened to
fall the right way.

**Discriminant overflow.** `b² - 4ac` is quadratic in its inputs, so it overflows long before the
values you are comparing do — [watch the integer width](/topics/takeaway/watch-integer-width).
Problem 141's `4·p³·q·limit` reaches about `4 × 10²⁴` and problem 932's `(m+1)²` sits near `10³⁰`;
both need [`__int128`](/topics/technique/int128) in C. Python's unbounded integers hide this
completely until you port the code, which is exactly when it is most expensive to discover.

## Sum and product, for free

One more use is worth internalising on its own. By
[Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas), if `p + q = S` and `pq = P`
then `p` and `q` are the roots of `x² - Sx + P = 0`. So **whenever a derivation hands you the sum and
product of two unknowns, you already have the unknowns** — they fall out of `√(S² - 4P)`, and
`S² - 4P` being a perfect square is precisely the test for whether an integer pair exists at all.
Problem 241 uses this to split a two-prime tail whose sum and product both drop out of the residual
condition, replacing an [integer factorisation](/topics/technique/integer-factorization) of a number
far beyond any sieve with one integer square root.

## How to reason about it

Reach for the quadratic formula when the *bound* of a loop or the *test* at its head is what costs,
not the body. It converts control flow into arithmetic, and arithmetic is what you can make exact.

- **Prefer, in order:** no square root (square the comparison) → integer square root → float root
  with a padded exact walk → float root trusted. Only the last one is a bug waiting to surface, and
  it is the one people write first.
- **Decide which root before you write the line.** Sketch the parabola or the geometry; a formula
  that yields two answers to a question with one answer needs an argument, not a `±`.
- **Check the discriminant's magnitude, not the result's.** It is the intermediate that overflows.
- **A perfect-square discriminant is an integrality test.** That is often the whole point: not the
  root's value, just whether it exists in the integers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0932](/solutions/0932/) — $2025$

<!-- /problems -->
