<!-- tags: [legendres-formula] -->
<!-- status: final -->
# Legendre's formula

[Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) answers one narrow
question: how many times does the prime $p$ divide $n!$? That one count, the
[$p$-adic valuation](/topics/domain/p-adic-valuation) $v_p(n!)$, is the key to most problems about
factorials and binomial coefficients that are far too large to write out. A factorial with $10^{12}$
factors has no usable decimal expansion, but its exponent of 5 is a sum of about a dozen integer
divisions. Every problem below asks about divisibility, trailing digits or the prime
factorisation of a huge product. Each one becomes tractable once I stop thinking about the number
and think about its exponents.

## The idea

Among $1, 2, \dots, n$, there are $\lfloor n/p \rfloor$ multiples of $p$. Each contributes at least one factor of $p$. The
$\lfloor n/p^2 \rfloor$ multiples of $p^2$ contribute a second factor, the multiples of $p^3$ a
third, and so on. Count each layer once:

$$v_p(n!) = \sum_{i \ge 1} \left\lfloor \frac{n}{p^i} \right\rfloor .$$

The sum stops when $p^i > n$, so it has $\lfloor \log_p n \rfloor$ terms. The loop never builds a power of $p$. It just keeps
dividing $n$:

```python
def legendre(n: int, p: int) -> int:
    e = 0
    while n:
        n //= p
        e += n
    return e
```

The second form matters more than the first. Write $n$ in base $p$ and let $s_p(n)$ be its
[digit sum](/topics/domain/digit-sum). Then

$$v_p(n!) = \frac{n - s_p(n)}{p - 1}.$$

The reason: a base-$p$ digit $d$ in position $j$ adds $d \cdot (p^{j-1} + \dots + 1) = d \cdot \frac{p^j - 1}{p-1}$ to
the floor-sum. The exponent depends only on the **digits** of $n$ in base $p$. That is the bridge
to everything else on this page.

### From factorials to binomials: Kummer

Apply the digit form to $\binom{n}{m} = \frac{n!}{m!\,(n-m)!}$. The $n$, $m$ and $n-m$ terms cancel,
leaving

$$v_p\!\binom{n}{m} = \frac{s_p(m) + s_p(n-m) - s_p(n)}{p - 1},$$

