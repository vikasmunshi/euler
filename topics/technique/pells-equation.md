<!-- tags: [pells-equation] -->
<!-- status: final -->
# Pell's equation

[Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation) is $x^2 - D y^2 = 1$ for a
non-square integer $D$. It has infinitely many integer solutions, and they are anything but
scattered: every one is a power of a single **fundamental** solution, so they follow a fixed
linear recurrence and grow geometrically. That is why it keeps turning up. Problems about
triangles with integral area, probabilities of exactly one half, special isosceles triangles,
golden nuggets of a generating function, square tilings and counter swaps all reduce, after
completing a square, to "this quadratic quantity must be a perfect square". That condition is a
Pell or Pell-like equation. Once you see it, a search over $10^{12}$ candidates becomes a walk
over a few dozen solutions.

## The idea: one unit generates everything

Write a solution as the number $x + y\sqrt D$. The product of two such numbers whose
*norm* $x^2 - D y^2$ is $N_1$ and $N_2$ has norm $N_1 N_2$. That's the
[Brahmagupta identity](https://en.wikipedia.org/wiki/Brahmagupta%E2%80%93Fibonacci_identity). So
if $x_1 + y_1\sqrt D$ is the smallest solution with norm $1$, multiplying any solution by it keeps
the norm and moves to the next solution:

$$(x, y) \;\mapsto\; (x_1 x + D y_1 y,\; y_1 x + x_1 y).$$

Every positive solution of $x^2 - D y^2 = 1$ is $(x_1 + y_1\sqrt D)^k$. Each step multiplies the
size by about $x_1 + y_1\sqrt D$, so only $O(\log N)$ solutions lie below any bound $N$. That
makes this a [linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients)
with a large growth rate, and enumerating by recurrence beats searching every time.

**Finding the fundamental solution.** For a small $D$ you can find it by trying $y = 1, 2, \dots$.
In general it can be astronomically large: for $D \le 1000$, Problem 66 meets an $x$ above
$10^{17}$. The classical theorem is that the fundamental solution is a
[convergent](/topics/domain/convergent-continued-fraction) of the
[continued fraction](/topics/domain/continued-fraction) of $\sqrt D$. That expansion is
[periodic](/topics/domain/periodic-continued-fraction), and the right convergent comes at the end
of the first period if the period is even, or of the second if it is odd. Walking the convergents
until one satisfies the equation sidesteps the parity bookkeeping, and it stays in integers
throughout:

```python
def pell_fundamental(D):                       # least x, y > 0 with x^2 - D*y^2 = 1; D not a square
    a0 = isqrt(D)
    m, d, a = 0, 1, a0
    p0, p1, q0, q1 = 1, a0, 0, 1               # consecutive convergents p/q of sqrt(D)
    while p1 * p1 - D * q1 * q1 != 1:
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d
        p0, p1 = p1, a * p1 + p0
        q0, q1 = q1, a * q1 + q0
    return p1, q1
```

Problem 66's published solution does the same with an explicit period-parity rule.

## Three variants the problems use

**The negative equation, $x^2 - D y^2 = -1$.** It is solvable exactly when the period of
$\sqrt D$'s continued fraction is odd. Its solutions are the odd powers of the smallest one.
[Problem 100](/solutions/0100/) is the cleanest example. Requiring a probability of exactly
$\tfrac12$ becomes $x^2 - 2y^2 = -1$ in $x = 2n - 1$, $y = 2b - 1$, and multiplying by the norm-$1$
unit $3 + 2\sqrt2$ steps from one $-1$ solution to the next:

```python
x, y = (1, 1)
while True:
    x, y = (3 * x + 4 * y, 2 * x + 3 * y)
    n = (x + 1) // 2
    b = (y + 1) // 2
    if n >= total_discs:
        return str(b)
```

Problem 138 does the same for $D = 5$. It deliberately multiplies by the *square* of the
fundamental unit $2 + \sqrt5$, so it lands only on $-1$ solutions and skips the $+1$ ones it has
no use for. Problem 139 goes the other way: its unit $1 + \sqrt2$ has norm $-1$, so its recurrence
alternates between $+1$ and $-1$, and the tiling condition accepts both.

**The generalised equation, $x^2 - D y^2 = N$.** For $|N| > 1$ the solutions split into a
*finite* number of classes. Each class is the orbit of one small seed under the norm-$1$ unit.
[Nagell's bounds](https://en.wikipedia.org/wiki/Pell%27s_equation)
limit how large the seeds can be, so a short scan finds them all. Problem 140 reduces its
golden-nugget condition to $u^2 - 5m^2 = 44$, scans a conservative range for seeds, and walks each
orbit. Problem 321 gets $v^2 - 8u^2 = -7$, which has two families. They interleave in size, so it
collects both and sorts, which is simpler than merging the two streams by hand.
[Problem 94](/solutions/0094/) interleaves its two triangle families inside a single recurrence
with a sign alternator.

**Pell inside a bigger structure.** Problem 224 counts triangles with $a^2 + b^2 + 1 = c^2$ by
walking a ternary tree of linear maps from one root. The tree's self-symmetric spine, where
$a = b$, consists exactly of the solutions of the Pell equation $2a^2 + 1 = c^2$. Problem 137
starts from a generating function: requiring its value to be an integer forces a discriminant to
be a square, and the result is a $D = 5$ Pell equation whose solutions are expressed through
[Fibonacci](/topics/domain/fibonacci-sequence) numbers.

## How to reason about it

- **Suspect Pell when a quadratic must be a perfect square.** Integral area from Heron's formula,
  a rational root from the quadratic formula, an exact probability: complete the square in both
  variables, and you get $X^2 - D Y^2 = N$ with small $D$ and $N$.
- **Track the substitution back.** The Pell variables are usually affine images of the problem's
  variables, such as $x = 2n - 1$ or $u = 5k + 7$. A solution only counts if it maps back to
  integers in range: odd $x$, $5 \mid u - 7$, positivity, the strict triangle inequality.
  Some seeds produce a degenerate member, like $n = 0$ in Problem 321, that the problem excludes.
  Filter on the original variables, and keep the guards even when theory says they always pass.
- **Know which unit you're multiplying by.** Norm $+1$ keeps the sign of $N$, and norm $-1$ flips
  it. Squaring a norm-$-1$ unit gives a norm-$+1$ step that stays within one family.
- **Find every class for $N \ne \pm1$.** Missing a seed silently drops a whole family of answers.
  Bound the seed search, or scan generously and confirm that the merged sequence matches the
  statement's first few terms, as 321 does with the start of its given sequence.
- **Budget for the size.** Solutions grow geometrically, so a few dozen steps can reach $10^{18}$
  or far beyond. Python's integers absorb that. In C, check the width at the largest step, and
  for fundamental solutions as large as Problem 66's, carry a big-integer type.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0321](/solutions/0321/) — Swapping Counters

<!-- /problems -->
