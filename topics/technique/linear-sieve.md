<!-- tags: [linear-sieve] -->
<!-- status: final -->
# Linear (Euler) sieve

The [linear sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Euler's_sieve), also
called Euler's sieve, finds all primes up to $n$ in $O(n)$ time by crossing off each composite
**exactly once**, through its smallest prime factor. The classic
[sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) crosses a number off once for
each of its prime factors. The linear sieve's reason for existing is not the saved
$\log\log n$ factor. It is the **smallest-prime-factor table** it builds as a by-product, and the
fact that every $n$ is reached from a known smaller number by a known prime. That lets one pass
compute a multiplicative function, such as Möbius, a totient, or anything defined on prime
powers, for every $n$ up to the bound. All three solved problems below use it for that.

## The idea — every composite has one canonical predecessor

Write each composite as $m = i \cdot p$, where $p$ is the smallest prime factor of $m$. Then $p$ is
at most the smallest prime factor of $i$. The sieve walks $i$ upward and, for each $i$, multiplies by
the primes $p \le \mathrm{spf}(i)$ in increasing order. It stops at the first $p$ that divides $i$,
because beyond it $p$ would no longer be the smallest factor of $i \cdot p$:

```python
for i in range(2, n + 1):
    if spf[i] == 0:                      # untouched -> prime
        spf[i] = i; primes.append(i)
    for p in primes:
        if p > spf[i] or i * p > n:
            break
        spf[i * p] = p                   # written once, by the smallest prime
```

Each composite is written once, so the work is $O(n)$. What matters more is the branch structure:
at the moment $i \cdot p$ is written, the sieve knows whether $p \nmid i$ or $p \mid i$.

- **$p \nmid i$**: $\gcd(i, p) = 1$, so any multiplicative $f$ satisfies $f(ip) = f(i)\,f(p)$.
- **$p \mid i$** (the breaking step): $p$ is already the smallest prime of $i$, and $ip$ has one more
  factor of $p$. This is the one case that needs the prime-power rule $f(p^{a+1})$, usually with
  $f$ of the cofactor coprime to $p$.

So with one extra array, recording the exponent of the smallest prime or the value of its prime-power block, a
[multiplicative function](/topics/domain/multiplicative-function) fills in during the sieve itself.
For Möbius the two branches are $\mu(ip) = -\mu(i)$ and $\mu(ip) = 0$.

## When it beats the classic sieve — and when it does not

| need | best tool |
|---|---|
| primes or a primality table only | Eratosthenes, or [primesieve](/topics/technique/primesieve) for speed |
| $\mu$, $\varphi$, $\sigma$, or any multiplicative $f$ for all $n \le N$ | **linear sieve** |
| smallest prime factor, for fast factorisation of many $n$ | **linear sieve** (or an spf variant of Eratosthenes) |
| primes in a window $[L, R]$ far from 0 | [segmented sieve](/topics/technique/segmented-sieve) |

The $O(n)$ bound is misleading in practice. Eratosthenes' inner loop is a strided store,
`flags[p*p::p] = 0`, which vectorises in NumPy, segments well into cache, and is what primesieve
optimises heavily. The linear sieve's inner loop reads `spf[i]` and the prime list at every step,
and each $i$ depends on writes made by smaller $i$. So it is inherently sequential and
cannot be expressed as array slices. For primes alone it is usually slower. It wins when the
multiplicative values are the goal, because the alternative is a second pass that factors each $n$.
Generating the prime list is covered in [generation of primes](/topics/technique/generation-of-primes).

## Three uses across the problems

**153, investigating Gaussian integers: Möbius up to $\sqrt N$.** The sum over Gaussian divisors
reduces to a sum over coprime lattice pairs. [Möbius inversion](/topics/technique/mobius-inversion-formula)
removes the coprimality condition at the cost of a sum over $d$ with weight $\mu(d)$, and the lattice
radius scales as $d^2$, so $\mu$ is needed only up to $\sqrt{N} = 10^4$. The linear sieve is the
natural way to produce it, using the two branches above. The heavy work is then nested
[quotient blocking](/topics/technique/quotient-blocking), and the sieve's cost is negligible.

**549, divisibility of factorials: smallest prime plus its exponent.** $s(n)$, the least $m$
with $n \mid m!$, is $\max_{p^e \,\|\, n} s(p^e)$. The sieve runs over all $n \le N$ and records
`least_prime[i]` and `pe_exp[i]`, the exponent of that prime in $i$. The exponent propagates in the
breaking branch as `pe_exp[i] + 1` and resets to 1 otherwise. Then
$s(i) = \max(s(p^e), s(i / p^e))$, where the cofactor $i/p^e$ is smaller and already done. The
$s(p^e)$ values come from [Legendre's formula](/topics/domain/legendres-formula) and are cached per
prime. This is a DP on the sieve order, and it works because the sieve hands each $i$ its smallest
prime-power block.

**745, sum of squares II: a Dirichlet convolution in one pass.** The largest square dividing $n$
sums to $S(N) = \sum_{m \le \sqrt N} h(m) \lfloor N/m^2 \rfloor$ with
$h = \mu * \mathrm{id}^2$, a [Dirichlet convolution](/topics/domain/dirichlet-convolution).
$h$ is multiplicative with $h(p^a) = p^{2a} - p^{2a-2}$. The sieve fills $h$ up to $10^7$: the
coprime branch multiplies, and the breaking branch divides out the whole $p$-block and applies the
prime-power formula. The solution uses $h[i] = 0$ as its "not yet seen, so prime" marker even
though $h$ is stored mod $10^9 + 7$. That is safe only because the modulus is prime and no
$h(p^a) = p^{2a-2}(p^2 - 1)$ with $p < 10^7$ is divisible by it, so no composite's product reduces
to zero. With a composite modulus the sentinel would need its own array.

## Python and C

The three solutions run the same sieve in both languages, and the differences are about storage and width:

- **Lists, NumPy and C arrays.** 153 and 745 keep `mu`/`h` in Python lists. 549 keeps its three
  $10^8$-entry tables in NumPy arrays (`int64`, `int32`, `int64`) to hold the memory down, but still
  walks them element by element, because the linear sieve cannot be sliced. C uses `calloc`'d arrays
  throughout, and `int` is enough for 549's `least_prime` and `pe_exp`.
- **Index width.** $i \cdot p$ is formed before the bound check, so C declares the loop indices
  `long long`. An `int` product would overflow silently near the top of the range and corrupt the table.
- **Modular products (745).** Python's `pow(p, 2a, mod)` and `%` work on unbounded integers. C
  computes $a \cdot b \bmod m$ through `__int128` in its `pow_mod`, and normalises the negative
  remainder of $p^{2a} - p^{2a-2}$ with `(x + mod) % mod`.
- **Prime-power caches (549).** Python uses a `dict` from prime to a growing list of $s(p^e)$. C uses an
  array of per-prime `realloc`'d buffers indexed by the prime itself.

## How to reason about it

- **Choose it for the function, not for the primes.** If you need $\mu$, $\varphi$, $\sigma_k$ or a
  custom multiplicative $f$ at every $n \le N$, the linear sieve gives them in the same $O(N)$ pass.
  For primes alone, use Eratosthenes or primesieve.
- **Know the two branches.** Coprime: $f(ip) = f(i) f(p)$. Same prime: apply the prime-power rule,
  which needs the exponent or the cofactor. Track one of them in an extra array.
- **Bound the sieve by what the formula needs.** 153 and 745 need $f$ only up to $\sqrt N$ because
  of a $d^2$ or $m^2$ in the sum. 549 needs every $n$.
- **Keep the spf table if you will factor again.** Any $n \le N$ factors in $O(\log n)$ by
  repeated division by `spf[n]`.
- **Check your sentinel.** Using "value is 0" to mean prime only works if no computed value can be 0,
  which is a real risk once values are reduced modulo something.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0745](/solutions/0745/) — Sum of Squares II

<!-- /problems -->
