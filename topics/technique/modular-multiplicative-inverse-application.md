<!-- tags: [modular-multiplicative-inverse-application] -->
<!-- status: final -->
# Modular multiplicative inverse (application)

A [modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) is
the element `a⁻¹` with `a·a⁻¹ ≡ 1 (mod m)`. Computing one is a solved, ten-line problem — that is
the [extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm)'s page. This page
is about the other half: what having one *lets you do*. The short answer is that it restores
division to a world that only has addition and multiplication, and the problems below all reach for
it at the moment a derivation produces a fraction, a quotient, or an unknown trapped behind a
coefficient.

## What the inverse buys

Modular arithmetic gives you `+`, `−` and `×` for free, and they are exactly the operations that
survive reduction: you may reduce operands at any point without changing the answer. Division is the
odd one out. `x / 3` has no meaning in `ℤ/m` as an operation on residues — but `x · 3⁻¹` does, and
when `3` is invertible the two agree wherever the ordinary division was exact. That is the whole
move. Every use below is some form of "I have a quotient I cannot compute, so I multiply by an
inverse instead."

The inverse exists exactly when `gcd(a, m) = 1`, which is the one precondition worth checking before
anything else. Two routes to it, both `O(log m)`:

| Route | Requires | Cost |
|---|---|---|
| [Extended Euclid](/topics/technique/extended-euclidean-algorithm) | `gcd(a, m) = 1` | `O(log m)` divisions |
| [Fermat](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem): `a⁻¹ ≡ a^(m−2)` | `m` **prime** | `O(log m)` multiplications |

In Python both are one expression — `pow(a, -1, m)` and `pow(a, m - 2, m)` — so the choice is about
the modulus, not the ergonomics. Prefer `pow(a, -1, m)`: it is faster, and it raises rather than
silently returning a wrong value when the inverse does not exist. Reach for the Fermat form only
when the modulus is a known prime *and* you are already doing
[modular exponentiation](/topics/technique/modular-exponentiation) anyway.

## Three shapes it takes

