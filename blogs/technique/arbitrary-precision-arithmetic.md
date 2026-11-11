<!-- tags: [arbitrary-precision-arithmetic] -->
<!-- status: final 2026-11-11T09:04Z -->
# Arbitrary-precision arithmetic

[Arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) is
integer (or fractional) arithmetic whose operands are limited by memory rather than by a register
width. It recurs across these problems for quite different reasons. Sometimes the *answer* is a
big number — the digits of $2^{1000}$, of $100!$, of the 1000-digit Fibonacci term. Far more often
the big number is an *intermediate*: an exact rational, a convergent's numerator, a scaled square
root, a binomial coefficient that must be compared for equality rather than approximated. And
sometimes it is not really a number at all, but a container — a bit array or a packed vector that
happens to be stored as one huge integer. In Python
this is invisible — [`int`](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
is unbounded and the arithmetic just works. In the C port it is a decision you have to make and
implement, and that asymmetry is what makes this tag worth a page.

## The idea

A machine integer is a fixed number of bits: 64 in a `long long`, 128 if you reach for
[`__int128`](/blogs/technique/int128). Arbitrary precision drops the ceiling by representing a
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
239, 321, 387, 558, 581, 582, 768, 776, 982 and 988 all do — because once you need division, comparison, exact binomials and a
sort over big values, a library that has already been tuned (with sub-quadratic multiplication above
a threshold) beats anything you will write in an afternoon. GMP also says what you mean:
Problem 239's port divides its rolling factorial and binomial with `mpz_divexact_ui`, which both
documents and exploits the fact that those divisions never leave a remainder.

Four shapes of use recur, and it is worth naming them separately:

- **The answer is the digits.** Problems 13, 16, 20 and 25 want a digit sum or a digit count, so the
  full expansion has to exist. Nothing clever avoids it; the only question is how efficiently you
  build it.
- **Exactness for an equality or a comparison.** A convergent recurrence
  $(p, q) \to (p + 2q,\, p + q)$ (Problem 57), an exact
  [`Fraction`](https://docs.python.org/3/library/fractions.html) chain for the continued fraction of
  $e$ (Problem 65), the fundamental solution of a [Pell equation](https://en.wikipedia.org/wiki/Pell%27s_equation)
  (Problem 66), squarefree tests on binomial coefficients (Problem 203) — in each case a `double`
  would silently agree with itself to fifteen digits and give the wrong count. This is the same
  instinct as [exact arithmetic for equality](/blogs/takeaway/exact-arithmetic-for-equality).
  It holds even when the answer *is* a decimal: Problem 239 wants a probability to twelve places,
  but it is an alternating inclusion–exclusion sum of factorial-sized terms divided by $100!$, and
  cancellation in that sum would eat a `double`'s sixteen digits. Keeping numerator and
  denominator as integers and rounding half-up only at the end,
  `(2 * num * 10**12 + den) // (2 * den)`, makes every printed digit exact by construction.
- **Fixed point in disguise.** To get $d$ digits of an irrational, scale by $10^{2d}$ and take an
  *integer* square root. Problem 80 does exactly this — `number *= 10 ** (2 * digits)`, then
  [Heron's method](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Heron's_method)
  in integers — and the resulting digit string is exact by construction. Where the quantity is not a
  root, [`decimal`](https://docs.python.org/3/library/decimal.html) with an explicit
  `getcontext().prec` does the same job: problems 686 and 751 both set a precision in the hundreds of
  digits and compute fractional parts of logarithms there rather than in binary floating point.
- **A big integer as a container.** An unbounded `int` is also an unbounded
  [bit array](https://en.wikipedia.org/wiki/Bit_array) whose shifts, masks and
  [population counts](https://en.wikipedia.org/wiki/Hamming_weight) run in compiled code. Problem 238
  keeps the set of reachable digit-sum residues as one integer of about 80 million bits, built in a
  single `int(runs, 2)`, and rotates it with `(bits >> s) | (bits << (T - s))` masked to $T$ bits,
  counting what is left with `bit_count()`. Problem 768 packs a whole coordinate vector into one
  integer instead: it evaluates the vector at a base $B$ large enough that no coordinate of any sum
  can carry into its neighbour, so adding two packed integers adds the vectors coordinate-wise, and
  "this subset's vector is zero" becomes a single comparison and a dictionary key. In C both
  containers have to be made explicit — a `uint64_t` word array for 238 (stored as two consecutive
  copies, so a rotation reads as a plain 64-bit window), and an `__int128` for 768, which holds the
  packed codes for the inputs that matter and reports an overflow rather than wrapping beyond them.

## How to reason about it

**Ask first whether you need the digits at all.** Arbitrary precision is the fallback, not the
opening move. If the problem asks for a value modulo something, use
[modular arithmetic](/blogs/domain/modular-arithmetic) and never let the number grow — Problem 97
computes a digit-slice of a 7-million-digit prime with nothing wider than a 128-bit product. If it
asks whether two quantities are equal, a well-chosen invariant often decides it without evaluating
either. A big integer that exists only because you did not think about reduction first is a cost you
chose.

**Or refuse the big number outright.** Problem 66 needs a Pell equation's fundamental solution in
full, however many digits it has. Problem 581 meets the same equations, one for each squarefree
smooth $q$, and most of their fundamental solutions are astronomically large. But it only wants
solutions whose $y$ is [smooth](https://en.wikipedia.org/wiki/Smooth_number), and a number with
hundreds of digits has essentially no chance of that. So the continued-fraction walk gives up once
$y$ passes a cap of $10^{10}$, and it never builds the huge solutions at all. A cap like that is a
claim about the problem, so the solution tests it: raising the cap to $10^{30}$ or $10^{40}$ gives the
same answer. Even inside the cap, the C port cannot stay in machine integers: $d\,y^2$ reaches about
$4 \times 10^{41}$, past the `unsigned __int128` ceiling, so the Pell check runs in GMP. The cap
limits how *many* big numbers you build. It does not make the ones you keep small.

**A huge bound is not huge work.** Problem 582 takes $10^{100}$ as its *input*. The C port's first
job is to parse `10**100` into an `mpz_t`, because no machine type can hold it. Even so, the search
is cheap. Each family of solutions is the orbit of a seed under the unit $2 + \sqrt 3$ of a
[Pell-type equation](https://en.wikipedia.org/wiki/Pell%27s_equation), so its values grow
geometrically, and the orbit passes $10^{100}$ after about 175 steps. The big numbers set the cost
of each step, and the geometry keeps the number of steps small. When an orbit, a doubling or a
continued fraction stands between you and a 100-digit bound, the bound's size is a parsing problem
and not a running-time problem.

**Division is where reduction gets hard.** Problem 250 wants a count modulo $10^{16}$ and builds it
from rows of binomials $\binom{c}{i}$. Python takes the easy road: it runs the exact recurrence
`b = b * (c - i) // (i + 1)` in big integers and reduces only when folding each coefficient in. The C
port cannot, because division by $i + 1$ has no meaning modulo $10^{16}$ unless $i + 1$ is coprime to
it. So it carries each binomial factored as $2^{a} \cdot 5^{b} \cdot u$ — strips the twos and fives
out of every numerator and denominator, keeps the unit $u$ coprime to the modulus, and divides by
multiplying with a [modular inverse](/blogs/technique/modular-multiplicative-inverse-application) —
with `__int128` products keeping each step exact. Python's big integers are buying the *right to
divide*, and the C port has to earn it back with number theory; the reward is $24$ ms against
Python's $0.95$ s.

**Exact rationals: keep the denominator out of the inner loop.** A `Fraction` is exact, but it pays
for a [GCD](https://en.wikipedia.org/wiki/Greatest_common_divisor) on every operation, and that
cost multiplies when every cell of a matrix is a fraction. Problem 982 is a zero-sum game, and it
solves the game as a [linear programme](https://en.wikipedia.org/wiki/Linear_programming) by exact
simplex. Instead of a tableau of `Fraction`s, it keeps a tableau of integers that all share one
implicit denominator: the previous pivot. This is the
[Bareiss](https://en.wikipedia.org/wiki/Bareiss_algorithm) fraction-free update,
`(x * piv - f * y) // det`. The division is always exact, because Sylvester's identity guarantees
that `det` divides the numerator. So nothing is normalised, the entries stay as small as the
determinants they really are, and the answer comes out as one rational, rounded only at the end.
The C port does the same in GMP, with `mpz_submul` and `mpz_divexact`, which is again the call that
says "this division has no remainder". The reverse also works: put the denominators in only at the
end. Problem 776 sums $n / d(n)$ over every $n \le N$, but groups the terms by digit sum $s$, so a
digit DP builds a handful of exact integer totals $T(s)$ (around $10^{40}$, which needs GMP in C).
Only the final $\sum_s T(s)/s$, with fewer than $9 \times$(digits of $N$) terms, is a rational at all.
That problem also takes the exact-rounding idea from Problem 239 to scientific notation. The exponent
is the digit count of $\lfloor x \rfloor$ minus one. The mantissa is
$\lfloor x / 10^{e-12} + \tfrac12 \rfloor$. A rounding carry into a fourteenth digit is caught
and shifts the exponent. All three steps are integer operations, so every printed digit is exact.

The same counting DPs explain most of the GMP in the newer C ports. A DP that adds up values
(776) or counts configurations (Problem 988 counts antichains in a staircase grid, and the number
grows exponentially with the grid) produces totals far larger than anything in its input. The code
is plain addition, and the only thing the port has to decide is how wide the accumulator must be.
For 988, `__int128` would not be enough: the totals outgrow 128 bits on the larger test inputs.

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
[algorithm beats language](/blogs/takeaway/algorithm-beats-language) in its purest form. The same
fact narrows the gap whenever Python's big integers carry the inner loop: Problem 238's bitset sweep
is only $6.8\times$ slower in Python ($3.51$ s against $0.51$ s), far less than an interpreted
bit-twiddling loop would suggest, because every shift and popcount is already a compiled pass over
the limbs; C wins by fusing them into one. And where both sides use a real bignum library, the
library decides — Problem 239's C port is about $4.8\times$ faster simply because GMP's
multiplications are faster than CPython's.

**Know the ladder, and stop at the lowest rung that holds.** 64-bit native → `__int128` (~38 digits,
still machine speed) → a hand-rolled base-$10^9$ `BigInt` (fine for add/multiply/compare) → GMP
(when you need division, roots, or performance at scale). Problem 80's two solutions bracket this:
`s0` picks the algorithm that keeps the numbers small and finishes the 999-root sweep in $5.3$ ms in
C, while `s1`'s heavier big-integer work takes $281$ ms for the same answer. Problem 957 sits on
the `__int128` rung by design: its answer is a closed form whose dominant term grows like
$11 \cdot 16^n$, past 64 bits at the main input $n = 16$, so the C port computes in `__int128`,
rejects $n > 30$ where even that would overflow, and needs its own decimal formatter because `printf`
cannot print a 128-bit value — while Python, unbounded, answers for any $n$. The rungs also mix
within one program: Problem 768's C keeps its packed vector codes in `__int128` but switches to GMP
for the truncated polynomial power at the end, where the counts outgrow 64 bits quickly and reach
34 digits already at $n = 720$ — too close to the `__int128` ceiling to trust it.
Pick the rung per quantity, not per program.

**Or per case: use floating point by default and big precision only where it can go wrong.** Problem 318
evaluates one closed form per pair, a ceiling of $d / (-2\log_{10} y)$, over about 42,000 pairs,
some of them with quotients in the millions. Running every pair in `decimal` would work, and it would
be slow for no reason. A `double` is enough for nearly all of them, provided the logarithm is taken
without [cancellation](/blogs/takeaway/rearrange-to-avoid-cancellation). But a ceiling is a
discontinuous function: it is fragile only when its argument lies near an integer. So the solution
checks for exactly that — if the float quotient is within $10^{-4}$ of an integer, that one pair is
recomputed in arbitrary precision (60-digit `decimal` in Python;
[MPFR](https://www.mpfr.org/), GMP's arbitrary-precision floating-point sibling, at 200 bits in C).
The check costs one comparison per pair and almost never triggers, and the result goes from
"probably right" to guaranteed. The same problem uses big precision a second way, as the
*reference*: a brute-force checker expands $(\sqrt p + \sqrt q)^{2n}$ directly in high-precision
`decimal` and counts the nines, an independent oracle for the closed form on small inputs. Keeping
the slow exact computation for the borderline cases and for testing, and the fast approximate one for
everything else, is often the right split.

**When the numbers are irrational, make the state exact and only the comparison approximate.**
Problem 558 expands integers greedily in base $r$, the real root of $x^3 = x^2 + 1$. Floating point
fails here: each greedy step subtracts a power of $r$ from the remainder, and the rounding error
builds up step after step. Higher precision only moves that failure further out. The fix is to
leave the reals entirely. Since $r^3 = r^2 + 1$, every power of $r$, and therefore every remainder,
is exactly $a + br + cr^2$ with integer coordinates in the ring $\mathbb Z[r]$, and multiplying by
$r$ is the coordinate rotation $(a, b, c) \mapsto (c, a, b + c)$. The state can no longer drift.
What still needs care is the sign of each difference, and the decision is split three ways:

- A fixed-point evaluation $a \cdot 2^p + bF + cG$ with $F$, $G$ the rounded values of $r$ and $r^2$.
  These come from a 200-bit value of $r$ found by integer bisection, which is Problem 80's
  scale-and-take-an-integer-root trick again. The 64-bit products are *allowed to wrap*:
  two's-complement overflow is exact modulo $2^{64}$, and the true value is known to fit, so the
  wrapped result is the right one. NumPy's int64 wraps silently. C has to use `uint64_t`, because
  signed overflow is undefined behaviour there.
- An explicit error bound that marks the narrow band where that rounding could change the sign.
- Inside the band, the exact [field norm](https://en.wikipedia.org/wiki/Field_norm): a 3×3
  determinant with the same sign as the difference. It is cubic in coefficients of about $2^{47}$,
  so it is computed in big integers (GMP in C). It fires on about $3375$ of roughly $10^9$
  decisions.

This is the same filter-then-certify split as in Problem 318, with one difference. The certificate
is not "the same computation at more bits" but an exact algebraic identity, so it cannot itself be
wrong.

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
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0558](/solutions/0558/) — Irrational Base
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ● [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0768](/solutions/0768/) — Chandelier
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0957](/solutions/0957/) — Point Genesis
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0982](/solutions/0982/) — The Third Dice
- ● [0988](/solutions/0988/) — Non-attacking Frogs

<!-- /problems -->
