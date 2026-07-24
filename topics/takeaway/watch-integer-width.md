<!-- tags: [watch-integer-width] -->
<!-- status: final -->
# Watch integer width

Every one of these problems is trivial in Python and a trap in C, for the same reason: Python's
`int` is an [arbitrary-precision](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
"bignum" that grows to fit whatever you compute, while C's integers are
[fixed-width](https://en.wikipedia.org/wiki/C_data_types#Basic_types) boxes that
[overflow](https://en.wikipedia.org/wiki/Integer_overflow) the moment a value outgrows them. The
takeaway is a habit: when you translate a working Python solution to C — as every problem here does
— stop at each multiply, sum, and power and ask *how big can this actually get?* The number that
matters is not the final answer but the largest **intermediate** value on the way to it.

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

That is the whole spectrum: pick a wider built-in, widen just the risky operation, or hand-roll a
bignum — in rising order of effort, chosen by how far the biggest intermediate exceeds the box.

## How to reason about it

- **Bound the intermediate, not the answer.** A ten-digit result computed through a twenty-digit
  product is Tier 2, not Tier 1. Trace the largest value that ever exists, including inside a
  multiply before the `% mod` lands (problem 48), or a factorial or power that is reduced later
  (problems 97, 288). This is where a Python-to-C port most often goes wrong.
- **Reduce early to stay small.** In modular problems, take the remainder after *every* operation
  so operands never grow. That is what keeps [modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation)
  (problems 48, 97) inside 64 bits between multiplies — leaving only the single product to widen.
- **Mind the order and exactness of mixed operations.** `(2*n+1)*(n+1)*n / 6` (problem 6) must
  keep the product exact before the division; reorder or widen so no partial product overflows and
  the final divide stays whole.
- **Signed overflow is undefined, so it hides.** Unlike Python, a C overflow throws no error and
  may pass small tests. When a C port disagrees with a verified Python solution only on the large
  input, an overflowed intermediate is the first suspect — reach for `long long`, then `__int128`,
  then a digit array.
- **Let the Python version be the oracle.** Because Python can't overflow, its answer is
  trustworthy by construction. Port to C for speed, but keep the Python solution as the reference
  the C output must match — the discipline these problems teach.

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
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
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
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
