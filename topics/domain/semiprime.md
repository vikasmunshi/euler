<!-- tags: [semiprime] -->
<!-- status: final 2026-10-19T06:39Z -->
# Semiprime

A [semiprime](https://en.wikipedia.org/wiki/Semiprime) is a product of exactly two primes,
$n = pq$, not necessarily distinct ([OEIS A001358](https://oeis.org/A001358)). It is the simplest
composite structure, and that is why it keeps appearing. Every multiplicative quantity of a
semiprime is a short expression in $p$ and $q$. So a question about $n$ becomes a question about
a pair of primes, and the pair can be *enumerated directly* instead of found by scanning and
factoring every $n$. The three solved problems below use that in three ways: a closed-form totient
(70), counting with the prime-counting function (187), and turning a divisibility condition into
a search over divisors (245).

## The idea — enumerate the pair, not the number

For $n = pq$ with $p \ne q$, the multiplicative functions collapse:

| quantity | general | semiprime $pq$ |
|---|---|---|
| [totient](/topics/domain/eulers-totient-function) $\varphi(n)$ | $n\prod(1 - 1/p)$ | $(p-1)(q-1)$ |
| $n - \varphi(n)$ | — | $p + q - 1$ |
| $n / \varphi(n)$ | $\prod p/(p-1)$ | $\frac{p}{p-1}\cdot\frac{q}{q-1}$ |
| divisors | $\prod(e_i + 1)$ | $1, p, q, pq$ |

Each of these is a function of two primes, so the search space is the set of prime pairs with
$pq \le N$. Under the canonical order $p \le q$, the smaller factor satisfies $p \le \sqrt N$
and every semiprime appears exactly once. Iterating over $p$ up to $\sqrt N$, and over $q$ in a range
fixed by $p$, replaces a scan of $N$ integers with work governed by $\pi(\sqrt N)$ outer steps.

Semiprimes are also extreme cases, and that is the other reason they show up. Among composites,
they have the fewest prime factors, so they come closest to primes in
quantities like $n/\varphi(n)$. They are also the base case of any recursion on the number of
prime factors. This is the structure behind
[RSA](/topics/domain/rsa-cryptosystem): $\varphi(pq)$ is easy to compute when $p$ and $q$ are
known and hard when they are not.

## Three uses across the problems

**70, totient permutation: the semiprime is the optimum.** Minimise $n/\varphi(n)$ over
$n < 10^7$ with $\varphi(n)$ a digit permutation of $n$. Since $n/\varphi(n) = \prod p/(p-1)$, each
distinct prime factor increases the ratio, and small ones increase it most. A prime is ruled out:
$\varphi(p) = p - 1$ has a different digit sum mod 9 from $p$. So the best candidates
are semiprimes with both factors near $\sqrt{10^7}$, whose totient $(p-1)(q-1)$ needs no
factorisation. The search covers a narrow band of prime pairs. In outline, the public Python is:

```python
for prime_1 in (p for p in primes_generator() if p > min_prime_1):
    if prime_1 > max_prime_1:
        break
    min_prime_2, max_prime_2 = (prime_1 + 2, int(limit / prime_1))
    for prime_2 in (p for p in primes_generator() if p > min_prime_2):
        ...
        number, totient = prime_1 * prime_2, (prime_1 - 1) * (prime_2 - 1)
```

**187, semiprimes: count the second factor with $\pi$.** How many $n < 10^8$ are semiprimes? Fix
the smaller prime $p$ (so $p^2 < N$). The partner $q$ is any prime in $[p, (N-1)/p]$, which is
$\pi((N-1)/p) - \pi(p - 1)$ choices. Summing over $p$ gives the count, with no product ever formed.
The solution uses a property of a sorted prime array: the index of the $i$-th prime *is* $\pi(p-1)$,
and $\pi$ at any other point is a [binary search](/topics/technique/binary-search-algorithm) for
its insertion point. One [sieve](/topics/technique/primesieve) to $N/2$ is the whole cost. See
[prime-counting function](/topics/domain/prime-counting-function).

**245, coresilience: a divisibility condition becomes a divisor search.** The condition is
$(n - \varphi(n)) \mid (n - 1)$. A short argument shows that $n$ must be
[square-free](/topics/domain/square-free-integer). The semiprime case is then the bulk of the
answer, and the closed forms carry it: $(p + q - 1) \mid (pq - 1)$. Reducing modulo $p + q - 1$,
where $q \equiv 1 - p$, gives the equivalent condition $(p+q-1) \mid (p^2 - p + 1)$. The
cofactor $e = (p^2-p+1)/(p+q-1)$ then *determines* $q$, and $q > p$ forces $e < p/2$. So the
solution walks moduli $e$ and the roots of $x^2 - x + 1 \equiv 0 \pmod e$, built with a primitive
cube root of unity, [Hensel lifting](/topics/technique/hensels-lemma) and CRT. It
reads off each $q$ and checks it with [Miller–Rabin](/topics/technique/miller-rabin-primality-test),
because $q$ can be far beyond the sieve. Composites with three or more prime factors use the same
"solve for the last prime" idea, applied to a pruned prefix search.

**278, linear combinations of semiprimes**, not yet solved here, uses the generators $pq, pr, qr$
of a numerical semigroup. Their [Frobenius number](/topics/domain/frobenius-number) has a closed
form in $p, q, r$ because of the same shared-factor structure.

## Python and C

- **70**: Python draws primes from an unbounded incremental sieve (a `dict` of next composites) and
  tests permutations with `sorted(str(n)) == sorted(str(phi))`. C sieves once into a flat array and
  compares digits with a 10-bucket counter: increment for $n$'s digits, decrement for $\varphi$'s,
  and expect all zeros. That avoids allocating any strings.
- **187**: Python does the whole sum with NumPy and no loop. One `searchsorted` finds the small-prime
  cut-off, `(limit - 1) // small` gives every upper bound as a vector, a second `searchsorted` gives
  every $\pi$, and `np.arange` subtracts the indices. C calls the primesieve C API and runs a
  hand-written `upper_bound` once per small prime. It finds the cut-off by binary search on
  `p * p < limit`, so no floating-point square root is involved.
- **245**: the prefix-bound products $m p^2$ that the pruning test exists to reject are exactly the ones that
  overflow `int64`, so C evaluates them in `__int128`. It also uses `__int128` in the Miller–Rabin
  multiply that Python gets from `pow(a, d, n)`.

## How to reason about it

- **When $n$'s factorisation drives the answer, generate $n$ from its factors.** For semiprimes that
  means a double loop over primes with $p \le \sqrt N$, not a factorisation of each $n$.
- **Fix the smaller factor.** The order $p \le q$ makes each semiprime unique and bounds the outer
  loop by $\sqrt N$. The inner range is then an interval of primes, which $\pi$ can count without listing.
- **Substitute the closed form into the condition.** Write $\varphi$, $n - \varphi$ or the divisor
  sum in $p, q$ and simplify. A congruence often reduces it to "$q$ is determined by a divisor of a
  polynomial in $p$" (245), and the search collapses.
- **Expect semiprimes at extremes.** When an objective penalises each prime factor, as $n/\varphi(n)$
  does, the optimum among composites has two large ones.
- **The second factor can be large.** $q$ reaches $N/p$, beyond a $\sqrt N$ sieve. Either sieve to
  $N/2$ (187) or test $q$ with Miller–Rabin (245), and watch the product width in C.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0245](/solutions/0245/) — Coresilience
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes

<!-- /problems -->
