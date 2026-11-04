<!-- tags: [prime-factor] -->
<!-- status: final -->
# Prime factor

The [prime factorization](/topics/domain/prime-factorization) page is about the whole exponent
vector of $n$. This page is about two entries in it: the **smallest** prime factor,
$\operatorname{lpf}(n)$, and the **largest**, $P(n)$. They keep coming back because, of all the
information in a factorization, they are the two that split $n$ into "the part below $p$" and "the
part at $p$" — and once you can do that, you stop handling integers one at a time and start handling
them in bulk. Problem 3 asks for $P(n)$ of a single number; problems 642 and 521 ask for $\sum P(n)$
and $\sum \operatorname{lpf}(n)$ over every $n$ up to $10^{11}$ and beyond; problem 779 averages over
every integer there is. That change of scale is what the rest of this page is about, along with what
happens when the numbers stop being a range (659) and when the cut falls at a prime you pick rather
than one $n$ picks (967).

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
the last prime $\le \sqrt v$, only primes remain. Problem 521 asks for $\sum \operatorname{lpf}(n)$,
and that sentence is nearly the whole solution. With $S$ counting survivors, the block struck from
$S(N)$ at step $p$ *is* the set of composites with smallest factor $p$, so $p$ times its size, read
before the step runs, is their entire contribution. The primes are their own smallest factors, and a
[sum table carried alongside the count](/topics/takeaway/carry-sums-alongside-counts) supplies them
at the end. The result was never in the sieve's final table: it is in the states the table passes
through, one entry read per prime
([worked through here](/topics/number-theory/summing-multiplicative-functions)). The
[Min_25 sieve](/topics/technique/min-25-sieve) generalises the same bookkeeping to arbitrary
multiplicative weights. So "largest" and "smallest" are not two techniques: the sieve walks numbers
by their smallest prime, and the $m \cdot p$ split reads them by their largest.

## Group by the smallest, with no $N$ at all

Take that invariant to the limit. Problem 779 wants the mean, over all integers, of a weight built
from $\operatorname{lpf}(n)$ and its exponent, so there is no $N$ to sieve to and no table to read.
What replaces the table is the [natural density](/topics/domain/natural-density) of each class. An
integer has smallest prime $p$ when $p$ divides it and no smaller prime does, and divisibility by
distinct primes is independent in the limit, by the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem):

$$\operatorname{dens}\{n : \operatorname{lpf}(n) = p\} = \frac{1}{p} \prod_{q < p} \Bigl(1 - \frac{1}{q}\Bigr).$$

