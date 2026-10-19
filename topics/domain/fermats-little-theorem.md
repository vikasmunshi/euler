<!-- tags: [fermats-little-theorem] -->
<!-- status: final -->
# Fermat's little theorem

[Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) says that for a
prime $p$ and any $a$ not divisible by $p$,

$$a^{p-1} \equiv 1 \pmod p.$$

On its own it is a primality fact. In Project Euler it is mostly used as an **upper bound on a
period**: it guarantees that the powers of $a$ modulo $p$ repeat, and that their period divides
$p - 1$. The solved problems below are all about the base 10, through decimal expansions and
[repunits](/topics/domain/repunit). In each, Fermat turns "search for the smallest $k$ with
$10^k \equiv 1$" into "check the divisors of a number you already know". (The curated page
[repunits and multiplicative order](/topics/number-theory/repunits-and-multiplicative-order) covers
the wider family.)

## The idea — the order divides $p - 1$

The [multiplicative order](/topics/domain/multiplicative-order) $\operatorname{ord}_p(a)$ is the
smallest $k \ge 1$ with $a^k \equiv 1 \pmod p$. Every $k$ with $a^k \equiv 1$ is a multiple of it.
Fermat says $k = p - 1$ is one such exponent, so

$$\operatorname{ord}_p(a) \mid p - 1.$$

That one line has three practical consequences:

- **A bound.** The order is at most $p - 1$, and equals it exactly when $a$ is a
  [primitive root](/topics/domain/primitive-root) mod $p$.
- **A shortcut to compute it.** Start from $k = p - 1$ and, for each prime $q \mid k$, divide $q$ out
  while $a^{k/q} \equiv 1$ still holds. That costs a handful of
  [modular exponentiations](/topics/technique/modular-exponentiation) instead of up to $p - 1$
  multiplications.
- **A test of divisibility properties of the order.** Whether the order divides some $m$ is just
  whether $a^m \equiv 1$. No need to find the order itself.

For composite moduli the role of $p - 1$ is taken by Euler's $\varphi(n)$, or more tightly by the
[Carmichael function](/topics/technique/carmichael-function) $\lambda(n)$, and the same
"start high, strip prime factors" method applies.

## Three problems, three uses

**26, reciprocal cycles: the bound.** The period of the decimal expansion of $1/d$, for $d$ coprime to
10, is $\operatorname{ord}_d(10)$ (see [repeating decimal](/topics/domain/repeating-decimal)). Fermat
caps it at $d - 1$, reached exactly when $d$ is a prime with 10 as a primitive root, a
[full reptend prime](https://en.wikipedia.org/wiki/Full_reptend_prime). So the longest cycle below a
limit must come from a denominator near the limit. The public solution uses that to scan only the
top tenth of the range, computing each order by the direct loop:

```python
r = 1
for k in range(1, modulus):
    r = r * a % modulus
    if r == 1:
        return k
```

This is the $O(d)$ method, which is fine for $d < 1000$. The bound is used for *pruning*, not for
computing the order. The top-tenth window is a heuristic justified by the answer, not a proof. The
proof would be to stop once $d - 1$ falls below the best order found so far.

**130, composites with the prime repunit property: Fermat in reverse.** For a prime $p > 5$, $p$ divides
the repunit $R(p - 1)$, because $10^{p-1} \equiv 1$. In repunit terms, $A(p) \mid p - 1$, where $A(n)$ is
the least $k$ with $n \mid R(k)$. The problem asks for *composites* $n$ with $A(n) \mid n - 1$. These
are numbers that pass a Fermat-style test without being prime, the repunit analogue of
[Fermat pseudoprimes](https://en.wikipedia.org/wiki/Fermat_pseudoprime). Computing $A(n)$ uses the
shortcut above with $\lambda(n)$ in place of $p - 1$: factor $n$ with a smallest-prime-factor sieve,
build $\lambda(n)$ as an lcm over prime powers, then strip primes from it while $10^{\lambda/q} \equiv 1$.
Multiples of 3 are skipped up front. If $3 \mid n$ then $3 \mid A(n)$, which can never divide $n - 1$.

**133, repunit nonfactors: test divisibility without finding the order.** A prime $p$ divides some
$R(10^n)$ iff $\operatorname{ord}_p(10)$ divides a power of 10, that is, iff the order is
[2-5 smooth](/topics/domain/smooth-number). The order divides $p - 1$, so it is 2-5 smooth iff it
divides the 2-5 smooth part $m = 2^a 5^b$ of $p - 1$. That is one check,
`pow(10, m, p) == 1`, per prime. The order itself is never computed.

## Python and C

- **The exponentiation.** Python's three-argument `pow(base, exp, mod)` is built in and exact at any
  size. C writes `powmod` by square-and-multiply, and casts each product to `__int128` so that a
  product near $\text{mod}^2$ cannot overflow. That cast is unnecessary for moduli below $10^6$, but it
  makes the helper safe for any 64-bit modulus.
- **26**: the C widens `r` to `long long` in the order loop for the same reason, and breaks ties
  between equal orders explicitly. Python's `max` over `(order, d)` tuples breaks ties by `d`
  automatically.
- **130**: Python computes the prime-power term as $(p - 1)p^{e-1}$, which is $\lambda$ only for odd $p$.
  That is enough here, because even $n$ never reach it. C implements the full Carmichael
  rule, including $\lambda(2^e) = 2^{e-2}$, and factors $\lambda$ by trial division instead of the sieve.
- **133**: Python handles 2 and 5 implicitly. For them $10^m \bmod p = 0 \ne 1$, so they are counted
  as nonfactors by the general test. C special-cases them with an explicit comment. Both build the
  prime sieve once and reuse it across benchmark runs: at module level in Python, behind an
  `if (num_primes == 0)` guard in C.

## How to reason about it

- **Powers mod a prime are periodic, with a period dividing $p - 1$.** Use that before any search
  for a period.
- **Compute orders from the top down.** Start from $p - 1$ (or $\lambda(n)$) and strip prime factors.
  This is $O(\omega(p-1) \log p)$ multiplications instead of $O(p)$.
- **Often you only need divisibility, not the order.** "Does the order divide $m$?" is a single
  `pow` call (133).
- **Mind 2, 5 and 3 in base 10.** 2 and 5 never divide a repunit. 3 interacts with the 9 in
  $R(k) = (10^k - 1)/9$. Every solution here special-cases them, explicitly or by a filter.
- **The converse fails.** $a^{n-1} \equiv 1 \pmod n$ does not make $n$ prime: pseudoprimes and
  [Carmichael numbers](https://en.wikipedia.org/wiki/Carmichael_number) pass. Problem 130 is a
  problem built on exactly that gap.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula

<!-- /problems -->
