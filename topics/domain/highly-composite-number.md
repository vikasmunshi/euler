<!-- tags: [highly-composite-number] -->
<!-- status: final -->
# Highly composite number

A [highly composite number](https://en.wikipedia.org/wiki/Highly_composite_number) has more
divisors than every smaller positive integer: 1, 2, 4, 6, 12, 24, 36, 48, 60, 120, …
([OEIS A002182](https://oeis.org/A002182)). The sequence itself rarely matters. What matters is the
**shape** Ramanujan proved such numbers must have: the smallest primes, with exponents that
never increase, $n = 2^{e_1} 3^{e_2} 5^{e_3} \cdots$ with $e_1 \ge e_2 \ge e_3 \ge \dots$. Any problem
that asks for the *smallest* number whose divisor-like count reaches a target has an answer of that
shape, by the same argument. That turns an unbounded search into a small tree. The solved problems below use the shape to
find the least $n$ with enough solutions to a Diophantine equation (108, 110), and its primorial
special case to minimise a totient ratio (243).

## The idea — the exchange argument

For $n = \prod p_i^{e_i}$, the divisor count is $\tau(n) = \prod (e_i + 1)$. It depends only on the
**multiset of exponents**, not on which primes carry them. Two exchanges then fix the shape of any
minimiser:

1. **Use the smallest primes.** Replacing a prime by a smaller unused one keeps $\tau$ and shrinks
   $n$. So the primes are $2, 3, 5, \dots$ with no gaps.
2. **Put larger exponents on smaller primes.** If $p < q$ but $e_p < e_q$, swapping the two exponents
   keeps $\tau$ and multiplies $n$ by $(p/q)^{e_q - e_p} < 1$. So exponents are non-increasing.

The same holds for any count that is a product of per-exponent factors, $\prod f(e_i)$ with $f$
increasing, such as $\tau(n^2) = \prod(2e_i + 1)$. The candidates are the *products of primorials*
([OEIS A025487](https://oeis.org/A025487)), and there are very few of them: 4357 below $10^{12}$,
counting 1, against $10^{12}$ integers. Every true highly composite number has this shape, but the least $n$ with
$\tau(n^2) \ge T$ is generally *not* highly composite itself. It is the cheapest member of the shape
class that reaches $T$.

The search is a depth-first search over primes in order, with the exponent of each prime capped by the
previous one:

```python
def dfs(i, n, count, cap):
    if count >= target: best = min(best, n); return
    for e in range(cap, 0, -1):
        if n * primes[i] ** e >= best: continue          # value bound
        if count * f(e) ** (primes_left) < target: break # reachability bound
        dfs(i + 1, n * primes[i] ** e, count * f(e), e)
```

The two bounds are [branch and bound](/topics/technique/branch-and-bound). Because of the cap, each exponent
multiset is visited once rather than in every order.

## Three uses across the problems

**108 and 110, Diophantine reciprocals: the least $n$ with enough divisors of $n^2$.** Solutions of
$\frac1x + \frac1y = \frac1n$ correspond to factor pairs of $n^2$, because $(x - n)(y - n) = n^2$ (see
[completing the square](/topics/domain/completing-the-square) for the same trick). So the count is
$(\tau(n^2) + 1)/2$, and the task is the least $n$ with $\tau(n^2) = \prod(2e_i + 1) \ge 2T - 1$. For
108, with $T = 1000$, a plain scan of $n$ with trial division works (solution 0) and the answer is
six digits. 110 asks for $T = 4 \times 10^6$, where the answer is far beyond scanning, and only the
shape-restricted DFS (108's solution 1, and 110) is feasible. With 17 primes and the two bounds it
runs in well under a millisecond.

**243, resilience: exponent 1 on every prime, then a multiplier.** The resilience
$R(d) = \varphi(d)/(d-1)$ must fall below $15499/94744$. Since
$\varphi(d)/d = \prod_{p \mid d}(1 - 1/p)$ depends only on the *set* of primes, the cheapest way to
push it down is the smallest primes, each once: a [primorial](/topics/technique/primorial), the
extreme of the non-increasing shape. The solution multiplies in primes until $\varphi(M)/M$ drops below the
target. Then, because $R$ divides by $d - 1$ and not $d$, it scans the multiples $kM$ with $k$
made of $M$'s own primes. These keep $\varphi/d$ unchanged and shrink the correction, and the
smallest one that clears the bound is the answer. Both tests are
[cross-multiplied](/topics/technique/cross-multiplication) to stay exact.

**485, maximum number of divisors**, not yet solved here, asks for $\max \tau$ over sliding windows,
where the windows' maxima are typically near numbers of this shape.

## Python and C

- **Overflow guards.** Python's DFS forms `n * p**e` freely and compares it with `best`, which starts
  at `float('inf')` and is converted back with `int(best)`. C must not overflow a
  `long long`, so 108 tests `new_n > best / p` before each multiply, and 110's `power_ll` returns
  0 as an overflow signal using the same `best / base` test. The reachability product
  `new_tau * factor**remaining` is one expression in Python. In C it is a loop that stops as soon as
  it reaches the target or would overflow.
- **Seeding the bound.** 110's C seeds `best` with the product of the first $k$ primes, $3^k \ge$ the
  target, a feasible answer, so the value prune works from the first leaf. Python starts from
  infinity, which still finishes in well under a millisecond.
- **Shared state.** Python's nested `dfs` updates `best` through `nonlocal`. C uses file-scope
  statics.
- **243** is one expression per line in both. $d$ stays below $10^9$, so `long long` never
  gets close to overflowing.

## How to reason about it

- **"Smallest $n$ with at least $T$ divisors" means: search only the shape.** Smallest primes,
  non-increasing exponents. Never scan $n$.
- **Check that the count is multiplicative and exponent-only.** $\tau(n)$, $\tau(n^2)$, and the
  number of representations of many forms qualify. Then the exchange argument applies.
- **Use both prunes.** A value bound (partial $n$ already at least `best`) and a reachability bound
  (even the best remaining exponents cannot reach the target). Seed `best` with any feasible shape.
- **For ratios like $\varphi(n)/n$, primes matter and exponents do not.** The minimiser is a
  primorial, possibly times a small multiplier when the formula has a $\pm 1$ (243).
- **Guard multiplications in C.** Test `a > limit / b` before `a * b`. Signed overflow is undefined
  behaviour, not a wrap you can detect afterwards.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0243](/solutions/0243/) — Resilience
- ○ [0485](/solutions/0485/) — Maximum Number of Divisors

<!-- /problems -->
