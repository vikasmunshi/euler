<!-- tags: [primorial] -->
<!-- status: final -->
# Primorial

The [primorial](https://en.wikipedia.org/wiki/Primorial) $p_k\#$ is the product of the first $k$
primes: $2, 6, 30, 210, 2310, 30030, \dots$. It is the smallest number with $k$ distinct prime
factors, and that one property makes it the answer whenever a problem rewards *many distinct small
primes per unit of size*. The problems below use it in three ways: as the extremal number for
$n/\varphi(n)$, as the modulus of a wheel that filters out small-prime structure, and as a growth
bound that limits how many primes a number below $N$ can have.

## The idea

Two facts carry most of the weight.

**Ratios depend only on the set of primes.** For Euler's totient,

$$\frac{n}{\varphi(n)} = \prod_{p \mid n} \frac{p}{p - 1},$$

with exponents playing no part. Each new prime multiplies the ratio by $p/(p - 1) > 1$, and the
factor is largest for the smallest $p$. So among all $n \le N$, $n/\varphi(n)$ is maximised by
taking the smallest primes once each. That gives the largest primorial $\le N$, or any number with
the same *radical* (set of primes). The ratio grows only like $e^\gamma \ln \ln n$
([Mertens' third theorem](https://en.wikipedia.org/wiki/Mertens%27_theorems)), so each further
prime buys less:

| $k$ | $p_k$ | $p_k\#$ | $p_k\# / \varphi(p_k\#)$ |
| --- | --- | --- | --- |
| 3 | 5 | 30 | 3.75 |
| 6 | 13 | 30030 | 5.21 |
| 9 | 23 | 223092870 | 6.11 |
| 15 | 47 | $6.1 \times 10^{17}$ | 7.21 |
| 16 | 53 | $3.3 \times 10^{19}$ | 7.35, past $2^{64}$ |

**It grows faster than exponentially.** $\ln p_k\# = \vartheta(p_k) \sim p_k \sim k \ln k$, where
$\vartheta$ is the first [Chebyshev function](https://en.wikipedia.org/wiki/Chebyshev_function). So
below $10^9$ no number has more than nine distinct primes, below $10^{18}$ none has more than 15,
and a signed 64-bit primorial stops at $47\#$.

## Three uses

**The extremal number: 69 and 243.** Problem 69 maximises $n/\varphi(n)$ for $n \le 10^6$. By
the product above, the answer is the largest primorial in range, and the solution is a greedy loop
that multiplies in primes until the next one would overshoot. That is about seven multiplications
in place of a million totients. Problem 243 asks the mirror question with a twist. It wants the
smallest $d$ whose resilience $\varphi(d)/(d - 1)$ is below a threshold. The $\varphi(d)/d$ part is
again driven down only by adding small primes, so the solution grows the primorial until
$\varphi(M)/M$ crosses the threshold. That fixes the radical. But the denominator is $d - 1$, not
$d$, so $M$ itself may still miss. Multiples $kM$ whose factors already divide $M$ keep
$\varphi/d$ unchanged and shrink the $-1$ correction, so the answer is the first such multiple
that clears. The primorial determines the radical, and a small search over multiples handles the
rest. Both comparisons are cross-multiplied integers, $\varphi(M) \cdot b < t \cdot M$, because
the thresholds are close enough that floating-point division is not trustworthy.

**The wheel modulus: 146.** Six values $n^2 + 1, \dots, n^2 + 27$ must be consecutive primes for
$n < 1.5 \times 10^8$. Small primes kill almost every $n$: 2 and 5 force $10 \mid n$, 3 forbids
$3 \mid n$, and 7, 11 and 13 each forbid a few residues of $n^2$. By the
[CRT](/topics/technique/chinese-remainder-theorem), those conditions are exactly a set of allowed
residues modulo $13\# = 30030$, and only about 60 survive. The main loop steps through
$n = r + 30030j$ for those residues only, a 500-fold reduction before any primality test. That
is [wheel factorisation](https://en.wikipedia.org/wiki/Wheel_factorization) aimed at a
polynomial instead of at $n$. A wheel's size is set by its primorial. Adding the next prime
multiplies the table by $p$ and the survivors by the fraction that $p$ allows. 146 stops the wheel
at 13 and handles 17 to 37 with per-prime forbidden-residue lookups instead, because a $37\#$
wheel would have $7 \times 10^{15}$ slots.

**The growth bound: 293.** Admissible numbers have prime factors that are a prefix of
$2, 3, 5, \dots$. The primorial is the smallest admissible number using $k$ primes, so
"$p_k\# \ge 10^9$" is exactly where $k$ stops. The prime pool comes from a running product with no
guessing, and below $10^9$ it is the nine primes up to 23. Enumerating
$2^{a_1} 3^{a_2} \cdots p_k^{a_k}$ with every $a_i \ge 1$ then yields only a few thousand numbers.
The same bound limits the divisor count of a squarefree number below $10^8$ to $2^8$, which is
why 357's C (on [power set](/topics/technique/power-set)) can use a fixed 256-entry array.

## C and Python

- **Overflow at the boundary.** 69's C uses *validate-then-commit*: it computes
  `next = result * candidate` and writes it back only if it is within the limit. The Python
  *commits then undoes*: it multiplies, checks, and divides the last prime back out. Both are
  correct at $10^6$. The C pattern is the one that survives near the top of the type, because it
  never stores an out-of-range product. Near $2^{63}$ even `next` can overflow, so the safe test is
  `result <= limit / candidate`.
- **Where the primes come from.** 69's C trial-divides candidates, since it needs fewer than ten.
  The Python draws from an incremental-sieve generator. 293 builds its pool from a running
  primorial in both languages.
- **Residue tables.** 146's Python keeps the allowed residues in a list and the forbidden
  residues of each larger prime in a `frozenset`. The C uses boolean arrays indexed by residue,
  which removes the hashing. The survivors' Miller–Rabin needs `__uint128_t` products in C. Python
  gets the same from `pow(a, d, n)`.
- **Exact comparisons.** 243 compares $\varphi \cdot b$ against $t \cdot (d - 1)$ in `long long`
  in C and in `int` in Python. At $d \approx 9 \times 10^8$ and $b \approx 10^5$ the products stay
  far below $2^{63}$.

## How to reason about it

- **When only distinct primes matter, the extremum is a primorial.** $n/\varphi(n)$,
  $\varphi(n)/n$ and "most distinct prime factors below $N$" are all maximised or minimised by
  taking the smallest primes once each.
- **The primorial fixes the radical, and a multiple fine-tunes the size.** If an off-by-one in the
  formula ($d - 1$, $d + 1$) spoils the primorial itself, search its multiples with the same
  primes.
- **Size a wheel by its primorial.** Each added prime multiplies the table by $p$. Stop when the
  table outgrows cache, and handle the remaining primes with per-prime residue checks.
- **Use $p_k\#$ as the loop bound.** It ends any enumeration over "the first $k$ primes" without a
  hand-picked limit, and it bounds $\omega(n)$ and $2^{\omega(n)}$ for every $n$ below it.
- **Mind the 64-bit edge.** $47\#$ is the last primorial below $2^{63}$. Test overflow before you
  multiply.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0243](/solutions/0243/) — Resilience
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers

<!-- /problems -->
