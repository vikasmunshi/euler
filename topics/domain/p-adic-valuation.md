<!-- tags: [p-adic-valuation] -->
<!-- status: final -->
# P-adic valuation

The [$p$-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation) $v_p(n)$ is the exponent
of the prime $p$ in $n$: the number of times I can divide by $p$ before a remainder appears. It turns
a multiplicative question into an additive one. "Does $10^{12}$ divide this coefficient?" becomes
"are two integers at least 12?" The problems below all involve numbers far too large to build:
factorials, multinomials, products of whole rows of Pascal's triangle. In each of them I stop holding
the number and hold its valuations instead.

## The idea

Every positive integer is a vector of exponents, $n = \prod_p p^{v_p(n)}$, with $v_p(0) = \infty$ by
convention. Four rules make that vector easy to work with:

| Rule | Statement | What it buys |
|---|---|---|
| Product | $v_p(ab) = v_p(a) + v_p(b)$ | Products, powers and quotients become sums and differences of exponents |
| Divisibility | $a \mid b \iff v_p(a) \le v_p(b)$ for every $p$ | Divisibility is a component-wise comparison; $\gcd$ is the min, $\operatorname{lcm}$ the max |
| Sum ([ultrametric](https://en.wikipedia.org/wiki/Ultrametric_space)) | $v_p(a+b) \ge \min(v_p(a), v_p(b))$, with **equality when the two differ** | The valuation of a sum is known exactly whenever one term is strictly "less divisible" |
| Factorials | $v_p(n!) = \sum_{i\ge1} \lfloor n/p^i \rfloor = \dfrac{n - s_p(n)}{p-1}$ | One huge product, $\log_p n$ divisions ([Legendre](/topics/domain/legendres-formula)) |

The last rule carries over to binomial and multinomial coefficients, which are quotients of
factorials. [Kummer's theorem](/topics/domain/kummers-theorem) gives the result as the number of
carries when the parts are added in base $p$. In digit-sum form,
$v_p\binom{n}{i,j,k} = \big(s_p(i)+s_p(j)+s_p(k)-s_p(n)\big)/(p-1)$.

The sum rule is the one engineers tend to forget. The other three treat $v_p$ like a logarithm. The
sum rule is what lets you reason about $v_p$ of an expression that is *not* a product.

## How the solutions use it

**Divisibility as exponent comparison: 154 and 549.** Problem 154 counts the coefficients of
$(x+y+z)^{200000}$ that are divisible by $10^{12}$. That means $v_2 \ge 12$ and $v_5 \ge 12$, and
Kummer turns each condition into a digit-sum inequality over a precomputed table. Neither language
ever builds a coefficient. The two sides differ only in how they scan the $O(n^2)$ triples. The
Python version vectorises each row with numpy: it adds `s[:m+1]` to the reversed `s[i:]`, so every
$j + k = m$ pair is lined up at once. The C version walks $j$ only up to $m/2$ and counts each
unordered pair twice. It also builds its digit sums with the one-line recurrence
`out[x] = out[x / base] + x % base` into `unsigned char` arrays, which keeps both tables in cache.
Problem 549 asks for the least $m$ with $n \mid m!$. The divisibility rule splits this prime by prime:
$s(n) = \max_{p^e \parallel n} s(p^e)$, where $s(p^e)$ is the least $m$ with $v_p(m!) \ge e$. A
[linear sieve](/topics/technique/linear-sieve) supplies each $i$'s smallest prime and its exponent,
and that is all the max needs. The two versions run the same loop. Python loops over numpy arrays
element by element. C grows a per-prime cache of $s(p^e)$ with `realloc`.

**Carrying the exponent vector instead of the number: 650.** $B(n) = \prod_k \binom{n}{k}$ has
millions of digits. Its divisor sum $\sigma$, however, is
[multiplicative](/topics/domain/multiplicative-function), so it needs only
$e_p = v_p(B(n)) = (n+1)\,v_p(n!) - 2\sum_{j\le n} v_p(j!)$. The product rule makes the step from
$n-1$ to $n$ a small *change* in exponent. For every prime that does not divide $n$, that change is
the same expression, $-v_p((n-1)!)$. So one blanket update covers almost every prime, and only the few
primes dividing $n$ need a fix-up. The language split is about keeping modular products in 64 bits.
The Python version keeps $p^{e_p} \bmod m$ for all primes in a numpy `int64` vector and reduces the
final product pairwise, so no intermediate exceeds $m^2 < 2^{63}$. The C version has no vector to
protect and multiplies through `__int128`.

**Splitting a number into $p$-part and unit: 160.** The last five non-zero digits of $N!$ are
$N!/10^{v_5(N!)} \bmod 10^5$. Writing $N! = 2^{v_2} 5^{v_5} u$ separates what is not invertible mod
$2^5$ and $5^5$ (the prime powers) from what is (the unit $u$). Each half is solved on its own and
then recombined by the [CRT](/topics/technique/chinese-remainder-theorem). The valuations are what
keep the leftover powers of 2 and 5 exact; the residues alone would lose them. Python gets the inverse
from `pow(x, -z, m)`. C hand-rolls an extended-Euclid `modinv`.

**The sum rule doing real work: 484 and 834.** Problem 484 needs $\gcd(k, k')$, where $k'$ is the
[arithmetic derivative](/topics/domain/arithmetic-derivative). Write $k'/k = \sum_q a_q/q$ over
$q^{a_q} \parallel k$. Here the ultrametric rule decides everything. If $p \nmid a_p$, the term $a_p/p$
has valuation $-1$ and every other term has valuation $\ge 0$. The minimum is strict, so
$v_p(k') = a_p - 1$ exactly. If $p \mid a_p$, every term has valuation $\ge 0$ and $v_p(k') \ge a_p$.
Either way the gcd is a clean per-prime formula, which makes it multiplicative and lets a
squarefull-number DFS sum it ([Dirichlet convolution](/topics/domain/dirichlet-convolution)).
Problem 834 reduces to deciding which $q > n$ divide $q(q-1)/2 + X$, where $X = n(n-1)/2$. Odd $q$ must
divide $X$. For even $q$, the first term is only $\equiv q/2 \pmod q$, so the condition becomes
$X \equiv q/2$. That pins the 2-adic valuation: $v_2(q) = v_2(X) + 1 = v_2(n) + v_2(n-1)$, exactly.
Every valid $q$ is therefore an odd divisor $d$ or $d \cdot 2^{v_2(n)+v_2(n-1)}$, never anything in
between. Both languages strip the 2s with a shift loop (`while (!(x & 1)) { v++; x >>= 1; }`) before
the SPF factorisation. A `__builtin_ctzll` would do the same in one instruction, but the loop is not
the bottleneck.

## How to reason about it

- **Reach for it whenever the question says "divisible by", "trailing zeros", "last non-zero digits"
  or "number of divisors" about a product.** Those depend only on the exponent vector. Computing that
  vector costs logarithms, where computing the number costs its digits.
- **Composite targets split by prime.** $10^{12}$ is two separate conditions, $v_2 \ge 12$ and
  $v_5 \ge 12$. Remember that the scarcer prime (5, for factorials) is the one that decides.
- **Track deltas, not totals.** When a product changes by one factor per step (650, Pascal rows,
  running factorials), the valuations change by small integers. Update those integers; do not
  re-factor.
- **Use the sum rule deliberately.** Equality in $v_p(a+b) = \min$ when the valuations differ is what
  turns "some sum is divisible" into an exact exponent (484, 834). When the valuations tie, the bound
  is only a bound, and that case needs a separate look.
- **Pitfalls.** $v_p(0)$ is infinite, so guard zero terms. Valuations of factorials grow like
  $n/(p-1)$, so they fit an `int` long after $p^{v}$ has overflowed everything. Keep the exponent
  and reduce the power modulo something only at the end. For $p = 2$ in C, the valuation is the
  trailing-zero count of the binary word ([power of two](/topics/domain/power-of-two)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ○ [0383](/solutions/0383/) — Divisibility Comparison Between Factorials
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0792](/solutions/0792/) — Too Many Twos
- ● [0834](/solutions/0834/) — Add and Divide

<!-- /problems -->
