<!-- tags: [lucass-theorem] -->
<!-- status: final -->
# Lucas's theorem

[Lucas's theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) is the statement that a
[binomial coefficient](/topics/domain/binomial-coefficient) modulo a prime is a *digit-local*
quantity. Write $n$ and $k$ in base $p$; then $\binom{n}{k} \bmod p$ depends on nothing but the
digits, one position at a time:

$$\binom{n}{k} \equiv \prod_i \binom{n_i}{k_i} \pmod p, \qquad n = \sum_i n_i p^i,\; k = \sum_i k_i p^i.$$

That is a startling amount of leverage. $\binom{10^{18}}{10^9}$ has over nine billion decimal
digits and can never be built, but modulo a prime near $5000$ it is a product of six small factors.
The theorem keeps reappearing in the archive because it converts a question about an astronomically
large number into a question about a *short string of digits* — and once a problem is about digits,
the rest of the toolkit ([digit DP](/topics/technique/digit-dp),
[self-similarity](/topics/domain/self-similarity), block recurrences) is waiting.

## The two things it tells you

Both uses fall out of the same product, but they are worth separating because they lead to
different code.

**When is the coefficient zero?** $\binom{n_i}{k_i} = 0$ whenever $k_i > n_i$, and a single zero
factor kills the product. So

> $\binom{n}{k} \not\equiv 0 \pmod p$ **iff** every base-$p$ digit of $k$ is at most the
> corresponding digit of $n$.

For $p = 2$ that reads: $\binom{n}{k}$ is odd iff the bits of $k$ are a subset of the bits of $n$,
written $k \subseteq n$. This is the whole reason [Pascal's
triangle](/topics/technique/pascals-triangle) mod $2$ is a [Sierpiński
triangle](https://en.wikipedia.org/wiki/Sierpi%C5%84ski_triangle) — the digit condition is
self-similar, so the picture is a [fractal](/topics/domain/fractal). The complementary statement is
[Kummer's theorem](/topics/domain/kummers-theorem): the exponent of $p$ in $\binom{n}{k}$ is the
number of carries when $k$ and $n-k$ are added in base $p$, and a digit inversion $k_i > n_i$ is
exactly a carry. Two views of one fact; reach for Lucas when you want the residue, Kummer when you
want the valuation.

**What is the coefficient, when it is not zero?** Each factor involves numbers below $p$, so one
factorial table modulo $p$ answers all of them, and the division inside $\binom{n_i}{k_i}$ is a
[modular multiplicative inverse](/topics/domain/modular-multiplicative-inverse) — by [Fermat's
little theorem](/topics/domain/fermats-little-theorem), $x^{-1} \equiv x^{p-2}$ via
[modular exponentiation](/topics/technique/modular-exponentiation). The shape is always this:

```python
def binom_mod_p(n, k, p):          # fact[] = factorials mod p, built once per p
    r = 1
    while n or k:                  # one base-p digit per step
        n, ni = divmod(n, p)
        k, ki = divmod(k, p)
        if ki > ni:
            return 0               # a carry — the whole product vanishes
        r = r * fact[ni] % p * pow(fact[ki] * fact[ni - ki] % p, p - 2, p) % p
    return r
```

Setup is $O(p)$, the walk is $O(\log_p n)$ digits. Note what that says about *when* this is a good
idea: the cost is driven by $p$, not by $n$. For a small prime and a colossal $n$ it is close to
free; for $p$ comparable to $n$ it buys nothing at all.

## Counting with it, not just evaluating

The evaluation use is the obvious one. The sharper use is to *count* the $k$ satisfying the digit
condition, never touching a coefficient. In row $n$, each base-$p$ digit $d_i$ independently admits
$d_i + 1$ legal digits of $k$, so the number of entries in that row not divisible by $p$ is
$\prod_i (d_i + 1)$ — for $p = 2$, that is $2^{s(n)}$ with $s$ the
[popcount](https://en.wikipedia.org/wiki/Hamming_weight).

Summing such a product over a range of rows is where the technique earns its keep, because the
digit representation is self-similar. Over one complete block of $p^m$ consecutive rows the low $m$
digits range independently over $0 \dots p-1$, so the block's total factors as
$\left(1 + 2 + \dots + p\right)^m = \left(\tfrac{p(p+1)}{2}\right)^m$. Split the range on its
leading digit, recurse on the remainder, and you consume one digit per step: a sum over $10^9$ rows
becomes about eleven iterations. Problem 148 is exactly this, in base $7$.

Problem 242 is the same move one derivation further out. It asks about the parity of a subset-count
$f(n,k)$, which is not a binomial coefficient at all — but its
[generating function](/topics/domain/generating-function) reduced mod $2$ collapses, via the
[freshman's dream](https://en.wikipedia.org/wiki/Freshman%27s_dream) $(1+x)^2 \equiv 1 + x^2$, onto
a single shifted $(1+x)^{n-1}$. From there Lucas turns the parity question into a subset-of-bits
condition, and the count becomes a $2^{s(\cdot)}$ sum evaluated by digit DP. That is the pattern
worth internalising: **Lucas is usually not the first step, it is the step that makes the last one
finite.**

## Beyond a single prime

Lucas needs a *prime* modulus. Two escapes cover most of what problems actually ask:

| modulus | what to do |
| --- | --- |
| prime $p$ | Lucas directly |
| squarefree $m = p_1 \cdots p_j$ | Lucas per prime, then [CRT](/topics/technique/chinese-remainder-theorem) |
| prime power $p^e$ | Lucas fails; use the Andrew Granville / Davis–Webb generalisation |

The squarefree case is the friendly one and shows up in problem 365, where every modulus is a
product of three distinct primes: [modular arithmetic](/topics/domain/modular-arithmetic) mod $pqr$
splits into three prime fields, so a residue per prime is exactly as good as the residue mod the
product. Worth noticing there that the CRT lift's inverses factor pairwise — $(qr)^{-1}_p =
q^{-1}_p \cdot r^{-1}_p$ — so a triple loop needs only $O(P^2)$ distinct inverses rather than one
per triple. That is a recombination trick, not a Lucas trick, but it is what turns "one residue per
prime" into a tractable sum over twenty million moduli.

The prime-power case is genuinely harder: $\binom{n_i}{k_i}$ is no longer a well-defined digit
factor because factorials mod $p^e$ have $p$-divisible terms that must be stripped and accounted
separately. If a problem hands you a modulus like $10^9$ (which is $2^9 5^9$, not squarefree),
Lucas alone will not close it.

## How to reason about it

The tell is a modulus that is small and prime (or squarefree with small prime factors) sitting next
to an $n$ that is absurd — $10^{12}$, $10^{18}$, "a billion rows". If both halves of that are
present, stop trying to compute the coefficient and start looking at base-$p$ digits.

Three practical cautions:

- **Check the zero case first.** In many ranges the answer is $0$ for most inputs, because a single
  carry suffices. Short-circuiting on $k_i > n_i$ before any factorial work is both faster and a
  useful sanity signal — if *everything* comes out zero, your digit extraction is probably
  misaligned.
- **Verify the closed form on the statement's small case.** Every problem here quotes a small
  check ($2361$ non-multiples in the first hundred rows; five odd-triplets below $n = 10$). A
  digit recurrence has several places — the leading-digit split, an off-by-one in an inclusive
  bound, the $t = 0$ term — where a slip still produces a plausible-looking number. These
  derivations are long enough that a brute-force cross-check on small inputs is not optional.
- **Watch the accumulator.** Digit recurrences produce answers that grow like $N^{\log_p c}$ for
  the block constant $c$, which lands uncomfortably close to the $64$-bit ceiling at these bounds.
  Python's unbounded integers hide it; a C port does not (see [watch integer
  width](/topics/takeaway/watch-integer-width)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient

<!-- /problems -->
