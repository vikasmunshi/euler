<!-- tags: [modular-exponentiation] -->
<!-- status: final -->
# Modular exponentiation

[Modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation) computes
`b^e mod m` without ever forming `b^e`. That one sentence is why it turns up in thirty problems
below: over and over, the quantity a problem asks for is a *residue* — the last ten digits, a count
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
is the primitive that other number-theoretic machinery is built from. Six recurring roles:

| Role | Shape | Seen in |
| --- | --- | --- |
| Direct residue | `pow(b, e, m)` | 48, 97, 194, 820 |
| [Modular inverse](/topics/domain/modular-multiplicative-inverse) | `pow(a, m-2, m)` for prime `m`, or `pow(a, -1, m)` | 365, 487, 545, 650, 743, 926 |
| Primality witness | `pow(a, d, n)` then repeated squaring — [Miller–Rabin](/topics/technique/miller-rabin-primality-test) | 111, 146, 216, 293 |
| [Multiplicative order](/topics/domain/multiplicative-order) | `pow(10, k, n) == 1` | 130, 132, 133 |
| Modular square root | `pow(a, (p+1)//4, p)`, [Tonelli–Shanks](/topics/technique/tonelli-shanks-algorithm) | 200, 745 |
| Period argument | no code — `λ(m)` bounds the exponent | 188, 250 |

The inverse row deserves a note, because it is the most common use by volume. By [Fermat's little
theorem](/topics/technique/fermats-little-theorem-application), `a^(p-1) ≡ 1 (mod p)`, so
`a^(p-2)` is `a⁻¹`. Any solution that divides under a prime modulus — a binomial coefficient, a
Faulhaber polynomial, an expected value as a fraction — is really calling modular exponentiation
once per division. Python's `pow(a, -1, m)` (3.8+) does the same job for a general modulus via the
[extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm), and is both faster
and honest about failure: it raises when `a` is not invertible, where `pow(a, m-2, m)` silently
returns garbage if `m` is composite.

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

The catch is coprimality. When `a` shares a factor with `m`, `a^e ≡ a^(e mod φ(m))` is **false**,
and this is the single most common bug in the technique. The generalized form, valid for any `a`
once `e ≥ log₂ m`, keeps one full period in the exponent:

```
a^e ≡ a^((e mod φ(m)) + φ(m))   (mod m)
```

Problem 188 needs precisely this: `1777` is not coprime to every modulus on its totient chain, and
the bare reduction gives a wrong answer that looks plausible.

## How to reason about it

- **Reach for it the moment the answer is a residue.** If the problem says "last `k` digits", "modulo
  `1000000007`", or "is `x ≡ 1`", you are in this territory, and the size of the true value is a red
  herring you should stop thinking about immediately.
- **`O(log e)` is not always necessary.** Problem 97's linear doubling loop is `7.8 × 10^6`
  iterations — 23 with square-and-multiply, but both finish instantly, and the linear one is easier
  to read. Square-and-multiply earns its keep when the exponent is genuinely large (`10^18`), or
  when you call it in a loop millions of times over, as problem 820 does once per denominator.
- **In C, watch the width.** Two residues below `m` multiply to nearly `m²`. With `m` near `10^10`
  the product is `10^20` and a `long long` silently overflows — hence the
  [`__int128`](/topics/technique/int128) casts above. The rule of thumb: a 64-bit modulus needs
  128-bit intermediates, or [Montgomery
  multiplication](https://en.wikipedia.org/wiki/Montgomery_modular_multiplication) if you cannot
  afford them. Python has no such trap, which is exactly why the C translation of a working Python
  solution is where this bug appears.
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
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0980](/solutions/0980/) — The Quaternion Group I

<!-- /problems -->
