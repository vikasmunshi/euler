<!-- tags: [modular-exponentiation] -->
<!-- status: final 2026-11-01T14:14Z -->
# Modular exponentiation

[Modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation) computes
`b^e mod m` without ever forming `b^e`. That one sentence is why it turns up in more than forty
problems below: over and over, the quantity a problem asks for is a *residue* — the last ten digits, a count
modulo `10^9+7`, whether some power lands on `1` — while the power itself has more digits than
there are atoms in the universe. The naive route computes a number you cannot store to answer a
question about a number that fits in a register. Reducing at every step keeps every intermediate
below `m^2`, and squaring instead of multiplying turns `e` steps into `log₂ e`.

## The idea

Two independent tricks, usually used together.

**Reduce as you go.** `(x · y) mod m = ((x mod m) · (y mod m)) mod m` — multiplication is a
homomorphism onto `ℤ/mℤ`, so you may reduce after each multiply and the final residue is unchanged.
That alone caps the operands at `m` and the products at `m²`, which is what makes the computation
fit in a machine word at all. It is worth `O(e)` on its own: problem 97 asks for the last ten
digits of `28433 · 2^7830457 + 1`, and simply doubling `7830457` times under `mod 10^10` answers it
in milliseconds without a single big integer.

**Square instead of multiply.** [Exponentiation by
squaring](/topics/technique/exponentiation-by-squaring) reads `e` in binary: square the running
base at every bit, fold it into the result only where the bit is set. `e` shrinks by half each
iteration, so the cost is `O(log e)` multiplications rather than `e` of them. The public C solution
to problem 48 is the whole algorithm in twelve lines:

```c
static long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;
    while (exp > 0) {
        /* Widen to __int128 before each multiply: operands near 10^10 give products
           up to ~10^20, which overflow a signed 64-bit long long. */
        if (exp & 1)
            result = (__int128)result * base % mod;
        base = (__int128)base * base % mod;
        exp >>= 1;
    }
    return result;
}
```

In Python you never write that loop: the built-in `pow(b, e, m)` is exactly it, in C, on arbitrary
precision integers, and a hand-rolled version is strictly slower. The same problem 48 in Python is
`sum(pow(i, i, 10**10) for i in range(1, n+1)) % 10**10`.

## The roles it plays

The reason this tag lands on so many solutions is that `pow(b, e, m)` is rarely the *answer* — it
is the primitive that other number-theoretic machinery is built from. Eight recurring roles:

| Role | Shape | Seen in |
| --- | --- | --- |
| Direct residue | `pow(b, e, m)` | 48, 97, 194, 615, 731, 820 |
| [Modular inverse](/topics/domain/modular-multiplicative-inverse) | `pow(a, m-2, m)` for prime `m`, or `pow(a, -1, m)` | 365, 487, 545, 635, 650, 675, 743, 860, 926 |
| Primality witness | `pow(a, d, n)` then repeated squaring — [Miller–Rabin](/topics/technique/miller-rabin-primality-test) | 111, 146, 216, 271, 293, 516 |
| [Multiplicative order](/topics/domain/multiplicative-order) | `pow(10, k, n) == 1` | 130, 132, 133, 752 |
| Modular root | `pow(a, (p+1)//4, p)`, `pow(g, (p-1)//k, p)`, [Tonelli–Shanks](/topics/technique/tonelli-shanks-algorithm) | 200, 271, 659, 745 |
| Exponent reduction | `pow(x, pow(2, k, p-1), p)`, or `λ(m)` bounds the exponent | 188, 250, 455, 492, 754, 822 |
| Product by multiplicity | `∏ pow(b, count[b], m)` | 754, 1010 |
| Power in a ring extension | `(a + b√d)^n` by square-and-multiply on pairs | 492, 752 |

The inverse row deserves a note, because it is the most common use by volume. By [Fermat's little
theorem](/topics/technique/fermats-little-theorem-application), `a^(p-1) ≡ 1 (mod p)`, so
`a^(p-2)` is `a⁻¹`. Any solution that divides under a prime modulus — a binomial coefficient, a
Faulhaber polynomial, an expected value as a fraction — is really calling modular exponentiation
once per division. Python's `pow(a, -1, m)` (3.8+) does the same job for a general modulus via the
[extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm), and is both faster
and honest about failure: it raises when `a` is not invertible, where `pow(a, m-2, m)` silently
returns garbage if `m` is composite.

