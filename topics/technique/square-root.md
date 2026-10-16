<!-- tags: [square-root] -->
<!-- status: final -->
# Square root

Almost no problem here wants $\sqrt n$ as a number. What they want is a *fact* about it: where a
search can stop, whether a value is a perfect square, which integers lie in a band. The
[square root](https://en.wikipedia.org/wiki/Square_root) is the tool that answers all three, and
whether it answers correctly depends on one choice every solution makes, mostly without noticing:
take the root in floating point, or take it exactly in integers. This page is about that choice: what
each kind of root guarantees, the patterns that make a float root safe, and the inputs where it
stops being safe. The exact function itself is covered on [math.isqrt](/topics/technique/math-isqrt),
the C library call on [sqrt](/topics/technique/sqrt), and the algorithms behind both on
[integer square root](/topics/technique/integer-square-root). None of that is repeated here.

## Three jobs, three tolerances

Across the problems below, a square root does one of three jobs, and each tolerates error differently.

| job | example | what an error costs |
| --- | --- | --- |
| **bound** a search | trial division to $\sqrt n$ (3, 46); divisor pairs $a \le \sqrt n$ (21, 179) | too high: wasted iterations; too low: missed answers |
| **test** for a square | $8n+1$ square ⇔ $n$ triangular (42, 45); integer shortest path (86); $\sigma_2(n)$ square (211) | a wrong answer, with nothing to show it happened |
| **delimit** a band | the roots of the $n$-digit squares (98) | a value from the wrong band slips in, or a real one drops out |

A bound is the forgiving one. It can be loose upward at the price of a few wasted iterations, so long
as the loop body checks the real condition. Problem 757 is built that way: it takes a float
`int(limit ** 0.5) + 2` with deliberate slack, then filters every candidate with exact integer
arithmetic. The `+ 2` is the whole safety argument. Rounding can move the float root by a unit, and
the slack absorbs that, so the root only has to be roughly right. Problem 173 skips the root
altogether. Its loop guard is `4 * t * (t + 1) <= N`, the inequality itself rather than its solved form
$t \le \sqrt{N/4}$, so nothing is ever rounded. Squaring the condition instead of rooting the bound
is the cheapest exact technique there is, and it turns up again on the C side as `g * g <= ...`.

A test is the unforgiving one. A float predicate that answers wrong answers *plausibly*: the loop goes on,
the count comes out one off, and nothing fails.

## What a float root actually guarantees

IEEE 754 requires `sqrt` to be *correctly rounded*: the result is the `double` nearest the true root
(see [double precision](/topics/technique/double-precision-floating-point-format)). Python's
`math.sqrt`, `x ** 0.5` on a float, C's `sqrt` and NumPy's `np.sqrt` all inherit the guarantee. Two
consequences follow, and the reasoning about float roots comes down to them:

- **A perfect square below $2^{53}$ gives back its root exactly.** Both $m^2$ and $m$ are
  representable, and $m$ is the nearest double to itself. That is why `(8 * n + 1) ** 0.5` in
  problem 42 never rejects a genuine triangular number.
- **A non-square can also give back an integer, once the root passes $2^{26}$.** Near $m$, the gap
  between neighbouring doubles is about $m \cdot 2^{-52}$. The true root of $m^2 + 1$ is
  $m + 1/(2m)$, and once $1/(2m)$ drops below half that gap the result rounds to $m$ itself:

  ```python
  >>> n = 2**52 + 1                  # (2**26)**2 + 1, not a square
  >>> math.sqrt(n).is_integer()
  True
  ```

So the bare float predicate, `sqrt(x).is_integer()` or `x ** 0.5 % 1 == 0`, has **false
positives** starting just past $2^{52}$. Above $2^{53}$ it also has false negatives, because the
argument is rounded before the root is even taken. [math.isqrt](/topics/technique/math-isqrt#the-trap-it-replaces)
shows the matching failure for `int(sqrt(n))` as a *floor*. This is the same edge seen from the
predicate side. Problems 42, 45, 46 and 86 all use the bare form in Python. All four are correct,
because their arguments stay in the millions or billions, and each is correct only for that reason.

## Round, then verify in integers

The repair keeps the fast float root and moves the *decision* into integer arithmetic. The C
counterparts here do it almost word for word:

```c
long long r = (long long)round(sqrt((double)x));
return r * r == x;                      /* the integers decide, not the double */
```

The float only has to land *within one half* of the true root, and correct rounding keeps it far
closer than that for any `x` a `long long` can hold. A non-square can no longer pass, because
`r * r == x` is exact. The guard has to compare against the original integer `x`, though. Problem 86's
C converts the `double` back with `(long long)val` and compares against that, which works only
because its `val` is built from small integers and is therefore exact. If `x` were wide enough to
round on the way into the double, the comparison would be checking the rounded value against itself.

When the inputs pass $2^{53}$, the float can be off by a whole unit and the fix-up becomes a window.
Problem 211 computes $\sigma_2(n)$, which reaches well past $2^{53}$, takes `np.sqrt` over the whole
array, and then tries `root - 1`, `root`, `root + 1` with an exact integer square-and-compare. This
is the vectorised form of round-and-verify. NumPy has no exact integer root (see
[math.isqrt](/topics/technique/math-isqrt#how-to-reason-about-it)), so the float does the bulk work
and a three-wide integer check makes the result exact. The C sibling applies the same window to
`sqrtl`.

## Pairing around the root

Problems 21 and 179 count divisors in pairs $(a, n/a)$ with $a \le \sqrt n$. That raises a second,
non-numerical trap at the root itself: when $n = a^2$, the pair is $(a, a)$ and the divisor gets
counted twice. Both solutions subtract it once. Problem 21's Python does it with
`- (n_sqrt if n_sqrt**2 == n else 0)`, and 179's sieve decrements `div_count[a * a]`. The correction
depends on the root being exact. If the root came out as $a - 1$, the loop would miss $a$ and the
subtraction would never fire. If it came out as $a + 1$, the square test would fail for a real
square and the double count would stand. A floor that is off by one at a perfect square breaks the
divisor sum both ways. That is why 179's C works out its bound with an exact integer loop (once,
outside the sieve) instead of trusting `sqrt` at precisely the inputs it is most likely to get wrong.

## Where rounding bites

The failures come from the *input* to the root more often than from the root, so look upstream:

- **Bands built from powers of ten.** Problem 98 delimits the $n$-digit squares with
  `ceil(sqrt(10**(n-1)))` and `floor(sqrt(10**n - 1))`. In Python the `10**n - 1` is an exact
  integer, but `math.sqrt` converts it to a float first, and from $n = 16$ on, $10^n - 1$ rounds up
  to $10^n$. The upper root comes out as $10^{n/2}$, one past the last $n$-digit root, so a
  $(n+1)$-digit square enters the band. Here $n$ is a word length and never gets near 16. The C
  version hits the same edge from a different direction: `pow(10.0, n) - 1` does the subtraction in
  `double`, where the `- 1` is lost at exactly the same $n$. Exact endpoints are `isqrt(10**n - 1)` and `isqrt(10**(n-1) - 1) + 1`.
- **A float division ahead of the root.** Problem 46 tests `((n - p) / 2) ** 0.5`, where the `/`
  has already made a float before the root is taken. It is exact here only because the operands are
  small. `(n - p) // 2`, or a parity check followed by `isqrt`, keeps the argument an integer.
- **`fmod` on a root.** Problem 45 asks `sqrt(1 + 24t) % 6 == 5`, a perfect-square test and a
  residue test in one comparison. It is exact while the root is an exactly represented integer, and
  above $2^{52}$ a non-square that rounds to such an integer passes both halves. Splitting it as
  `r = isqrt(x); r * r == x and r % 6 == 5` costs nothing and has no ceiling.
- **A bound that goes stale.** Problem 3 recomputes `int(remaining ** 0.5)` every time it strips a
  factor. That is right, since the cofactor shrinks and so should the bound, but the recomputation is
  also a float root of a value that started at the size of the input. With a 64-bit input, the
  first few bounds sit exactly in the range where the floor can be off by one.

## How to reason about it

- **Name the job before writing the root.** A bound can use slack plus an exact filter, or no root at
  all (`while d * d <= n`). A test needs an exact decision. A band needs exact endpoints on both
  sides.
- **Treat $2^{52}$ as the threshold, not $2^{53}$.** Float floors and float predicates are both
  trustworthy only below about $4.5 \times 10^{15}$. Under that, a bare float root is fine as long
  as the bound on the input is a real constraint of the problem and not just the size of today's
  test case.
- **If you keep the float, make the integers decide.** Round, then square and compare against the
  original integer, widening to a $\pm 1$ window past $2^{53}$. In scalar Python there is seldom a
  reason to bother, because `math.isqrt` is exact and faster. The pattern matters for NumPy arrays
  and for C, which have no integer root built in.
- **Check the argument as well as the root.** A `/`, a `pow(10.0, n)` or an implicit `int → float`
  conversion upstream of the root loses precision before `sqrt` ever runs, and no care taken over
  the root itself can get it back. See [rounding](/topics/technique/rounding) and
  [floating-point arithmetic](/topics/technique/floating-point-arithmetic) for the general rules.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0757](/solutions/0757/) — Stealthy Numbers

<!-- /problems -->