Read it as the sieve again. The product is the fraction of integers still standing when the sieve
reaches $p$, and $1/p$ is the share of those that step strikes. Each class is the drop in that
survivor product from one prime to the next, so the classes telescope to a total of 1, as a partition
of the integers must. Inside a class, each further factor of $p$ is one more independent event of
probability $1/p$, so the exponent is [geometric](https://en.wikipedia.org/wiki/Geometric_distribution).

The effect is that a mean over every integer becomes a single series over the primes. The problem's
outer sum over a parameter folds in first, by
[swapping the order of summation](/topics/technique/interchange-of-summation), and what is left
falls off so fast that a modest list of primes finishes it. The cost is the length of that prime
list, not anything to do with integers. The catch moves to the output, which is now a real number.
The truncation has to be judged against the distance to the nearest rounding boundary, not against
the digits requested, and 779's value happens to sit close to one, so both the tail and the
[accumulated rounding error](/topics/technique/floating-point-arithmetic) have to be held below that
gap.

## When the numbers are not a range: sieve the values, read the leftover

The bijection $n = m \cdot P(n)$ pays off only because the $n$ fill an interval, so that every pair
$(m, p)$ lands on a member. Problem 659 removes that. A prime dividing two successive terms of
$n^2 + k^2$ divides their difference $2n + 1$, and substituting back shows it divides $4k^2 + 1$, so
the problem is $P(4k^2 + 1)$ for every $k \le 10^7$: ten million numbers scattered up to
$4 \times 10^{14}$. A prime count at $\lfloor N/m \rfloor$ cannot tell you which of them exist, so
the regrouping has nothing to hold on to. This is the one place on the page where you really do factor
everything, but together rather than one at a time.

Two things make that affordable. The first is a
[polynomial sieve](/topics/technique/polynomial-sieve). $p \mid 4k^2 + 1$ is a congruence on $k$ with
two roots when $-1$ is a [quadratic residue](/topics/technique/quadratic-residue) mod $p$ and none
otherwise, so only primes $p \equiv 1 \pmod 4$ take part, and each walks two arithmetic progressions
through the array of values, just as Eratosthenes walks one through the integers.

The second is the elementary fact from the top of this page, used as a stopping rule. Any two primes
above $2N + 1$ multiply past every value, so the sieve stops there, and what is left in a cell is $1$
or a single prime. That leftover is $P$, because it exceeds everything already stripped; if the cell
reached $1$, then $P$ is the last prime that touched it, since primes arrive in increasing order, and
one overwrite per hit records it with no comparison. This is the last line of the problem 3 loop,
applied to an array. It is also why [Hensel lifting](/topics/technique/hensels-lemma) to the prime
powers is not an optional refinement: a factor of $p$ left behind would make a composite leftover
pass for a large prime.

Problem 632 runs the same rule more cheaply. It needs $\omega(d)$ for the square-free $d \le 10^8$,
sieves with the primes up to $10^4$ alone, and keeps a running product of the primes that hit each
$d$. If the product falls short of $d$, exactly one large prime is missing, and the problem never
needs to know which. One comparison replaces millions of slice operations. So the leftover rule
comes in two strengths: divide, when you need the prime itself, and compare, when you only need to
know it is there. (The other half of 632, getting "exactly $k$" from "at least $j$", is on the
[factorization](/topics/domain/prime-factorization) page.)

## Cut at a bound: small primes repeat, large primes are rare

Smallest and largest split $n$ at a prime that $n$ chooses. Problem 967 splits at one you choose. It
scores each $n \le 10^{18}$ by its distinct primes up to $B = 120$, so primes above $B$ are invisible
and the question is only which of a fixed list divide $n$. That has a property no question about
$P(n)$ has: whether a fixed $p$ divides $n$ depends only on $n \bmod p$, so for a set of primes with
product $Q$ the pattern is [periodic](/topics/domain/periodic-sequence) in $n$ with period $Q$. The
seven smallest primes that matter have $Q \approx 3.2 \times 10^6$, one table over one period holds
everything about them, and a [prefix sum](/topics/technique/prefix-sum) over it answers any partial
sum up to $10^{18}$ in $O(1)$.

The remaining primes are handled the opposite way. Their products are sparse, so they can be
enumerated: about $1.4 \times 10^6$ square-free products below $N$. The
[multiplicative function](/topics/domain/multiplicative-function) page has the convolution that joins
the two halves and the ring that carries the residues. The point here is the shape of the split: it
echoes the $\sqrt N$ split above, but for a different reason. Small primes are dense, so use their
regularity; large primes are rare, so list them. And the cut is a dial set by how big a table you can
afford, not a fixed $\sqrt N$.

The period depends on the question seeing only *distinct* primes. The exact power of 2 dividing $n$
has no period at all, so a question that reads exponents, as 632 and 779 do, gets no such table.

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
- **Over a full range, never factor.** Rewrite $n = m \cdot P(n)$ (or sort by $\operatorname{lpf}$)
  and turn the sum into prime counts or prime sums at the $\lfloor N/k \rfloor$ points. If you find
  yourself sieving all the way to $10^{10}$, you have missed the regrouping. A sparse set is the
  exception: for the values of a polynomial, sieve at the roots and stop at the square root of the
  largest value.
- **Ask what the question can see.** Only primes below a bound, and only whether they divide: the
  problem is periodic, and a table over one period replaces those primes. No bound on $n$ at all:
  it is a density, and the answer is a series over primes.
- **Know the densities.** By [Dickman's function](https://en.wikipedia.org/wiki/Dickman_function),
  the fraction of $n \le x$ with $P(n) \le x^{1/u}$ tends to $\rho(u)$; for $u = 2$ that is
  $1 - \ln 2 \approx 0.31$. It tells you up front how much of the range the "large $p$" branch owns,
  and gives a rough plausibility check on any count you produce. The smallest-prime density above is
  a limit at *fixed* $p$, so do not push it to a $p$ that grows with $N$: by
  [Mertens' third theorem](https://en.wikipedia.org/wiki/Mertens%27_theorems) the product up to
  $\sqrt x$ is about $1.12/\ln x$, not the true prime density $1/\ln x$.
- **Mind the boundaries.** $1$ has no prime factor and belongs to neither side; strict versus
  non-strict ($P(n) < \sqrt n$ against $\le$) flips the squares of primes; and in the $m \cdot p$
  enumeration the run of admissible $p$ starts at the cofactor's own largest prime, not above it.
  A brute-force cross-check up to $10^6$ catches all three.
- **Under a modulus, differences go negative.** Isolating a prime interval as $S(b) - S(a)$ after
  reducing mod $M$ can leave a negative residue; add $M$ before the final reduction. And test for
  zero before you reduce: problem 632 multiplies its non-zero counts, and a count that happens to be
  a multiple of $M$ is still non-zero.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0526](/solutions/0526/) — Largest Prime Factors of Consecutive Numbers
- ● [0632](/solutions/0632/) — Square Prime Factors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers

<!-- /problems -->
