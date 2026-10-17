<!-- tags: [double-precision-floating-point-format] -->
<!-- status: final 2026-10-17T07:18Z -->
# Double-precision floating-point format

The [floating-point arithmetic](/topics/technique/floating-point-arithmetic) page asks *when* a
float can be trusted in an exact problem. This page is about the format underneath:
[IEEE 754 binary64](https://en.wikipedia.org/wiki/Double-precision_floating-point_format), the
`double` of C and the `float` of Python. The two languages share it bit for bit, and that one
fact settles most porting questions. The problems below use it in four ways. They depend on its
determinism (197), use the values it stores exactly (232), keep a probability computation inside
its error budget (253), and treat it as a fast first guess that integers then correct (210, 808).

## The idea

A double is 64 bits: one sign bit, an 11-bit biased exponent, and a 52-bit fraction with an
implicit leading 1. That gives a **53-bit significand**. Everything an engineer needs follows from
that layout:

| Property | Value | Consequence |
|---|---|---|
| Machine epsilon | 2⁻⁵² ≈ 2.2 × 10⁻¹⁶ | About 15–17 significant decimal digits; `%.17g` round-trips any double |
| Exact integers | every integer with \|n\| ≤ 2⁵³ ≈ 9.007 × 10¹⁵ | Above that, only every 2nd, 4th, … integer is representable |
| Exact fractions | dyadic rationals m / 2ᵏ in range | `0.5`, `2**-t`, `0.375` are exact; `0.1` and `1/3` are not |
| Rounding | `+ − × ÷ sqrt` correctly rounded (round-half-even) | The same inputs give the same bits on every conforming machine |

Python's `float` *is* a C `double`: CPython stores one in each float object and passes most
operations to the C compiler and C library. So a faithful C port of float code is not just
approximately equal to the Python. It produces the **same bit patterns**, as long as both sides
do the same operations in the same order and call the same library functions. The places where
the two can still drift apart are worth knowing:

- **Library functions are not covered by IEEE.** `pow`, `exp`, `log` are only "nearly" correctly
  rounded, and the result depends on the libm. CPython's `x ** y` on floats calls the platform
  `pow`, so on one machine the two sides agree. A different libm could change the last bit.
- **Extended precision.** C's `long double` is the 80-bit x87 format on x86 (64-bit significand)
  and something else on other targets. Using `sqrtl` in C where Python uses a double `sqrt` is a
  deliberate change of format, not a port.
- **Evaluation order and contraction.** `a*b + c` may compile to a fused multiply-add, which
  rounds once instead of twice. Reordering a sum changes its rounding. Faithful ports keep the
  Python's expression shape.
- **Formatting.** `f'{x:.9f}'` and `printf("%.9f", x)` both round the exact binary value
  correctly, so a quoted answer comes out the same digit string on both sides.

## How the solutions use it

### Determinism: exact equality as a cycle test (197)

Problem 197 iterates `u ↦ ⌊2^(c − u²)⌋ · 10⁻⁹` and asks for `u_n + u_{n+1}` at an astronomically
large `n`. The floor truncates every term to a multiple of 10⁻⁹, so the orbit lives in a finite
set of doubles. A deterministic map on a finite set is eventually periodic, and this one settles
into a 2-cycle after a few hundred steps. The solution detects the cycle with a bare
`u_k == u_{k−2}`, with no tolerance. That is sound because the iteration is a pure function of
the current double: once the same bits come back, the same bits follow forever. The `==` test is
not about the real-number sequence, which may never repeat exactly. It is about the floating-point
sequence the program actually computes, and that one does repeat.

The C port writes `floor(pow(2.0, C - x*x)) * 1e-9`, the same expression the Python evaluates with
`2.0 ** (...)`. Both reach the same `pow`, so both find the cycle at the same step and print the
same nine digits. Replacing `pow(2, y)` with `exp2(y)` in one language would be mathematically
equal and might still break that agreement.

### Exact dyadics in a probability recurrence (232)

In the race of problem 232 a player picks a `T`, and wins `2^(T−1)` points with probability
`2^−T`. Every one of those probabilities is a power of two, so it is stored *exactly*. The Python
builds it as `2.0 ** -t` and the C as `ldexp(1.0, -t)`, which just sets the exponent field. These
are two spellings of the same exact value, and either one is safe to use here, unlike `pow` in 197,
because no rounding is involved. The rest of the recurrence (the fixed point
`(heads + q·win) / (1 + q)` per choice, then a max over choices) rounds in the ordinary way, but
it only ever combines probabilities in [0, 1]. The error stays near epsilon, far below the eight
decimal places the answer needs.

### A benign error budget instead of exact rationals (253)

Problem 253 runs a forward pass over a Markov chain on caterpillar segments and wants an
expectation to six decimal places. The notes check the choice that makes this possible. The
recurrence only adds and multiplies non-negative weights that sum to 1, and it has no
subtraction of nearly equal values for cancellation to hit. So relative error stays near machine
epsilon across the whole pass. The solution was confirmed against an exact
[`fractions.Fraction`](https://docs.python.org/3/library/fractions.html) run of the same
recurrence, whose numerator and denominator run to over forty digits. Doubles lose nothing that
matters here, and they keep the C port a plain flattened `double` array instead of a bignum
library. This is the positive version of the
[round-off](/topics/technique/round-off-error) question: write the error bound down, and when it
leaves orders of magnitude to spare, use the fast format.

### Float seed, integer verdict (210, 808)

When the quantity is an integer square root, the double is only a guess. Problem 210 counts
lattice points inside a circle row by row, which needs `⌊√d⌋` for values of `d` far past 2⁵³. The
NumPy version takes `np.sqrt` over a whole `float64` array and then corrects the guess with
vectorised integer loops. Here is the pattern as a general helper:

```python
s = np.floor(np.sqrt(d.astype(np.float64))).astype(np.int64)
while (m := s * s > d).any(): s[m] -= 1          # float64 rounded d before the root
while (m := (s + 1) * (s + 1) <= d).any(): s[m] += 1
```

The C port seeds with `sqrtl` on `long double` and runs the same two correction loops. On x86 the
extra 11 bits of significand make the seed exact more often, but the loops are what make it
correct. Without NumPy, Python would just call
[`math.isqrt`](/topics/technique/math-isqrt). See
[integer square root](/topics/technique/integer-square-root) for the exact algorithms.

Problem 808 asks whether a digit-reversed square is itself a square. The Python writes
`int(r ** 0.5)` with no correction, and the C clamps `(long long)sqrt((double)r)` in both
directions. The Python is safe at these sizes, and the reason is the format. When `r = k²`
exactly, converting `r` to a double perturbs it by at most half an ulp, the square root halves
that relative error, and correct rounding then lands exactly on the representable integer `k`.
When `r` is not a square, the integer check `s * s == r` rejects it whatever `s` is. The C clamp
costs two multiplies and removes the need for that argument. That makes it the better port
whenever the bound on `r` is not obvious.

## How to reason about it

- **Know which half of the format you are in.** Integers below 2⁵³ and dyadic fractions are exact
  (232's `2^−T`, 197's comparisons). Everything else is a value within half an ulp of the truth,
  and a chain of operations widens that.
- **Exact `==` is fine when it compares the program's own deterministic values** (197's cycle). It
  is wrong when it compares a computed value with a mathematical one (`0.1 + 0.2 == 0.3`).
- **Port expressions, not formulas.** Keep the same operations, the same order, and the same library
  calls, and C and Python agree to the bit. Change `pow` to `exp2`, `sqrt` to `sqrtl`, or let the
  compiler fuse a multiply-add, and they agree only to within an ulp, which is enough to move a
  floor or break an equality.
- **Budget the error against the answer's precision** (232, 253). Sums of non-negative
  probabilities are benign; differences of near-equal quantities are not.
- **Above 2⁵³, a double is a seed.** NumPy's `float64` has the same 2⁵³ limit as scalar code (210),
  so vectorising does not remove the need for the integer fix-up.
- **Print with intent.** `%.17g` / `repr` shows the stored value, which is useful in `--show`
  diagnostics (232 prints both). `%.Nf` gives the quoted answer, rounded once from the exact binary
  value. For rounding policy beyond that, see [rounding](/topics/technique/rounding).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0232](/solutions/0232/) — The Race
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
