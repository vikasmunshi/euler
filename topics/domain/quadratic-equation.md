<!-- tags: [quadratic-equation] -->
<!-- status: final 2026-10-17T06:35Z -->
# Quadratic equation

A [quadratic equation](https://en.wikipedia.org/wiki/Quadratic_equation) is rarely what a Project
Euler problem *says*. It is what the problem *becomes* once you write it down: a figurate number
asked to be inverted, a generating function asked to take an integer value, a line asked where it
leaves an ellipse, two numbers whose sum and product are both pinned. The page on the
[quadratic formula](/topics/technique/quadratic-formula) covers what to do with `ax² + bx + c = 0`
once you have it — which root, how to evaluate it without cancellation, when the discriminant
overflows. This page is about the step before: **recognising the quadratic, and choosing which of
its structures to exploit.** Often the best answer never evaluates a root at all.

## Four structures a quadratic hands you

A quadratic in one unknown carries more than its roots. The solved problems below each lean on a
different piece:

| Structure | What it buys | Problems |
|---|---|---|
| The inverse of a closed form | O(1) membership test | 42, 44, 45 |
| A perfect-square discriminant | an integrality condition — a Diophantine equation | 137, 757 |
| A root you already know | the other root by one division (Vieta) | 144 |
| A factorisation | a divisibility condition instead of a search | 932 |

Problem 587 (a line meeting a circle) is the plain "solve it and pick the right branch" case, and
the formula page tells that story fully.

## Inverting a closed form

Every [figurate number](/topics/domain/figurate-number) is a quadratic in its index, so "is `t`
triangular?" is "does `n² + n - 2t = 0` have a positive integer root?" — which is "is `8t + 1` a
square?". Problems 42, 44 and 45 are this idea and nothing else; the formula page walks through the
modular trick 45 uses to fuse two tests.

What this page adds is how the two languages differ, because they do. The Python solutions trust
the float:

```python
def is_triangle_number(n: int) -> bool:
    return ((8 * n + 1) ** 0.5).is_integer()
```

The C ports of 42 and 44 do not. They round the float root to the nearest integer and **verify in
integers** — `r*r == 8n+1` in 42, `nth_pentagonal(round(n)) == m` in 44:

```c
double n = (1.0 + sqrt(1.0 + 24.0 * (double)m)) / 6.0;
long long ni = (long long)round(n);
return (ni > 0) && (nth_pentagonal(ni) == m);
```

At these sizes both are correct; the discriminants stay far below `2⁵²`. But the C shape is the one
to copy, because it is correct for a reason: the float only *proposes* a candidate, and exact
arithmetic decides. In Python the clean version is `r = math.isqrt(d); r*r == d`
([integer square root](/topics/technique/integer-square-root)), which needs no float at all.
Problem 45 is the exception on both sides — C keeps the `fmod(sqrt(...), 6.0) == 5.0` test
verbatim — and it works only because `sqrt` is correctly rounded and the values are small.

## The discriminant as a Diophantine equation

When a problem asks for the *integer* or *rational* solutions of something quadratic, the roots
`(-b ± √Δ) / 2a` are rational exactly when `Δ` is a perfect square. That converts "find the inputs
for which this equation has nice roots" into a new equation, `Δ = p²`, in which the unknown roots
have vanished. This is the most productive move on the page, and the two private problems that use
it show where it leads.

**Problem 137** asks when the Fibonacci [generating function](/topics/domain/generating-function)
`A(x) = x / (1 - x - x²)` takes a positive integer value `k` at a rational `x`. Clearing the
denominator gives `kx² + (k+1)x - k = 0`, so `x` is rational iff `5k² + 2k + 1` is a perfect
square — a generalised [Pell equation](/topics/technique/pells-equation), exactly the
[Pell-in-disguise](/topics/number-theory/pells-equation-in-disguise) pattern. The solution never
solves it numerically: the Pell solutions turn out to be products of consecutive Fibonacci numbers,
so the code is just a Fibonacci loop. The C/Python split is all about width. Python multiplies two
Fibonacci numbers freely; C runs the iteration in `unsigned __int128` and formats the result by hand,
because the product passes `2⁶⁴` within the tested range ([`__int128`](/topics/technique/int128)).

**Problem 757** has two pairs with `ab = cd = N` and `a + b = c + d + 1`. Read `a` and `b` as the
roots of `z² - (c+d+1)z + cd = 0`. With `m = d - c`, the discriminant simplifies to

```
Δ = (c + d + 1)² - 4cd = (m + 1)² + 4c
```

and `Δ = p²` rewrites as `p² - (m+1)² = 4c` — a
[difference of two squares](/topics/domain/difference-of-two-squares). Since `p` and `m + 1` share
parity, the two factors are `2g` and `2h`, so `c = gh` and `m = h - g - 1`. The search over four
unknowns has collapsed into a free enumeration over two, `(g, h)` with `g < h`, each pair generating
one valid `N`. That is the general lesson: **a square discriminant usually factors, and the factors
become your loop variables.**

Both sides enumerate the same `(g, h)` grid; they differ in how they deduplicate. Python vectorises
the inner `h` sweep with numpy and pours each row into a `set`; C appends every value to a growing
array and finishes with `qsort` and a run-length count of distinct values — cheaper in memory, and
the sorting cost is paid once rather than in hashing on every insert.

## The root you already know

If you know one root `t₁`, Vieta's `t₁ + t₂ = -b/a` gives the other with no square root. The
commonest source of a known root is a ray leaving a curve: parametrise the ray from a point *on* the
curve, substitute, and the constant term is the curve equation evaluated at the starting point —
zero.

**Problem 144** bounces a laser inside the ellipse `4x² + y² = 100`. From the hit point `(x, y)` along
the reflected direction `(r_x, r_y)`, substituting `(x + t·r_x, y + t·r_y)` gives

```
t²(4r_x² + r_y²) + t(8x·r_x + 2y·r_y) + (4x² + y² - 100) = 0
```

and the last bracket is zero, so `t = 0` is one root and the next hit is the other,
`t = -(8x·r_x + 2y·r_y) / (4r_x² + r_y²)` — one division per bounce. Besides being faster, it is
*more accurate* than the formula: the constant term is only zero up to the drift accumulated over
hundreds of bounces, so a `±√Δ` evaluation would ask the float to tell "zero" from "tiny" every
time. Cancelling the known root analytically removes the question. The Python and C solutions are
line-for-line identical here; plain `double` is all either needs. (The reflection itself is the
[specular reflection](/topics/technique/specular-reflection) formula.)

## Factor it instead of solving it

Sometimes the quadratic factors into pieces with structure, and divisibility does the rest.
**Problem 932** wants numbers whose decimal split `a ‖ b` satisfies `a·10ᵈ + b = (a + b)²`. With
`s = a + b` that becomes `a(10ᵈ - 1) = s(s - 1)`, a quadratic in `s` which nobody needs to solve:
it says `m = 10ᵈ - 1` must divide `s(s - 1)`. Because `s` and `s - 1` are coprime, each prime power of
`m` divides exactly one of them, and the [CRT](/topics/technique/chinese-remainder-theorem) lists the
`2ᵏ` admissible residues of `s` directly. The formula page covers the second half — the digit-count
bound that becomes an interval between two roots.

## How to reason about it

- **Write the problem as a polynomial before writing any loop.** If the unknown appears squared,
  or as a product with its partner, you are holding a quadratic, and one of the four structures
  above probably deletes your search.
- **Integer or rational answers wanted → look at the discriminant first.** `Δ = p²` is the real
  equation; expect it to factor as a difference of squares or to be Pell.
- **A known root is free information.** Ray–curve intersections, recurrences with a fixed point,
  Vieta jumping: divide it out and keep the linear remainder.
- **Let floats propose and integers decide.** The C ports of the figurate tests show the shape;
  `math.isqrt` is the Python way to skip the float entirely.
- **Watch what squaring does to width.** `Δ` and products of roots grow twice as fast as their
  inputs — free in Python, `__int128` in C.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0144](/solutions/0144/) — Laser Beam Reflections
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ○ [0317](/solutions/0317/) — Firecracker
- ● [0318](/solutions/0318/) — 2011 Nines
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0932](/solutions/0932/) — $2025$
- ○ [0935](/solutions/0935/) — Rolling Square

<!-- /problems -->
