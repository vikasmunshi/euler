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

There is a language asymmetry here that recurs in five of the six problems below. Python has the
inverse built in — `pow(a, -1, m)` since 3.8 — so the Python solution is a single expression and
the technique is invisible in the source. The C port has no such primitive and carries a
hand-written `mod_inverse` doing the loop above. When you compare a Python and a C solution in this
stack and the only structural difference is a fifteen-line helper near the top of the C file, this
is usually what it is.

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

Problem 0198 sits between the two cases: its inner count is "how many integers in `[lo, hi]` are
congruent to `r (mod m)`", where `r` is an inverse from the Farey-neighbour relation `bc - ad = 1`
— a Bézout identity that the problem hands you rather than one you have to compute.

## Getting it right

- **Normalise the sign.** The Bézout `x` can be negative; the inverse must land in `[0, m)`.
  Python's `%` already returns a non-negative result for a positive modulus, so `x % m` suffices.
  C's `%` follows the sign of the dividend, so the idiom is `((x % m) + m) % m` — and the same
  correction is needed on any other quantity you reduce, not just the inverse.
- **Watch the coefficient growth.** The remainders shrink monotonically but the coefficients grow;
  they stay bounded by roughly `max(a, b)`, so the danger is not the coefficients themselves but the
  `x·a` products you form afterwards. Reduce operands modulo `m` *before* multiplying, and reach for
  a wider type when the intermediate does not fit — problems 0236 and 0932 both do the arithmetic in
  `__int128` on the C side for this reason, where Python's
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
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
