<!-- tags: [repunit] -->
<!-- status: final 2026-10-14 -->
# Repunit

A [repunit](https://en.wikipedia.org/wiki/Repunit) is a number written entirely with ones:
`R(k) = 11…1` with `k` digits. It looks like a toy, but it keeps turning up because it is really a
[geometric series](https://en.wikipedia.org/wiki/Geometric_series) in disguise, and that one
closed form ties it to modular exponentiation, multiplicative orders, Legendre's formula and
place-value arithmetic. The problems below almost never want you to *write down* a repunit.
`R(10⁹)` has a billion digits, and `R₁₉` is used as a count. What they test is whether you can
work with what the repunit means without ever building the digit string.

## The idea

In base `b` the `k`-digit repunit is

$$ R_b(k) = 1 + b + b^2 + \dots + b^{k-1} = \frac{b^k - 1}{b - 1}. $$

Base 10 gives the familiar `(10ᵏ − 1)/9`. Base 2 gives the
[Mersenne numbers](https://en.wikipedia.org/wiki/Mersenne_prime) `2ᵏ − 1` ([OEIS
A002275](https://oeis.org/A002275) lists the decimal ones). From that formula I get three working
forms, and each problem picks one of them:

| Form | Expression | What it is good for |
|---|---|---|
| Recurrence | `R(k) = b·R(k−1) + 1` | streaming one digit at a time, mod `n` if needed |
| Closed form | `(bᵏ − 1)/(b − 1)` | turning divisibility into a power congruence |
| Digit sum | `Σ bʲ` for `j < k` | place-value bookkeeping: `k` copies of a digit in a row |

### Divisibility becomes a multiplicative order

The main fact is the closed form read modulo `n`. For `gcd(n, 10) = 1`,

$$ n \mid R(k) \iff 9n \mid 10^k - 1 \iff 10^k \equiv 1 \pmod{9n}. $$

So the least `k` with `n | R(k)` is the
[multiplicative order](https://en.wikipedia.org/wiki/Multiplicative_order) of 10 modulo `9n`.
When `3 ∤ n` this is just the order of 10 modulo `n`. The rest of the divisibility family follows
from this:

- **Existence and a bound.** Since `gcd(n, 10) = 1`, the order exists, and by the pigeonhole
  principle it is at most `n`. A repunit ends in 1, so 2 and 5 never divide one, and that is why
  every statement excludes them. In [Problem 129](/solutions/0129/) the bound `A(n) ≤ n` matters
  twice: it caps the inner loop, and it tells you where the outer search has to start.
- **Primes.** For a prime `p > 5`, `p | R(k)` exactly when `ord_p(10)` divides `k`, and by
  [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) that order
  divides `p − 1`. [Problem 130](/solutions/0130/) hunts the composites that imitate this
  (`A(n) | n − 1`). These are the repunit analogue of
  [Fermat pseudoprimes](https://en.wikipedia.org/wiki/Fermat_pseudoprime) to base 10.
- **Fixed huge `k`.** To ask whether `p` divides `R(10⁹)` ([Problem 132](/solutions/0132/)), I
  don't need the order. One [modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation)
  `pow(10, k, p) == 1` settles it in `O(log k)`.
- **A whole family of `k`.** For [Problem 133](/solutions/0133/), `p` divides some `R(10ⁿ)` exactly
  when `ord_p(10)` divides a power of ten, which means the order has no prime factor other than 2
  or 5. Infinitely many `n` collapse to one test per prime: keep only the 2s and 5s of `p − 1`, call that `m`,
  and check whether `10ᵐ ≡ 1 (mod p)`.

Two structural identities sit behind all of this, and they are worth knowing on their own:
`R(a) | R(b)` exactly when `a | b`, and `gcd(R(a), R(b)) = R(gcd(a, b))`. Repunits behave like
the integers that index them. One consequence is that `R(k)` can be prime only when `k` is prime,
the same rule that applies to Mersenne numbers.

### Streaming the residue

If I need the order by direct search instead of by factoring, the recurrence does the job and
nothing large ever appears:

```python
r, k = 0, 0
while True:
    k += 1
    r = (10 * r + 1) % n   # r = R(k) mod n
    if r == 0:
        break
```

This loop is `O(A(n))`, which is fine for a handful of `n` and too slow when you scan many.
Problem 130 scans many, so its notes bound the order by the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) `λ(n)` and remove prime
factors from there, with a smallest-prime-factor sieve keeping the factorisations cheap.

### Repunits in other bases

[Problem 346](/solutions/0346/) leaves base 10 behind. Every `N ≥ 3` is `11` in base `N − 1`, so
being a repunit in *two* bases only needs one more representation with three or more digits. That
turns the problem into generating `1 + b + b² + …` for every base up to about `√L` and removing
duplicates, because some numbers are long repunits in two bases at once (`31 = 11111₂ = 111₅`).
How rare those collisions are is an open question: the
[Goormaghtigh conjecture](https://en.wikipedia.org/wiki/Goormaghtigh_conjecture) says 31 and 8191
are the only ones.

### Repunits that appear without being named

Sometimes nobody says "repunit", and the geometric sum shows up anyway:

- **Legendre's formula.** In [Problem 288](/solutions/0288/), the exponent of `p` in `N!` can be
  written digit by digit as `Σ Tₙ · (pⁿ − 1)/(p − 1)`. Each base-`p` digit is weighted by a base-`p`
  repunit. Modulo `pᵏ`, every repunit longer than `k` reduces to the same constant, and the problem
  is built around that.
- **Runs of equal digits.** In [Problem 885](/solutions/0885/), sorting a number's digits places `c`
  copies of digit `v` next to each other, and their contribution is `v · 10ᵗ · R(c)`. The repunit
  is the place-value weight of a block of identical digits, which is what makes a digit-count DP
  possible.
- **As an input size.** [Problem 847](/solutions/0847/) asks for `H(R₁₉)`. Here the repunit is
  only a very large argument, but that already tells you something: no loop up to `N` will finish,
  so you need a closed form or a logarithmic recursion.

## How to reason about it

- **Never build the digits.** Carry `R(k) mod n` with the recurrence, or skip it entirely and use
  the closed form. A million-digit repunit is a sign that only its residue matters.
- **Rewrite divisibility as `10ᵏ ≡ 1`.** Once you have the congruence you can use the standard
  tools: orders, Fermat, Carmichael's `λ`, and fast powering. Remember the factor of 9: you work
  modulo `9n`, or modulo `n` when `3 ∤ n`.
- **Choose the tool by what is fixed.** If `k` is fixed and `p` varies, one `pow` per prime is
  enough. If you need the least `k`, you need the order: search for it when there are few `n`,
  factor `λ` when there are many. If `k` ranges over a family such as powers of ten, ask which
  orders divide some member of the family.
- **Exclude 2, 5 and usually 3 up front.** 2 and 5 never divide a repunit. 3 behaves differently
  because of the 9 in the denominator. Dealing with them first keeps the main test clean and can
  shrink the search, as the `gcd(n, 30) = 1` filter does in Problem 130.
- **Recognise `Σ bʲ` when you see it.** Legendre exponents, runs of identical digits and geometric
  weights are all repunits, and the closed form `(bᵏ − 1)/(b − 1)` usually collapses the sum.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0346](/solutions/0346/) — Strong Repunits
- ○ [0847](/solutions/0847/) — Jack's Bean
- ● [0885](/solutions/0885/) — Sorted Digits

<!-- /problems -->
