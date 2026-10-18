<!-- tags: [natural-logarithm] -->
<!-- status: final 2026-10-18T10:22Z -->
# Natural logarithm

The [natural logarithm](https://en.wikipedia.org/wiki/Natural_logarithm) turns products into sums
and powers into products: $\ln(b^e) = e \ln b$. In these problems that matters because the numbers
involved are too big to build. There are three-million-digit powers to rank, $(N/k)^k$ to maximise
over $k$, the leading digits of $2^j$ for $j$ in the billions, and $p^q q^p$ to compare against a
bound with millions of digits. Taking logs brings each one down to a double or a scaled integer.
The cost is precision, and much of this page is about when a `double` logarithm can be trusted and
what to do when it cannot.

## The idea

$\ln$ is strictly increasing on $(0, \infty)$, so it preserves order:

$$A < B \iff \ln A < \ln B, \qquad \ln\!\Big(\prod_i b_i^{e_i}\Big) = \sum_i e_i \ln b_i.$$

That gives three uses:

- **Compare.** Rank or bound huge products by comparing sums of logarithms (99, 800).
- **Optimise.** A product that depends on a parameter becomes a smooth function you can
  differentiate. Find the real optimum, then check the integers on either side (183).
- **Locate.** The fractional part of a logarithm gives the leading digits of a number. Counting
  where those fractional parts fall answers questions about digits (686).

## Three uses in the problems

**Compare: 99 and 800.** Problem 99 asks which of a thousand $b^e$ is largest, some with over three
million digits. Ranking by $e \ln b$ is one multiply per line, and the public solution does exactly
that:

```python
log_val = exponent * math.log(base)
```

Problem 800 counts *hybrid integers* $p^q q^p \le N$ for $N$ with millions of digits. The condition
becomes $q \ln p + p \ln q \le \ln N$, and $\ln N$ itself is `exp * log(base)`. The log also sizes
the search. At $p = 2$ the partner must satisfy $q \ln 2 < \ln N$, so the prime sieve stops at
$\ln N / \ln 2$, plus a small margin. Since $f(p, q)$ increases in $q$, each $p$ gets one binary
search over the precomputed $\ln q$ values.

**Optimise: 183.** Split $N$ into $k$ equal parts and maximise $(N/k)^k$. In logs that is
$k(\ln N - \ln k)$. Its derivative $\ln N - \ln k - 1$ vanishes at $k = N/e$, and the second
derivative $-1/k$ shows it is a maximum. The function is concave, so the integer optimum is
$\lfloor N/e \rfloor$ or $\lceil N/e \rceil$, and the solution compares $k(\ln N - \ln k)$ at those
two values. The rest of the problem (does $(N/k)^k$ terminate as a decimal?) uses exact integers.
The logarithm picks $k$, and exact arithmetic decides the property.

**Locate: 686.** $2^j$ starts with the digits $L$ exactly when the fractional part of
$j \log_{10} 2$ falls in $[\{\log_{10} L\}, \{\log_{10}(L+1)\})$. The answer $j$ runs into the
billions, so the solution counts hits with a floor sum over rational approximations of the
logarithms and binary-searches for the $n$-th one. Here the logarithm is not just a comparison
tool. Its digits are the input, and they must be correct far beyond double precision. That is where
the languages differ most (below). The leading-digit argument itself is on
[power of two](/topics/domain/power-of-two).

## When is a `double` logarithm enough?

`log` is accurate to about one ulp, a relative error near $10^{-16}$. The *absolute* error in
$e \ln b$ is about $10^{-16} \cdot e \ln b$. So the question is whether the smallest gap you need to
resolve is larger than that:

- **99:** values are around $10^6$–$10^7$, so the absolute error is about $10^{-9}$. A thousand
  distinct powers from real data are separated by far more, so `double` is fine.
- **183:** at the two neighbours of $N/e$, the values of $k(\ln N - \ln k)$ differ by roughly
  $1/(2k)$, and they are equal only in exact ties. For $N \le 10^4$ that gap dwarfs the error.
- **800:** here *exact ties exist*. $800 = 2^5 5^2$ is itself a hybrid integer, so
  $f(2, 5) = \ln 800$ exactly, and the floating-point comparison could go either way. The Python
  handles this by checking a tolerance. Only when $f$ lands within $10^{-6}$ of $\ln N$ does it build
  $p^q q^p$ and $N$ as big integers and compare exactly, caching $N$ the first time. The C has no
  big integers linked. It relies on `double` and on the fact that, for these inputs, the only true
  tie is the small one, which rounds the right way.
- **686:** the hit indicators flip at boundaries that $j \log_{10} 2$ approaches within about
  $1/j$, and $j \approx 3 \times 10^9$, so the logarithms need at least about 10 correct digits after
  scaling, plus margin. Doubles are not enough, so the constants are computed to high precision.

The general rule is to **decide in logs and confirm exactly at the boundary.** If the problem can
produce exact equality (integer powers equal to the bound), a pure-`double` comparison is a guess,
and a lazy exact fallback within a tolerance costs almost nothing.

## C and Python

| problem | Python | C |
| --- | --- | --- |
| 99 | `math.log`, `enumerate(..., start=1)` | `log` from `<math.h>`, `strtok_r` parsing |
| 183 | `math.e`, `math.log` | `M_E` (POSIX, not ISO C), `log` |
| 686 | `Decimal` at 300 digits with a hand-written artanh series (s0), or `mpmath.log10` at 150 digits (s1) | the same artanh series in `__int128` fixed point, scale $10^{25}$, in natural-log space |
| 800 | `double` plus a lazy big-integer tie-break | `double` only |

686 has the most interesting split. Python can afford base-10 logs scaled by $10^{100}$, because
big integers make the cross-multiplications free. The C has 128 bits. It works with *natural*
logs so that the floor-sum denominator is $\ln 10 \cdot W$, avoiding a product that would overflow
`__int128`. It computes every constant with the series
$\ln\frac{q+p}{q-p} = 2\sum_k \frac{1}{2k+1}\left(\frac pq\right)^{2k+1}$ in integer arithmetic, so
no floating point is involved and each floor is exact. The base of the logarithm is a choice:
any base works mathematically, so pick the one that keeps the intermediates small. Of the Python
pair, `mpmath` (s1) is the faster, because its arbitrary-precision `log10` is implemented more
efficiently than a hand-written `Decimal` series.

## How to reason about it

- **Never build what you only compare.** Rank, bound or threshold huge products by their logs.
- **Write the error budget.** The absolute error is about $10^{-16} \times$ the magnitude of the
  log. Compare it against the smallest gap the answer depends on.
- **Exact ties need exact arithmetic.** If equality is possible, fall back to integers within a
  tolerance band.
- **Optimise in log space, then test integer neighbours.** $\ln$ turns products into concave
  functions with a closed-form optimum.
- **Use the log's fractional part for leading digits.** It needs more precision than `double`
  once indices reach the billions. Compute the constants yourself in fixed point or with a
  multiprecision library.
- **Size searches with logs.** If $q \ln p$ must stay below $\ln N$, then $q < \ln N / \ln 2$.
  That is the whole sieve bound in 800.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0099](/solutions/0099/) — Largest Exponential
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0800](/solutions/0800/) — Hybrid Integers

<!-- /problems -->