Volume is also where the inverse row gets expensive, and the cure is to invert less. Problem 860
needs every `k!⁻¹` for `k ≤ n` to evaluate binomials; it makes exactly one `pow` call, for
`(n!)⁻¹`, and walks the table down with `(k-1)!⁻¹ = k · k!⁻¹` — `n` multiplications in place of
`n` exponentiations. Problem 675 has no such telescoping structure: it needs the inverse of every
odd `2k+1` up to `2·10^7`, so it pays for all of them, but as one vectorised exponentiation over the
whole array (see below) rather than ten million interpreted calls. Problem 635 shows the third
way to invert less: an inverse of a product is an inverse of each factor in disguise. Each of its
terms divides by `p · p! · ((q-1)p)!`; it inverts that whole denominator once, and recovers `1/p`
for free as `inv · p! · ((q-1)p)!` — two multiplications instead of a second exponentiation. The
same identity, chained, is [batch
inversion](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Multiple_inverses): `n`
inverses for one `pow` and `3n` multiplications.

The root row is the same power map read the other way. In a cyclic group of order `p - 1`,
raising to `(p-1)/k` lands in the subgroup of `k`-th roots of unity, so problem 271 — cube roots of
`1` modulo a primorial — gets a primitive cube root modulo each prime from `pow(g, (p-1)//3, p)`
for any `g` that is not a cubic residue, then lifts it to higher prime powers with a
[Hensel](https://en.wikipedia.org/wiki/Hensel%27s_lemma) step whose division is, again, a modular
inverse. Problem 659 is the `k = 4` case: a polynomial sieve over `4k² + 1` needs the roots of that
quadratic modulo every prime `p ≡ 1 (mod 4)`, which is `√-1` halved — and `c^((p-1)/4)` is a square
root of `-1` for any non-residue `c`, recognised by its square landing on `p - 1`.

The direct-residue row hides a pattern worth naming: reading digits far to the right of a
decimal point. The `n`-th digit of `1/k` is a function of `10^(n-1) mod k` alone (problem 820),
so a digit a billion places out costs `log n` multiplications. Problem 731 pushes the same move
through a series: its [Stoneham number](https://en.wikipedia.org/wiki/Stoneham_number) is a sum of
terms `1/(3^i · 10^(3^i))`, and a ten-digit window deep inside it is `∑ ⌊10^e / 3^i⌋ mod 10^10`
plus a carry. Each term needs *two* moduli: `r = pow(10, e, 3^i)` is the remainder, so
`(10^e − r)` is exactly divisible by `3^i`, and *because* that division is exact and `3` is coprime
to `10`, it becomes a multiplication by `3^(-i)` mod `10^10`. The remainders `r / 3^i` are summed
exactly for the carry. It is the [BBP digit-extraction
idea](https://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula) in base ten.

The last row is the newest, and it turns the usual relationship around: the exponent is not given,
it is *counted*. Problem 1010 asks for a product of tableau counts over every partition of `300`
into at most `150` parts — about `9 × 10^15` factors, far too many to multiply. But each factor is
`n!` divided by a product of hook lengths, and hook lengths only run from `1` to `n`. So the whole
product is `(n!)^N / ∏ h^(c_h)`, where `N` is the number of partitions and `c_h` the number of boxes
with hook `h` across all of them. The hard work moves into *counting* `N` and the `c_h` (generating
functions, not enumeration); once those exponents are known, `n + 1` calls to `pow` and a single
inverse finish the job. Whenever a product ranges over more objects than you can visit but its
factors come from a small alphabet, count multiplicities and let modular exponentiation absorb
them — and divide once, at the end, rather than once per factor.

Problem 754 adds signs. Its product of [Gauss
factorials](https://en.wikipedia.org/wiki/Gauss_factorial) over `n ≤ 10^8` becomes, by Möbius
inversion, `∏_d (d^(T(N/d)) · F(N/d))^(μ(d))` — `F` a superfactorial, `T` a triangular number, and
`μ(d) ∈ {-1, 0, 1}` an exponent that can be negative. Two observations make it cheap. The exponent
of a nonzero residue under a prime modulus lives mod `p - 1`, so a negative exponent is just
`(e mod (p-1))` — no separate inversion branch. And the factor depends on `d` only through
`⌊N/d⌋`, which takes `O(√N)` distinct values: within each block, `∏ d^(μ(d))` is a ratio of two
prefix products (the `μ = +1` and `μ = -1` factors kept apart), so one inverse and two `pow` calls
per block replace `10^8` of them.

## Reducing the exponent

The deepest use is the one that writes no `pow` call at all. If `gcd(a, m) = 1`, then
`a^e ≡ a^(e mod φ(m)) (mod m)` — the exponent lives modulo
[`φ(m)`](/topics/domain/eulers-totient-function), or better, modulo the smaller
[`λ(m)`](/topics/technique/carmichael-function). So an exponent that is itself astronomically large
can be reduced *before* you exponentiate.

This is the engine of problem 188, which asks for a
[tetration](https://en.wikipedia.org/wiki/Tetration) — a power tower of height 1855 — modulo `10^8`.
You cannot reduce the tower, but you can reduce its exponent modulo `φ(10^8)`, and that exponent is
a shorter tower, whose exponent reduces modulo `φ(φ(10^8))`, and so on. The totient chain
`m, φ(m), φ(φ(m)), …` reaches `1` in `O(log m)` steps, so the recursion terminates in about
two dozen levels no matter how tall the tower is. Problem 250 uses the same fact statically: it
proves `k^k mod 250` is periodic in `k` with period `500` by noting the base repeats mod `250` and
the exponent repeats mod `λ(125)`, collapsing a `250250`-term sum to a `500`-term one.

The simplest instance is a prime modulus, where every base below `p` is coprime to it and the
exponent lives mod `p - 1` by Fermat alone. Problem 822 repeatedly squares the smallest of a list of
numbers, about `10^12` squarings each; a number squared `k` times is `x^(2^k)`, and `2^k` is
itself far too large to hold. So the exponent is computed first, as a residue mod `p - 1`, and fed
to the outer power — two nested `pow` calls per term, and the only hard part of the problem is
deciding *which* `k` each number ends with.

Problem 455 runs the chain in the other direction: it wants `x` with `n^x ≡ x (mod 10^9)`, a
fixed point of `x ↦ n^x`. Iterating that map from `x = 1` builds the tower `n, n^n, n^(n^n), …`
mod `10^9`, and the `λ`-chain argument is exactly why such a tower stops changing after a few
levels: each level only matters modulo a strictly shorter modulus, until the modulus is `1`. The
iteration never reduces an exponent explicitly; the theory is what guarantees it terminates — in
about a dozen rounds for every base up to `10^6`.

The catch is coprimality. When `a` shares a factor with `m`, `a^e ≡ a^(e mod φ(m))` is **false**,
and this is the single most common bug in the technique. The generalized form, valid for any `a`
once `e ≥ log₂ m`, keeps one full period in the exponent:

```
a^e ≡ a^((e mod φ(m)) + φ(m))   (mod m)
```

Problem 188 needs precisely this: `1777` is not coprime to every modulus on its totient chain, and
the bare reduction gives a wrong answer that looks plausible.

## Powers in a ring extension

Square-and-multiply never cared that its operands were integers — only that multiplication is
associative. So the same loop raises `a + b√d` to a power modulo `m`, carrying the pair `(a, b)` and
multiplying by `(a + b√d)(c + e√d) = (ac + d·be) + (ae + bc)√d`:

```python
def ring_pow(a, b, n, m, d):           # (a + b√d)^n mod m, as a pair
    ra, rb = 1, 0
    while n:
        if n & 1:
            ra, rb = (ra*a + d*rb*b) % m, (ra*b + rb*a) % m
        a, b = (a*a + d*b*b) % m, 2*a*b % m
        n >>= 1
    return ra, rb
```

What makes this more than a curiosity is that exponent reduction carries over, with a twist that
the [Legendre symbol](https://en.wikipedia.org/wiki/Legendre_symbol) decides. Modulo a prime `p`,
if `d` is a square the ring `𝔽_p[√d]` splits into two copies of `𝔽_p` and every unit's order divides
`p - 1`, as usual. If `d` is not a square, the ring is the field `𝔽_{p²}`, and
[Frobenius](https://en.wikipedia.org/wiki/Frobenius_endomorphism) — `x^p` is the conjugate of `x` —
gives `x^(p+1) = N(x)`, the norm. An element of norm `1` therefore has order dividing `p + 1`.

Problem 752 asks for the multiplicative order of `1 + √7` modulo every `x` up to a million. CRT
reduces it to prime powers, and the split/inert dichotomy hands each prime a known multiple of the
order — `p - 1` in the split case; in the inert one, the order `o` of the norm `-6` in `𝔽_p`, times
a divisor of `p + 1` for the norm-1 element `x^o`. The exact order is then found the standard way:
strip each prime factor `q` from the multiple while `x^(multiple/q)` is still `1`. Lifting to `p^k`
costs one more ring power, because the order either stays or gains exactly one factor of `p`.

Problem 492 never mentions a square root: its sequence `a' = 6a² + 10a + 3` becomes, after
`b = 6a + 5`, the doubling map `b' = b² - 2`, so `b(n) = α^(2^(n-1)) + α^(-2^(n-1))` for a root `α`
of `x² - 11x + 1`. The index is doubly exponential, but modulo `p` the exponent `2^(n-1)` reduces
mod `p - 1` or `p + 1` according to whether the discriminant `117` is a residue — one nested `pow`
— and the [Lucas sequence](https://en.wikipedia.org/wiki/Lucas_sequence) `V(k) = α^k + α^(-k)` is
then evaluated by a *Lucas ladder*, the square-and-multiply loop rewritten on the pair
`(V(k), V(k+1))` with `V(2k) = V(k)² - 2` and `V(2k+1) = V(k)V(k+1) - P`. The ladder never touches
`√117` at all, which is why it works identically for split and inert primes.

## How to reason about it

- **Reach for it the moment the answer is a residue.** If the problem says "last `k` digits", "modulo
  `1000000007`", or "is `x ≡ 1`", you are in this territory, and the size of the true value is a red
  herring you should stop thinking about immediately.
- **…but residues forget order.** When the problem asks for the `n`-th smallest of something and
  only then for a residue, you cannot sort residues. Problem 615 wants the millionth number with at
  least a million prime factors: every candidate near the front is `2^(k-s)` times a small number,
  so the ranking is done exactly on the small numbers, and the astronomical factor enters only at
  the very end, as one `pow(2, k - s, m)`. Factor out the part that is too big to compare, compare
  what is left, exponentiate last.
- **`O(log e)` is not always necessary.** Problem 97's linear doubling loop is `7.8 × 10^6`
  iterations — 23 with square-and-multiply, but both finish instantly, and the linear one is easier
  to read. Square-and-multiply earns its keep when the exponent is genuinely large (`10^18`), or
  when you call it in a loop millions of times over, as problem 820 does once per denominator.
  The exponents in problem 1010 are counts near `10^18`; there no loop but square-and-multiply
  would finish at all.
- **In C, watch the width.** Two residues below `m` multiply to nearly `m²`. With `m` near `10^10`
  the product is `10^20` and a `long long` silently overflows — hence the
  [`__int128`](/topics/technique/int128) casts above. The rule of thumb: a 64-bit modulus needs
  128-bit intermediates, or [Montgomery
  multiplication](https://en.wikipedia.org/wiki/Montgomery_modular_multiplication) if you cannot
  afford them. The converse saves work: a modulus below `2^32` — problem 1010's `1234567891` —
  keeps every product under `2^64`, and an `unsigned long long` needs no widening. Python has no
  such trap, which is exactly why the C translation of a working Python solution is where this bug
  appears.
- **Vectorise the loop, not the call.** When you need a million powers at once — every base
  with its own exponent in problem 455, every odd denominator's inverse in problem 675 — `pow` in
  a Python loop is the bottleneck. Square-and-multiply ports directly to NumPy: one pass per
  exponent bit, squaring a base *array* and using `np.where` to fold it into a result array where
  that bit is set. Thirty array operations replace a million interpreted calls. The modulus can
  vary per lane as easily as the exponent: problem 492 runs one shared exponent `2^(n-1)` against
  an array of moduli `p ∓ 1`, then a Lucas ladder in which every prime reads its own exponent bit.
  The width rule above applies here too: operands under `2^31` keep every product inside `int64`.
- **Reduce the base before the loop, not after.** `base %= mod` on entry costs one division and
  bounds every subsequent operand; skipping it is how a "correct" `mod_pow` overflows on its first
  squaring.
- **A composite modulus wants [CRT](/topics/technique/chinese-remainder-theorem), not a bigger
  exponent.** Split `m` into prime powers, exponentiate in each, recombine. Problem 160 does this
  for `10^k`, working separately modulo `2^k` and `5^k` — necessary there because the factorials
  involved are *not* coprime to the modulus, so no inverse exists until the factors of 2 and 5 are
  stripped out by hand.
- **`pow` is not free.** Each call is `O(log e)` multiplications of `O(log² m)` bit-cost. A sweep
  that calls it per candidate is `O(n log n)` at best; if you find yourself calling it inside two
  nested loops, look for a way to hoist it — usually by exponentiating once and multiplying
  incrementally.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0048](/solutions/0048/) — Self Powers
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0245](/solutions/0245/) — Coresilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0250](/solutions/0250/) — $250250$
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0520](/solutions/0520/) — Simbers
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0731](/solutions/0731/) — A Stoneham Number
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0822](/solutions/0822/) — Square the Smallest
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
