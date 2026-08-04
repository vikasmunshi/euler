<!-- tags: [arbitrary-precision-arithmetic] -->
<!-- status: final -->
# Arbitrary-precision arithmetic

[Arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) is
integer (or fractional) arithmetic whose operands are limited by memory rather than by a register
width. It recurs across these problems for two quite different reasons. Sometimes the *answer* is a
big number — the digits of 21000, of 100!, of the 1000-digit Fibonacci term. Far more often
the big number is an *intermediate*: an exact rational, a convergent's numerator, a scaled square
root, a binomial coefficient that must be compared for equality rather than approximated. In Python
this is invisible — [`int`](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
is unbounded and the arithmetic just works. In the C port it is a decision you have to make and
implement, and that asymmetry is what makes this tag worth a page.

## The idea

A machine integer is a fixed number of bits: 64 in a `long long`, 128 if you reach for
[`__int128`](/topics/technique/int128). Arbitrary precision drops the ceiling by representing a
number as a *sequence of limbs* — an array of small integers, each holding one digit in some base
$B$, least-significant first — and implementing the schoolbook algorithms over that array. Addition
walks the limbs propagating a carry; multiplication is the $O(n \cdot m)$ double loop; division is
[Knuth's Algorithm D](https://en.wikipedia.org/wiki/Division_algorithm#Long_division). The number
grows by appending limbs, so the only bound is memory.

The choice of $B$ is the whole engineering decision, and the public solutions show both ends of it.
Problem 16 builds $2^{n}$ in an array of **single decimal digits** — `unsigned char`, one digit per
byte:

```c
for (int j = 0; j < len; j++) {
    int val = digits[j] * base + carry;
    digits[j] = (unsigned char)(val % 10);
    carry = val / 10;
}
```

That is the easiest version to write and to print, and it wastes about 96% of each byte. Problems
25, 57, 65 and 80 instead pack **nine decimal digits into a 64-bit limb** with $B = 10^9$, chosen so
that a limb-by-limb product $B^2 \approx 10^{18}$ still fits under the 64-bit ceiling — one multiply
now does the work of nine, and the value is still trivially convertible to decimal because the base
is a power of ten. CPython's own `int` makes the same trade in binary, using 30-bit digits inside a
machine word.

Above a certain complexity you stop hand-rolling. Several private solutions link
[GMP](https://gmplib.org/) and work in `mpz_t` — problems 168, 169, 172, 176, 178, 180, 192, 203,
321 and 387 all do — because once you need division, comparison, exact binomials and a sort over
big values, a library that has already been tuned (with sub-quadratic multiplication above a
threshold) beats anything you will write in an afternoon.

Three shapes of use recur, and it is worth naming them separately:

- **The answer is the digits.** Problems 13, 16, 20 and 25 want a digit sum or a digit count, so the
  full expansion has to exist. Nothing clever avoids it; the only question is how efficiently you
  build it.
- **Exactness for an equality or a comparison.** A convergent recurrence
  $(p, q) \to (p + 2q,\, p + q)$ (Problem 57), an exact
  [`Fraction`](https://docs.python.org/3/library/fractions.html) chain for the continued fraction of
  $e$ (Problem 65), the fundamental solution of a [Pell equation](https://en.wikipedia.org/wiki/Pell%27s_equation)
  (Problem 66), squarefree tests on binomial coefficients (Problem 203) — in each case a `double`
  would silently agree with itself to fifteen digits and give the wrong count. This is the same
  instinct as [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
- **Fixed point in disguise.** To get $d$ digits of an irrational, scale by $10^{2d}$ and take an
  *integer* square root. Problem 80 does exactly this — `number *= 10 ** (2 * digits)`, then
  [Heron's method](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Heron's_method)
  in integers — and the resulting digit string is exact by construction. Where the quantity is not a
  root, [`decimal`](https://docs.python.org/3/library/decimal.html) with an explicit
  `getcontext().prec` does the same job: problems 686 and 751 both set a precision in the hundreds of
  digits and compute fractional parts of logarithms there rather than in binary floating point.

## How to reason about it

**Ask first whether you need the digits at all.** Arbitrary precision is the fallback, not the
opening move. If the problem asks for a value modulo something, use
[modular arithmetic](/topics/domain/modular-arithmetic) and never let the number grow — Problem 97
computes a digit-slice of a 7-million-digit prime with nothing wider than a 128-bit product. If it
asks whether two quantities are equal, a well-chosen invariant often decides it without evaluating
either. A big integer that exists only because you did not think about reduction first is a cost you
chose.

**When you do need it, the base and the algorithm dominate — not the language.** The benchmarks here
make that unusually vivid. For Problem 25 (repeated addition, base-$10^9$ limbs), C runs in
$0.66$ ms against Python's $12$ ms — an 18× win. For Problem 65 (exact rationals) the C `BigInt`
beats Python's `Fraction` by 72× at $n = 100$ and by 500× at $n = 10\,000$, because `Fraction`
normalises through a [GCD](https://en.wikipedia.org/wiki/Greatest_common_divisor) on every operation.
But for Problem 16 the ranking inverts: at $2^{10000}$ the hand-rolled C takes $28.8$ ms and Python
takes $0.24$ ms — Python is **122× faster**. Nothing about C is at fault; the C code multiplies by
the base $n$ times over single-decimal-digit limbs, an $O(n^2)$ walk, while `2 ** 10000` uses
[exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) over 30-bit
limbs. A naive bignum in a fast language loses to a good bignum in a slow one, every time. This is
[algorithm beats language](/topics/takeaway/algorithm-beats-language) in its purest form.

**Know the ladder, and stop at the lowest rung that holds.** 64-bit native → `__int128` (~38 digits,
still machine speed) → a hand-rolled base-$10^9$ `BigInt` (fine for add/multiply/compare) → GMP
(when you need division, roots, or performance at scale). Problem 80's two solutions bracket this:
`s0` picks the algorithm that keeps the numbers small and finishes the 999-root sweep in $5.3$ ms in
C, while `s1`'s heavier big-integer work takes $281$ ms for the same answer.

**Two pitfalls specific to Python.** First, `int` being free is exactly why the C translation
surprises you — the overflow you never saw is now yours to handle, and the port is not a
transliteration but a design task. Second, Python 3.11 and later cap `int` ↔ `str` conversion at 4300
digits by default (a denial-of-service mitigation, since the conversion is quadratic), so `str(n)` on
a large value raises `ValueError`. Problem 57 handles it where it actually fires rather than lifting
the limit up front:

```python
try:
    result += len(str(numerator)) > len(str(denominator))
except ValueError:
    sys.set_int_max_str_digits(0)
```

Reaching for `n.bit_length()` or comparing against a precomputed power of ten sidesteps the
conversion altogether, and is usually faster besides.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0013](/solutions/0013/) — Large Sum
- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0031](/solutions/0031/) — Coin Sums
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0205](/solutions/0205/) — Dice Game
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0250](/solutions/0250/) — $250250$
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0768](/solutions/0768/) — Chandelier
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
