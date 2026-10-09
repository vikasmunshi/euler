<!-- tags: [quotient-blocking] -->
<!-- status: final -->
# quotient blocking

Quotient blocking is the observation that `⌊n/k⌋`, as `k` runs from `1` to `n`, takes only about
`2√n` distinct values — and that each value is taken on a *contiguous* run of `k`. Any sum whose
terms depend on `k` only through `⌊n/k⌋` (or on `⌊n/k⌋` times a weight whose run-sums are cheap)
can therefore be evaluated one run at a time instead of one term at a time, turning `O(n)` into
`O(√n)`. Competitive programmers know it as "divisor blocks" or
[the floor-division trick](https://codeforces.com/blog/entry/53925); number theorists meet it inside
the [Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method). It keeps coming back
in the problems below because Project Euler loves bounds like `10¹¹`, where `O(n)` is out of the
question and `O(√n) ≈ 3·10⁵` is instant — and because almost every sum over divisors, multiples or
coprime pairs eventually produces a `⌊n/k⌋`.

## The idea

Fix `n` and look at `q(k) = ⌊n/k⌋`. Two facts carry everything:

- **Few values.** For `k ≤ √n` there are at most `√n` values of `k`, hence of `q`. For `k > √n` the
  quotient itself is below `√n`. So `q` takes at most `2√n` distinct values.
- **Runs are intervals with a closed-form end.** If `q = ⌊n/k⌋`, the largest `k'` with the same
  quotient is `⌊n/q⌋`. That gives the standard jump:

```python
k = 1
while k <= n:
    q = n // k
    k_end = n // q              # last k with n // k == q
    total += q * (F(k_end) - F(k - 1))
    k = k_end + 1
```

Here `F` is a prefix sum of whatever weight multiplies the quotient. The simplest case is the
[divisor summatory function](/topics/domain/divisor-summatory-function)
`D(n) = Σ σ(m) = Σₖ k·⌊n/k⌋`: the weight is `k`, its prefix sum is triangular, and the whole sum
costs `O(√n)`. Nothing about the loop depends on the weight being simple — only on its prefix sums
being available. That is the hinge on which every variant below turns.

The second, subtler consequence is about **which arguments ever appear**. The set
`V(n) = {⌊n/k⌋ : k ≥ 1}` is closed under the operation that recursions perform, because
`⌊⌊n/a⌋/b⌋ = ⌊n/(ab)⌋`. So a recursion that only ever asks for `f(⌊n/k⌋)` never leaves `V(n)`, and
a table of `2√n` entries holds every value it will need. The usual storage is a
[split by size](/topics/technique/sqrt-decomposition): `small[v]` for `v ≤ √n`, and `large[k]` for
the value `⌊n/k⌋` when it exceeds `√n` — indexing by the *denominator* keeps both arrays `O(√n)`.

## The shapes it takes here

**Blocked weighted sums.** The direct form. Problem 0153 evaluates `D(x)` by blocks, and does so at
many `x` — a nested sum over Gaussian norms where each outer term needs `D(⌊N/(a²+b²)⌋)`, so the
block trick sits inside another sum. The weight need not be arithmetic: when it is the
[Möbius function](/topics/domain/mobius-function), as after any
[Möbius inversion](/topics/technique/mobius-inversion-formula) strips a coprimality condition, its
prefix sums are the [Mertens function](/topics/technique/mertens-function-application) `M(x)`, and
each block contributes `g(q)·(M(k_end) − M(k−1))`. Problems 0319 and 0478 both reduce to exactly
`Σ_d μ(d)·g(⌊n/d⌋)`; 0319 then needs `M` at every point of `V(n)`, which is itself a
quotient-blocked recursion, `M(v) = 1 − Σ_{j≥2} M(⌊v/j⌋)`.

**Sieving at the key values only.** The Lucy_Hedgehog prime-counting DP — a cousin of the
[Meissel–Lehmer algorithm](https://en.wikipedia.org/wiki/Meissel%E2%80%93Lehmer_algorithm) and the
engine of the [Min_25 sieve](/topics/technique/min-25-sieve) — computes the
[prime-counting function](/topics/domain/prime-counting-function) (or the sum of primes, or any
completely multiplicative weight over primes) at *every* `v ∈ V(n)` at once, by running Eratosthenes'
strike-out as a recurrence on `2√n` running counts rather than on `n` cells. Problems 0501, 0565 and
0642 all need prime counts or prime sums at arguments like `⌊n/(pq)⌋`, and that is precisely the set
the DP has already filled. The closure property is what makes this work.

**Iterate over the quotient, not the index.** When the outer loop is over large primes `p > √T` that
each appear once, the interesting quantity `⌊T/p⌋` again takes few values. Problem 0272 flips the
loop: for each quotient `q` it multiplies a cofactor sum `S(q)` by the sum of qualifying primes in
the band `(⌊T/(q+1)⌋, ⌊T/q⌋]`, read from a prefix-sum array. Problems 0429 and 0926 do the same to
[Legendre's formula](/topics/domain/legendres-formula): every prime above `√n` has exponent exactly
`⌊n/p⌋` in `n!`, so millions of primes collapse into a few thousand exponent classes, each handled
once. 0926 then blocks a second time — as a function of `k`, the product `Π (⌊e/k⌋ + 1)` is a step
function whose breakpoints are the union of each factor's quotient breakpoints, so a ten-million-term
sum becomes a sweep over a couple of hundred thousand constant segments.

**Blocking the numerator.** The same structure runs the other way. With the *divisor* `x` fixed,
`⌈n/x⌉ = c` holds on the run `n ∈ ((c−1)x, cx]`. Problem 0255 averages an integer Heron iteration
over `9·10¹³` starting values; each step reads `n` only through `⌈n/x⌉`, so whole intervals of `n`
march together and split only when their next estimate differs. The step count is tracked per
interval, never per `n`.

## How to reason about it

- **The trigger is a floor in the summand.** Write the sum out. If `k` enters only as `⌊n/k⌋` —
  or as `⌊n/k⌋` times a weight with an `O(1)` prefix sum — block it. If it does not, try swapping the
  order of summation: `Σ_{m≤n} Σ_{d|m} f(d)` is `Σ_d f(d)·⌊n/d⌋`, and the floor appears.
- **The cost moves to the prefix sums.** Blocking is free only if `F(k_end) − F(k−1)` is. Triangular
  numbers and power sums are closed forms; `M(x)` and `π(x)` are not, and computing them at all of
  `V(n)` is usually the real work — about `O(n^{3/4})`, or `O(n^{2/3})` with a sieve up to `n^{2/3}`
  for the small arguments. Budget for that, not for the `O(√n)` outer loop.
- **Use `n // q` for the run end, not a float.** `int(n / q)` loses precision past `2⁵³`; integer
  division is exact and costs the same. In C, keep `n` and its products in 64 bits (or
  [`__int128`](/topics/technique/int128) when weights are multiplied before a modular reduction).
- **Get the boundary at `√n` right.** The `small`/`large` split must agree on which side `⌊√n⌋`
  itself falls, and the lookup `large[n / v]` is valid only because `v` came from `V(n)`. Use an
  exact integer square root (`math.isqrt`), never `int(n ** 0.5)`.
- **It composes.** A blocked sum inside a blocked sum (0153, 0926) or inside a DFS over factorisation
  shapes (0272, 0501, 0642) stays cheap as long as each layer's arguments stay inside some `V(m)`.
  Problems that look like they need `O(n)` work often need `O(√n)` work at `O(√n)` points — and the
  question to ask is how much of that work is shared.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0478](/solutions/0478/) — Mixtures
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
