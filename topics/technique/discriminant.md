<!-- tags: [discriminant] -->
<!-- status: final -->
# Discriminant

The [discriminant](https://en.wikipedia.org/wiki/Discriminant) of $ax^2 + bx + c$ is
$\Delta = b^2 - 4ac$, the quantity under the square root in the
[quadratic formula](/topics/technique/quadratic-formula). In school it tells you *how many* real
roots there are. In number theory it tells you something sharper: **a quadratic with integer
coefficients has rational roots exactly when $\Delta$ is a perfect square.** That turns questions of
the form "for which integers does this equation have an integer (or rational) solution?" into "when
is this expression a square?", and that second question has well-developed tools: residues, Pell
equations and factorisations. Each of the three solved problems below makes exactly that move, and
then needs a different tool to finish.

## The idea — "has a rational root" becomes "is a square"

For $ax^2 + bx + c = 0$ with integer coefficients,

$$x = \frac{-b \pm \sqrt{\Delta}}{2a}, \qquad \Delta = b^2 - 4ac.$$

The root is rational iff $\sqrt{\Delta}$ is rational, which for an integer $\Delta$ means
$\Delta = s^2$. For an *integer* root you also need $2a \mid (-b \pm s)$, a congruence on $s$. So the
recipe is:

1. Write the condition as a quadratic in the unknown you want to be integral or rational.
2. Its discriminant, a polynomial in the remaining parameters, must equal $s^2$.
3. Solve "polynomial $= s^2$". When the polynomial is quadratic in a parameter, completing the square
   gives either a [Pell-type equation](/topics/technique/pells-equation) $u^2 - Dv^2 = N$ or a
   [difference of two squares](/topics/domain/difference-of-two-squares), and both can be
   parametrised.
4. Apply the divisibility condition from the $2a$ in the denominator.

## Three problems, three ways to finish

**45, triangular, pentagonal and hexagonal: a square test plus a residue.** A number $T$ is
pentagonal iff $3k^2 - k - 2T = 0$ has a positive integer root. The discriminant is $1 + 24T$, so
$1 + 24T$ must be a square $s^2$, and for $k = (1 + s)/6$ to be an integer, $s \equiv 5 \pmod 6$.
Hexagonal works the same way with $1 + 8T$ and $s \equiv 3 \pmod 4$. The public solution walks the
triangular numbers and applies both tests in one line each:

```python
if (1 + 24 * triangular_number) ** 0.5 % 6 == 5.0:
    if (1 + 8 * triangular_number) ** 0.5 % 4 == 3.0:
```

For a triangular $T = n(n+1)/2$ the second discriminant is always $(2n+1)^2$, so the hexagonal test
reduces to "$n$ is odd". The discriminant view makes such shortcuts visible. (The float `sqrt` is safe
here only because the arguments stay near $10^{10}$. See
[round-off error](/topics/technique/round-off-error) for the margin.)

**140, golden nuggets: discriminant to a Pell equation.** The generating function of a
Fibonacci-like sequence, $A(x) = k$, is a quadratic in $x$ once you clear the denominator. A
"nugget" is an integer $k$ for which $x$ is rational, so the discriminant, a quadratic in $k$, must
be a perfect square. Completing the square in $k$ with the substitution $u = 5k + c$ turns
"$\Delta(k) = m^2$" into a generalised Pell equation $u^2 - 5m^2 = N$. Its solutions come in
finitely many families. Each family is found by a small search and then generated without limit by
the automorphism of $x^2 - 5y^2 = 1$. The nuggets are the family members with $u$ in the right
residue class mod 5 and a positive root $x$. So the discriminant replaces a search over $k$ with a
recurrence. Problem 137 has the same structure with the plain Fibonacci sequence.

**757, stealthy numbers: discriminant to a difference of squares.** $N$ is stealthy if
$N = ab = cd$ with $a + b = c + d + 1$. Treat $a, b$ as the roots of $t^2 - (c + d + 1)t + N = 0$. They are
integers exactly when the discriminant $(c + d + 1)^2 - 4cd$ is a square. With $m = d - c$ it simplifies to
$(m + 1)^2 + 4c = p^2$, that is, $(p - m - 1)(p + m + 1) = 4c$, a difference of two squares. Both factors
must be even, so writing them as $2g$ and $2h$ gives $c = gh$ and $m = h - g - 1$. Every stealthy number
is then $gh\,(gh + h - g - 1)$, and the solution enumerates pairs $g < h$ instead of factorisations. The
discriminant turns a search over divisors into a two-parameter family.

## Python and C

- **45**: the same float test in both: `** 0.5 % 6 == 5.0` in Python, `fmod(sqrt(...), 6.0) != 5.0`
  in C. A non-square gives a non-integer root, so the comparison fails, and at $10^{10}$ the float
  root of a true square is exact. Neither version verifies in integers, so neither is safe for inputs
  much larger than this.
- **140**: Python grows each Pell family with unbounded integers (stopping at $10^{100}$) and checks
  every candidate again with `math.isqrt`. C uses `__int128`, bounds $|u|$ at $10^{30}$ so that the next
  `9u + 20m` cannot overflow, skips the re-check because $\sqrt{\Delta} = |m|$ by construction, and
  formats the sum itself, since `printf` has no 128-bit conversion.
- **757**: Python vectorises over $h$ for each $g$ with NumPy (`n = g*h * (g*h + h - g - 1)` as an
  `int64` array) and removes duplicates with a `set`. C appends every value to a growing array and
  removes duplicates by `qsort` + adjacent compare. With tens of millions of values, a flat array of
  8-byte integers is far smaller than a hash set of Python `int` objects.

## How to reason about it

- **"Integer or rational solution" plus "quadratic" means look at the discriminant.** It is the first
  thing to write down.
- **Square, then congruence.** Rationality needs $\Delta = s^2$, and integrality adds a residue
  condition on $s$ from the $2a$. Check both, as in 45.
- **Complete the square on the discriminant.** If $\Delta$ is quadratic in a parameter, completing the
  square gives $u^2 - Dv^2 = N$: Pell (140) if $D > 0$ is not a square, a difference of squares
  that factors (757) if $D$ is a square.
- **Parametrise, don't search.** Both reductions give a generator for all solutions: a Pell recurrence
  or a $(g, h)$ grid. The work becomes proportional to the number of answers, not to the search space.
- **Duplicate solutions are possible.** Different families (140) or different $(g, h)$ pairs (757) can
  give the same value, so both solutions deduplicate.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0757](/solutions/0757/) — Stealthy Numbers

<!-- /problems -->
