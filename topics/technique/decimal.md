<!-- tags: [decimal] -->
<!-- status: final -->
# decimal

Python's [`decimal`](https://docs.python.org/3/library/decimal.html) module is
arbitrary-precision **decimal floating point**. You choose how many significant digits to carry,
arithmetic is correctly rounded to that precision, and the exponent range is effectively unlimited.
It is the tool to use when a `float` (53 bits, about 16 digits, exponent below about 308) is too
narrow, but the problem is still a floating-point problem: a root to find, a constant to compute,
a self-referential number to iterate. The three solved problems below use it in those three roles.
Their C ports, or the absence of one, show what you give up without it.

## The idea — precision you set, rounding you control

The parts of the module these solutions rely on:

- **A context sets the precision.** `getcontext().prec = 80` means every operation's *result* is
  rounded to 80 significant digits. The inputs are exact: `Decimal('0.1')` is exactly one tenth, and
  `Decimal(2)` is exactly two. Build Decimals from `int` or `str`, never from a `float`, or you import
  the float's binary error.
- **The exponent range is enormous.** The default context allows exponents up to 999999, and
  that can be raised to about $10^{18}$, so `r ** 5000` or even `2 ** 1_000_000` is an ordinary
  Decimal, not an overflow.
- **Rounding is explicit.** `x.quantize(Decimal(1).scaleb(-12), rounding=ROUND_HALF_UP)` rounds to
  12 places by the stated rule. That matters when a problem says "rounded to 12 decimal places" and
  the answer is a string.
- **Conversion to `int` truncates toward zero**, so `int(b)` is the floor only for $b \ge 0$.
- **The context is per thread and mutable.** Setting `prec` at import time changes it for every later
  Decimal operation in the process. Setting it inside `solve()`, or using `localcontext()`, keeps the
  change scoped.

It is slower than `float` (CPython uses the C library libmpdec, but each operation still allocates), so
you pay for precision only where precision is needed.

## Three roles across the problems

**235, an arithmetic geometric sequence: a float with more range and digits.** The task is a
bisection for the ratio $r$ at which a 5000-term arithmetico-geometric sum hits $-6 \times 10^{11}$,
to 12 decimals. The closed form involves $r^{5000}$, and the bracket search doubles $r$ until the sign
flips, which can push $r^n$ far past the float range. At 80 digits, Decimal makes both concerns
disappear: no overflow, and plenty of guard digits. `quantize` with `ROUND_HALF_UP` produces the
12-place string. The sensitivity analysis in the notes shows that about 19 digits would suffice, so
this is precision as insurance, not necessity. See [geometric progression](/topics/domain/geometric-progression).

**686, powers of two: compute constants exactly, then leave Decimal.** Which powers $2^j$ start with
"123" depends on the fractional part of $j \log_{10} 2$, and the solution counts hits with a
[floor-sum](/topics/technique/floor-sum-algorithm) recursion on integers. It needs $\log_{10} 2$,
$\log_{10} L$ and $\log_{10}(L+1)$ to about 100 digits, scaled to integers by $Q = 10^{100}$.
Solution 0 computes them in Decimal at 300 digits from the series
$\ln\frac{q+p}{q-p} = 2\,\mathrm{artanh}(p/q)$, expanded around the nearest power of two so the series
converges fast. Then `int(x * Q)` turns each into an integer, and all later work is exact integer
arithmetic. Solution 1 gets the same constants from [`mpmath`](/topics/technique/mpmath)`.log10` at
150 digits, which is shorter and faster. Here Decimal is a *constant generator*, used once.

**751, concatenation coincidence: digits that are the data.** $\theta$ is defined by its own decimal
expansion: the integer parts $a_n$ of a recurrence started at $\theta$, written one after another after
"2.", must reproduce $\theta$. [Fixed-point iteration](/topics/domain/contraction-mapping) converges
from $\theta = 2$. Each step of $b_n = \lfloor b_{n-1} \rfloor (b_{n-1} - \lfloor b_{n-1} \rfloor + 1)$
multiplies the fractional part by a growing integer and loses about one digit per term, so the
solution works at 160 digits to deliver 24. Decimal suits this problem in a second way: the next
iterate is built *from a string*, `Decimal('2.' + frac_digits)`, because the answer is defined in
base-10 digits. Binary floating point would misrepresent it at every step.

## Python and C

| | Python | C |
|---|---|---|
| 235 | `Decimal` at 80 digits, `quantize(ROUND_HALF_UP)` | `long double` (64-bit mantissa, about 19 digits). `powl` overflow gives a signed `inf`, which keeps the bisection's sign test valid |
| 686 | `Decimal` artanh series at 300 digits → `int` scaled by $10^{100}$ | the same series in **`__int128` fixed point** scaled by $10^{25}$, working in natural-log space so the floor-sum denominator is $\ln 10 \cdot W$ and the intermediates stay below $2^{127}$ |
| 751 | `Decimal` at 160 digits | **no port.** About 19 digits cannot survive the digit erosion, so a C version would need MPFR, or GMP plus decimal conversion each pass |

Read down the C column for the general lesson. A modest precision need can be met with
`long double`. A known, bounded precision with integer-friendly use can be met with
[`__int128`](/topics/technique/int128) fixed point. A deep precision need, especially in base 10,
requires an arbitrary-precision library.

## How to reason about it

- **Reach for Decimal when a float is too small or too binary.** That means more than 16 digits, exponents beyond
  $10^{308}$, or answers defined by decimal digits.
- **Budget the precision.** Estimate the digits lost to cancellation or amplification (751 loses one
  digit per term) and set `prec` to the target plus that loss plus guard digits.
- **Construct from `int` or `str`.** `Decimal(0.1)` is not one tenth.
- **Round once, at the end, with the rule the problem states.** Use `quantize` with an explicit
  rounding mode, and return the string.
- **Use Decimal for constants, integers for the work.** If high precision is needed only for a few
  constants, compute them once, scale them to integers (686), and keep the hot loop exact and fast.
- **Scope the context.** Set `prec` inside `solve()` or under `localcontext()` so one solution's
  setting does not leak into others.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0751](/solutions/0751/) — Concatenation Coincidence

<!-- /problems -->
