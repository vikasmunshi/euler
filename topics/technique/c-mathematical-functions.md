<!-- tags: [c-mathematical-functions] -->
<!-- status: final -->
# C mathematical functions

`<math.h>` is where a C solution goes the moment a problem stops being pure integer arithmetic:
a square root to bound a search, a `round` to invert a quadratic, an `asin` to integrate an arc.
Python's `math` module looks like the same library with nicer syntax, and for floats it largely
is. The places where the two diverge are exactly where these five solutions spend their care:
what a `double` can hold, what a cast to an integer does, and what happens when an argument
falls outside a function's domain.

## The idea

The [C mathematical functions](https://en.wikipedia.org/wiki/C_mathematical_functions) are a
fixed family declared in `<math.h>` (and linked from `libm`, hence `-lm`): `sqrt`, `cbrt`,
`pow`, `exp`, `log`, the trig and inverse-trig functions, and the rounding group `floor`,
`ceil`, `trunc`, `round`, `lround`/`llround`. Each comes in three widths — `sqrt` on `double`,
`sqrtf` on `float`, `sqrtl` on `long double` — and every one of them works in floating point.
Hand `sqrt` a `long long` and it is silently converted to a 53-bit-mantissa `double` first
(see [double-precision floating point](/topics/technique/double-precision-floating-point-format)).

Python's `math` module wraps the same C library for floats, so `math.sqrt` and `math.asin`
return the same correctly rounded values. Three differences matter in practice:

| | C `<math.h>` | Python `math` |
|---|---|---|
| Integer square root | none — `(long long)sqrt((double)n)` plus a correction | `math.isqrt(n)`, exact on any size of `int` |
| Out-of-domain argument (`sqrt(-1)`, `asin(1.0000001)`) | returns NaN, maybe sets `errno`; the program keeps going | raises `ValueError` |
| Float → integer | a cast truncates toward zero; `round`/`llround` rounds half away from zero | `int()` truncates; `round()` rounds half to even |

## How the solutions use it

**Round, then verify in integers.** Problem 44 needs a constant-time "is this pentagonal?"
test. Inverting P = n(3n−1)/2 gives n = (1 + √(1+24P))/6, so the C side computes that in
`double`, snaps it to the nearest integer, and lets exact arithmetic have the last word:

```c
double n = (1.0 + sqrt(1.0 + 24.0 * (double)m)) / 6.0;
long long ni = (long long)round(n);
return (ni > 0) && (nth_pentagonal(ni) == m);
```

The `double` only *proposes* a candidate; the recomputed `nth_pentagonal(ni) == m` decides.
The Python sibling takes the shortcut `((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()`, which
is sound at this problem's magnitudes but trusts the float outright — past about 2⁵³ a
non-square can round to an exact integer root and the test lies. The C form is the one to copy.

**Seed from `sqrt`, correct with a loop.** Problems 142, 206 and 218 all need ⌊√n⌋ for 64-bit
`n`. Python just calls `math.isqrt`; C has no such function, so each one seeds from the float
and nudges:

```c
long long r = (long long)sqrt((double)n);
while (r * r > n) r--;
while ((r + 1) * (r + 1) <= n) r++;
```

Problem 206 shows why the loops are not decoration: its bounds are the roots of two 17-digit
constants, and `10203040506070809.0` is not even representable — as a `double` it is
`10203040506070808`. The error enters before `sqrt` runs, and only the integer correction
removes it. Problem 218 does the same with `sqrtl` on `long double`, which on x86 carries a
64-bit mantissa and usually lands exactly — but "usually" and "on x86" are why it still
corrects. The mechanics of the correction live on the
[integer square root](/topics/technique/integer-square-root) page; the Python side of the story
is [math.isqrt](/topics/technique/math-isqrt).

**Guard the domain yourself.** Problem 226 integrates the area between a circle and the
blancmange curve, using the circle's half-chord √(r² − (x−c)²) and its antiderivative, which
needs `asin(u/r)`. At the circle's edge, rounding can push r² − u² a hair below zero or u/r a
hair above one. Both languages guard it identically — `t > 0.0 ? sqrt(t) : 0.0` and a clamp of
the `asin` argument into [−1, 1] — but for different reasons: in Python an unguarded call would
*raise*, in C it would quietly return NaN and poison every sum downstream. The C guard is the
more important one, because nothing would tell you it was missing.

## How to reason about it

- **Floats propose, integers decide.** Whenever a `<math.h>` result becomes an integer that
  matters — a bound, an index, a membership test — follow it with an exact check. It costs one
  or two multiplications and removes a whole class of off-by-one-at-the-boundary bugs.
- **Know where precision ends.** A `double` holds every integer up to 2⁵³ ≈ 9·10¹⁵ exactly.
  Above that, the conversion `(double)n` already loses bits, so `sqrt` is correctly rounded
  around the wrong input. See [floating-point arithmetic](/topics/technique/floating-point-arithmetic).
- **Pick the rounding deliberately.** A bare `(long long)x` truncates, which is right for ⌊√n⌋
  of a positive value and wrong for "nearest integer". Use `round`/`llround` for the latter,
  and remember Python's `round` uses banker's rounding if a translation must agree on halves.
- **Domain errors are silent in C.** Clamp or test arguments of `sqrt`, `log`, `asin`, `acos`
  before calling; a NaN propagates through arithmetic without a sound.
- **Reach for `long double` only as a margin, not a guarantee.** Its width is
  platform-dependent; the correction loop is what makes the code portable.

For the language-neutral view of square roots, see [square root](/topics/technique/square-root)
and [sqrt](/topics/technique/sqrt).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0226](/solutions/0226/) — A Scoop of Blancmange

<!-- /problems -->
