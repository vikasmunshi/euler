<!-- tags: [round-off-error] -->
<!-- status: final -->
# Round-off error

[Round-off error](https://en.wikipedia.org/wiki/Round-off_error) is the gap between a real number and
the nearest value the machine can store. The background, binary64 layout, ulps and correct rounding, is on
the [floating-point arithmetic](/topics/technique/floating-point-arithmetic) and
[double-precision format](/topics/technique/double-precision-floating-point-format) pages. This page
is about one recurring situation in Project Euler: **an integer question answered through a
floating-point shortcut**. "Is $n$ triangular?", "is $m$ pentagonal?" and "how many lattice points lie
in this row?" all invert a quadratic, and inverting a quadratic means a square root. The three solved
problems below each take that root in floating point. They differ in how close they come to the
point where the error starts to change the answer, and in what they do about it.

## The idea — where the error comes from, and when it decides

A figurate-number test inverts $P(k) = m$ with the quadratic formula: $m$ is triangular iff
$8m + 1$ is a perfect square, and pentagonal iff $(1 + \sqrt{1 + 24m})/6$ is an integer. In exact
arithmetic that is a yes/no question. In binary64 there are **two** places where error enters:

1. **Converting the argument.** An integer converts to a double exactly only up to $2^{53}$. Above
   that, $8m + 1$ may already be a different number before the root is taken.
2. **The root itself.** IEEE 754 requires `sqrt` to be *correctly rounded*. So the root of a true
   perfect square comes out exact. But the root of $k^2 + 1$ is $k + \frac{1}{2k} + \dots$, and once
   $\frac{1}{2k}$ falls below half an ulp of $k$, that root **rounds to exactly $k$**. The test then
   reports a non-square as a square. The first such case is $k = 2^{26}$: `((2**52 + 1) ** 0.5).is_integer()`
   is `True` in Python.

So the float test is exact for arguments below roughly $2^{52}$ and unreliable above. Error
*accumulates* only a little in these formulas, one rounding in the square root and one in the
divide, but a single rounding is enough to flip a boolean. And `is_integer()` turns any perturbation
into a wrong yes or no.

The fix is always the same pattern, **round, then verify in integers**: use the float only to
*guess* $k$, then check $P(k) = m$ (or $k^2 = n$) exactly. Or skip the float entirely with an
[integer square root](/topics/technique/integer-square-root) (`math.isqrt` in Python).

## Three problems, three margins

**42, coded triangle numbers: safe by a wide margin, and the C verifies anyway.** Word values are at
most a few hundred, so $8n + 1$ is tiny and the float test cannot fail. The public Python trusts it:

```python
result: bool = ((8 * n + 1) ** 0.5).is_integer()
```

The C does the robust version: `round(sqrt(...))`, then `sq_int * sq_int == 8 * n + 1` in 64-bit
integers. At this size both are correct. The C version also stays correct for any `n` an `int` can hold.

**44, pentagon numbers: safe, but less obviously.** The search ends near the 2,200th pentagonal
number, so the arguments to `sqrt` stay below $10^9$, far below $2^{52}$. The Python test
`((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()` has *two* roundings, the root and the division by 6,
and both are harmless at this scale. A non-integer quotient $k + r/6$ is at least $1/6$ away from an
integer, which is enormous compared with an ulp. The C again rounds and then checks
`nth_pentagonal(ni) == m` exactly. If you widened the search to pentagonal numbers near $10^{15}$, only
the C would still be correct.

**210, obtuse angled triangles: the margin is gone, so the code corrects.** Counting lattice points
inside a circle row by row needs $\lfloor\sqrt{2r^2 - a^2 - 1}\rfloor$ for every row, and with
$r = 10^9$ the argument is near $2 \times 10^{18}$. That is far past $2^{53}$, so even converting it to a
double loses the low bits. A float floor-root here is routinely off by one, and an off-by-one in every row of a
$\sim 3.5 \times 10^8$-row sum would make the answer wrong. The solution uses floating point for speed
and **repairs** every result:

```python
s = np.floor(np.sqrt(d.astype(np.float64))).astype(np.int64)
while (mask := s * s > d).any():
    s[mask] -= 1
while (mask := (s + 1) * (s + 1) <= d).any():
    s[mask] += 1
```

The float gives a guess within one or two of the truth. The integer loops enforce the definition
$s^2 \le d < (s + 1)^2$ exactly. The products stay below $2^{63}$, so the `int64` check is
itself exact.

## Python and C

- **42 and 44**: the clearest difference between the languages on this page. The Python solutions
  trust `is_integer()` on a float, correct only because the inputs are small. The C solutions round and
  verify in `long long`, correct up to the integer width. Neither is wrong today, but only one would
  survive larger inputs.
- **210**: both repair a float seed, at different widths. Python vectorises with
  [NumPy](/topics/technique/numpy): a float64 `sqrt` over a chunk of rows, then masked `±1` fix-ups
  applied to the whole array until no element violates the bound. C calls `sqrtl` on an x87
  `long double`, with a 64-bit mantissa that represents $2 \times 10^{18}$ exactly, so the seed is
  usually already exact. It still corrects with the same two `while` loops, because "usually" is not a
  proof. Python's scalar `math.isqrt` covers the one root outside the loop, which needs no repair.

## How to reason about it

- **Know your margin.** Below $2^{52}$, a correctly rounded `sqrt` decides perfect squares correctly.
  Above it, assume it does not. Estimate the largest argument before you trust a float test.
- **Use floats to guess and integers to decide.** `k = round(f(m))`, then check `P(k) == m` exactly.
  It costs one multiplication and removes the whole question.
- **Correct floors in both directions.** A float floor-root can be one too high or one too low, so
  check $s^2 \le d$ *and* $(s+1)^2 > d$.
- **Prefer exact tools when they are cheap.** `math.isqrt` in Python, or an integer Newton
  iteration in C, avoids the issue altogether. Floats are only worth it when, as in 210, they are
  the fast path through a vectorised loop.
- **Watch the conversion as well as the operation.** `float(x)` for $x > 2^{53}$ is already rounded,
  so no later step can recover the lost bits.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles

<!-- /problems -->
