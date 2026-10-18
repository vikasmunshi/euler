<!-- tags: [composite-number] -->
<!-- status: final -->
# Composite number

A [composite number](https://en.wikipedia.org/wiki/Composite_number) is an integer greater than 1
that is not prime: it has a factorisation $n = ab$ with $1 < a, b < n$. Problems rarely ask about
composites for their own sake. They pick a property every prime has for free and ask which
composites have it too, or they hunt for the first composite where a pattern breaks, or they use
the fact that only a composite can be split further. So the composites in these problems are
defined by contrast with the primes. The work is in excluding the primes cheaply, then exploiting
or constructing whatever structure the remaining composites have.

## The idea

A few facts about composites do most of the work here:

- **A smallest factor at most $\sqrt n$.** If $n = ab$ with $a \le b$, then $a \le \sqrt n$. That
  justifies trial division to the square root, and it is why a sieve need only strike from $p^2$.
- **The sieve labels both.** A sieve of Eratosthenes, or its smallest-prime-factor (SPF) variant,
  labels every integer as prime or composite at once. With an SPF table, `spf[n] == n` is the
  primality test and `spf[n]` is a witness of compositeness.
- **Primes satisfy identities that composites usually fail.** Fermat's little theorem gives
  $a^{p-1} \equiv 1 \pmod p$. The totient gives $\varphi(p) = p - 1$. The order of 10 modulo a
  prime $p$ divides $p - 1$. Any of these, read as a test, passes on every prime, so the composites
  that also pass are the interesting ones. Those are
  [pseudoprimes](https://en.wikipedia.org/wiki/Pseudoprime) in the broad sense, and
  [Carmichael numbers](https://en.wikipedia.org/wiki/Carmichael_number) are the best-known family.
- **Only composites factor.** A prime has one factorisation, itself. For a quantity defined over
  factorisations, the primes are the base case and composites are where the recursion happens.

## Four ways the problems use it

**The first counterexample: 46.**
[Goldbach's other conjecture](https://en.wikipedia.org/wiki/Goldbach%27s_other_conjecture) says
every odd composite is $p + 2k^2$. It fails, and the task is the smallest failure. The search
needs primality for two things: to skip primes (only *composites* are candidates) and to supply
the $p$ in each decomposition. So both solutions grow a prime list as they walk upward. The Python
uses an incremental sieve, a `dict` from each upcoming composite to the primes that strike it, so a
number missing from the dict is prime. The C uses trial division against the primes so far, up to
$\sqrt n$, in a doubling array. Both test whether $(n - p)/2$ is a square for every smaller odd
prime. The C confirms the float root in integers, `root * root == half`. The Python trusts the
float, `x ** 0.5 % 1 == 0`, which is exact at this scale. The
[sqrt](/topics/technique/sqrt) page explains why that check stops being safe for larger values.

**Composites that pass a prime test: 130 and 245.** Both problems state a divisibility that every
prime satisfies, then ask only about composites:

| problem | property | why every prime has it |
| --- | --- | --- |
| 130 | $A(n) \mid n - 1$, with $A(n)$ the order of 10 mod $n$ | Fermat: the order divides $p - 1$ |
| 245 | $(n - \varphi(n)) \mid (n - 1)$ | $\varphi(p) = p - 1$, so $n - \varphi(n) = 1$ |

130 is a Fermat-pseudoprime hunt in base 10. The answer is a search: scan $n$ upward, skip primes
with `spf[n] == n`, skip multiples of 2, 3 and 5 with one `gcd(n, 30)` check, and compute
$A(n)$ from the Carmichael function by stripping prime factors (see
[multiplicative order](/topics/domain/multiplicative-order)). The cheap prime filter matters
because primes far outnumber the qualifying composites.

245 is a relative of [Lehmer's totient problem](https://en.wikipedia.org/wiki/Lehmer%27s_totient_problem),
which asks whether any composite has $\varphi(n) \mid n - 1$. The limit is $2 \times 10^{11}$, far
too large to filter, so the solution has to *construct* candidates. That depends on structure
only composites have. A qualifying $n$ must be squarefree, since a repeated prime would divide both
$n - \varphi(n)$ and $n - 1$. For two prime factors $pq$, the condition becomes
$(p + q - 1) \mid (p^2 - p + 1)$, which determines $q$ from $p$ and a divisor. For three or more,
fixing all but the largest prime makes the equation linear in that prime, and a prefix with
$\varphi(m)/m \le 1/2$ can be cut. The primes, which trivially qualify, are never generated at all.
That is the cleanest way to exclude them.

**Composites as things that split: 159.** $\operatorname{mdrs}(n)$ is the best digital-root sum
over all factorisations of $n$. For a prime it is just $\operatorname{dr}(p)$. For a composite it
is the best of keeping $n$ whole or splitting off a factor $f$ and recursing on $n/f$. The DP runs
as a divisor-style sieve: once `mdrs[n]` is final, push $\operatorname{mdrs}[n] + \operatorname{dr}(f)$
to every multiple $fn$. Primes never receive a push, since no proper divisor reaches them, so
they keep their seed. The sieve never has to ask whether a number is prime.

**The open one: 467** writes the digital roots of the first $n$ primes and of the first $n$
composites as two digit strings and asks for the smallest integer containing both as subsequences. It is the same contrast, with the
composites taken as a sequence of their own.

## C and Python

- **Sieves and tables.** 46's Python sieve is a `dict` of future composites, which needs no bound
  in advance. The C has no hash map, so it uses trial division against a growing array. 130's
  sieve is an SPF array in both languages. The Python also reuses it to factor $\lambda(n)$, while
  the C factors $\lambda(n)$ by trial division.
- **Modular arithmetic width.** 130 and 245 exponentiate modulo $n$. Python's three-argument `pow`
  is exact and compiled. The C uses an `__int128` modular multiply. 245's C also checks the
  prefix bounds $m p^2 \le N$ in `__int128`, because the products that test exists to reject are
  exactly the ones that overflow 64 bits.
- **Vectorised sieve DP.** 159's inner push is `np.maximum` over the strided slice `mdrs[2n::n]`
  in Python and a plain nested loop in C. The digital roots are a precomputed table in both, so
  the inner step is an array read instead of a modulo.
- **Where the gap shows.** 245 is pure small-integer arithmetic with nothing to vectorise, and its
  C runs about 60 times faster. That is the usual ratio for that kind of workload in this
  repository.

## How to reason about it

- **When a property holds for every prime, the composites that share it are the question.**
  Identify the identity behind it (Fermat, $\varphi(p) = p - 1$, the order dividing $p - 1$) and
  look for the composite analogue: pseudoprimes, Carmichael-like conditions, Lehmer-like
  conditions.
- **Exclude primes as cheaply as you can.** An SPF lookup, a gcd with a small primorial, or not
  generating them at all. The exclusion runs on every candidate.
- **Squarefreeness is often forced.** If a prime $p^2 \mid n$ makes $p$ divide both sides of the
  condition, the candidates are squarefree, and you can enumerate products of distinct primes.
- **Construct when you cannot filter.** Past about $10^9$, generate composites from their prime
  factors (solve for the last one, prune prefixes by a bound) instead of testing every integer.
- **Factorisation DPs run as sieves.** Push from each finished $n$ to its multiples. Primes are the
  entries nothing pushes to.
- **Mind the edges.** 1 is neither prime nor composite, so "not prime" is not the same as
  "composite". The first odd composite is 9. A loop that labels every non-prime as composite
  misclassifies 1 unless it starts at 2.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0245](/solutions/0245/) — Coresilience
- ○ [0467](/solutions/0467/) — Superinteger

<!-- /problems -->
