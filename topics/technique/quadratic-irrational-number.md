<!-- tags: [quadratic-irrational-number] -->
<!-- status: final 2026-10-28T08:26Z -->
# Quadratic irrational number

A [quadratic irrational](https://en.wikipedia.org/wiki/Quadratic_irrational_number) is an
irrational root of a quadratic with integer coefficients, which always has the form
`a + b√d` with rational `a`, `b` and a non-square integer `d`. `√2`, the golden ratio
`φ = (1 + √5)/2` and `⌈√a⌉ + √a` are all of this kind. The companion page,
[irrational number](/topics/domain/irrational-number), is about the general problem of getting
integer facts out of numbers you cannot store. This page is about the special case where you
don't have to give anything up: a quadratic irrational is completely described by **two
rationals**, and you can add, multiply, divide and compare these numbers using integers alone.
Three tools do nearly all of the work in the problems below: pair arithmetic, the conjugate, and
the periodic continued fraction.

## The idea: compute on the coordinates, never on the value

### A number is a pair

Fix `d`. Every element of the field `ℚ(√d)` is a pair `(a, b)` meaning `a + b√d`, and the
pairs close under arithmetic because `√d · √d = d` is an integer:

$$ (a_1 + b_1\sqrt d)(a_2 + b_2\sqrt d) = (a_1 a_2 + d\,b_1 b_2) + (a_1 b_2 + a_2 b_1)\sqrt d $$

That one line is the whole arithmetic. With integer coordinates the pairs form the ring
`ℤ[√d]`. It works modulo a prime too, which is how [Problem 721](/solutions/0721/) takes the
power `(c + √a)^n` for `n` in the trillions. It runs
[exponentiation by squaring](/topics/technique/exponentiation-by-squaring) on pairs `(u, v)`
reduced mod `p`, and the irrational number never touches a float. Because `√d` is irrational,
`a₁ + b₁√d = a₂ + b₂√d` holds only when `a₁ = a₂` and `b₁ = b₂`. So equality is exact and
"is this an integer?" just means "is `b = 0`?".

[Problem 473](/solutions/0473/) uses exactly that test. A palindrome in base `φ` is a sum of
mirrored pairs `φ^k + φ^{-(k+1)}`. Each power of `φ` is `(L_k + F_k√5)/2` in terms of the
[Lucas](https://en.wikipedia.org/wiki/Lucas_number) and
[Fibonacci](https://en.wikipedia.org/wiki/Fibonacci_sequence) numbers, so every candidate sum is
a pair of integers, stored doubled so that the halves of `ℤ[φ]` stay integral. The sum is an
integer exactly when its `√5` coordinates cancel to zero. The search can use a float of the
value to prune branches, but it accepts a candidate only on the exact integer test. A float
asked "is this an integer?" gives no reliable answer.

### The conjugate and the norm

Swapping the sign of the root gives the
[conjugate](https://en.wikipedia.org/wiki/Conjugate_(square_roots)): the conjugate of
`α = a + b√d` is `ᾱ = a − b√d`. Both are roots of the same quadratic, so anything symmetric in
them is rational:

$$ \alpha + \bar\alpha = 2a, \qquad N(\alpha) = \alpha\bar\alpha = a^2 - d\,b^2 $$

The [norm](https://en.wikipedia.org/wiki/Field_norm) `N` is multiplicative,
`N(αβ) = N(α)N(β)`, and that gives three standard moves:

- **Division without division.** `1/α = ᾱ / N(α)`. You rationalise the denominator and the
  result is a pair again.
- **Powers that are integers.** `αⁿ + ᾱⁿ` is an integer that follows a linear recurrence. If
  `|ᾱ| < 1`, then `ᾱⁿ` is a sliver and `⌊αⁿ⌋` follows from it. This is Problem 721's floor
  trick, worked through on the [companion page](/topics/domain/irrational-number#pair-it-with-its-conjugate).
  In pair form you get it almost for free: if `αⁿ = u + v√d` then `αⁿ + ᾱⁿ = 2u`.
- **Diophantine equations as norms.** `x² − Dy² = 1` says `N(x + y√D) = 1`. That is
  [Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation). Since the norm is
  multiplicative, once you have the smallest solution, its powers `(x₁ + y₁√D)^k` give every
  other one. All the difficulty is in finding that first solution.

### Continued fractions are periodic

By [Lagrange's theorem](https://en.wikipedia.org/wiki/Periodic_continued_fraction), a real number
has an eventually periodic
[continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) exactly when it is a
quadratic irrational. For `√D` the expansion is `[a₀; a₁, …, a_{L−1}, 2a₀]`, where the
repeating block ends on `2a₀`. Each complete quotient has the shape `(√D + m)/n` with integers
`m` and `n`, so the expansion runs on a three-integer state and needs no real numbers at all.
[Problem 66](/solutions/0066/) generates it like this:

```python
while continued_fraction[-1] != 2 * continued_fraction[0]:
    m = n * continued_fraction[-1] - m
    n = (d - m * m) // n
    continued_fraction += (math.floor((sqrt_d + m) / n),)
```

The division `(d − m²) // n` is always exact, which is a fact about the conjugate, not a
coincidence. The convergents `p/q` of this expansion are the best rational approximations to
`√D`, and the one at the end of the first period (or the second period, when `L` is odd)
satisfies `p² − Dq² = 1`. That is the fundamental Pell solution. Problem 66 maximises it over
`D ≤ 1000`. The search is hopeless, because for `D = 61` the smallest `x` is already
1,766,319,049. The continued fraction finds it in about twenty steps, and Python's `Fraction`
evaluates the convergent exactly.

## How to reason about it

- **Recognise the shape.** Look for a square root of a non-square inside a power, a floor, a base
  or a Diophantine equation. `φ`, `√2 ± 1`, `x² − Dy² = ±1` and "the floor of a huge power" are
  the usual signs. The number lives in `ℚ(√d)`, so you can keep it as two coordinates.
- **Pick the ring before you write code.** Integer pairs in `ℤ[√d]` are exact but can grow without
  bound. Pairs mod `p` are bounded, which is right when the problem asks for a residue (721).
  For `φ`, store doubled coordinates, or use the basis `a + bφ` with `φ² = φ + 1`, so the
  halves never appear (473).
- **Let the conjugate do the bookkeeping.** Every `+`/`−` pair, every norm, every "rationalise
  the denominator" is the conjugate. If you find yourself subtracting two nearly equal floats,
  the conjugate usually gives you the difference exactly.
- **Floats can guide, but never decide.** A float value is fine for ordering or pruning when it
  has a safety margin (473). Membership, equality, floors and Pell checks should all be decided
  by integer arithmetic on the coordinates.
- **Watch for the floor of the root itself.** Problem 66 takes `⌊(√D + m)/n⌋` as a float, which
  is safe for `D ≤ 1000`. The exact form needs no float at all: since `n > 0`, it equals
  `(⌊√D⌋ + m) // n`, with `⌊√D⌋ = math.isqrt(D)`. Use that form once `D` grows.
- **Handle the rational exceptions separately.** When `d` is a perfect square the "irrational"
  collapses to an integer. Pell then has only the trivial solution, the expansion of `√D` stops
  after one term, and 721's conjugate becomes `0`. Check for it first.
- **Mind the width.** Coordinates grow geometrically under powers. Pell solutions overflow 64
  bits well before `D = 1000`, and 473's doubled values need `__int128` in C. Use Python's `int`, reduce
  mod `p`, or plan the integer width ahead of time.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers

<!-- /problems -->
