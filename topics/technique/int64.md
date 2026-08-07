<!-- tags: [int64] -->
<!-- status: final -->
# int64

A 64-bit signed integer is the default working width of every solution here that leaves Python's
unbounded `int` behind — spelled `long long` or [`int64_t`](https://en.cppreference.com/w/c/types/integer)
in the C port, and [`np.int64`](https://numpy.org/doc/stable/reference/arrays.dtypes.html) in the
[NumPy](/topics/technique/numpy) ones. It holds values up to $2^{63}-1 \approx 9.22 \times 10^{18}$,
nineteen digits, at exactly the speed of the hardware. That range is wide enough that the great
majority of these problems never need anything else, and narrow enough that you have to *say* so —
which is why the tag recurs: it marks the solutions where the choice of width was a decision, not
an accident.

## The idea

The 64-bit integer is the machine's native word, so arithmetic on it costs one instruction and
nothing is emulated. The whole art is knowing that the box exists and deciding, deliberately, that
your values fit in it.

**In C, 64 bits is this project's default currency.** The runner hands arguments over as
`long long parse_int(const char *)` and the answer goes back out through
`snprintf(_answer, sizeof _answer, "%lld", ...)` — so a solution that keeps everything at 64 bits
never converts at either end. The two spellings are interchangeable on any 64-bit target:
`long long` is the C99 type guaranteed *at least* 64 bits wide, `int64_t` from
[`<stdint.h>`](https://en.cppreference.com/w/c/types/integer) is the exact-width alias. In practice
the choice follows the neighbours — solutions that call [primesieve](https://github.com/kimwalisch/primesieve)
take its `uint64_t *` arrays and stay in `uint64_t`; everything else uses `long long`, because
`%lld` prints it without the `PRId64` macro dance.

**The cast belongs on an operand, not on the result.** This is the single most common way a
correct-looking C port goes wrong: in C the type of a multiply is decided by its *operands*, so
`long long x = a * b;` with `int` operands computes a 32-bit product, overflows, and only then
widens the wreckage. Problem 9 keeps its loop counters `int` — the search bounds are small — and
promotes only where the product is formed:

```c
int c = sum_sides - a - b;
if (a * a + b * b == c * c) {                       /* fits 32 bits for this bound */
    snprintf(_answer, sizeof _answer, "%lld", (long long)a * b * c);   /* product does not */
}
```

One cast is enough: promoting the leftmost operand promotes the rest of the expression with it.
Problem 87 does the same thing for a fourth power built from `int` primes, and says so in a comment
— `(long long)primes[i4] * primes[i4] * primes[i4] * primes[i4]`, where the un-cast version would
wrap for any prime past 215.

**Literals need the suffix too.** `1 << 40` is a shift of an `int` and is undefined; `1LL << 40` is
the value you meant. The pattern shows up wherever a power of two indexes a 64-bit range —
`(1LL << (k - 1)) * (long long)(k - 2) + 1`, `1ULL << k` for an unsigned span, `1000000007LL` for a
modulus macro — and it pairs with the `ll`-suffixed intrinsics, `__builtin_clzll` and
`__builtin_popcountll`, which are the 64-bit members of that family.

**Uniform width beats mixed width.** Once any value in a computation is 64-bit, the cheapest
correct thing is usually to make *all* of them 64-bit, loop counters included. Problem 642's
prime-sum sieve declares `long long` throughout — the arrays, the indices, the `for` variables —
because its central expression is `num / i` with `num` far past $2^{31}$, and one stray `int`
index would silently truncate a key. Problem 71 does the same at a much smaller scale: `parse_int`
already returns `long long`, so keeping `k`, `num` and `den` at that width means the
$3k-1$ over $7k$ arithmetic needs no thought at all. The cost of over-widening a scalar is zero;
the cost of under-widening one is a wrong answer that passes the small test case.

**NumPy is the same box under a different name.** `np.int64` is a fixed-width C integer, not a
Python one, and it wraps at $2^{63}$ **silently** — no exception, no warning, just a negative
number where a large positive one belonged. Two habits follow. Widen before you accumulate: a
[Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function) array is stored `int8` because it only
holds $-1, 0, +1$, but its [prefix sum](https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html)
is not, so problem 464 spells the widening out as `np.cumsum(mu.astype(np.int64))` rather than
letting `cumsum` inherit the narrow dtype. And pin the dtype at construction — `np.arange(a, b,
dtype=np.int64)` — instead of trusting a platform default, which is how problems 193, 210 and 478
build the ranges they then multiply.

**Sixty-four bits of integer is not fifty-three bits of float.** A tempting shortcut for
$\lfloor\sqrt{n}\rfloor$ over an array is to route through
[`float64`](https://en.wikipedia.org/wiki/Double-precision_floating-point_format), but its mantissa
carries only 53 bits, so past $2^{53} \approx 9 \times 10^{15}$ the conversion is already lossy
before the square root runs. Problem 210's vectorised integer square root takes the float estimate
and then corrects it back to the exact floor with an integer comparison — the general shape being:

```python
s = np.floor(np.sqrt(d.astype(np.float64))).astype(np.int64)
while (mask := s * s > d).any():      # float64 loses precision past 2**53
    s[mask] -= 1                      # nudge each root down to the exact floor
```

## How to reason about it

- **Bound the largest intermediate, then pick the width.** That habit has its own page —
  [watch the integer width](/topics/takeaway/watch-integer-width) — and 64 bits is its most common
  answer. The number to bound is never the final answer; it is the biggest value that ever exists
  on the way there.
- **Memorise one threshold: $\sqrt{2^{63}} \approx 3.04 \times 10^{9}$.** A product of two values
  below that fits in a signed 64-bit integer. This is what makes the standard $10^9+7$ modulus
  safe — $(10^9+7)^2 \approx 10^{18}$, comfortably inside — and what makes a $10^{10}$-scale
  modulus unsafe, since its square is $10^{20}$. Reduce modulo after every operation and the only
  thing left to check is that one multiply.
- **Unsigned buys one bit and defined behaviour, at the price of comparisons.** `unsigned long
  long` reaches $1.8 \times 10^{19}$ and wraps modulo $2^{64}$ by definition, where signed overflow
  is [undefined](https://en.wikipedia.org/wiki/Integer_overflow) and therefore invisible. Take it
  when a library hands you `uint64_t`, when you want the top bit, or when the wraparound *is* the
  algorithm — but never mix it with a signed value in a comparison or a subtraction, because the
  signed side is converted up and a negative difference becomes enormous.
- **Going narrower is a memory decision, not a correctness one.** A sieve of $10^8$ flags at
  `int64` is 800 MB and at `int8` is 100 MB; the values fit either way. Choose the narrow dtype for
  the array that must be resident and widen at the point of accumulation — see the
  [NumPy](/topics/technique/numpy) page for how that trade plays out.
- **When 64 bits genuinely will not hold it, step up once, not twice.**
  [`__int128`](/topics/technique/int128) doubles the digit budget to about $1.7 \times 10^{38}$ at
  near-native speed and is the right next move for a single wide multiply;
  [GMP](/topics/technique/gmp) or a hand-rolled
  [bignum](/topics/technique/arbitrary-precision-arithmetic) is for when no fixed width suffices.
  Problem 192's high-precision continued-fraction comparisons need GMP; most of the problems on
  this page needed only to be told, once, that their integers were 64 bits wide.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0127](/solutions/0127/) — abc-hits
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0899](/solutions/0899/) — DistribuNim I

<!-- /problems -->