**1 — Pinning an unknown to a residue class.** A linear congruence `a·x ≡ b (mod m)` becomes
`x ≡ a⁻¹·b (mod m)` in one step, and the payoff is not the single value but the
[arithmetic progression](https://en.wikipedia.org/wiki/Arithmetic_progression) it names: the
solutions are `x₀, x₀ + m, x₀ + 2m, …`. A search over candidates collapses into a first term plus a
stride, so "the smallest such `x`" is one expression and "how many lie in `[lo, hi]`" is a
subtraction. Problems 0134, 0198, 0202 and 0251 all turn on this. Their derivations differ wildly —
a digit-suffix condition, a [Farey](https://en.wikipedia.org/wiki/Farey_sequence) neighbour
relation, a residue class modulo 3, a divisibility constraint from a
[Diophantine](https://en.wikipedia.org/wiki/Diophantine_equation) reduction — but each ends at
`something · unknown ≡ constant (mod n)`, and each is then `O(1)`. When you see that line at the end
of a derivation, stop searching.

**2 — The glue in the Chinese remainder theorem.** The
[CRT](/topics/technique/chinese-remainder-theorem) tells you a solution exists; an inverse is what
constructs it. Merging `x ≡ r₁ (mod m₁)` with `x ≡ r₂ (mod m₂)` means finding how many `m₁`-steps to
take from `r₁`, and that count is itself a linear congruence — one inverse per merge, which is the
[Garner](https://en.wikipedia.org/wiki/Chinese_remainder_theorem#Garner's_algorithm) form:

```python
t = (r2 - r1) * pow(m1, -1, m2) % m2      # steps of m1 to take
x = r1 + m1 * t                            # now correct modulo m1*m2
```

Problems 0160, 0932 and 0934 each merge exactly this way, and 0365 does the symmetric full lift over
three prime moduli. 0365 also shows the optimisation worth knowing: its lift needs `(q·r)⁻¹ mod p`
for twenty million prime triples, but the inverse is *multiplicative* — `(q·r)⁻¹ ≡ q⁻¹ · r⁻¹` — so a
table of `O(P²)` pairwise inverses serves an `O(P³)` loop. Inverting a product is never worth doing
directly if the factors recur.

**3 — Exact division of a number you never build.** This is the deepest use, and the one that
justifies the technique's presence in problems that look nothing like number theory. A combinatorial
quantity — a [binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient), a
[Lagrange](https://en.wikipedia.org/wiki/Lagrange_polynomial) weight, the sum of a
[geometric series](https://en.wikipedia.org/wiki/Geometric_series) — is defined as a quotient of
enormous integers, but the *answer* is only wanted modulo `m`. Inverses let you evaluate the formula
residue-by-residue and never materialise the numerator. Problem 0650 wants
[σ](https://en.wikipedia.org/wiki/Divisor_function)`(B(n))` where `B(n)` has astronomically many
digits, and computes each prime's factor as `(p^(e+1) − 1) · (p − 1)⁻¹ mod m`; 0487 needs Lagrange
interpolation weights, which are reciprocal factorials; 0365 needs a
[Lucas](https://en.wikipedia.org/wiki/Lucas%27s_theorem) digit factor `nᵢ! / (kᵢ!(nᵢ−kᵢ)!)`; 0743
walks a trinomial sum by the ratio between consecutive terms, which is a fraction. In every case the
inverse is what makes "the formula has a division in it" a non-issue.

A variant of the same idea is the inverse as *undo*. Problem 0926 sweeps a running product across
segment boundaries and multiplies by a factor's inverse to remove it again when the segment ends;
0650 keeps a running `p^(−v)` for the same reason. Where a sliding window over sums would use a
subtraction, a sliding window over products uses an inverse — with the caveat that a zero factor has
no inverse and breaks the trick, so this only works in a field with the zeros excluded by
construction.

## Making it cheap

`pow(a, -1, m)` is not free — it is `O(log m)`, roughly thirty multiplications at a 64-bit modulus.
That is nothing once and ruinous inside a hot loop, so the interesting engineering is in avoiding
the repetition.

- **Batch the inverses you need in bulk.** For a whole factorial table, compute *one* inverse and
  sweep backwards, since `(i−1)!⁻¹ = i!⁻¹ · i`. `n` inverses for one exponentiation and `n`
  multiplications — problem 0487 does exactly this. The general form is
  [Montgomery's trick](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Multiple_inverses):
  any `n` inverses cost one inversion plus `3n` multiplications via a prefix-product pass.

  ```python
  inv_fact[n] = pow(fact[n], -1, p)
  for i in range(n, 0, -1):
      inv_fact[i - 1] = inv_fact[i] * i % p
  ```

- **Hoist loop-invariant inverses.** If the divisor depends on the outer index only, invert once
  outside — 0650 precomputes `(p − 1)⁻¹` per prime before the sweep, not per iteration of it.
- **Ask whether you need one at all.** Problem 0381 is the instructive case. Its derivation ends at
  `S(p) ≡ −3 · 8⁻¹ (mod p)`, an inverse per prime over millions of primes. But `8·S ≡ −3` with
  `0 ≤ S < p` forces `8S = t·p − 3` for a small `t` determined by `p mod 8`, so a four-entry lookup
  table replaces every inverse with a multiply, a subtract and an exact shift. When the modulus
  varies but the *numerator* is a small constant, look for the integer identity before reaching for
  the general machinery.

## Getting it right

- **Check `gcd(a, m) = 1` before assuming.** This is the failure mode that produces silently wrong
  numbers rather than exceptions. When the shared factor is structural, strip it first: problem 0160
  pulls all factors of 5 out of a factorial before working modulo `5⁵`, precisely so the remaining
  quantity is invertible. Problem 0134's statement excludes one prime pair for the same reason — the
  inverse genuinely does not exist there.
- **A composite modulus is not a field, but inverses still work.** `gcd(a, m) = 1` is the only
  requirement; primality is not. Problem 0152 inverts squares modulo `p²` and problem 0251 works
  modulo an odd square, both perfectly well. What primality buys is only the Fermat shortcut and the
  guarantee that *every* non-zero element is invertible — modulo `p²`, multiples of `p` are not.
  Using `pow(a, m - 2, m)` on a composite `m` returns a plausible-looking number that is not an
  inverse.
- **Normalise the sign, especially in C.** Python's `%` returns a non-negative result for a positive
  modulus; C's follows the dividend, so `((x % m) + m) % m` is the idiom, and it is needed on the
  differences you feed *into* an inverse (`r2 - r1` above) as much as on the result.
- **Reduce before multiplying.** `a⁻¹` is a full-width residue, so `a⁻¹ · b` is a full-width product
  and overflows a 64-bit type at moduli above about `2³²`. Reduce both operands first, and reach for
  `__int128` or [GMP](/topics/technique/gmp) when the product still does not fit —
  Python's [arbitrary-precision integers](/topics/technique/arbitrary-precision-arithmetic) hide
  this failure right up until the C port exposes it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
