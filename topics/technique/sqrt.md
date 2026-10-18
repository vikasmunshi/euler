<!-- tags: [sqrt] -->
<!-- status: final -->
# sqrt

C has no integer square root. When a C solution needs $\lfloor\sqrt n\rfloor$, a loop bound, or a
yes/no on squareness, it reaches for [`sqrt`](https://en.cppreference.com/w/c/numeric/math/sqrt)
from `<math.h>`. That function takes a `double` and returns a `double`, and all the work is in
converting the answer back into an integer you can trust. The five problems below are where this
repository's C files do that, and in each one the Python sibling uses something else: `math.isqrt`,
a pure-integer Newton loop, or a bare `math.sqrt` that gets away with it. This page covers the C
call: what it promises, what the cast back to an integer loses, and the correction loop that makes
the result exact. The general question of float roots versus exact roots is on
[square root](/topics/technique/square-root), the Python function on
[math.isqrt](/topics/technique/math-isqrt), and the algorithms on
[integer square root](/topics/technique/integer-square-root).

## What the call promises

`sqrt` is one of the operations IEEE 754 requires to be *correctly rounded*: the result is the
`double` nearest the true root. Every mainstream libm meets that, and on x86-64 the call compiles
to the single `sqrtsd` instruction. So the error is never more than half an ulp. What remains
inexact comes from two places outside the root:

- **The argument.** `(double)n` rounds a `long long` to 53 bits. Below $2^{53}$ that conversion is
  exact; above it the root is taken of a different number.
- **The way back.** `(long long)x` *truncates* toward zero, and the true root of a non-square is
  irrational, so the `double` lies on one side of it or the other.

Put those together and you get the useful facts. For $n < 2^{53}$, `(long long)sqrt((double)n)` is
**never too small**. If $n \ge m^2$, then $m$ is itself a double no larger than $\sqrt n$, and
correct rounding cannot return anything below it. It **can be one too large**: once $m$ passes
about $2^{26}$, $\sqrt{m^2 - 1}$ lies within half an ulp of $m$ and rounds up to it. Past $2^{53}$
both directions are possible, because the argument itself moved.

The [`sqrtl`](https://en.cppreference.com/w/c/numeric/math/sqrt) variant computes in `long double`.
On x86 Linux that has a 64-bit mantissa, which covers every `long long`. On MSVC and on AArch64
macOS it is just `double`. Neither the C standard nor the portability story lets you treat it as
exact.

## The correction step

Since the float result is at most one away, a couple of integer comparisons recover the exact
floor. The repository writes it in three shapes, depending on what the caller needs.

**One-sided, for bounds.** Problem 420 needs the largest $a$ with $a^2 < T$ and the largest $G$
with $G^2 \cdot (a^2 + b^2) < T$. Its C takes the float root and only walks *down*:

```c
int a_max = (int)sqrt((double)T);
while ((long long)a_max * a_max >= T) a_max--;   /* ensure a_max^2 < T */
```

That relies on the "never too small" fact, so the loop is enough while $T < 2^{53}$, and the loop
condition encodes the *strict* inequality the problem needs. The Python sibling writes `isqrt(T)`
and `isqrt((T - 1) // ab2)` instead, which is the same bound spelled with the off-by-one folded into
the argument (see the bounds table on [math.isqrt](/topics/technique/math-isqrt#the-algebra-of-bounds)).

**Two-sided, for an exact floor.** Problem 719 enumerates roots $k \le \sqrt N$ with $N$ up to
$10^{12}$ and beyond, and its C defines its own `isqrt_ll`:

```c
long long r = (long long)sqrtl((long double)n);
while (r * r > n) r--;
while ((r + 1) * (r + 1) <= n) r++;
```

Both loops are there because the function makes no assumption about the input range or about how
wide `long double` is. Each loop runs zero or one time in practice, so the cost is the root plus
two multiplies. This is the portable C equivalent of `math.isqrt`, which is exactly what the Python
side calls. One caveat: `(r + 1) * (r + 1)` overflows when `r` is near $\sqrt{2^{63}}$, so a fully
general version compares `r + 1 <= n / (r + 1)` instead.

**Round and test a window, for a predicate.** Problems 44 and 80 want to know whether a value is a
perfect square (44 asks whether $1 + 24m$ is the square of something $\equiv 5 \pmod 6$). Here
truncation is the wrong rounding: a truncated $4.9999\ldots$ becomes 4. So the C rounds to nearest
and lets the integers decide:

```c
int s = (int)(sqrt((double)n) + 0.5);            /* problem 80 */
for (int k = s - 1; k <= s + 1; k++)
    if (k > 0 && k * k == n) return 1;
```

Problem 44 does the same through `round()`: it inverts the pentagonal formula in `double`, rounds
the candidate index, and accepts it only if `nth_pentagonal(ni) == m` holds in `long long`. The
float picks a candidate and the integer arithmetic confirms it. Without that confirmation a
non-pentagonal $m$ whose root rounds onto an integer would pass.

## Where the Python side differs

The Python versions of 44 and 80 test squareness with the bare float predicate:
`((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()` and `i**0.5 % 1 == 0`. Both are correct for the
inputs these problems use, and both would admit false positives once the argument passes $2^{52}$,
the failure [square root](/topics/technique/square-root#what-a-float-root-actually-guarantees)
works through. In this pair the C files are the stricter ones, because a C author knows there is no
`isqrt` to fall back on and checks with integers out of habit. Where the Python reaches for
`math.isqrt` (420, 719), the two sides agree, and the C correction loop is just how `isqrt` is
spelled in C.

## A float as a seed, not an answer

Problem 80 wants the first hundred decimal digits of $\sqrt n$, which is
$\lfloor\sqrt{n \cdot 10^{200}}\rfloor$ computed in big integers. The Python starts
[Newton's method](/topics/technique/newtons-method) from $x_0 = n \cdot 10^{200}$ and lets it
converge. Quadratic convergence only starts near the root, so most of the iterations go on halving
the oversized guess. The C hand-rolls its own bignum arithmetic and can't afford that, so it seeds
the iteration from `sqrt((double)n) * 1e15 + 100`, scaled up by $10^{d-15}$. That gives about fifteen
correct digits immediately, and Newton doubles them on each step after that. The `+ 100` matters.
From a start *above* the root, the integer Heron step $x \leftarrow \lfloor (x + N/x)/2 \rfloor$
decreases monotonically to the floor, so the stopping rule "stop when the next iterate is not
smaller" is valid. A start that rounded below the root would break that rule. The margin is far
larger than the half-ulp error of `sqrt`, so the seed is above the root whatever the rounding does.

## A float only where a float is the answer

Problem 816 asks for the shortest distance among a few million points as a decimal, so a `double`
*is* the output, and both languages call `sqrt`. What the solutions get right is *where* they call
it. Every comparison runs on squared integer distances, and `sqrt` is used only for the grid cell
size and the final formatted value. The cell size is the one place a rounding error could matter:
a cell a hair too small could leave a closer pair two cells apart. It does not, because a pair
exactly at the current distance cannot improve the strict `dd < cur_sq` test, and anything closer
is well inside one cell. Keeping comparisons on squares is the same move as writing `d * d <= n`
instead of `d <= sqrt(n)`. Leave the root out of every decision and use it only to format the result.

## How to reason about it

- **Below $2^{53}$, `(long long)sqrt(x)` is at most one too large, never too small.** A single
  downward `while` is enough for a bound. Add the upward loop when the input range is open-ended or
  you used `sqrtl`.
- **Truncate for floors, round for predicates.** Then let `r * r == n` (or a $\pm 1$ window)
  decide. Never compare a `double` root to an integer directly.
- **Squaring is free and exact.** If a loop needs `d <= sqrt(n)`, write `d * d <= n` and the root
  disappears. Watch for overflow in `d * d` near the top of the type.
- **`sqrtl` is not a portability fix.** Its width depends on the platform, so the correction loops
  are still needed.
- **In Python, use `math.isqrt`.** The correction pattern matters for C and for NumPy arrays, which
  have no exact integer root of their own.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0816](/solutions/0816/) — Shortest Distance Among Points

<!-- /problems -->
