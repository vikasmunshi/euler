<!-- tags: [carmichael-function] -->
<!-- status: final -->
# Carmichael function

The [Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) `λ(n)` is the smallest
exponent that returns *every* unit modulo `n` to `1` — the
[exponent of the group](https://en.wikipedia.org/wiki/Exponent_of_a_group) `(ℤ/nℤ)*`. Everyone
reaches for [Euler's totient](/topics/domain/eulers-totient-function) `φ(n)` in that role, and `φ`
does work: `a^φ(n) ≡ 1` for all `a` coprime to `n`. But `φ` is merely *an* exponent that works, while
`λ` is *the* smallest one, and `λ(n)` can be many times smaller. Everywhere below, that gap is the
whole point: a smaller exponent means a shorter search for a
[multiplicative order](/topics/domain/multiplicative-order), and a shorter period when you are
arguing that a sequence repeats.

## The idea

`λ(n)` is defined by a universal property — the least `m > 0` with `a^m ≡ 1 (mod n)` for every `a`
with `gcd(a, n) = 1` — but it is computed from the factorisation, prime power by prime power:

| `n` | `λ(n)` |
| --- | --- |
| `p^e`, `p` odd | `p^(e-1)(p - 1)` — same as `φ` |
| `2`, `4` | `1`, `2` — same as `φ` |
| `2^e`, `e ≥ 3` | `2^(e-2)` — **half** of `φ(2^e)` |
| `n = ∏ p^e` | `lcm` of the parts |

```python
from math import lcm

def carmichael(factors):           # factors: {p: e}
    out = 1
    for p, e in factors.items():
        if p == 2 and e >= 3:
            part = 1 << (e - 2)
        else:
            part = (p - 1) * p ** (e - 1)
        out = lcm(out, part)
    return out
```

The single structural difference from `φ` is that last line: `φ` **multiplies** the parts, `λ` takes
their **lcm**. Since the parts usually share factors of `2`, the lcm throws a lot away. Take
`n = 561 = 3 · 11 · 17`: `φ(n) = 2 · 10 · 16 = 320`, but `λ(n) = lcm(2, 10, 16) = 80`, a quarter of
it. The more distinct odd primes divide `n`, the wider the gap grows — while for the `n` that have a
[primitive root](https://en.wikipedia.org/wiki/Primitive_root_modulo_n) (`1, 2, 4, p^e, 2p^e`) the
group is [cyclic](/topics/domain/cyclic-group) and `λ(n) = φ(n)` exactly, with no gain at all.

The `2^e` row is not a footnote. For `e ≥ 3` the group `(ℤ/2^eℤ)*` is not cyclic — it is
`{±1} × ⟨3⟩` — so no single element reaches order `φ(2^e) = 2^(e-1)`, and `λ` is half that. It is the
one row that cannot be derived by pattern-matching the others, and the one a from-scratch
implementation gets wrong.

## Two ways it earns its keep

**As a bound you compute with.** To find the order of `a` modulo `n` — the least `k` with
`a^k ≡ 1` — you never iterate `k` upward. The order divides any valid exponent, so start from one
you know and strip it down: factor `λ(n)`, and for each of its primes `p`, keep dividing the
candidate by `p` while [modular exponentiation](/topics/technique/modular-exponentiation) still
confirms `1`.

```python
def order(a, n, lam):              # lam = carmichael(n); requires gcd(a, n) == 1
    k = lam
    for p in prime_factors(lam):
        while k % p == 0 and pow(a, k // p, n) == 1:
            k //= p
    return k
```

That is `O(log λ)` exponentiations instead of `O(n)` multiplications, and starting from `λ(n)`
rather than `φ(n)` means fewer factors to strip. Problem 130 is built on this: the least repunit
length `A(n)` with `n | R(k)` is exactly the order of `10` modulo `n`, because `R(k) = (10^k - 1)/9`,
so `n | R(k)` is `10^k ≡ 1 (mod n)`. Sweeping millions of candidates makes the difference between a
descent and a scan the difference between seconds and never. Feed the factorisations from a
[smallest-prime-factor sieve](/topics/technique/sieve-of-eratosthenes) and the whole per-candidate
cost collapses to a handful of `pow` calls.

**As a period you argue with.** The other use writes no code at all. If you need to know that some
modular sequence repeats — so you can compute one block and replay it — `λ` is what proves the
period. Problem 250 needs `k^k mod 250` for `k` up to `250250`, and gets it by showing the map is
periodic in `k` with period `500`. The argument splits `250 = 2 · 5^3` by the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem): mod `2`, `k` and `k + 500`
have the same parity; mod `125`, the shift leaves the base alone because `500 ≡ 0 (mod 125)`, and
leaves the *exponent* alone because `λ(125) = 100` and `500 ≡ 0 (mod 100)`. A `250250`-term sweep
becomes a `500`-term one. Note what did the work: the base repeats mod `n`, and the exponent repeats
mod `λ(n)`.

## How to reason about it

Reach for `λ` when you are about to write `φ` as an exponent and the modulus is composite with
several distinct prime factors. If the modulus is prime or a prime power, `λ` buys you nothing (bar
the `2^e` case) and `φ` is the honest tool.

Things to keep in mind:

- **`λ(n)` is a group-wide bound, not any one element's order.** Every order divides `λ(n)`, and
  *some* element attains it, but the `a` you care about may sit well below. If you need the exact
  order, you still have to descend — `λ` only shortens the descent.
- **Exponent reduction needs `gcd(a, n) = 1`.** `a^e ≡ a^(e mod λ(n))` is false the moment `a` shares
  a factor with `n`. The safe general form for `e ≥ log₂ n` is
  `a^e ≡ a^(λ(n) + (e mod λ(n))) (mod n)` — keeping one full `λ` in the exponent covers the
  non-invertible part. Reducing to a bare `e mod λ(n)` is the classic off-by-a-cycle bug.
- **Computing `λ(n)` costs a factorisation.** Below a sieve limit that is `O(log n)` divisions with
  an SPF table and free in practice; above it you are trial-dividing, and `λ(n)` itself may exceed
  the sieve bound even when `n` does not — a real case when you go on to factor `λ(n)` to strip the
  order.
- **`λ(n) | n - 1` for composite `n` is the definition of a
  [Carmichael number](https://en.wikipedia.org/wiki/Carmichael_number)** — Korselt's criterion, and
  exactly the composites that pass every Fermat base. Problem 130's condition is the same shape
  restricted to a single base: `ord_n(10) | n - 1` says `10^(n-1) ≡ 1 (mod n)`, so its composites are
  precisely the [Fermat pseudoprimes](https://en.wikipedia.org/wiki/Fermat_pseudoprime) to base `10`
  that are coprime to `10`. Recognising a condition as "pseudoprime to one base" tells you
  immediately that the set is sparse and that no closed form is coming.
- **The gap is bounded but unbounded in ratio.** `λ(n) | φ(n)` always, so `λ` never costs you
  anything; but the quotient `φ(n)/λ(n)` grows with the number of prime factors, which is why the
  technique pays off most on exactly the squarefree, many-factored composites that a sweep spends
  most of its time on.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0250](/solutions/0250/) — $250250$

<!-- /problems -->
