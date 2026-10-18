<!-- tags: [geometric-series] -->
<!-- status: final 2026-10-18T10:07Z -->
# Geometric series

A [geometric series](https://en.wikipedia.org/wiki/Geometric_series) is a sum whose terms share a
constant ratio: $1 + r + r^2 + \dots + r^{n-1}$. It turns up in a solution whenever something is
*repeated with a fixed multiplier*: a digit's weight in a positional number, a prime power's
divisors, the chance that a failed round sends the game back where it started. Each time, the
useful move is to replace the loop with the closed form. That leaves one awkward step, dividing by
$r - 1$, and that step is where the four problems below differ. The C and Python versions differ
in the same place.

## The idea

The finite sum telescopes. Multiply by $r$, subtract, and nearly everything cancels:

$$\sum_{j=0}^{n-1} r^j = \frac{r^n - 1}{r - 1} \qquad (r \ne 1),$$

and for $|r| < 1$ the infinite tail converges to $\frac{1}{1 - r}$. The finite form appears in this
repository in two guises:

- **As a count.** $\sigma(p^e) = 1 + p + \dots + p^e = \frac{p^{e+1} - 1}{p - 1}$ is the sum of the
  divisors of a prime power. Because $\sigma$ is
  [multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function), the divisor sum of any
  factored number is a product of geometric series.
- **As a repunit.** $\frac{p^n - 1}{p - 1}$ is the base-$p$ number written with $n$ ones. Weighting
  a digit by it is what [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula)
  does when it is written in its digit-sum form.

The infinite form turns up in probability, where "fail and go round again" with constant odds is a
geometric number of retries.

## Three ways to divide by $r - 1$

Over the integers the division is exact, because $r - 1$ always divides $r^n - 1$. Under a modulus
it is not automatically available. The solutions take three routes:

| route | when it works | used in |
| --- | --- | --- |
| divide first, reduce after | the numerator fits before reduction | 288 |
| work modulo $m \cdot (r - 1)$, then divide | $r - 1$ shares a factor with $m$ | 319 |
| multiply by $(r - 1)^{-1} \bmod m$ | $\gcd(r - 1, m) = 1$ | 650 |

**Divide first.** Problem 288 needs the exponent of $p$ in $N!$ modulo $p^k$, with $N$ given by its
ten million base-$p$ digits. Legendre's formula makes each digit $T_n$ contribute
$T_n \cdot \frac{p^n - 1}{p - 1}$. Modulo $p^k$ that repunit stops changing once $n \ge k$, because
every higher power of $p$ vanishes. So all the long tail shares one constant
$R = \frac{p^k - 1}{p - 1}$. Both languages compute it as `(modulus - 1) // (p - 1)`, where
`modulus` is $p^k$ itself, so the division is an exact integer division with no inverse involved.
The first $k - 1$ repunits are built by Horner's rule, `acc = acc * p + 1`, which never divides at
all. When you can build the sum digit by digit, that is the simplest way to avoid the division.

**Widen the modulus.** Problem 319 reduces to $F(m) = \sum_{h \le m} (3^h - 2^h - 1)$, which is
two geometric series and a count:
$F(m) = \frac{3^{m+1} - 3}{2} - (2^{m+1} - 2) - m$. The answer is wanted modulo $10^9$, and $2$ has
no inverse there. The solution therefore evaluates $3^{m+1} - 3$ modulo $2 \cdot 10^9$. The value is
always even, and its residue modulo an even modulus keeps that parity, so halving the residue gives
the right answer modulo $10^9$:

```python
twice = 2 * modulus
geo3 = ((pow(3, m + 1, twice) - 3) % twice) // 2
```

This works for any divisor $d$: compute modulo $d \cdot m$, divide exactly, and the quotient is
correct modulo $m$.

**Invert.** Problem 650 needs $\sigma(B(n))$ for a product of binomial coefficients, modulo the prime
$10^9 + 7$. Every prime $p \le 20000$ has $p - 1$ coprime to that modulus, so each solution
precomputes $(p - 1)^{-1}$ once by Fermat (`pow(p - 1, mod - 2, mod)`) and evaluates each factor as
$(p \cdot p^{e} - 1) \cdot (p - 1)^{-1}$. The tidy detail is that a prime with $e = 0$ gives
$(p - 1)(p - 1)^{-1} = 1$, so inactive primes need no special case in the product. The inverse
precomputation and the vectorised product are on
[modular multiplicative inverse](/topics/domain/modular-multiplicative-inverse).

## The infinite form: a self-loop solved in closed form

Problem 232 is a coin race. On their turn, Player 2 picks $T$ and scores $2^{T-1}$ with probability
$q = 2^{-T}$. A miss by both players returns the game to the *same* state, so a state's value
appears on both sides of its own equation. Iterating that equation would sum the series
$\sum_k \bigl(\tfrac{1-q}{2}\bigr)^k$ one term at a time. Instead the solution solves the linear
fixed point once per candidate $T$:

$$x = \tfrac12 h + \tfrac12\bigl(q w + (1 - q)x\bigr) \;\Longrightarrow\; x = \frac{h + q w}{1 + q}.$$

The denominator $1 + q$ is the geometric series' $1 - r$ with $r = \frac{1 - q}{2}$, rescaled by
2. A geometric number of retries is always a closed form, because the retries are
independent and the ratio does not change. The general pattern of collapsing self-loops is on
[probability distribution](/topics/domain/probability-distribution).

## C and Python

The algorithms match line for line. The differences come from integer width and from how a power of
two is formed:

- **Width of the product.** In 288 the head and the tail product $R \cdot \text{tail\_sum}$
  reach about $10^{25}$. Python's integers absorb that. The C accumulates in `unsigned __int128` and
  reduces once at the end. 319 and 650 use `__int128` inside `mulmod` for the same reason.
  Python's `pow(b, e, m)` is already exact at any width.
- **Vectorised products.** 650's Python keeps the per-prime powers in NumPy `int64` arrays, so
  every product must stay below $2^{63}$. It multiplies the geometric factors pairwise in a tree
  reduction instead of one big `np.prod`. The C loop calls `mulmod` on each factor in turn.
- **Exact powers of two.** 232 forms $2^{-T}$ as `2.0 ** -t` in Python and `ldexp(1.0, -t)` in C.
  Both are exact in binary64, so the two languages print the same digits (see
  [double-precision floating-point format](/topics/technique/double-precision-floating-point-format)).

## How to reason about it

- **Spot the fixed ratio.** Digit weights, prime-power divisor sums, retry probabilities, and
  sums of $a^h$ over a range are all geometric series. Write the closed form before writing a loop.
- **Decide how to divide before you reduce.** Check whether $r - 1$ is invertible modulo $m$. If it
  is not, widen the modulus by $r - 1$ and divide exactly. If the numerator fits, divide over the
  integers.
- **Look for a stabilising tail.** Modulo $r^k$, the partial sums stop changing after $k$ terms,
  and a long loop collapses to a short head plus one multiplication (288).
- **Horner avoids the division entirely** when you need every partial sum anyway.
- **A self-referencing state is a geometric series in disguise.** Solve the linear equation instead
  of iterating it to convergence.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0232](/solutions/0232/) — The Race
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0650](/solutions/0650/) — Divisors of Binomial Product

<!-- /problems -->
