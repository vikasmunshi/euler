<!-- tags: [quadratic-residue] -->
<!-- status: final 2026-11-03T22:41Z -->
# Quadratic residue

A [quadratic residue](https://en.wikipedia.org/wiki/Quadratic_residue) modulo `p` is a number that
has a square root modulo `p`. That sounds like a fact about squares, and in the problems below it is
never used that way. It does two jobs. Most often it is a **filter on primes**: given a quadratic
expression — `2n² - 1`, `p² + 1`, `x² - x + 1` — the primes that can ever divide it are exactly the
primes modulo which some constant is a residue, and that condition usually collapses to a congruence
you can test with a single `p % 8` or `p % 3`. Half the primes fall away before any work begins. The
other job is a **switch**: for a power of a quadratic irrational no prime falls away, but the same
symbol decides which group the arithmetic lives in, and so whether exponents reduce by `p - 1` or
`p + 1`.

## The idea

Modulo an odd prime `p`, squaring is two-to-one on the non-zero residues (`x` and `-x` square to the
same thing), so exactly half of them are squares. The
[Legendre symbol](https://en.wikipedia.org/wiki/Legendre_symbol) `(a|p)` records which half `a` is
in: `+1` if `a` is a non-zero square mod `p`, `-1` if not.
[Euler's criterion](https://en.wikipedia.org/wiki/Euler%27s_criterion) makes it computable in one
[modular exponentiation](/topics/technique/modular-exponentiation):

```python
def legendre(a, p):            # p an odd prime
    return pow(a, (p - 1) // 2, p)   # 1 → residue, p-1 → non-residue, 0 → p | a
```

That is already fast, but for a *fixed* `a` swept over millions of primes it is still a `log p`
loop per prime, and it is often unnecessary. The
[law of quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity) and its two
supplements convert the question "is `a` a residue mod `p`?" into a congruence on `p` alone. The
rows that keep showing up:

| Is it a residue mod `p`? | Exactly when | Cost |
| --- | --- | --- |
| `-1` | `p ≡ 1 (mod 4)` | `p & 3 == 1` |
| `2` | `p ≡ ±1 (mod 8)` | `(p & 7) in (1, 7)` |
| `-3` | `p = 3` or `p ≡ 1 (mod 3)` | `p % 3 == 1` |
| `13` | `p mod 13` is in `{1, 3, 4, 9, 10, 12}` | one table lookup |

The `13` row is the general case. For a prime `q ≡ 1 (mod 4)`, reciprocity says simply
`(q|p) = (p|q)`, so the test is a lookup of `p mod q` among the squares mod `q`; problems 457 and 492
both use it. For `q ≡ 3 (mod 4)` the answer also depends on `p mod 4`, so the table is indexed by
`p mod 4q`: for `7`, six of the twelve classes coprime to 28. Square factors drop out first, which is
why the `117 = 3²·13` of problem 492 tests exactly like `13` for every prime except 3.

Each row replaces a modular exponentiation with a mask or a lookup, and each halves the list: a fixed
non-square is a residue for half of all primes, because reciprocity picks out half the classes and
[Dirichlet's theorem](https://en.wikipedia.org/wiki/Dirichlet%27s_theorem_on_arithmetic_progressions)
spreads the primes evenly over them. The `-3` row looks harsher, since `1 mod 3` is a third of the
integers, but the primes split evenly between `1` and `2 mod 3`.

## Reading a quadratic form's prime divisors

The step that turns a problem into one of those rows is completing the square. If `p | f(n)` for
some quadratic `f`, multiply by `4a` and complete: the congruence becomes `y² ≡ D (mod p)` for the
discriminant `D`, so `p` can divide `f` at all only when `D` is a residue mod `p`. Each of these
lands on a different row of the table:

- `t(n) = 2n² - 1`: `p | t(n)` means `2n² ≡ 1`, i.e. `n² ≡ 2⁻¹ (mod p)`, which is solvable exactly
  when `2` is a residue — the `p ≡ ±1 (mod 8)` row. Problem 216 uses that to skip half the primes
  before doing anything else.
- `m = p² + 1`: any odd prime `ℓ | m` has `p² ≡ -1 (mod ℓ)`, so `-1` is a residue mod `ℓ` — the
  `ℓ ≡ 1 (mod 4)` row. Problem 221 trial-divides only by `2` and the `1 mod 4` primes, roughly a
  quarter of the integers. Problems 291 and 659 reach the same row through `2f(n) = (2n + 1)² + 1`
  and `(2k)² + 1`.
- `n² - 3n - 1`: `4f(n) = (2n - 3)² - 13`, so `13` must be a residue. Problem 457 sums a root for
  every prime that passes the `13` row, and the rest contribute nothing.
- `x² - x + 1`: not obviously any of the rows until you complete the square —
  `4(x² - x + 1) = (2x - 1)² + 3`, so a prime divisor needs `-3` to be a residue, giving `ℓ = 3` or
  `ℓ ≡ 1 (mod 3)`. Problem 245 leans on this hard: it *builds* its moduli out of admissible primes
  rather than testing candidates, and the same identity shows `9` can never divide `x² - x + 1`.

That last case is the general lesson. A form whose divisors look unconstrained usually is not; the
constraint is hiding in the discriminant.

## From "there is a root" to "here is a root"

The residue test is an existence proof, and a sieve needs the actual root: knowing that `p | 2n² - 1`
happens for *some* `n` is useless until you know the two residue classes `n ≡ ±n₀ (mod p)`, because
those are the arithmetic progressions you strike out of a
[sieve](/topics/technique/sieve-of-eratosthenes).

Extracting the root is [Tonelli–Shanks](/topics/technique/tonelli-shanks-algorithm) in general, but
the special cases are worth knowing because they are one line and cover most primes you meet:

- `p ≡ 3 (mod 4)` — the root is `a^((p+1)/4) mod p`, a single `pow`. No loop, no non-residue search.
- `p ≡ 1 (mod 4)` and you want `√-1` — raise any **non-residue** `a` to `(p-1)/4`. Euler's criterion
  says `a^((p-1)/2) ≡ -1`, so the result squares to `-1`. Half of all bases qualify, so a few small
  candidates settle every prime. Problem 659 does this one prime at a time; problem 291 runs it as
  array arithmetic over two million primes at once, which a branching Tonelli–Shanks loop would
  resist.
- `ℓ ≡ 1 (mod 3)` and you want a root of `x² - x + 1` — that root is `-ω` for `ω` a primitive cube
  root of unity, found as `g^((ℓ-1)/3)` for the first base `g` that does not give `1`. Cheaper than
  a general square root, and it is what problem 245 does.

Lifting a root from `ℓ` to `ℓᵏ` is [Hensel's lemma](/topics/technique/hensels-lemma); combining
roots modulo coprime factors is the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem), and a modulus with `k`
distinct admissible prime factors ends up carrying `2^k` roots. That combination — residue condition
picks the primes, Hensel lifts, CRT merges — is how you enumerate every modulus with a solution
without factoring anything.

## Factoring every value at once

Striking is the simplest use of the roots. The stronger one is **dividing**. Problems 216 and 291
only ask whether a value is prime, so they mark it and move on. Problems 621 and 659 need each value's
factorisation, and trial division one value at a time costs about `√f(n)` each, around `10¹⁴` steps
in problem 659. But a prime divides `f(n)` only along its root progressions, so one pass over the
primes, dividing along those progressions, factors all `N` values together in about `N log log N`
divisions. That is the [polynomial sieve](/topics/technique/polynomial-sieve), and two details make
it exact:

- **Stop at `√max f` and read the leftover.** Once every prime up to that bound is divided out, what
  remains of a value is `1` or a single prime, because two larger primes would overshoot `f`. No
  primality test is needed. In problem 659 the leftover, when there is one, *is* the largest prime
  factor; in problem 621 its residue mod 4 alone settles its contribution.
- **A progression finds `p`, not its exponent.** Problem 621 keeps dividing at each hit until `p`
  stops going in. Problem 659 Hensel-lifts the root instead and walks the sparser progression for
  `p²`, `p³`, …, touching only the indices that really carry the higher power.

## When no prime is filtered out

Problems 492 and 752 ask no divisibility question at all. Each is a power of a root of a quadratic.
Problem 492's recurrence, once the square is completed, is `b → b² - 2`, the doubling rule of the
[Lucas sequence](/topics/technique/lucas-sequence) `Vₖ = αᵏ + α⁻ᵏ` with `α` a root of `t² - 11t + 1`.
Problem 752 wants the [order](/topics/domain/multiplicative-order) of `u = 1 + √7` modulo `x`. Every
prime counts, so nothing can be discarded. Instead the symbol of the discriminant `D` says where `α`
lives:

| `D` mod `p` | Name | `α` lives in | What collapses |
| --- | --- | --- | --- |
| residue | split | `GF(p)`; the ring is `GF(p) × GF(p)` | `α^(p-1) = 1` |
| non-residue | inert | `GF(p²)` | `α^(p+1) = αᾱ`, the norm |
| zero | ramified | a double root | neither; handle it apart |

The inert row is the one to remember. In `GF(p²)` the
[Frobenius map](/topics/technique/frobenius-endomorphism) `y → yᵖ` swaps `α` with its conjugate `ᾱ`,
so `α^(p+1)` is `αᾱ`, the constant term of the quadratic, and that is an ordinary number.

In problem 492 that constant is `1`, so the order divides `p + 1`, and the enormous index `2^(n-1)`
[reduces](/topics/takeaway/reduce-exponent-modulo-group-order) modulo `p - 1` or `p + 1` as the `13`
row decides. The values `Vₖ` are traces, which stay in `GF(p)` either way, so the inert branch never
touches `GF(p²)` arithmetic: the symbol changes one modulus and nothing else. In problem 752 the norm
is `-6`, so `u^(p+1) = -6`, not `1`. That still helps. The order `o` of `-6` in `GF(p)` must divide
the answer, and `u^o` has norm one, so its order divides `p + 1`. The search runs over the divisors
of `p + 1` rather than the much richer `p² - 1`, and most of the powering stays in plain integers.

## The other two answers

A filter only cares about `+1`. Once the symbol is a switch, the other answers carry information too.

**Zero is a third case, not a boundary nuisance.** When `p | D` the two roots merge, the derivative
vanishes there, and [Hensel's lemma](/topics/technique/hensels-lemma) has nothing to divide by. If
`p` divides `D` exactly once, `y² ≡ D` has a root mod `p` and none mod `p²`: that is why problem 457
gets nothing from `p = 13`, and why `9` never divides `x² - x + 1`, where `D = -3`. The "exactly once"
matters. In problem 621 a high power of 3 divides the constant, so high powers of 3 do appear in the
values; there the merged root must be recorded once, or an index gets divided twice. Problem 752's
ramified prime `7` has a unit group of order `7 · 6`, which is neither `p - 1` nor `p + 1`, and gets
its own branch.

**A non-residue tells you something too.** If `-1` is a non-residue mod `q` and `q | x² + y²`, then
`q` divides both `x` and `y`, since otherwise `x/y` would be a square root of `-1`. So such a `q`
enters a sum of two squares to an even power, which is the heart of the
[sum of two squares theorem](/topics/domain/sum-of-two-squares-theorem). Problem 621 therefore runs
two symbols in one sieve: whether the large constant is a residue mod `p` decides if `p` divides
any value at all, and whether `-1` is decides what `p` contributes, a factor `e + 1` for exponent `e`
when `p ≡ 1 (mod 4)`, or a verdict of `1` or `0` on the parity of `e` when `p ≡ 3 (mod 4)`.

## How to reason about it

Reach for a residue argument when a loop is testing divisibility against a **quadratic** in the
index, and the inner test is doing the work. The filter's gain is not a better algorithm for the
same candidate set; it is a smaller candidate set, halved at zero cost. That makes it a
[cheap check first](/topics/takeaway/cheap-checks-first) in the strictest sense: a mask on `p` that
is faster than the load of the value it protects. The roots are where the asymptotic win is, since
they turn per-value factoring into one sieve. Reach for the symbol as a switch when a problem powers
a root of a quadratic, or runs a second-order recurrence, modulo many primes: ask for the
discriminant before asking for the period.

Things to keep in mind:

- **Small constant `a`, varying `p` → use reciprocity. Otherwise use Euler's criterion.** The tables
  only help when `a` is fixed across the sweep, and they are about as large as `a` is. Problem 621's
  constant is fixed but huge, so its condition on `p` would be a table nobody can build. Problem 752's
  `7` would fit in a table, but the order search after it costs far more than one `pow`, so the code
  just calls `pow`. In both, `pow(a, (p-1)//2, p)` is the honest tool.
- **Handle `p = 2` and `p | a` separately.** Every table above is stated for odd primes not dividing
  `a`. These are the boundary cases that produce a wrong count rather than a crash.
- **A residue class gives *two* roots, not one** — `n₀` and `p - n₀`. Sieving only one of them
  silently leaves half the composites marked prime. When `p | 2a` the two coincide; that collision
  is a real case, not a rounding error.
- **Watch the self-divisor.** When you sieve `f(n)` by the primes dividing it, the index where
  `f(n) = p` exactly is a *prime* value being struck out by itself. Problem 216 has to advance the
  start of that progression by one full period `p` to avoid losing it, and problem 291 does the same.
- **The filter shrinks the prime list, not the sieve.** In problem 216 the mod-8 test halves the
  per-prime setup work, but the index array is still `O(N log log N)` to sweep. Knowing which half
  of the cost a filter attacks tells you whether it is worth the branch.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0245](/solutions/0245/) — Coresilience
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ● [0921](/solutions/0921/) — Golden Recurrence

<!-- /problems -->
