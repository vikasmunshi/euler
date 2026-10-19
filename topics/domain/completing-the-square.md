<!-- tags: [completing-the-square] -->
<!-- status: final 2026-10-19T06:40Z -->
# Completing the square

[Completing the square](https://en.wikipedia.org/wiki/Completing_the_square) rewrites
$ax^2 + bx + c$ as $a(x + \tfrac{b}{2a})^2 + (c - \tfrac{b^2}{4a})$. It removes the linear term,
so a quadratic in shifted variables becomes a sum or difference of squares. In school it is the
derivation of the quadratic formula. In Project Euler it is the step that turns a messy integer
condition into a *standard form* with known solution methods: a Pell equation, a circle, or a
discriminant. All three solved problems below hinge on it, and in all three the work is in
keeping everything integral.

## The idea — complete the square without leaving the integers

With integer unknowns, the fractions $b/2a$ are a problem. The fix is to **multiply through by
$4a$ first**:

$$4a(ax^2 + bx + c) = (2ax + b)^2 - (b^2 - 4ac).$$

Every term is now an integer, and the new variable $X = 2ax + b$ is an integer whenever $x$ is. Two
consequences follow, and both matter in practice:

- **The substitution narrows to a residue class.** $X$ is not an arbitrary integer: $X \equiv b \pmod{2a}$. A solution of
  the transformed equation corresponds to an original solution only if it lies in that class, so
  every solution of the standard form has to be filtered by it.
- **The constant term reappears as the discriminant.** $b^2 - 4ac$ ends up on the right-hand side.
  With two variables, completing the square in each one leaves an equation of the form $X^2 - DY^2 = N$
  or $X^2 + Y^2 < R$. Those are standard forms.

## Three standard forms across the problems

**100, arranged probability: a Pell equation.** Two blues drawn with probability exactly $\tfrac12$
means $2b(b-1) = n(n-1)$. Multiply by 4 and complete both squares:
$2(2b-1)^2 - 2 = (2n-1)^2 - 1$, which is

$$(2n-1)^2 - 2(2b-1)^2 = -1,$$

the negative [Pell equation](/topics/technique/pells-equation) $x^2 - 2y^2 = -1$. Its solutions
come from a linear recurrence, $(x, y) \to (3x + 4y, 2x + 3y)$, and about 40 steps pass
$10^{12}$. The residue condition here is that $x$ and $y$ are odd, and the recurrence preserves
that, so $n = (x+1)/2$ and $b = (y+1)/2$ are always integers. The public solution is one loop:

```python
x, y = (1, 1)
while True:
    x, y = (3 * x + 4 * y, 2 * x + 3 * y)
    n = (x + 1) // 2
    b = (y + 1) // 2
    if n >= total_discs:
        return str(b)
```

**138, special isosceles triangles: Pell again, with a real residue filter.** Half the base $k$,
height $2k \pm 1$ and leg $L$ give $L^2 = 5k^2 \pm 4k + 1$. Multiplying by 5 completes the square
in $k$: $5L^2 = (5k \pm 2)^2 + 1$, so $x^2 - 5L^2 = -1$ with $x = 5k \pm 2$. This time the residue
class does real work. A Pell solution yields a triangle only if $x \mp 2 \equiv 0 \pmod 5$ and the
resulting $k$ is positive. The solution steps along the $-1$ branch with
$(x, y) \to (9x + 20y, 4x + 9y)$ and tests both signs at each step. See
[Pell's equation in disguise](/topics/number-theory/pells-equation-in-disguise) for the family.

**210, obtuse angled triangles: a circle on the integer lattice.** The angle at $B$ is obtuse
exactly when $B$ is strictly inside the circle with diameter $OC$
([Thales](/topics/domain/thaless-theorem)): $x^2 + y^2 < \tfrac r4 (x + y)$. Multiply by 64
and complete both squares:

$$(8x - r)^2 + (8y - r)^2 < 2r^2.$$

The fraction is gone, and the region is now a centred disk in the variables $a = 8x - r$,
$b = 8y - r$. These are not arbitrary lattice points. Both lie in the class $\equiv -r \pmod 8$. So the
count is a [Gauss circle](/topics/domain/gauss-circle-problem) sum, row by row with an
[integer square root](/topics/technique/integer-square-root), where each row counts only the $b$
in one residue class mod 8, using floor-division arithmetic. The other two obtuse cases are
half-planes with closed-form counts.

## Python and C

- **100** is identical in both. The values stay below $2^{63}$, and C needs two temporaries where
  Python uses one tuple assignment.
- **138** is where the languages diverge. The recurrence grows by a factor of about $17.9$ per step, so large
  test inputs reach more than 120 digits. Python's `int` handles that without any extra code. C carries a small
  purpose-built `BigInt` (base-$10^9$ limbs) with only the operations the loop needs: add,
  multiply by a small scalar, divide by 5, residue mod 5, and add a small signed integer.
- **210** loops over about $3.5 \times 10^8$ rows. C runs a plain `long long` loop with an
  `sqrtl`-seeded `isqrt` and a hand-written `floordiv`, because C's `/` truncates toward zero and
  the residue counts use negative bounds. Python cannot afford that loop, so it vectorises the rows in
  NumPy chunks. `np.sqrt` in `float64` is wrong past $2^{53}$, so each chunk's roots are corrected
  to the exact floor with masked `±1` fix-ups. Python's `//` already floors.

## How to reason about it

- **When a quadratic Diophantine condition looks ad hoc, complete the square.** Try $4a$ times the
  equation. A difference of squares with a non-square coefficient points to Pell, and a sum of
  squares points to a lattice count in a circle.
- **Carry the residue class forward.** The transformed variable lives in $X \equiv b \pmod{2a}$, so
  solutions of the standard form must be filtered (138) or shown to stay in the class (100's odd $x, y$).
- **Clear denominators before counting lattice points.** Multiply by the square of the denominator
  so the region's boundary is an integer inequality, as with $(8x - r)^2 + (8y - r)^2 < 2r^2$, and test
  points exactly with integer arithmetic.
- **Watch the width after scaling.** Multiplying by 64 makes $2r^2 = 2 \times 10^{18}$ for
  $r = 10^9$, which still fits in `int64` but has little room left. A larger $r$ would need `__int128`.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles

<!-- /problems -->
