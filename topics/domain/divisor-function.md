<!-- tags: [divisor-function] -->
<!-- status: final 2026-10-14T07:14Z -->
# Divisor function

The [divisor function](https://en.wikipedia.org/wiki/Divisor_function)
$\sigma_k(n) = \sum_{d \mid n} d^k$ adds up the $k$-th powers of the divisors of $n$. Two cases do
almost all the work: $\sigma_0(n) = d(n)$ (also written $\tau(n)$), which *counts* the divisors, and
$\sigma_1(n) = \sigma(n)$, which *sums* them. Its relative $s(n) = \sigma(n) - n$, the sum of the
*proper* divisors, sits behind [perfect](/topics/domain/perfect-number),
[abundant](/topics/domain/abundant-number) and [amicable](/topics/domain/amicable-numbers) numbers.
The function keeps coming back in the problems below because it is the simplest arithmetic
quantity that depends on a number's *factorisation* rather than its size: 48 has ten divisors and
47 has two. Asked about divisors, the useful question is never "what are they?" but "what is
the factorisation?". Once the factorisation is in hand, the formula does the rest.

## The idea: one formula, from the factorisation

The divisors of $n = p_1^{a_1} p_2^{a_2} \cdots p_r^{a_r}$ are exactly the numbers
$p_1^{b_1} \cdots p_r^{b_r}$ with $0 \le b_i \le a_i$. Each exponent is chosen independently, so
both the count and the sum split prime by prime:

$$d(n) = \prod_i (a_i + 1), \qquad
\sigma_k(n) = \prod_i \left(1 + p_i^k + p_i^{2k} + \dots + p_i^{a_i k}\right)
= \prod_i \frac{p_i^{(a_i+1)k} - 1}{p_i^k - 1}.$$

This is the statement that $\sigma_k$ is a [multiplicative function](/topics/domain/multiplicative-function):
$\sigma_k(mn) = \sigma_k(m)\,\sigma_k(n)$ whenever $\gcd(m, n) = 1$. Each prime-power factor is a
[geometric series](/topics/technique/geometric-series). Nearly every problem on this page uses that
identity in one of four ways.

**1. Split a number into coprime parts.** Problem 12 wants the first triangular number
$T_i = i(i+1)/2$ with more than 500 divisors. Consecutive integers are coprime, so once the factor
of 2 is assigned to whichever of $i$ or $i+1$ is even, $d(T_i)$ is the product of two divisor counts
on numbers about $\sqrt{2T_i}$ in size, not one count on $T_i$:

```python
if i % 2 == 0:
    divisor_count = num_factors(i // 2) * num_factors(i + 1)
else:
    divisor_count = num_factors(i) * num_factors((i + 1) // 2)
```

**2. Turn a counting question into $d$ of something.** The equation $\tfrac1x + \tfrac1y = \tfrac1n$
of problems 108 and 110 rearranges to $(x - n)(y - n) = n^2$. Its solutions are therefore the
factor pairs of $n^2$, and there are $\lceil d(n^2)/2 \rceil$ of them up to order. Because
$d(n^2) = \prod (2a_i + 1)$, "at least $N$ solutions" becomes a condition on an exponent vector, and
the search runs over exponent *shapes*, not over $n$: the smallest $n$ for a shape puts the
largest exponents on the smallest primes. Several of the geometry problems tagged here (176, 827)
take the same route once a Pythagorean or Diophantine parametrisation reduces them to counting
divisors.

**3. Invert the formula: from a divisor count back to shapes.** $d(k) = 8$ means
$\prod (a_i + 1) = 8$, and the factorisations $8 = 4 \cdot 2 = 2 \cdot 2 \cdot 2$ give exactly three
disjoint shapes, $p^7$, $p^3 q$ and $pqr$. That decomposition is the whole combinatorial content of
problem 501; what is left is prime counting at scale. Problem 500 runs the same inversion the
other way: the smallest number with $2^{500500}$ divisors is built greedily from factors
$p^{2^j}$, each of which doubles the count, always taking the smallest one available.

**4. Reason about $\sigma$ one prime power at a time.** Divisibility and ratio conditions on
$\sigma$ factor too. A prime $q$ divides $\sigma(n)$ exactly when it divides some
$\sigma(p^a) = 1 + p + \dots + p^a$, which is how problem 565 reduces "2017 divides $\sigma(i)$" to
conditions on the individual prime powers of $i$. The
[abundancy index](/topics/domain/abundancy-index) $\sigma(n)/n = \prod \sigma(p^a)/p^a$ is a product
of factors each strictly greater than 1, so problem 241 searches factorisations depth-first and
prunes as soon as the running ratio can no longer reach its target. Problem 650 never builds its
astronomically large product of binomials: it tracks the prime-exponent vector with
[Legendre's formula](/topics/domain/legendres-formula) and evaluates $\sigma$ as one geometric
series per prime.

## Computing it for every $n$ at once

When a problem needs $d(n)$ or $\sigma(n)$ for *all* $n$ up to a bound, factoring each number
separately is the slow path. A [divisor-sum sieve](/topics/technique/divisor-sum-sieve) turns the
question around: rather than asking which numbers divide $n$, let each $i$ add itself to every one
of its multiples. Problem 95 does this for $s(n)$, the proper-divisor sum (21 and 23 are the
small versions of the same loop):

```python
for i in range(1, max_num // 2 + 1):
    for j in range(i * 2, max_num + 1, i):
        divisor_sum[j] += i
```

The cost is $\sum_i N/i = O(N \log N)$ additions, with no divisions or factorisation at all. Add
`1` instead of `i` and the same loop gives $d(n)$; add `i * i` and it gives $\sigma_2(n)$, which is
problem 211 over 64 million values. Two refinements are worth knowing:

- **Pair the divisors.** Each divisor $a < \sqrt n$ comes with a partner $n/a$, so a sieve can walk
  only $a \le \sqrt N$ and credit both members of the pair. Problem 179 counts the $n < 10^7$ with
  $d(n) = d(n+1)$ this way.
- **Sieve the multiplicative way.** A [linear sieve](/topics/technique/linear-sieve) visits each
  $n$ once, through its smallest prime factor. If it also records that prime's exponent, it can
  update $d$ or $\sigma$ with the multiplicative formula in $O(N)$.

## Summing it without listing it

Some problems want $\sum_{n \le N} \sigma_k(n)$ for $N$ far too large for any sieve (problems 401
and 439 have this shape). The way out is to swap the order of summation. Every $d \le N$ divides
exactly $\lfloor N/d \rfloor$ of the numbers up to $N$, so

$$\sum_{n \le N} \sigma_k(n) = \sum_{d \le N} d^k \left\lfloor \frac{N}{d} \right\rfloor.$$

The quotient $\lfloor N/d \rfloor$ takes only $O(\sqrt N)$ distinct values, so the sum groups into
blocks of constant quotient, each block's $\sum d^k$ given by a closed form (see the
[floor function](/topics/domain/floor-function) and the
[divisor summatory function](/topics/domain/divisor-summatory-function)). The
[Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method) is the general version
of this trick. The cost drops from $O(N \log N)$ to $O(\sqrt N)$, which is the difference between
impossible and instant at $N = 10^{15}$.

## How to reason about it

- **Factorisation first.** If a statement mentions divisors, look for the prime-power form. A
  condition on $d(n)$ is a condition on the exponents, and a condition on $\sigma(n)$ usually splits
  into one condition per prime power.
- **Know the sizes.** $d(n)$ grows very slowly: the most divisors below $10^7$ is 448 and below
  $10^{18}$ it is 103680 (the [highly composite numbers](/topics/domain/highly-composite-number)
  hold these records). $\sigma(n)$, by contrast, is about $n$ on average and never much more than a
  small multiple of it ($\sigma_2(n) < \zeta(2)\,n^2$), so check whether your 64-bit integers
  survive before you pick a type.
- **One number, many numbers, or a sum?** Trial division to $\sqrt n$ is fine for a handful of
  values. Use a sieve for every value up to $N$. For an aggregate over a range too large to sieve,
  use the swapped sum. Picking the wrong one of these three costs orders of magnitude.
- **Proper or not.** $s(n)$ leaves out $n$ itself and $\sigma(n)$ includes it, and amicable, perfect
  and abundant are all defined with $s$. Mixing them up is the most common off-by-$n$ bug on this page.
- **Divisor variants.** [Unitary](/topics/domain/unitary-divisor) and
  [bi-unitary](/topics/domain/bi-unitary-divisor) divisors (problem 861) change the per-prime-power
  factor but keep the multiplicative structure, so the same reasoning carries over with a different
  local formula.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0241](/solutions/0241/) — Perfection Quotients
- ○ [0378](/solutions/0378/) — Triangle Triples
- ○ [0379](/solutions/0379/) — Least Common Multiple Count
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0452](/solutions/0452/) — Long Products
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0485](/solutions/0485/) — Maximum Number of Divisors
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ● [0501](/solutions/0501/) — Eight Divisors
- ○ [0548](/solutions/0548/) — Gozinta Chains
- ○ [0561](/solutions/0561/) — Divisor Pairs
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0608](/solutions/0608/) — Divisor Sums
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ○ [0636](/solutions/0636/) — Restricted Factorisations
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ○ [0646](/solutions/0646/) — Bounded Divisors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0722](/solutions/0722/) — Slowly Converging Series
- ○ [0723](/solutions/0723/) — Pythagorean Quadrilaterals
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ○ [0827](/solutions/0827/) — Pythagorean Triple Occurrence
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0861](/solutions/0861/) — Products of Bi-Unitary Divisors
- ○ [0920](/solutions/0920/) — Tau Numbers
- ○ [0956](/solutions/0956/) — Super Duper Sum

<!-- /problems -->
