<!-- tags: [modular-multiplicative-inverse-application] -->
<!-- status: final 2026-11-02T22:20Z -->
# Modular multiplicative inverse (application)

A [modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) is
the element `a⁻¹` with `a·a⁻¹ ≡ 1 (mod m)`. Computing one is a solved, ten-line problem — that is
the [extended Euclidean algorithm](/blogs/technique/extended-euclidean-algorithm)'s page. This page
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
anything else. Three routes to it, all `O(log m)`:

| Route | Requires | Cost |
|---|---|---|
| [Extended Euclid](/blogs/technique/extended-euclidean-algorithm) | `gcd(a, m) = 1` | `O(log m)` divisions |
| [Fermat](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem): `a⁻¹ ≡ a^(m−2)` | `m` **prime** | `O(log m)` multiplications |
| [Euler](https://en.wikipedia.org/wiki/Euler%27s_theorem): `a⁻¹ ≡ a^(φ(m)−1)` | `gcd(a, m) = 1`, `φ(m)` known | `O(log m)` multiplications |

In Python each is one expression — `pow(a, -1, m)`, `pow(a, m - 2, m)` — so the choice is about
the modulus, not the ergonomics. Prefer `pow(a, -1, m)`: it is faster, and it raises rather than
silently returning a wrong value when the inverse does not exist. Reach for the exponent forms when
the modulus is a known prime *and* you are already doing
[modular exponentiation](/blogs/technique/modular-exponentiation) anyway — or when you need
inverses of a whole *array* at once. Euclid branches on every element; square-and-multiply does the
same operations on every lane, so it [vectorises](/blogs/technique/vectorized) cleanly. Problem 0675
inverts every odd number up to `2n + 1` in one NumPy Fermat pass. Problem 0407 inverts every residue
of a small composite `s` with the Euler form, computing `φ(s)` along the way as the count of units.

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
of a derivation, stop searching. The same move can thin out a sum, too. In problem 0860 the
constraint `3i + 5j = 4n` gives `3i ≡ 4n (mod 5)`, so `i ≡ 4n · 3⁻¹ ≡ 3n (mod 5)`. A double sum over
`(i, j)` becomes one loop that steps `i` by 5 from a known start. At its barest the unknown *is* the inverse: problem 0274's
"divisibility multiplier" — the `m` that makes `a + b·m` a test for divisibility of `10a + b` by `p`
— turns out, after one line of algebra (`10·f(n) = n + b(10m − 1)`), to be exactly `10⁻¹ mod p`. A
puzzle phrased about digits is a sum of inverses.

The congruence can also be solved for *every* right-hand side at once, and then the inverse becomes
a change of coordinates. Problem 0718 needs, for each residue `r` modulo `x`, the least multiple of
`y` in that class: `a·y ≡ r` gives `a ≡ r·y⁻¹`, so it is `y · ((r·y⁻¹) mod x)`. The solution walks
the classes along the cycle `rᵢ = i·z mod x` rather than in order. The class index then becomes
`rᵢ·y⁻¹ ≡ i·(z·y⁻¹)`, so one precomputed multiplier `k = z·y⁻¹ mod x` turns the whole sweep into
`y · ((i·k) mod x)` — plain array arithmetic over `i`, with no per-class solve. Multiplying by a unit
permutes `ℤ/x`, which is why the walk still visits every class exactly once.

The same congruence is also the step of [Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma),
which lifts a root of a polynomial from modulo `p^e` to modulo `p^(e+1)`. Problem 0659 sieves
`f(k) = 4k² + 1` by its prime factors. A prime `p` divides `f(k)` along the progressions
`k ≡ ±√−1 · 2⁻¹ (mod p)`, and the derivation reaches them through a fraction: `n ≡ −1/2`, which is
just the residue `(p − 1)/2`. To catch `p²`, `p³`, … it looks for the root modulo `p·q` (with
`q = p^e`) in the form `k + q·s`. Expanding `f` gives a linear congruence for the correction,
`s ≡ −(f(k)/q) · f′(k)⁻¹ (mod p)`. That is Newton's method done over the integers modulo `p`, and the
division by the derivative is an inverse. It needs `f′(k) = 8k` to be a unit modulo `p`, and at a
root it always is: `p` is odd, and `p | k` would make `f(k) ≡ 1`, so the lift exists and is unique. The inverse is taken modulo `p`, not modulo
`p·q`, so every intermediate stays below `p` and the C port needs no wide arithmetic for it.

Problem 0457 shows the case where the derivative *can* vanish. It wants roots of
`n² − 3n − 1 ≡ 0 (mod p²)`, and completing the square turns that into the quadratic formula,
`n ≡ (3 ± √13) · 2⁻¹`. The formula needs two inverses. `2⁻¹` excludes `p = 2`, and is
`(p² + 1)/2` everywhere else, with no Euclid needed. The Newton step `r ← r − (r² − 13)·(2r)⁻¹` that
lifts `√13` from modulo `p` to modulo `p²` needs `2r` to be a unit, and that fails exactly at
`p = 13`, where the root is `0`. Apart from the primes where `13` has no square root at all, the
only primes the solution treats specially are the ones where an inverse does not exist. Reading the
formula for its denominators gives the list of special cases.

**2 — The glue in the Chinese remainder theorem.** The
[CRT](/blogs/technique/chinese-remainder-theorem) tells you a solution exists; an inverse is what
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

Garner's step assumes `gcd(m₁, m₂) = 1`. Problem 0531 shows what to do when it isn't: it merges
`x ≡ φ(n) (mod n)` with `x ≡ φ(m) (mod m)` over every pair in a window of consecutive integers,
where the moduli share factors all the time. With `d = gcd(n, m)`, the step congruence
`n·t ≡ r₂ − r₁ (mod m)` is solvable only when `d` divides `r₂ − r₁`. When it is, you divide all
three by `d` and invert `n/d` modulo `m/d`, which is now a unit. The answer is unique modulo
`lcm(n, m)`, not `n·m`. So the inverse still does the work. The gcd decides first whether there is
a solution at all, and then shrinks the modulus until the inverse exists.

Sometimes the merged residue is the answer itself. For problem 0407, the idempotents of `ℤ/n`
(`a² ≡ a`) are exactly the CRT solutions of `a ≡ 0 (mod d)`, `a ≡ 1 (mod e)` over the coprime
splits `n = d·e`. Each one is `d · (d⁻¹ mod e)`: the CRT basis element, an inverse times its modulus.
Finding the largest idempotent is then a sweep over factorisations, not a search over `a`.

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

Two newer problems show how far the denominator can be from anything you would build. Problem 0996
ends at a sum of binomials `C(t + n, n)` whose top `t` is far too large for any factorial table, but
whose bottom `n` is small — so each one is a falling factorial of `n` terms times `(n!)⁻¹`, and the
table you would normally precompute is replaced by a short product. Problem 1010 counts
standard Young tableaux by the
[hook length formula](https://en.wikipedia.org/wiki/Hook_length_formula), `n! / ∏ h`, multiplied
over some 10¹⁶ partitions it never lists: the whole product collapses to `(n!)^N / ∏ h^(c_h)`, so the
denominator is assembled as exponents per hook length and inverted once. Both lean on the same
guarantee — a prime modulus larger than every factor in the denominator, so nothing on the bottom
line can vanish.

Exactness is a property of the integer, not of the pieces you compute it from. Problem 0635's
[roots-of-unity filter](https://en.wikipedia.org/wiki/Series_multisection) ends at
`(C(qp, p) + q(p − 1)) / p`. The sum is divisible by `p`, but neither term has to be. Over the
integers you would have to add first and then divide. Modulo a prime you can multiply each term by
`p⁻¹` separately, because multiplying by an inverse distributes over addition and ordinary division
does not. Problem 0705 uses the same freedom to count with probabilities. Its total is `T · E[X]`:
the number of sequences times the expected number of inversions. The expectation is a sum of
fractions with denominators `d(x)·d(y) ≤ 16`. Each fraction becomes a residue, and the product with
`T` is the count. Linearity of expectation is often the easy way to set up a count, and modular
inverses let you use it without leaving integer arithmetic.

The modulus does not need to be prime, either. Problem 0731 wants ten digits of a decimal expansion
starting near position `10¹⁶`, which is an integer part taken modulo `10¹⁰`. Each term needs the
quotient `q = (10^e − r) / 3^i`, an integer with about `10¹⁶` digits. Since `3^i` is a unit modulo
`10¹⁰`, its last ten digits are `(10^e − r) · 3^(−i) mod 10¹⁰`. The remainder `r = 10^e mod 3^i`
comes from a second modular exponentiation in the *other* modulus. So floor division is split into
two residues: the remainder modulo the divisor, and the quotient modulo the base. This is the
[BBP](https://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula)-style
digit-extraction trick, and the inverse is the part that makes it work for an exact quotient.

A variant of the same idea is the inverse as *undo*. Problem 0926 sweeps a running product across
segment boundaries and multiplies by a factor's inverse to remove it again when the segment ends;
0650 keeps a running `p^(−v)` for the same reason. Problem 0675 shows the undo at its clearest. Its
`S(i!)` is a product `∏ (2eₚ + 1)` over the prime exponents of `i!`. Going from `(i−1)!` to `i!`
changes only the exponents of primes dividing `i`, so each step multiplies in the new factor and
multiplies by the inverse of the old one. That is an incremental update of a multiplicative function,
and it is affordable only because the inverse removes one factor without rebuilding the whole
product. Where a sliding window over sums would use a
subtraction, a sliding window over products uses an inverse — with the caveat that a zero factor has
no inverse and breaks the trick, so this only works in a field with the zeros excluded by
construction. The same reasoning gives range products. With prefix products `P(x)`, the product over
`(a, b]` is `P(b) · P(a)⁻¹`, the multiplicative version of a prefix-sum difference. Problem 0754
reads a product of `d^μ(d)` over each of its `O(√N)` quotient blocks this way.

The inverse also undoes a change of variables. Problem 0492's recurrence `a′ = 6a² + 10a + 3`
becomes `b′ = b² − 2` under `b = 6a + 5`, which is a
[Lucas sequence](https://en.wikipedia.org/wiki/Lucas_sequence) doubling rule with a closed form.
All the work happens in `b`, and one `6⁻¹` at the end returns to `a`. The substitution is free
to choose as long as the map back can be inverted modulo every prime involved. Here it fails only
for 2 and 3, which the solution handles separately.

Once you have it, an inverse is also just a residue, and you can use it as a *base* as well as a
divisor. Problem 0711's closed form needs `Σ 2^(−m)` and `Σ m·2^(−m)` alongside the same sums in
`2^m`. Modulo a prime, `2^(−m)` is `(2⁻¹)^m`, so these are ordinary geometric and
arithmetico-geometric series with ratio `2⁻¹`. The function that sums powers of `2` sums powers of
`2⁻¹` unchanged. Negative exponents need no separate code path.

Problem 1006 uses an inverse power to make a state update *linear*. It walks the Fibonacci word
letter by letter and tracks `N(r) = Σ_{i<r} gᵢ·10^i`, a number that grows at its high end. That step,
`N ← N + a·10^r`, depends on the position `r`, so no single matrix per letter describes it, and the
block-matrix composition the solution relies on needs exactly that. Scaling the state by `10^(−r)`
fixes this. The tracked value `N′ = 10^(−r)·N` updates as `N′ ← 10⁻¹·(N′ + a)`, the same rule at
every step, and `N′²` updates the same way with `100⁻¹`. One `10^r` at the end converts back. This
is the same trick as discounting future cash flows to present value. A position-dependent weight
becomes a constant factor per step, and a constant factor per step is what a transfer matrix can
represent.

## Making it cheap

`pow(a, -1, m)` is not free — it is `O(log m)`, roughly thirty multiplications at a 64-bit modulus.
That is nothing once and ruinous inside a hot loop, so the interesting engineering is in avoiding
the repetition.

- **Batch the inverses you need in bulk.** For a whole factorial table, compute *one* inverse and
  sweep backwards, since `(i−1)!⁻¹ = i!⁻¹ · i`. `n` inverses for one exponentiation and `n`
  multiplications — problems 0487 and 0860 do exactly this. The table also pays off across
  queries. Problem 0517 turns its real-valued recursion into a sum of about `√n` binomials
  `C(m + j, j)` for each of several hundred primes `n`. It builds the factorial and
  inverse-factorial tables once, up to the largest `n`, and every binomial after that is three
  lookups and two multiplications. The general form is
  [Montgomery's trick](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Multiple_inverses):
  any `n` inverses cost one inversion plus `3n` multiplications via a prefix-product pass.
  The backward sweep has one weakness: each step depends on the previous one, so it runs one
  element at a time. Problem 0423 needs inverse factorials up to tens of millions in NumPy, and computes
  them without the sweep. Since `1/i! = (top · (top−1) ⋯ (i+1)) / top!`, the whole table is a
  running product of the *descending* integers, reversed, times the single inverse `(top!)⁻¹`. A
  running product of a fixed array can be vectorised, for example in √n blocks, so the sequential
  sweep becomes a few array passes.

  ```python
  inv_fact[n] = pow(fact[n], -1, p)
  for i in range(n, 0, -1):
      inv_fact[i - 1] = inv_fact[i] * i % p
  ```

- **Hoist loop-invariant inverses.** If the divisor depends on the outer index only, invert once
  outside — 0650 precomputes `(p − 1)⁻¹` per prime before the sweep, not per iteration of it. In
  0996 every binomial in the sum shares the same `n!` denominator, so one `(n!)⁻¹` serves them all.
- **Invert the residues, not the operands.** When a small modulus `s` meets many large values `L`,
  `L⁻¹ mod s` depends only on `L mod s`. Problem 0407 builds one table of all `s` residues' inverses,
  then gathers `inv[L % s]` for thousands of `L` in a single indexed read.
- **Divide once, at the end.** When the answer is one big quotient of products, keep numerator and
  denominator as separate running residues — or, as in 1010, as exponent counts per factor — and
  invert the denominator a single time. Per-term inverses turn `k` multiplications into `k`
  exponentiations for no gain; a quotient of products is a product of one quotient.
  Problem 0754 needs the signed product `∏ d^μ(d)`. It keeps two running products, one over the
  `d` with `μ = +1` and one over the `d` with `μ = −1`. A block's product is then one ratio, so it
  takes one inverse per block rather than one per `d`.
- **Invert the product, then multiply the factors back.** If you need the inverses of several
  factors that appear together, invert their product once. The inverse of any one factor is that
  inverse times all the others. Problem 0635 inverts `p · p! · ((q−1)p)!` once per prime. Multiplying
  it by `(qp)!` gives `C(qp, p) / p`, and multiplying it by `p! · ((q−1)p)!` gives `p⁻¹` for the
  other term. This is Montgomery's trick for two factors. Since every prime's denominator is
  inverted by the same Fermat exponent, all 5.76 million inversions run as one
  [vectorised](/blogs/technique/vectorized) exponentiation.
- **Fold inverse powers into the exponent.** Modulo a prime `p`, `x^(−k) = x^((−k) mod (p − 1))` for
  any `x` not divisible by `p`, by [Fermat](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem).
  When signed exponents appear, as with Möbius weights or a difference of
  [Mertens](https://en.wikipedia.org/wiki/Mertens_function) sums in 0754, reduce the exponent
  modulo `p − 1` and use an ordinary `pow`. The inverse comes from the same exponentiation, with no
  separate inversion and no special case for negative signs. Reduce exponents modulo `p − 1`, never
  modulo `p`.
- **Ask whether you need one at all.** Problem 0381 is the instructive case. Its derivation ends at
  `S(p) ≡ −3 · 8⁻¹ (mod p)`, an inverse per prime over millions of primes. But `8·S ≡ −3` with
  `0 ≤ S < p` forces `8S = t·p − 3` for a small `t` determined by `p mod 8`, so a four-entry lookup
  table replaces every inverse with a multiply, a subtract and an exact shift. Problem 0274 is the
  same move from the other side: `10⁻¹ mod p` is `(k·p + 1) / 10`, with `k ∈ {9, 3, 7, 1}` fixed by
  `p`'s last digit, so the inverses of 10 modulo 660-odd thousand primes become one branch-free
  [vectorised](/blogs/technique/vectorized) expression over the sieve's output array — no
  per-prime Euclid at all. Problem 0492 does the same for `6⁻¹`: it is `(p + 1)/6` or `(5p + 1)/6`,
  chosen by `p mod 6`, and it is applied to half a million primes as one array expression. When the
  modulus varies but the *inverted value* is a small constant,
  look for the integer identity before reaching for the general machinery.

## Getting it right

- **Check `gcd(a, m) = 1` before assuming.** This is the failure mode that produces silently wrong
  numbers rather than exceptions. When the shared factor is structural, strip it first: problem 0160
  pulls all factors of 5 out of a factorial before working modulo `5⁵`, precisely so the remaining
  quantity is invertible. Problem 0134's statement excludes one prime pair for the same reason — the
  inverse genuinely does not exist there — and 0274 masks out 2 and 5, the only primes sharing a
  factor with 10. The cheapest proof of invertibility is a size argument: in 0996, 1010, 0675, 0635
  and 0754 the prime modulus exceeds every factor of the denominator, so the check is done before
  the code starts.
- **Check every value the denominator takes, not just the formula.** A closed form can be valid for
  the formula in general and still divide by zero at one value of its parameter. Problem 0520
  reduces its count to 21 geometric series `Σ k^L` with ratios `k = −10, …, 10`. Each is summed as
  `(k^m − 1) · (k − 1)⁻¹`. That works for nineteen of them. At `k = 1` the denominator is zero and
  the sum is just the number of terms. At `k = 0` only the `0⁰ = 1` term survives. Python's
  `pow(0, −1, p)` raises an exception, but a hand-written extended Euclid in C usually returns some
  value without any error, so handle the degenerate values explicitly before applying the closed form. The same check applies modulo
  `p` to any ratio `k ≡ 1 (mod p)`, not only to `k = 1`.
  When non-units can't be excluded, handle them on purpose. Problem 0407's inverse table stores 0 for
  every non-unit, and the CRT formula then gives the trivial idempotents 0 and 1 for those splits,
  which the maximum discards. It never yields a wrong one. Problem 0531 handles them by dividing:
  it pulls out the shared `gcd` before inverting (see the CRT section above).
- **A composite modulus is not a field, but inverses still work.** `gcd(a, m) = 1` is the only
  requirement; primality is not. Problem 0152 inverts squares modulo `p²` and problem 0251 works
  modulo an odd square, both perfectly well. Problem 0506 sums geometric series modulo
  `123454321 = 41²·271²`. It divides by `10⁶ − 1` twice, once for each level of the nested sum
  `Σ_k (x^k − 1)/(x − 1)`. That is valid because `10⁶ − 1 = 3³·7·11·13·37` shares no prime with the
  modulus. Problem 0718 inverts modulo `17^p` for the same reason. What primality buys is only the Fermat shortcut and the
  guarantee that *every* non-zero element is invertible — modulo `p²`, multiples of `p` are not.
  Using `pow(a, m - 2, m)` on a composite `m` returns a plausible-looking number that is not an
  inverse.
- **Normalise the sign, especially in C.** Python's `%` returns a non-negative result for a positive
  modulus; C's follows the dividend, so `((x % m) + m) % m` is the idiom, and it is needed on the
  differences you feed *into* an inverse (`r2 - r1` above) as much as on the result.
- **Reduce before multiplying.** `a⁻¹` is a full-width residue, so `a⁻¹ · b` is a full-width product
  and overflows a 64-bit type at moduli above about `2³²`. Reduce both operands first, and reach for
  `__int128` or [GMP](/blogs/technique/gmp) when the product still does not fit —
  Python's [arbitrary-precision integers](/blogs/technique/arbitrary-precision-arithmetic) hide
  this failure right up until the C port exposes it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0407](/solutions/0407/) — Idempotents
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0475](/solutions/0475/) — Music Festival
- ● [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0520](/solutions/0520/) — Simbers
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0731](/solutions/0731/) — A Stoneham Number
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0767](/solutions/0767/) — Window into a Matrix II
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0892](/solutions/0892/) — Zebra Circles
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0994](/solutions/0994/) — Counting Triangles
- ● [0996](/solutions/0996/) — Overtakes
- ● [1006](/solutions/1006/) — Fibonacci Subwords
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
