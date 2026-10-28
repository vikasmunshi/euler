<!-- tags: [prime-factor] -->
<!-- status: final 2026-10-28T08:03Z -->
# Prime factor

The [prime factorization](/topics/domain/prime-factorization) page is about the whole exponent
vector of $n$. This page is about two entries in it: the **smallest** prime factor,
$\operatorname{lpf}(n)$, and the **largest**, $P(n)$. They keep coming back because, of all the
information in a factorization, they are the two that split $n$ into "the part below $p$" and "the
part at $p$" — and once you can do that, you stop handling integers one at a time and start handling
them in bulk. Problem 3 asks for $P(n)$ of a single number; problems 642 and 521 ask for $\sum P(n)$
and $\sum \operatorname{lpf}(n)$ over every $n$ up to $10^{11}$ and beyond, and that change of scale
is what the rest of this page is about.

## The two extremes are not symmetric

Two elementary facts, each one line, drive almost everything:

- **A composite $n$ has $\operatorname{lpf}(n) \le \sqrt{n}$.** The smallest prime factor is always
  *small*: [trial division](/topics/technique/trial-division) up to $\sqrt n$ finds it for one
  number, and a smallest-prime-factor table from a
  [sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) or a
  [linear sieve](/topics/technique/linear-sieve) finds it for every $n$ in a range — and then
  factors any of them in $O(\log n)$ by repeated division.
- **$n$ has at most one prime factor $> \sqrt{n}$.** The largest prime factor is usually *large*,
  appears to the first power, and leaves a small cofactor behind.

The public solution to problem 3 uses both at once. It divides out factors in increasing order, so
each divisor that hits is the current smallest prime factor; and because the search ceiling is
recomputed from the shrinking remainder, the loop stops as soon as what is left has no factor below
its own square root — at which point the remainder *is* $P(n)$:

```python
while remaining_number > 1 and current_factor <= search_limit:
    if remaining_number % current_factor == 0:
        remaining_number = reduce(remaining_number, current_factor)
        largest_factor = current_factor
        search_limit = int(remaining_number**0.5)
    current_factor += 2
return str(remaining_number if remaining_number > 1 else largest_factor)
```

That is the single-number picture. For billions of numbers it is the wrong tool: you never factor
anything, you *group by the extreme factor*.

## Group by the largest: $n = m \cdot P(n)$

Every $n \ge 2$ factors uniquely as $n = m \cdot p$ with $p = P(n)$ and $m$ a
[$p$-smooth](/topics/domain/smooth-number) cofactor (every prime of $m$ is $\le p$). Read
backwards, that is a bijection: pick a prime $p$ and any $p$-smooth $m$, and $mp$ is a number whose
largest prime factor is exactly $p$. Questions about $P(n)$ over a range become sums over pairs
$(m, p)$, and the second fact above says which side of the pair is cheap to enumerate:

- When $p > \sqrt N$, the cofactor $m < \sqrt N$ is small, and the smoothness condition on it is
  automatic because $m < p$. For a fixed $m$, the valid $p$ fill a contiguous run of primes ending
  at $\lfloor N/m \rfloor$, so the whole group costs one lookup of a prime *count* or prime *sum*.
- When $p \le \sqrt N$, the numbers are comparatively rare (smooth numbers thin out fast), and a
  depth-first walk over factorization shapes — peel primes in non-decreasing order, recurse on the
  quotient — reaches them directly.

Problem 642 ($\sum_{n \le N} P(n)$) is exactly this: the large-$p$ groups are prime sums over
intervals, the small-$p$ part is the DFS. Problem 668 asks how many $n \le 10^{10}$ are *square-root
smooth* ($P(n) < \sqrt n$), and the bijection makes the complement trivially countable:
$P(n)^2 \ge n$ means $p^2 \ge mp$, i.e. $m \le p$, and every $m \le p$ is automatically $p$-smooth.
So the failures are just the pairs with $m \le \min(p, N/p)$ — a sum of $p$ over the small primes
plus a sum of $\lfloor N/p \rfloor$ over the large ones. No smoothness test survives into the code.

