<!-- tags: [mobius-function] -->
<!-- status: final -->
# Möbius function

The [Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function) $\mu(n)$ is
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) written down as a lookup
table. It is $0$ when $n$ has a repeated prime factor, and otherwise $(-1)^{\omega(n)}$, the sign
set by the parity of how many distinct primes divide $n$ ([OEIS
A008683](https://oeis.org/A008683)). Those signs are exactly the $+$ and $-$ terms you would write
by hand when you correct a count for overlapping conditions — so any problem that needs "count the
things not divisible by any of these primes", or "count the ones I have not already counted in a
smaller form", ends up multiplying by $\mu$ somewhere. What makes it a *domain* rather than a
formula is that it arrives from two very different directions: sometimes the statement hands it to
you, and sometimes it is the thing you discover halfway through a derivation that never mentioned
primes at all.

## The one identity everything rests on

For every $n \ge 1$,

$$\sum_{d \mid n} \mu(d) = \begin{cases} 1 & n = 1 \\ 0 & n > 1. \end{cases}$$

Read that as a switch: summing $\mu$ over the divisors of $n$ annihilates everything except
$n = 1$. In the language of [Dirichlet convolution](/topics/domain/dirichlet-convolution) it says
$\mu * \mathbf{1} = \varepsilon$ — $\mu$ is the convolution inverse of the constant-one function,
which is the whole reason it exists. Slot that switch inside a double sum and it sifts out the
terms you want, which is the mechanical content of the [Möbius inversion
formula](/topics/technique/mobius-inversion-formula): if $g(n) = \sum_{d \mid n} f(d)$, then
$f(n) = \sum_{d \mid n} \mu(d)\, g(n/d)$. Given a quantity counted *with* multiplicity, inversion
recovers the *primitive* count underneath it.

$\mu$ is [multiplicative](/topics/domain/multiplicative-function) but not completely so
($\mu(2)\mu(2) = 1 \ne \mu(4) = 0$), which is precisely what makes it sieveable: you can build the
whole table with one pass per prime rather than by factorising each $n$.

```python
mu = np.ones(n + 1, dtype=np.int8)
for p in primes_up_to(n):
    mu[p::p] *= -1        # one more distinct prime factor — flip the sign
    mu[p*p::p*p] = 0      # a repeated prime factor — not squarefree, so zero
M = np.cumsum(mu)         # the Mertens function, as a prefix sum
```

That is a [sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) with signs instead of
strikes, and it costs $O(n \log \log n)$. Two things to notice in it: the sign flip is applied to
*every* multiple of $p$, before the square pass zeroes the ones that turn out not to be
[squarefree](/topics/domain/square-free-integer); and the zeroing must come second, or the flips
would resurrect it.

## The two ways a problem reaches it

**The statement names it.** Problem 464 defines $\mu$ outright and asks about intervals $[a, b]$
where the count of $+1$s and the count of $-1$s stay within one percent of each other. Here the
work is not computing $\mu$ — that is the ten lines above — but noticing that both counts are
prefix differences. The $+1$-minus-$-1$ imbalance over $[a,b]$ is $M(b) - M(a-1)$ for the
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function) $M(x) = \sum_{k \le x} \mu(k)$,
and their *sum* is the count of squarefree integers in the interval, another prefix difference. So
a condition on an interval becomes a condition on a pair of prefix points, and an $O(n^2)$ scan
over intervals becomes a sweep over $n+1$ points.

**The derivation produces it.** Problem 319 never says "Möbius" and is not obviously about primes
at all — it counts integer sequences obeying a web of coupled inequalities. Those collapse to
$x_i = \lfloor t^i \rfloor$ for a single real parameter $t$, so the count becomes the number of
*distinct* reals of the form $m^{1/i}$ in a range. "Distinct" is the whole difficulty:
$8^{1/2}$ and $64^{1/4}$ are the same number. Each such real has a unique minimal representation,
and characterising minimality is a condition indexed by the primes dividing the exponent — which
is to say, a $\mu$ sum. This is the more common shape in the archive, and worth learning to
recognise: **whenever you are de-duplicating a count down to its primitive representatives, expect
$\mu$ to appear.** [Euler's totient](/topics/domain/eulers-totient-function) is the same move on
the smallest possible example ($\varphi = \mu * \mathrm{id}$, primitive fractions with denominator
$n$).

## How to reason about it

The hard part is almost never $\mu$ itself. It is that both roads lead to a *summatory* $\mu$ —
$M(x)$, or a sum $\sum_d \mu(d) F(\lfloor n/d \rfloor)$ — at an $n$ far past what you can sieve.
Problem 319 wants $n = 10^{10}$; there is no array of that length. The standard escape has three
moves, and they compose:

- **[Quotient blocking](/topics/technique/quotient-blocking).** $\lfloor n/d \rfloor$ takes only
  $O(\sqrt n)$ distinct values, so group the $d$ that share one and pay per *block*. The block's
  weight is a difference $M(\mathrm{hi}) - M(\mathrm{lo} - 1)$, which is why you need $M$ at the
  quotients rather than everywhere.
- **A hybrid evaluation of $M$.** Sieve $\mu$ up to about $n^{2/3}$, prefix-sum it, and get the
  larger values from the [hyperbola-method](/topics/technique/dirichlet-hyperbola-method)
  recursion $M(v) = 1 - \sum_{j \ge 2} M(\lfloor v/j \rfloor)$, memoised at the quotients — the
  standard [Mertens evaluation](/topics/technique/mertens-function-application), $O(n^{2/3})$
  overall. The exponent is a genuine trade-off between sieve cost and recursion cost, not folklore;
  it is worth timing $n^{1/2}$ and $n^{3/4}$ against it once.
- **Compute the inner $F$ in closed form.** Blocking only helps if each block is $O(1)$ or so. If
  $F$ is a geometric or polynomial sum, evaluate it directly rather than looping.

Two practical cautions. First, $\mu$ fits in an `int8`, and $M(x)$ stays remarkably small — under
$2 \times 10^7$ it never leaves $[-1447, 1240]$, consistent with the conjectural $O(\sqrt x)$
growth. That smallness is exploitable: it lets you index a data structure *by Mertens value*, with
a few thousand slots instead of $n$. But it is an empirical bound, not a theorem, so size the
container from the observed range rather than hard-coding a constant. Second, the sign flips mean
partial sums cancel heavily; do not reach for floating point anywhere near this, and if you are
reducing modulo something, remember $\mu$ contributes $-1$s that need the usual care about
negative remainders.

The tell that you are in this domain: a count that is "over all $n$" but should really be "over
the ones not already counted", or a condition attached to *distinct* prime factors. When you see
it, write the inclusion–exclusion out once by hand for a small case. If the coefficients you get
are $+1, -1, 0$ patterned by squarefreeness, you have found $\mu$, and the rest of the work is
summing it fast.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0464](/solutions/0464/) — Möbius Function and Intervals

<!-- /problems -->
