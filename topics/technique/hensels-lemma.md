<!-- tags: [hensels-lemma] -->
<!-- status: final 2026-10-28T08:00Z -->
# Hensel's lemma

[Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma) lets me solve a congruence
modulo a prime *power* $p^k$ by solving it modulo $p$ first and then lifting the answer. A
modulus such as $p^k$ looks like it needs a search over $p^k$ residues. Hensel turns that into
$k$ cheap steps, each of which fixes one more base-$p$ digit. It keeps coming back because the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem) breaks any modulus
into prime powers, and Hensel is how each prime power is handled. CRT and Hensel together solve
a polynomial congruence modulo any $n$ whose factorisation I know.

## The idea

Suppose $f$ is an integer polynomial and $r$ is a root modulo $p^k$, so $f(r) \equiv 0 \pmod{p^k}$.
I look for a root modulo $p^{k+1}$ of the form $r + t p^k$ with $t \in \{0, \dots, p-1\}$. The
Taylor expansion stops after the linear term, because every higher term carries $p^{2k}$:

$$f(r + t p^k) \equiv f(r) + t p^k f'(r) \pmod{p^{k+1}}.$$

Divide by $p^k$ and the condition becomes a *linear* congruence in the new digit:

$$\frac{f(r)}{p^k} + t\, f'(r) \equiv 0 \pmod p.$$

Two cases follow, and the whole technique comes down to telling them apart:

- **Simple root, $p \nmid f'(r)$.** $f'(r)$ is invertible mod $p$, so exactly one $t$ works.
  The root lifts **uniquely**, all the way up, and the lift is a
  [Newton step](/topics/technique/newtons-method) computed with modular arithmetic:
  $r \leftarrow r - f(r)\, f'(r)^{-1}$. Using the inverse modulo $p^{k}$ instead of $p$ even
  doubles the precision on each step, from $p^k$ to $p^{2k}$. That is the same quadratic
  convergence Newton has over the reals.
- **Singular root, $p \mid f'(r)$.** The linear congruence loses its $t$ term. Either
  $p^{k+1} \mid f(r)$ and **all $p$** choices of $t$ lift, or it does not and **none** do. The
  root can branch or die, and only a direct check tells me which.

The lift itself is a few lines:

```python
def hensel_lift(f, df, r, p, k):
    """Lift a simple root r of f mod p to a root mod p**k."""
    m = p
    for _ in range(k - 1):
        m *= p
        r = (r - f(r) * pow(df(r), -1, m)) % m
    return r
```

Expressed in base $p$, the digits of a root modulo $p^k$ are fixed one at a time from the
lowest up, and a digit never needs revisiting. This is the finite form of a root in the
[$p$-adic integers](https://en.wikipedia.org/wiki/P-adic_number). Hensel is the reason the
$p$-adic digits of a simple root are well defined.

## How it shows up

**Roots of unity modulo a prime power (271).** The non-trivial cube roots of unity modulo $p$
are the roots of $\Phi_3(x) = x^2 + x + 1$. They exist exactly when $p \equiv 1 \pmod 3$, which
the [cyclotomic polynomial](/topics/domain/cyclotomic-polynomial) page explains. For
$f(x) = x^3 - 1$ the derivative is $3x^2$, a unit for every $p \ne 3$, so each root mod $p$
lifts uniquely, and the solution count modulo $p^k$ equals the count modulo $p$. The prime $3$
is the singular case, and it really does branch: mod $3$ only $x = 1$ survives, but mod $9$ and
above three roots exist, $1$, $1 + 3^{k-1}$ and $1 + 2\cdot 3^{k-1}$. The two pages split the
work this way: $\Phi_d$ says *which* roots exist mod $p$, and Hensel says how they extend to
$p^k$. CRT then combines them across the factors of $n$.

**Building the moduli that admit a root (245).** The coresilience problem reduces to finding
moduli $e$ for which $x^2 - x + 1 \equiv 0 \pmod e$ is solvable, along with every root. A root
mod a prime $\ell \equiv 1 \pmod 3$ is minus a primitive cube root of unity, so it is the same
polynomial family as 271. Hensel lifts it to $\ell^j$, and CRT multiplies the root sets
together. The singular prime shows the other outcome. At $p = 3$ the root $x \equiv 2$ has
$f'(2) = 3 \equiv 0$, and $f(2) = 3 \not\equiv 0 \pmod 9$, so the root dies: **$9$ never
divides $x^2 - x + 1$**. That one-line check caps the power of $3$ in $e$ at one and removes a
large share of candidate moduli before any arithmetic is done.

**Lifting with no polynomial (277).** The modified Collatz map divides by $3$ at every step, and
the step taken depends only on the current value mod $3$. Following $a_1$ through $k$ steps
gives $a_{k+1} = (c\,a_1 + b)/3^k$, where $c$ is a product of $1$s, $2$s and $4$s, which makes
$c$ a unit mod $3$. So the next step character depends on the next base-$3$ digit of $a_1$
through a slope that is invertible: the simple-root case again, with no polynomial involved.
Of the three possible digits, exactly one reproduces the next step, so a step string of length
$L$ fixes $a_1$ to a single residue class mod $3^L$. The solution recovers that class one digit
at a time, never backtracking, then moves up to the smallest representative above the bound.

## How to reason about it

- **Reach for it** when the modulus is a prime power, or will be after CRT has split it, and
  the condition is a polynomial, or any map whose dependence on the next digit is affine.
  Solve mod $p$, which is usually easy (a primitive root, an
  [exponentiation](/topics/technique/modular-exponentiation) like $a^{(p-1)/3}$, or a short
  search), then lift.
- **Check the derivative first.** If $p \nmid f'(r)$ the lift is unique, and counts carry over
  unchanged from $p$ to $p^k$. If $p \mid f'(r)$, nothing carries over automatically. Test
  directly at the first power or two where the behaviour changes, and expect the primes that
  divide the polynomial's discriminant (for $x^n - 1$, the primes dividing $n$) to need special
  handling.
- **Root counts are multiplicative.** CRT turns "how many roots mod $n$" into a product of
  per-prime-power counts. Enumerating the roots costs the product of those counts, which can be
  small even when $n$ is astronomically large.
- **Watch the word size.** A lift multiplies residues near $p^k$, so the intermediate products
  overflow 64 bits long before the modulus does. The C ports here use `__int128`, or stop lifting
  once the next power would pass the bound they need.
- **Mind the sum, not just the residue.** Combining roots by CRT gives residues mod $n$. If the
  question asks for the integers themselves (their sum, their minimum above a threshold),
  reduce every combination to $[0, n)$ first and add those values, rather than adding the
  residues mod $n$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0245](/solutions/0245/) — Coresilience
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$

<!-- /problems -->
