<!-- tags: [lucass-theorem, kummers-theorem, legendres-formula, p-adic-valuation] -->
<!-- status: final 2026-10-14T07:42Z -->
# Primes in Pascal’s triangle

A surprising number of problems ask something about a [binomial
coefficient](/topics/domain/binomial-coefficient) or a [factorial](/topics/domain/factorial) that is
far too large to write down — $\binom{10^{18}}{10^9}$, $(10^{12})!$, every entry of a billion rows of
Pascal’s triangle — and then, on closer reading, only want to know how a *prime* sits inside it: does
$p$ divide it, how many times, what is it modulo $p$. Three classical results answer those questions,
and they are usually taught as three separate theorems. I find it far more useful to treat them as one
toolkit, because they all say the same thing: **the arithmetic of $\binom{n}{k}$ at a prime $p$ is
decided by the base-$p$ digits of $n$ and $k$**. Once a problem is about digits, the astronomically
large number disappears.

## One idea, three readings

Write $v_p(m)$ for the [$p$-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation) of $m$ —
the exponent of $p$ in its factorisation — and $s_p(m)$ for the [digit sum](/topics/domain/digit-sum)
of $m$ in base $p$.

**[Legendre’s formula](https://en.wikipedia.org/wiki/Legendre%27s_formula)** gives the valuation of a
factorial. Every multiple of $p$ up to $n$ contributes one factor, every multiple of $p^2$ one more,
and so on:

$$v_p(n!) = \sum_{i \ge 1} \left\lfloor \frac{n}{p^i} \right\rfloor = \frac{n - s_p(n)}{p - 1}.$$

The second form is the one to remember: the valuation is read straight off the digits.

**[Kummer’s theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem)** is Legendre applied to
$\binom{n}{k} = n! / (k!\,(n-k)!)$. Subtracting three digit-sum formulas gives

$$v_p\binom{n}{k} = \frac{s_p(k) + s_p(n-k) - s_p(n)}{p - 1} = \#\text{carries when adding } k + (n-k) \text{ in base } p.$$

Every carry turns $p$ units in one column into one unit in the next, losing exactly $p-1$ from the
digit sum — that is the whole proof. It is just as visible in the floor form: each term
$\lfloor n/p^i \rfloor - \lfloor k/p^i \rfloor - \lfloor (n-k)/p^i \rfloor$ is $0$ or $1$, and it is
$1$ precisely when column $i$ receives a carry.

**[Lucas’s theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem)** answers the complementary
question — not *how many* $p$’s, but *what is left* modulo $p$:

$$\binom{n}{k} \equiv \prod_i \binom{n_i}{k_i} \pmod p.$$

A factor is zero exactly when some digit $k_i > n_i$ — which is the same event as a carry in
$k + (n-k)$. So Lucas’s "is it zero mod $p$?" and Kummer’s "is the carry count positive?" are one
statement, seen from two sides.

| The question | The tool | Cost |
|---|---|---|
| Exponent of $p$ in $n!$ | Legendre | $O(\log_p n)$ |
| Exponent of $p$ in $\binom{n}{k}$ or a multinomial | Kummer (carries / digit sums) | $O(\log_p n)$ |
| Is $p \mid \binom{n}{k}$? | Lucas digit test, or Kummer $> 0$ | $O(\log_p n)$ |
| $\binom{n}{k} \bmod p$ | Lucas digit product | $O(p)$ setup, $O(\log_p n)$ per query |

The code shape is correspondingly tiny — two loops over the digits of $n$:

```python
def v_fact(n: int, p: int) -> int:      # Legendre: v_p(n!)
    e = 0
    while n:
        n //= p
        e += n
    return e

def v_binom(n: int, k: int, p: int) -> int:   # Kummer, via Legendre
    return v_fact(n, p) - v_fact(k, p) - v_fact(n - k, p)
```

## How to reason about it

**Never build the number.** The signal that this toolkit applies is a binomial or factorial whose
*value* is hopeless but whose *divisibility* is the question. Problem 231 asks for the sum of the
prime factors of $\binom{20\,000\,000}{15\,000\,000}$, a number with millions of digits; it is just
Legendre applied to every prime up to $n$. Problem 650 needs the full factorisation of a *product* of
a whole row of binomials, and the same exponent bookkeeping, accumulated across rows, delivers it.
In both, the work is $\pi(n)$ primes times $\log_p n$ digits, with the primes coming from one
[sieve](/topics/technique/sieve-of-eratosthenes).

**Split a composite modulus into primes.** The theorems are about one prime at a time, so a
composite target is first broken apart. Divisibility by $10^{12} = 2^{12} \cdot 5^{12}$ (problem
154) becomes two independent carry counts; trailing zeros of $N!$ (problem 160) are $v_5(N!)$, since
fives are always scarcer than twos; and the smallest $m$ with $n \mid m!$ (problem 549) is the maximum
over $n$’s prime powers $p^e$ of the smallest $m$ with $v_p(m!) \ge e$. A residue modulo a
*squarefree* number goes the same way: Lucas modulo each prime, then glue the residues with the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem) — that is all problem 365
is.

**Turn "for every coefficient" into "for every digit string".** When the question ranges over a
whole region of the triangle, the digit view makes it countable. By Lucas, row $n$ has
$\prod_i (n_i + 1)$ entries not divisible by $p$ — that product is why Pascal’s triangle mod $p$ is a
[fractal](/topics/domain/fractal), and it is what problem 148 sums over a billion rows by collapsing
whole blocks of $p^m$ rows at once. For $p = 2$ everything becomes bit-twiddling: $\binom{n}{k}$ is
odd iff $k$’s bits are a subset of $n$’s (the parity question behind problem 242), and $v_2\binom{n}{k}$
is a popcount deficit, so maximising it over $k$ (problem 704) is a question about $n$’s bit length
and popcount alone. Problem 154 extends Kummer to multinomials — the valuation of
$\binom{n}{i,j,k}$ is the carry count of $i + j + k$ — and then counts carry patterns rather than
coefficients. When the counting gets awkward, a [digit DP](/topics/technique/digit-dp) over the
base-$p$ digits, carrying the carry, is the general tool.

**Squarefree and exact-exponent questions are carry thresholds.** Problem 203 needs to know
whether a binomial is squarefree; instead of factoring entries far beyond a machine word it asks, for each prime,
whether adding $k$ and $n-k$ in base $p$ produces two or more carries. "Divisible by $p^e$" is
"at least $e$ carries", and nothing more.

**Pitfalls.**

- Lucas needs a **prime** modulus. Modulo a prime *power* the digit product is wrong; you need
  Granville’s generalisation, or the classic route of stripping every factor of $p$ out of the
  factorial and working with what remains (problem 160’s last-five-digits computation is exactly
  that, modulo $2^5$ and $5^5$).
- Kummer counts carries in $k + (n-k)$, not in anything involving $n$ itself; for multinomials it is
  the carries of all the lower indices added together.
- Legendre’s floor sum stops when $p^i > n$; written as a repeated `n //= p` it never overflows,
  whereas computing $p^i$ directly can.
- A prime $p > n$ never divides $n!$, and a prime $p > \sqrt{n}$ divides $\binom{n}{k}$ at most once ($n$ has only two base-$p$ digits) —
  cheap early exits when looping over all primes.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ○ [0383](/solutions/0383/) — Divisibility Comparison Between Factorials
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0792](/solutions/0792/) — Too Many Twos
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
