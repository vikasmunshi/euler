<!-- tags: [watch-integer-width] -->
<!-- status: final 2026-10-15T10:17Z -->
# Watch integer width

Almost every one of these problems is trivial in Python and a trap in C, for the same reason: Python's
`int` is an [arbitrary-precision](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
"bignum" that grows to fit whatever you compute, while C's integers are
[fixed-width](https://en.wikipedia.org/wiki/C_data_types#Basic_types) boxes that
[overflow](https://en.wikipedia.org/wiki/Integer_overflow) the moment a value outgrows them. The
takeaway is a habit: when you translate a working Python solution to C — as every problem here does
— stop at each multiply, sum, and power and ask *how big can this actually get?* The number that
matters is not the final answer but the largest **intermediate** value on the way to it — and, as
the later problems show, the one place Python *does* overflow is the fixed-width NumPy array
underneath it.

## The idea

Python never makes you think about width. `2**1000`, `product`, `pow(i, i, 10**10)` — the
interpreter promotes to a bignum silently and the arithmetic is exact up to the limits of memory.
C gives you a fixed menu, and picking the wrong item is a silent, data-dependent bug: signed
overflow is [undefined behaviour](https://en.wikipedia.org/wiki/Integer_overflow#Security_ramifications_and_bugs),
so a value that fits on your test case and wraps on the real one may still "run fine" and just
print the wrong number. The widths worth memorising:

| C type | signed max | roughly |
| --- | --- | --- |
| `int` (32-bit) | $2^{31}-1$ | $2.1 \times 10^{9}$ |
| `long long` / `int64_t` | $2^{63}-1$ | $9.2 \times 10^{18}$ |
| `unsigned long long` | $2^{64}-1$ | $1.8 \times 10^{19}$ |
| `__int128` (GCC/Clang) | $2^{127}-1$ | $1.7 \times 10^{38}$ |

Against that menu, the problems in this topic fall into three tiers, and each tier has a standard
C response.

**Tier 1 — reach for 64 bits.** The value overflows a 32-bit `int` but fits comfortably in a
`long long`. Problem 8 multiplies thirteen digits: $9^{13} \approx 2.5 \times 10^{12}$, past `int`
but far short of `long long`. Problem 6 squares a sum near $n(n+1)/2$; for the real $n$ the square
lands around $10^{10}$. The whole fix is to declare the accumulators `long long` and move on:

```c
long long product = 1;                 /* not int — 9^13 overflows 32 bits */
for (int j = i; j < i + length; j++)
    product *= (number[j] - '0');
```

"Fits in 64 bits" is a claim to check, not assume, once the answer gets close to the ceiling.
Problems 240 and 242 land at 80–97% of $2^{63}-1$, and both C ports keep `long long` only after
bounding every term added; 242's answer grows like $t^{\log_2 3}$, so a modestly larger input would
cross the line. Problem 365's answer sits near $9 \times 10^{18}$ — inside `long long`, but close
enough that the port takes an `unsigned __int128` accumulator as the honest choice rather than
defend a margin of a few percent.

**Tier 2 — the intermediate overflows 64 bits, even though the answer doesn't.** Problem 48 sums
$i^i \bmod 10^{10}$. The *answer* is a ten-digit number, but computing it multiplies two operands
each near $10^{10}$, and their product $\approx 10^{20}$ blows past a signed 64-bit `long long`.
The reduced result fits; the multiply on the way to it does not. Two mitigations, often combined:
reduce modulo at every step so operands stay small, and **widen the multiply itself** to a type
that holds the product before you reduce:

```c
/* operands near 10^10, product ~10^20 — widen to __int128 before reducing */
result = (__int128)result * base % mod;
```

Where `__int128` isn't available, the same job is done by a `mulmod` built from repeated
doubling, or by splitting the operands into high and low halves.

The single most common Tier 2 site in this collection is the modular squaring inside
[Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test): a candidate near
$3 \times 10^9$ already squares past $2^{63}$ (problem 248), so problems 241, 245 and 248 all route
that one multiply through `__int128` — which is also how the C keeps pace with CPython's compiled
`pow(a, d, n)`. The widened operation need not be a modular one: problem 255 keeps every interval
bound and its total in `long long` and widens only the final rounding step, which multiplies by
$2 \times 10^{10}$.

The other half of Tier 2 is the **accumulator**. A running total of many 64-bit terms can clear
$2^{64}$ even when no single term comes close: problem 421's total grows as $4N\pi(M)$ and passes
$2^{64}$ by a quarter, and 272, 276, 297, 882 and 963 all have sums that outgrow 64 bits while the
per-step values fit comfortably. The fix is an `unsigned __int128` total — and then a small printer,
because `printf` has no conversion for it:

```c
static const char *format_u128(unsigned __int128 value) {
    static char digits[40];                        /* 2^128 has 39 decimal digits */
    char *cursor = digits + sizeof digits - 1;
    *cursor = '\0';
    do { *--cursor = (char)('0' + (int)(value % 10)); value /= 10; } while (value);
    return cursor;
}
```

Even 128 bits is a box with walls. Problem 241 carries exact fractions in `unsigned __int128` and
needs two guards to keep every product under $2^{128}$, one of them capping a product of primes at
the largest primorial that fits — a cap the Python mirrors so both run the identical algorithm.

**Tier 3 — no fixed width is enough; you must build the bignum yourself.** Problem 16 wants the
digit sum of $2^{1000}$ — a 302-digit number — and problem 25 hunts the first 1000-digit
[Fibonacci](https://en.wikipedia.org/wiki/Fibonacci_sequence) term. No C integer comes close.
Here you re-implement, by hand, the arbitrary precision Python gave you for free: store the number
as an array of decimal digits and do
[schoolbook long multiplication](https://en.wikipedia.org/wiki/Multiplication_algorithm#Long_multiplication)
with carries.

```c
/* digits[] little-endian; multiply the whole big number by base, once */
int carry = 0;
for (int j = 0; j < len; j++) {
    int val = digits[j] * base + carry;
    digits[j] = (unsigned char)(val % 10);
    carry = val / 10;
}
while (carry > 0) { digits[len++] = (unsigned char)(carry % 10); carry /= 10; }
```

When the bignum is only needed some of the time, don't pay for it all of the time. Problem 254's
candidate length reaches about $10^{51}$ for the largest inputs, so its C uses
[GMP](https://gmplib.org/) `mpz_t` — but keeps a native `unsigned long long` fast path for every
candidate of at most 19 digits, which covers the dense small cases, and falls back to GMP only on
the sparse large ones where a candidate or two settles the answer.

That is the whole spectrum: pick a wider built-in, widen just the risky operation, or hand-roll a
bignum — in rising order of effort, chosen by how far the biggest intermediate exceeds the box.

## Two places overflow hides

**Inside a bound test.** A guard like `n1 * n1 * e < room` reads as harmless, but the products a
bound test exists to *reject* are exactly the large ones, so they are exactly the ones that
overflow. In problem 251 that product wrapped for a large divisor, the wrapped value passed the
test, and the count came out inflated — invisible on the main input, caught only by the larger
benchmark cases. Problem 245's prefix tests $m p^2$ have the same shape. There are two fixes:
evaluate the test in `__int128` (245), or rearrange it so the large product is never formed (251),
comparing against a cap computed once:

```c
/* n1*n1*e < room  <=>  n1 <= isqrt((room - 1) / e) — no product can wrap */
unsigned long long cap = isqrt((room - 1) / e);
```

**Inside NumPy.** Python's `int` cannot overflow, but a NumPy `int64` / `uint64` array is a C
array, and its arithmetic wraps just as silently. Problem 421 sums millions of `uint64` terms; turning
the array sum into a Python `int` afterwards does not help, because the array sum is what overflows.
It splits each term into 32-bit halves first, so neither partial sum can wrap:

```python
total = (int((terms >> 32).sum()) << 32) + int((terms & 0xFFFFFFFF).sum())
```

Problem 249 sums its counters in chunks of 1024 for the same reason, and problem 1010 trusts its
`int64` arithmetic only after proving the bound: every term counts a partition, the counts sum to
an identity near $2.8 \times 10^{18}$, and `--show` checks that identity on every run.

## How to reason about it

- **Bound the intermediate, not the answer.** A ten-digit result computed through a twenty-digit
  product is Tier 2, not Tier 1. Trace the largest value that ever exists, including inside a
  multiply before the `% mod` lands (problem 48), or a factorial or power that is reduced later
  (problems 97, 288). The intermediate need not be on the path to the answer at all: in problem
  943 a deep subtree's leaf count can outgrow the root's, so its counts and sums are `__int128`.
  This is where a Python-to-C port most often goes wrong.
- **Reduce early to stay small — or spend the headroom on purpose.** In modular problems, taking
  the remainder after *every* operation keeps operands small; that is what keeps
  [modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation) (problems 48, 97)
  inside 64 bits between multiplies — leaving only the single product to widen. But the `%` is the
  expensive part, and the width you have is a budget. Problem 249's fold can at most double a
  counter, so starting below $10^{16}$ it runs ten folds before reducing — the worst case,
  $2^{10} \cdot 10^{16} \approx 1.02 \times 10^{19}$, still fits an unsigned 64-bit word — and that
  batching cut the Python run time by more than half.
- **Make the width limit an explicit input limit.** Where a representation caps the input, say so
  up front instead of letting it wrap later. Problem 421's modular multiply needs $p^2 < 2^{64}$,
  so both versions reject a prime bound $M \ge 2^{32}$ on entry; problem 963 packs a shape into an
  `unsigned long long`, which caps it at 13 trits.
- **Mind the order and exactness of mixed operations.** `(2*n+1)*(n+1)*n / 6` (problem 6) must
  keep the product exact before the division; reorder or widen so no partial product overflows and
  the final divide stays whole.
- **Signed overflow is undefined, so it hides.** Unlike Python, a C overflow throws no error and
  may pass small tests. When a C port disagrees with a verified Python solution only on the large
  input, an overflowed intermediate is the first suspect — reach for `long long`, then `__int128`,
  then a digit array. Unsigned overflow, by contrast, is defined: it wraps modulo $2^{64}$, so a
  total that is off by an exact multiple of $2^{64}$ points straight at the accumulator.
- **Let the Python version be the oracle — where it is pure Python.** Python's own integers can't
  overflow, so arithmetic done in them is trustworthy by construction. Port to C for speed, but keep
  the Python solution as the reference the C output must match. That guarantee stops at the NumPy
  boundary: a vectorised solution needs the same width audit as its C port (problems 249, 421,
  1010), and a brute force in plain Python ints is the better oracle for both.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0031](/solutions/0031/) — Coin Sums
- ● [0048](/solutions/0048/) — Self Powers
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0240](/solutions/0240/) — Top Dice
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0245](/solutions/0245/) — Coresilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
