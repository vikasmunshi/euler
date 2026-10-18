<!-- tags: [multiplicative-order] -->
<!-- status: final 2026-10-18T10:03Z -->
# Multiplicative order

The [multiplicative order](https://en.wikipedia.org/wiki/Multiplicative_order) of `a` modulo `n`,
written `ordₙ(a)`, is the smallest `k ≥ 1` with `aᵏ ≡ 1 (mod n)`. It is the length of the cycle
that the powers of `a` run around before they repeat. Recurring decimals, repunit divisibility and
riffle shuffles that restore a deck all turn out to be this one number. The companion page
[Repunits and multiplicative order](/topics/number-theory/repunits-and-multiplicative-order)
already shows how each of those problems reduces to an order, and compares three ways of computing
one. This page adds two things. The first is the small piece of algebra that lets you combine
orders and test them without ever computing them. The second is a side-by-side reading of the five
solved problems, showing where their C and Python versions part ways.

## The idea

The order exists exactly when `gcd(a, n) = 1`. If `a` shares a factor with `n`, then so does every
power of `a`, and no power can be 1. Everything else follows from one lemma:

$$ a^k \equiv 1 \pmod n \iff \operatorname{ord}_n(a) \mid k. $$

To see why, write `k = q·ord + r` with `0 ≤ r < ord`. Then `aᵏ ≡ aʳ`, and `r` is smaller than the
order, so `aʳ ≡ 1` only when `r = 0`. Four consequences carry nearly all the problems:

- **Upper bounds.** The order divides the size of the unit group, `φ(n)`
  ([Lagrange](https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory))). It also divides
  the group's exponent, the [Carmichael function](/topics/technique/carmichael-function) `λ(n)`,
  which is the sharper bound. For a prime, both are `p − 1`.
- **Powers.** `ordₙ(aʲ) = ordₙ(a) / gcd(ordₙ(a), j)`. Raising to a power shortens the cycle by
  exactly the common factor.
- **Coprime moduli combine by `lcm`.** If `gcd(m, n) = 1`, then
  `ordₘₙ(a) = lcm(ordₘ(a), ordₙ(a))`. By the
  [Chinese remainder theorem](/topics/technique/chinese-remainder-theorem), `aᵏ ≡ 1 (mod mn)`
  holds exactly when it holds mod `m` and mod `n`. By the lemma, that means `k` is a common
  multiple of the two orders. For example, `ord₃(10) = 1` and `ord₇(10) = 6`, so `ord₂₁(10) = 6`,
  and indeed `1/21 = 0.(047619)`.
- **Prime powers grow slowly.** For odd `p`, `ord_{pᵉ⁺¹}(a)` is either `ord_{pᵉ}(a)` or `p` times
  it. Once a lift by `p` has happened, every later lift multiplies by `p` again. The powers of 3
  show this for `a = 10`: `ord₉(10) = 1`, `ord₂₇(10) = 3`, `ord₈₁(10) = 9`. This is why
  `A(3ᵏ) = ord_{3ᵏ⁺²}(10) = 3ᵏ` on the companion page.

The last two rules are what problems over a whole range of moduli need. Problem 417 sums
`ordₙ(10)` for every `n` up to `10⁸`, and Problem 952 asks for an order modulo a factorial. Neither
can afford to walk each modulus, or even to factorise each one separately. Both build the order
from its prime-power pieces and combine them with `lcm`:

```python
# ord_n(a) from n's factorisation {p: e} — each piece is a prime-power order
order = lcm(*(ord_prime_power(a, p, e) for p, e in factors.items()))
```

The lemma also turns many questions into a single
[modular exponentiation](/topics/technique/modular-exponentiation), with no order computed at
all:

| The question                              | The test                                        |
|-------------------------------------------|-------------------------------------------------|
| Does `ordₙ(a)` divide `k`?                | `aᵏ ≡ 1 (mod n)`                                |
| Is `ordₙ(a)` exactly `k`?                 | `aᵏ ≡ 1`, and `a^(k/q) ≢ 1` for each prime `q ∣ k` |
| Is `ordₙ(a)` built only from primes in `S`? | `aᵐ ≡ 1`, where `m` is the `S`-part of `λ(n)`     |
| Is `a` a primitive root mod `p`?          | `a^((p−1)/q) ≢ 1` for each prime `q ∣ p − 1`    |

The second row is the "divide down from `λ`" method, run as a check rather than a search. The last
row is the question behind [primitive roots](/topics/domain/primitive-root).

## The five solved problems, side by side

