<!-- tags: [extended-euclidean-algorithm] -->
<!-- status: final -->
# Extended Euclidean algorithm

The [extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
runs the ordinary [Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm) for
`gcd(a, b)` while carrying along the bookkeeping that answers a second question: *which* integer
combination of `a` and `b` produces that gcd. It costs the same `O(log min(a, b))` steps and it is
the workhorse behind almost every "divide in modular arithmetic" move in this stack — most often
disguised as a modular inverse, occasionally in its full form as the general solution of a linear
equation in integers.

## The algorithm

Euclid's algorithm repeatedly replaces `(a, b)` with `(b, a mod b)` until the second term is zero;
the first term is then the gcd. The extended version threads two extra registers through the same
loop, tracking how the current remainder is built out of the original `a` and `b`:

```python
def egcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_r, old_s          # g, and x with a*x ≡ g (mod b)
```

Every remainder in the sequence is an integer combination `x·a + y·b`, and the loop just applies
the same subtraction to the coefficients that it applies to the remainders. When it terminates you
have the gcd `g` together with a pair `(x, y)` satisfying `a·x + b·y = g` — the coefficients of
[Bézout's identity](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity). The `y` register can
be dropped when you only want `x`, since `y` is recoverable as `(g - a·x) / b`; that is why the
version above tracks a single coefficient. Write it iteratively rather than recursively — the
recursion is prettier on a blackboard but the loop has no stack cost and is the form both languages
here use.

## The common case: a modular inverse

Nine times out of ten the reason to reach for it is a
[modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse):
given `a` and `m`, find `a⁻¹` with `a·a⁻¹ ≡ 1 (mod m)`. Take `b = m`. If `gcd(a, m) = 1`, Bézout
gives `a·x + m·y = 1`, and reading that modulo `m` collapses the second term to leave
`a·x ≡ 1 (mod m)` — so `x mod m` *is* the inverse. Nothing extra is needed; the inverse is a
by-product of the gcd computation.

Two consequences are worth internalising. First, the algorithm returns `g` as well as `x`, so it
**tells you whether the inverse exists** rather than requiring you to check separately: `g ≠ 1`
means there is no inverse. Problem 0134 turns on exactly that boundary — it must end a fixed block
of decimal digits while being divisible by the next prime, which needs `10ᵈ` inverted modulo that
prime, and the one excluded pair in the statement is precisely the one where the modulus shares a
factor with `10ᵈ` and the inverse does not exist. Second, an inverse is what lets you *divide*
inside a modulus, which is why this technique shows up wherever a
[linear congruence](https://en.wikipedia.org/wiki/Linear_congruence_theorem) has to be solved for
its unknown, and as the glue step inside the
[Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem). Problems
0160, 0932 and 0934 all use it that way: each merges congruences modulo coprime factors, and each
merge is one inverse.

Problem 0271 shows the CRT glue in its other arrangement, and is worth seeing for that reason. It
sums the cube roots of unity modulo a squarefree `n` with fourteen prime factors, and the roots
modulo `n` are every combination of one root modulo each factor — hundreds of combinations, not
one. Merging pairwise would repeat the inversions for every combination. Instead, each factor `q`
gets one *idempotent* up front,

```
e_q = (n/q) · ((n/q)⁻¹ mod q)        ≡ 1 (mod q),  ≡ 0 (mod n/q)
```

after which any combination of per-factor residues `r_q` is just `Σ r_q·e_q mod n` — additions and
multiplications only. The inverses are paid once per factor, not once per combination: a fixed
basis, then cheap linear algebra. The same problem uses the inverse a second time, inside a
Newton step: lifting a root of `x³ − 1` from `p` to `p^k` by
[Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma) is
`ω ← ω − (ω³ − 1)·(3ω²)⁻¹`, and the division by the derivative is, once again, an inverse modulo
the current prime power — one that exists precisely because `3ω²` is a unit when `p ≠ 3`, which is
exactly why `p = 3` is the case that needs separate handling.

There is a language asymmetry here that recurs in most of the problems below. Python has the
inverse built in — `pow(a, -1, m)` since 3.8 — so the Python solution is a single expression and
the technique is invisible in the source. The C port has no such primitive and carries a
hand-written `mod_inverse` doing the loop above. When you compare a Python and a C solution in this
stack and the only structural difference is a fifteen-line helper near the top of the C file, this
is usually what it is. Problem 0250 is the asymmetry taken one step further: there the Python side
needs no inverse *at all*, and only the C side does — see the next section.

## When the divisor is not a unit

The `g ≠ 1` verdict is not always the end of the road. Problem 0250 counts subsets by residue and
needs whole rows of binomial coefficients modulo `10¹⁶`, built by the multiplicative recurrence
`C(n, i+1) = C(n, i)·(n−i)/(i+1)`. That division is exact over the integers but not legal modulo
`10¹⁶`: half the denominators are even, a fifth are multiples of 5, and neither has an inverse.
Python dodges the question by carrying the binomial as an exact big integer and reducing only when
it stores it. The C port cannot, and the fix is worth knowing in general: split the running value
into the part the modulus can see and the part it cannot,

```
C(n, i) = 2^e₂ · 5^e₅ · u        with gcd(u, 10) = 1
```

Strip every factor of 2 and 5 out of each numerator and denominator into the exponent counters
`e₂`, `e₅` (which may go up and down), and what remains of the denominator is coprime to `10¹⁶`, so
extended Euclid inverts it and the division becomes a multiplication on `u`. The coefficient is
reassembled as `u · 2^e₂ · 5^e₅ mod 10¹⁶` only when it is needed. The recipe generalises to any
composite modulus: the primes it shares with your denominators are tracked as exponents, everything
else is a unit, and units are exactly what the algorithm can invert.

An alternative exists when the modulus is prime: by
[Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), `a⁻¹ ≡ a^(p-2)
(mod p)`, computable by
[exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring). It is a
one-liner and worth knowing, but it needs a prime modulus and spends `O(log p)` *multiplications*
where extended Euclid spends `O(log m)` cheap divisions. Prefer Euclid unless you are already doing
modular exponentiation anyway.

## The general case: a solution family

The inverse is a special case that discards most of what the algorithm computes. The full object is
the general solution of a
[linear Diophantine equation](https://en.wikipedia.org/wiki/Diophantine_equation)
`c₁x + c₂y = R`. It is solvable exactly when `g = gcd(c₁, c₂)` divides `R`; scaling the Bézout
coefficients by `R/g` gives one particular solution `(x₀, y₀)`, and *every* solution is

```
(x₀ + k·c₂/g,  y₀ − k·c₁/g)     for k ∈ ℤ
```

— a one-parameter family, a lattice line. That shift vector is the useful part: it converts "does
an integer solution exist in this box?" into two linear inequalities on `k`, one from each
variable's interval, and the answer is whether the two `k`-ranges intersect. Problem 0236 (the
[Simpson's paradox](https://en.wikipedia.org/wiki/Simpson%27s_paradox) hamper table) leans on this
directly: its feasibility test reduces to a three-variable equation with each variable confined to
a known interval, and after iterating the narrowest interval the remaining two-variable equation is
decided in `O(1)` per candidate by exactly this range-intersection test. A brute-force scan over
the widest interval instead would have been thousands of times the work.

Between the two cases sits a pattern common enough to name: *count* the solutions of a linear
congruence in a range rather than find one. The solutions of `a·x ≡ c (mod m)` with
`gcd(a, m) = 1` are the single class `x ≡ c·a⁻¹ (mod m)`, so the number of them in `[lo, hi]` is
an arithmetic-progression count — `O(1)` once you have the inverse, however wide the range.
Problem 0198's inner count has exactly this shape, with `r` an inverse that falls out of the
Farey-neighbour relation `bc − ad = 1` — a Bézout identity the problem hands you rather than one
you have to compute. Problem 0251 (Cardano triplets) shows it at scale: after splitting `b`
against `n` by their gcd, the divisibility condition becomes `8·n₁·d ≡ 3 (mod b₁²)`, so for each
coprime pair `(n₁, b₁)` the admissible `d` are one residue class modulo `b₁²`, its smallest member
is `3·(8n₁)⁻¹ mod b₁²`, and the count up to a bound is a single floor division. Note how existence
is settled by structure rather than tested: `b₁` is forced odd, and pairs with `gcd(n₁, b₁) > 1`
are skipped before the inverse is ever asked for. A search over triplets collapses into one
inverse per `(n₁, b₁)` pair.

## Getting it right

- **Normalise the sign.** The Bézout `x` can be negative; the inverse must land in `[0, m)`.
  Python's `%` already returns a non-negative result for a positive modulus, so `x % m` suffices.
  C's `%` follows the sign of the dividend, so the idiom is `((x % m) + m) % m` — and the same
  correction is needed on any other quantity you reduce, not just the inverse.
- **Watch the coefficient growth.** The remainders shrink monotonically but the coefficients grow;
  they stay bounded by roughly `max(a, b)`, so the danger is not the coefficients themselves but the
  `x·a` products you form afterwards. Reduce operands modulo `m` *before* multiplying, and reach for
  a wider type when the intermediate does not fit — problems 0236, 0271 and 0932 all do the
  arithmetic in `__int128` on the C side for this reason, and 0250, whose modulus `10¹⁶` already fills most of a
  64-bit word, runs the Euclid loop itself in `__int128`, where Python's
  [arbitrary-precision integers](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic)
  simply absorb it.
- **Floor, don't truncate.** The recurrence and the interval clipping both assume floored division.
  C truncates toward zero, so a C port that clips a solution family to an interval needs an explicit
  floored-division helper; getting this wrong shows up as an off-by-one only on negative inputs,
  which is exactly the case a quick test is least likely to cover.
- **Recognise the shape.** If a derivation ends in "…so `k ≡ something (mod n)`" or "…so this must
  be a multiple of `M`", you are one inverse away from a closed form and should stop searching. That
  is the real payoff: the technique routinely replaces a loop over candidates with a single
  expression.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0250](/solutions/0250/) — $250250$
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
