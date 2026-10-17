<!-- tags: [rounding] -->
<!-- status: final 2026-10-17T06:53Z -->
# Rounding

Rounding maps a value onto a grid: the nearest integer, the nearest multiple of 10⁻ᵈ, or the floor
or ceiling of a quotient. In these problems it does three different jobs. It is the **last step**,
where a problem asks for an answer "rounded to d decimal places". It is a **test**, where I snap a
float to the nearest grid point to decide whether a computed quantity is really an integer. And it is
**part of the problem**, where the statement defines an iteration with floors and ceilings built in.
Each job fails in its own way, and Python and C give different tools for each.

## The idea

A [rounding](https://en.wikipedia.org/wiki/Rounding) function is fixed by its grid and by its rule
for the points in between. The rules that matter here are:

| rule | value at 2.5 | at −2.5 | Python | C |
|---|---|---|---|---|
| floor | 2 | −3 | `//`, `math.floor` | `floor`; `/` only for non-negatives |
| ceiling | 3 | −2 | `-(-a // b)` | `(a + b - 1) / b` for positives |
| truncation | 2 | −2 | `int(x)` | `/` on integers, `(long)x` |
| half up | 3 | −2 | `(2a + b) // (2b)` | same, in a wide enough integer |
| half to even | 2 | −2 | `round`, `ROUND_HALF_EVEN` | `rint`, `nearbyint` |
| half away from zero | 3 | −3 | `ROUND_HALF_UP` in `decimal` | `round`, `llround` |

The table holds two traps. First, Python's `//` floors and C's `/` truncates, so the same expression
gives different answers on negative operands. Every quotient in these solutions is non-negative,
which is why the two sides can share one formula; I check that each time rather than assume it.
Second, "half up" means different things in different libraries. Python's `decimal.ROUND_HALF_UP`
and C's `round` both round halves *away from zero*. The integer formula `(2a + b) // (2b)` rounds
halves toward +∞. These agree for positive values, which is all these problems need.

## Rounding the answer: keep it exact until the last step

Problems 239, 255 and 493 all ask for a probability or a mean to a fixed number of decimals, and all
three solutions compute it as an exact fraction `a / b` first. Rounding to `d` places is then one
integer division:

```python
scaled = (2 * a * 10**d + b) // (2 * b)    # round(a/b · 10^d), halves up
whole, frac = divmod(scaled, 10**d)
text = f'{whole}.{frac:0{d}d}'
```

That is ⌊a·10ᵈ/b + ½⌋ with the ½ moved inside the floor: doubling both terms keeps everything an
integer. The method has three parts: compute exactly, scale by the power of ten, and floor-divide
once. Every digit it prints is correct, while `float(a) / b` would already have dropped below 17
significant digits before any formatting took place. The zero-padded `frac` field matters too. A
fractional part of 42 at nine places has to print as `000000042`.

The C sides do the same thing with the integer width the numbers need, and that width is where they
differ from Python:

- **493** works with a ratio of two binomials that fit in 64 bits, but `a · 10⁹` does not, so its
  `round_decimal` does the scaling and the division in `__int128` (see
  [int128](/topics/technique/int128)).
- **255** totals iteration counts over every d-digit number. The total still fits in 64 bits;
  `2 · total · 10¹⁰` does not, so only that final rounding line goes up to `__int128`.
- **239** divides a count of permutations by n!, both hundreds of bits long, so the whole formula
  runs in [GMP](/topics/technique/gmp): `mpz_mul_2exp` does the doubling and `mpz_fdiv_q` the
  floored division. The rounded result is small again, so it is read back with `mpz_get_ui` and
  split into whole and fractional parts with ordinary `unsigned long` arithmetic.

Python's arbitrary-precision `int` makes all three the same line. That is the clearest case in the
repository of a step that costs nothing in Python and needs a decision about integer width in C.

Is half up even the right rule? A tie needs `a·10ᵈ/b` to land exactly on a half, which almost never
happens with these denominators, so in practice the rule makes no difference here. The integer form
still states the rule outright, and that is better than whatever a formatting routine does
internally.

## Rounding a float you trust: bound the error first

When the answer is irrational there is no exact fraction to round. Problem 395 (the Pythagorean
tree's bounding box) computes its area as a `double`. Python prints it with `f'{area:.{d}f}'` and C
with `snprintf("%.*f", d, area)`. Both convert the binary value *correctly rounded* to decimal, so
the two languages print the same string from the same double. The real question comes earlier: is
the double close enough to the true value? The solution answers it by computing the support function
twice, truncating the recursion once from above (with the invariant disk) and once from below (with
the bare square). The true value lies between the two, the gap between them is far below 10⁻ᵈ, and
the area sits nowhere near a rounding boundary. Rounding a float is safe only when the error
bound is smaller than the distance to the nearest boundary. If the value is close to a boundary, no
rounding mode will save it. (The cost of floats more generally is covered in
[floating-point-arithmetic](/topics/technique/floating-point-arithmetic).)

Problem 751 is the case where a `double` is not enough at all. It asks for 24 decimals of a fixed
point of a digit-concatenation map, and each step of that map multiplies the error by a growing
integer, losing about one digit per term. The solution iterates in `decimal.Decimal` at 160 digits of
working precision, far more than the 24 it reports. It then rounds once at the end with
`theta.quantize(Decimal(1).scaleb(-24), rounding=ROUND_HALF_EVEN)`. Two settings are at work here:
the context precision controls rounding *during* the computation, and `quantize` controls rounding
*of the answer*. Setting the first well beyond the second is what keeps the 24th digit safe. This
one is Python-only. A faithful C port would need hundreds of digits of decimal arithmetic, a
redesign rather than a translation.

## Rounding as a test: snap, then check how far you moved

Problem 177 counts quadrilaterals whose eight angles are all whole degrees. The solution fixes the
central angle and three corner angles, solves for the last one with `atan2`, and keeps it only if it
is an integer. In floating point, "is an integer" means: round to the nearest integer and accept
only if the rounding moved the value by less than a tolerance.

```python
r = np.round(w).astype(np.int64)
hit = (np.abs(w - r) < 1e-7) & (r >= 1) & (r <= hi)
```

The C side runs the same test one candidate at a time, with `llround(w)` and
`fabs(w - (double)r) < 1e-7`. The tolerance has to sit between two scales. It must be larger than
the accumulated error of the sine ratios and `atan2`, and smaller than the gap between a true hit
and the nearest near miss. The statement offers 10⁻⁹ of a degree. The solution uses a looser
10⁻⁷ degrees, and that works only because no near miss comes that close to an integer. The cross-check
against the known answer is what confirms it. The range check after the snap matters as well: a value that
rounds to 0 or to the full angle is a degenerate triangle and must be rejected. Which half-way rule
the snap uses makes no difference here, because a true hit is nowhere near a half.

This is the floating-point form of a test that is exact in integers: compute
`r = isqrt(n)` and check `r * r == n` (see [integer-square-root](/topics/technique/integer-square-root)
and [exact-arithmetic-for-equality](/topics/takeaway/exact-arithmetic-for-equality)). Use that
exact form whenever an integer certificate exists. Snapping with a tolerance is for cases like the
trigonometry in 177, where no integer certificate exists.

## Rounding inside the problem: floors make step functions

Problem 255 defines a rounded version of Heron's square-root iteration,
x ← ⌊(x + ⌈n / x⌉) / 2⌋, and asks for the mean number of steps over all d-digit n. The floor and
ceiling are what make the problem tractable. Because ⌈n/x⌉ is constant on blocks of x consecutive
n, the map n ↦ next estimate is a step function, and the solution follows whole *intervals* of n
that share an estimate instead of single numbers. Each interval usually has just one child.
An interval ends when its estimate stops changing, and that interval's n are added to the total all
at once. With exact arithmetic there would be no blocks to follow. The rounding in the statement is
the structure the algorithm uses.

The two languages write the ceiling differently. Python uses `-(-lo // x)`, which floors the
negated quotient and is valid for any sign. C uses `(lo + x - 1) / x`, which is correct only because
`lo` and `x` are positive. Every bound the interval walk computes is also a floor or a ceiling. Off
by one in either direction, and an interval either overlaps its neighbour or leaves a gap. So the
solution derives each interval's endpoints from the quotient's floor/ceiling definition, not from
plain division.

## When to reach for which

- **Fixed decimals of a rational answer:** keep the exact fraction, round once with integer
  arithmetic, and size the integer width for `a·10ᵈ` in C.
- **Fixed decimals of an irrational answer:** bound the error first, so you know how many digits
  you can trust, then format. `%.*f` and `f'{x:.{d}f}'` agree on the same double.
- **More digits than a double holds:** `decimal` with spare working precision, then `quantize`
  once at the end.
- **Recognising an integer from a float:** snap and test against a tolerance chosen between the
  error scale and the near-miss scale, but use an exact integer test whenever one exists.
- **Floors and ceilings in the statement:** look for the piecewise-constant structure they create,
  and get the ceiling right for both the language and the sign of its operands.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0751](/solutions/0751/) — Concatenation Coincidence

<!-- /problems -->