Either way the problem collapses onto one primitive: $\pi(v)$ (and, for 642, the sum of primes
$\le v$) at every $v = \lfloor N/k \rfloor$. There are only about $2\sqrt N$ such values — the
[quotient blocking](/topics/technique/quotient-blocking) observation — and the
[Meissel–Lehmer](/topics/domain/meissel-lehmer-algorithm) family, in its Lucy_Hedgehog form,
produces all of them in roughly $O(N^{3/4})$ time and $O(\sqrt N)$ memory. That pairing is why 642
and 668 sit on both pages: $P(n)$ supplies the decomposition, the
[prime-counting function](/topics/domain/prime-counting-function) supplies the arithmetic.

## Group by the smallest: the sieve's own invariant

The smallest prime factor is the dual view, and it is hiding inside the very sieve that solves the
largest-factor problems. Lucy's update

$$S(v) \leftarrow S(v) - \bigl(S(\lfloor v/p \rfloor) - S(p-1)\bigr) \qquad (v \ge p^2)$$

removes, at step $p$, precisely the composites $\le v$ whose **smallest** prime factor is $p$; after
the last prime $\le \sqrt v$, only primes remain. Weight each removed block by $p$ instead of
discarding it and you are summing $\operatorname{lpf}(n)$ — which is what problem 521 asks — and the
[Min_25 sieve](/topics/technique/min-25-sieve) generalises the same bookkeeping to arbitrary
multiplicative weights. So "largest" and "smallest" are not two techniques: the sieve walks numbers
by their smallest prime, and the $m \cdot p$ split reads them by their largest.

## When the number is too big to touch: test primes, not $n$

Problem 132 turns the question around. It wants the smallest prime factors of the
[repunit](/topics/domain/repunit) $R(10^9)$, a number with a billion digits that can never be
written down, let alone factored. But "smallest prime factors" only needs the primes in increasing
order and a yes/no for each: a prime $p \ge 7$ divides $R(k) = (10^k - 1)/9$ exactly when
$10^k \equiv 1 \pmod p$ — when the [multiplicative order](/topics/domain/multiplicative-order) of
$10$ divides $k$ — and one [modular exponentiation](/topics/technique/modular-exponentiation)
answers that in $O(\log k)$. Scan sieved primes upward and stop at the count you need. The small
prime factors of a structured giant are found by scanning primes against it, never by dividing
it — the same asymmetry as before, seen from the other side.

## How to reason about it

- **Ask which extreme the problem is about.** "Smallest" means the factor is $\le \sqrt n$ and a
  sieve or a prime scan finds it; "largest" means it is probably $> \sqrt n$, appears once, and
  leaves a small cofactor worth enumerating.
- **Over a range, never factor.** Rewrite $n = m \cdot P(n)$ (or sort by $\operatorname{lpf}$) and
  turn the sum into prime counts or prime sums at the $\lfloor N/k \rfloor$ points. If you find
  yourself sieving all the way to $10^{10}$, you have missed the regrouping.
- **Know the densities.** By [Dickman's function](https://en.wikipedia.org/wiki/Dickman_function),
  the fraction of $n \le x$ with $P(n) \le x^{1/u}$ tends to $\rho(u)$; for $u = 2$ that is
  $1 - \ln 2 \approx 0.31$. It tells you up front how much of the range the "large $p$" branch owns,
  and gives a rough plausibility check on any count you produce.
- **Mind the boundaries.** $1$ has no prime factor and belongs to neither side; strict versus
  non-strict ($P(n) < \sqrt n$ against $\le$) flips the squares of primes; and in the $m \cdot p$
  enumeration the run of admissible $p$ starts at the cofactor's own largest prime, not above it.
  A brute-force cross-check up to $10^6$ catches all three.
- **Under a modulus, differences go negative.** Isolating a prime interval as $S(b) - S(a)$ after
  reducing mod $M$ can leave a negative residue; add $M$ before the final reduction.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0132](/solutions/0132/) — Large Repunit Factors
- ○ [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0526](/solutions/0526/) — Largest Prime Factors of Consecutive Numbers
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0829](/solutions/0829/) — Integral Fusion
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers

<!-- /problems -->
