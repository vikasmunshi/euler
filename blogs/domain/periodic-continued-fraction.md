<!-- tags: [periodic-continued-fraction] -->
<!-- status: final 2026-10-14T12:05Z -->
# Periodic continued fraction

Every irrational number has an infinite continued fraction, and for most of them the partial
quotients never settle into any pattern. Square roots are the exception. By
[Lagrange's theorem](https://en.wikipedia.org/wiki/Periodic_continued_fraction) a real number has an
eventually periodic expansion exactly when it is a quadratic irrational, and for √D the shape is
especially rigid. That rigidity is why √D keeps turning up. The expansion is produced by a finite
integer recurrence, the cycle in that recurrence answers counting questions (64), and the
convergents it produces along the way contain the solutions of
[Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation) (66) and the best rational
approximations to √D (192).

## The idea

### The shape of √D

For a non-square D, with a₀ = ⌊√D⌋,

    √D = [a₀; a₁, a₂, …, a_{L−1}, 2a₀]   (the bar over a₁ … 2a₀ repeats forever)

Two facts hold for every D, and both are useful:

- the period always **ends on 2a₀**, and that is the only place 2a₀ appears;
- the part before it, a₁ … a_{L−1}, is a **palindrome**.

For example √13 = [3; 1, 1, 1, 1, 6] has period L = 5, √7 = [2; 1, 1, 1, 4] has L = 4, and
√61 = [7; 1, 4, 3, 1, 2, 2, 1, 3, 4, 1, 14] has L = 11.

### The recurrence: no floating point

Every complete quotient of √D (the tail of the expansion read from position k) has the form
(√D + mₖ) / dₖ with integers mₖ, dₖ. Taking the floor and reciprocal of that form gives a recurrence
on three small integers:

    m ← d·a − m
    d ← (D − m²) / d        # always an exact division
    a ← (a₀ + m) // d

It starts at (m, d, a) = (0, 1, a₀). The third line uses a₀ in place of √D, and the floor still
comes out exact, because d > 0 and replacing √D with its integer part cannot cross an integer
boundary. All three values stay below 2√D, so the whole expansion fits in machine integers for any
D a problem will give you. This is the same three-line kernel in 64, 66 and 192. The
[MathWorld entry](https://mathworld.wolfram.com/PeriodicContinuedFraction.html) and the
[Wikipedia derivation](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Continued_fraction_expansion)
give the algebra.

Since the state takes only finitely many values and each step is invertible, the sequence of states
is purely periodic after a₀. You can count the period by watching for a repeated `(m, d, a)`. The
public solution to 64 does it that way, and its notes give the reasoning. The cheaper stopping
rule is the first fact above: **stop when a = 2a₀**, which is equivalent to d = 1 (the state
returning to its starting value). That makes 64 a loop of L steps per D with no memory at all.

### The identity that connects it to Pell

Build the convergents pₖ/qₖ with the usual two-term recurrence
(pₖ = aₖpₖ₋₁ + pₖ₋₂, and the same for q). Then each convergent satisfies

    pₖ² − D·qₖ² = (−1)^(k+1) · d_{k+1}

which ties the convergents to the recurrence above: the "error" of each convergent, measured as a
norm, is the next d. Here is √13 worked through:

| k | aₖ | pₖ/qₖ | pₖ² − 13qₖ² | d_{k+1} |
|---|----|-------|-------------|---------|
| 0 | 3 | 3/1 | −4 | 4 |
| 1 | 1 | 4/1 | 3 | 3 |
| 2 | 1 | 7/2 | −3 | 3 |
| 3 | 1 | 11/3 | 4 | 4 |
| 4 | 1 | 18/5 | **−1** | **1** |
| … | | | | |
| 9 | 1 | 649/180 | **+1** | **1** |

d returns to 1 exactly at the end of each period, k = L−1, 2L−1, …. At those indices the norm is
±1, and its sign is (−1)^L. So:

- **L even:** p_{L−1}² − D·q_{L−1}² = +1, and (p_{L−1}, q_{L−1}) is the fundamental solution of
  x² − Dy² = 1.
- **L odd:** the first period gives the **negative** Pell equation x² − Dy² = −1 (18² − 13·5² = −1).
  You have to run a second period to reach +1, at index 2L−1 (649² − 13·180² = 1).

This is why 64 and 66 belong together. The odd periods that 64 counts are exactly the D for which
x² − Dy² = −1 is solvable, and they are the D for which 66 has to walk a second period. It is also
why 66 can't be brute-forced. For D = 61, with L = 11, the fundamental x is 1766319049, and for
other D ≤ 1000 it runs past 10³⁰. The cost of finding it is governed by the period, which is
O(√D log D), rather than by the size of the answer.

### Best approximations

The same convergents are the best rational approximations to √D. 192 bounds the denominator and
asks for the closest fraction. The answer is either the last convergent under the bound or the
largest semiconvergent (p_{k−1} + t·pₖ)/(q_{k−1} + t·qₖ) that still fits, since the two lie on
opposite sides of √D. The problem's own example shows the overlap with Pell: 18/5, the best
approximation to √13 with denominator at most 20, is the convergent that solves the negative Pell
equation. 656 reaches the same expansion from another direction. The palindromic prefixes of the
Sturmian sequence ⌊nα⌋ − ⌊(n−1)α⌋ have lengths fixed by the continued fraction of α. For α = √β
that expansion is periodic, so after one period the pattern repeats.

## How to reason about it

- **Recognise the trigger.** Use this machinery when a problem asks for √D, an equation
  x² − Dy² = N, "closest fraction with denominator ≤ d", or a quantity that grows with the period of
  something quadratic. Geometry problems that reduce to a Pell equation (very common past 100) belong
  here too. Once the equation is in the form x² − Dy² = 1, the
  continued-fraction kernel finds the fundamental solution. Every other solution comes from powers
  of x + y√D, so a family of solutions is a linear recurrence and you never need to search for it.
- **Stay in integers.** Use `math.isqrt` for a₀ and the integer recurrence for everything else.
  Computing `floor((sqrt(D) + m) / d)` in floating point works for small D (66's public solution
  does this with D ≤ 1000) but fails silently once √D loses precision. The integer form costs
  nothing and has no such limit.
- **Big numbers live only in p and q.** m, d and a stay below 2√D. The convergent numerators and
  denominators grow exponentially in k, so Pell solutions need Python integers (or a bignum in C).
  Problems with a bounded denominator, like 192, can stop at the bound and stay within 64 bits.
- **Get the convergent index right.** The usual off-by-one is between "period length" and "index of
  the convergent". If you count a₀ as index 0, the period ends at k = L−1. Let the d = 1 condition
  tell you when you are there rather than doing the arithmetic on L, and check the sign of the norm
  instead of predicting it.
- **Generate the convergents forward.** The two-term recurrence costs O(1) per step and gives every
  prefix. Evaluating a chosen convergent from the inside out, as 66 does, is correct, but it repeats
  work each time you need a different index.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0192](/solutions/0192/) — Best Approximations
- ○ [0656](/solutions/0656/) — Palindromic Sequences

<!-- /problems -->