which is [Kummer's theorem](/topics/domain/kummers-theorem): the exponent equals the number of
**carries** when $m$ and $n-m$ are added in base $p$. Multinomials work the same way. For a trinomial coefficient
$\frac{n!}{i!\,j!\,k!}$ the numerator becomes $s_p(i)+s_p(j)+s_p(k)-s_p(n)$. Problem 154 uses this: "Is
this entry of Pascal's pyramid divisible by $10^{12}$?" turns into two comparisons of precomputed
base-2 and base-5 digit sums. Its threshold for 5 is multiplied by $p-1 = 4$, which removes the
division. Problem 704 asks for the largest power of 2 dividing any binomial in a row. By Kummer,
that is the maximum number of binary carries, which depends only on the bit length and popcount
of $n$. The sum over $n$ then reduces to closed forms grouped by bit length. When the question
switches from "how many factors of $p$" to "what is the residue mod $p$", the companion result is
[Lucas's theorem](/topics/domain/lucass-theorem), which is also digit-wise.

### The trailing-digit connection

The number of trailing zeros of an integer in base $b$ is its valuation at $b$. For $b = 10$ that is
$\min(v_2, v_5)$. For a factorial, $v_5(n!) \le v_2(n!)$ always holds, so $n!$ ends in exactly $v_5(n!)$ zeros
($100!$ has $20 + 4 = 24$). In a general base $b = \prod q_j^{a_j}$ the count is
$\min_j \lfloor v_{q_j}(n!) / a_j \rfloor$, and the scarcest prime power sets it. Problem 926
reverses this. Its "roundness" counts trailing zeros across every base at once. Summed over $b$,
that becomes a question about the exponent vector of the number, so for a factorial input the
first step is Legendre on every prime.

Problem 160 asks for the last nonzero digits instead, and here the zeros are an obstacle, not the
answer. Legendre tells me exactly how many 2s and 5s to remove. The rest is a
[CRT](/topics/technique/chinese-remainder-theorem) split of $10^5$ into $2^5 \cdot 5^5$, plus a
"$p$-free factorial" modulo each prime power. That factorial recurses on $\lfloor n/p \rfloor$, which
is exactly Legendre's layering. The units in each full period multiply to $\pm 1$ by
[Wilson's theorem](/topics/domain/wilsons-theorem) generalised to prime powers.

### Whole factorisations

Several problems need $v_p$ for **every** prime up to $n$, not just one. Examples are the sum of the prime factors of a
binomial (231), the unitary-divisor or divisor sums of $n!$ or of a product of binomials (429, 650),
a divisor-type sum over every factorial up to $n$ (675), and the roundness of $n!$ (926). The pattern is a
[sieve](/topics/technique/sieve-of-eratosthenes), then Legendre per prime. Then a
[multiplicative](/topics/domain/multiplicative-function) assembly from the exponents: $\sigma$,
$\sigma_2^*$, or a divisor count is a product over primes of a function of $e_p$ alone. Two
refinements show up repeatedly:

- **Primes above $\sqrt n$ need only one term**, $e_p = \lfloor n/p \rfloor$. They fall into bands
  $(n/(m+1),\, n/m]$ that share exponent $m$. A count of primes per band replaces a per-prime loop
  when the downstream work depends only on $e_p$.
- **Binomials subtract**: $v_p\binom{n}{k} = v_p(n!) - v_p(k!) - v_p((n-k)!)$. Each term
  $\lfloor n/p^i\rfloor - \lfloor k/p^i\rfloor - \lfloor (n-k)/p^i\rfloor$ is 0 or 1 (a carry
  again), so I can accumulate level by level without building the three factorial exponents.
- **A run of factorials updates, it does not recompute.** Problem 675 sums $S(i!)$ for every
  $i \le 10^7$, where $S(p^e) = 2e + 1$. Running Legendre afresh for each $i$ would cost $\pi(i)$
  primes per term. The difference form is what saves it: $v_p(i!) - v_p((i-1)!) = v_p(i)$, so
  going from $(i-1)!$ to $i!$ changes only the exponents of the primes dividing $i$. The product
  then moves by at most $\omega(i)$ ratios $(2e+1)/(2(e - v)+1)$, which is a modular inverse
  because the modulus is prime. Prime $p$ is touched at $n/p$ positions, so the whole sequence
  costs $O(n \log\log n)$. The large-prime band appears again: for $p > \sqrt n$ the exponent at
  the $k$-th multiple is just $k$, so the ratio $(2k+1)/(2k-1)$ depends on $k$ alone and one
  update can serve every such prime at once.

### Running it backwards

Legendre gives $v_p(n!)$ from $n$. Some problems fix the exponent and ask for $n$. Problem 549's
$s(n)$ (the [Kempner function](https://en.wikipedia.org/wiki/Kempner_function)) is the least $m$
with $n \mid m!$. For a prime power that means the least $m$ with $v_p(m!) \ge e$. Since
$v_p(m!)$ only increases at multiples of $p$, the search walks $m = p, 2p, 3p, \dots$ and adds
$v_p(m)$ at each step. A general $n$ takes the maximum over its prime-power parts. Problem 383
compares two valuations, $v_5((2i-1)!)$ against $2\,v_5(i!)$. The digit form turns that into an
inequality between base-5 digit sums, which suits a digit DP over $i$ up to $10^{18}$. Problem
288 gives its $N$ directly as base-$p$ digits, so the digit form computes $v_p(N!)$ without ever
building $N$.

## How to reason about it

- **Reach for it** whenever a factorial, binomial or multinomial is too large to compute and the
  question concerns divisibility, trailing zeros, the factorisation, or residues once the zeros are
  removed.
- **Choose the form by the input.** The floor-sum suits one $n$ with many primes. The digit-sum form
  suits many $n$ with one prime, and anything phrased by base-$p$ digits, because it turns
  inequalities between valuations into digit-sum inequalities that a digit DP can count.
- **Mind the slow prime.** For trailing zeros in base 10 only $5$ matters. In base $b$ check which
  $q^a \parallel b$ is scarcest. $\lfloor v_q / a\rfloor$ rarely comes from the largest prime.
- **Cost:** $O(\log_p n)$ per prime, so a full factorisation of $n!$ is dominated by the sieve and
  not by Legendre. The pitfall is the opposite mistake, factoring each of $1..n$ separately,
  which repeats work that the floor-sum does once per layer.
- **Exponents can overflow.** With $n$ given by $10^7$ base-$p$ digits (288), $v_p(N!)$ itself is
  astronomically large and only its residue is wanted. Each digit's weight
  $\frac{p^j-1}{p-1}$ is a geometric sum that becomes constant modulo $p^k$ for $j \ge k$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ○ [0383](/solutions/0383/) — Divisibility Comparison Between Factorials
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
