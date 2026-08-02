<!-- tags: [quadratic-residue] -->
<!-- status: final -->
# Quadratic residue

A [quadratic residue](https://en.wikipedia.org/wiki/Quadratic_residue) modulo `p` is a number that
has a square root modulo `p`. That sounds like a fact about squares, and in the problems below it is
never used that way. It is used as a **filter on primes**: given a quadratic expression — `2n² - 1`,
`p² + 1`, `x² - x + 1` — the primes that can ever divide it are exactly the primes modulo which some
constant is a residue, and that constant's residue condition collapses to a congruence class you can
test with a single `p % 8` or `p % 3`. Half or three-quarters of the primes fall away before any
work begins.

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
loop per prime, and it is unnecessary. The
[law of quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity) and its two
supplements convert the question "is `a` a residue mod `p`?" into a congruence on `p` alone. The
three that keep showing up:

| Is it a residue mod `p`? | Exactly when | Cost |
| --- | --- | --- |
| `-1` | `p ≡ 1 (mod 4)` | `p & 3 == 1` |
| `2` | `p ≡ ±1 (mod 8)` | `(p & 7) in (1, 7)` |
| `-3` | `p = 3` or `p ≡ 1 (mod 3)` | `p % 3 == 1` |

Each row is one bit-mask instead of a modular exponentiation, and each is worth roughly the fraction
of primes it discards — a half for `-1` and `2`, two-thirds for `-3`.

## Reading a quadratic form's prime divisors

The step that turns a problem into one of those rows is completing the square. If `p | f(n)` for
some quadratic `f`, multiply by `4a` and complete: the congruence becomes `y² ≡ D (mod p)` for the
discriminant `D`, so `p` can divide `f` at all only when `D` is a residue mod `p`. The three
problems below are three instances of the same move:

- `t(n) = 2n² - 1`: `p | t(n)` means `2n² ≡ 1`, i.e. `n² ≡ 2⁻¹ (mod p)`, which is solvable exactly
  when `2` is a residue — the `p ≡ ±1 (mod 8)` row. Problem 216 uses that to skip half the primes
  before doing anything else.
- `m = p² + 1`: any odd prime `ℓ | m` has `p² ≡ -1 (mod ℓ)`, so `-1` is a residue mod `ℓ` — the
  `ℓ ≡ 1 (mod 4)` row. Problem 221 trial-divides only by `2` and the `1 mod 4` primes, roughly a
  quarter of the integers.
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
- `ℓ ≡ 1 (mod 3)` and you want a root of `x² - x + 1` — that root is `-ω` for `ω` a primitive cube
  root of unity, found as `g^((ℓ-1)/3)` for the first base `g` that does not give `1`. Cheaper than
  a general square root, and it is what problem 245 does.

Lifting a root from `ℓ` to `ℓᵏ` is [Hensel's lemma](/topics/technique/hensels-lemma); combining
roots modulo coprime factors is the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem), and a modulus with `ω`
distinct admissible prime factors ends up carrying `2^ω` roots. That combination — residue condition
picks the primes, Hensel lifts, CRT merges — is how you enumerate every modulus with a solution
without factoring anything.

## How to reason about it

Reach for a residue argument when a loop is testing divisibility against a **quadratic** in the
index, and the inner test is doing the work. The gain is not a better algorithm for the same
candidate set; it is a smaller candidate set, cut by a constant factor (2, 3, 4) at zero cost. That
makes it a [cheap check first](/topics/takeaway/cheap-checks-first) in the strictest sense: a mask on
`p` that is faster than the load of the value it protects.

Things to keep in mind:

- **Constant `a`, varying `p` → use reciprocity. Varying `a`, fixed `p` → use Euler's criterion.**
  The supplements only help when the number whose residue-ness you are asking about is fixed across
  the sweep; otherwise `pow(a, (p-1)//2, p)` is the honest tool.
- **Handle `p = 2` and `p | a` separately.** Every table above is stated for odd primes not dividing
  `a`, and the Legendre symbol is `0` in the second case. These are the boundary cases that produce
  a wrong count rather than a crash.
- **A residue class gives *two* roots, not one** — `n₀` and `p - n₀`. Sieving only one of them
  silently leaves half the composites marked prime. When `p | 2a` the two coincide; that collision
  is a real case, not a rounding error.
- **Watch the self-divisor.** When you sieve `f(n)` by the primes dividing it, the index where
  `f(n) = p` exactly is a *prime* value being struck out by itself. Problem 216 has to advance the
  start of that progression by one full period `p` to avoid losing it.
- **The filter shrinks the prime list, not the sieve.** In problem 216 the mod-8 test halves the
  per-prime setup work, but the index array is still `O(N log log N)` to sweep. Knowing which half
  of the cost a filter attacks tells you whether it is worth the branch.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0245](/solutions/0245/) — Coresilience

<!-- /problems -->
