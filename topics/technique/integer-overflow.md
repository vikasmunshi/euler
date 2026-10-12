<!-- tags: [integer-overflow] -->
<!-- status: final -->
# Integer overflow

[Integer overflow](https://en.wikipedia.org/wiki/Integer_overflow) is an arithmetic result that
falls outside the range its type can hold. Python's integers grow without limit, so the
reference solutions never see it. Every C port does, and in C an overflow raises no error: the
answer simply comes out wrong. The takeaway
[watch integer width](/topics/takeaway/watch-integer-width) is about choosing a type wide
enough for a value you can bound. This page is about the cases where you *can't* simply widen:
products that grow inside a search with no fixed ceiling, powers whose size is the thing being
tested, and intermediates that are briefly far larger than anything kept. These need a guard, a
signal or a domain restriction, and the problems below use all three.

## What C actually does

- **Signed overflow is undefined behaviour.** The standard says nothing about the result, and an
  optimising compiler may assume it never happens. It is free to rewrite comparisons and loops on
  that assumption, so an overflowing program may behave in ways no wrap-around model predicts.
  Problem 119's notes put it plainly: the guard exists "because signed 64-bit overflow is
  undefined behavior in C and would silently corrupt the result".
- **Unsigned overflow wraps modulo $2^w$.** This is defined, and sometimes useful, but it is
  just as silent. Problem 421's answer passes $2^{64}$, and a 64-bit accumulator would be off by
  *exactly* $2^{64}$. That exact error is the signature of a wrapped unsigned sum.
- **Python can't show you any of this.** Its answer is the oracle. When the C port disagrees,
  suspect width before you suspect the algorithm.

## Five defences

**1. Prove the bound, then pick the type.** Most overflows are prevented by an estimate made
before any code is written. Problem 6's sums of squares outgrow a 32-bit `int`, so everything is
`long long`. Problem 27's quadratic reaches about $2 \times 10^6$. Problem 119 bounds its search at
$10^{18}$ precisely because that still fits under the signed 64-bit maximum of about
$9.2 \times 10^{18}$.

**2. Guard the multiply with a division.** When a value grows by repeated multiplication inside a
search, test *before* multiplying. For non-negative operands, $a \cdot b \le L$ exactly when
$a \le \lfloor L / b \rfloor$, and the division can't overflow:

```c
/* a * b, but only when the product stays at or below limit; a, b >= 0 and b > 0 */
static int mul_within(long long a, long long b, long long limit, long long *out) {
    if (a > limit / b) return 0;
    *out = a * b;
    return 1;
}
```

Problems 108 and 110 search over prime-exponent assignments with
[branch and bound](/topics/technique/branch-and-bound). Their guard `n > best / p` is the overflow
check *and* the pruning test at once: a candidate that would exceed the best found so far is
abandoned before its product is formed. Problem 484 uses the same test, $p^a > \lfloor N/d \rfloor / p$,
as its loop bound. Problem 119 breaks out of its power loop the moment `power > max_val / base`.

**3. Signal instead of computing.** Sometimes the overflow *is* information. Problem 63 asks which
powers have exactly $n$ digits. Its C `ipow` returns $-1$ when the product would overflow, and the
caller then trusts a $\log_{10}$ estimate instead. That is safe because any power too big for 64
bits has far more digits than any $n$ that can match. Problem 110's `power_ll` returns $0$ as the
same kind of sentinel.

**4. Widen one expression, test, then narrow.** When the *kept* value is small but a candidate is
briefly huge, compute just that candidate wide. Problem 221's product $p(p+1)(p+m)$ approaches
$10^{22}$ for the extreme divisor pair, although every value it keeps is below $10^{17}$. So each
candidate is formed in [`__int128`](/topics/technique/int128) and narrowed only after the bound
test. Problem 259 compares exact rationals by cross-multiplication. The products overflow 64 bits
before the gcd reduction shrinks them, so each one is cast to `__int128` first.

**5. Restrict the domain up front.** If a fast path is only valid in a range, reject inputs
outside it rather than let them corrupt the answer. Problem 421 multiplies residues modulo primes
up to $M$, so it refuses $M \ge 2^{32}$ before starting, and it accumulates the total in
`unsigned __int128`.

## The failure you don't see

Problem 251 is the cautionary case. Its Python test `n1 * n1 * e < room` is always exact. In C
that product silently wrapped for a large divisor of a large $n$, and the overflow quietly
*inflated* the count. Nothing was visible at the main input. The bug only appeared on the larger
benchmark inputs, above $L \approx 1.9 \times 10^8$. Overflow bugs are input-dependent, so a port that
matches Python on the main case has not been shown correct.

Two compiler aids help while testing:
[`__builtin_mul_overflow`](https://gcc.gnu.org/onlinedocs/gcc/Integer-Overflow-Builtins.html) and
its siblings (GCC and Clang) compute the operation and report whether it overflowed, and
`-fsanitize=undefined` traps signed overflow at run time in a test build.

## How to reason about it

- **Find every value that grows.** Products in a search, powers, cross-multiplications, running
  sums, squared bounds. Write down the largest each can reach, at the *largest* test input.
- **Prefer a guard that is also a prune.** In a search the overflow check and the "too big to
  matter" check are often the same comparison, as in 108 and 110, so the guard costs nothing.
- **Never trust a C port on one input.** Run the extra and larger cases against the Python
  oracle. 251's overflow only showed up there.
- **Know your sentinels.** If a helper returns $0$ or $-1$ on overflow, every caller has to
  handle it, and the sentinel must not be a value the computation can legitimately produce.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0484](/solutions/0484/) — Arithmetic Derivative

<!-- /problems -->