| Problem | Asks for                                     | As an order                      | How the code gets it          |
|---------|----------------------------------------------|----------------------------------|-------------------------------|
| 26      | the `d < N` with the longest cycle in `1/d`  | maximise `ord_d(10)`             | walk the powers               |
| 129     | the least `n` with `A(n) > T`                | `ord₉ₙ(10) > T`                  | walk the repunit residues     |
| 130     | composites `n` with `A(n) ∣ n − 1`           | `ordₙ(10) ∣ n − 1`               | `λ(n)`, then divide down      |
| 132     | prime factors of `R(10⁹)`                    | `ord_p(10) ∣ 10⁹`                | one `pow` per prime           |
| 133     | primes dividing no `R(10ᵏ)`                  | `ord_p(10)` not `{2,5}`-smooth    | one `pow` per prime           |

Problem 129 is worth a second look. Its order lives modulo `9n`, but the solution never forms
`9n`. It carries `r = R(k) mod n` through `r = 10r + 1` until `r` is 0, which visits the same cycle
with the modulus kept at `n`. It also handles the factor of 3 correctly without a special case,
because the repunit itself is what is being tested.

## Where C and Python differ

The algorithms are the same in both languages. What differs is the arithmetic each language makes
you think about, and how much of the edge-case handling is explicit.

- **Overflow headroom is chosen per problem in C.** Python's three-argument `pow` and its unbounded
  integers make every product safe, so there is no choice to make. In C each solution sizes its
  arithmetic to its moduli. Problem 129 keeps `r` in an `int`, which is safe because `10r + 1 < 10n`.
  Problem 26 widens `r` to `long long`. Problem 132's `pow_mod` multiplies in plain `long long`,
  since primes below `10⁶` give products below `10¹²`. Problems 130 and 133 cast through
  `__int128`, which is more headroom than moduli this small need. That costs nothing and stays
  correct if the bound is ever raised.
- **`λ` at 2.** The Python `_A` in Problem 130 uses `λ(pᵉ) = (p − 1)pᵉ⁻¹` for every prime. That is
  wrong for `2ᵉ` with `e ≥ 3`, where `λ = 2ᵉ⁻²`, but the error is never reached, because the
  `gcd(n, 30) = 1` filter guarantees `n` is odd. The C version special-cases 2 anyway. If you copy
  the Python formula into a problem with even moduli, add the case back.
- **Factorising `λ`.** Python reuses the smallest-prime-factor sieve for `λ(n)`. That is valid
  because `λ(n) ≤ φ(n) < n`, so `λ(n)` always falls inside the sieve. The C version trial-divides
  `λ` instead, citing a bound it can never actually exceed. Both are cheap at this size, but
  `λ(n) < n` is the fact that lets one sieve serve both factorisations.
- **Who handles 2, 3 and 5 in Problem 133.** The test `10ᵐ ≡ 1 (mod p)` really asks whether
  `p ∣ 10ᵐ − 1 = 9·R(m)`. For `p = 2` or `5`, `10ᵐ mod p` is 0, so the Python version counts them
  as nonfactors through the general test with no branch. The C version adds an explicit branch for
  them. Both need a branch for `p = 3`: the 9 makes the test pass for every `m`, even though 3
  divides no `R(10ᵏ)` (the digit sum `10ᵏ` is not a multiple of 3). The general caution about 3 on
  the companion page shows up here as one line of code.
- **No order and tie-breaks.** Problem 26's helper returns `None` in Python and `-1` in C when
  there is no order. Python picks the winner with `max` over `(order, d)` tuples, so a tie goes to
  the larger `d` automatically. C has to write that rule out (`order == best_len && d > best_d`) to
  produce the same answer.

## How to reason about it

- **Decide what the question actually needs.** It may want the order itself (26, 129), only a
  divisibility fact about it (130, 132, 133), or an aggregate over many moduli (417, 952). These
  cost a walk, one `pow`, and a factor-and-combine pass respectively. Prefer the cheapest one that
  answers the question.
- **Check `gcd(a, n) = 1` first.** Every solution here filters on `gcd(n, 10)` or `gcd(n, 30)`
  before it computes an order. Without that check, a walk never reaches 1 and a `pow` test
  silently answers a different question.
- **Use the lemma to rewrite.** A condition like "`p` divides some `R(10ᵏ)`" quantifies over
  infinitely many `k`. "The order divides `k`" turns it into a property of one number, the order,
  and that property usually comes down to a single exponentiation.
- **The group can change while the rules stay the same.** Problem 622's shuffle is the order of 2
  modulo `n − 1`, and Problem 752 takes orders in `ℤ[√7]` modulo `n`. The lemma, the `lcm` rule and
  the prime-power lifting all carry over. For the cycle-finding view of the same structure, without
  any algebra, see [cycle detection](/topics/technique/cycle-detection).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ○ [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0952](/solutions/0952/) — Order Modulo Factorial

<!-- /problems -->
