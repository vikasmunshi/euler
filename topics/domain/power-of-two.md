<!-- tags: [power-of-two] -->
<!-- status: final -->
# Power of two

A [power of two](https://en.wikipedia.org/wiki/Power_of_two) is $2^k$ for some integer
$k \ge 0$. A machine stores $2^k$ as a single set bit. A problem that defines its objects in terms
of $2^k$ is usually asking one of a handful of questions about it: *is* this a power of two, *how
many* are there below $n$, *which* is the largest one that fits, *what do its digits look like*, or
*how many factors of 2* does a number carry. The problems below each ask one of those questions,
and each answer is a small piece of structure that turns an impossible loop into a short one. The
companion page [binary number](/topics/domain/binary-number) reads $n$ *as* a sum of powers of
two, its digits. This page is about the power itself.

## The idea — six questions about $2^k$

| question | answer | cost |
|---|---|---|
| is $n$ a power of two? | `n & (n - 1) == 0` (for $n > 0$) | $O(1)$ |
| how many $2^j \le n$? | $\lfloor \log_2 n \rfloor + 1$, i.e. the [bit length](/topics/technique/bit-length) of $n$ | $O(1)$ |
| largest $2^j \le n$? | the top bit of $n$ | $O(1)$ |
| how many subsets of an $n$-set? | $2^n$, mod $m$ by [modular exponentiation](/topics/technique/modular-exponentiation) | $O(\log n)$ |
| leading digits of $2^j$? | the fractional part of $j \log_{10} 2$ | needs high-precision logs |
| how many factors of 2 in $n$? | the [2-adic valuation](/topics/domain/p-adic-valuation) $v_2(n)$, the trailing zero count | $O(1)$ |

The first three are bit tricks. What makes them useful is the *banding* they imply. Between two
consecutive powers of two, $[2^p, 2^{p+1})$, every quantity that depends only on
$\lfloor\log_2 n\rfloor$ is constant. So a scan over $n$ can jump a whole band at a time. The last
three are where the real mathematics sits: [double counting](https://en.wikipedia.org/wiki/Double_counting_(proof_technique))
over subsets, [equidistribution](/topics/domain/equidistributed-sequence) of $j\log_{10}2$, and
[Kummer's theorem](/topics/domain/kummers-theorem) for $v_2$ of a binomial coefficient.

## Powers of two as a sparse set — count them, band them

**Problem 207** reduces $4^t = 2^t + k$ to $k = n(n-1)$ with $n = 2^t$ a positive integer. A
partition is *perfect* exactly when $t$ is an integer, i.e. when $n$ is a power of two. The
proportion of perfect partitions below a threshold is then (powers of two in $[2, n]$) over
$(n - 1)$, and the numerator is $\lfloor \log_2 n \rfloor$. The solution never tests individual
$n$ for being a power of two. Inside a band $[2^p, 2^{p+1})$ the numerator is frozen at $p$, so the
first qualifying $n$ in the band has a closed form. The loop walks $p$, a few dozen bands, instead
of walking $n$, and the first band that admits a solution gives the minimum.

That is the general lesson. Powers of two are logarithmically sparse, so anything counted by "how
many powers of two lie below $n$" is a step function with $\log_2 N$ steps. Iterate over the
steps.

**Problem 293** uses powers of two in a smaller way. The admissible numbers are those whose
distinct prime factors are the first $k$ primes, with each exponent at least 1. The $k = 1$ family
is exactly the powers of two, and every admissible number is even. That evenness is all the gap
search needs: $N + 2$ is even, so the first candidate is $M = 3$ and the search steps by 2.

## $2^n$ as a count — subsets

$2^n$ is the number of subsets of an $n$-element set. Fixing some elements *in* and some *out*
leaves a smaller power of two. **Problem 944** sums a statistic over all $2^{n}$ subsets of
$\{1..n\}$ with $n = 10^{14}$. [Double counting](https://en.wikipedia.org/wiki/Double_counting_(proof_technique))
by element turns it around: $x$ is in $2^{n-1}$ subsets, and in $2^{n-1-k}$ of them its $k$ proper
multiples are all absent. The whole problem becomes a sum of terms
$x \cdot 2^{\,n - \lfloor n/x \rfloor}$. The exponent is constant on
[divisor blocks](/topics/technique/dirichlet-hyperbola-method), so the work is one modular power
per block. The power of two here is never written out; it lives only as $2^e \bmod m$.

The two languages part ways on that modular power. C calls a scalar square-and-multiply `powmod`
once per block, with an `unsigned __int128` product because $m^2$ sits close to $2^{63}$. Python
cannot afford $2\cdot 10^7$ calls to `pow(2, e, m)` from a Python loop. It builds the array of
exponents and runs square-and-multiply *over the exponent bits* instead: about 47 iterations, each
one masked `int64` array multiply (`result[odd] = result[odd] * base % m`). The pairing works
because $m^2 < 2^{63}$, so `int64` never overflows. The same trick fails silently for a larger
modulus, so the bound is stated in the code.

## $2^j$ as a magnitude — leading digits

**Problem 686** asks for the $n$-th $j$ such that $2^j$ begins with given digits $L$. The digits of
$2^j$ are fixed by the fractional part of $j\log_{10} 2$. So "starts with $L$" means
$\{j\alpha\} \in [\{\log_{10} L\},\ \{\log_{10}(L+1)\})$, where $\alpha = \log_{10}2$ is
irrational and the sequence $\{j\alpha\}$ is [equidistributed](/topics/domain/equidistributed-sequence).
The hit count up to $J$ is a difference of two [floor sums](/topics/technique/floor-sum-algorithm),
and a [binary search](/topics/technique/binary-search-algorithm) on $J$ finds the $n$-th hit. It
never computes $2^j$, which at $j$ in the billions would have hundreds of millions of digits even
for Python.

The difficulty is precision. Each boundary must be right to more digits than $J$ has, and the
languages solve that differently:

- **Python** scales every log by $Q = 10^{100}$ and works in exact big integers. The constants
  come from a `Decimal` artanh series, $\ln 2 = 2\,\mathrm{artanh}(1/3)$, expanded around the
  nearest power of two so the series converges fast. A second solution takes them from `mpmath`
  instead.
- **C** has only `__int128`, about $1.7\cdot10^{38}$. Scaling $\log_{10}$ values by $10^{100}$ is
  impossible, and cross-multiplying would overflow. So it moves to *ln*-space with a scale of
  $10^{25}$. The floor-sum denominator becomes $\ln 10$ itself, and the largest intermediate,
  about $\ln 10 \cdot J$ scaled, still fits. Same algorithm, with the precision budget worked out
  by hand.

## $2^k \mid n$ — the 2-adic valuation

The largest power of two dividing $n$ is $2^{v_2(n)}$, and $v_2$ is the trailing-zero count.
**Problem 704** maximises $v_2\binom{n}{m}$ over $m$. [Kummer's theorem](/topics/domain/kummers-theorem)
says that valuation is the number of carries when $m + (n-m)$ is added in binary, which equals
$s_2(m) + s_2(n-m) - s_2(n)$ with $s_2$ the popcount. The maximum then depends only on $n$'s bit
length and popcount. So the sum over $n \le 10^{16}$ falls into the bands $[2^{k-1}, 2^k)$ again:
one closed-form term per complete band, plus a partial top band whose popcount total is read off
$M + 1$. The [p-adic valuation](/topics/domain/p-adic-valuation) page covers the general prime.
For $p = 2$ the arithmetic becomes bit counting.

Python's `int.bit_count()` and `bit_length()` are built in. The C port writes both as shift
loops. `__builtin_popcountll` and `__builtin_clzll` would do the same job, but each is called once
on a 54-bit number, so the choice is cosmetic.

## The largest power that fits — greedy

**Problem 872**'s tree has a closed-form parent rule: node $k$'s parent is $k$ plus the largest
power of two $\le n - k$. That greedy step clears one bit per move, so the climb is popcount long.
The [binary number](/topics/domain/binary-number) page treats it in full, including the
`bit_length` / `__builtin_clzll` table. The power-of-two content is the primitive *largest
$2^j \le x$*: `1 << (x.bit_length() - 1)` in Python and `1ULL << (63 - __builtin_clzll(x))` in C,
undefined at $x = 0$.

## Pitfalls

- **Shift width in C.** `1 << p` is an `int`. Use `1LL << p`, and keep $p \le 62$ for a signed
  result: `1LL << 63` overflows. Problem 207's C loop bounds `p < 63` for exactly this reason.
  Python's `1 << p` has no ceiling.
- **Never test with floating `log2`.** `log2(n).is_integer()` misfires once $n$ exceeds $2^{53}$,
  where doubles stop being exact. Use `n & (n - 1) == 0`, or better, avoid the test by banding.
- **$2^n$ is not the thing to compute.** In every problem here the actual power is either
  astronomically large (944, 686) or a single bit. Carry its exponent, its residue mod $m$, or
  its logarithm, never its value.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0494](/solutions/0494/) — Collatz Prefix Families
- ○ [0499](/solutions/0499/) — St. Petersburg Lottery
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ● [0872](/solutions/0872/) — Recursive Tree
- ○ [0890](/solutions/0890/) — Binary Partitions
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ● [0944](/solutions/0944/) — Sum of Elevisors

<!-- /problems -->
